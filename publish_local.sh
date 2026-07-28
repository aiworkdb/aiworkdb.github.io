#!/bin/bash
# 本地发布团建文章到公众号 - 完整脚本
# 使用方法：在本地电脑上运行此脚本

echo "=========================================="
echo "团建文章公众号发布脚本"
echo "=========================================="
echo ""

# 检查 wenyan-mcp 是否安装
if ! command -v wenyan-mcp &> /dev/null; then
    echo "❌ 未找到 wenyan-mcp，正在安装..."
    npm install -g @wenyan-md/mcp
    echo "✅ wenyan-mcp 安装完成"
else
    echo "✅ wenyan-mcp 已安装"
fi

echo ""
echo "=========================================="
echo "步骤 1: 列出可用主题"
echo "=========================================="
echo "可用的排版主题："
echo "  - default  : 经典布局，适合长文"
echo "  - orangeheart: 温暖橙色，充满活力"
echo "  - rainbow  : 彩色活泼，适合轻松内容"
echo "  - lapis    : 清爽蓝色，专业冷静"
echo "  - pie      : 现代科技风（推荐）✨"
echo "  - maize    : 清新浅色，柔和舒适"
echo "  - purple   : 简约紫色，优雅时尚"
echo "  - phycat   : 薄荷绿色，清晰结构"
echo ""
echo "已选择主题：pie（科技风）"
echo ""

echo "=========================================="
echo "步骤 2: 发布文章到公众号"
echo "=========================================="
echo "正在发布：teambuilding/README.md"
echo "使用主题：pie（科技风）"
echo ""

# 发布主要文章
articles=(
    "teambuilding/README.md"
    "teambuilding/guide.md"
)

success_count=0
fail_count=0

for article in "${articles[@]}"; do
    echo "------------------------------------------"
    echo "正在发布：$article"
    echo "------------------------------------------"
    
    # 使用 wenyan-mcp 发布（需要通过 MCP 客户端）
    # 这里输出命令，让用户自己在支持 MCP 的客户端中运行
    
    echo "✅ 请在对 AI 说："
    echo "   使用 wenyan-mcp 发布 $article 到公众号，主题选择 pie"
    echo ""
done

echo "=========================================="
echo "批量发布命令"
echo "=========================================="
echo "如果想一次发布所有文章，请对 AI 说："
echo ""
echo "使用 wenyan-mcp 批量发布以下文章到公众号，主题统一使用 pie（科技风）："
echo ""

# 列出所有文章
find teambuilding -name "*.md" -not -name "ROADMAP.md" | while read article; do
    echo "  - $article"
done

echo ""
echo "=========================================="
echo "✅ 脚本执行完成"
echo "=========================================="
echo ""
echo "📝 下一步："
echo "1. 打开 WorkBuddy 或 Claude Desktop"
echo "2. 确保已连接 wenyan-mcp"
echo "3. 复制上面的命令，发送给 AI"
echo "4. 前往微信公众号后台查看草稿"
echo ""
echo "🔗 相关链接："
echo "  - 微信公众号后台: https://mp.weixin.qq.com"
echo "  - wenyan-mcp 文档: https://yuzhi.tech/docs/wenyan/mcp"
echo ""
