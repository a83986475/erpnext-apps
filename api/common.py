# solua_home/api/common.py
# ============================
# 通用功能：内外部 API、工具函数
# ============================

import frappe
from frappe import _


def validate_address(doc, method=None):
    """地址保存时验证"""
    # 示例：地址必填字段检查
    if not doc.city:
        frappe.throw(_("城市为必填项"))

    # 示例：自动补全地址类型
    if not doc.address_type:
        doc.address_type = "Billing"


def validate_contact(doc, method=None):
    """联系人保存时验证"""
    # 示例：手机号格式检查（简单校验）
    if doc.mobile_no and not doc.mobile_no.startswith("1"):
        frappe.msgprint(
            _("手机号 {0} 格式可能不正确，请确认").format(doc.mobile_no),
            alert=True,
        )


# ------------------- 对外 API（可供外部系统调用） -------------------

@frappe.whitelist(allow_guest=False)
def get_customer_summary(customer_name):
    """获取客户摘要信息（可供外部系统调用）"""
    customer = frappe.get_doc("Customer", customer_name)
    return {
        "customer_name": customer.customer_name,
        "customer_group": customer.customer_group,
        "territory": customer.territory,
        "currency": customer.default_currency,
        "status": "active" if customer.disabled == 0 else "disabled",
    }


@frappe.whitelist(allow_guest=False)
def get_today_sales():
    """获取今日销售汇总"""
    today = frappe.utils.nowdate()
    data = frappe.db.sql("""
        SELECT
            COUNT(name) as invoice_count,
            SUM(grand_total) as total_amount
        FROM `tabSales Invoice`
        WHERE posting_date = %s
            AND docstatus = 1
    """, today, as_dict=True)

    return {
        "date": today,
        "invoice_count": data[0].invoice_count or 0,
        "total_amount": data[0].total_amount or 0,
    }


# ------------------- 工具函数 -------------------

def send_wechat_notification(user, title, message):
    """发送企业微信通知（示例）"""
    # 实际对接企业微信 API
    # webhook_url = frappe.db.get_single_value("WeChat Settings", "webhook_url")
    # requests.post(webhook_url, json={"msgtype": "text", "text": {"content": message}})
    frappe.log_error(f"通知 {user}: {title} - {message}", "企业微信通知")


def log_api_call(endpoint, request_data, response_data):
    """记录 API 调用日志"""
    frappe.get_doc({
        "doctype": "API Log",
        "endpoint": endpoint,
        "request_data": str(request_data),
        "response_data": str(response_data),
        "timestamp": frappe.utils.now_datetime(),
    }).insert(ignore_permissions=True)
