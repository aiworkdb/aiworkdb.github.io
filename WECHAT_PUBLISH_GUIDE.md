# 团建文章公众号发布指南

## ✅ 已完成
- [x] 所有团建文章已添加 frontmatter（title、cover、source_url）
- [x] 文章格式符合 wenyan-mcp 要求

## 📋 发布步骤

### 方案 A：使用 WorkBuddy 本地客户端（推荐）

1. **在本地打开 WorkBuddy**，确保已连接 `wenyan-mcp`

2. **逐篇发布**，对 AI 说：
   ```
   使用 wenyan-mcp 发布 teambuilding/README.md 到公众号，
   主题选择 pie（科技风）
   ```

3. **批量发布**，对 AI 说：
   ```
   使用 wenyan-mcp 批量发布以下文章到公众号，
   主题统一使用 pie（科技风）：
   - teambuilding/README.md
   - teambuilding/guide.md
   - teambuilding/flows/one-day/01-schedule.md
   - teambuilding/games/icebreaker/human-bingo.md
   ```

### 方案 B：使用命令行（高级）

```bash
# 1. 列出可用主题
npx @wenyan-md/mcp list_themes

# 2. 发布单篇文章（需要通过 MCP 客户端）
# 在 Claude Desktop 或支持 MCP 的客户端中运行

# 3. 查看草稿
# 前往微信公众号后台 -> 草稿箱
```

## 🎨 主题选择

**推荐主题：`pie`**
- 描述：现代、锐利、时尚（受 sspai.com 和 Misty 启发）
- 风格：科技风、简洁、专业
- 适合：技术团队、企业培训、现代风格内容

**备选主题：**
- `lapis`：清爽蓝色，适合冷静专业风格
- `purple`：简约紫色，适合优雅风格
- `default`：经典布局，适合长文阅读

## 📝 已整理的文章列表

### 主要文章（推荐优先发布）
1. `teambuilding/README.md` - 团建游戏库介绍
2. `teambuilding/guide.md` - 教练使用指南
3. `teambuilding/flows/one-day/01-schedule.md` - 全天团建流程
4. `teambuilding/flows/half-day/01-schedule.md` - 半日团建流程

### 游戏文章（可选发布）
- 破冰游戏：human-bingo、two-truths-one-lie、name-chain 等
- 协作游戏：human-knot、ball-relay、eyebrow-stick 等
- 沟通游戏：blind-polygon、draw-guess、telephone-game 等
- 信任游戏：trust-fall、blind-walk
- 领导力游戏：red-black-game、silent-leader、tangram
- 创新游戏：10-yuan-idea、newspaper-tower
- 问题解决游戏：desert-survival、egg-drop

## ⚠️ 注意事项

1. **IP 白名单**：确保运行 wenyan-mcp 的机器 IP 已添加到微信公众号后台
2. **预览确认**：发布后请在微信公众号后台预览确认排版效果
3. **封面图**：如需更换封面图，修改每篇文章的 `cover` 字段
4. **批量发布**：建议先发布 1-2 篇测试效果，再批量发布

## 🔗 相关链接

- wenyan-mcp 文档：https://yuzhi.tech/docs/wenyan/mcp
- 团建游戏库预览：https://aiworkdb.github.io/teambuilding/
- 微信公众号后台：https://mp.weixin.qq.com
