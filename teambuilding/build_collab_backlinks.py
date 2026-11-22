# -*- coding: utf-8 -*-
"""给 39 款协作游戏页（md + html）加「→ collab.html 挑款页」反向互链。

背景（ROADMAP 下一步建议 · 2026-10-24 首选）：
    collab.html 挑款页只有 4 个入口（index 分类标题 / 首屏胶囊 / generator 页脚 /
    README 决策表），39 款协作游戏页自己都不知道它存在。而教练最常走的路线恰恰是
    「先翻到某一款，再想还有没有同类」——与第 18 项「游戏 → 流程反向互链」同构。

做法（经验 91：A 页介绍 B 内容，一律复用 B 的原文）：
    组名 / 组导语 / 该款「在练什么」全部从 collab.html 现成表格与 index.html 小标题里
    抽出来，不另写一份。两边永远不会漂移。

用法：
    python teambuilding/build_collab_backlinks.py
幂等：已含锚点章节的游戏页会跳过。
"""
import io
import os
import re
import sys

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

TB = os.path.dirname(os.path.abspath(__file__))
COLLAB = os.path.join(TB, 'games', 'collaboration')
SECTION_TITLE = '🤝 协作挑款：这一款练的是哪一种协作'


def rd(p):
    return io.open(p, encoding='utf-8', newline='').read()


def wr(p, s):
    io.open(p, 'w', encoding='utf-8', newline='').write(s)


def eol_of(t):
    return '\r\n' if '\r\n' in t else '\n'


def parse_collab():
    """从 collab.html 抽 6 组的标题 / 导语 / 成员 / 每款「在练什么」。"""
    t = rd(os.path.join(TB, 'collab.html'))
    keys = re.findall(r'id="g-([a-z]+)"', t)
    pos = sorted([(t.index('id="g-%s"' % k), k) for k in keys])
    groups = {}
    # 最后一组的边界：取「三个最容易挑错的地方」这个 h2 的开标签位置
    end_all = t.rindex('<h2', 0, t.index('三个最容易挑错的地方'))
    for i, (p, k) in enumerate(pos):
        end = pos[i + 1][0] if i + 1 < len(pos) else end_all
        seg = t[p:end]
        chunks = [x.strip() for x in re.sub(r'<[^>]+>', '\x00', seg).split('\x00') if x.strip()]
        # chunks[0] = 'id="g-xxx">'  chunks[1] = h3 标题  chunks[2] = 组导语
        title = chunks[1]
        lead = chunks[2]
        n = int(re.search(r'（(\d+) 款）', title).group(1))
        short = re.sub(r'^[^\w一-龥]+', '', title.split('·')[0]).strip()
        members = []
        for tr in re.finditer(r'<tr[^>]*>(.*?)</tr>', seg, re.S):
            row = tr.group(1)
            lm = re.search(r'href="games/collaboration/([a-z0-9-]+)\.html"', row)
            tds = re.findall(r'<td[^>]*>(.*?)</td>', row, re.S)
            if lm and len(tds) >= 4:
                cells = [re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', x)).strip() for x in tds]
                members.append((lm.group(1), cells[3]))
        assert len(members) == n, '组 %s 表格 %d 款，标题写 %d 款' % (k, len(members), n)
        groups[k] = dict(key=k, title=title, lead=lead, n=n, short=short, members=members)
    return groups


def build_map(groups):
    """game_id -> 组信息 + 该款在练什么；并断言 39 款不重不漏。"""
    m = {}
    for k, g in groups.items():
        for gid, desc in g['members']:
            assert gid not in m, '游戏 %s 同时属于多组' % gid
            m[gid] = dict(key=k, title=g['title'], lead=g['lead'], n=g['n'],
                          short=g['short'], desc=desc)
    on_disk = set(f[:-3] for f in os.listdir(COLLAB) if f.endswith('.md'))
    assert set(m) == on_disk, '分组覆盖 %d 款，目录 %d 款；缺 %s 多 %s' % (
        len(m), len(on_disk), sorted(on_disk - set(m)), sorted(set(m) - on_disk))
    return m


def md_block(g, nl):
    L = []
    a = L.append
    a('---' + nl)
    a(nl)
    a('## ' + SECTION_TITLE + nl)
    a(nl)
    a('协作类 39 款按「到底在练哪种协作」分成 6 组，它属于 **%s**：%s' % (g['title'], nl))
    a(nl)
    a('> %s%s' % (g['lead'], nl))
    a(nl)
    a('**这一组把它收进来，是因为**：%s%s' % (g['desc'], nl))
    a(nl)
    a('- [协作挑款指南 · %s这一组](../../collab.html#g-%s) —— 同组另外 %d 款，'
      '附「什么情况下选它 / 什么时候别选它 / 拿不准就先拿」%s'
      % (g['short'], g['key'], g['n'] - 1, nl))
    a('- [挑款指南首页（30 秒决策表）](../../collab.html) —— 按你现在的麻烦直接对组，'
      '不用先读完 39 张卡%s' % nl)
    a(nl)
    a('> 想换一种协作练？6 组之间的边界，以及「三个最容易挑错的地方」，都写在挑款页里。%s' % nl)
    a(nl)
    return ''.join(L)


def html_block(g, indent, nl):
    i = indent
    j = indent + '    '
    k = indent + '        '
    L = []
    a = L.append
    a('%s<div class="section">%s' % (i, nl))
    a('%s<h2>%s</h2>%s' % (j, SECTION_TITLE, nl))
    a('%s<p>协作类 39 款按「到底在练哪种协作」分成 6 组，它属于 <strong>%s</strong>：</p>%s'
      % (j, g['title'], nl))
    a('%s<div class="highlight">%s' % (j, nl))
    a('%s<p>%s</p>%s' % (k, g['lead'], nl))
    a('%s</div>%s' % (j, nl))
    a('%s<p><strong>这一组把它收进来，是因为：</strong>%s</p>%s' % (j, g['desc'], nl))
    a('%s<ul style="margin-left: 20px;">%s' % (j, nl))
    a('%s<li><a href="../../collab.html#g-%s">协作挑款指南 · %s这一组</a> —— 同组另外 %d 款，'
      '附「什么情况下选它 / 什么时候别选它 / 拿不准就先拿」</li>%s'
      % (k, g['key'], g['short'], g['n'] - 1, nl))
    a('%s<li><a href="../../collab.html">挑款指南首页（30 秒决策表）</a> —— 按你现在的麻烦直接对组，'
      '不用先读完 39 张卡</li>%s' % (k, nl))
    a('%s</ul>%s' % (j, nl))
    a('%s<p>想换一种协作练？6 组之间的边界，以及「三个最容易挑错的地方」，都写在挑款页里。</p>%s'
      % (j, nl))
    a('%s</div>%s' % (i, nl))
    a(nl)
    return ''.join(L)


def patch_md(gid, g):
    p = os.path.join(COLLAB, gid + '.md')
    t = rd(p)
    if SECTION_TITLE in t:
        return 'skip'
    marker = '## 🧩 这套游戏被哪些流程用过'
    assert t.count(marker) == 1, '%s 流程反向互链章节数 %d' % (gid, t.count(marker))
    i = t.index(marker)
    j = t.rindex('\n---', 0, i)          # 该章节前一个分隔行的行首换行
    nl = eol_of(t)
    new = t[:j + 1] + md_block(g, nl) + t[j + 1:]
    assert new.count(marker) == 1 and SECTION_TITLE in new
    assert len(new) > len(t)
    wr(p, new)
    return 'ok'


def patch_html(gid, g):
    p = os.path.join(COLLAB, gid + '.html')
    t = rd(p)
    if SECTION_TITLE in t:
        return 'skip'
    marker = '<h2>🧩 这套游戏被哪些流程用过</h2>'
    assert t.count(marker) == 1, '%s 流程反向互链章节数 %d' % (gid, t.count(marker))
    i = t.index(marker)
    j = t.rindex('<div class="section">', 0, i)
    line_start = t.rindex('\n', 0, j) + 1
    indent = t[line_start:j]
    assert indent.strip() == '', '缩进行含非空白：%r' % indent
    nl = eol_of(t)
    new = t[:line_start] + html_block(g, indent, nl) + t[line_start:]
    assert new.count(marker) == 1 and SECTION_TITLE in new
    assert len(new) > len(t)
    wr(p, new)
    return 'ok'


def main():
    groups = parse_collab()
    gmap = build_map(groups)
    print('分组 %d 组 / 游戏 %d 款：%s'
          % (len(groups), len(gmap),
             ', '.join('%s=%d' % (k, g['n']) for k, g in sorted(groups.items()))))
    n_md = n_html = n_skip = 0
    for gid in sorted(gmap):
        g = gmap[gid]
        for fn in (patch_md, patch_html):
            r = fn(gid, g)
            if r == 'ok':
                if fn is patch_md:
                    n_md += 1
                else:
                    n_html += 1
            else:
                n_skip += 1
    print('完成：md %d 个 / html %d 个新增章节；跳过（已存在）%d 处' % (n_md, n_html, n_skip))


if __name__ == '__main__':
    main()
