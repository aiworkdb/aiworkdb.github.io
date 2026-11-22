# -*- coding: utf-8 -*-
"""site_check.py 的第 36 / 37 / 38 项：领导力二级索引 / 挑款反向互链 / 生成器领导力子类。

单独成一个模块，由 site_check.py 在 main() 里 import 调用 —— 保持 site_check.py
本身不继续膨胀。

  [36] 领导力二级索引：6 款 data-lead 与目录一致、3 组锚点同源、
       「领导力 ≠ 有人站出来」边界说明与「领导力不只是这 6 款」跨分类说明必须在场、
       跨分类那 3 款逐一点名、每组款数三处一致、首选真实存在且属于本组
  [37] 领导力挑款反向互链：6 款 md + html 双侧章节齐全、锚点所属组与 data-lead 一致
  [38] 生成器领导力子类：3 组定义与 index.html 的 data-lead 逐款同源、
       4 个按钮取值 == 3 个 key + any、refreshLeadSub / 目的判定 /
       LEAD_SUB_OF[game.id] === leadKey / lastLeadFallback / LEAD_ALL_IDS
       缺一不可、组文案与 lead.html 双向逐字相等、?lead= 参数必须在场

固化原因与第 21 / 24 / 27 / 30 / 33 项同型：**新增游戏不会自动归入某一组，
也不会自动进挑款页**；且领导力的分组口径（按「带人这件事卡在哪一层」）
与协作（练哪种协作）、创意解题（卡在哪一步）、破冰（结束留下什么）、
线上（远程靠什么成立）、沟通（这一局坏在哪一环）都不同 —— 这是全库第六套切法。
"""
import io
import os
import re

# 跨分类：带「领导力」标签但分类不在 leadership 的游戏（lead.html 必须逐一点名）
CROSS_LEAD = ['space-miners', 'virus-outbreak', 'kaiju-defenders']   # 🤝 协作

LEAD_GROUP_NAMES = ['🧭 定方向与拍板', '🔑 授权与放手', '📣 不带权也能带']

SECTION_TITLE = '👑 领导力挑款：这一款练的是哪一层'

# 尾部锚点：必须锚到带标签的 <h2>（纯文本在上一节 blockquote 里也出现过一次）
TAIL = '<h2>👑 领导力不只是这 6 款</h2>'


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
        r'<a href="games/leadership/([a-z0-9-]+)\.html" '
        r'class="card" data-lead="([a-z]+)"', idx))


# ---------------- [36] 领导力二级索引 ----------------
def check_lead_index(errors, TB):
    idx = io.open(os.path.join(TB, 'index.html'), encoding='utf-8').read()
    cm = io.open(os.path.join(TB, 'lead.html'), encoding='utf-8').read()
    rm = io.open(os.path.join(TB, 'README.md'), encoding='utf-8').read()
    bad = 0

    on_disk = set()
    for f in os.listdir(os.path.join(TB, 'games', 'leadership')):
        if f.endswith('.md'):
            on_disk.add(f[:-3])
    tagged = _tagged(idx)
    if set(tagged) != on_disk:
        errors.append('领导力卡片的 data-lead 与目录不一致：缺 %s 多 %s'
                      % (sorted(on_disk - set(tagged)), sorted(set(tagged) - on_disk)))
        bad += 1
    if len(tagged) != 6:
        errors.append('领导力卡片 data-lead 数量 %d != 6' % len(tagged))
        bad += 1

    if 'id="lead-filter"' not in idx:
        errors.append('index.html 缺「带人卡在哪一层」筛选行')
        bad += 1
    # ⚠️ 光查函数名不够（函数名在定义处也存在），必须连 toggleFilter 里的整条调用分支一起断言
    for needle in ('resetLead', 'setLeadRow', 'currentFilters.lead',
                   "card.getAttribute('data-lead') !== currentFilters.lead",
                   "value === 'leadership'",
                   "if (value === 'leadership') { setLeadRow(true); }",
                   "else { resetLead(); setLeadRow(false); }"):
        if needle not in idx:
            errors.append('index.html 缺领导力筛选逻辑片段：%s' % needle)
            bad += 1
    btns = re.findall(r"onclick=\"toggleFilter\('lead', '([a-z]+)', this\)\"", idx)
    if len(btns) != 4 or set(btns) != set(tagged.values()) | set(['all']):
        errors.append('index.html 的 lead 按钮 %s 与分组 %s 不对应'
                      % (sorted(btns), sorted(set(tagged.values()))))
        bad += 1

    m_le = re.search(r'<div class="grid" id="grid-leadership">(.*?)\n    </div>', idx, re.S)
    if not m_le:
        errors.append('index.html 未找到 grid-leadership 网格')
        bad += 1
    elif 'class="subhead"' in m_le.group(1):
        errors.append('index.html 领导力网格不应有小标题（.subhead）—— '
                      '全站只有协作网格用小标题')
        bad += 1
    for gid in sorted(tagged):
        mm = re.search(r'<a href="games/leadership/%s\.html" class="card"[^>]*>(.*?)</a>'
                       % re.escape(gid), idx, re.S)
        if not mm:
            errors.append('index.html 缺领导力卡片 %s' % gid)
            bad += 1
        elif 'card-tags' not in mm.group(1):
            errors.append('index.html 领导力卡片 %s 缺肌肉标签胶囊' % gid)
            bad += 1

    anchors = _anchor_keys(cm)
    if set(anchors) != set(tagged.values()):
        errors.append('lead.html 分组锚点 %s 与 index.html data-lead %s 不一致'
                      % (sorted(set(anchors)), sorted(set(tagged.values()))))
        bad += 1
    if len(anchors) != 3:
        errors.append('lead.html 分组数 %d != 3' % len(anchors))
        bad += 1

    if '「领导力」不等于「有人站出来」' not in cm:
        errors.append('lead.html 缺「领导力 ≠ 有人站出来」边界说明')
        bad += 1
    if '领导力不只是这 6 款' not in cm:
        errors.append('lead.html 缺「领导力不只是这 6 款」跨分类说明')
        bad += 1
    for gid in CROSS_LEAD:
        if ('games/collaboration/%s.html' % gid) not in cm:
            errors.append('lead.html 未列出带「领导力」标签的跨分类游戏：%s' % gid)
            bad += 1

    blocks = _group_blocks(cm)
    for key in sorted(anchors):
        blk = blocks[key]
        m = re.search(r'<h3>(.*?)（(\d+) 款）</h3>', blk)
        if not m:
            errors.append('lead.html 组 %s 缺标题款数' % key)
            bad += 1
            continue
        n_title = int(m.group(2))
        rows = re.findall(r'<tr><td><a href="games/leadership/([a-z0-9-]+)\.html">', blk)
        if len(rows) != n_title:
            errors.append('lead.html 组 %s 表格 %d 款，标题写 %d 款'
                          % (key, len(rows), n_title))
            bad += 1
        n_card = sum(1 for v in tagged.values() if v == key)
        if n_card != n_title:
            errors.append('lead.html 组 %s 标题写 %d 款，index.html 该组 %d 款'
                          % (key, n_title, n_card))
            bad += 1
        if '什么情况下选它' not in blk or '什么时候别选它' not in blk:
            errors.append('lead.html 组 %s 缺「何时选 / 何时别选」' % key)
            bad += 1
        pick = re.search(r'🎯 拿不准就先拿：<a href="games/leadership/([a-z0-9-]+)\.html"', blk)
        if not pick:
            errors.append('lead.html 组 %s 缺组内首选' % key)
            bad += 1
        elif pick.group(1) not in rows:
            errors.append('lead.html 组 %s 的首选 %s 不在本组表格里' % (key, pick.group(1)))
            bad += 1

    if '领导力挑款指南' not in rm:
        errors.append('README 缺领导力挑款指南入口')
        bad += 1
    for name in LEAD_GROUP_NAMES:
        if name not in rm:
            errors.append('README 领导力小节缺分组：%s' % name)
            bad += 1
    for href in ('index.html', 'README.md', 'toolbox/generator.html'):
        if href not in cm:
            errors.append('lead.html 缺相关入口：%s' % href)
            bad += 1

    print('[36] 领导力二级索引：%d 款 / %d 组（%s）；挑款页收录 %d 次；异常 %d 项'
          % (len(tagged), len(anchors),
             ', '.join('%s=%d' % (k, sum(1 for v in tagged.values() if v == k))
                       for k in sorted(set(tagged.values()))),
             rm.count('lead.html'), bad))
    return bad


# ---------------- [37] 领导力挑款反向互链 ----------------
def check_lead_backlinks(errors, TB):
    idx = io.open(os.path.join(TB, 'index.html'), encoding='utf-8').read()
    tagged = _tagged(idx)
    bad = 0
    n_md = n_html = n_link = 0
    anchors = set()

    for gid in sorted(tagged):
        for ext in ('md', 'html'):
            p = os.path.join(TB, 'games', 'leadership', gid + '.' + ext)
            if not os.path.exists(p):
                errors.append('领导力游戏页缺失：%s.%s' % (gid, ext))
                bad += 1
                continue
            t = io.open(p, encoding='utf-8').read()
            if SECTION_TITLE not in t:
                errors.append('%s.%s 缺「领导力挑款」章节' % (gid, ext))
                bad += 1
                continue
            if ext == 'md':
                n_md += 1
                m = re.search(r'\[领导力挑款指南 · [^]]*\]\(\.\./\.\./lead\.html#g-([a-z]+)\)', t)
            else:
                n_html += 1
                m = re.search(r'<a href="\.\./\.\./lead\.html#g-([a-z]+)">领导力挑款指南 · ', t)
            if not m:
                errors.append('%s.%s 缺领导力挑款页锚点链接' % (gid, ext))
                bad += 1
                continue
            n_link += 1
            anchors.add(m.group(1))
            if m.group(1) != tagged[gid]:
                errors.append('%s.%s 的锚点组 %s 与 index.html data-lead %s 不一致'
                              % (gid, ext, m.group(1), tagged[gid]))
                bad += 1
            home = '](../../lead.html)' if ext == 'md' else 'href="../../lead.html"'
            if home not in t:
                errors.append('%s.%s 缺挑款页首页链接' % (gid, ext))
                bad += 1

    if anchors != set(tagged.values()):
        errors.append('领导力挑款反向互链锚点集合 %s 与分组 %s 不一致'
                      % (sorted(anchors), sorted(set(tagged.values()))))
        bad += 1

    print('[37] 领导力挑款反向互链：md %d 次 / html %d 次，锚点链接 %d 条，分组 %d 个；异常 %d 项'
          % (n_md, n_html, n_link, len(anchors), bad))
    return bad


# ---------------- [38] 生成器领导力子类 ----------------
_GROUP_RE = (
    r"\{ key: '([a-z]+)', name: '([^']*)', short: '([^']*)', n: (\d+),\s*"
    r"lead: '((?:[^'\\]|\\.)*)',\s*"
    r"when: '((?:[^'\\]|\\.)*)',\s*"
    r"avoid: '((?:[^'\\]|\\.)*)',\s*"
    r"pick: '([a-z0-9-]+)',\s*"
    r"ids: \[([^\]]*)\] \}"
)


def check_generator_lead_sub(errors, TB):
    g = io.open(os.path.join(TB, 'toolbox', 'generator.html'), encoding='utf-8').read()
    cm = io.open(os.path.join(TB, 'lead.html'), encoding='utf-8').read()
    idx = io.open(os.path.join(TB, 'index.html'), encoding='utf-8').read()
    bad = 0

    idx_sub = _tagged(idx)
    blk = re.search(r'var LEAD_GROUPS = \[([\s\S]*?)\n\];', g)
    if not blk:
        errors.append('generator.html 缺 LEAD_GROUPS 定义')
        return 1
    if len(re.findall(r"\{ key: '([a-z]+)', name: '([^']*)', short: '([^']*)', n: (\d+),",
                      blk.group(1))) != 3:
        errors.append('generator.html LEAD_GROUPS 组数 != 3')
        bad += 1
    gen_sub = {}
    for m in re.finditer(_GROUP_RE, blk.group(1)):
        # 捕获组：1=key 2=name 3=short 4=n 5=lead 6=when 7=avoid 8=pick 9=ids
        ids = [x.strip().strip("'") for x in m.group(9).split(',') if x.strip()]
        for gid in ids:
            if gid in gen_sub:
                errors.append('generator.html 游戏 %s 同时属于多组' % gid)
                bad += 1
            gen_sub[gid] = m.group(1)
    if set(gen_sub) != set(idx_sub):
        errors.append('generator.html 领导力分组覆盖 %s 与 index.html %s 不一致'
                      % (sorted(set(gen_sub)), sorted(set(idx_sub))))
        bad += 1
    else:
        for gid, sub in idx_sub.items():
            if gen_sub[gid] != sub:
                errors.append('generator.html 游戏 %s 归组 %s 与 index.html %s 不一致'
                              % (gid, gen_sub[gid], sub))
                bad += 1

    vals = re.findall(r"data-value=\"([a-z]+)\" onclick=\"selectOption\(this, 'leadSub'\)\"", g)
    if len(vals) != 4 or set(vals) != set(gen_sub.values()) | set(['any']):
        errors.append('generator.html leadSub 按钮取值 %s 与分组 %s 不对应'
                      % (sorted(vals), sorted(set(gen_sub.values()))))
        bad += 1

    for needle in ('refreshLeadSub', 'renderLeadSubHint',
                   "userSelections.purpose === 'leadership'",
                   'LEAD_SUB_OF[game.id] === leadKey',
                   'lastLeadFallback', 'LEAD_ALL_IDS', 'leadAll'):
        if needle not in g:
            errors.append('generator.html 缺领导力子类逻辑片段：%s' % needle)
            bad += 1

    if "params.get('lead')" not in g:
        errors.append('generator.html 缺 ?lead= URL 参数')
        bad += 1

    blocks_html = _group_blocks(cm)
    for m in re.finditer(_GROUP_RE, blk.group(1)):
        key = m.group(1)
        hblk = blocks_html.get(key)
        if hblk is None:
            errors.append('generator.html 组 %s 在 lead.html 里没有对应分组' % key)
            bad += 1
            continue
        h_lead = re.search(r'<div class="group-lead">(.*?)</div>', hblk, re.S).group(1).strip()
        h_when = re.search(r'<div class="when-box"><b>✅ 什么情况下选它</b><br>(.*?)</div>',
                           hblk, re.S).group(1).strip()
        h_avoid = re.search(r'<div class="avoid-box"><b>⛔ 什么时候别选它</b><br>(.*?)</div>',
                            hblk, re.S).group(1).strip()
        h_pick = re.search(r'🎯 拿不准就先拿：<a href="games/leadership/([a-z0-9-]+)\.html"',
                           hblk).group(1)
        h_name = re.search(r'<h3>(.*?)（\d+ 款）</h3>', hblk).group(1).strip()
        for label, gv, hv in (('组名', m.group(2), h_name),
                              ('组导语', m.group(5), h_lead),
                              ('何时选', m.group(6), h_when),
                              ('何时别选', m.group(7), h_avoid),
                              ('首选', m.group(8), h_pick)):
            gv = gv.replace("\\'", "'")
            if gv != hv:
                errors.append('generator.html 组 %s 的%s与 lead.html 不一致：%r != %r'
                              % (key, label, gv, hv))
                bad += 1

    if 'lead.html' not in g:
        errors.append('generator.html 缺领导力挑款页入口')
        bad += 1

    print('[38] 生成器领导力子类：%d 款 / %d 组；按钮 %d 个；文案与 lead.html 逐字比对 %d 组；异常 %d 项'
          % (len(gen_sub), len(set(gen_sub.values())), len(vals),
             len(re.findall(_GROUP_RE, blk.group(1))), bad))
    return bad
