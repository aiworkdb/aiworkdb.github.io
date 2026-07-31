#!/usr/bin/env python3
"""
将线上团建游戏的Markdown文件转换为HTML文件
"""
import os
import re

def md_to_html(md_file, html_file):
    """将Markdown文件转换为HTML文件"""
    
    # 读取Markdown文件
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # 提取标题
    title_match = re.search(r'^# (.+)$', md_content, re.MULTILINE)
    title = title_match.group(1) if title_match else "团建游戏"
    
    # 提取描述（引用块）
    desc_match = re.search(r'^> (.+)$', md_content, re.MULTILINE)
    desc = desc_match.group(1) if desc_match else ""
    
    # 简单的Markdown到HTML转换
    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - 团建游戏</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@1/css/pico.min.css">
    <style>
        .tag {{ display: inline-block; padding: 0.25rem 0.5rem; margin: 0.25rem; font-size: 0.875rem; border-radius: 0.25rem; }}
        .tag-purpose {{ background: #e3f2fd; color: #1565c0; }}
        .tag-form {{ background: #f3e5f5; color: #7b1fa2; }}
        .tag-scene {{ background: #e8f5e9; color: #2e7d32; }}
        .difficulty {{ color: #ff9800; }}
        table {{ width: 100%; border-collapse: collapse; }}
        table th, table td {{ padding: 0.75rem; border: 1px solid #dee2e6; }}
        table th {{ background: #f8f9fa; }}
        blockquote {{ border-left: 4px solid #0077b6; padding-left: 1rem; margin: 1rem 0; }}
        code {{ background: #f8f9fa; padding: 0.25rem 0.5rem; border-radius: 0.25rem; }}
        pre {{ background: #f8f9fa; padding: 1rem; border-radius: 0.5rem; overflow-x: auto; }}
    </style>
</head>
<body>
    <main class="container">
        <nav>
            <ul>
                <li><a href="../../index.html">← 返回首页</a></li>
                <li><a href="../../index.html">返回游戏库</a></li>
            </ul>
        </nav>

        <article>
            <h1>{title}</h1>
            <blockquote>{desc}</blockquote>
"""
    
    # 转换Markdown内容（简化版）
    # 这里只是简单的转换，实际的转换需要更复杂的逻辑
    body = md_content
    
    # 移除YAML风格的元数据（> 开头的行）
    body = re.sub(r'^> .+$', '', body, flags=re.MULTILINE)
    
    # 转换标题
    body = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', body, flags=re.MULTILINE)
    body = re.sub(r'^### (.+)$', r'<h3>\1</h3>', body, flags=re.MULTILINE)
    body = re.sub(r'^## (.+)$', r'<h2>\1</h2>', body, flags=re.MULTILINE)
    body = re.sub(r'^# (.+)$', r'<h1>\1</h1>', body, flags=re.MULTILINE)
    
    # 转换表格（简化版，假设表格格式规范）
    # 这里需要更复杂的逻辑来正确转换表格
    
    # 转换列表
    body = re.sub(r'^- (.+)$', r'<li>\1</li>', body, flags=re.MULTILINE)
    
    # 转换粗体
    body = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', body)
    
    # 转换斜体
    body = re.sub(r'\*(.+?)\*', r'<em>\1</em>', body)
    
    # 转换代码块
    body = re.sub(r'```\n(.+?)\n```', r'<pre><code>\1</code></pre>', body, flags=re.DOTALL)
    
    # 转换行内代码
    body = re.sub(r'`(.+?)`', r'<code>\1</code>', body)
    
    # 转换水平线
    body = re.sub(r'^---$', r'<hr>', body, flags=re.MULTILINE)
    
    html_content += f"""
            {body}
        </article>
    </main>
</body>
</html>
"""
    
    # 写入HTML文件
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"已生成: {html_file}")

def main():
    """主函数"""
    md_dir = "d:/mycode/aiworkdb.github.io/teambuilding/online"
    html_dir = "d:/mycode/aiworkdb.github.io/teambuilding/games/online"
    
    # 确保HTML目录存在
    os.makedirs(html_dir, exist_ok=True)
    
    # 转换所有Markdown文件
    for filename in os.listdir(md_dir):
        if filename.endswith('.md'):
            md_file = os.path.join(md_dir, filename)
            html_file = os.path.join(html_dir, filename.replace('.md', '.html'))
            md_to_html(md_file, html_file)

if __name__ == "__main__":
    main()
