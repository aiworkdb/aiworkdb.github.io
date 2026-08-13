# 团建在线产品库 P1 二期 · QA 验证报告

**QA Engineer：严过关（Edward）**
**验证方式**：node 静态检查 + JS 语法检查（node --check）+ 计分矩阵数据推演 + Chrome 无头浏览器（chrome-devtools）真实功能冒烟
**验证日期**：本次会话

---

## 一、汇总表（7 文件）

| # | 文件 | 结构 | 核心逻辑 | P0 | P1 | P2 | 结论 |
|---|------|:---:|:---:|:---:|:---:|:---:|------|
| 1 | tools/scoreboard/index.html（T4 积分计分板） | ✓ | ✓ | 0 | 0 | 1 | 通过 |
| 2 | tools/materials/index.html（T5 物资清单生成器） | ✓ | ✓ | 0 | 0 | 1 | 通过 |
| 3 | tools/debrief-cards/index.html（T6 复盘引导卡） | ✓ | ✗ | **1** | 0 | 0 | **不通过** |
| 4 | games/pictionary/index.html（G4 线上你画我猜） | ✓ | ✗ | **1** | 0 | 1 | **不通过** |
| 5 | games/never-have-i-ever/index.html（G5 我从未） | ✓ | ✓ | 0 | 0 | 0 | 通过 |
| 6 | games/red-black/index.html（G6 红黑游戏） | ✓ | ✓ | 0 | 0 | 1 | 通过（含 P2 建议） |
| 7 | play/index.html（总览页） | ✓ | ✓ | 0 | 0 | 0 | 通过 |

**总计：P0 × 2，P1 × 0，P2 × 3**

---

## 二、静态结构检查（A 项，7 文件全过）

- `<script>`/`</script>`、`<style>`/`</style>` 配对：全部成对，无缺失
- `id="..."` 无重复：静态 id 唯一，动态 id（teamName0..7 / score0..7 / playerName0..7 等）按渲染范围唯一
- 外部资源：无 CDN/script/link 外链；仅 footer 允许的 `https://aiworkdb.github.io/teambuilding/` 文字链接
- onclick 函数：全部有对应 `function` 定义（内置 alert/confirm/window.print 白名单）
- footer 返回链接：子页面均为 `../../index.html`，总览页为团建游戏库链接
- JS 语法：每个 `<script>` 块经 `node --check` 全部通过（无语法错误）

---

## 三、关键发现（P0/P1 必须修复）

### 🔴 P0-1：T6 复盘引导卡 — 全局变量 `history` 与浏览器内置 `window.history` 冲突，页面初始化即抛错

- **文件**：`play/tools/debrief-cards/index.html`
- **位置**：`var history = []`（L158）；`history.unshift(...)`（L195）；`history.length` / `history.forEach`（L245 / L248）；`history = []`（L255）
- **现象**（Chrome 实测）：
  - 页面加载即报 `Uncaught TypeError: history.forEach is not a function`（init 调 renderHistory 时）
  - 每次「抽一张 / 换一张 / 随机模式」执行到 `history.unshift` 抛 TypeError，「已抽问题」列表永不更新
  - 根因：`window.history` 是浏览器只读访问器属性（无 setter），全局 `var history = []` 的赋值在非严格模式下静默失败，`history` 仍指向 History 对象
- **修复建议**：将该变量重命名为 `pickedHistory` / `drawnHistory`（避开 window 内置名），同步替换 L158/L195/L245/L248/L255（也可改用 `let` 词法绑定，但重命名更稳妥）

### 🔴 P0-2：G4 线上你画我猜 — 猜词阶段画作不可见，核心玩法「看画猜词」失效

- **文件**：`play/games/pictionary/index.html`
- **位置**：`finishDrawing()`（L316-320）；`renderGuess()`（L322-345）；panelGuess 结构（L99-102）
- **现象**（Chrome 实测）：点击「画好了，进入猜词」后，`hideAll()` 将 `panelDraw`（含 `#drawCanvas`）整体隐藏（display:none），而 `panelGuess` 只渲染「轮到 X 猜测 + 输入框 + 按钮」，**不含任何画作/canvas**。猜词者看不到画，只能盲猜，游戏主流程不可用
- **修复建议**（任选其一）：
  1. 将 canvas 从 panelDraw 移入 panelGuess（renderGuess 顶部插入画布区），保证猜词时画作可见；或
  2. `finishDrawing()` 不隐藏整个 panelDraw，仅隐藏按钮/词区，保留 canvas-box 可见；或
  3. 进入猜词前用 `canvas.toDataURL()` 生成快照 `<img>` 展示在 guessInner 顶部（可避免同一 canvas 元素 display 冲突）

---

## 四、次要发现（P2，不阻断交付但建议优化）

| # | 文件 | 位置 | 描述 | 建议 |
|---|------|------|------|------|
| 1 | games/pictionary/index.html | `renderGuess()` L322-345 | 猜错/跳过时 `guessMsg` 已赋值但 `!roundDone` 分支不渲染，用户看不到「猜错了，换下一位」反馈 | 在未结束分支的状态行同时渲染 guessMsg |
| 2 | games/red-black/index.html | `choose()` L265-279 + `renderReveal()` L281-299 | `choose()` 先 `save()` 后 `renderGame()` 才 push history；reveal 阶段刷新页面再「继续」，存档缺少本轮记录且续玩会重复 push（Chrome 实测 histBefore=0 → 续玩后=1） | 将 history.push 移入 choose() 并在 push 后 save()，或 push 前判断本轮是否已记录 |
| 3 | tools/materials/index.html | `generate()` L268-277 | 同名物资去重时 qty 取首个出现值；如「白板笔」（两真一假 '1 支/人' vs 团队知识竞答 '2 支'）合并后只显示 '1 支/人' | 同名多数量时展示数量列表或取最大建议值 |
| 4 | tools/scoreboard/index.html | `init()` L227-239 | 存档校验仅检查 `names.length >= 2`，未校验 `scores.length === names.length`；异常存档下可能渲染 undefined | 加载时补齐/截断 scores 长度 |

---

## 五、核心逻辑验证明细（B 项）

### T4 积分计分板 — 通过
- 加减分含负数：浏览器实测 `addScore(2,-1)` → 分数 `-1` 正常显示
- 领先判定含并列：实测两对并列 → `当前并列：红队、蓝队（5 分）`
- localStorage 读写均包 try/catch（lsGet/lsSet）✓；重置/清除存档均有 confirm ✓

### T5 物资清单生成器 — 通过
- 搜索过滤：实测输入「红黑」过滤出 1 款游戏 ✓
- 生成数据流：勾选 2 款 → `已选 2 款游戏 · 汇总物资 7 项（去重后）· 合计出现 7 次`，分类分组渲染 ✓
- 打印（window.print + @media print 隐藏操作区）、清空选择 confirm ✓；GAMES 内置 20 款游戏数据完整

### T6 复盘引导卡 — 不通过（见 P0-1）
- 四维度问题库数据完整：Fact 7 / Feeling 6 / Finding 7 / Future 7 = 27 条 ✓
- 抽卡不重复、随机模式、已抽列表的**逻辑本身正确**，但被 `history` 命名冲突整体击穿（运行时崩溃）

### G4 线上你画我猜 — 不通过（见 P0-2）
- 词库：8 类 × 13 = **104 词**（≥100 ✓），无重复词 ✓
- 出词防偷看：toggleWord 默认隐藏、可再隐藏 ✓
- canvas pointer 事件：pointerdown/move/up/cancel/leave 齐全，DPR 缩放、clearCanvas、橡皮/颜色切换逻辑正确 ✓
- 猜词计分：实测猜对 → 猜者 +10、画者 +5，roundDone 后显示答案与下一回合 ✓
- 排行榜按分数降序 ✓；轮次流转：N 人每人画一轮 ✓
- **致命点：猜词阶段看不到画（P0-2）**

### G5 我从未 — 通过
- 话题库 **44 条**，逐条人工阅读 + 敏感词扫描：全部为职场/生活向安全话题（加班、外卖、宠物、追剧等），无敏感/尴尬/冒犯内容 ✓
- 翻卡/换一张：实测换卡索引不同、不重复 ✓
- 扣分逻辑：实测标记 -1、取消 +1 恢复；下一位轮转并自动抽新卡 ✓

### G6 红黑游戏 — 通过（计分矩阵节点推演 + 浏览器完整对局）
- 计分矩阵（node 推演 + 实测均正确）：红红 → -3/-3；黑黑 → +1/+1；红黑 → +5/-3；黑红 → -3/+5 ✓
- 完整 3 轮对局实测：轮次流转 red→blue→reveal→nextRound→done，比分累计正确（-3,-3 → -2,-2 → 3,-5），末轮按钮变「查看总结」✓
- 结果揭示：winner（红队获胜）、每轮记录表（表头+3 行）✓
- 进度存档/续玩：实测中途刷新 → 显示续玩条「继续/放弃并重来」→ 继续可恢复 ✓（附 P2-2 历史记录一致性建议）

### index 总览页 — 通过
- T4/T5/T6/G4/G5/G6 六个产品卡片均「开始使用」+ url 存在（6 个目标文件在磁盘上均存在）、soon 已移除 ✓
- G7/G8/I1/I2 四个保持「规划中」soon:true ✓
- 16 张卡片渲染正常、分类计数（6/8/2）、文案合理 ✓

---

## 六、智能路由判定

**判定：源码有 Bug → 发送给 Engineer（Alex）修复**

### 修复清单（按优先级）

| 优先级 | 文件 | 问题 | 建议改动 |
|:---:|------|------|------|
| P0 | tools/debrief-cards/index.html | `history` 变量与 window.history 冲突，初始化抛错、已抽列表失效 | L158/L195/L245/L248/L255 重命名变量（如 `pickedHistory`） |
| P0 | games/pictionary/index.html | 猜词阶段画作不可见，核心玩法失效 | `finishDrawing()`/`renderGuess()` 保证猜词面板展示 canvas 或画作快照 |
| P2 | games/pictionary/index.html | 猜错/跳过无反馈 | `renderGuess()` !roundDone 分支渲染 guessMsg |
| P2 | games/red-black/index.html | reveal 阶段存档 history 落后/续玩重复 | history.push 移入 choose() 并在 push 后 save() |
| P2 | tools/materials/index.html | 同名物资 qty 合并取首值 | 多数量时展示列表/最大值 |
| P2 | tools/scoreboard/index.html | 存档 scores/names 长度不一致 | init 时补齐/截断 scores |

---

## 七、总评

**暂不可交付。** 6 个新页面中 T4/T5/G5/G6 与总览页功能完整、结构规范、无致命缺陷；但存在 **2 个 P0 阻断项**：

1. **T6 复盘引导卡**：页面打开即抛 TypeError，抽卡功能实际不可用（主功能失效）；
2. **G4 你画我猜**：猜词环节看不到画作，「画→猜」核心闭环断裂（主功能失效）。

按交付标准（每个页面打开即可用、功能正常、无致命缺陷），需由 Engineer 修复上述 P0 后，QA 进行第 2 轮回归验证（重点：T6 抽卡/已抽列表全流程、G4 猜词阶段画作可见性 + 完整对局），全部通过后方可上线。
