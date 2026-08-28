#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将文章中的相对路径链接转换为完整的绝对URL

问题：文章中的链接使用相对路径（如 games/icebreaker/human-bingo.md），
发布到微信公众号后用户无法访问引用的文章。

解决方案：将所有相对路径链接转换为完整的绝对URL，格式为：
https://ai.aitboy.cn/teambuilding/xxx/xxx.html

使用方法：
python fix_links.py

作者：AIWorkDB
日期：2026-07-07
"""

import os
import re
import glob

# 配置
BASE_URL = "https://ai.aitboy.cn"
TEAMBUILDING_DIR = "teambuilding"

# 待处理的文章列表
ARTICLES = [
    "teambuilding/README.md",
    "teambuilding/guide.md",
    "teambuilding/flows/one-day/01-schedule.md",
    "teambuilding/flows/half-day/01-schedule.md",
    "teambuilding/flows/online/01-schedule.md"
]

def convert_link(file_dir, match):
    """
    将相对路径链接转换为绝对URL
    
    输入：文件所在目录，匹配对象（包含 [文字](路径) 格式）
    输出：转换后的 [文字](完整URL)
    """
    text = match.group(1)
    path = match.group(2)
    
    # 如果已经是完整URL，检查是否需要替换域名
    if path.startswith("http://") or path.startswith("https://"):
        path = path.replace("https://aiworkdb.github.io", BASE_URL)
        path = path.replace("http://aiworkdb.github.io", BASE_URL)
        return f"[{text}]({path})"
    
    # 如果是图片路径，跳过（图片会被上传到公众号）
    if path.endswith(".png") or path.endswith(".jpg") or path.endswith(".jpeg") or path.endswith(".svg"):
        return f"[{text}]({path})"
    
    # 处理相对路径
    # 移除 .md 扩展名，添加 .html
    if path.endswith(".md"):
        path = path[:-3] + ".html"
    elif path.endswith("/"):
        path = path + "index.html"
    elif not path.endswith(".html"):
        path = path + ".html"
    
    # 根据文件所在目录计算完整路径
    # 文件路径：teambuilding/guide.md -> 文件目录：teambuilding/
    # 相对路径：README.md -> 完整路径：teambuilding/README.html
    # 相对路径：games/icebreaker/human-bingo.md -> 完整路径：teambuilding/games/icebreaker/human-bingo.html
    
    full_path = os.path.normpath(os.path.join(file_dir, path))
    
    # 移除开头的 teambuilding/
    if full_path.startswith("teambuilding/"):
        full_path = full_path[len("teambuilding/"):]
    
    # 添加完整的 URL
    full_url = BASE_URL + "/teambuilding/" + full_path
    
    return f"[{text}]({full_url})"

def process_file(file_path):
    """
    处理单个文件，转换其中的链接
    """
    print(f"\n处理文件: {file_path}")
    
    # 获取文件所在目录
    file_dir = os.path.dirname(file_path)
    
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复已有的错误链接（重复的 teambuilding/teambuilding）
    content = content.replace("/teambuilding/teambuilding/", "/teambuilding/")
    
    # 使用正则表达式匹配并替换所有 Markdown 链接
    # 匹配模式：[文字](路径)
    pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    new_content = re.sub(pattern, lambda m: convert_link(file_dir, m), content)
    
    # 替换 source_url 字段中的域名
    new_content = new_content.replace("https://aiworkdb.github.io", BASE_URL)
    new_content = new_content.replace("http://aiworkdb.github.io", BASE_URL)
    
    # 统计替换数量
    original_count = len(re.findall(pattern, content))
    converted_count = len(re.findall(r'\[([^\]]+)\]\((https://ai\.aitboy\.cn[^)]+)\)', new_content))
    
    # 写入修改后的内容
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"  替换完成: {converted_count} / {original_count} 个链接")
    return converted_count

def main():
    """主函数"""
    print("="*60)
    print("文章链接转换工具")
    print("="*60)
    print(f"\n配置信息:")
    print(f"  基础 URL: {BASE_URL}")
    print(f"  待处理文章数: {len(ARTICLES)}")
    print(f"\n开始转换...")
    
    total_converted = 0
    
    for article in ARTICLES:
        if os.path.exists(article):
            converted = process_file(article)
            total_converted += converted
        else:
            print(f"\n警告: 文件不存在 - {article}")
    
    print(f"\n{'='*60}")
    print("转换完成!")
    print(f"{'='*60}")
    print(f"\n📊 统计:")
    print(f"   已处理文章: {len(ARTICLES)} 篇")
    print(f"   已转换链接: {total_converted} 个")
    
    print(f"\n📝 下一步:")
    print(f"   1. 运行发布脚本: python3 publish_local.py")
    print(f"   2. 登录公众号后台查看草稿")
    print(f"   3. 验证链接是否正确")

if __name__ == "__main__":
    main()