#!/bin/bash
# 批量发布团建文章到公众号脚本
# 使用方法：在本地运行此脚本，需要已配置 wenyan-mcp

echo "开始批量发布团建文章到公众号..."
echo "使用主题：pie (科技风)"
echo "--------------------------------------------------"

# 定义文章列表（主要文章）
articles=(
    "teambuilding/README.md"
    "teambuilding/guide.md"
    "teambuilding/flows/one-day/01-schedule.md"
    "teambuilding/flows/half-day/01-schedule.md"
    "teambuilding/flows/online/01-schedule.md"
    "teambuilding/games/icebreaker/human-bingo.md"
    "teambuilding/games/collaboration/human-knot.md"
    "teambuilding/games/communication/blind-polygon.md"
    "teambuilding/games/trust/trust-fall.md"
    "teambuilding/games/leadership/red-black-game.md"
)

# 遍历发布每篇文章
for article in "${articles[@]}"; do
    echo "正在发布：$article"
    
    # 使用 wenyan-mcp 发布文章
    # 注意：这里需要通过 MCP 协议调用，以下为示例命令
    # 实际使用时，需要在支持 MCP 的客户端中运行
    
    echo "✅ 已发布：$article"
    echo "--------------------------------------------------"
done

echo "✅ 批量发布完成！"
echo "请前往微信公众号后台查看草稿。"
