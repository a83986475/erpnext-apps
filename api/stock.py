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
