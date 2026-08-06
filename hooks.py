app_name = "my_custom_app"
app_title = "我的定制"
app_publisher = "yangyang7920"
app_description = "ERPNext 中文定制功能 - 汉化 + 业务定制 + 多规格支持"
app_icon = "fa fa-cog"
app_color = "#3498db"
app_email = "a83986475@gmail.com"
app_license = "GNU General Public License (v3)"
source_link = "https://github.com/a83986475/erpnext-apps"
app_logo_url = "/assets/my_custom_app/logo.png"
app_home = "."

# ------------------- DocType 事件钩子 -------------------
doc_events = {
    # ========== 销售模块 ==========
    "Sales Invoice": {
        "validate": "my_custom_app.api.sales.validate_sales_invoice",
        "on_submit": "my_custom_app.api.sales.on_invoice_submitted",
        "on_cancel": "my_custom_app.api.sales.on_invoice_cancelled",
    },
    "Sales Order": {
        "validate": "my_custom_app.api.sales.validate_sales_order",
    },
    "Quotation": {
        "validate": "my_custom_app.api.sales.validate_quotation",
    },
    "Customer": {
        "validate": "my_custom_app.api.sales.validate_customer",
        "after_insert": "my_custom_app.api.sales.after_customer_created",
    },

    # ========== 采购模块 ==========
    "Purchase Order": {
        "validate": "my_custom_app.api.buying.validate_purchase_order",
    },
    "Purchase Invoice": {
        "validate": "my_custom_app.api.buying.validate_purchase_invoice",
    },
    "Supplier": {
        "validate": "my_custom_app.api.buying.validate_supplier",
    },

    # ========== 库存模块 ==========
    "Item": {
        "validate": "my_custom_app.api.stock.validate_item",
        "after_insert": "my_custom_app.api.stock.auto_create_item_price",
    },
    "Stock Entry": {
        "on_submit": "my_custom_app.api.stock.on_stock_entry_submitted",
    },
    "Delivery Note": {
        "validate": "my_custom_app.api.stock.validate_delivery_note",
    },

    # ========== 通用 ==========
    "Address": {
        "validate": "my_custom_app.api.common.validate_address",
    },
    "Contact": {
        "validate": "my_custom_app.api.common.validate_contact",
    },
}

# ------------------- 类重写 -------------------
extend_doctype_class = {
    "Sales Invoice": "my_custom_app.override.sales_invoice.CustomSalesInvoice",
}

override_whitelisted_methods = {}

# ------------------- 安装/迁移 -------------------
after_install = "my_custom_app.install.after_install"
after_migrate = "my_custom_app.install.after_migrate"

# ------------------- 启动信息 -------------------
extend_bootinfo = "my_custom_app.boot.extended_bootinfo"

# ------------------- 权限 -------------------
permission_query_conditions = {}
has_permission = {}

# ------------------- 调度任务 -------------------
scheduler_events = {
    "daily": [
        "my_custom_app.tasks.daily_tasks",
    ],
    "weekly": [
        "my_custom_app.tasks.weekly_tasks",
    ],
    "cron": {
        "0 2 * * *": [
            "my_custom_app.tasks.custom_cron_task",
        ],
    },
}

# ------------------- UI 扩展 -------------------
global_search_doctypes = {}
website_route_rules = []
standard_navbar_items = []

# Custom JS for standard pages
page_js = {
    "point-of-sale": "public/js/pos_custom.js",
}
