# -*- coding: utf-8 -*-
"""恢复配置快照 v4（bench wipe 后重放）—— 平时不需要，重置时运行
用法: 把 config-snapshot-v4-20260807.json 放到服务器，然后:
  cd /home/frappe/frappe-bench && ./env/bin/python /tmp/restore_config_v4.py

恢复范围:
1. Property Setter 180 条
2. Custom Field 29 条（注意: 依赖的 DocType 需已存在；业务字段可能需在 app 安装后）
3. POS Profile（含 applicable_for_users 子表）
4. 隐藏 Workspace
5. POS Cashier 角色 + Custom DocPerm 权限
6. pos1/pos2 收银员账号（Sales User + Accounts User + POS Cashier、静音、默认公司）
7. Mode of Payment 账户配置
"""
import json
import sys

import frappe

frappe.init(site="erp.solua.one", sites_path="/home/frappe/frappe-bench/sites")
frappe.connect()

SNAPSHOT_PATH = "/tmp/config-snapshot-v4-20260807.json"
with open(SNAPSHOT_PATH, encoding="utf-8") as f:
    snap = json.load(f)


def restore_property_setters(rows):
    n = 0
    for r in rows:
        if frappe.db.exists(
            "Property Setter", {"doc_type": r["doc_type"], "field_name": r.get("field_name"), "property": r["property"]}
        ):
            continue
        ps = frappe.get_doc(
            {
                "doctype": "Property Setter",
                "doc_type": r["doc_type"],
                "doctype_or_field": r.get("doctype_or_field", "DocField"),
                "field_name": r.get("field_name"),
                "property": r["property"],
                "property_type": r.get("property_type"),
                "value": r.get("value", "0"),
            }
        )
        ps.insert(ignore_permissions=True)
        n += 1
    print(f"[Property Setter] 重建 {n} 条")
    frappe.db.commit()


def restore_custom_fields(rows):
    n = 0
    for r in rows:
        if frappe.db.exists("Custom Field", {"dt": r["dt"], "fieldname": r["fieldname"]}):
            continue
        cf = frappe.get_doc(
            {
                "doctype": "Custom Field",
                "dt": r["dt"],
                "fieldname": r["fieldname"],
                "label": r.get("label"),
                "fieldtype": r.get("fieldtype", "Data"),
                "options": r.get("options"),
                "insert_after": r.get("insert_after"),
                "reqd": r.get("reqd", 0),
                "hidden": r.get("hidden", 0),
            }
        )
        cf.insert(ignore_permissions=True)
        n += 1
    print(f"[Custom Field] 重建 {n} 条")
    frappe.db.commit()


def restore_pos_profile(rec):
    name = rec["company"]  # 用 company 作为标识
    if frappe.db.exists("POS Profile", {"company": rec["company"], "name": ["like", "%收银方式1%"]}):
        return False
    doc = frappe.get_doc({"doctype": "POS Profile"})
    for k, v in rec.items():
        if k in ("applicable_for_users", "payments", "item_groups", "customer_groups", "doctype"):
            continue
        setattr(doc, k, v)
    for row in rec.get("payments", []):
        doc.append("payments", {"mode_of_payment": row["mode_of_payment"], "default": row.get("default", 0)})
    for row in rec.get("applicable_for_users", []):
        doc.append("applicable_for_users", {"user": row["user"]})
    doc.insert(ignore_permissions=True)
    print(f"[POS Profile] 重建 {doc.name}")
    frappe.db.commit()
    return True


def restore_role(role_rec):
    if frappe.db.exists("Role", role_rec["role_name"]):
        print(f"[Role] {role_rec['role_name']} 已存在")
    else:
        frappe.get_doc(
            {"doctype": "Role", "role_name": role_rec["role_name"], "desk_access": role_rec.get("desk_access", 0), "is_custom": 1}
        ).insert(ignore_permissions=True)
        print(f"[Role] 重建 {role_rec['role_name']}")
    # Custom DocPerm（先清后建，保证幂等）
    for dp in role_rec.get("docperms", []):
        frappe.db.sql("DELETE FROM `tabCustom DocPerm` WHERE parent=%s AND role=%s", (dp["parent"], role_rec["role_name"]))
        frappe.get_doc(
            {
                "doctype": "Custom DocPerm",
                "parent": dp["parent"],
                "parenttype": "DocType",
                "parentfield": "permissions",
                "role": dp["role"],
                "permlevel": dp.get("permlevel", 0),
                "read": dp.get("read", 1),
                "create": dp.get("create", 1),
                "write": dp.get("write", 1),
                "submit": dp.get("submit", 1),
                "delete": dp.get("delete", 0),
                "amend": dp.get("amend", 0),
            }
        ).insert(ignore_permissions=True)
    frappe.db.commit()
    print(f"[Role] {role_rec['role_name']} DocPerm 重建 {len(role_rec.get('docperms', []))} 条")


def restore_cashier(c):
    email = c["email"]
    if frappe.db.exists("User", email):
        print(f"[Cashier] {email} 已存在，跳过")
        return
    user = frappe.get_doc(
        {
            "doctype": "User",
            "email": email,
            "first_name": c.get("full_name") or email,
            "enabled": c.get("enabled", 1),
            "user_type": c.get("user_type", "System User"),
            "language": c.get("language", "zh"),
            "time_zone": c.get("time_zone"),
            "desk_theme": c.get("desk_theme", "Light"),
            "mute_sounds": c.get("mute_sounds", 0),
            "send_welcome_email": 0,
            "roles": [{"role": r} for r in c.get("roles", [])],
        }
    )
    user.insert(ignore_permissions=True)
    if c.get("default_company"):
        frappe.defaults.set_user_default("company", c["default_company"], user=email)
    frappe.db.commit()
    print(f"[Cashier] 重建 {email}（密码需另行设置: update_password）")


def restore_mop(rows):
    for mop in rows:
        doc = frappe.get_doc("Mode of Payment", mop["mode_of_payment"])
        for acc in mop.get("accounts", []):
            if not frappe.db.exists(
                "Mode of Payment Account", {"parent": mop["mode_of_payment"], "company": acc["company"]}
            ):
                doc.append("accounts", {"company": acc["company"], "default_account": acc["default_account"]})
        doc.save(ignore_permissions=True)
    frappe.db.commit()
    print(f"[MOP] 重建 {len(rows)} 个付款方式账户")


def main():
    print("=== 开始恢复配置快照 v4 ===")
    restore_property_setters(snap.get("property_setters", []))
    restore_custom_fields(snap.get("custom_fields", []))
    for rec in snap.get("pos_profiles", []):
        restore_pos_profile(rec)
    for rec in snap.get("roles", []):
        restore_role(rec)
    for c in snap.get("cashiers", []):
        restore_cashier(c)
    restore_mop(snap.get("mode_of_payment_accounts", []))
    # 隐藏 workspace
    for w in snap.get("hidden_workspaces", []):
        ws = frappe.get_doc("Workspace", w["name"])
        if ws:
            ws.is_hidden = 1
            ws.save(ignore_permissions=True)
    frappe.db.commit()
    print("=== 恢复完成（请执行 bench clear-cache + 重启） ===")


if __name__ == "__main__":
    main()
    frappe.destroy()
    sys.exit(0)
