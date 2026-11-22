# -*- coding: utf-8 -*-
"""把新写的流程 md 转成 CRLF（flows/ 下其余 18 套全是 CRLF，混排会让 diff 花掉）。"""
import io
import os
import re
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

TB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
targets = [os.path.join(TB, 'flows', 'annual-party', '01-party.md')]
for p in targets:
    raw = io.open(p, encoding='utf-8', newline='').read()
    had = '\r\n' in raw
    fixed = re.sub(r'(?<!\r)\n', '\r\n', raw)
    fixed = fixed.replace('\r\r\n', '\r\n')
    io.open(p, 'w', encoding='utf-8', newline='').write(fixed)
    print('%s：%s → CRLF，%d 字符' % (os.path.basename(p), 'CRLF' if had else 'LF', len(fixed)))

# 全站裸 LF 体检（只报不看）
bad = []
for base in ('flows', 'games', 'toolbox'):
    for dirp, _d, fs in os.walk(os.path.join(TB, base)):
        for fn in fs:
            if fn.endswith('.md'):
                p = os.path.join(dirp, fn)
                r = io.open(p, encoding='utf-8', newline='').read()
                n = len(re.findall(r'(?<!\r)\n', r))
                if n:
                    bad.append((os.path.relpath(p, TB), n))
print('裸 LF 文件数：%d' % len(bad))
for b in bad[:10]:
    print('  ', b)
