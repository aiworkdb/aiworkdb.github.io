# -*- coding: utf-8 -*-
"""给 10 款创意/解题游戏页（md + html）加「→ idea.html 挑款页」反向互链。

背景（ROADMAP 下一步建议 · 2026-10-25 首选）：
    创意与解题二级索引建好后，idea.html 挑款页本身只有几个入口（index 分类标题 /
    首屏胶囊 / README 决策表 / 分类筛选行），10 款游戏页自己都不知道它存在。
    而教练最常走的路线恰恰是「先翻到某一款，再想还有没有同类」——与第 22 项
    「协作挑款反向互链」同构。

做法（经验 91：A 页介绍 B 内容，一律复用 B 的原文）：
    组名 / 组导语 / 该款「在练什么」全部从 idea.html 现成表格抽取，
    不另写一份。两边永远不会漂移。

用法：
    python teambuilding/build_idea_backlinks.py
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
DIRS = ['creativity', 'problem-solving']
SECTION_TITLE = '💡 创意与解题挑款：这一款练的是哪一步'


def rd(p):
    return io.open(p, encoding='utf-8', newline='').read()


def wr(p, s):
    io.open(p, 'w', encoding='utf-8', newline='').write(s)


def eol_of(t):
    return '\r\n' if '\r\n' in t else '\n'


def parse_idea():
    """从 idea.html 抽 4 组的 组名 / 导语 / 每款「在练什么」。"""
    t = rd(os.path.join(TB, 'idea.html'))
    keys = re.findall(r'<div class="group-card" id="g-([a-z]+)">', t)
    assert len(keys) == 4, 'idea.html 分组数 %d != 4' % len(keys)
    groups = {}
    for k in keys:
        start = t.index('<div class="group-card" id="g-%s">' % k)
        nxt = [t.index('<div class="group-card" id="g-%s">' % x)
               for x in keys if t.index('<div class="group-card" id="g-%s">' % x) > start]
        end = min(nxt) if nxt else t.index('⚠️ 三个最容易挑错的地方')
        seg = t[start:end]
        h3 = re.search(r'<h3>(.*?)（(\d+) 款）</h3>', seg, re.S)
        assert h3, '组 %s 缺 h3 标题' % k
        title = h3.group(1).strip()
        n = int(h3.group(2))
        lead = re.search(r'<div class="group-lead">(.*?)</div>', seg, re.S).group(1).strip()
        members = []
        for row in re.finditer(r'<tr><td><a href="games/(?:creativity|problem-solving)/'
                               r'([a-z0-9-]+)\.html">(.*?)</a></td>'
                               r'<td class="cat">(.*?)</td><td>.*?</td><td>.*?</td>'
                               r'<td>(.*?)</td></tr>', seg, re.S):
            members.append((row.group(1),
                            re.sub(r'\s+', ' ', row.group(2)).strip(),
                            re.sub(r'\s+', ' ', row.group(3)).strip(),
                            re.sub(r'\s+', ' ', row.group(4)).strip()))
        assert len(members) == n, '组 %s 表格 %d 款，标题写 %d 款' % (k, len(members), n)
        groups[k] = dict(key=k, title=title, n=n, lead=lead, members=members)
    return groups


def build_map(groups):
    """game_id -> 组信息 + 该款「在练什么」；并断言 10 款不重不漏。"""
    m = {}
    for k, g in groups.items():
        for gid, name, cat, desc in g['members']:
            assert gid not in m, '游戏 %s 同时属于多组' % gid
            m[gid] = dict(key=k, title=g['title'], n=g['n'], lead=g['lead'],
                          name=name, cat=cat, desc=desc)
    on_disk = set()
    for d in DIRS:
        for f in os.listdir(os.path.join(TB, 'games', d)):
            if f.endswith('.md'):
                on_disk.add(f[:-3])
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
    a('💡创新思维 + 🔧问题解决 共 10 款按「团队当下卡在哪一步」分成 4 组，'
      '它属于 **%s（%d 款）**：' % (g['title'], g['n']) + nl)
    a(nl)
    a('> %s%s' % (g['lead'], nl))
    a(nl)
    a('**这一组把它收进来，是因为**：%s%s' % (g['desc'], nl))
    a(nl)
    a('- [创意与解题挑款指南 · %s这一组](../../idea.html#g-%s) —— 同组另外 %d 款，'
      '附「什么情况下选它 / 什么时候别选它 / 拿不准就先拿」%s'
      % (g['title'], g['key'], g['n'] - 1, nl))
    a('- [挑款指南首页（30 秒决策表）](../../idea.html) —— 按你现在的麻烦直接对组，'
      '不用先读完 10 张卡%s' % nl)
    a(nl)
    a('> 想换一种练？4 组之间的边界，以及「三个最容易挑错的地方」，都写在挑款页里。%s' % nl)
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
    a('%s<p>💡创新思维 + 🔧问题解决 共 10 款按「团队当下卡在哪一步」分成 4 组，'
      '它属于 <strong>%s（%d 款）</strong>：</p>%s'
      % (j, g['title'], g['n'], nl))
    a('%s<div class="highlight">%s' % (j, nl))
    a('%s<p>%s</p>%s' % (k, g['lead'], nl))
    a('%s</div>%s' % (j, nl))
    a('%s<p><strong>这一组把它收进来，是因为：</strong>%s</p>%s' % (j, g['desc'], nl))
    a('%s<ul style="margin-left: 20px;">%s' % (j, nl))
    a('%s<li><a href="../../idea.html#g-%s">创意与解题挑款指南 · %s这一组</a> —— 同组另外 %d 款，'
      '附「什么情况下选它 / 什么时候别选它 / 拿不准就先拿」</li>%s'
      % (k, g['key'], g['title'], g['n'] - 1, nl))
    a('%s<li><a href="../../idea.html">挑款指南首页（30 秒决策表）</a> —— 按你现在的麻烦直接对组，'
      '不用先读完 10 张卡</li>%s' % (k, nl))
    a('%s</ul>%s' % (j, nl))
    a('%s<p>想换一种练？4 组之间的边界，以及「三个最容易挑错的地方」，都写在挑款页里。</p>%s'
      % (j, nl))
    a('%s</div>%s' % (i, nl))
    a(nl)
    return ''.join(L)


def patch_md(gid, g):
    p = None
    for d in DIRS:
        cand = os.path.join(TB, 'games', d, gid + '.md')
        if os.path.exists(cand):
            p = cand
            break
    assert p, '找不到游戏 md: ' + gid
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
    p = None
    for d in DIRS:
        cand = os.path.join(TB, 'games', d, gid + '.html')
        if os.path.exists(cand):
            p = cand
            break
    assert p, '找不到游戏 html: ' + gid
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
    groups = parse_idea()
    gmap = build_map(groups)
    print('分组 %d 组 / 游戏 %d 款：%s'
          % (len(groups), len(gmap),
             ', '.join('%s=%d' % (k, sum(1 for v in gmap.values() if v['key'] == k))
                       for k in sorted(groups))))
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
