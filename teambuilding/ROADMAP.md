# 团建 & 培训资料库 · 建设规划

> 最新进度更新：2026-06-26  
> 下一步规划更新：2026-06-26

---

## 📊 当前进度总览

| 模块 | 进度 | 说明 |
|------|------|------|
| 目录结构 | ✅ 100% | 完整创建 |
| README 总索引 | ✅ 100% | 27款游戏已入库 |
| 教练使用指南 | ✅ 100% | guide.md 完整 |
| 教练工具箱 | ✅ 100% | 4个文件完整 |
| 游戏库 | ✅ 130% | **30款**（目标23款，超额完成） |
| 团建流程方案 | ✅ 133% | **4套**（目标3套，超额完成） |
| 现有桌游改造 | ✅ 100% | 7款已改造，优先清单完成 |
| HTML 版本 | 🟡 50% | **5款**已完成（目标10款，完成50%） |
| 上线部署 | ✅ 100% | https://aiworkdb.github.io/teambuilding/ |

---

## ✅ 已完成内容清单

### 游戏库（27款）

#### 🧊 破冰热场（7款）
1. 人类宾果 `icebreaker/human-bingo.md`
2. 两真一假 `icebreaker/two-truths-one-lie.md`
3. 名字接龙 `icebreaker/name-chain.md`
4. 盲盒神话（改造）`icebreaker/blind-box-myth.md`
5. 美食挑战赛（改造）`icebreaker/food-challenge.md`
6. 探险家日记（改造）`icebreaker/explorer-journal.md`
7. 台词之王（改造）`icebreaker/line-master.md`

#### 🔐 信任建立（2款）
1. 信任背摔 `trust/trust-fall.md`
2. 盲行 `trust/blind-walk.md`

#### 💬 沟通表达（7款）
1. 盲人方阵 `communication/blind-polygon.md`
2. 传话游戏 `communication/telephone-game.md`
3. 你说我画 `communication/draw-guess.md`
4. 画图接龙 `communication/drawing-relay.md`
5. 动物城大侦探（改造）`communication/animal-detective.md`
6. 时间特工（改造）`communication/time-agents.md`
7. 谣言工厂（改造）`communication/rumor-factory.md`

#### 🤝 团队协作（9款）
1. 人结 `collaboration/human-knot.md`
2. 齐眉棍 `collaboration/eyebrow-stick.md`
3. 珠行万里 `collaboration/ball-relay.md`
4. 风火轮 `collaboration/wind-fire-wheel.md`
5. 人体拼字 `collaboration/body-letters.md`
6. 岛屿求生（改造）`collaboration/island-survival.md`
7. 魔法学院（改造）`collaboration/magic-academy.md`
8. 星际矿工（改造）`collaboration/space-miners.md`
9. 疯狂厨房（改造）`collaboration/crazy-kitchen.md`

#### 👑 领导力（3款）
1. 红黑游戏 `leadership/red-black-game.md`
2. 七巧板 `leadership/tangram.md`
3. 沉默领袖 `leadership/silent-leader.md`

#### 💡 创新思维（2款）
1. 10元买创意 `creativity/10-yuan-idea.md`
2. 报纸塔挑战 `creativity/newspaper-tower.md`

#### 🔍 问题解决（2款）
1. 沙漠逃生 `problem-solving/desert-survival.md`
2. 鸡蛋坠落挑战 `problem-solving/egg-drop.md`

### 流程方案（4套）
1. 一日团建模板 `flows/one-day/01-schedule.md`
2. 半日团建模板 `flows/half-day/01-schedule.md`
3. 领导力觉醒工作坊 `flows/workshop/leadership-awakening.md`
4. 线上团建模板 `flows/online/01-schedule.md`

### 教练工具箱（4个）
1. 引导话术库 `toolbox/facilitation.md`
2. 复盘引导框架 `toolbox/debrief.md`
3. 安全与管理 `toolbox/safety.md`
4. 物资与效率工具 `toolbox/checklist.md`

---

## 🎯 下一步规划（第五阶段）

### 目标：将游戏库扩充至 50+ 款，并优化用户体验

#### 任务1：继续改造现有桌游（优先级：高）
从 `boardgames/` 中挑选更多适合团建的桌游进行改造。

**优先清单（第二批）**：
| 现有桌游 | 适合场景 | 改造重点 |
|---------|---------|---------|
| 时间特工（time-agent） | 团队协作 | 增加复盘框架 |
| 魔法学院（magic-academy） | 协作 | 增加角色分工观察点 |
| 星际矿工（star-miner） | 协作/资源 | 增加竞争vs合作讨论 |
| 疯狂厨房（crazy-kitchen） | 协作/沟通 | 增加抗压复盘 |
| 探险家日记（explorer-journal） | 破冰/沟通 | 增加分享引导 |
| 台词之王（line-master） | 破冰/沟通 | 增加团队赛变体+复盘问题 |
| 谣言工厂（rumor-factory） | 沟通/信任 | 增加引导要点 |

**目标**：再改造 7 款，使游戏库达到 **34 款**。

---

#### 任务2：创建 HTML 版本游戏文档（优先级：中）
将 `.md` 游戏文档转为 `.html`，在 GitHub Pages 上更友好。

**方案**：
- 使用简单的 CSS 框架（如 Water.css 或 Pico.css）
- 保持简洁，专注内容
- 自动生成索引页

**目标**：完成 10 款高频使用游戏的 HTML 版本。

---

#### 任务3：添加搜索和筛选功能（优先级：中）
在 `teambuilding/index.html` 中加入游戏名称/标签的实时搜索。

**功能**：
- 按分类筛选
- 按人数筛选
- 按时长筛选
- 关键词搜索

**目标**：提升教练使用体验。

---

#### 任务4：创建「团建方案生成器」（优先级：低）
根据人数/时长/目的，自动推荐游戏组合。

**输入**：
- 人数（<10 / 10-20 / 20-30 / 30+）
- 时长（<1h / 1-3h / 3-6h / 6h+）
- 目的（破冰 / 协作 / 信任 / 领导力 / 综合）

**输出**：
- 推荐游戏组合
- 时间安排建议
- 物资清单汇总

**目标**：做成简单的静态页面（HTML + JavaScript）。

---

#### 任务5：补充线上团建游戏（优先级：低）
创建更多适合远程团队的线上游戏。

**候选清单**：
1. 线上宾果（Online Bingo）
2. 我从未（Never Have I Ever/线上版）
3. 虚拟逃脱（Online Escape/简化）
4. 画图猜词（Online Pictionary）
5. 知识竞答（Team Quiz）

**目标**：再创建 5 款，使线上游戏达到 6+ 款。

---

## 📅 执行计划

### 本周任务（2026-06-25 至 2026-07-01）
- [x] 改造现有桌游 × 7 款（任务1） - ✅ 已完成（7/7）
- [x] 创建 HTML 版本 × 5 款（任务2开始） - ✅ 已完成（5/10）

### 下周任务（2026-07-02 至 2026-07-08）
- [ ] 完成 HTML 版本 × 5 款（任务2完成，累计10/10）
- [ ] 添加搜索和筛选功能（任务3）

### 后续任务（2026-07-09 起）
- [ ] 创建团建方案生成器（任务4）
- [ ] 补充线上团建游戏 × 5（任务5）

---

## 🤖 自动化任务设置

### 定时任务：每10小时检查并推进建设进度

**任务名称**：团建资料库自动建设  
**执行频率**：每10小时（RRULE: FREQ=HOURLY;INTERVAL=10）  
**执行目录**：`d:/mycode/aiworkdb.github.io`  
**提示词**：

```
检查 teambuilding/ROADMAP.md 中的下一步规划，自动完成下一个优先任务：
1. 读取 ROADMAP.md，找到第一个未完成的任务
2. 根据任务描述，创建或更新相应的游戏/流程/工具文件
3. 更新 ROADMAP.md 中的进度
4. 提交并推送到 GitHub（如果内容有变化）
5. 报告完成了什么，以及下一步建议

如果没有未完成的任务，则：
- 从 boardgames/ 中挑选一款未改造的桌游进行改造
- 或者优化现有内容的格式和链接
```

**状态**：待用户确认后创建

---

## 📈 成功指标

- [x] 游戏库达到 20+ 款（✅ 已完成 27 款）
- [ ] 游戏库达到 50+ 款
- [x] 流程方案达到 3+ 套（✅ 已完成 4 套）
- [ ] 所有游戏都有 HTML 版本
- [ ] 索引页支持搜索和筛选
- [ ] 团建方案生成器上线

---

_规划制定：2026-06-24 | 最后更新：2026-06-25_
