# SHD → SH 迁移评估清单
> POS 收银与窗帘库存从 `Solua Home, Lda (Demo)` 迁移到正式公司 `Solua Home, Lda`
> 生成日期：2026-08-06 ｜ 数据来源：erp.solua.one 生产库实测

---

## 0. 结论速览

**可以迁，风险低**。两家公司是同一安装模板生成的结构孪生体（科目/仓库/税/成本中心一一对应），正式公司 SH 目前是**零业务空壳**，迁移本质是「把 SHD 上的 2 个 POS Profile + 6 个变体库存搬到 SH」，无历史单据、无客户供应商、无账期包袱。

> ⚠️ 重要前置事实：**公司简称 Abbr（SH/SHD）创建后不可修改**。一旦在 SH 产生交易，之后想再改公司名/简称只能重建公司。所以"迁移到 SH"应当是**一次做对**的最终决定。

---

## 1. 两家公司结构对比（实测）

| 维度 | Solua Home, Lda (**SH**) | Solua Home, Lda (Demo) (**SHD**) | 差异 |
|---|---|---|---|
| 本位币 | MZN | MZN | 一致 |
| 科目表 | 193 个（139 末级）| 193 个（139 末级）| **结构一致** |
| 默认收入科目 | 4110 - Sales - SH | 4110 - Sales - SHD | 各归各 |
| 默认成本科目 | 5111 - COGS - SH | 5111 - COGS - SHD | 各归各 |
| 应收/应付/舍入 | 1310/2110/5212 - SH | 1310/2110/5212 - SHD | 各归各 |
| 成本中心 | Main - SH（+ 根组）| Main - SHD（+ 根组）| 一致 |
| 仓库 | 5 个（All/FG/Stores/GIT/WIP）| 5 个（同名）| **结构一致** |
| 销售税模板 | Mozambique Tax - SH（17%）| Mozambique Tax - SHD（17%）| 一致 |
| 采购税模板 | ✅（同样 17%）| ✅ | 一致 |
| 价格表 | Standard Selling/Buying（**全局共享，无公司维度**）| 同 | 共享 |
| 汇率/付款条款 | 空 | 空 | 一致（暂无需） |
| **业务数据** | **0 单据 / 0 库存 / 0 账目** | 2 POS Profile + 6 变体库存 + 1 盘点单 | ⚠️ 全在 SHD |

**结论**：SH 不是缺配置，而是缺"业务"。迁移不需要重建任何科目/仓库/税，只需把 SHD 的资产指针搬到 SH。

---

## 2. SHD 上待迁移资产清单（精确盘点）

| # | 资产 | 明细 | 迁移方式 |
|---|---|---|---|
| 1 | POS Profile ×2 | `收银方式1`、`收银方式1-Test`（company=SHD, warehouse=Finished Goods - SHD, selling_price_list=Standard Selling）| 改 company + warehouse 字段 |
| 2 | POS 支付方式 ×4 | Cash（默认）+ Credit Card，挂在 POS Profile 子表（`tabPOS Payment Method`）| **随 Profile 自动走，无需单独迁** |
| 3 | 窗帘变体库存 ×6 | CR-001-AZ/BR/BG/VM/CZ/PR 各 **10 件** @ Finished Goods - SHD（Bin 6 条）| 见第 3 节方案 |
| 4 | 盘点单 | MAT-RECO-2026-00002（SLE 6 条 + GL 2 条，金额 24000 MZN）| 决定清空/保留 |
| 5 | Item Price ×6 | Standard Selling 价表，1200–1450 MZN（**价表全局**）| **无需迁移** |
| 6 | Item 主数据 ×7 | CR-001 模板 + 6 变体（**Item 无公司维度**）| **无需迁移** |
| 7 | 客户/供应商 | 仅 Walkin（全局）| **无需迁移** |
| 8 | 自定义字段/翻译/代码 | 站点级全局（solua_home app）| **无需迁移** |

**不需要动的**：科目、仓库、税模板、成本中心、价格表、物料主数据、客户、自定义字段、solua_home 定制代码——它们要么全局、要么 SH 已有孪生结构。

---

## 3. 核心决策：库存怎么搬（3 个方案）

### 方案 A —「SHD 清零 + SH 重新盘点」（推荐 ⭐）
1. SHD 反向盘点：6 变体在 Finished Goods - SHD 调整为 0
2. SH 正向盘点：6 变体在 Finished Goods - SH 调整为实际数量（当前账面 10）
- ✅ 账实一致、两公司各自平账、审计最清晰
- ✅ 库存进 SH 时用的是 **SH 的科目**（1400/1410 - SH），天然正确
- ❌ 工作量略大（2 张盘点单）
- 风险：低

### 方案 B —「SHD 保留不动，SH 直接盘点入库」（最快）
1. 只在 SH 做正向盘点（6 变体 @ Finished Goods - SH = 10）
2. SHD 库存保留当 demo 数据（反正 SHD 是测试公司）
- ✅ 一步到位，最快
- ❌ SHD 账上多挂 6×10 库存（无业务单据，不影响 SH）
- ⚠️ 若将来删除 SHD 公司，需先清这批库存
- 风险：最低

### 方案 C —「跨公司移库（不推荐）」
ERPNext **不支持跨公司 Stock Transfer**。若强行直接改 Bin/SLE/GL 的 warehouse/company 字段，会破坏台账一致性（voucher 与 ledger 指向不同公司），**否决**。

> 建议：**方案 B 起步**（demo 公司无需纠结），正式开业前若决定清理 SHD 再补一次"清零"盘点。若追求账目绝对干净 → 方案 A。

---

## 4. 迁移步骤（按序执行，方案 B + POS 迁移）

> 前置：**已确认 6 变体实际库存 = 10**（现场核对，勿盲信账面）；预计中断 < 5 分钟（POS 迁移窗口）。

### Phase 0 — 备份与快照（必做）
```bash
# 1. 数据库全量备份（已有惯例，追加日期）
sudo -u frappe -i bash -l -c "cd /home/frappe/frappe-bench && bench --site erp.solua.one backup --with-files"

# 2. 记录迁移前状态快照（POS Profile / Bin / SLE / GL 全量导出）
#    将 bin/sle/gl/pos 四个表导出为 CSV 存档
```

### Phase 1 — 迁移 POS Profile（核心）
```python
# bench --site erp.solua.one console（或 execute 脚本）
for name in ["收银方式1", "收银方式1-Test"]:
    pos = frappe.get_doc("POS Profile", name)
    pos.company = "Solua Home, Lda"
    pos.warehouse = "Finished Goods - SH"
    pos.save(ignore_permissions=True)
frappe.db.commit()
```
- 支付方式子表自动跟随；价格表 Standard Selling 全局不变
- 迁移后 POS 的收款科目/收入科目自动取 SH 默认值（Company 变更会触发重算）

### Phase 2 — SH 库存盘点入库
1. 创建 Stock Reconciliation（目的仓库 `Finished Goods - SH`）：
   - CR-001-AZ 10、CR-001-BR 10、CR-001-BG 10、CR-001-VM 10、CR-001-CZ 10、CR-001-PR 10
2. 提交 → 系统自动过账到 SH 科目（1400/1410 - SH）

### Phase 3 — 验证
| 检查项 | 期望 |
|---|---|
| POS Profile company | Solua Home, Lda ×2 |
| POS Profile warehouse | Finished Goods - SH ×2 |
| Bin 归属 | 6 条全部在 Finished Goods - SH，qty=10 |
| SLE/GL | SH 新增 6 SLE + 2 GL（Stock In Hand - SH）|
| POS 扫码实测 | 开单→扫码 CR-001→选色→库存 10→结账，**公司=Solua Home, Lda** |
| 增值税 | 发票税率 17%（Mozambique Tax - SH）|

### Phase 4 — 收尾（可选，独立任务）
- SHD 进入"只读/冻结"：POS Profile 迁移后 SHD 无业务入口
- 决定 SHD 命运：保留（测试用）或后续清理删除（先清 6×10 库存）
- **修复遗留 bug**：`sites/erp.solua.one/site_config.json` 中 `installed_apps` 仍是 `["frappe","erpnext","my_custom_app"]`（上次重命名只改了 tabDefaultValue）→ 应改为 `solua_home`，否则部分 bench 命令可能仍读旧 app 名

---

## 5. 风险清单

| 风险 | 等级 | 缓解 |
|---|---|---|
| 变更中 POS 短暂不可用 | 🟢 低 | 低峰窗口执行；Phase 1 仅几秒 |
| 库存数量不符（账面 10 ≠ 实物）| 🟡 中 | Phase 0 先现场核对；盘点按实际数量 |
| Company 变更触发字段联动出错 | 🟡 中 | 迁移后立即跑 Phase 3 验证 + POS 实测 |
| Abbr 不可改（SH 定名即终身）| 🟡 中 | 迁移前确认"Solua Home, Lda/SH"即最终命名 |
| 误操作破坏台账 | 🟢 低 | 只走正规单据（盘点），禁手改 Bin/SLE/GL |
| 旧 app 名残留（site_config.json）| 🟢 低 | Phase 4 顺手修复 |

---

## 6. 回滚方案

| 场景 | 回滚操作 |
|---|---|
| POS Profile 迁移失败/异常 | 数据库备份还原（Phase 0）；或把 company/warehouse 改回 SHD |
| 盘点单提交后发现数量错误 | 取消（Cancel）盘点单 → SLE/GL 自动冲销，恢复原状 |
| 全部失败 | `restore` Phase 0 备份 → clear-cache → supervisor restart |
| 迁移成功但不想留 SHD 库存 | SHD 补一张反向盘点清零 |

**回滚安全边界**：所有步骤都是"正规单据 + 可逆字段修改"，无一步直接改台账底层；配合 Phase 0 备份可完整还原。

---

## 7. 遗留建议（迁移之外的独立优化）

1. `site_config.json` installed_apps 旧名残留 → 修正为 solua_home（**建议本次一并做**）
2. Item Defaults 全空 → 迁移后在 Products 物料组配 Item Group Defaults（默认仓 Finished Goods - SH、价表、4110/5111 科目）
3. 6 变体库存为 0 的老问题 → 本次盘点一并解决
4. SHD 公司的最终处置（保留测试 / 清零 / 删除）需单独决策
