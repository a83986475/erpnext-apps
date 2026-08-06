# Solua Home, Lda (Demo) [SHD] 公司删除记录

> 目标站点：erp.solua.one（数据库 `_62af7cb1044ac230`）
> 执行日期：2026-08-07 ｜ 前置文档：《SHD-SH 迁移评估清单.md》（迁移评估）、《demo-data-cleanup-plan.md》（demo 数据清理）
> 用途：**上线前对照**——确认 Demo 公司已彻底清除、正式公司 SH 配置完好、如有异常可按备份回滚。

---

## 0. 决策背景

- 原计划「把 POS 收银与窗帘库存从 SHD 迁移到 SH」，迁移配置（POS Profile、银行科目、付款方式账户）已在 SH 侧完成。
- **最终决策改为直接删除 SHD**：SHD 是 Demo 测试公司，保留会导致全局自定义功能（扫码选色、空态、模块隐藏等）可能误应用到 SHD，测试数据也无保留价值。
- SH 正式公司配置已就绪（POS Profile「收银方式1 - SH」：Walkin 默认、Cash/刷卡支付、自动填充收款、科目联动 SH）。

---

## 1. 删除前状态盘点（全表扫描）

- 扫描方法：遍历所有含 `company` 列的 ~130 张表，统计 SHD 记录数。
- **关键残留清单**（删除对象）：

| 类别 | 数量 | 明细 |
|------|------|------|
| Sales Invoice | 1 | ACC-SINV-2026-00006（**未提交** docstatus=0，直接删）|
| Stock Reconciliation | 1 | MAT-RECO-2026-00002（已提交，**先 Cancel**）|
| POS Opening Entry | 2 | POS-OPE-2026-00001 / 00003（已提交，先 Cancel）|
| Process Deferred Accounting | 2 | ACC-PDA-00003 / 00004（已提交）|
| Account（科目）| 97 | 全部 SHD 科目（含 1410 Stock In Hand、5119 Stock Adjustment 等有 GL 交易的）|
| Warehouse（仓库）| 5 | Finished Goods - SHD、All Warehouses - SHD 等 |
| Cost Center（成本中心）| 2 | Main - SHD + 根组 |
| 税模板 | 3 | Mozambique Tax - SHD（销售 / 采购 / Item Tax）|
| POS Profile | 2 | 收银方式1、收银方式1-Test |
| GL Entry | 4 | 已提交单据留下的台账 |
| Stock Ledger Entry | 12 | Cancel 盘点单产生的反向分录 |
| Bin | 6 | 库存台账 |
| Repost Item Valuation | 9 | 重估记录 |
| Mode of Payment 账户行 | 若干 | Cash / Credit Card 的 SHD 默认账户子表行 |

---

## 2. 备份（删除前必做）

| 备份号 | 时间 | 文件 |
|--------|------|------|
| **`20260807_002435`** | 2026-08-07 06:24 | `20260807_002435-erp_solua_one-database.sql.gz` + `-files.tar` + `-private-files.tar` + `-site_config_backup.json` |

- 位置：`/home/frappe/frappe-bench/sites/erp.solua.one/private/backups/`
- 备份前还有一份更早的 `20260807_000003`（06:00 自动备份），双保险。

---

## 3. 执行顺序（依赖关系，结构化删除）

```
0. 备份数据库（20260807_002435）✅
1. 业务单据（先处理已提交的单据）：
   - ACC-SINV-2026-00006 未提交 → 直接 delete_doc
   - MAT-RECO-2026-00002 盘点单 → 先 Cancel（产生反向 SLE）
   - POS-OPE-2026-00001/00003 开店单 → Cancel
   - ACC-PDA-00003/04 递延会计 → Cancel
2. POS Profile：收银方式1、收银方式1-Test → 删除
3. 税模板：Mozambique Tax - SHD（销售/采购/Item Tax）→ 删除
4. 台账清理（SQL 兜底）：SLE 12 → Bin 6 → GL 4
5. 仓库：5 个 SHD 仓库 → 删除（清完台账后）
6. 科目：97 个 → 自底向上删除
   - 有交易的科目（1410 / 5119）→ 先清 GL 台账再删
   - 父级科目 → 等子科目删完后再删（自底向上）
7. 成本中心：Main - SHD + 根组 → 删除
8. 其他：Mode of Payment 的 SHD 账户行、Repost Item Valuation → 清理
9. 公司本体：Solua Home, Lda (Demo) → delete_doc（最后删，所有引用清空后）
10. bench clear-cache + supervisor 重启（7 进程 RUNNING）
```

> ⚠️ 执行中发现：删除公司本体后仍有残留（2 仓库、2 科目 1410/5119、6 个父级科目因 GL/SLE 删不掉）→ 用第二个清理脚本先清台账（SLE 12 / Bin 6 / GL 4）再删仓库科目，最终全部清零。

---

## 4. 删除后验证（全部通过）

| 检查项 | 结果 |
|--------|------|
| 全表扫描（~130 张含 company 表）SHD 记录 | **0** ✅ |
| tabCompany 剩余 | 仅 `Solua Home, Lda`（abbr=SH, MZN）✅ |
| SH 侧配置 | 科目 97 / 仓库 5 / POS Profile「收银方式1 - SH」（Walkin 默认）✅ |
| GL Entry / Stock Ledger Entry | 0 / 0（台账干净）✅ |
| 进程状态 | supervisor 7 进程全部 RUNNING ✅ |
| 缓存 | clear-cache 已执行 ✅ |

**删除后系统状态**：
- 唯一公司：`Solua Home, Lda`（SH），收银配置齐全（收银方式1 - SH：Walkin 默认、Cash/刷卡支付、自动填充收款、科目联动 SH）。
- 自定义功能（扫码选色、空态、模块隐藏）全是全局代码，与公司无关，照常生效。
- 「定制功能误用到 SHD」的风险已不存在。

---

## 5. 回滚方案（如需恢复）

```bash
# 1. 恢复数据库（会回到删除前状态，含 SHD 与 SH 所有数据）
bench --site erp.solua.one restore \
  /home/frappe/frappe-bench/sites/erp.solua.one/private/backups/20260807_002435-erp_solua_one-database.sql.gz

# 2. 恢复文件附件（如有）
# 3. 清缓存 + 重启
bench --site erp.solua.one clear-cache
sudo supervisorctl restart all
```

> ⚠️ 恢复会**回退整个数据库**（包括 SHD 删除后 SH 侧新建的 pos1/pos2 收银员等后续变更），仅作灾难恢复手段，日常不需要。

---

## 6. 上线前对照检查项（本记录的核心用途）

- [ ] `erp.solua.one` 登录后公司选择器**只有 Solua Home, Lda**（无 Demo）
- [ ] POS 打开时 Profile 只有「收银方式1 - SH」（无收银方式1-Test）
- [ ] 收款界面：Cash / Credit Card 点击自动填充剩余金额（`set_grand_total_to_default_mop=0`）
- [ ] 默认顾客 = Walkin；扫码 → 选色弹窗 → 购物车（自定义功能正常）
- [ ] 收银员账号：pos1@solua.one / pos2@solua.one（Sales User + Accounts User + **POS Cashier** 角色，静音已开，默认公司 SH，可自助开店/关店）
- [ ] 物料/库存：SH 仓库目前**空库**，正式营业前需建立真实物料档案 + 盘点入库
- [ ] 税模板：Mozambique Tax - SH（17%）在销售/采购单据正确套用

---

## 7. 相关文档索引

- 《SHD-SH 迁移评估清单.md》— 迁移前评估（两家公司结构对比、资产盘点）
- 《demo-data-cleanup-plan.md》— 更早的 demo 数据清理（SKU/test 物料与往来单位）
- 《ERPNext 定制开发操作手册.md》— 自定义 App（solua_home）开发与部署
- 《SESSION_SUMMARY.md》— 会话历史与待办
