# my_custom_app/api/stock.py
# ============================
# 库存模块的自定义验证和事件处理
# ============================

import frappe
from frappe import _


def validate_item(doc, method=None):
    """物料保存时验证"""
    # 示例：物料编码规则校验
    if doc.item_code and len(doc.item_code) < 3:
        frappe.throw(_("物料编码长度不能少于3位"))

    # 示例：物料名称不能包含特殊字符
    import re
    if doc.item_name and re.search(r'[<>"\'/]', doc.item_name):
        frappe.throw(_("物料名称不能包含特殊字符（< > \" \' /）"))


def on_stock_entry_submitted(doc, method=None):
    """库存入库/出库提交后"""
    # 示例：库存变更后通知
    if doc.stock_entry_type == "Material Transfer":
        frappe.msgprint(_("物料转移单 {0} 已提交").format(doc.name))


def validate_delivery_note(doc, method=None):
    """交货单验证"""
    # 示例：出库前检查库存是否充足
    for item in doc.items:
        actual_qty = frappe.db.get_value(
            "Bin",
            {"item_code": item.item_code, "warehouse": item.warehouse},
            "actual_qty",
        )
        if actual_qty is not None and item.qty > actual_qty:
            frappe.throw(
                _("物料 {0} 在仓库 {1} 的库存不足（需求: {2}, 可用: {3}）").format(
                    item.item_code, item.warehouse, item.qty, actual_qty
                )
            )


def auto_create_item_price(doc, method=None):
    """Variant 创建时自动从模板生成 Item Price"""
    if not doc.variant_of:
        return  # 不是 Variant，跳过

    # 获取模板价格
    if not doc.standard_rate:
        # 如果 Variant 没有价格，尝试从模板继承
        template_rate = frappe.db.get_value("Item", doc.variant_of, "standard_rate")
        if not template_rate:
            return  # 模板也没有价格，跳过

    # 检查是否已有 Item Price
    existing = frappe.db.get_value("Item Price",
        {"item_code": doc.name, "price_list": "Standard Selling", "selling": 1},
        "name"
    )
    if existing:
        return  # 已存在，不重复创建

    # 获取默认货币
    currency = frappe.defaults.get_user_default("currency") or "MZN"

    # 创建 Item Price
    try:
        price_doc = frappe.get_doc({
            "doctype": "Item Price",
            "item_code": doc.name,
            "price_list": "Standard Selling",
            "price_list_rate": doc.standard_rate,
            "selling": 1,
            "currency": currency,
        })
        price_doc.insert(ignore_permissions=True)
    except Exception as e:
        frappe.log_error(f"Item Price 自动创建失败 [{doc.name}]: {e}", "my_custom_app.auto_price")
