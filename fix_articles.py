#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复团建文章的 frontmatter 格式
解决 YAML 解析错误（URL 中的 ? 和 = 导致的问题）
"""

import os
import re

def fix_article(article_path):
    """
    修复单篇文章
    
    Args:
        article_path: 文章路径
    
    Returns:
        (success, message): 是否成功，消息
    """
    if not os.path.exists(article_path):
        return False, f"文件不存在"
    
    try:
        # 读取文章
        with open(article_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否有 frontmatter
        if not content.startswith('---'):
            return False, "无 frontmatter"
        
        # 找到 frontmatter 结束位置
        end_match = re.search(r'\n---\s*\n', content)
        if not end_match:
            return False, "frontmatter 格式错误"
        
        frontmatter_end = end_match.start()
        frontmatter = content[:frontmatter_end]
        body = content[end_match.end():]
        
        # 修复 cover 行
        # 方案：移除 cover 行，使用本地图片路径
        lines = frontmatter.split('\n')
        new_lines = []
        has_cover = False
        
        for line in lines:
            # 跳过有问题的 cover 行
            if line.startswith('cover:'):
                # 不复制这行，后面会添加正确的
                has_cover = True
                continue
            new_lines.append(line)
        
        # 在 source_url 后添加正确的 cover 行
        if has_cover or True:  # 总是添加 cover
            new_frontmatter = '\n'.join(new_lines)
            # 在 source_url 行后插入 cover
            if 'source_url:' in new_frontmatter:
                new_frontmatter = new_frontmatter.replace(
                    '\nsource_url:',
                    '\ncover: "images/cover.png"\nsource_url:'
                )
            else:
                # 如果没有 source_url，在 --- 后添加
                new_frontmatter = new_frontmatter.replace(
                    '---',
                    '---\ncover: "images/cover.png"',
                    1
                )
        else:
            new_frontmatter = '\n'.join(new_lines)
        
        # 组合新内容
        new_content = new_frontmatter + '\n---\n' + body
        
        # 保存
        with open(article_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True, "修复成功"
        
    except Exception as e:
        return False, str(e)

def main():
    """主函数"""
    print("="*60)
    print("修复团建文章格式")
    print("="*60)
    
    # 核心文章列表
    articles = [
        'teambuilding/README.md',
        'teambuilding/guide.md',
        'teambuilding/flows/one-day/01-schedule.md',
        'teambuilding/flows/half-day/01-schedule.md',
        'teambuilding/flows/online/01-schedule.md'
    ]
    
    # 统计
    success_count = 0
    failed_articles = []
    
    # 逐篇修复
    for i, article in enumerate(articles, 1):
        print(f"\n[{i}/{len(articles)}] 修复: {article}")
        
        success, message = fix_article(article)
        
        if success:
            print(f"✅ 修复成功!")
            success_count += 1
        else:
            print(f"❌ 修复失败: {message}")
            failed_articles.append({
                "file": article,
                "error": message
            })
    
    # 输出总结
    print(f"\n{'='*60}")
    print("修复完成!")
    print(f"{'='*60}")
    print(f"\n📊 统计:")
    print(f"   成功: {success_count} 篇")
    print(f"   失败: {len(failed_articles)} 篇")
    
    if failed_articles:
        print(f"\n❌ 失败文章列表:")
        for item in failed_articles:
            print(f"   - {item['file']}")
            print(f"     错误: {item['error']}")
    
    print(f"\n💡 下一步:")
    print(f"   1. 运行 create_cover.py 创建本地封面图")
    print(f"   2. 检查修复后的文章格式")
    print(f"   3. 重新运行发布脚本")

if __name__ == "__main__":
    main()
