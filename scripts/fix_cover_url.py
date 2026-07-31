#!/usr/bin/env python3
"""
修复团建文章封面图链接 - 修正拼写错误的域名
picsum.photos -> picsum.photos
"""

from pathlib import Path

ROOT_DIR = Path("teambuilding")

def fix_cover_url(file_path: Path):
    """修复文件中的 cover URL 拼写错误"""
    try:
        content = file_path.read_text(encoding='utf-8')
        
        if 'picsum.photos' in content:
            content = content.replace('picsum.photos', 'picsum.photos')
            file_path.write_text(content, encoding='utf-8')
            print(f"✅ 已修复: {file_path}")
            return True
        
        return False
            
    except Exception as e:
        print(f"❌ 处理失败 {file_path}: {e}")
        return False

def main():
    print("开始修复封面图链接...")
    print(f"根目录: {ROOT_DIR.absolute()}")
    print("-" * 50)
    
    fixed_count = 0
    
    for md_file in ROOT_DIR.rglob("*.md"):
        if md_file.name == "ROADMAP.md":
            continue
        if fix_cover_url(md_file):
            fixed_count += 1
    
    print("-" * 50)
    print(f"✅ 修复完成！共修复 {fixed_count} 篇文件。")
    print("\n正确的域名：https://picsum.photos")
    print("示例：https://picsum.photos/id/10/1200/630")

if __name__ == "__main__":
    main()
