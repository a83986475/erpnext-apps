# -*- coding: utf-8 -*-
# Copyright (c) 2026, yangyang7920 and contributors
# For license information, please see license.txt

import frappe
from frappe import _


@frappe.whitelist()
def get_template_variants(template_item):
    """获取指定模板物料的所有变体

    Args:
        template_item: 模板物料编码

    Returns:
        list: 变体列表，每个变体包含 item_code, item_name, attributes 等信息
    """
    if not template_item:
        return []

    variants = frappe.get_all(
        "Item",
        filters={
            "variant_of": template_item,
            "disabled": 0,
        },
        fields=["item_code", "item_name", "custom_chinese_name",
                "custom_spec_summary", "custom_pos_short_name",
                "image", "custom_swatch_image",
                "stock_uom", "disabled",
                "item_group", "brand"],
        order_by="item_code asc",
    )

    # 为每个变体获取属性值
    result = []
    for v in variants:
        attrs = frappe.get_all(
            "Item Variant Attribute",
            filters={"parent": v.item_code},
            fields=["attribute", "attribute_value"],
        )
        v["attributes"] = {a.attribute: a.attribute_value for a in attrs}
        result.append(v)

    return result


@frappe.whitelist()
def get_template_stock_summary(template_item, warehouse=None):
    """获取模板物料下所有变体的库存汇总

    Args:
        template_item: 模板物料编码
        warehouse: 可选，指定仓库

    Returns:
        dict: {
            "template_code": "...",
            "template_name": "...",
            "total_stock": 123,
            "variants": [
                {
                    "item_code": "...",
                    "item_name": "...",
                    "attributes": {...},
                    "actual_qty": 10,
                    "warehouse": "..." (if specified)
                },
                ...
            ]
        }
    """
    if not template_item:
        frappe.throw(_("Please specify a template item"))

    template = frappe.get_doc("Item", template_item)
    if not template.has_variants:
        frappe.throw(_("{0} is not a template item").format(template_item))

    variants = get_template_variants(template_item)
    total_stock = 0

    filters = {"item_code": ["in", [v.item_code for v in variants]]}
    if warehouse:
        filters["warehouse"] = warehouse

    stock_data = {}
    try:
        bins = frappe.get_all(
            "Bin",
            filters=filters,
            fields=["item_code", "warehouse", "actual_qty"],
        )
    except frappe.PermissionError:
        bins = []

    for d in bins:
        key = d.item_code
        if key not in stock_data:
            stock_data[key] = 0
        stock_data[key] += d.actual_qty
        total_stock += d.actual_qty

    for v in variants:
        v["actual_qty"] = stock_data.get(v.item_code, 0)

    return {
        "template_code": template.item_code,
        "template_name": template.item_name,
        "template_spu": template.custom_spu_code,
        "total_stock": total_stock,
        "variants": variants,
    }


@frappe.whitelist()
def get_attribute_values(attribute_name):
    """获取指定属性的所有可选值

    Args:
        attribute_name: 属性名称（如 Color, Size）

    Returns:
        list: 属性值列表 [{attribute_value, abbr}, ...]
    """
    if not attribute_name:
        return []

    if not frappe.db.exists("Item Attribute", attribute_name):
        return []

    attr = frappe.get_doc("Item Attribute", attribute_name)

    return [
        {"attribute_value": v.attribute_value, "abbr": v.abbr}
        for v in attr.item_attribute_values
    ]


@frappe.whitelist()
def search_items_by_spu(spu_code):
    """通过 SPU 编码搜索模板物料及其变体

    Args:
        spu_code: SPU 编码

    Returns:
        dict: 模板和变体信息
    """
    if not spu_code:
        return None

    templates = frappe.get_all(
        "Item",
        filters={"custom_spu_code": spu_code, "has_variants": 1},
        fields=["item_code", "item_name", "custom_chinese_name", "custom_spu_code"],
        limit=1,
    )

    if not templates:
        return {
            "template": None,
            "variant_count": 0,
            "variants": [],
        }

    template = templates[0]
    variants = get_template_variants(template.item_code)

    return {
        "template": template,
        "variant_count": len(variants),
        "variants": variants,
    }
