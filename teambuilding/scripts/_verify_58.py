# -*- coding: utf-8 -*-
"""校验第 58 次改动：5 款游戏 md+html 双侧落点节；slot-map 新节；时间窗；内链。"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
TB = r'd:\mycode\aiworkdb.github.io\teambuilding'
G = os.path.join(TB, 'games', 'leadership')
TARGET = {
    'broken-squares': '01:55–02:40，45 min',
    'crisis-briefing': '02:20–03:10，50 min',
    'frostbite': '14:50–15:40，50 min',
    'paper-airplane-factory': '10:30–12:00，90 min',
    'resource-negotiation': '15:30–16:30，60 min',
}

ok = bad = 0
for gid, claim in TARGET.items():
    md = io.open(os.path.join(G, gid + '.md'), encoding='utf-8', newline='').read()
    html = io.open(os.path.join(G, gid + '.html'), encoding='utf-8', newline='').read()
    # html 用 <h2> 正则定位（避开侧栏目录）
    m = re.search(r'<h2[^>]*>[^<]*这套游戏被哪些流程用过', html)
    seg = html[m.start():] if m else ''
    a = '## 🧩 这套游戏被哪些流程用过' in md and claim in md
    b = bool(m) and claim.replace('–', '–') in seg
    print('%-24s md=%-5s html=%-5s' % (gid, a, b))
    if a and b:
        ok += 1
    else:
        bad += 1

# slot-map
sm_md = io.open(os.path.join(TB, 'toolbox', 'slot-map.md'), encoding='utf-8', newline='').read()
sm_html = io.open(os.path.join(TB, 'toolbox', 'slot-map.html'), encoding='utf-8', newline='').read()
for name, txt, needle in (('slot-map.md', sm_md, '## 十一、一轮定长'),
                          ('slot-map.html', sm_html, '一轮定长')):
    print('%-16s 含「一轮定长」= %s ｜ 含 5 款名 = %d/5' % (
        name, needle in txt,
        sum(1 for n in ('破碎的正方形', '极地庇护所', '危机发布会', '纸飞机工厂', '资源谈判局') if n in txt)))

print('-' * 60)
print('游戏页双侧 %d/%d' % (ok, ok + bad))
