# -*- coding: utf-8 -*-
import io, os, re, sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
TB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def read(p):
    return io.open(p, encoding='utf-8', newline='').read()

targets = [
    ('games/boardgame', 'ai-dream-designer'), ('games/boardgame', 'ancient-auction'),
    ('games/boardgame', 'chef-undercover'), ('games/boardgame', 'digital-twin-work'),
    ('games/boardgame', 'gene-lab'), ('games/boardgame', 'mars-colony'),
    ('games/variety', 'acting-party'), ('games/variety', 'host-show'),
    ('games/variety', 'name-tag-war'), ('games/variety', 'trivia-show'),
    ('games/variety', 'team-quiz'),
]
for d, g in targets:
    p = os.path.join(TB, d, g + '.md')
    t = read(p)
    eol = 'CRLF' if '\r\n' in t else 'LF'
    heads = re.findall(r'^##\s+(.+)$', t, re.M)
    print('%-18s %-32s %s  len=%d' % (d.split('/')[-1], g, eol, len(t)))
    print('    ', ' || '.join(h.strip() for h in heads))

print()
print('=== 时长字段 ===')
for d, g in targets:
    t = read(os.path.join(TB, d, g + '.md'))
    for ln in t.split('\n'):
        ln = ln.rstrip('\r')
        if ln.startswith('|') and ('时长' in ln or '人数' in ln):
            print('%-18s %s' % (g, ln.strip()))
