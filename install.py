# -*- coding: utf-8 -*-
import frappe


def after_install():
    """首次安装后执行"""
    add_translations()
    add_custom_fields()
    add_item_attributes()
    add_color_pool()
    add_variant_custom_fields()
    configure_item_variant_settings()
    sync_standard_print_formats()
    frappe.db.commit()


def after_migrate():
    """每次迁移后执行"""
    after_install()


def sync_standard_print_formats():
    """导入 app 自带的标准打印格式（价格标签等）到数据库

    新版 frappe 的 migrate 只同步 app 模块目录下的 print_format，
    app 根目录下的 print_format 需要手动导入（放这里随 migrate 自动执行）。
    """
    import os

    from frappe.modules.import_file import import_file_by_path

    base = os.path.join(os.path.dirname(__file__), "print_format")
    if not os.path.isdir(base):
        return

    for folder in os.listdir(base):
        json_path = os.path.join(base, folder, f"{folder}.json")
        if not os.path.exists(json_path):
            continue
        try:
            import_file_by_path(json_path, force=True, ignore_version=True)
            frappe.db.commit()
        except Exception as e:
            frappe.log_error(f"打印格式导入失败 [{json_path}]: {e}", "solua_home.print_formats")


def add_translations():
    """导入中文翻译到数据库"""
    translations = {
        "Sales Invoice": "销售发票",
        "Sales Order": "销售订单",
        "Delivery Note": "交货单",
        "Quotation": "报价单",
        "Customer": "客户",
        "Customer Name": "客户名称",
        "Overdue": "逾期",
        "Pending": "待处理",
        "Pending Approval": "待审批",
        "Approved": "已审批",
        "Rejected": "已拒绝",
        "Fully Paid": "已全额付款",
        "Partially Paid": "部分付款",
        "Unpaid": "未付款",
        "Overdue Amount": "逾期金额",
        "Outstanding Amount": "未结金额",
        "Grand Total": "总计",
        "Net Total": "净额",
        "Discount Amount": "折扣金额",
        "Purchase Order": "采购订单",
        "Purchase Invoice": "采购发票",
        "Purchase Receipt": "采购收货",
        "Supplier": "供应商",
        "Supplier Name": "供应商名称",
        "Item": "物料",
        "Item Code": "物料编码",
        "Item Name": "物料名称",
        "Item Group": "物料分组",
        "UOM": "单位",
        "Quantity": "数量",
        "Rate": "单价",
        "Amount": "金额",
        "Warehouse": "仓库",
        "Stock": "库存",
        "Address": "地址",
        "Contact": "联系人",
        "Phone": "电话",
        "Email": "邮箱",
        "Status": "状态",
        "Created By": "创建人",
        "Modified By": "修改人",
        "Created": "创建时间",
        "Modified": "修改时间",
        "Enabled": "已启用",
        "Disabled": "已禁用",
        "Active": "激活",
        "Inactive": "未激活",
        "Yes": "是",
        "No": "否",
        "Save": "保存",
        "Cancel": "取消",
        "Submit": "提交",
        "Amend": "修改",
        "Print": "打印",
        "Download": "下载",
        "Upload": "上传",
        "Search": "搜索",
        "Filter": "筛选",
        "Clear": "清除",
        "Close": "关闭",
        "Open": "打开",
        "New": "新建",
        "Edit": "编辑",
        "Delete": "删除",
        "View": "查看",
        "List": "列表",
        "Report": "报表",
        "Dashboard": "仪表盘",
        "Settings": "设置",
        "Help": "帮助",
        "Error": "错误",
        "Warning": "警告",
        "Success": "成功",
        "Information": "信息",
        "Loading": "加载中",
        "No Data": "无数据",
        "This field is required": "此字段为必填",
        "Operation completed successfully": "操作成功完成",
        "Are you sure?": "确定吗？",
        "Confirm": "确认",
        "Continue": "继续",
        "Back": "返回",
        "Next": "下一步",
        "Finish": "完成",
        "Total": "合计",
        "Subtotal": "小计",
        "Tax": "税",
        "Discount": "折扣",
        "Shipping": "运费",
        "Payment": "付款",
        "Reference": "参考",
        "Description": "描述",
        "Notes": "备注",
        "Terms": "条款",
        "Valid Till": "有效期至",
        "Currency": "货币",
        "Exchange Rate": "汇率",
        "Customer Group": "客户分组",
        "Territory": "销售区域",
        "Sales Partner": "销售伙伴",
        "Campaign": "营销活动",
        "Lead": "潜在客户",
        "Opportunity": "商机",
        "Company": "公司",
        "Chart of Accounts": "会计科目表",
        "Journal Entry": "日记账",
        "Payment Entry": "付款单",
        "Budget": "预算",
        "Asset": "资产",
        "Task": "任务",
        "Project": "项目",
        "Issue": "问题",
        "Support Ticket": "支持工单",
        "Serial No": "序列号",
        "Batch No": "批次号",
        "Barcode": "条码",
        "Image": "图片",
        "Attachment": "附件",
        "Comment": "评论",
        "History": "历史",
        "Version": "版本",
        "Workflow": "工作流",
        "Approval": "审批",
        # Item Variant 相关
        "Has Variants": "启用多规格",
        "Variant Of": "所属模板",
        "Variant Based On": "变体依据",
        "Attributes": "规格属性",
        "Item Attribute": "物料属性",
        "Item Attribute Value": "属性值",
        "Attribute": "属性",
        "Attribute Value": "属性值",
        "Abbreviation": "缩写",
        "Numeric Values": "数值属性",
        "From Range": "起始范围",
        "To Range": "结束范围",
        "Increment": "增量",
        "Template Item": "模板物料",
        "Variant Item": "变体物料",
        "Variant": "变体",
        "Variants": "多规格",
        "Item Variant Settings": "物料变体设置",
        "Copy Fields to Variant": "复制字段到变体",
        "Do Not Update Variants": "不更新变体",
        "Allow Rename Attribute Value": "允许重命名属性值",
        # 自定义字段
        "SPU Code": "SPU编码",
        "Chinese Name": "中文名称",
        "Spec Summary": "规格摘要",
        "POS Short Name": "POS收银简称",
        "Main Image": "主图",
        "Color Swatch": "色卡图",
        "Swatch Image": "色卡图",
        "Color": "颜色",
        "Size": "尺码",
        "Material": "材质",
        # 颜色池（Cor 属性）
        "Branco": "白色",
        "Preto": "黑色",
        "Prata": "银色",
        "Cinza": "灰色",
        "Azul": "蓝色",
        "Vermelho": "红色",
        "Verde": "绿色",
        "Amarelo": "黄色",
        "Bege": "米色",
        "Laranja": "橙色",
        "Rosa": "粉色",
        "Roxo": "紫色",
        "Dourado": "金色",
        "Marrom": "棕色",
        "Turquesa": "青色",
        "Creme": "奶油色",
        # 批量生成变体
        "Bulk Create Variants": "批量生成变体",
        "Select Template Item": "选择模板物料",
        "Select Colors": "选择颜色",
        "Create Variants": "创建变体",
    }

    for source, translated in translations.items():
        try:
            if not frappe.db.exists("Translation", {"source_text": source, "language": "zh"}):
                doc = frappe.get_doc({
                    "doctype": "Translation",
                    "source_text": source,
                    "translated_text": translated,
                    "language": "zh",
                    "contributed": 0,
                })
                doc.insert(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(f"翻译导入失败 [{source}]: {e}", "solua_home.translations")

    frappe.db.commit()


def add_custom_fields():
    """初始化自定义字段"""
    custom_fields = [
        {
            "dt": "Customer",
            "fieldname": "custom_contract_status",
            "label": "合同状态",
            "fieldtype": "Select",
            "options": "\n正常\n即将到期\n已到期\n已续约",
            "insert_after": "customer_name",
        },
    ]

    for field in custom_fields:
        try:
            if not frappe.db.exists("Custom Field", {"dt": field["dt"], "fieldname": field["fieldname"]}):
                doc = frappe.get_doc({
                    "doctype": "Custom Field",
                    **field,
                    "owner": "Administrator",
                })
                doc.insert(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(f"自定义字段创建失败 [{field.get('fieldname')}]: {e}", "solua_home.custom_fields")

    frappe.db.commit()


def add_item_attributes():
    """初始化 Item Attribute 框架（不含预填值，由用户自行添加属性值）"""
    attribute_names = ["Color", "Size", "Material", "Season", "Gender"]

    for attr_name in attribute_names:
        try:
            if frappe.db.exists("Item Attribute", attr_name):
                continue

            doc = frappe.get_doc({
                "doctype": "Item Attribute",
                "attribute_name": attr_name,
                "numeric_values": 0,
            })
            doc.insert(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(f"Item Attribute 创建失败 [{attr_name}]: {e}", "solua_home.attributes")

    frappe.db.commit()


def add_variant_custom_fields():
    """添加多规格体系相关的自定义字段到 Item"""
    fields = [
        {
            "dt": "Item",
            "fieldname": "custom_spu_code",
            "label": "SPU编码",
            "fieldtype": "Data",
            "insert_after": "item_code",
            "description": "商品款号/主款编码，同一款不同规格共享此编码",
        },
        {
            "dt": "Item",
            "fieldname": "custom_chinese_name",
            "label": "中文显示名",
            "fieldtype": "Data",
            "insert_after": "item_name",
            "description": "门店或客户看到的中文商品名",
        },
        {
            "dt": "Item",
            "fieldname": "custom_spec_summary",
            "label": "规格摘要",
            "fieldtype": "Data",
            "insert_after": "custom_chinese_name",
            "description": "例如：红-M-纯棉，自动拼装或手动填写",
        },
        {
            "dt": "Item",
            "fieldname": "custom_pos_short_name",
            "label": "POS收银简称",
            "fieldtype": "Data",
            "insert_after": "custom_spec_summary",
            "description": "收银界面显示的简短名称",
        },
        {
            "dt": "Item",
            "fieldname": "custom_swatch_image",
            "label": "色卡图",
            "fieldtype": "Attach Image",
            "insert_after": "image",
            "description": "同款不同颜色的色卡小图",
        },
        {
            "dt": "Item Attribute Value",
            "fieldname": "swatch_image",
            "label": "色卡图",
            "fieldtype": "Attach Image",
            "insert_after": "abbr",
            "description": "该颜色值的色卡小图（POS 颜色弹窗/设计器显示）",
        },
    ]

    for field in fields:
        try:
            if not frappe.db.exists("Custom Field", {"dt": "Item", "fieldname": field["fieldname"]}):
                doc = frappe.get_doc({
                    "doctype": "Custom Field",
                    **field,
                    "owner": "Administrator",
                })
                doc.insert(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(f"Variant 自定义字段创建失败 [{field.get('fieldname')}]: {e}", "solua_home.variant_fields")

    frappe.db.commit()


# 窗帘颜色池（Cor 属性）：全部常用颜色 + 唯一缩写
# 变体编码 = 模板编码-缩写（如 CR-001-PR = Preto 黑）；缩写必须全局唯一
CURTAIN_COLOR_POOL = [
    ("Branco", "BR"),      # 白
    ("Preto", "PR"),       # 黑
    ("Prata", "PT"),       # 银（PT 避免与 Preto 的 PR 冲突）
    ("Cinza", "CZ"),       # 灰
    ("Azul", "AZ"),        # 蓝
    ("Vermelho", "VM"),    # 红
    ("Verde", "VD"),       # 绿
    ("Amarelo", "AM"),     # 黄
    ("Bege", "BG"),        # 米
    ("Laranja", "LJ"),     # 橙
    ("Rosa", "RS"),        # 粉
    ("Roxo", "RX"),        # 紫
    ("Dourado", "DR"),     # 金
    ("Marrom", "MR"),      # 棕
    ("Turquesa", "TQ"),    # 青
    ("Creme", "CM"),       # 奶油
]


def add_color_pool():
    """初始化/更新窗帘颜色池（Cor 属性 16 色，缩写唯一）

    - 属性不存在则创建；已存在则按 CURTAIN_COLOR_POOL 重建颜色值
    - 幂等：可重复执行，不会重复插入
    """
    if not frappe.db.exists("Item Attribute", "Cor"):
        doc = frappe.get_doc({
            "doctype": "Item Attribute",
            "attribute_name": "Cor",
            "numeric_values": 0,
        })
        doc.insert(ignore_permissions=True)

    attr = frappe.get_doc("Item Attribute", "Cor")
    # 校验缩写唯一性
    abbrs = [a for _, a in CURTAIN_COLOR_POOL]
    dupes = {x for x in abbrs if abbrs.count(x) > 1}
    if dupes:
        frappe.log_error(f"颜色池缩写重复: {dupes}", "solua_home.color_pool")
        raise ValueError(f"Color pool abbreviations conflict: {dupes}")

    existing = {v.attribute_value for v in attr.item_attribute_values}
    pool = dict(CURTAIN_COLOR_POOL)
    changed = False

    # 更新/新增
    for v in attr.item_attribute_values:
        if v.attribute_value in pool:
            new_abbr = pool[v.attribute_value]
            if v.abbr != new_abbr:
                v.abbr = new_abbr
                changed = True
            del pool[v.attribute_value]
        else:
            # 不在池子里的旧值移除（避免与池子冲突）
            attr.item_attribute_values.remove(v)
            changed = True

    # 池子里新增的
    for value, abbr in pool.items():
        attr.append("item_attribute_values", {"attribute_value": value, "abbr": abbr})
        changed = True

    if changed:
        attr.save(ignore_permissions=True)
        frappe.db.commit()
    return len(CURTAIN_COLOR_POOL)


def clear_prefilled_attributes():
    """清除服务器上已预填的属性值（改为空框架）"""
    import frappe

    for attr_name in ["Color", "Size", "Material", "Season", "Gender"]:
        try:
            if not frappe.db.exists("Item Attribute", attr_name):
                continue

            attr = frappe.get_doc("Item Attribute", attr_name)
            if attr.item_attribute_values:
                attr.item_attribute_values = []
                attr.save(ignore_permissions=True)
                print(f"  ✓ {attr_name}: values cleared")
            else:
                print(f"  - {attr_name}: already empty")
        except Exception as e:
            print(f"  ✗ {attr_name}: error - {e}")

    frappe.db.commit()
    print("Done: all attribute values cleared")

def configure_item_variant_settings():
    """配置 Item Variant Settings（复制字段到变体）"""
    try:
        settings = frappe.get_single("Item Variant Settings")

        fields_to_copy = [
            "item_name",
            "description",
            "image",
            "stock_uom",
            "brand",
            "item_group",
            "custom_chinese_name",
            "custom_spu_code",
        ]

        existing_fields = {row.field_name for row in settings.fields}
        changed = False

        for field_name in fields_to_copy:
            if field_name not in existing_fields:
                settings.append("fields", {"field_name": field_name})
                changed = True

        if changed:
            settings.save(ignore_permissions=True)
    except Exception as e:
        frappe.log_error(f"Item Variant Settings 配置失败: {e}", "solua_home.variant_settings")

    frappe.db.commit()
