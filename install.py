import frappe

def after_install():
    add_translations()
    add_custom_fields()
    frappe.db.commit()

def after_migrate():
    after_install()

def add_translations():
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
        "Purchase Receipt": "采购收货单",
        "Supplier": "供应商",
        "Supplier Name": "供应商名称",
        "Material Request": "物料需求单",
        "Item": "物料",
        "Item Code": "物料编码",
        "Item Name": "物料名称",
        "Item Group": "物料分组",
        "Warehouse": "仓库",
        "Stock Entry": "库存入库单",
        "Stock Reconciliation": "库存盘点",
        "Material Transfer": "物料转移",
        "Material Issue": "物料出库",
        "Batch No": "批号",
        "Serial No": "序列号",
        "Required": "需求数量",
        "Available": "可用数量",
        "Projected": "预计数量",
        "Skip Material Transfer": "跳过物料转移",
        "Phantom Item": "虚拟物料",
        "Sub Assembly": "子装配件",
        "Shipment Tracking": "物流追踪",
        "Journal Entry": "日记账",
        "Payment Entry": "付款单",
        "Payment": "付款",
        "Receive": "收款",
        "Bank Account": "银行账户",
        "Chart of Accounts": "会计科目表",
        "Account": "会计科目",
        "Debit": "借方",
        "Credit": "贷方",
        "Budget": "预算",
        "Fiscal Year": "财年",
        "Cost Center": "成本中心",
        "Cost Allocation": "成本分配",
        "Bill of Materials": "物料清单",
        "Production Order": "生产订单",
        "Work Order": "工单",
        "Lead": "潜在客户",
        "Opportunity": "商机",
        "Contact": "联系人",
        "Address": "地址",
        "Project": "项目",
        "Task": "任务",
        "Employee": "员工",
        "Department": "部门",
        "Designation": "职务",
        "Leave Application": "请假申请",
        "Attendance": "考勤",
        "Expense Claim": "费用报销",
        "Credit Limit": "信用额度",
        "Approver": "审批人",
        "Approval Date": "审批日期",
        "Status": "状态",
        "Remarks": "备注",
        "Reference": "参考号",
        "Description": "描述",
        "Company": "公司",
        "Currency": "货币",
        "Exchange Rate": "汇率",
        "Valid Till": "有效期至",
        "Delivery Date": "交货日期",
        "Customer Group": "客户分组",
        "Territory": "销售区域",
        "Print Format": "打印格式",
        "Email Template": "邮件模板",
        "Enabled": "已启用",
        "Disabled": "已停用",
        "Default": "默认",
        "Active": "活跃",
        "Inactive": "不活跃",
        "Ticketing": "工单",
        "Issue": "问题",
        "Priority": "优先级",
        "Amount exceeds approval limit": "金额超过审批限额",
        "Please check the input data": "请检查输入数据",
        "Operation completed successfully": "操作成功完成",
        "Insufficient stock": "库存不足",
        "Data saved successfully": "数据保存成功",
        "Record submitted": "记录已提交",
        "Record cancelled": "记录已取消",
        "This field is required": "此字段为必填",
        "No records found": "未找到记录",
    }
    for source, target in translations.items():
        try:
            if not frappe.db.exists("Translation", {
                "source_text": source,
                "language": "zh"
            }):
                doc = frappe.get_doc({
                    "doctype": "Translation",
                    "source_text": source,
                    "translated_text": target,
                    "language": "zh",
                    "contributed": 0,
                })
                doc.insert(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(f"Translation insert failed: {source}: {e}", "my_custom_app")
            continue
    frappe.db.commit()

def add_custom_fields():
    fields = [
        {
            "dt": "Customer",
            "fieldname": "custom_contract_status",
            "label": "合同状态",
            "fieldtype": "Select",
            "options": chr(10).join(["", "正常", "即将到期", "已到期", "已续约"]),
            "insert_after": "customer_name",
        },
    ]
    for field in fields:
        try:
            fn = field.get("fieldname")
            dt = field.get("dt")
            if not frappe.db.exists("Custom Field", {"dt": dt, "fieldname": fn}):
                frappe.get_doc({"doctype": "Custom Field", **field, "owner": "Administrator"}).insert(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(f"Custom field insert failed: {field.get("fieldname", "?")}: {e}", "my_custom_app")
            continue
    frappe.db.commit()
