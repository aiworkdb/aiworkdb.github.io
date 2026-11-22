# -*- coding: utf-8 -*-
"""列出 20 套流程里 ≥40 min 的可排期时段（含环节名）"""
import io, os, re, sys
sys.stdout.reconfigure(encoding='utf-8')
TB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FLOWS = os.path.join(TB, 'flows')

RANGE = re.compile(r'(\d{2}:\d{2})[–-](\d{2}:\d{2})')

def hhmm(s):
    h, m = s.split(':')
    return int(h) * 60 + int(m)

SKIP = ('午餐', '茶歇', '课间', '休息', '到达', '签到', 'Closing', '收尾', '散场', '合影', '颁奖', '转场')

for dirp, _d, fs in sorted(os.walk(FLOWS)):
    for fn in sorted(fs):
        if not fn.endswith('.md'):
            continue
        p = os.path.join(dirp, fn)
        key = os.path.basename(dirp)
        txt = io.open(p, encoding='utf-8', newline='').read()
        print('=== %s / %s' % (key, fn))
        for ln in txt.split('\n'):
            ln = ln.rstrip('\r')
            if not ln.startswith('|'):
                continue
            m = RANGE.search(ln)
            if not m:
                continue
            mins = hhmm(m.group(2)) - hhmm(m.group(1))
            if mins < 40:
                continue
            cells = [c.strip() for c in ln.strip().strip('|').split('|')]
            label = cells[1] if len(cells) > 1 else ''
            if any(k in label for k in SKIP):
                tag = '  [休整格]'
            else:
                tag = ''
            print('   %s–%s %3d min | %s%s' % (m.group(1), m.group(2), mins, label[:60], tag))
