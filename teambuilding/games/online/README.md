# games/online —— 在线版游戏说明

本目录**不在** `build.py` 的 `CATEGORIES` 列表中，因此这里的 `.md` **不会**被渲染成官网页面。
它只存放「官网没有独立详情页、但需要留档说明」的在线版游戏文档。

## 目录约定

| 文件 | 说明 |
|---|---|
| `online-bingo.md` | 线上宾果（Online Bingo）的玩法说明。页面本体是同目录下的手写静态页 `online-bingo.html`，由 `plan-generator` 工具的 `EXTRA_PLAN` 条目引用。 |

## 禁止事项 ⚠️

**不要把已经有分类目录版本的游戏文档往这里再放一份。**

同一个游戏只能有一份事实源。已经收录进游戏库、并在官网生成了详情页的游戏，
其权威文档在对应的分类目录里：

| 游戏 | 权威文档 | 官网页面 |
|---|---|---|
| 我从未（Never Have I Ever） | `games/icebreaker/never-have-i-ever.md` | `games/icebreaker/never-have-i-ever.html` |
| 团队知识竞答（Team Quiz） | `games/variety/team-quiz.md` | `games/variety/team-quiz.html` |
| 虚拟密室逃脱（Virtual Escape） | `games/problem-solving/virtual-escape.md` | `games/problem-solving/virtual-escape.html` |
| 你画我猜（Pictionary） | `games/communication/you-draw-i-guess.md` | `games/communication/you-draw-i-guess.html` |

历史原因：早期这 4 款游戏只有本目录下的 md（且用的是旧格式：无 frontmatter、
人数与时长口径已过期）。它们已迁移到上表的分类目录，本目录下的副本已删除。

> **内容一致性铁律**：一个游戏的规则/人数/时长改动，必须同时改
> 「游戏库 md + 公众号文章源 + 在线版实现」三处。
> 本目录不属于这三处中的任何一处，只是补充说明，不要在这里维护规则数值。
