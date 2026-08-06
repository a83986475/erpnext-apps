# erp.solua.one 生产环境 demo/测试数据清理清单

> 生成时间：2026-08-06 | 目标站点：erp.solua.one（数据库 `_62af7cb1044ac230`）
> 原则：**只清理 demo/测试数据，保留窗帘产品线（CR-001 全家）、Walkin、公司/科目/仓库/税/价格表/翻译等正式档案**。
> 🔄 **后续变更（2026-08-06）**：自定义 App 已由 `my_custom_app` 重命名为 **`solua_home`**（GitHub 仓库同步改名 `a83986475/solua-erp`），与本清理无关，仅记录命名上下文。
> 🔄 **后续变更（2026-08-07）**：**Demo 公司 `Solua Home, Lda (Demo)` 已整体删除**（含其科目/仓库/税/POS Profile/单据），详见《SHD-company-deletion-record.md》。本清单中的「保留项」（收银方式1-Test、pos.test 等）凡属 SHD 的均已随公司删除。

---

## 一、待清理对象（已盘点核实）

### 1. 物料（Item）— 11 个
| 项 | 数量 | 说明 |
|----|------|------|
| SKU001 ~ SKU010 | 10 | 2026-07-16 由 demo 数据导入，属 `Demo Item Group`，有库存与单据引用 |
| test | 1 | 2026-08-06 测试物料，无引用 |

- 关联：**Item Price 20 条**（SKU 各 Buying+Selling 价）、**Bin 22 条**、**Stock Ledger Entry ~50 条**、**Item Barcode 0 条**、Item Default/Reorder/Tax/Supplier/Customer 子表 0 条。

### 2. 客户（Customer）— 5 个
| 项 | 说明 |
|----|------|
| Palmer Productions Ltd. / West View Software Ltd. / Grant Plastics Ltd. | demo 客户（Demo Customer Group） |
| test / test-1 | 测试客户 |

### 3. 供应商（Supplier）— 3 个
Summit Traders Ltd. / MA Inc. / Zuckerman Security Ltd.（全部 Demo Supplier Group）

### 4. 联系人（Contact）— 2 个
test-test（→ test）、test-1-test-1（→ test-1）。保留：YangYang Chen（开发者）、POS Test（pos.test 用户档案）。

### 5. 已提交业务单据 — 32 张（全部 demo，仅引用 demo 物料/往来单位）
| 类型 | 数量 | 名称 |
|------|------|------|
| Payment Entry | 5 | ACC-PAY-2026-00001 ~ 00005 |
| Sales Invoice | 5 | ACC-SINV-2026-00001 ~ 00005 |
| Purchase Invoice | 6 | ACC-PINV-2026-00001 ~ 00006 |
| Sales Order | 5 | SAL-ORD-2026-00001 ~ 00005 |
| Purchase Order | 10 | PUR-ORD-2026-00001 ~ 00010 |
| Stock Entry | 1 | MAT-STE-2026-00001（Material Receipt，SKU 入库 180） |

### 6. 分组（Group）— 3 个
Demo Item Group / Demo Customer Group / Demo Supplier Group（物料与往来单位删除后为空，可删）。

### 7. 台账/流水残留（SQL 兜底清理）
- `tabStock Ledger Entry`：item_code LIKE 'SKU%'
- `tabGL Entry`：voucher_no ∈ 上述 demo 单据（46 条中 42 条；保留 MAT-RECO-2026-00002 的 2 条）
- `tabPayment Ledger Entry`：voucher_no ∈ demo 单据
- `tabBin`：item_code LIKE 'SKU%'（on_trash 会删，SQL 兜底）
- `tabVersion`：demo docname 记录（21 条）

---

## 二、安全检查结论（引用分析）

| 检查项 | 结果 |
|--------|------|
| SKU 物料被哪些单据引用 | SI/SO/PI/PO 各 10 条明细（全 demo，随单据删除）|
| SKU 库存来源 | PI ×6（入库）、SI ×5（出库）、MAT-STE-2026-00001（+180）→ 全部随单据删除 + SQL 清 ledger |
| demo 客户/供应商引用 | 仅上述 demo 单据 + PE；删单据后可安全删除 |
| 是否误伤正式数据 | **否**：CR-001 + 6 变体、Walkin、公司/科目/仓库/价格表/VAT 税模板/翻译/Item Variant Settings/自定义字段/收银方式1 全部保留 |
| 序列号/批次/资产/BOM | 0（SKU 无序列号、无批次、无资产） |
| 删除方式 | `frappe.delete_doc(force=True)`（Item.on_trash 确认只清理 Bin/Item Price，不检查库存台账）+ SQL 清 ledger/GL 残留 |
| 风险兜底 | 执行前 `bench --site erp.solua.one backup` 全量备份 |

**明确保留（不在清理范围）**：Walkin 客户、CR-001 全家（模板+6 变体+价格+条码+盘点单 MAT-RECO）、收银方式1、pos.test@solua.one 用户与收银方式1-Test Profile（如需一并清理，单独确认）、Item Attribute（Cor 等）、Mozambique Tax 税模板、Sales Team。

---

## 三、执行顺序（依赖关系）

```
1. 备份：bench --site erp.solua.one backup
2. 删除单据（先删引用方）：
   Payment Entry(5) → Sales Invoice(5) → Purchase Invoice(6)
   → Sales Order(5) → Purchase Order(10) → Stock Entry MAT-STE(1)
3. 删除物料：SKU001-010 + test（on_trash 自动清 Bin/Item Price）
4. 删除联系人：test-test、test-1-test-1
5. 删除客户：Palmer / West View / Grant / test / test-1
6. 删除供应商：Summit / MA Inc. / Zuckerman
7. 删除分组：Demo Item Group / Demo Customer Group / Demo Supplier Group
8. SQL 兜底清理：Stock Ledger Entry(SKU)、GL Entry(demo voucher)、
   Payment Ledger Entry(demo voucher)、Bin(SKU)、Version(demo docname)
9. 验证（见第四节）
```

---

## 四、清理后验证标准

| 检查项 | 清理前 | 清理后应达到 |
|--------|--------|--------------|
| Item 总数 | 18 | **7**（CR-001 + 6 变体）|
| Customer | 6 | **1**（Walkin）|
| Supplier | 3 | **0** |
| Item Price | 26 | **6**（仅 CR-001 变体）|
| Stock Ledger Entry (CR-001) | 6 | 6（MAT-RECO 保留，数量 0）|
| GL Entry | 46 | **2**（MAT-RECO-2026-00002）|
| Bin (SKU) | 22 | **0** |
| 已提交单据（SI/SO/PI/PO/PE/Stock Entry）| 32 | **0** |

---

## 五、可选后续项（本次不执行）
- 删除测试用户 `pos.test@solua.one` + `收银方式1-Test` POS Profile（SESSION_SUMMARY 待办项，需单独确认）
- CR-001 变体库存当前为 0，正式营业前需重新盘点入库

---

## 六、执行记录（2026-08-06 23:1x）

1. **备份**：`20260806_231541-erp_solua_one-database.sql.gz`（1.1MiB）✅
2. **执行方式**：
   - 物料/往来单位/分组：`frappe.delete_doc(force=True)`（Item.on_trash 自动清理 Bin/Item Price）
   - 已提交单据（PE/SI/PI/SO/PO/Stock Entry 共 32 张）：`frappe.delete_doc` 拒删已提交文档 → 改用 SQL 按 `frappe.get_meta().get_table_fields()` 动态删除主表+全部子表
   - 台账/GL/版本残留：SQL 清理（Stock Ledger Entry、GL Entry、Payment Ledger Entry、Bin、Version）
3. **实测结果**（全部符合预期）：
   - 单据 32 张全删，子表残留 0；Item 7（CR-001 全家）、Customer 1（Walkin）、Supplier 0、Item Price 6、Bin 6、GL 2（仅 MAT-RECO）、SLE 6（仅 CR-001）、PLE 0、Version 0
   - 补删过程中发现命名列表生成错误（`PUR-ORD-2026-00010` 写成 `000010`），已补删
   - `bench clear-cache` 已执行，supervisor 全部 RUNNING
4. **遗留问题（与清理无关）**：SKU 删除前的库存有正有负（demo 单据日期乱序所致），已随单据/台账一起清除，不影响正式数据。
