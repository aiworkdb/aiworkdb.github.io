# -*- coding: utf-8 -*-
"""本轮回归：md 站内链接坏链 / 首页流程卡数量 / 新流程页渲染 / slot-map 新节。"""
import io
import os
import re
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

TB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINK = re.compile(r'\[[^\]]*\]\(([^)]+)\)')


def read(p):
    return io.open(p, encoding='utf-8', newline='').read()


# ---------------------------------------------------------------- 1. md 链接
total = bad = 0
bads = []
for base in ('flows', 'games', 'toolbox'):
    for dirp, _d, fs in os.walk(os.path.join(TB, base)):
        for fn in fs:
            if not fn.endswith('.md'):
                continue
            p = os.path.join(dirp, fn)
            for m in LINK.finditer(read(p)):
                u = m.group(1).strip()
                if u.startswith(('http://', 'https://', 'mailto:', '#')):
                    continue
                total += 1
                path = u.split('#')[0]
                if not path:
                    continue
                if path.startswith('/'):
                    tgt = os.path.join(TB, path.lstrip('/'))
                else:
                    tgt = os.path.normpath(os.path.join(dirp, path))
                if not os.path.exists(tgt):
                    bad += 1
                    bads.append('%s -> %s' % (os.path.relpath(p, TB), u))
# README / ROADMAP / guide
for fn in ('README.md', 'ROADMAP.md', 'guide.md'):
    p = os.path.join(TB, fn)
    if not os.path.exists(p):
        continue
    for m in LINK.finditer(read(p)):
        u = m.group(1).strip()
        if u.startswith(('http', 'mailto:', '#')) or '(' in u:
            continue
        total += 1
        path = u.split('#')[0]
        if not path:
            continue
        tgt = os.path.normpath(os.path.join(TB, path))
        if not os.path.exists(tgt) and not os.path.exists(tgt.rstrip('/')):
            bad += 1
            bads.append('%s -> %s' % (fn, u))
print('[链接] md 站内链接 %d 条，坏链 %d' % (total, bad))
for b in bads[:15]:
    print('   ❌', b)

# ---------------------------------------------------------------- 2. 首页流程卡
idx = read(os.path.join(TB, 'index.html'))
cards = re.findall(r'<a class="flow" href="(flows/[^"]+)"', idx)
print('[首页] 流程卡 %d 张' % len(cards))
assert len(cards) == 19, '流程卡应为 19 张'
assert any('annual-party' in c for c in cards)
assert idx.count('套流程') >= 1
m = re.search(r'<div><b>(\d+)</b><i>套流程</i></div>', idx)
print('   首页统计「套流程」= %s' % (m.group(1) if m else '未找到'))
assert m and m.group(1) == '19', '首页 套流程 计数不对'

# ---------------------------------------------------------------- 3. 新流程页
fp = os.path.join(TB, 'flows', 'annual-party', '01-party.html')
assert os.path.exists(fp), '流程 html 未生成'
h = read(fp)
print('[流程页] 01-party.html %d 字节' % len(h))
h2 = re.findall(r'<h2[^>]*>(.*?)</h2>', h, re.S)
h2 = [re.sub('<[^>]+>', '', x).strip() for x in h2]
print('   h2 %d 个：%s' % (len(h2), ' | '.join(h2)))
assert any('时间轴 A' in x for x in h2) and any('时间轴 B' in x for x in h2)
assert '这套方案解决什么问题' in ' '.join(h2)
assert '本方案配套游戏' in ' '.join(h2)
for g in ('host-show', 'acting-party', 'trivia-show', 'name-tag-war', 'team-quiz',
          'mars-colony', 'gene-lab', 'ai-dream-designer', 'ancient-auction',
          'chef-undercover', 'digital-twin-work'):
    assert '../games/' in h and g + '.html' in h, '流程页缺游戏链接：' + g
print('   11 款游戏链接全部在页内')
assert h.count('<table') >= 6, '表格数偏少：%d' % h.count('<table')
print('   表格 %d 张' % h.count('<table'))

# ---------------------------------------------------------------- 4. slot-map
sm = read(os.path.join(TB, 'toolbox', 'slot-map.html'))
print('[slot-map] %d 字节' % len(sm))
assert '娱乐格' in sm, 'slot-map 缺娱乐格节'
assert '十、维护约定' in sm, '维护约定未改编号'
assert '80–100 min' not in sm or '不是 6' in sm
print('   含「娱乐格」小节 + 维护约定已改十')

# ---------------------------------------------------------------- 5. 14 款游戏页
for rel in ('variety/acting-party', 'variety/host-show', 'variety/trivia-show',
            'variety/name-tag-war', 'variety/team-quiz', 'variety/whisper-chain',
            'icebreaker/name-chain', 'icebreaker/never-have-i-ever',
            'boardgame/mars-colony', 'boardgame/gene-lab', 'boardgame/ai-dream-designer',
            'boardgame/ancient-auction', 'boardgame/chef-undercover',
            'boardgame/digital-twin-work'):
    md = read(os.path.join(TB, 'games', rel + '.md'))
    ht = read(os.path.join(TB, 'games', rel + '.html'))
    ok = ('已真实收录' in md) and ('已真实收录' in ht) and ('annual-party' in md) and ('annual-party' in ht)
    assert ok, '页面收录状态不一致：' + rel
print('[游戏页] 14 款 md + html 双侧均含「已真实收录」与年会链接')
print('\n✅ 回归全部通过')
