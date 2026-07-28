#!/usr/bin/env python3
"""
修复团建文章中的相对路径链接，转换为完整的 URL
基础 URL：https://aiworkdb.github.io/teambuilding/
"""

import re
from pathlib import Path, PurePosixPath

BASE_URL = "https://aiworkdb.github.io/teambuilding/"

def fix_relative_links(content: str, file_path: Path) -> str:
    """将内容中的相对路径链接转换为完整的 URL"""
    
    # 计算当前文件相对于 teambuilding 根目录的路径
    rel_path = file_path.relative_to(Path("teambuilding").parent / "teambuilding")
    # 获取当前文件所在的目录（相对于根目录）
    rel_dir = rel_path.parent
    
    # 正则表达式匹配 Markdown 链接：[text](url)
    # 排除已经以 http 或 https 开头的 URL
    pattern = r'\[([^\]]*)\]\((?!http)([^)]+)\)'
    
    def replace_link(match):
        text = match.group(1)
        url = match.group(2)
        
        # 如果 URL 已经是完整的（以 # 开头，可能是锚点），则不修改
        if url.startswith('#'):
            return match.group(0)
        
        # 处理相对路径
        if not url.startswith(('http://', 'https://', 'mailto:', 'tel:')):
            # 将相对路径转换为完整的 URL
            # 首先，将 Windows 路径分隔符替换为 /
            url = url.replace('\\', '/')
            
            # 构建完整路径
            if url.startswith('./'):
                url = url[2:]
            
            # 计算基于当前文件目录的完整路径
            if rel_dir != Path('.'):
                full_path = PurePosixPath(rel_dir) / url
            else:
                full_path = PurePosixPath(url)
            
            # 规范化路径（处理 ../）
            parts = []
            for part in full_path.parts:
                if part == '..':
                    if parts:
                        parts.pop()
                elif part != '.':
                    parts.append(part)
            
            normalized_path = '/'.join(parts)
            
            # 构建完整 URL
            complete_url = BASE_URL + normalized_path
            
            # 如果是 .md 文件，转换为 .html（因为 GitHub Pages 会生成 HTML）
            if complete_url.endswith('.md'):
                complete_url = complete_url[:-3] + '.html'
            
            return f'[{text}]({complete_url})'
        
        return match.group(0)
    
    # 应用替换
    fixed_content = re.sub(pattern, replace_link, content)
    
    return fixed_content

def process_file(file_path: Path):
    """处理单个文件"""
    try:
        content = file_path.read_text(encoding='utf-8')
        fixed_content = fix_relative_links(content, file_path)
        
        if fixed_content != content:
            file_path.write_text(fixed_content, encoding='utf-8')
            print(f"✅ 已修复: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"❌ 处理失败 {file_path}: {e}")
        return False

def main():
    print("开始修复团建文章中的相对路径链接...")
    print(f"基础 URL: {BASE_URL}")
    print("-" * 50)
    
    root_dir = Path("teambuilding")
    fixed_count = 0
    
    for md_file in root_dir.rglob("*.md"):
        if md_file.name == "ROADMAP.md":
            continue
        if process_file(md_file):
            fixed_count += 1
    
    print("-" * 50)
    print(f"✅ 修复完成！共修复 {fixed_count} 篇文件。")
    print("\n📝 说明：")
    print("  - 已将相对路径链接转换为完整的 URL")
    print("  - 基础 URL: https://aiworkdb.github.io/teambuilding/")
    print("  - .md 链接已转换为 .html（适配 GitHub Pages）")

if __name__ == "__main__":
    main()
