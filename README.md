# aiworkdb.github.io

> AI 工具收集、桌游设计、团建游戏与儿童绘本的资源整合平台

## 项目简介

本项目是一个资源收集与创作平台，涵盖以下核心模块：

- **AI 工具导航**：系统性整理和收录各类优质 AI 工具
- **桌游设计**：85 款原创桌游，含设计文档、开发工具和可打印素材
- **团建游戏库**：面向培训师与团建教练的游戏与流程资源库（55+ 款游戏）
- **儿童绘本**：互动绘本设计与教具资源（小步绘本品牌，2 套绘本）
- **AI 笔记增强**：浏览器扩展，为 AI 笔记平台提供 Markdown 渲染、图表、公式等功能
- **小游戏**：休闲 HTML 小游戏集合

---

## 目录结构

```
aiworkdb.github.io/
├── README.md                        # 本文件，项目索引
├── LICENSE                          # 开源协议
├── CNAME                            # 自定义域名
├── aitool.md                        # AI 工具导航大全
├── wechat-51.md                     # 微信相关文档
│
├── boardgames/                      # 桌游项目（85 款）
│   ├── README.md                    # 桌游索引目录
│   ├── development-guide.md         # 开发规范文档
│   ├── category/                    # 按类别分类
│   │   ├── strategy/               # 策略类（23 款）
│   │   ├── party/                  # 派对类（16 款）
│   │   ├── card/                   # 卡牌类（16 款）
│   │   └── cooperative/            # 合作类（30 款）
│   └── tools/                      # 工具集（卡牌生成器）
│
├── teambuilding/                    # 团建 & 培训游戏库（55+ 款）
│   ├── README.md                    # 游戏索引与使用指南
│   ├── guide.md                     # 教练使用指南
│   ├── ROADMAP.md                   # 项目路线图
│   ├── index.html                   # 在线导航页
│   ├── games/                       # 游戏文档（按目的分类）
│   │   ├── icebreaker/             # 破冰热场
│   │   ├── communication/          # 沟通表达
│   │   ├── collaboration/          # 团队协作
│   │   ├── trust/                  # 信任建立
│   │   ├── leadership/             # 领导力
│   │   ├── creativity/             # 创新思维
│   │   └── problem-solving/        # 问题解决
│   ├── flows/                       # 团建流程方案（6 套模板）
│   ├── online/                      # 线上团建游戏
│   ├── toolbox/                     # 教练工具箱
│   └── images/                      # 插图与封面
│
├── pbook/                           # 儿童绘本（小步绘本）
│   ├── story.md                     # 绘本1 故事内容
│   ├── parent-sop.md                # 家长引导话术SOP
│   ├── task-cards.md                # 练习任务卡
│   ├── teaching-aids.md             # 互动教具方案
│   ├── picture-book-tidy-*.html     # 绘本1 HTML（v1/v2/v3）
│   ├── minnie-birthday/             # 绘本2：《米妮的生日派对》
│   └── assets/                      # 素材资源
│
├── ainote/                          # AI 笔记浏览器扩展
│   ├── manifest.json                # 扩展清单
│   ├── CHROME_EXTENSION.md          # 扩展文档
│   ├── background.js / content.js   # 核心脚本
│   ├── renderers/                   # 渲染器（Mermaid/KaTeX/Graphviz 等）
│   ├── lib/                         # 第三方依赖库
│   └── assets/ / styles/            # 资源与样式
│
├── wechat-articles/                 # 微信公众号文章（7 篇）
├── game/                            # 休闲小游戏
├── prompt/                          # Prompt 资源
├── docs/                            # 项目文档（发布指南等）
├── scripts/                         # 工具脚本（发布/修复/封面等）
├── references/                      # 参考资料
└── images/                          # 根目录图片资源
```

---

## 快速导航

### AI 工具导航

📄 **[aitool.md](aitool.md)** - 全面的 AI 工具收录大全

收录类别：
- 🧠 AI 对话 / 大语言模型（ChatGPT、Claude、Gemini 等）
- 🎨 AI 图像生成（Midjourney、DALL·E、Stable Diffusion 等）
- 🎬 AI 视频生成（Sora、Runway、Kling AI 等）
- 🎵 AI 音频 / 音乐生成（Suno AI、Udio、ElevenLabs 等）
- ✍️ AI 写作 / 文案（Notion AI、Jasper、秘塔写作猫等）
- 💻 AI 编程助手（GitHub Copilot、Cursor、Windsurf 等）
- 📊 AI 数据分析（Julius AI、ChatGPT Code Interpreter 等）
- 🔍 AI 搜索引擎（Perplexity AI、You.com、Phind 等）
- 🎙️ AI 语音 / 转录（Whisper、Otter.ai、讯飞听见等）
- 🧩 AI 提示词工具（PromptHero、FlowGPT、AIPRM 等）
- 📄 AI 文档 / 知识库（Notion AI、Dify、Coze 等）
- 🎭 AI 角色扮演 / 虚拟人（Character.AI、Replika、HeyGen 等）
- 🛠️ AI 工作流 / 自动化（Zapier AI、Make、n8n 等）
- 📱 AI 应用开发平台（OpenAI API、Anthropic API、Groq 等）

---

### 桌游设计项目

📁 **[boardgames/](boardgames/)** - 85 款原创桌游

#### 桌游统计

| 类别 | 数量 | 说明 |
| :--- | :--- | :--- |
| 🎯 策略类 | 23 款 | 需要深思熟虑的策略游戏 |
| 🎉 派对类 | 16 款 | 适合聚会娱乐的轻松游戏 |
| 🃏 卡牌类 | 16 款 | 以卡牌为核心机制的游戏 |
| 🤝 合作类 | 30 款 | 玩家共同对抗游戏系统的游戏 |
| **总计** | **85 款** | 持续更新中 |

#### 主要资源

| 资源 | 说明 | 链接 |
| :--- | :--- | :--- |
| 桌游索引 | 所有桌游的索引目录 | [boardgames/README.md](boardgames/README.md) |
| 开发规范 | 桌游项目开发流程与规范 | [development-guide.md](boardgames/development-guide.md) |
| 卡牌生成器 | 在线创建和打印桌游卡牌 | [tools/card-maker.html](boardgames/tools/card-maker.html) |

#### 精选推荐

| 游戏名称 | 类别 | 玩家 | 时长 | 难度 | 链接 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 宝藏猎人 | 策略 | 2-4人 | 45-60分钟 | 中等 | [查看](boardgames/category/strategy/treasure-hunter/README.md) |
| 星际贸易站 | 策略 | 2-4人 | 60-90分钟 | 中等/困难 | [查看](boardgames/category/strategy/starport-trader/README.md) |
| 魔法学院 | 合作 | 2-4人 | 45-60分钟 | 中等 | [查看](boardgames/category/cooperative/magic-academy/README.md) |
| 时间特工 | 派对 | 4-8人 | 20-40分钟 | 中等 | [查看](boardgames/category/party/time-agents/README.md) |
| 文明密语 | 卡牌 | 2-5人 | 30-50分钟 | 中等 | [查看](boardgames/category/card/civilization-cipher/README.md) |
| 芙莉莲的旅程 | 合作 | 2-4人 | 45-90分钟 | 中等 | [查看](boardgames/category/cooperative/frieren-journey/README.md) |
| 远征33：绘母之末 | 合作 | 2-4人 | 45-75分钟 | 中等/困难 | [查看](boardgames/category/cooperative/expedition-33/README.md) |

---

### 团建 & 培训游戏库

🎯 **[teambuilding/](teambuilding/)** - 面向培训师与团建教练的实用游戏与流程资源库

#### 游戏分类

| 类别 | 数量 | 说明 |
| :--- | :--- | :--- |
| 🧊 破冰热场 | 7 款 | 快速活跃气氛，打破陌生感 |
| 💬 沟通表达 | 7 款 | 提升倾听、表达与信息传递能力 |
| 🤝 团队协作 | 31 款 | 培养协作意识与团队默契 |
| 🔐 信任建立 | 2 款 | 建立团队信任基础 |
| 👑 领导力 | 3 款 | 训练决策、统筹与领导思维 |
| 💡 创新思维 | 2 款 | 激发创意与发散思考 |
| 🔧 问题解决 | 2 款 | 训练系统化分析与解决问题能力 |

#### 团建流程方案

| 方案 | 时长 | 人数 | 核心目标 |
| :--- | :--- | :--- | :--- |
| [一日团建模板](teambuilding/flows/one-day/) | 6-8 小时 | 15-50人 | 破冰+协作+复盘 |
| [半日团建模板](teambuilding/flows/half-day/01-schedule.md) | 3-4 小时 | 10-30人 | 快速凝聚 |
| [主题工作坊](teambuilding/flows/workshop/leadership-awakening.md) | 2.5-3 小时 | 12-24人 | 领导力深度培训 |
| [线上团建模板](teambuilding/flows/online/01-schedule.md) | 2-2.5 小时 | 8-30人 | 远程团队团建 |
| [新员工融入流程](teambuilding/flows/onboarding/01-schedule.md) | 3-4 小时 | 8-20人 | 新员工快速融入 |
| [跨部门协作流程](teambuilding/flows/cross-dept/01-schedule.md) | 6-7 小时 | 15-30人 | 打破部门墙 |

#### 教练工具箱

| 工具 | 说明 | 链接 |
| :--- | :--- | :--- |
| 引导话术库 | 开场白、规则讲解、介入干预模板 | [facilitation.md](teambuilding/toolbox/facilitation.md) |
| 复盘框架 | 4F模型、提问清单、复盘话术 | [debrief.md](teambuilding/toolbox/debrief.md) |
| 安全管理 | 户外安全清单、突发预案、免责声明 | [safety.md](teambuilding/toolbox/safety.md) |
| 物资清单 | 通用物资、分组方法、评估问卷 | [checklist.md](teambuilding/toolbox/checklist.md) |

#### 微信推广文章

📰 **[wechat-articles/](wechat-articles/)** - 7 篇团建游戏库推广文章（开篇总介、破冰专题、沟通专题、协作专题、信任专题、领导力+创意专题、实战指南）

---

### 儿童绘本（小步绘本）

📚 **[pbook/](pbook/)** - 互动儿童绘本设计与教具资源

#### 绘本1：《玩具的家在哪里？》

**主题**：生活习惯 / 整理收纳 | **适龄**：3-6 岁

| 资源 | 说明 | 链接 |
| :--- | :--- | :--- |
| 绘本故事 | 完整故事内容与画面描述 | [story.md](pbook/story.md) |
| 家长SOP | 逐页共读引导话术（情绪教练三步法） | [parent-sop.md](pbook/parent-sop.md) |
| 任务卡 | 5 个递进式生活实践任务 | [task-cards.md](pbook/task-cards.md) |
| 教具方案 | 3 页互动教具（寻家地图、魔法师证书、整理日记） | [teaching-aids.md](pbook/teaching-aids.md) |
| 绘本HTML | 可交互的绘本网页版本 | [v1](pbook/picture-book-tidy-v1.html) / [v2](pbook/picture-book-tidy-v2.html) / [v3](pbook/picture-book-tidy-v3.html) |

#### 绘本2：《米妮的生日派对》

**主题**：情绪管理 | **适龄**：3-6 岁

| 资源 | 说明 | 链接 |
| :--- | :--- | :--- |
| 绘本HTML | 32 页完整绘本（含 3 个互动教具：情绪温度计、呼吸魔法、情绪日记） | [查看绘本](pbook/minnie-birthday/picture-book-minnie-v1.html) |

---

### AI 笔记浏览器扩展

🧩 **[ainote/](ainote/)** - AI 笔记增强浏览器扩展

为 AI 笔记平台提供强大的内容渲染能力：

- 📝 **Markdown 渲染**：完整支持 Markdown 语法
- 📊 **Mermaid 图表**：流程图、时序图、类图等可视化
- 🎨 **代码高亮**：支持 200+ 编程语言的语法高亮
- 🧮 **KaTeX 公式**：数学公式渲染
- 📐 **Graphviz / D2 / PlantUML**：图形可视化支持
- 📓 **Jupyter Notebook**：`.ipynb` 文件渲染

详细安装与使用请参考 [CHROME_EXTENSION.md](ainote/CHROME_EXTENSION.md)。

---

### 小游戏

🎮 **[game/](game/)** - 休闲小游戏集合

| 游戏名称 | 说明 | 链接 |
| :--- | :--- | :--- |
| 重力翻转 | 重力感应的休闲游戏 | [gravity-flip.html](game/gravity-flip.html) |
| 双生逆行 | 阴阳双世界的障碍挑战游戏 | [shuangsheng/](game/shuangsheng/) |

---

## 使用指南

### AI 工具导航

直接查看 [aitool.md](aitool.md)，按需浏览各类 AI 工具，每个工具包含简介、官网链接和收费模式说明。

### 桌游设计

1. **浏览桌游**：查看 [boardgames/README.md](boardgames/README.md) 了解 85 款桌游
2. **使用工具**：打开 [卡牌生成器](boardgames/tools/card-maker.html) 创建自定义卡牌
3. **添加新桌游**：参考 [开发规范](boardgames/development-guide.md) 创建新项目

### 团建游戏

1. **选游戏**：查看 [teambuilding/README.md](teambuilding/README.md)，按目的/形式/人数/时长四维筛选
2. **看流程**：参考 [flows/](teambuilding/flows/) 目录选择合适的团建流程模板
3. **用工具**：查阅 [教练工具箱](teambuilding/toolbox/) 获取话术、复盘框架和安全清单
4. **新手入门**：先读 [教练使用指南](teambuilding/guide.md)（5 分钟快速上手）

### 儿童绘本

打开绘本 HTML 文件即可在线阅读，配套家长SOP和任务卡可打印使用。

### 玩游戏

打开 [game/gravity-flip.html](game/gravity-flip.html) 开始游戏。

---

## 项目特点

- 📚 **系统性整理**：AI 工具按功能分类，桌游按类别归档
- 🎮 **开箱即用**：桌游提供完整可打印素材，团建游戏即拿即用
- 🎯 **四维筛选**：团建游戏支持目的/形式/人数/时长四维检索
- 🧩 **浏览器扩展**：AI 笔记增强扩展，支持 200+ 语言高亮
- 📚 **儿童绘本**：互动绘本设计，配套家长SOP、任务卡和教具
- 📖 **文档完善**：每个项目都有完整的说明文档
- 🆓 **免费使用**：所有资源可免费使用和打印
- 🔄 **持续更新**：桌游库、团建游戏库持续扩充

---

## 贡献与反馈

欢迎提供以下建议：
- 推荐优质 AI 工具
- 提交新的桌游设计
- 补充团建游戏或流程方案
- 设计新的儿童绘本
- 改进现有文档
- 报告问题或错误

---

*最后更新：2026-07-31*
