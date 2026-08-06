# -*- coding: utf-8 -*-
import frappe


def extended_bootinfo(bootinfo):
    """注入自定义 boot 信息"""
    bootinfo["solua_home"] = {
        "version": "0.0.1",
        "app_name": "solua_home",
        "curtain_colors": get_curtain_colors(),
    }


def get_curtain_colors():
    """获取窗帘颜色列表 (Cor Item Attribute 的值)"""
    try:
        attr = frappe.get_cached_doc("Item Attribute", "Cor")
        return [
            {"value": v.attribute_value, "abbr": v.abbr}
            for v in attr.item_attribute_values
        ]
    except Exception:
        return []
