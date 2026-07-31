#!/usr/bin/env python3
"""
移除团建文章 frontmatter 中的 cover 字段
解决 wenyan-mcp 下载图片失败的问题
"""

import re
from pathlib import Path

ROOT_DIR = Path("teambuilding")

def remove_cover_field(file_path: Path):
    """移除文件 frontmatter 中的 cover 字段"""
    try:
        content = file_path.read_text(encoding='utf-8')
        
        if not content.startswith('---'):
            return False
        
        parts = content.split('---', 2)
        if len(parts) < 3:
            return False
        
        frontmatter = parts[1]
        body = parts[2]
        
        # 移除 cover 行
        lines = frontmatter.strip().split('\n')
        new_lines = [line for line in lines if not line.strip().startswith('cover:')]
        
        if len(new_lines) < len(lines):
            new_frontmatter = '\n'.join(new_lines)
            new_content = '---' + new_frontmatter + '\n\n---' + body
            file_path.write_text(new_content, encoding='utf-8')
            print(f"✅ 已移除 cover: {file_path}")
            return True
        
        return False
            
    except Exception as e:
        print(f"❌ 处理失败 {file_path}: {e}")
        return False

def main():
    """主函数"""
    # 需要修复的文件列表
    failed_files = [
        "teambuilding/games/icebreaker/human-bingo.md",
        "teambuilding/games/icebreaker/two-truths-one-lie.md",
        "teambuilding/games/communication/blind-polygon.md",
        "teambuilding/games/trust/trust-fall.md",
    ]
    
    print("开始修复封面图问题...")
    print("-" * 50)
    
    for file_path in failed_files:
        path = Path(file_path)
        if path.exists():
            remove_cover_field(path)
        else:
            print(f"⚠️ 文件不存在: {file_path}")
    
    print("-" * 50)
    print("✅ 修复完成！")

if __name__ == "__main__":
    main()
