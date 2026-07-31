#!/usr/bin/env python3
"""
修复团建文章中的错误行：删除 >\1 这样的错误行
"""

from pathlib import Path

ROOT_DIR = Path("teambuilding")

def fix_file(file_path: Path):
    """修复单个文件：删除包含 >\1 的行"""
    try:
        lines = file_path.read_text(encoding='utf-8').split('\n')
        new_lines = []
        modified = False
        
        for line in lines:
            # 删除包含 >\1 的行（可能是错误的 blockquote）
            if '>\\1' in line or '>\1' in line:
                print(f"  删除错误行: {line[:50]}")
                modified = True
                continue
            new_lines.append(line)
        
        if modified:
            file_path.write_text('\n'.join(new_lines), encoding='utf-8')
            return True
        return False
    except Exception as e:
        print(f"❌ 处理失败 {file_path}: {e}")
        return False

def main():
    print("开始修复团建文章中的错误行...")
    print("-" * 50)
    
    fixed_count = 0
    for md_file in ROOT_DIR.rglob("*.md"):
        if md_file.name == "ROADMAP.md":
            continue
        if fix_file(md_file):
            print(f"✅ 已修复: {md_file}")
            fixed_count += 1
    
    print("-" * 50)
    print(f"✅ 修复完成！共修复 {fixed_count} 篇文件。")

if __name__ == "__main__":
    main()
