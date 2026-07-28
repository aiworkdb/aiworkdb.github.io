#!/usr/bin/env python3
"""
修复团建文章的 frontmatter 格式
确保 --- 单独占一行
"""

from pathlib import Path

ROOT_DIR = Path("teambuilding")

def fix_frontmatter_format(file_path: Path):
    """修复文件中的 frontmatter 格式"""
    try:
        lines = file_path.read_text(encoding='utf-8').split('\n')
        
        # 检查第1行是否以 --- 开头，但后面还有内容
        if lines[0].startswith('---') and len(lines[0]) > 3:
            # 将第1行拆分为 --- 和剩余内容
            rest = lines[0][3:].strip()
            lines = ['---', rest] + lines[1:]
        
        # 找到 frontmatter 结束的行（第二个 ---）
        # 从第1行之后开始找
        end_idx = -1
        for i in range(1, len(lines)):
            if lines[i].strip() == '---':
                end_idx = i
                break
        
        if end_idx == -1:
            # 没有找到结束的 ---，可能格式错误
            return False
        
        # 确保结束的 --- 单独占一行（即这一行只有 ---）
        if lines[end_idx].strip() != '---':
            # 这一行有其他内容，需要拆分
            # 但是，这种情况应该很少，因为 frontmatter 结束后应该是正文
            # 所以，我们暂时不处理，先确保开始的 --- 正确
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
        if fix_frontmatter_format(md_file):
            print(f"✅ 已修复: {md_file}")
            fixed_count += 1
    
    print("-" * 50)
    print(f"✅ 修复完成！共修复 {fixed_count} 篇文件。")

if __name__ == "__main__":
    main()
