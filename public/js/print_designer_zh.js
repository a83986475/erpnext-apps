// ============================================================================
// solua_home / public/js/print_designer_zh.js
// Print Designer 界面汉化（运行时文本覆写）
//
// 背景：print_designer 的 UI 字符串大部分是硬编码英文（编译时固化为 label），
//       frappe 翻译文件（zh.csv）无法覆盖。此脚本在页面加载后用
//       MutationObserver 监听 DOM 变化，把已知英文文本替换为中文。
//
// 优点：不改 print_designer 源码、官方升级不冲突、无需重新 build。
// 局限：只能替换"纯文本"节点；若未来官方改用 __() 国际化，此脚本可移除。
//
// 注册方式（hooks.py）：
//   page_js = {
//       "point-of-sale": "public/js/pos_custom.js",
//       "print-designer": "public/js/print_designer_zh.js",
//   }
// ============================================================================

frappe.provide("solua_home.print_designer_zh");

(function () {
	"use strict";

	// 翻译映射（英文原文 -> 中文）
	// 来源：print_designer.bundle 中的 label 硬编码字符串 + __() 运行时字符串
	const ZH = {
		// ---- 页面/对话框 ----
		"Create or Edit Print Format": "创建或编辑打印格式",
		"Select Document Type": "选择单据类型",
		"Select Print Format": "选择打印格式",
		"Print Format Name": "打印格式名称",
		"Create New": "新建",
		"Edit Existing": "编辑现有",
		"Action": "操作",
		"Create": "创建",
		"Edit": "编辑",
		"Save": "保存",
		"Delete": "删除",
		"Cancel": "取消",
		"Refresh": "刷新",
		"Print": "打印",
		"PDF": "PDF",
		"Language": "语言",
		"Name": "名称",

		// ---- 工具栏元素 ----
		"Mouse Pointer (M)": "鼠标指针 (M)",
		"Rectangle (R)": "矩形 (R)",
		"Barcode (B)": "条码 (B)",
		"Image (I)": "图片 (I)",
		"Components (C)": "组件 (C)",
		"Table (A)": "表格 (A)",
		"Dynamic Text": "动态文本",
		"Static Text": "静态文本",
		"Label Element": "标签元素",
		"Main Element": "主体元素",
		"Column": "列",
		"Row": "行",
		"Rows": "行数",
		"Full Page": "整页",
		"Form": "表单",
		"Current Table": "当前表格",
		"Primary Table": "主表格",
		"Table Header": "表头",
		"All Rows": "所有行",
		"Alternate Rows": "交替行",
		"Field Labels": "字段标签",
		"Apply Style to Header": "将样式应用于表头",
		"Delete Page": "删除页面",
		"Current Page": "当前页",
		"Total Pages": "总页数",
		"Print Date": "打印日期",
		"Print Time": "打印时间",
		"First": "首页",
		"Last": "末页",
		"Odd": "奇数页",
		"Even": "偶数页",
		"Set as Default": "设为默认",
		"Try the new Print Designer": "试试新的打印设计器",
		"Edit Format": "编辑格式",
		"Loading Print Format": "正在加载打印格式",
		"Search Doctypes": "搜索单据类型",
		"Search Field by label, fieldname or fieldtype": "按标签、字段名或字段类型搜索",
		"Enter Label": "输入标签",
		"Please select DocType first": "请先选择单据类型",
		"Print Format not saved": "打印格式未保存",

		// ---- 属性面板 ----
		"Page Size": "页面尺寸",
		"Page UOM": "页面单位",
		"Height": "高度",
		"Weight": "粗细",
		"Width": "宽度",
		"Auto": "自动",
		"Auto ( min-height)": "自动（最小高度）",
		"Fixed": "固定",
		"Inline": "行内",
		"Z Index": "层级",
		"Font": "字体",
		"Thin": "细",
		"Extra Light": "特细",
		"Light": "细体",
		"Regular": "常规",
		"Medium": "中等",
		"Semi Bold": "半粗",
		"Bold": "粗体",
		"Extra Bold": "特粗",
		"Black": "特黑",
		"Border Color": "边框颜色",
		"Image Fit": "图片适配",
		"Contain (fit within bounds)": "包含（完整显示）",
		"Cover (fill entire area)": "覆盖（填满区域）",
		"Avoid Page Break": "避免分页",
		"Render Jinja": "渲染 Jinja",
		"Yes": "是",
		"Barcode Format": "条码格式",

		// ---- 单位 ----
		"Pixels (px)": "像素 (px)",
		"Milimeter (mm)": "毫米 (mm)",
		"Centimeter (cm)": "厘米 (cm)",
		"Inch (in)": "英寸 (in)",

		// ---- 条码格式 ----
		"QR Code": "二维码",
		"EAN": "EAN",
		"GTIN": "GTIN",
		"UPCA": "UPC-A",
		"ISBN": "ISBN",
		"ISSN": "ISSN",
		"ITF": "ITF",
		"JAN": "JAN",
		"PZN": "PZN",

		// ---- 提示/状态 ----
		"Please enable pop-ups": "请启用弹窗",
		"Please resolve overlapping elements ": "请解决元素重叠问题",
		"Atleast 1 element is required inside body": "正文中至少需要 1 个元素",
		"Are you sure you want to delete the page?": "确定要删除这个页面吗？",
		"Do you want to save copy of it ?": "是否保存一份副本？",
		"Error Generating PDF...": "生成 PDF 出错...",
		"in header": "在页眉",
		"in footer": "在页脚",
		"in table, auto layout failed": "在表格中，自动布局失败",
		"Letter Head": "信纸抬头",
		"Loading...": "加载中...",
	};

	// 只处理有实际翻译的文本
	const translateText = (text) => {
		const trimmed = text.trim();
		if (ZH[trimmed]) return ZH[trimmed];
		return null;
	};

	// 替换文本节点的内容（保留原节点的换行结构）
	const replaceInNode = (node) => {
		if (node.nodeType !== Node.TEXT_NODE) return;
		const parent = node.parentNode;
		if (!parent) return;
		// 跳过脚本/样式
		const tag = parent.tagName;
		if (tag === "SCRIPT" || tag === "STYLE" || tag === "TEXTAREA" || tag === "INPUT") return;

		const translated = translateText(node.nodeValue);
		if (translated) {
			node.nodeValue = node.nodeValue.replace(node.nodeValue.trim(), translated);
		}
	};

	let observer = null;
	let applyTimer = null;
	let applied = false;

	const applyToTree = (root) => {
		if (!root) return;
		// 处理根节点本身
		replaceInNode(root);
		// 遍历所有文本节点
		const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
		let n;
		while ((n = walker.nextNode())) {
			replaceInNode(n);
		}
	};

	const start = () => {
		if (applied) return;
		applied = true;

		// 确认页面存在（print-designer 路由）
		if (!frappe.pages["print-designer"] || !frappe.router || frappe.router.current_route[0] !== "print-designer") {
			return;
		}

		// 初次应用
		applyToTree(document.body);

		// 监听后续 Vue 渲染产生的节点
		observer = new MutationObserver((mutations) => {
			if (applyTimer) return; // 节流
			applyTimer = setTimeout(() => {
				applyTimer = null;
				for (const m of mutations) {
					for (const added of m.addedNodes) {
						if (added.nodeType === Node.ELEMENT_NODE) {
							applyToTree(added);
						} else if (added.nodeType === Node.TEXT_NODE) {
							replaceInNode(added);
						}
					}
				}
			}, 50);
		});

		observer.observe(document.body, { childList: true, subtree: true });
	};

	// ============================================================
	// 方案 A：过滤 DocType 下拉，只显示常用单据
	// ============================================================
	// print_designer 的新建对话框里「选择单据类型」是 Link 控件
	// （options: DocType, filters: {istable: 0}），会列出全部 459 个 DocType。
	//
	// 机制（frappe link.js）：每次搜索走 get_search_args() -> set_custom_query(args)，
	//   - df.get_query 为对象时合并其 filters（line 762-835）
	//   - df.filters 存在时直接合并进 args.filters（line 840-843）
	// print_designer 的对话框传的是 df.filters，所以在这里合并 name 白名单。
	// 只影响本页面（脚本经 page_js 只在 print-designer 加载）的 DocType 链接，
	// 其他页面的 DocType 下拉不受影响。
	const ALLOWED_DOCTYPES = [
		"Item", "Item Group", "Item Attribute", "Item Price",
		"Customer", "Customer Group", "Supplier", "Supplier Group",
		"Sales Invoice", "Sales Order", "Quotation", "Delivery Note",
		"Purchase Invoice", "Purchase Order", "Purchase Receipt", "Supplier Quotation",
		"Payment Entry", "Journal Entry", "Sales Partner", "Price List",
		"POS Profile", "POS Opening Entry", "POS Closing Entry",
		"Stock Entry", "Stock Reconciliation", "Warehouse",
		"Employee", "User", "Address", "Contact", "Project", "Task", "Company",
	];

	const applyDoctypeFilter = () => {
		if (!frappe.ui || !frappe.ui.form || !frappe.ui.form.LinkControl) return false;
		const orig = frappe.ui.form.LinkControl.prototype.set_custom_query;
		if (!orig || orig.__solua_filtered) return true;

		frappe.ui.form.LinkControl.prototype.set_custom_query = function (args) {
			const isDocTypePicker = this.df && this.df.options === "DocType";
			if (isDocTypePicker) {
				// 路径 1（print_designer 实际用的）：df.filters 直接合并（line 840）
				if (this.df.filters && !this.df.filters.name) {
					// 浅拷贝后再加白名单，避免污染 Dialog 的原始 df 定义
					this.df.filters = { ...this.df.filters, name: ["in", ALLOWED_DOCTYPES] };
				}
				// 路径 2（兜底）：df.get_query / this.get_query 传 filters 的情况
				const gq = this.get_query || this.df.get_query;
				if (gq && $.isPlainObject(gq) && gq.filters && !gq.filters.name && !gq.__solua_patched) {
					gq.filters = { ...gq.filters, name: ["in", ALLOWED_DOCTYPES] };
					gq.__solua_patched = true; // 标记在 gq 外层，不会随 filters 发到服务器
				}
			}
			return orig.apply(this, arguments);
		};
		frappe.ui.form.LinkControl.prototype.set_custom_query.__solua_filtered = true;
		return true;
	};

	// ============================================================
	// 交互优化：Link 输入框有内容时，点击也弹出下拉
	// ============================================================
	// frappe link.js 的 focus 处理器只在输入框为空时才触发 on_input()（弹下拉）；
	// 已有内容时点击毫无反应，必须清空才能重新选。这里覆写 make_input，
	// 给 Link 输入框追加 click 处理器：有内容时点击同样调用 on_input() 弹出下拉。
	// （仅本页面生效：脚本经 page_js 只在 print-designer 加载）
	const enhanceLinkClickToOpen = () => {
		if (!frappe.ui || !frappe.ui.form || !frappe.ui.form.LinkControl) return false;
		const proto = frappe.ui.form.LinkControl.prototype;
		if (proto.make_input.__solua_click) return true;

		const origMakeInput = proto.make_input;
		const wrapped = function () {
			origMakeInput.apply(this, arguments);
			const me = this;
			// 只对已存在的输入框绑一次，避免重复绑定
			if (this.$input && !this.$input.data("solua_click_open")) {
				this.$input.data("solua_click_open", true);
				this.$input.on("click", function () {
					// 有内容时点击弹下拉；空值由 frappe 原 focus 逻辑处理（避免重复触发）
					if (me.$input.val()) {
						me.on_input();
					}
				});
			}
		};
		wrapped.__solua_click = true;
		proto.make_input = wrapped;
		return true;
	};

	// LinkControl 可能在脚本加载时尚未就绪，轮询等它加载（最多 10 秒）
	const ensurePatches = () => {
		const done = applyDoctypeFilter() & enhanceLinkClickToOpen();
		if (done) return;
		let tries = 0;
		const iv = setInterval(() => {
			tries++;
			const d1 = applyDoctypeFilter();
			const d2 = enhanceLinkClickToOpen();
			if ((d1 && d2) || tries > 20) clearInterval(iv);
		}, 500);
	};
	ensurePatches();

	// print-designer 页面加载时执行
	const origLoad = frappe.pages["print-designer"] && frappe.pages["print-designer"].on_page_load;
	if (origLoad) {
		frappe.pages["print-designer"].on_page_load = function (wrapper) {
			origLoad.call(this, wrapper);
			// 等 Vue 应用挂载后开始监听
			setTimeout(start, 500);
			setTimeout(start, 2000); // 兜底再跑一次
		};
	} else {
		frappe.pages["print-designer"] = frappe.pages["print-designer"] || {};
		frappe.pages["print-designer"].on_page_load = function () {
			setTimeout(start, 500);
			setTimeout(start, 2000);
		};
	}
})();
