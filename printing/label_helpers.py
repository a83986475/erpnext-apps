# -*- coding: utf-8 -*-
# solua_home/printing/label_helpers.py
# 价格标签打印格式的 Jinja helper：
#   get_barcode_img(doc)  -> 条码 base64 PNG data URI（无条码返回空字符串）
#   get_selling_price(doc)-> 现价格式化字符串（无价格返回 "—"）
# 依赖：python-barcode（服务器 bench env 已安装，Pillow 为 frappe 自带）

import base64
from io import BytesIO

import frappe

DEFAULT_PRICE_LIST = "Standard Selling"
DEFAULT_CURRENCY = "MZN"


def get_barcode_img(doc, font_size=8, module_height=8):
    """渲染物料第一个条码为 PNG data URI（可直接放进 <img>）。

    - 优先按物料声明的 barcode_type（如 ean13 / code128）渲染
    - 渲染失败自动回退 code128（万能，任意字符串可编码）
    - 无条码返回空字符串（模板里自动隐藏）
    """
    barcode_value, barcode_type = _get_barcode(doc)
    if not barcode_value:
        return ""

    try:
        import barcode as python_barcode
        from barcode.writer import ImageWriter
    except ImportError:
        return ""

    # 13 位纯数字默认按 EAN-13 渲染（超市风格）；否则用 code128
    candidates = []
    if barcode_type:
        candidates.append(barcode_type)
    elif len(str(barcode_value)) == 13 and str(barcode_value).isdigit():
        candidates.append("ean13")
    if "code128" not in candidates:
        candidates.append("code128")

    for bt in candidates:
        try:
            writer = ImageWriter()
            writer.set_options({
                "module_width": 0.2,
                "module_height": module_height,
                "font_size": font_size,
                "quiet_zone": 1.5,
                "dpi": 300,
            })
            code = python_barcode.get(bt, str(barcode_value), writer=writer)
            buf = BytesIO()
            code.write(buf)
            data = buf.getvalue()
            return f"data:image/png;base64,{base64.b64encode(data).decode()}"
        except Exception:
            continue

    frappe.log_error(f"条码渲染失败: {barcode_value}", "solua_home")
    return ""


def _get_barcode(doc):
    """取物料的条码（变体无条码时继承模板条码）。

    窗帘策略：条码只挂在模板 Item 上，变体共用；
    变体打印标签时自动取模板条码。
    """
    def _first_barcode(item):
        if getattr(item, "barcodes", None):
            for row in item.barcodes:
                if row.barcode:
                    return row.barcode, (row.barcode_type or "").lower()
        return None, ""

    value, btype = _first_barcode(doc)
    if value:
        return value, btype

    variant_of = getattr(doc, "variant_of", None)
    if variant_of:
        try:
            tpl = frappe.get_doc("Item", variant_of)
        except frappe.DoesNotExistError:
            return None, ""
        value, btype = _first_barcode(tpl)
        if value:
            return value, btype

    return None, ""


def get_selling_price(doc, price_list=None, currency=None):
    """取物料现价（Standard Selling），返回格式化字符串。

    无价格时返回 "—"（模板里显示占位符）。
    """
    price_list = price_list or DEFAULT_PRICE_LIST
    currency = currency or frappe.db.get_single_value("Global Defaults", "default_currency") or DEFAULT_CURRENCY

    rate = frappe.db.get_value(
        "Item Price",
        {"item_code": doc.name, "price_list": price_list},
        "price_list_rate",
    )
    if not rate:
        return "—"
    return frappe.utils.fmt_money(rate, currency=currency, precision=0)
