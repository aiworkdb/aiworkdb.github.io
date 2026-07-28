#!/usr/bin/env python3
"""
修复团建文章 frontmatter 中的 source_url 路径分隔符问题
将 Windows 反斜杠替换为正斜杠
"""

import re
from pathlib import Path

ROOT_DIR = Path("teambuilding")

def fix_frontmatter(file_path: Path):
    """修复文件中的 frontmatter"""
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # 检查是否有 frontmatter
        if not content.startswith('---'):
            return False
        
        # 找到 frontmatter 结束位置
        parts = content.split('---', 2)
        if len(parts) < 3:
            return False
        
        frontmatter = parts[1]
        body = parts[2]
        
        # 修复 source_url 中的反斜杠
        fixed_frontmatter = frontmatter.replace('\\', '/')
        
        # 如果有修改，写回文件
        if fixed_frontmatter != frontmatter:
            new_content = '---' + fixed_frontmatter + '---' + body
            file_path.write_text(new_content, encoding='utf-8')
            print(f"✅ 已修复: {file_path}")
            return True
        else:
            # print(f"○ 无需修复: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ 处理失败 {file_path}: {e}")
        return False

def main():
    print("开始修复团建文章 frontmatter...")
    print(f"根目录: {ROOT_DIR.absolute()}")
    print("-" * 50)
    
    fixed_count = 0
    
    # 遍历所有 md 文件
    for md_file in ROOT_DIR.rglob("*.md"):
        if md_file.name == "ROADMAP.md":
            continue
        if fix_frontmatter(md_file):
            fixed_count += 1
    
    print("-" * 50)
    print(f"✅ 修复完成！共修复 {fixed_count} 篇文件。")

if __name__ == "__main__":
    main()
