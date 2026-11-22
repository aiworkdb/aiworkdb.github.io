# -*- coding: utf-8 -*-
"""核对 name-chain.md 的恢复结果：与 git HEAD 比对（归一化 CRLF），并转成 CRLF。"""
import io
import os
import re
import subprocess
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

TB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(TB)
p = os.path.join(TB, 'games', 'icebreaker', 'name-chain.md')

raw = io.open(p, encoding='utf-8', newline='').read()
norm = raw.replace('\r\n', '\n')
head = subprocess.run(['C:\\Program Files\\Git\\cmd\\git.exe', 'show',
                       'HEAD:teambuilding/games/icebreaker/name-chain.md'],
                      cwd=REPO, capture_output=True).stdout.decode('utf-8').replace('\r\n', '\n')

SEC = '## 🧩 这套游戏被哪些流程用过'
mine = norm.index(SEC)
body_wo = norm[:mine].rstrip('\n') + '\n'
head_s = head.rstrip('\n') + '\n'
print('恢复后（去掉新节）字符数：%d ｜ HEAD：%d' % (len(body_wo), len(head_s)))
print('与 HEAD 完全一致：', body_wo == head_s)

if body_wo != head_s:
    import difflib
    d = list(difflib.unified_diff(head_s.split('\n'), body_wo.split('\n'),
                                  'HEAD', 'restored', lineterm='', n=1))
    print('差异行数：%d' % len(d))
    for ln in d[:40]:
        print('   ', ln)

# 统一 CRLF
fixed = re.sub(r'(?<!\r)\n', '\r\n', norm)
io.open(p, 'w', encoding='utf-8', newline='').write(fixed)
print('已写回 CRLF，%d 字符' % len(fixed))
