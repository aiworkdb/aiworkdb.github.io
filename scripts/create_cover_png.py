#!/usr/bin/env python3
"""创建简单的 PNG 封面图（纯 Python，无需 Pillow）"""
import struct, zlib, os

def create_png(filename, width=1200, height=400):
    """创建渐变 PNG 图片"""
    
    def make_chunk(chunk_type, data):
        chunk = chunk_type + data
        crc = struct.pack('>I', zlib.crc32(chunk) & 0xffffffff)
        return struct.pack('>I', len(data)) + chunk + crc
    
    # PNG 签名
    signature = b'\x89PNG\r\n\x1a\n'
    
    # IHDR
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    ihdr = make_chunk(b'IHDR', ihdr_data)
    
    # IDAT - 图像数据
    raw_data = b''
    for y in range(height):
        raw_data += b'\x00'  # 过滤器：无
        for x in range(width):
            # 渐变色：从 #2D3436 到 #4ECDC4
            r = int(45 + (78 - 45) * x / width)
            g = int(52 + (205 - 52) * x / width)
            b = int(54 + (196 - 54) * x / width)
            raw_data += bytes([r, g, b])
    
    compressed = zlib.compress(raw_data, 9)
    idat = make_chunk(b'IDAT', compressed)
    
    # IEND
    iend = make_chunk(b'IEND', b'')
    
    # 写入文件
    with open(filename, 'wb') as f:
        f.write(signature + ihdr + idat + iend)
    
    print(f'✅ 已创建: {filename} ({os.path.getsize(filename)} bytes)')

# 创建图片
os.makedirs('teambuilding/images', exist_ok=True)
create_png('teambuilding/images/cover.png')
print('\n✅ 本地封面图创建完成！')
