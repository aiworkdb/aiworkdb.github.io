# -*- coding: utf-8 -*-
import io, os, re, sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
TB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for fn in sorted(os.listdir(os.path.join(TB, 'games', 'boardgame'))):
    if not fn.endswith('.md'):
        continue
    t = io.open(os.path.join(TB, 'games', 'boardgame', fn), encoding='utf-8', newline='').read()
    print('===', fn, 'len', len(t), 'crlf', '\r\n' in t)
    for ln in t.split('\n'):
        ln = ln.rstrip('\r')
        if ln.startswith('|') and ('时长' in ln or '人数' in ln or '场地' in ln):
            print('   ', ln.strip())
    print('   has 落点节:', '## 🧩' in t, '| has 教练笔记:', '## 📝 教练笔记' in t)
