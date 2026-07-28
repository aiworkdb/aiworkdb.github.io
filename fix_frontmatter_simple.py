#!/usr/bin/env python3
"""
修复团建文章的 frontmatter 格式
将 --- 和字段内容在同一行的情况修复为正确的格式
"""

from pathlib import Path

ROOT_DIR = Path("teambuilding")

def fix_frontmatter_simple(file_path: Path):
    """简单修复：确保开始的 --- 单独占一行"""
    try:
        lines = file_path.read_text(encoding='utf-8').split('\n')
        
        # 检查第1行
        if lines[0].startswith('---') and len(lines[0]) > 3:
            # 将第1行拆分为 --- 和剩余内容
            rest = lines[0][3:].strip()
            lines = ['---', rest] + lines[1:]
        
        # 找到 frontmatter 结束的行（第二个 ---）
        end_idx = -1
        for i in range(1, len(lines)):
            if lines[i].strip() == '---':
                end_idx = i
                break
        
        if end_idx == -1:
            return False
        
        # 确保结束的 --- 单独占一行（即这一行只有 ---）
        # 如果这一行有其他内容，则拆分（但这种情况应该很少）
        if lines[end_idx].strip() != '---':
            # 这一行有内容，需要拆分
            # 但是，这种情况可能意味着 frontmatter 格式完全错误
            # 暂时不处理，先确保开始的 --- 正确
            pass
        
        # 写回文件
        file_path.write_text('\n'.join(lines), encoding='utf-8')
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
        if fix_frontmatter_simple(md_file):
            print(f"✅ 已修复: {md_file}")
            fixed_count += 1
    
    print("-" * 50)
    print(f"✅ 修复完成！共修复 {fixed_count} 篇文件。")
    print("\n📝 说明：")
    print("  - 已确保开始的 --- 单独占一行")
    print("  - 如果仍然发布失败，可能需要手动检查格式")

if __name__ == "__main__":
    main()
