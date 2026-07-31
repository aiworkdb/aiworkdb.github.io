#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建本地 PNG 封面图
使用纯 Python 标准库（无需安装 Pillow）
"""

import struct
import zlib
import os

def create_png(filename, width=1200, height=630, color1=(45, 52, 54), color2=(78, 205, 196)):
    """
    创建简单的渐变 PNG 图片
    
    Args:
        filename: 保存路径
        width: 宽度
        height: 高度
        color1: 起始颜色 (R, G, B)
        color2: 结束颜色 (R, G, B)
    """
    
    def make_chunk(chunk_type, data):
        """创建 PNG chunk"""
        chunk = chunk_type + data
        crc = struct.pack('>I', zlib.crc32(chunk) & 0xffffffff)
        return struct.pack('>I', len(data)) + chunk + crc
    
    # PNG 签名
    signature = b'\x89PNG\r\n\x1a\n'
    
    # IHDR chunk
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    ihdr = make_chunk(b'IHDR', ihdr_data)
    
    # IDAT chunk - 创建渐变背景
    raw_data = b''
    for y in range(height):
        raw_data += b'\x00'  # 过滤器字节
        for x in range(width):
            # 水平渐变：从 color1 到 color2
            r = int(color1[0] + (color2[0] - color1[0]) * x / width)
            g = int(color1[1] + (color2[1] - color1[1]) * x / width)
            b = int(color1[2] + (color2[2] - color1[2]) * x / width)
            raw_data += bytes([r, g, b])
    
    compressed = zlib.compress(raw_data, 9)
    idat = make_chunk(b'IDAT', compressed)
    
    # IEND chunk
    iend = make_chunk(b'IEND', b'')
    
    # 保存文件
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'wb') as f:
        f.write(signature + ihdr + idat + iend)
    
    file_size = os.path.getsize(filename)
    print(f'✅ 已创建: {filename} ({file_size/1024:.1f} KB)')

def main():
    """主函数"""
    print("="*60)
    print("创建本地封面图")
    print("="*60)
    
    # 创建不同颜色的封面图
    covers = [
        ('teambuilding/images/cover.png', (45, 52, 54), (78, 205, 196)),  # 团建 - 深灰到青绿
        ('teambuilding/images/cover-guide.png', (78, 205, 196), (45, 52, 54)),  # 指南 - 青绿到深灰
        ('teambuilding/images/cover-flow.png', (108, 92, 231), (0, 184, 148)),  # 流程 - 紫色到绿色
    ]
    
    for filename, color1, color2 in covers:
        create_png(filename, color1=color1, color2=color2)
    
    print("\n✅ 所有封面图创建完成！")
    print("\n提示：现在可以运行 fix_articles.py 修复文章格式")

if __name__ == "__main__":
    main()
