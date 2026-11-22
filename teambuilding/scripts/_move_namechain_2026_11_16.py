# -*- coding: utf-8 -*-
"""把 name-chain 的落点节从「物资清单之前」挪到文末（与其他游戏页一致）。"""
import io
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

TB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(TB, 'games', 'icebreaker', 'name-chain.md')
raw = io.open(P, encoding='utf-8', newline='').read()
EOL = '\r\n' if '\r\n' in raw else '\n'

HEAD = '## 🧩 这套游戏被哪些流程用过'
assert raw.count(HEAD) == 1
i = raw.index(HEAD)
j = raw.index('## 3. 物资清单', i)
seg = raw[i:j]
rest = raw[j:]
# 去掉段尾多余空行后重拼
new = rest.rstrip('\r\n') + EOL + EOL + seg.rstrip('\r\n') + EOL
assert new.count(HEAD) == 1
assert new.index('## 3. 物资清单') < new.index(HEAD)
rows = len([ln for ln in new.split(EOL) if ln.startswith('| [') and '(../../flows/' in ln])
assert rows == 1, rows
io.open(P, 'w', encoding='utf-8', newline='').write(new)
print('name-chain：落点节已移到文末（%d 字符）' % len(new))
