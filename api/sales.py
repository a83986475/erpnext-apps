# solua_home/api/sales.py
# ============================
# 销售模块的自定义验证和事件处理
# ============================

import frappe
from frappe import _
from frappe.utils import cint, flt

# 收银员折扣限额（%）：超过此比例的折扣必须管理员审批后提交
# 2026-08-08 按需求收紧：任何折扣（>0）都必须管理员审批，收银员无自由打折权
MAX_DISCOUNT_PERCENTAGE = 0
# 有权限直接审批超限折扣的角色
DISCOUNT_APPROVER_ROLES = {"Sales Master Manager", "Accounts Manager", "System Manager"}


def before_validate_sales_invoice(doc, method=None):
    """销售发票保存前执行：行折扣保险

    ERPNext v16.28 的 calculate_item_rate 以 rate 优先：
    若行 rate（单价）不等于按 discount_percentage 算出的折后价，会清除行折扣。
    POS 里收银员输入折扣 % 时 rate 仍是原价 → 折扣被清。
    这里在保存前把仍为原价的 rate 同步为折后价，让折扣正确保留。
    """
    for item in doc.get("items", []):
        dp = flt(item.get("discount_percentage"))
        if dp <= 0 or item.get("is_free_item"):
            continue
        price_list_rate = flt(item.get("price_list_rate"))
        rate = flt(item.get("rate"))
        if price_list_rate and rate and abs(rate - price_list_rate) < 0.01:
            # rate 仍是原价 → 同步为折后价（保留四位小数精度）
            item.rate = flt(price_list_rate * (1 - dp / 100.0), item.precision("rate"))


def get_max_discount_percentage(doc):
    """计算单据上的最大折扣比例（整单 + 行折扣取最大值，%）"""
    pct = 0.0
    # 整单折扣（百分比形式）
    if doc.get("additional_discount_percentage"):
        pct = max(pct, flt(doc.get("additional_discount_percentage")))
    # 整单折扣（金额形式，按净额折算）
    if doc.get("discount_amount") and doc.get("net_total"):
        pct = max(pct, flt(doc.discount_amount) / flt(doc.net_total) * 100)
    # 行折扣
    for item in doc.get("items", []):
        if item.get("discount_percentage"):
            pct = max(pct, flt(item.get("discount_percentage")))
        if item.get("discount_amount") and item.get("amount"):
            pct = max(pct, flt(item.discount_amount) / flt(item.amount) * 100)
    return pct


def is_discount_approver():
    """当前用户是否有超限折扣审批权限"""
    user_roles = set(frappe.get_roles(frappe.session.user))
    return bool(user_roles & DISCOUNT_APPROVER_ROLES)


def validate_sales_invoice(doc, method=None):
    """销售发票保存时验证"""
    # 示例1：大额审批控制
    if doc.grand_total > 100000:
        frappe.throw(_("金额超过 100,000，需要额外审批"))

    # 示例2：检查客户信用额度
    customer_credit_limit = frappe.db.get_value(
        "Customer", doc.customer, "custom_credit_limit"
    )
    if customer_credit_limit and doc.outstanding_amount > customer_credit_limit:
        frappe.throw(
            _("客户 {0} 的信用额度为 {1}，当前欠款 {2} 已超限").format(
                doc.customer, customer_credit_limit, doc.outstanding_amount
            )
        )

    # 折扣审批门：任何折扣（幅度 > 限额）都需管理员审批后提交
    # 限额=0 时即「任何折扣都需审批」，收银员无自由打折权
    max_pct = get_max_discount_percentage(doc)
    if max_pct > MAX_DISCOUNT_PERCENTAGE:
        approved = cint(doc.get("custom_discount_approved"))
        if not is_discount_approver() and not approved:
            if doc.get("_action") == "submit":
                frappe.throw(
                    _("折扣 {0}% 未经审批，需管理员在发票上勾选「折扣超限已审批」后提交").format(
                        max_pct
                    )
                )
            else:
                frappe.msgprint(
                    _("折扣 {0}% 未经审批，提交前需管理员审批").format(max_pct)
                )

    # 示例3：检查自定义字段
    if doc.get("custom_approver") and not doc.get("custom_approval_date"):
        frappe.msgprint(_("请填写审批日期"))


def on_invoice_submitted(doc, method=None):
    """销售发票提交后执行"""
    frappe.msgprint(_("发票 {0} 已成功提交").format(doc.name))

    # 示例：提交后自动更新客户上次交易日期
    frappe.db.set_value(
        "Customer", doc.customer, "custom_last_transaction_date", frappe.utils.nowdate()
    )

    # 示例：调用外部 API
    # if doc.custom_sync_required:
    #     sync_to_external_system(doc)


def on_invoice_cancelled(doc, method=None):
    """销售发票取消时执行"""
    frappe.msgprint(_("发票 {0} 已取消").format(doc.name))


def validate_sales_order(doc, method=None):
    """销售订单保存时验证"""
    # 交货日期至少在当前日期3天后（date_diff 返回整数，兼容字符串/日期）
    if doc.delivery_date:
        from frappe.utils import date_diff, today

        if date_diff(doc.delivery_date, today()) < 3:
            frappe.throw(_("交货日期必须至少在当前日期3天后"))


def validate_quotation(doc, method=None):
    """报价单验证"""
    # 报价有效期不能超过30天（date_diff 返回整数，兼容字符串/日期）
    if doc.valid_till and doc.transaction_date:
        from frappe.utils import date_diff

        if date_diff(doc.valid_till, doc.transaction_date) > 30:
            frappe.throw(_("报价有效期不能超过30天"))


def validate_customer(doc, method=None):
    """客户保存时验证"""
    # 示例：统一客户名称格式（去掉前后空格、全角转半角）
    if doc.customer_name:
        doc.customer_name = doc.customer_name.strip()

    # 示例：检查重复客户
    if doc.is_new():
        existing = frappe.db.exists(
            "Customer",
            {"customer_name": doc.customer_name, "name": ["!=", doc.name]},
        )
        if existing:
            frappe.throw(_("客户名称 {0} 已存在").format(doc.customer_name))


def after_customer_created(doc, method=None):
    """客户创建后自动操作"""
    # Walkin 客户（散客）不创建联系人
    if doc.customer_name == "Walkin" or doc.name == "Walkin":
        return

    # 自动创建默认联系人（用正确的子表过滤语法）
    existing = frappe.get_all("Contact",
        filters=[
            ["Dynamic Link", "link_doctype", "=", "Customer"],
            ["Dynamic Link", "link_name", "=", doc.name],
        ],
        limit=1
    )
    if not existing:
        contact = frappe.get_doc({
            "doctype": "Contact",
            "first_name": doc.customer_name,
            "is_primary_contact": 1,
            "links": [{"link_doctype": "Customer", "link_name": doc.name}],
        })
        contact.insert(ignore_permissions=True)
        frappe.msgprint(_("已为客户 {0} 自动创建联系人").format(doc.customer_name))
