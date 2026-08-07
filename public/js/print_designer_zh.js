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
