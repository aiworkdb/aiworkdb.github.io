#!/usr/bin/env python3
"""
为团建文章添加封面图（使用可靠的图片源）
使用 picsum.photos 提供免费、稳定的图片
"""

from pathlib import Path

ROOT_DIR = Path("teambuilding")

# 使用 picsum.photos 提供免费、稳定的图片
# 格式：https://picsum.photos/id/{id}/1200/630
COVER_MAP = {
    "icebreaker": "https://picsum.photos/id/1/1200/630",
    "collaboration": "https://picsum.photos/id/2/1200/630",
    "communication": "https://picsum.photos/id/3/1200/630",
    "trust": "https://picsum.photos/id/4/1200/630",
    "leadership": "https://picsum.photos/id/5/1200/630",
    "creativity": "https://picsum.photos/id/6/1200/630",
    "problem-solving": "https://picsum.photos/id/7/1200/630",
    "flows": "https://picsum.photos/id/8/1200/630",
    "toolbox": "https://picsum.photos/id/9/1200/630",
    "default": "https://picsum.photos/id/10/1200/630",
}

def add_cover_field(file_path: Path):
    """为文件添加 cover 字段"""
    try:
        content = file_path.read_text(encoding='utf-8')
        
        if not content.startswith('---'):
            return False
        
        parts = content.split('---', 2)
        if len(parts) < 3:
            return False
        
        frontmatter = parts[1]
        body = parts[2]
        
        # 检查是否已有 cover 字段
        if 'cover:' in frontmatter:
            return False
        
        # 选择合适的封面图
        cover = COVER_MAP["default"]
        path_str = str(file_path)
        for key, url in COVER_MAP.items():
            if key in path_str:
                cover = url
                break
        
        # 添加 cover 字段
        lines = frontmatter.strip().split('\n')
        lines.append(f'cover: "{cover}"')
        new_frontmatter = '\n'.join(lines)
        
        new_content = '---' + new_frontmatter + '\n\n---' + body
        file_path.write_text(new_content, encoding='utf-8')
        print(f"✅ 已添加 cover: {file_path}")
        return True
            
    except Exception as e:
        print(f"❌ 处理失败 {file_path}: {e}")
        return False

def main():
    print("开始为团建文章添加封面图...")
    print(f"根目录: {ROOT_DIR.absolute()}")
    print("-" * 50)
    
    added_count = 0
    
    for md_file in ROOT_DIR.rglob("*.md"):
        if md_file.name == "ROADMAP.md":
            continue
        if add_cover_field(md_file):
            added_count += 1
    
    print("-" * 50)
    print(f"✅ 添加完成！共添加 {added_count} 篇文件的封面图。")

if __name__ == "__main__":
    main()
