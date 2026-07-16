# my_custom_app/hooks.py
# ========================
# 这是自定义 App 的核心配置文件。所有扩展点都在这里注册。
#
# 使用方法：
# 1. bench new-app my_custom_app  # 创建 app
# 2. 把本文件覆盖到 apps/my_custom_app/my_custom_app/hooks.py
# 3. bench --site dev.localhost install-app my_custom_app
# ========================

app_name = "my_custom_app"
app_title = "我的定制"
app_publisher = "你的名字"
app_description = "ERPNext 中文定制功能 - 包括中文翻译、自定义验证、自动编号等"
app_icon = "fa fa-cog"
app_color = "#3498db"
app_email = "your@email.com"
app_license = "GNU General Public License (v3)"
source_link = "https://github.com/你的用户名/my_custom_app"
app_logo_url = "/assets/my_custom_app/images/logo.svg"
app_home = "/desk/home"

# ------------------- 文档事件钩子（最常用） -------------------
# 格式: "DocType": { "事件名": "模块.函数" }
# 事件名: validate, on_submit, on_cancel, on_trash, before_insert, after_insert, on_update
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
# 用来自定义类替代 ERPNext 原有的 DocType 类
extend_doctype_class = {
    "Sales Invoice": "my_custom_app.override.sales_invoice.CustomSalesInvoice",
}

# ------------------- API 方法重写 -------------------
override_whitelisted_methods = {}

# ------------------- 安装/迁移钩子 -------------------
after_install = "my_custom_app.install.after_install"
after_migrate = "my_custom_app.install.after_migrate"

# ------------------- 站点启动时的 boot 信息 -------------------
extend_bootinfo = []

# ------------------- 权限 -------------------
permission_query_conditions = {}
has_permission = {}

# ------------------- 调度任务（定时任务） -------------------
scheduler_events = {
    "daily": [
        "my_custom_app.tasks.daily_tasks",
    ],
    "daily_long": [],
    "daily_maintenance": [],
    "hourly": [],
    "weekly": [
        "my_custom_app.tasks.weekly_tasks",
    ],
    "monthly": [],
    "cron": {
        # 每天凌晨2点执行
        "0 2 * * *": [
            "my_custom_app.tasks.custom_cron_task",
        ],
    },
}

# ------------------- 全局搜索 -------------------
global_search_doctypes = {}

# ------------------- 网页路由 -------------------
website_route_rules = []

# ------------------- 导航栏项目 -------------------
standard_navbar_items = []

# ------------------- 门户菜单 -------------------
