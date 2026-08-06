# solua_home - ERPNext 中文定制

ERPNext v16 中文定制功能扩展包。提供常用模块的中文翻译和自定义字段。

## 功能

- 中文翻译（覆盖销售、采购、库存、财务、制造等模块）
- 自定义字段（客户合同管理、供应商审批等）
- 事件钩子（Sales Invoice 验证等）
- POS 定制（扫码选色、空态提示、隐藏评论框）

## 仓库结构

```
├── api/             # 自定义 API（POS 扫码选色等）
├── public/          # 前端资源（CSS 隐藏评论框等）
├── override/        # 控制器覆盖（Sales Invoice）
├── docs/            # 项目文档与操作手册（中文）
│   ├── ERPNext 定制开发操作手册.md
│   ├── SESSION_SUMMARY.md
│   ├── SHD-SH 迁移评估清单.md
│   ├── SHD-company-deletion-record.md
│   ├── demo-data-cleanup-plan.md
│   └── transaction-deletion-import-logic-summary.md
├── config-snapshot/ # 生产配置快照（Property Setter / Custom Field / POS Profile）
└── scripts/         # 部署/维护脚本（start.sh 等）
```
