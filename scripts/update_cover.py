#!/usr/bin/env python3
"""
为团建文章添加可靠的封面图链接
使用 placeholder.co 提供免费、稳定的图片服务
"""

from pathlib import Path

ROOT_DIR = Path("teambuilding")

# 使用可靠的图片服务
# 方案 1: placeholder.co (稳定可靠)
# 格式：https://placehold.co/1200x630/3D8BFA/white?text=Title

COVER_MAP = {
    "icebreaker": "https://placehold.co/1200x630/FF6B6B/white?text=Ice+Breaker",
    "collaboration": "https://placehold.co/1200x630/4ECDC4/white?text=Collaboration",
    "communication": "https://placehold.co/1200x630/45B7D1/white?text=Communication",
    "trust": "https://placehold.co/1200x630/96CEB4/white?text=Trust+Building",
    "leadership": "https://placehold.co/1200x630/F7DC6F/black?text=Leadership",
    "creativity": "https://placehold.co/1200x630/B8B42D/white?text=Creativity",
    "problem-solving": "https://placehold.co/1200x630/E8A87C/white?text=Problem+Solving",
    "flows": "https://placehold.co/1200x630/6C5CE7/white?text=Flow",
    "toolbox": "https://placehold.co/1200x630/00B894/white?text=Tools",
    "default": "https://placehold.co/1200x630/2D3436/white?text=Teambuilding",
}

def update_cover_field(file_path: Path):
    """更新文件中的 cover 字段"""
    try:
        content = file_path.read_text(encoding='utf-8')
        
        if not content.startswith('---'):
            return False
        
        parts = content.split('---', 2)
        if len(parts) < 3:
            return False
        
        frontmatter = parts[1]
        body = parts[2]
        
        # 选择合适的封面图
        cover = COVER_MAP["default"]
        path_str = str(file_path)
        for key, url in COVER_MAP.items():
            if key in path_str:
                cover = url
                break
        
        # 更新或添加 cover 字段
        lines = frontmatter.strip().split('\n')
        new_lines = []
        cover_updated = False
        
        for line in lines:
            if line.strip().startswith('cover:'):
                new_lines.append(f'cover: "{cover}"')
                cover_updated = True
            else:
                new_lines.append(line)
        
        if not cover_updated:
            new_lines.append(f'cover: "{cover}"')
        
        new_frontmatter = '\n'.join(new_lines)
        new_content = '---' + new_frontmatter + '\n\n---' + body
        
        file_path.write_text(new_content, encoding='utf-8')
        print(f"✅ 已更新 cover: {file_path.name}")
        return True
            
    except Exception as e:
        print(f"❌ 处理失败 {file_path}: {e}")
        return False

def main():
    """主函数"""
    print("开始更新团建文章封面图链接...")
    print(f"使用图片服务：https://placehold.co")
    print("-" * 50)
    
    updated_count = 0
    
    for md_file in ROOT_DIR.rglob("*.md"):
        if md_file.name == "ROADMAP.md":
            continue
        if update_cover_field(md_file):
            updated_count += 1
    
    print("-" * 50)
    print(f"✅ 更新完成！共更新 {updated_count} 篇文件。")
    print("\n📝 说明：")
    print("  - 使用 placehold.co 提供稳定可靠的图片服务")
    print("  - 图片尺寸：1200x630 (微信公众号推荐尺寸)")
    print("  - 可根据需要替换为实际图片 URL")

if __name__ == "__main__":
    main()
