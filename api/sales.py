# my_custom_app/api/sales.py
# ============================
# 销售模块的自定义验证和事件处理
# ============================

import frappe
from frappe import _


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
