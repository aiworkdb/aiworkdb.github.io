# -*- coding: utf-8 -*-
"""md 站内链接体检（相对路径），坏链计数。修复旧坑：排除目录用 not in ('.git','node_modules','_data')"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
TB = r'd:\mycode\aiworkdb.github.io\teambuilding'
LINK = re.compile(r'\]\(([^)\s]+)\)')

total = bad = 0
badlist = []
for base in ('games', 'flows', 'toolbox'):
    for dirp, dirs, fs in os.walk(os.path.join(TB, base)):
        dirs[:] = [d for d in dirs if d not in ('.git', 'node_modules', '_data')]
        for fn in fs:
            if not fn.endswith('.md'):
                continue
            p = os.path.join(dirp, fn)
            txt = io.open(p, encoding='utf-8', newline='').read()
            for u in LINK.findall(txt):
                if u.startswith(('http://', 'https://', 'mailto:', '#')):
                    continue
                total += 1
                path = u.split('#')[0]
                if not path:
                    continue
                tgt = os.path.normpath(os.path.join(dirp, path))
                if not os.path.exists(tgt):
                    bad += 1
                    badlist.append('%s -> %s' % (os.path.relpath(p, TB), u))
print('md 站内链接 %d 条，坏链 %d' % (total, bad))
for b in badlist[:10]:
    print('  ❌', b)
