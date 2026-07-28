#!/usr/bin/env python3
"""
批量整理团建文章格式，添加 wenyan-mcp 所需的 frontmatter
"""

import os
import re
import sys
from pathlib import Path

# 设置 stdout 编码为 UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# 配置
ROOT_DIR = Path("teambuilding")
DEFAULT_COVER = "https://images.unsplash.com/photo-1542744095-fcf48d80b0fd?w=1200"

# 根据文章分类选择不同的封面图
COVER_MAP = {
    "icebreaker": "https://images.unsplash.com/photo-1529156065689-4594dda70eb6?w=1200",  # 破冰
    "collaboration": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=1200",  # 协作
    "communication": "https://images.unsplash.com/photo-1573164713714-d95e370249db?w=1200",  # 沟通
    "trust": "https://images.unsplash.com/photo-1507537297725-24a6cae93a8f?w=1200",  # 信任
    "leadership": "https://images.unsplash.com/photo-1552664730-d307ca884978?w=1200",  # 领导力
    "creativity": "https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?w=1200",  # 创新
    "problem-solving": "https://images.unsplash.com/photo-1553481187-be93c21490a9?w=1200",  # 问题解决
    "flows": "https://images.unsplash.com/photo-1542744094-3a31f272c490?w=1200",  # 流程
    "toolbox": "https://images.unsplash.com/photo-1507537297725-24a6cae93a8f?w=1200",  # 工具
}

def get_cover_image(file_path: Path) -> str:
    """根据文件路径选择合适的封面图"""
    path_str = str(file_path)
    for key, url in COVER_MAP.items():
        if key in path_str:
            return url
    return DEFAULT_COVER

def extract_title(content: str) -> str:
    """从内容中提取标题（第一个 # 后面的内容）"""
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        # 移除可能的 emoji 和特殊字符
        title = match.group(1).strip()
        # 移除 markdown 链接格式
        title = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', title)
        return title
    return "团建游戏"

def has_frontmatter(content: str) -> bool:
    """检查是否已有 frontmatter"""
    return content.startswith('---')

def add_frontmatter(file_path: Path):
    """为文件添加 frontmatter"""
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # 如果已有 frontmatter，跳过
        if has_frontmatter(content):
            print(f"✓ 已有 frontmatter: {file_path}")
            return
        
        # 提取标题
        title = extract_title(content)
        
        # 获取封面图
        cover = get_cover_image(file_path)
        
        # 生成 source_url
        rel_path = file_path.relative_to(ROOT_DIR.parent)
        source_url = f"https://aiworkdb.github.io/{rel_path.with_suffix('.html')}"
        
        # 创建 frontmatter
        frontmatter = f"""---
title: "{title}"
author: "AIWorkDB"
cover: "{cover}"
source_url: "{source_url}"
---

"""
        
        # 写入文件
        file_path.write_text(frontmatter + content, encoding='utf-8')
        print(f"✅ 已添加 frontmatter: {file_path}")
        
    except Exception as e:
        print(f"❌ 处理失败 {file_path}: {e}")

def main():
    """主函数"""
    print("开始批量整理团建文章格式...")
    print(f"根目录: {ROOT_DIR.absolute()}")
    print("-" * 50)
    
    # 遍历所有 md 文件
    for md_file in ROOT_DIR.rglob("*.md"):
        # 跳过 ROADMAP.md
        if md_file.name == "ROADMAP.md":
            continue
        add_frontmatter(md_file)
    
    print("-" * 50)
    print("✅ 批量整理完成！")

if __name__ == "__main__":
    main()
