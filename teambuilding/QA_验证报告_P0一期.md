# 团建在线产品库 P0 一期 — 验证报告

- 验证人：Edward（QA Engineer）
- 验证范围：7 个单文件 HTML 页面（无构建、纯前端）
- 验证方法：Node 静态结构检查 + JS 语法检查（node --check）+ onclick 交叉引用 + 核心算法沙箱模拟 + 逐文件代码阅读
- 验证时间：交付当日

---

## 1. 汇总表

| # | 文件 | 结构检查 | JS 语法 | 核心逻辑 | P0 | P1 | P2 |
|---|------|:---:|:---:|:---:|:---:|:---:|:---:|
| — | play/index.html（产品总览） | ✓ | ✓ | ✓ | 0 | 0 | 1 |
| T1 | tools/plan-generator/index.html | ✓ | ✓ | ✓ | 0 | 0 | 0 |
| T2 | tools/group-splitter/index.html | ✓ | ✓ | ✓ | 0 | 0 | 1 |
| T3 | tools/timer/index.html | ✓ | ✓ | ✓ | 0 | 0 | 0 |
| G1 | games/two-truths-one-lie/index.html | ✓ | ✓ | ✓ | 0 | 0 | 0 |
| G2 | games/human-bingo/index.html | ✓ | ✓ | ✓ | 0 | 0 | 1 |
| G3 | games/team-quiz/index.html | ✓ | ✓ | ⚠（1 处 P1） | 0 | **1** | 0 |
| **合计** | | **7/7** | **7/7** | 6/7 | **0** | **1** | **3** |

> 结构检查项说明：`<script>/<style>` 配对 1/1；`id` 无重复；`http(s)://` 外部引用仅剩规范要求的 footer 文字链接 `https://aiworkdb.github.io/teambuilding/`，无 CDN/外链脚本；onclick 引用的函数全部有定义（`window.print()` 为浏览器内置 API，非缺失）；tools/* 与 games/* 的 footer 返回链接均为 `../../index.html`（正确）；无 `fetch/XHR/import/require` 运行时外部调用；无空 href / `href="#"` / `javascript:` 链接。

---

## 2. 逐文件关键发现

### 2.0 play/index.html（产品总览页）— 通过
- 三个分类卡片齐全：教练执行工具（T1-T6）、线上互动游戏（G1-G8）、IP 沉浸衍生（I1-I2）。
- 已上线卡片（T1/T2/T3/G1/G2/G3）url 正确指向 `tools/plan-generator/`、`tools/group-splitter/`、`tools/timer/`、`games/two-truths-one-lie/`、`games/human-bingo/`、`games/team-quiz/`，目录与 index.html 均已落盘确认存在 ✓。
- 规划中卡片（T4-T6/G4-G8/I1-I2）为 `<button>` + alert「该产品规划中，敬请期待」，不可导航 ✓。
- `render()` 通过 innerHTML 渲染，模板中 `\'` 转义正确，生成属性合法 ✓。
- P2-1（体验/环境提示）：卡片链接采用目录式相对路径（`tools/plan-generator/` 而非 `.../index.html`）。在 GitHub Pages 部署环境下完全正常；若本地 file:// 双击打开，部分浏览器（如 Chrome）对目录跳转不自动加载 index.html，需手动点一次。不影响线上交付，建议若强调"本地离线双击即用"，可将链接显式加 `index.html`。

### 2.1 T1 团建方案生成器 — 通过（无问题）
- 筛选逻辑成立：`generatePlan()` 校验四维（目的/形式/人数/时长）均已选择；过滤条件为「目的精确匹配 且 形式/人数/时长至少满足一项」；匹配不足 3 款时自动放宽为仅按目的匹配（并有提示文案）✓（沙箱验证：破冰热场/线上/10-30人/30分钟内 → 3 款，不触发放宽；领导力/室内/10-30人/30-60分钟 → 2 款，触发放宽，均符合预期）。
- 单选切换 `toggleOpt`：同维度互斥、再次点击取消 ✓。
- 洗牌 `shuffle`：Fisher-Yates ✓；推荐上限 5 款 ✓。
- 时间轴 `buildTimelineHtml`：开场热身 → 主游戏 → 收尾复盘，`seq.pop()` 取收尾、`seq.slice(1)` 取主游戏，所有被推荐游戏均被覆盖不丢失 ✓（含 1 款/全为破冰等边界，无越界/空指针）。
- 打印按钮 `onclick="window.print()"` + `@media print` 隐藏 `.no-print` ✓。

### 2.2 T2 随机分组器 — 通过（1 处 P2）
- 名单解析：按行 trim 过滤空行 ✓；`updateTotal()` 实时统计 ✓。
- 分组算法 `chunk`：轮转分配保证人数均衡（沙箱验证：10/3 → [4,3,3]；15/4 → [4,4,4,3]；23/6 → [4,4,4,4,4,3]，组间差 ≤1、总人数守恒）✓。
- 两种模式：按组数（组数超人数自动收敛并提示）、按每组人数（`ceil(n/size)` 组数，各组 ≤ size）✓。
- 复制：使用 Clipboard API，`navigator.clipboard` 不可用或 reject 时有 `fallbackCopy`（textarea + execCommand，包裹 try/catch）降级 ✓，符合 file:// 环境要求。
- **P2-2**：`copyText()` 无论降级复制实际是否成功（execCommand 可能返回 false 但被 try/catch 吞掉），`done()` 都会弹出「已复制到剪贴板」成功提示，存在"提示成功但实际未复制"的误报可能。建议：`fallbackCopy` 返回 `document.execCommand('copy')` 的布尔值，失败时提示"复制失败，请长按手动复制"。

### 2.3 T3 环节计时器 — 通过（无问题）
- setInterval 倒计时闭环成立：`toggleStart`（开始/暂停切换，剩余为 0 时重置）、`tick`（每秒减 1，到 0 停表 + beep + 自动高亮下一环节但不自动开始）、`nextSegment`（循环跳转）、`resetCurrent`、`selectSegment`、`removeSegment`（含删除当前/删空后 currentIndex 归位逻辑）✓。
- 提示音：`ensureAudio`（AudioContext 创建/resume）与 `beep`（三连音振荡器）均包 try/catch ✓。
- localStorage 读写均包 try/catch，损坏数据回退默认 3 环节 ✓。
- 边界：添加环节校验名称非空、分钟 1-600；清空有 confirm ✓。

### 2.4 G1 两真一假 — 通过（无问题）
- 数据流闭环验证：出题（`nextPlayer` 校验三条陈述非空 + 必选假话下标）→ 存储 `players[i]` 与 `votes[i]` 一一对应（`backPlayer` 修改复用不破坏对齐）→ 投票（`castVote`/`attachName`）→ 揭晓（`revealAnswer` 用 `x.idx === p.lie` 统计猜对）→ 下一位/排行榜（出题者榜按骗到人数、猜题者榜按具名猜对次数）✓。
- **无答案泄露**：投票页 `enterVote` 渲染陈述时不带 is-lie 标记，假话仅在点击「揭晓答案」后才高亮 ✓。
- 无索引错位：revealIdx 全程对齐 players/votes ✓；人数输入校验 2-30 ✓；重开 confirm 防误触 ✓。

### 2.5 G2 人类宾果 — 通过（1 处 P2）
- 编解码自洽：`encode`（25 个 0-29 特征索引 → ALPHA[32 字符表] 25 位码）与 `decode`（大写/去空格、长度校验、字符合法性校验、索引 >29 拒绝）往返一致。沙箱 2000 次随机往返全部 PASS；非法码（长度 24、含 I/O/0/1 易混淆字符、含 8/9 越界索引）均正确拒绝 ✓。
- BINGO 检测 `countLines`：5 行 + 5 列 + 2 对角线共 12 线算法正确（沙箱 7 组用例全部命中预期）✓。
- 主持：生成卡片（30 特征池随机取 25 不重复）→ 卡片码存 localStorage（上限 100 条）→ 喊格子随机 ✓；玩家：载入码 → 恢复历史标记 → 点格子标记/取消 → BINGO 横幅 ✓；`regenCard` 重生成自卡 ✓。
- 复制降级逻辑与 T2 一致（Clipboard API + fallback）✓。
- **P2-3**：`enterPlayer()` 只清空输入框，未隐藏/重置 `#playerArea`。玩家模式载入过一次卡片后返回再进入，会残留上一张卡片的网格与卡号（且输入框已清空，视觉上"没输入却有卡片"）。建议 `enterPlayer()` 中 `playerArea.style.display='none'`。

### 2.6 G3 团队知识竞答 — ⚠ 发现 1 处 P1
- 常规流程成立：预置 15 题题库 → 队伍设置（2-6 队，改名保留）→ `startPlay`（题库空拦截）→ `renderPlay` 出题 → `pickAnswer` 揭晓（高亮正确/错误、禁用选项、展示解析、启用下一题）→ `nextQ` 计分/下一题 → `showEnd` 排行 → `playAgain`/`restartAll` ✓。
- JSON 导入：`importQuestions` 整体包 try/catch，含格式逐条校验（q 非空、options 恰 4 项、answer 为 0-3 数字），失败 alert 提示 ✓。
- 计分 `score(i, delta)` 与题目管理 `addQuestion`/`removeQ` 正常。
- **P1-1（源码 Bug）**：`score()` 调用 `renderPlay()` 全量重渲染，导致"揭晓答案后任何一次 +10/-5 加减分"都会：
  1. 清掉选项上的 correct/wrong 高亮；
  2. 隐藏解析框 `#explain`（正确答案展示随之消失）；
  3. 选项按钮被重建为可点击状态，但 `pickAnswer` 有 `if (revealed) return` 守卫，点击后无任何反应（看起来可点、实际是死按钮）。
  - 影响：竞答主持人在揭晓后立即给答对队伍加分（核心操作路径），正确答案展示即刻丢失且**无法恢复**（再点选项是空操作、解析框不再显示），直接影响主持人对答案的核对与讲解。
  - 位置：`score()`（line 261-264）→ `renderPlay()`（line 240-259）；`pickAnswer`（line 266-281）。
  - 修复建议（二选一）：
    - A. `score()` 改为只更新对应 `.tscore` 文本（或维护 `lastPicked` 状态后重渲染时按 `revealed` 重新应用高亮/解析）；
    - B. `renderPlay()` 末尾增加：`if (revealed) { /* 按 questions[currentQ].answer 重新加 correct 类、恢复 explain 显示 */ }`，并保持选项 disabled。

---

## 3. 问题分级汇总

| 编号 | 级别 | 文件 | 位置 | 问题描述 |
|---|---|---|---|---|
| P1-1 | P1 | team-quiz | `score()` line 261-264 / `renderPlay()` line 240-259 | 揭晓后加减分触发全量重渲染，正确答案高亮与解析被清除，选项变"假可点" |
| P2-1 | P2 | index | 卡片链接 `tools/*/`、`games/*/` | 目录式相对链接在本地 file:// 双击下可能不自动加载 index.html（GitHub Pages 线上正常） |
| P2-2 | P2 | group-splitter | `copyText()` line 197-208 / `fallbackCopy()` line 210-219 | 降级复制失败时仍提示"已复制到剪贴板"，存在误报 |
| P2-3 | P2 | human-bingo | `enterPlayer()` line 202 | 再次进入玩家模式未隐藏旧卡片区，残留上一张卡片 |

**P0 阻断：无。** 7 个页面均可打开、无 JS 语法错误、无运行时外部依赖、主流程均可用。

---

## 4. 智能路由判定

- **源码有 Bug → 需工程师（Alex）修复的问题清单：**
  1. **【P1】team-quiz `score()`/`renderPlay()`**：揭晓答案后加减分会清掉正确答案展示且无法恢复。建议按上文修复方案 A/B 处理，修复后回归验证。
- **测试自身问题：无**（本次为验证性检查，未发现检查脚本/断言自身错误）。
- **P2 建议项**（可随下个迭代一并处理，不阻塞交付）：P2-1、P2-2、P2-3 见上表。

---

## 5. 总评

**结论：可交付（有条件）**。

- 7 个页面结构完整、语法合法、离线可运行、无 P0 致命缺陷；T1/T2/T3/G1/G2 五个页面的核心逻辑经代码阅读与算法模拟双重验证均正确，index 总览页导航与禁用逻辑正确。
- **唯一需要工程师修复的是 G3 团队知识竞答的 P1 问题（揭晓后加减分丢失答案展示）**，修复后即可完全交付；3 个 P2 为体验/环境优化项，不阻塞一期上线。
- 建议修复 P1 后对该场景做一次回归：揭晓 → +10/-5 → 确认答案高亮/解析仍保留、选项仍禁用、下一题可正常进入。
