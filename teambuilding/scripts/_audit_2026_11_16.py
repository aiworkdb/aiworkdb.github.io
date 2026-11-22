# -*- coding: utf-8 -*-
"""2026-11-16 体检：22 款无落点游戏的真实时长 / 分类，以及 18 套流程的时间轴。"""
import io, os, re, sys, json

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

TB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAMES = os.path.join(TB, 'games')
FLOWS = os.path.join(TB, 'flows')

ABS = re.compile(r'/games/([a-z-]+)/([a-z0-9-]+)\.html')
REL = re.compile(r'\.\./\.\./games/([a-z-]+)/([a-z0-9-]+)\.md')
LN = re.compile(r'\]\(\.\./\.\./games/([a-z-]+)/([a-z0-9-]+)\.md\)')


def read(p):
    return io.open(p, encoding='utf-8', newline='').read()


real_ids = set()
for dirp, _d, fs in os.walk(FLOWS):
    for fn in fs:
        if fn.endswith('.md'):
            t = read(os.path.join(dirp, fn))
            real_ids |= set(ABS.findall(t)) | set(REL.findall(t))

rows = []
for cat in sorted(os.listdir(GAMES)):
    cdir = os.path.join(GAMES, cat)
    if not os.path.isdir(cdir):
        continue
    for fn in sorted(os.listdir(cdir)):
        if not fn.endswith('.md') or fn.lower() in ('readme.md', 'index.md'):
            continue
        p = os.path.join(cdir, fn)
        t = read(p)
        gid = fn[:-3]
        m = re.search(r'\*\*(?:游戏时长|时长)\*\*\s*\|\s*([^\n|]*)', t)
        dur = re.findall(r'\d+', m.group(1)) if m else []
        m2 = re.search(r'\*\*(?:人数|建议人数)\*\*\s*\|\s*([^\n|]*)', t)
        ppl = m2.group(1).strip() if m2 else ''
        m3 = re.search(r'\*\*(?:团建总时长)\*\*\s*\|\s*([^\n|]*)', t)
        total = re.findall(r'\d+', m3.group(1)) if m3 else []
        has_flow = '(../../flows/' in t or '/teambuilding/flows/' in t
        kind = 'REAL' if (cat, gid) in real_ids else ('SUGG' if has_flow else 'NONE')
        if kind != 'REAL':
            rows.append((kind, cat, gid, dur[:2], total[:2], ppl))

print('=== 非真实收录 %d 款 ===' % len(rows))
for k, c, g, d, tot, ppl in rows:
    print('%-5s %-16s %-32s dur=%-10s total=%-8s people=%s' % (k, c, g, d, tot, ppl))

print()
print('=== 流程时间轴 ===')
RANGE = re.compile(r'(\d{2}:\d{2})[–-](\d{2}:\d{2})')
for d in sorted(os.listdir(FLOWS)):
    dp = os.path.join(FLOWS, d)
    if not os.path.isdir(dp):
        continue
    for fn in sorted(os.listdir(dp)):
        if not fn.endswith('.md'):
            continue
        t = read(os.path.join(dp, fn))
        segs = []
        for ln in t.split('\n'):
            if ln.startswith('|'):
                m = RANGE.search(ln)
                if m:
                    h1, m1 = m.group(1).split(':')
                    h2, m2 = m.group(2).split(':')
                    mins = (int(h2) * 60 + int(m2)) - (int(h1) * 60 + int(m1))
                    segs.append('%s-%s(%d)' % (m.group(1), m.group(2), mins))
        print('%-20s %-22s %s' % (d, fn, ' '.join(segs)))
