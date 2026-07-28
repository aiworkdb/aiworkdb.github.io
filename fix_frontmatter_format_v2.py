#!/usr/bin/env python3
"""
修复团建文章的 frontmatter 格式
确保 --- 单独占一行，并且字段格式正确
"""

import re
from pathlib import Path

ROOT_DIR = Path("teambuilding")

def fix_frontmatter(file_path: Path):
    """修复单个文件的 frontmatter 格式"""
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # 使用正则表达式匹配 frontmatter
        # 匹配从第一个 --- 到第二个 --- 之间的内容
        pattern = r'^(---\s*\n)(.*?)(\n\s*---\s*\n)'  
        match = re.search(pattern, content, re.DOTALL)
        
        if not match:
            print(f"⚠️ 未找到 frontmatter: {file_path.name}")
            return False
        
        # 提取字段
        fm_content = match.group(2)
        
        # 解析字段
        fields = {}
        for line in fm_content.split('\n'):
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                fields[key.strip()] = value.strip()
        
        # 重新构建 frontmatter
        new_fm = '---\n'
        for key in ['title', 'author', 'source_url', 'cover']:
            if key in fields:
                new_fm += f'{key}: {fields[key]}\n'
        new_fm += '---\n'
        
        # 替换原来的 frontmatter
        new_content = content[:match.start()] + new_fm + content[match.end():]
        
        # 写回文件
        file_path.write_text(new_content, encoding='utf-8')
        print(f"✅ 已修复: {file_path.name}")
        return True
            
    except Exception as e:
        print(f"❌ 处理失败 {file_path}: {e}")
        return False

def main():
    print("开始修复团建文章的 frontmatter 格式...")
    print(f"根目录: {ROOT_DIR.absolute()}")
    print("-" * 50)
    
    fixed_count = 0
    
    for md_file in ROOT_DIR.rglob("*.md"):
        if md_file.name == "ROADMAP.md":
            continue
        if fix_frontmatter(md_file):
            fixed_count += 1
    
    print("-" * 50)
    print(f"✅ 修复完成！共修复 {fixed_count} 篇文件。")
    print("\n📝 说明：")
    print("  - 已确保 --- 单独占一行")
    print("  - 已按标准格式重新组织字段")

if __name__ == "__main__":
    main()
