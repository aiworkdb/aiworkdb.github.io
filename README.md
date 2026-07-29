# aiworkdb.github.io

> AI 工具收集与桌游设计资源的整合项目

## 项目简介

本项目是一个资源收集与创作平台，主要包含以下模块：

- **AI 工具导航**：系统性整理和收录各类优质 AI 工具
- **桌游设计**：提供桌游设计文档、开发工具和可打印素材
- **AI 笔记增强**：浏览器扩展，为 AI 笔记平台提供 Markdown 渲染、Mermaid 图表、代码高亮等功能
- **儿童绘本**：互动绘本设计与教具资源（小步绘本品牌）
- **小游戏**：休闲小游戏集合

---

## 目录结构

```
aiworkdb.github.io/
├── README.md                    # 本文件，项目索引
├── LICENSE                      # 开源协议
├── CNAME                         # 自定义域名
├── aitool.md                    # AI 工具导航大全
├── wechat-51.md                 # 微信相关文档
├── boardgames/                  # 桌游项目目录
│   ├── README.md                # 桌游索引目录
│   ├── development-guide.md      # 桌游开发规范文档
│   ├── category/                # 按类别分类的桌游
│   │   ├── strategy/           # 策略类桌游（23款）
│   │   ├── party/              # 派对类桌游（16款）
│   │   ├── card/               # 卡牌类桌游（16款）
│   │   └── cooperative/         # 合作类桌游（30款）
│   └── tools/                   # 桌游工具集
│       ├── README.md           # 工具说明文档
│       └── card-maker.html     # 卡牌生成器
├── ainote/                      # AI 笔记浏览器扩展
│   ├── manifest.json           # 扩展清单
│   ├── background.js           # 后台脚本
│   ├── content.js              # 内容脚本
│   └── ...                     # 渲染器、样式、依赖库等
├── pbook/                       # 儿童绘本（小步绘本）
│   ├── story.md                 # 绘本故事内容
│   ├── parent-sop.md            # 家长引导话术SOP
│   ├── task-cards.md            # 练习任务卡
│   ├── teaching-aids.md         # 互动教具方案
│   ├── picture-book-tidy-*.html # 绘本HTML版本
│   └── assets/                  # 素材资源（图片、SVG教具）
├── game/                        # 小游戏
│   ├── README.md               # 游戏索引
│   ├── gravity-flip.html       # 重力翻转游戏
│   └── shuangsheng/            # 双生逆行游戏
└── prompt/                      # Prompt 资源
    └── wechat.md               # 微信相关 Prompt
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

📁 **[boardgames/](boardgames/)** - 桌游设计与开发资源

#### 桌游统计

| 类别 | 数量 | 说明 |
| :--- | :--- | :--- |
| 🎯 策略类 | 23款 | 需要深思熟虑的策略游戏 |
| 🎉 派对类 | 16款 | 适合聚会娱乐的轻松游戏 |
| 🃏 卡牌类 | 16款 | 以卡牌为核心机制的游戏 |
| 🤝 合作类 | 30款 | 玩家共同对抗游戏系统的游戏 |
| **总计** | **85款** | 持续更新中 |

#### 主要资源

| 资源 | 说明 | 链接 |
| :--- | :--- | :--- |
| 桌游索引 | 所有桌游的索引目录 | [boardgames/README.md](boardgames/README.md) |
| 开发规范 | 桌游项目开发流程与规范 | [development-guide.md](boardgames/development-guide.md) |
| 卡牌生成器 | 在线创建和打印桌游卡牌 | [tools/card-maker.html](boardgames/tools/card-maker.html) |
| 工具说明 | 桌游工具集使用文档 | [tools/README.md](boardgames/tools/README.md) |

#### 精选桌游推荐

| 游戏名称 | 类别 | 玩家人数 | 游戏时长 | 难度 | 链接 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 宝藏猎人 | 策略 | 2-4人 | 45-60分钟 | 中等 | [查看详情](boardgames/category/strategy/treasure-hunter/README.md) |
| 星际贸易站 | 策略 | 2-4人 | 60-90分钟 | 中等/困难 | [查看详情](boardgames/category/strategy/starport-trader/README.md) |
| 魔法学院 | 合作 | 2-4人 | 45-60分钟 | 中等 | [查看详情](boardgames/category/cooperative/magic-academy/README.md) |
| 时间特工 | 派对 | 4-8人 | 20-40分钟 | 中等 | [查看详情](boardgames/category/party/time-agents/README.md) |
| 文明密语 | 卡牌 | 2-5人 | 30-50分钟 | 中等 | [查看详情](boardgames/category/card/civilization-cipher/README.md) |
| 芙莉莲的旅程 | 合作 | 2-4人 | 45-90分钟 | 中等 | [查看详情](boardgames/category/cooperative/frieren-journey/README.md) |
| 天命人 | 合作 | 1-4人 | 60-90分钟 | 中等偏难 | [查看详情](boardgames/category/cooperative/destined-one/README.md) |
| 远征33：绘母之末 | 合作 | 2-4人 | 45-75分钟 | 中等/困难 | [查看详情](boardgames/category/cooperative/expedition-33/README.md) |

#### 可用工具

- 🃏 **[卡牌生成器](boardgames/tools/card-maker.html)**：可视化创建和打印桌游卡牌，支持多种卡牌类型和自定义样式

---

### AI 笔记浏览器扩展

🧩 **[ainote/](ainote/)** - AI 笔记增强浏览器扩展

为 AI 笔记平台提供强大的内容渲染能力：

- 📝 **Markdown 渲染**：完整支持 Markdown 语法
- 📊 **Mermaid 图表**：流程图、时序图、类图等可视化
- 🎨 **代码高亮**：支持多种编程语言的语法高亮
- 🧮 **KaTeX 公式**：数学公式渲染
- 📐 **Graphviz / D2**：图形可视化支持

---

### 儿童绘本（小步绘本）

📚 **[pbook/](pbook/)** - 互动儿童绘本设计与教具资源

**品牌**：小步绘本 | **主题**：生活习惯 / 整理收纳 | **适龄**：3-6岁

#### 资源清单

| 资源 | 说明 | 链接 |
| :--- | :--- | :--- |
| 绘本故事 | 《玩具的家在哪里？》完整故事内容与画面描述 | [story.md](pbook/story.md) |
| 家长SOP | 逐页共读引导话术（情绪教练三步法） | [parent-sop.md](pbook/parent-sop.md) |
| 任务卡 | 5个递进式生活实践任务 | [task-cards.md](pbook/task-cards.md) |
| 教具方案 | 3页互动教具（寻家地图、魔法师证书、整理日记） | [teaching-aids.md](pbook/teaching-aids.md) |
| 绘本HTML | 可交互的绘本网页版本 | [v1](pbook/picture-book-tidy-v1.html) / [v2](pbook/picture-book-tidy-v2.html) / [v3](pbook/picture-book-tidy-v3.html) |

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

直接查看 [aitool.md](aitool.md) 文件，按需浏览各类 AI 工具，每个工具都包含简介、官网链接和收费模式说明。

### 桌游设计

1. **浏览现有桌游**：查看 [boardgames/README.md](boardgames/README.md) 了解已收录的 85 款桌游
2. **使用工具**：打开 [卡牌生成器](boardgames/tools/card-maker.html) 创建自定义卡牌
3. **添加新桌游**：参考 [开发规范](boardgames/development-guide.md) 创建新桌游项目

### 玩游戏

打开 [game/gravity-flip.html](game/gravity-flip.html) 开始游戏。

---

## 项目特点

- 📚 **系统性整理**：AI 工具按功能分类，便于查找
- 🎮 **开箱即用**：桌游提供完整的可打印素材
- 🛠️ **工具完善**：提供卡牌生成器等实用工具
- 🧩 **浏览器扩展**：AI 笔记增强扩展，提升阅读体验
- 📚 **儿童绘本**：互动绘本设计，配套家长SOP、任务卡和教具
- 📖 **文档详细**：每个项目都有完整的说明文档
- 🆓 **免费使用**：所有资源可免费使用和打印
- 🎯 **持续更新**：桌游库持续扩充，涵盖多种类型

---

## 贡献与反馈

欢迎提供以下建议：
- 推荐优质 AI 工具
- 提交新的桌游设计
- 改进现有文档
- 报告问题或错误

---

*最后更新：2026-07-29*
