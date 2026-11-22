# -*- coding: utf-8 -*-
import io, os, re, sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
TB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FL = os.path.join(TB, 'flows')
for d in sorted(os.listdir(FL)):
    dp = os.path.join(FL, d)
    if not os.path.isdir(dp):
        continue
    for fn in sorted(os.listdir(dp)):
        if not fn.endswith('.md'):
            continue
        t = io.open(os.path.join(dp, fn), encoding='utf-8', newline='').read()
        title = ''
        m = re.search(r'^#\s+(.+)$', t, re.M)
        if m:
            title = m.group(1).strip()
        tm = re.search(r'\*\*时长\*\*[：:]\s*(.+)', t)
        pm = re.search(r'\*\*人数\*\*[：:]\s*(.+)', t)
        # 页脚互链节
        tail = t[-1200:]
        print('%-20s %-24s' % (d, fn))
        print('   title:', title)
        print('   time :', tm.group(1).strip()[:70] if tm else '-')
        print('   ppl  :', pm.group(1).strip()[:70] if pm else '-')
        print('   h2s  :', ' | '.join(x.strip() for x in re.findall(r'^##\s+(.+)$', t, re.M))[:300])
