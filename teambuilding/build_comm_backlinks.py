# -*- coding: utf-8 -*-
"""给 8 款沟通游戏页（md + html）加「→ comm.html 挑款页」反向互链。

背景（ROADMAP 下一步建议 · 2026-10-28 首选）：
    沟通二级索引建好后，comm.html 挑款页本身只有几个入口（index 分类标题 /
    首屏胶囊 / README 决策表 / 分类筛选行），8 款游戏页自己都不知道它存在。
    而教练最常走的路线恰恰是「先翻到某一款，再想还有没有同类」——
    与第 22 / 25 / 28 / 31 项（协作、创意解题、破冰、线上的挑款反向互链）完全同构。

做法（经验 91：A 页介绍 B 内容，一律复用 B 的原文）：
    组名 / 组导语 / 该款「这一局堵住的是什么」全部从 comm.html 现成表格抽取，
    不另写一份。两边永远不会漂移。

用法：
    python teambuilding/build_comm_backlinks.py          # 只补没有的章节
    python teambuilding/build_comm_backlinks.py --force  # 已有章节也用 comm.html 现值覆盖
幂等：已含锚点章节的游戏页会跳过（--force 时改为覆盖）。
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
DIR = 'communication'
SECTION_TITLE = '💬 沟通挑款：这一款练的是哪一环'
FORCE = '--force' in sys.argv

# 尾部锚点必须锚到带标签的 <h2>：纯文本「💬 沟通不只是这 8 款」在上一节的
# blockquote 里也出现过一次，用纯文本当边界会把最后一组切成空段（经验 98/101）
TAIL = '<h2>💬 沟通不只是这 8 款</h2>'


def rd(p):
    return io.open(p, encoding='utf-8', newline='').read()


def wr(p, s):
    io.open(p, 'w', encoding='utf-8', newline='').write(s)


def eol_of(t):
    return '\r\n' if '\r\n' in t else '\n'


def parse_comm():
    """从 comm.html 抽 4 组的 组名 / 导语 / 每款「这一局堵住的是什么」。"""
    t = rd(os.path.join(TB, 'comm.html'))
    keys = re.findall(r'<div class="group-card" id="g-([a-z]+)">', t)
    assert len(keys) == 4, 'comm.html 分组数 %d != 4' % len(keys)
    assert t.count(TAIL) == 1, 'comm.html 尾部锚点命中 %d 次' % t.count(TAIL)
    groups = {}
    for k in keys:
        start = t.index('<div class="group-card" id="g-%s">' % k)
        nxt = [t.index('<div class="group-card" id="g-%s">' % x)
               for x in keys if t.index('<div class="group-card" id="g-%s">' % x) > start]
        end = min(nxt) if nxt else t.index(TAIL)
        assert end > start, '组 %s 段为空（边界在起点之前）' % k
        seg = t[start:end]
        h3 = re.search(r'<h3>(.*?)（(\d+) 款）</h3>', seg, re.S)
        assert h3, '组 %s 缺 h3 标题' % k
        title = h3.group(1).strip()
        n = int(h3.group(2))
        lead = re.search(r'<div class="group-lead">(.*?)</div>', seg, re.S).group(1).strip()
        members = []
        for row in re.finditer(r'<tr><td><a href="games/communication/([a-z0-9-]+)\.html">(.*?)</a></td>'
                               r'<td class="cat">.*?</td><td>.*?</td><td>.*?</td>'
                               r'<td>(.*?)</td><td>.*?</td></tr>', seg, re.S):
            members.append((row.group(1),
                            re.sub(r'\s+', ' ', row.group(2)).strip(),
                            re.sub(r'\s+', ' ', row.group(3)).strip()))
        assert len(members) == n, '组 %s 表格 %d 款，标题写 %d 款' % (k, len(members), n)
        groups[k] = dict(key=k, title=title, n=n, lead=lead, members=members)
    return groups


def build_map(groups):
    """game_id -> 组信息 + 该款「堵住的是什么」；并断言 8 款不重不漏。"""
    m = {}
    for k, g in groups.items():
        for gid, name, blocked in g['members']:
            assert gid not in m, '游戏 %s 同时属于多组' % gid
            m[gid] = dict(key=k, title=g['title'], n=g['n'], lead=g['lead'],
                          name=name, blocked=blocked)
    on_disk = set()
    for f in os.listdir(os.path.join(TB, 'games', DIR)):
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
    a('💬沟通 8 款按「这一局，沟通坏在哪一环」分成 4 组，'
      '它属于 **%s（%d 款）**：' % (g['title'], g['n']) + nl)
    a(nl)
    a('> %s%s' % (g['lead'], nl))
    a(nl)
    a('**这一局堵住的是什么**：%s%s' % (g['blocked'], nl))
    a(nl)
    a('- [沟通挑款指南 · %s这一组](../../comm.html#g-%s) —— 同组另外 %d 款，'
      '附「什么情况下选它 / 什么时候别选它 / 拿不准就先拿」%s'
      % (g['title'], g['key'], g['n'] - 1, nl))
    a('- [挑款指南首页（30 秒决策表）](../../comm.html) —— 按你现在的麻烦直接对组，'
      '不用先读完 8 张卡%s' % nl)
    a(nl)
    a('> 想换一环练？4 组之间的边界，以及「四个最容易挑错的地方」，都写在挑款页里。%s' % nl)
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
    a('%s<p>💬沟通 8 款按「这一局，沟通坏在哪一环」分成 4 组，'
      '它属于 <strong>%s（%d 款）</strong>：</p>%s'
      % (j, g['title'], g['n'], nl))
    a('%s<div class="highlight">%s' % (j, nl))
    a('%s<p>%s</p>%s' % (k, g['lead'], nl))
    a('%s</div>%s' % (j, nl))
    a('%s<p><strong>这一局堵住的是什么：</strong>%s</p>%s' % (j, g['blocked'], nl))
    a('%s<ul style="margin-left: 20px;">%s' % (j, nl))
    a('%s<li><a href="../../comm.html#g-%s">沟通挑款指南 · %s这一组</a> —— 同组另外 %d 款，'
      '附「什么情况下选它 / 什么时候别选它 / 拿不准就先拿」</li>%s'
      % (k, g['key'], g['title'], g['n'] - 1, nl))
    a('%s<li><a href="../../comm.html">挑款指南首页（30 秒决策表）</a> —— 按你现在的麻烦直接对组，'
      '不用先读完 8 张卡</li>%s' % (k, nl))
    a('%s</ul>%s' % (j, nl))
    a('%s<p>想换一环练？4 组之间的边界，以及「四个最容易挑错的地方」，都写在挑款页里。</p>%s'
      % (j, nl))
    a('%s</div>%s' % (i, nl))
    a(nl)
    return ''.join(L)


def remove_md_section(t):
    """把先前插入的 md 章节整段摘掉，回到「插入之前」的状态。"""
    nl = eol_of(t)
    sep = nl + '---' + nl
    i = t.index('## ' + SECTION_TITLE)
    s = t.rindex(sep, 0, i) + len(nl)
    k = t.index('## 🧩 这套游戏被哪些流程用过', i)
    e = t.rindex(sep, 0, k) + len(nl)
    assert s < e, 'md 章节边界异常'
    return t[:s] + t[e:]


def remove_html_section(t):
    """把先前插入的 html 章节整段摘掉（与 patch_html 的插入对称）。"""
    i = t.index('<h2>' + SECTION_TITLE + '</h2>')
    s = t.rindex('<div class="section">', 0, i)
    line_start = t.rindex('\n', 0, s) + 1
    k = t.index('<h2>🧩 这套游戏被哪些流程用过</h2>', i)
    e = t.rindex('<div class="section">', 0, k)
    assert line_start < e, 'html 章节边界异常'
    return t[:line_start] + t[e:]


def patch_md(gid, g):
    p = os.path.join(TB, 'games', DIR, gid + '.md')
    assert os.path.exists(p), '找不到游戏 md: ' + gid
    t = rd(p)
    if SECTION_TITLE in t:
        if not FORCE:
            return 'skip'
        t = remove_md_section(t)
    marker = '## 🧩 这套游戏被哪些流程用过'
    assert t.count(marker) == 1, '%s 流程反向互链章节数 %d' % (gid, t.count(marker))
    i = t.index(marker)
    j = t.rindex('\n---', 0, i)
    nl = eol_of(t)
    new = t[:j + 1] + md_block(g, nl) + t[j + 1:]
    assert new.count(marker) == 1 and SECTION_TITLE in new
    assert len(new) > len(t)
    wr(p, new)
    return 'ok'


def patch_html(gid, g):
    p = os.path.join(TB, 'games', DIR, gid + '.html')
    assert os.path.exists(p), '找不到游戏 html: ' + gid
    t = rd(p)
    if SECTION_TITLE in t:
        if not FORCE:
            return 'skip'
        t = remove_html_section(t)
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
    groups = parse_comm()
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
