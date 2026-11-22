# -*- coding: utf-8 -*-
"""列出 9 款「完全没落点」的游戏，并看它们有没有落点节"""
import io, os, re, sys
sys.stdout.reconfigure(encoding='utf-8')
TB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAMES = os.path.join(TB, 'games')
FLOWS = os.path.join(TB, 'flows')

def read(p):
    return io.open(p, encoding='utf-8', newline='').read()

ABS = re.compile(r'/games/([a-z-]+)/([a-z0-9-]+)\.html')
REL = re.compile(r'\.\./\.\./games/([a-z-]+)/([a-z0-9-]+)\.md')
real_ids = set()
for dirp, _d, fs in os.walk(FLOWS):
    for fn in fs:
        if fn.endswith('.md'):
            t = read(os.path.join(dirp, fn))
            real_ids |= set(ABS.findall(t)) | set(REL.findall(t))

for cat in sorted(os.listdir(GAMES)):
    cdir = os.path.join(GAMES, cat)
    if not os.path.isdir(cdir):
        continue
    for fn in sorted(os.listdir(cdir)):
        if not fn.endswith('.md') or fn.lower() in ('readme.md', 'index.md'):
            continue
        gid = fn[:-3]
        txt = read(os.path.join(cdir, fn))
        has_flow = '(../../flows/' in txt or '/teambuilding/flows/' in txt
        if (cat, gid) in real_ids or has_flow:
            continue
        has_sec = '## 🧩 这套游戏被哪些流程用过' in txt
        # 时长与人数
        m = re.search(r'\*\*(?:游戏时长|时长)\*\*\s*\|\s*([^\n|]*)', txt)
        p = re.search(r'\*\*人数\*\*\s*\|\s*([^\n|]*)', txt)
        print('%-16s %-24s 落点节=%-5s 时长=%-20s 人数=%s'
              % (cat, gid, has_sec, (m.group(1).strip() if m else '?'), (p.group(1).strip() if p else '?')))
