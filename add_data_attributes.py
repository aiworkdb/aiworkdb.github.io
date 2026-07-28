#!/usr/bin/env python3
"""
为 teambuilding/index.html 中的游戏卡片添加数据属性
数据属性包括：data-category, data-people, data-duration
"""

import re

def add_data_attributes(html_file):
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 定义游戏的分类映射（从grid的ID提取）
    category_map = {
        'grid-icebreaker': 'icebreaker',
        'grid-communication': 'communication',
        'grid-collaboration': 'collaboration',
        'grid-trust': 'trust',
        'grid-leadership': 'leadership',
        'grid-creativity': 'creativity'
    }
    
    # 为每个grid中的卡片添加数据属性
    for grid_id, category in category_map.items():
        # 找到grid的开始和结束位置
        grid_pattern = rf'(<div class="grid" id="{grid_id}">)(.*?)(</div>\s*<!--|</div>\s*<div style=|</div>\s*</div>\s*<div class="section">)'
        match = re.search(grid_pattern, content, re.DOTALL)
        
        if match:
            grid_start = match.start()
            grid_end = match.end()
            grid_content = match.group(0)
            
            # 在grid内容中为每个card添加数据属性
            # 这里需要根据每个游戏的标签来推断people和duration
            # 由于这很复杂，我将采用更简单的方法：直接修改HTML文件
            
            print(f"Found grid: {grid_id}")
    
    # 由于正则表达式方法太复杂，我将采用更简单的方法：
    # 直接在每个<a href="games/..." class="card">标签中添加数据属性
    
    # 读取原始的HTML文件并手动添加数据属性
    print("This script needs to be run manually to add data attributes to each game card")
    print("Alternatively, we can modify the HTML file directly with specific data for each game")

if __name__ == '__main__':
    add_data_attributes('teambuilding/index.html')
