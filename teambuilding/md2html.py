#!/usr/bin/env python3
"""
将 teambuilding/games/ 下的 .md 文件批量转换为 .html 文件
模板风格与现有 human-bingo.html / trust-fall.html 保持一致
"""
import os
import re
import sys
from pathlib import Path

# ── HTML 模板 ────────────────────────────────────────────────────────────────
TEMPLATE = """<!DOCTYPE html>
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
                <li><a href="{home_link}">← 返回首页</a></li>
                <li><a href="{games_link}">返回游戏库</a></li>
            </ul>
        </nav>

        <article>
            {body}
        </article>
    </main>
</body>
</html>"""

# ── Markdown 基础解析器（不依赖外部库）────────────────────────────────────
def md_to_html(text: str) -> str:
    """将基础 Markdown 转换为 HTML（处理标题、加粗、列表、表格、引用、代码等）"""
    lines = text.split('\n')
    html_lines = []
    in_table = False
    in_list_ul = False
    in_list_ol = False
    in_blockquote = False
    in_pre = False
    table_rows = []

    def close_lists():
        nonlocal in_list_ul, in_list_ol
        if in_list_ul:
            html_lines.append('</ul>')
            in_list_ul = False
        if in_list_ol:
            html_lines.append('</ol>')
            in_list_ol = False

    def close_blockquote():
        nonlocal in_blockquote
        if in_blockquote:
            html_lines.append('</blockquote>')
            in_blockquote = False

    def close_table():
        nonlocal in_table, table_rows
        if in_table and table_rows:
            html_lines.append('<table>')
            for i, row in enumerate(table_rows):
                if i == 0:
                    html_lines.append('<thead><tr>')
                    for cell in row:
                        html_lines.append(f'<th>{cell}</th>')
                    html_lines.append('</tr></thead><tbody>')
                else:
                    html_lines.append('<tr>')
                    for cell in row:
                        html_lines.append(f'<td>{cell}</td>')
                    html_lines.append('</tr>')
            html_lines.append('</tbody></table>')
            table_rows = []
            in_table = False

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # 表格检测
        if stripped.startswith('|') and '|' in stripped[1:]:
            close_lists()
            close_blockquote()
            if not in_table:
                in_table = True
                table_rows = []
            # 解析表格行
            cells = [c.strip() for c in stripped.split('|')]
            # 去掉首尾空字符串
            if cells and cells[0] == '':
                cells = cells[1:]
            if cells and cells[-1] == '':
                cells = cells[:-1]
            # 跳过分隔行（|---|---|）
            if not re.match(r'^[\s|:-]+$', stripped):
                table_rows.append(cells)
            i += 1
            continue
        else:
            close_table()

        # 代码块
        if stripped.startswith('```'):
            close_lists()
            close_blockquote()
            in_pre = not in_pre
            if in_pre:
                html_lines.append('<pre><code>')
            else:
                html_lines.append('</code></pre>')
            i += 1
            continue
        if in_pre:
            html_lines.append(line)
            i += 1
            continue

        # 引用
        if stripped.startswith('>'):
            close_lists()
            quote_content = stripped.lstrip('> ')
            html_lines.append(f'<blockquote>{quote_content}</blockquote>')
            i += 1
            continue
        else:
            close_blockquote()

        # 标题
        if stripped.startswith('# '):
            close_lists()
            html_lines.append(f'<h1>{stripped[2:]}</h1>')
        elif stripped.startswith('## '):
            close_lists()
            html_lines.append(f'<h2>{stripped[3:]}</h2>')
        elif stripped.startswith('### '):
            close_lists()
            html_lines.append(f'<h3>{stripped[4:]}</h3>')
        elif stripped.startswith('#### '):
            close_lists()
            html_lines.append(f'<h4>{stripped[5:]}</h4>')
        # 分隔线
        elif stripped.startswith('---'):
            close_lists()
            html_lines.append('<hr>')
        # 无序列表
        elif stripped.startswith('- ') or stripped.startswith('* '):
            if not in_list_ul:
                close_blockquote()
                in_list_ul = True
                html_lines.append('<ul>')
            content = stripped[2:]
            html_lines.append(f'<li>{content}</li>')
        # 有序列表
        elif re.match(r'^\d+\. ', stripped):
            if not in_list_ol:
                close_blockquote()
                in_list_ol = True
                html_lines.append('<ol>')
            content = re.sub(r'^\d+\. ', '', stripped)
            html_lines.append(f'<li>{content}</li>')
        # 空行
        elif stripped == '':
            close_lists()
            # 不添加额外内容
        # 普通段落
        else:
            close_lists()
            close_blockquote()
            if stripped:
                html_lines.append(f'<p>{stripped}</p>')

        i += 1

    close_table()
    close_lists()
    close_blockquote()
    if in_pre:
        html_lines.append('</code></pre>')

    return '\n'.join(html_lines)


def extract_title(md_text: str) -> str:
    """从 Markdown 中提取第一个标题作为页面标题"""
    for line in md_text.split('\n'):
        stripped = line.strip()
        if stripped.startswith('# '):
            return stripped[2:].strip()
    return '团建游戏'


def build_game_html(md_path: Path) -> str:
    """将一个游戏的 .md 文件转换为完整的 HTML 字符串"""
    md_text = md_path.read_text(encoding='utf-8')

    # 计算相对路径：从 games/分类名/文件名.html 到 teambuilding/index.html 需要上两级
    # games/icebreaker/foo.html -> ../../index.html
    home_link = '../../index.html'
    games_link = '../../index.html'

    title = extract_title(md_text)
    body_html = md_to_html(md_text)

    return TEMPLATE.format(
        title=title,
        home_link=home_link,
        games_link=games_link,
        body=body_html
    )


def main():
    base = Path('d:/mycode/aiworkdb.github.io/teambuilding/games')
    games_base = Path('d:/mycode/aiworkdb.github.io/teambuilding')

    # 确保团建首页存在
    index_html = games_base / 'index.html'
    if not index_html.exists():
        print(f"警告: {index_html} 不存在，链接可能无效")

    # 遍历所有子目录中的 .md 文件
    count = 0
    for md_path in base.rglob('*.md'):
        html_path = md_path.with_suffix('.html')
        # 强制覆盖重新生成
        print(f"生成: {html_path}")
        try:
            html_content = build_game_html(md_path)
            html_path.write_text(html_content, encoding='utf-8')
            count += 1
        except Exception as e:
            print(f"  错误: {e}")

    print(f"\n完成！共生成 {count} 个 HTML 文件")


if __name__ == '__main__':
    main()
