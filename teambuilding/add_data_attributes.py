#!/usr/bin/env python3
"""
为 teambuilding/index.html 中的所有游戏卡片添加 data-people 和 data-duration 属性
"""

import re

# 读取原文件
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 定义每个游戏的属性值
# 格式: { 'href模式': ('data-people值', 'data-duration值') }
# 注意：HTML中的路径包含 games/ 前缀
game_attributes = {
    # 破冰热场 (icebreaker)
    'games/icebreaker/food-challenge.html': ('medium', 'medium'),
    'games/icebreaker/explorer-journal.html': ('medium', 'medium'),
    'games/icebreaker/line-master.html': ('medium', 'short'),
    
    # 沟通表达 (communication)
    'games/communication/blind-polygon.html': ('medium', 'medium'),
    'games/communication/telephone-game.html': ('medium', 'short'),
    'games/communication/draw-guess.html': ('small', 'medium'),
    'games/communication/drawing-relay.html': ('small', 'medium'),
    'games/communication/animal-detective.html': ('medium', 'medium'),
    'games/communication/time-agents.html': ('medium', 'medium'),
    'games/communication/rumor-factory.html': ('medium', 'medium'),
    
    # 团队协作 (collaboration)
    'games/collaboration/human-knot.html': ('medium', 'medium'),
    'games/collaboration/eyebrow-stick.html': ('medium', 'medium'),
    'games/collaboration/ball-relay.html': ('medium', 'medium'),
    'games/collaboration/wind-fire-wheel.html': ('large', 'medium'),
    'games/collaboration/island-survival.html': ('medium', 'long'),
    'games/collaboration/magic-academy.html': ('medium', 'long'),
    'games/collaboration/space-miners.html': ('medium', 'long'),
    'games/collaboration/crazy-kitchen.html': ('medium', 'medium'),
    'games/collaboration/body-letters.html': ('medium', 'medium'),
    
    # 信任建立 (trust)
    'games/trust/trust-fall.html': ('medium', 'medium'),
    'games/trust/blind-walk.html': ('small', 'medium'),
    
    # 领导力 (leadership)
    'games/leadership/red-black-game.html': ('medium', 'long'),
    'games/leadership/tangram.html': ('large', 'long'),
    'games/leadership/silent-leader.html': ('small', 'medium'),
    
    # 创新思维 (creativity)
    'games/creativity/10-yuan-idea.html': ('medium', 'medium'),
    'games/creativity/newspaper-tower.html': ('medium', 'medium'),
    
    # 问题解决 (problem-solving)
    'games/problem-solving/desert-survival.html': ('medium', 'medium'),
    'games/problem-solving/egg-drop.html': ('medium', 'long'),
}

# 为每个游戏添加属性
updated_count = 0
for href, (people, duration) in game_attributes.items():
    # 匹配 <a href="XXX" class="card"> 但没有 data-people 属性的情况
    pattern = rf'(<a href="{href}" class="card")>'
    replacement = rf'\1 data-people="{people}" data-duration="{duration}">'
    
    if re.search(pattern, content):
        content = re.sub(pattern, replacement, content)
        updated_count += 1
        print(f"✅ 已更新: {href} (people={people}, duration={duration})")
    else:
        # 检查是否已经有属性了
        pattern_check = rf'<a href="{href}" class="card" data-people='
        if re.search(pattern_check, content):
            print(f"⏭️  跳过: {href} (已有属性)")
        else:
            print(f"❌ 未找到: {href}")

# 写回文件
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n🎉 完成！共更新 {updated_count} 个游戏卡片")
