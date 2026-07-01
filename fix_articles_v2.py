#!/usr/bin/env python3
"""修复团建文章格式：清理冲突图片引用，统一使用 cover.png"""
import os
import re

ARTICLES = [
    'teambuilding/README.md',
    'teambuilding/guide.md',
    'teambuilding/flows/one-day/01-schedule.md',
    'teambuilding/flows/half-day/01-schedule.md',
    'teambuilding/flows/online/01-schedule.md',
]

for article in ARTICLES:
    if not os.path.exists(article):
        print(f"⚠️  不存在: {article}")
        continue

    with open(article, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # 1. 确保 frontmatter 有 cover: 字段（指向本地 images/cover.png）
    if content.startswith('---'):
        # 找 frontmatter 结束位置
        fm_end = content.index('---', 3)
        fm = content[0:fm_end+3]

        # 移除旧的 cover 行（如果有）
        fm = re.sub(r'\ncover:\s*".*?"', '', fm)

        # 在 source_url 前插入 cover
        if 'source_url:' in fm:
            fm = fm.replace(
                '\nsource_url:',
                '\ncover: "images/cover.png"\nsource_url:'
            )
        else:
            # 在 --- 结束前插入
            fm = fm.replace('\n---', '\ncover: "images/cover.png"\n---')

        content = fm + content[fm_end+3:]

    # 2. 删除正文中的远程图片引用（placehold.co / placeholder.com 等）
    content = re.sub(r'!\[封面图?\]\(https?://[^\)]+\).?\n?', '', content)
    content = re.sub(r'!\[封面\]\(https?://[^\)]+\).?\n?', '', content)

    # 3. 保留本地图片引用（images/cover.png），最多保留一个
    local_img_pattern = r'!\[.*?\]\(images/cover\.png\)'
    local_imgs = re.findall(local_img_pattern, content)
    if len(local_imgs) > 1:
        # 只保留第一个，删除其余
        first_pos = content.index(local_imgs[0])
        # 删除所有，再插回第一个
        content = re.sub(local_img_pattern + r'.?\n?', '', content)
        # 在第一个标题后插入
        lines = content.split('\n')
        new_lines = []
        inserted = False
        for i, line in enumerate(lines):
            new_lines.append(line)
            if not inserted and line.startswith('# ') and i < 20:
                new_lines.append('')
                new_lines.append('![封面](images/cover.png)')
                new_lines.append('')
                inserted = True
        content = '\n'.join(new_lines)
    elif len(local_imgs) == 0:
        # 没有本地图片引用，在第一个标题后插入
        lines = content.split('\n')
        new_lines = []
        inserted = False
        for i, line in enumerate(lines):
            new_lines.append(line)
            if not inserted and line.startswith('# ') and i < 20:
                new_lines.append('')
                new_lines.append('![封面](images/cover.png)')
                new_lines.append('')
                inserted = True
        content = '\n'.join(new_lines)

    # 4. 清理多余空行
    content = re.sub(r'\n{3,}', '\n\n', content)

    if content != original:
        with open(article, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 已修复: {article}")
    else:
        print(f"⚡ 无需修改: {article}")

print("\n✅ 所有文章已修复！")
print("\n下一步：")
print("  1. 确认 images/cover.png 存在于每个文章目录下")
print("  2. 重新运行 wenyan-mcp publish_article ...")
