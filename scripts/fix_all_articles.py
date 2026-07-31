#!/usr/bin/env python3
"""
批量修复团建文章的所有问题：
1. 移除 cover 字段（避免图片下载失败）
2. 修复 blockquote 语法（添加正确的换行）
"""

import re
from pathlib import Path

ROOT_DIR = Path("teambuilding")

def fix_article(file_path: Path):
    """修复单篇文章"""
    try:
        content = file_path.read_text(encoding='utf-8')
        original = content
        
        # 1. 移除 cover 字段
        lines = content.split('\n')
        new_lines = []
        in_frontmatter = False
        frontmatter_end = 0
        
        for i, line in enumerate(lines):
            if line.strip() == '---':
                if not in_frontmatter:
                    in_frontmatter = True
                else:
                    frontmatter_end = i
                    break
        
        if frontmatter_end > 0:
            # 重建 frontmatter（移除 cover）
            fm_lines = lines[1:frontmatter_end]
            fm_lines = [l for l in fm_lines if not l.strip().startswith('cover:')]
            new_content = '---\n' + '\n'.join(fm_lines) + '\n---\n' + '\n'.join(lines[frontmatter_end+1:])
            content = new_content
        
        # 2. 修复 blockquote（确保 > 后面有空格，且前后有空行）
        # 在 frontmatter 结束后处理
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                fm = parts[1]
                body = parts[2]
                
                # 修复 body 中的 blockquote
                # 确保 blockquote 前后有空行
                body = re.sub(r'\n(?!\\s*\\n)>', r'\n\n>', body)
                body = re.sub(r'>([^\\n]*)\n(?!\\s*\\n)', r'>\\1\n\n', body)
                
                content = '---' + fm + '---' + body
        
        # 3. 写回文件
        if content != original:
            file_path.write_text(content, encoding='utf-8')
            return True
        
        return False
            
    except Exception as e:
        print(f"❌ 处理失败 {file_path}: {e}")
        return False

def main():
    """主函数"""
    print("开始批量修复团建文章...")
    print(f"根目录: {ROOT_DIR.absolute()}")
    print("-" * 50)
    
    fixed_count = 0
    
    # 遍历所有 md 文件
    for md_file in ROOT_DIR.rglob("*.md"):
        if md_file.name == "ROADMAP.md":
            continue
        if fix_article(md_file):
            print(f"✅ 已修复: {md_file}")
            fixed_count += 1
    
    print("-" * 50)
    print(f"✅ 修复完成！共修复 {fixed_count} 篇文件。")

if __name__ == "__main__":
    main()
