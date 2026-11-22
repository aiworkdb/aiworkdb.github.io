# -*- coding: utf-8 -*-
"""site_check.py 的第 39 / 40 / 41 项：信任二级索引 / 挑款反向互链 / 生成器信任子类。

  [39] 信任二级索引：6 款 data-trust 与目录一致、3 组锚点同源、
       「信任 ≠ 敢把后背交出去」边界说明与「信任不只是这 6 款」跨分类说明必须在场、
       跨分类那 4 款逐一点名、每组款数三处一致、首选真实存在且属于本组
  [40] 信任挑款反向互链：6 款 md + html 双侧章节齐全、锚点所属组与 data-trust 一致
  [41] 生成器信任子类：3 组定义与 index.html 的 data-trust 逐款同源、
       4 个按钮取值 == 3 个 key + any、refreshTrustSub / 目的判定 /
       TRUST_SUB_OF[game.id] === trustKey / lastTrustFallback / TRUST_ALL_IDS
       缺一不可、组文案与 trust.html 双向逐字相等、?trust= 参数必须在场

固化原因与第 33 / 36 项同型。信任的分组口径是**「托付出去的是什么」**——
全库第七套切法，与协作（练哪种协作）、创意解题（卡在哪一步）、破冰（结束留下什么）、
线上（远程靠什么成立）、沟通（这一局坏在哪一环）、领导力（带人卡在哪一层）都不同。
"""
import io
import os
import re

# 跨分类：带「信任」标签但分类不在 trust 的游戏（trust.html 必须逐一点名）
CROSS_TRUST = [
    'huntrix-honmoon',                     # 🤝 协作
    'blind-polygon', 'rumor-factory',      # 💬 沟通
    'red-black-game',                      # 👑 领导力
]
CROSS_TRUST_CATS = ('collaboration', 'communication', 'leadership')

TRUST_GROUP_NAMES = ['🫱 交出身体与安全', '💬 交出会受伤的自己', '🤝 交出一件事的成败']

SECTION_TITLE = '🔐 信任挑款：这一款托付出去的是什么'

TAIL = '<h2>🔐 信任不只是这 6 款</h2>'


def _anchor_keys(html):
    return re.findall(r'<div class="group-card" id="g-([a-z]+)">', html)


def _group_blocks(html):
    keys = _anchor_keys(html)
    blocks = {}
    for k in keys:
        start = html.index('<div class="group-card" id="g-%s">' % k)
        nxt = [html.index('<div class="group-card" id="g-%s">' % x)
               for x in keys if html.index('<div class="group-card" id="g-%s">' % x) > start]
        end = min(nxt) if nxt else html.index(TAIL)
        blocks[k] = html[start:end]
    return blocks


def _tagged(idx):
    return dict((gid, sub) for gid, sub in re.findall(
        r'<a href="games/trust/([a-z0-9-]+)\.html" '
        r'class="card" data-trust="([a-z]+)"', idx))


# ---------------- [39] 信任二级索引 ----------------
def check_trust_index(errors, TB):
    idx = io.open(os.path.join(TB, 'index.html'), encoding='utf-8').read()
    cm = io.open(os.path.join(TB, 'trust.html'), encoding='utf-8').read()
    rm = io.open(os.path.join(TB, 'README.md'), encoding='utf-8').read()
    bad = 0

    on_disk = set()
    for f in os.listdir(os.path.join(TB, 'games', 'trust')):
        if f.endswith('.md'):
            on_disk.add(f[:-3])
    tagged = _tagged(idx)
    if set(tagged) != on_disk:
        errors.append('信任卡片的 data-trust 与目录不一致：缺 %s 多 %s'
                      % (sorted(on_disk - set(tagged)), sorted(set(tagged) - on_disk)))
        bad += 1
    if len(tagged) != 6:
        errors.append('信任卡片 data-trust 数量 %d != 6' % len(tagged))
        bad += 1

    if 'id="trust-filter"' not in idx:
        errors.append('index.html 缺「托付出去的是什么」筛选行')
        bad += 1
    for needle in ('resetTrust', 'setTrustRow', 'currentFilters.trust',
                   "card.getAttribute('data-trust') !== currentFilters.trust",
                   "value === 'trust'",
                   "if (value === 'trust') { setTrustRow(true); }",
                   "else { resetTrust(); setTrustRow(false); }"):
        if needle not in idx:
            errors.append('index.html 缺信任筛选逻辑片段：%s' % needle)
            bad += 1
    btns = re.findall(r"onclick=\"toggleFilter\('trust', '([a-z]+)', this\)\"", idx)
    if len(btns) != 4 or set(btns) != set(tagged.values()) | set(['all']):
        errors.append('index.html 的 trust 按钮 %s 与分组 %s 不对应'
                      % (sorted(btns), sorted(set(tagged.values()))))
        bad += 1

    m_tr = re.search(r'<div class="grid" id="grid-trust">(.*?)\n    </div>', idx, re.S)
    if not m_tr:
        errors.append('index.html 未找到 grid-trust 网格')
        bad += 1
    elif 'class="subhead"' in m_tr.group(1):
        errors.append('index.html 信任网格不应有小标题（.subhead）')
        bad += 1
    for gid in sorted(tagged):
        mm = re.search(r'<a href="games/trust/%s\.html" class="card"[^>]*>(.*?)</a>'
                       % re.escape(gid), idx, re.S)
        if not mm:
            errors.append('index.html 缺信任卡片 %s' % gid)
            bad += 1
        elif 'card-tags' not in mm.group(1):
            errors.append('index.html 信任卡片 %s 缺肌肉标签胶囊' % gid)
            bad += 1

    anchors = _anchor_keys(cm)
    if set(anchors) != set(tagged.values()):
        errors.append('trust.html 分组锚点 %s 与 index.html data-trust %s 不一致'
                      % (sorted(set(anchors)), sorted(set(tagged.values()))))
        bad += 1
    if len(anchors) != 3:
        errors.append('trust.html 分组数 %d != 3' % len(anchors))
        bad += 1

    if '「信任」不等于「敢把后背交出去」' not in cm:
        errors.append('trust.html 缺「信任 ≠ 敢把后背交出去」边界说明')
        bad += 1
    if '信任不只是这 6 款' not in cm:
        errors.append('trust.html 缺「信任不只是这 6 款」跨分类说明')
        bad += 1
    for gid in CROSS_TRUST:
        if any(('games/%s/%s.html' % (c, gid)) in cm for c in CROSS_TRUST_CATS):
            continue
        errors.append('trust.html 未列出带「信任」标签的跨分类游戏：%s' % gid)
        bad += 1

    blocks = _group_blocks(cm)
    for key in sorted(anchors):
        blk = blocks[key]
        m = re.search(r'<h3>(.*?)（(\d+) 款）</h3>', blk)
        if not m:
            errors.append('trust.html 组 %s 缺标题款数' % key)
            bad += 1
            continue
        n_title = int(m.group(2))
        rows = re.findall(r'<tr><td><a href="games/trust/([a-z0-9-]+)\.html">', blk)
        if len(rows) != n_title:
            errors.append('trust.html 组 %s 表格 %d 款，标题写 %d 款'
                          % (key, len(rows), n_title))
            bad += 1
        n_card = sum(1 for v in tagged.values() if v == key)
        if n_card != n_title:
            errors.append('trust.html 组 %s 标题写 %d 款，index.html 该组 %d 款'
                          % (key, n_title, n_card))
            bad += 1
        if '什么情况下选它' not in blk or '什么时候别选它' not in blk:
            errors.append('trust.html 组 %s 缺「何时选 / 何时别选」' % key)
            bad += 1
        pick = re.search(r'🎯 拿不准就先拿：<a href="games/trust/([a-z0-9-]+)\.html"', blk)
        if not pick:
            errors.append('trust.html 组 %s 缺组内首选' % key)
            bad += 1
        elif pick.group(1) not in rows:
            errors.append('trust.html 组 %s 的首选 %s 不在本组表格里' % (key, pick.group(1)))
            bad += 1

    if '信任挑款指南' not in rm:
        errors.append('README 缺信任挑款指南入口')
        bad += 1
    for name in TRUST_GROUP_NAMES:
        if name not in rm:
            errors.append('README 信任小节缺分组：%s' % name)
            bad += 1
    for href in ('index.html', 'README.md', 'toolbox/generator.html'):
        if href not in cm:
            errors.append('trust.html 缺相关入口：%s' % href)
            bad += 1

    print('[39] 信任二级索引：%d 款 / %d 组（%s）；挑款页收录 %d 次；异常 %d 项'
          % (len(tagged), len(anchors),
             ', '.join('%s=%d' % (k, sum(1 for v in tagged.values() if v == k))
                       for k in sorted(set(tagged.values()))),
             rm.count('trust.html'), bad))
    return bad


# ---------------- [40] 信任挑款反向互链 ----------------
def check_trust_backlinks(errors, TB):
    idx = io.open(os.path.join(TB, 'index.html'), encoding='utf-8').read()
    tagged = _tagged(idx)
    bad = 0
    n_md = n_html = n_link = 0
    anchors = set()

    for gid in sorted(tagged):
        for ext in ('md', 'html'):
            p = os.path.join(TB, 'games', 'trust', gid + '.' + ext)
            if not os.path.exists(p):
                errors.append('信任游戏页缺失：%s.%s' % (gid, ext))
                bad += 1
                continue
            t = io.open(p, encoding='utf-8').read()
            if SECTION_TITLE not in t:
                errors.append('%s.%s 缺「信任挑款」章节' % (gid, ext))
                bad += 1
                continue
            if ext == 'md':
                n_md += 1
                m = re.search(r'\[信任挑款指南 · [^]]*\]\(\.\./\.\./trust\.html#g-([a-z]+)\)', t)
            else:
                n_html += 1
                m = re.search(r'<a href="\.\./\.\./trust\.html#g-([a-z]+)">信任挑款指南 · ', t)
            if not m:
                errors.append('%s.%s 缺信任挑款页锚点链接' % (gid, ext))
                bad += 1
                continue
            n_link += 1
            anchors.add(m.group(1))
            if m.group(1) != tagged[gid]:
                errors.append('%s.%s 的锚点组 %s 与 index.html data-trust %s 不一致'
                              % (gid, ext, m.group(1), tagged[gid]))
                bad += 1
            home = '](../../trust.html)' if ext == 'md' else 'href="../../trust.html"'
            if home not in t:
                errors.append('%s.%s 缺挑款页首页链接' % (gid, ext))
                bad += 1

    if anchors != set(tagged.values()):
        errors.append('信任挑款反向互链锚点集合 %s 与分组 %s 不一致'
                      % (sorted(anchors), sorted(set(tagged.values()))))
        bad += 1

    print('[40] 信任挑款反向互链：md %d 次 / html %d 次，锚点链接 %d 条，分组 %d 个；异常 %d 项'
          % (n_md, n_html, n_link, len(anchors), bad))
    return bad


# ---------------- [41] 生成器信任子类 ----------------
_GROUP_RE = (
    r"\{ key: '([a-z]+)', name: '([^']*)', short: '([^']*)', n: (\d+),\s*"
    r"lead: '((?:[^'\\]|\\.)*)',\s*"
    r"when: '((?:[^'\\]|\\.)*)',\s*"
    r"avoid: '((?:[^'\\]|\\.)*)',\s*"
    r"pick: '([a-z0-9-]+)',\s*"
    r"ids: \[([^\]]*)\] \}"
)


def check_generator_trust_sub(errors, TB):
    g = io.open(os.path.join(TB, 'toolbox', 'generator.html'), encoding='utf-8').read()
    cm = io.open(os.path.join(TB, 'trust.html'), encoding='utf-8').read()
    idx = io.open(os.path.join(TB, 'index.html'), encoding='utf-8').read()
    bad = 0

    idx_sub = _tagged(idx)
    blk = re.search(r'var TRUST_GROUPS = \[([\s\S]*?)\n\];', g)
    if not blk:
        errors.append('generator.html 缺 TRUST_GROUPS 定义')
        return 1
    if len(re.findall(r"\{ key: '([a-z]+)', name: '([^']*)', short: '([^']*)', n: (\d+),",
                      blk.group(1))) != 3:
        errors.append('generator.html TRUST_GROUPS 组数 != 3')
        bad += 1
    gen_sub = {}
    for m in re.finditer(_GROUP_RE, blk.group(1)):
        ids = [x.strip().strip("'") for x in m.group(9).split(',') if x.strip()]
        for gid in ids:
            if gid in gen_sub:
                errors.append('generator.html 游戏 %s 同时属于多组' % gid)
                bad += 1
            gen_sub[gid] = m.group(1)
    if set(gen_sub) != set(idx_sub):
        errors.append('generator.html 信任分组覆盖 %s 与 index.html %s 不一致'
                      % (sorted(set(gen_sub)), sorted(set(idx_sub))))
        bad += 1
    else:
        for gid, sub in idx_sub.items():
            if gen_sub[gid] != sub:
                errors.append('generator.html 游戏 %s 归组 %s 与 index.html %s 不一致'
                              % (gid, gen_sub[gid], sub))
                bad += 1

    vals = re.findall(r"data-value=\"([a-z]+)\" onclick=\"selectOption\(this, 'trustSub'\)\"", g)
    if len(vals) != 4 or set(vals) != set(gen_sub.values()) | set(['any']):
        errors.append('generator.html trustSub 按钮取值 %s 与分组 %s 不对应'
                      % (sorted(vals), sorted(set(gen_sub.values()))))
        bad += 1

    for needle in ('refreshTrustSub', 'renderTrustSubHint',
                   "userSelections.purpose === 'trust'",
                   'TRUST_SUB_OF[game.id] === trustKey',
                   'lastTrustFallback', 'TRUST_ALL_IDS', 'trustAll'):
        if needle not in g:
            errors.append('generator.html 缺信任子类逻辑片段：%s' % needle)
            bad += 1

    if "params.get('trust')" not in g:
        errors.append('generator.html 缺 ?trust= URL 参数')
        bad += 1

    blocks_html = _group_blocks(cm)
    for m in re.finditer(_GROUP_RE, blk.group(1)):
        key = m.group(1)
        hblk = blocks_html.get(key)
        if hblk is None:
            errors.append('generator.html 组 %s 在 trust.html 里没有对应分组' % key)
            bad += 1
            continue
        h_lead = re.search(r'<div class="group-lead">(.*?)</div>', hblk, re.S).group(1).strip()
        h_when = re.search(r'<div class="when-box"><b>✅ 什么情况下选它</b><br>(.*?)</div>',
                           hblk, re.S).group(1).strip()
        h_avoid = re.search(r'<div class="avoid-box"><b>⛔ 什么时候别选它</b><br>(.*?)</div>',
                            hblk, re.S).group(1).strip()
        h_pick = re.search(r'🎯 拿不准就先拿：<a href="games/trust/([a-z0-9-]+)\.html"',
                           hblk).group(1)
        h_name = re.search(r'<h3>(.*?)（\d+ 款）</h3>', hblk).group(1).strip()
        for label, gv, hv in (('组名', m.group(2), h_name),
                              ('组导语', m.group(5), h_lead),
                              ('何时选', m.group(6), h_when),
                              ('何时别选', m.group(7), h_avoid),
                              ('首选', m.group(8), h_pick)):
            gv = gv.replace("\\'", "'")
            if gv != hv:
                errors.append('generator.html 组 %s 的%s与 trust.html 不一致：%r != %r'
                              % (key, label, gv, hv))
                bad += 1

    if 'trust.html' not in g:
        errors.append('generator.html 缺信任挑款页入口')
        bad += 1

    print('[41] 生成器信任子类：%d 款 / %d 组；按钮 %d 个；文案与 trust.html 逐字比对 %d 组；异常 %d 项'
          % (len(gen_sub), len(set(gen_sub.values())), len(vals),
             len(re.findall(_GROUP_RE, blk.group(1))), bad))
    return bad
