# -*- coding: utf-8 -*-
"""site_check.py 的第 33 / 34 / 35 项：沟通二级索引 / 沟通挑款反向互链 / 生成器沟通子类。

单独成一个模块，由 site_check.py 在 main() 里 import 调用 —— 保持 site_check.py
本身不继续膨胀（它已经 8 万多字符）。

三项与第 30 / 31 / 32 项（线上）完全同构：
  [33] 沟通二级索引：8 款 data-comm 与目录一致、4 组锚点同源、
       「沟通 ≠ 练说话」边界说明与「沟通不只是这 8 款」跨分类说明必须在场、
       跨分类那 12 款逐一点名、每组款数三处一致、首选真实存在且属于本组
  [34] 沟通挑款反向互链：8 款 md + html 双侧章节齐全、锚点所属组与 data-comm 一致、
       md/html 两侧集合一致、每页 ≥1 条挑款页首页链接
  [35] 生成器沟通子类：4 组定义与 index.html 的 data-comm 逐款同源、
       5 个按钮取值 == 4 个 key + any、refreshCommSub / 目的判定 /
       COMM_SUB_OF[game.id] === commKey / lastCommFallback / COMM_ALL_IDS
       四段逻辑缺一不可、组文案与 comm.html 双向逐字相等、?comm= 参数必须在场

固化原因与第 21 / 24 / 27 / 30 项同型：**新增游戏不会自动归入某一组，
也不会自动进挑款页**；且沟通的分组口径（按「这一局坏在哪一环」）
与协作（练哪种协作）、创意解题（卡在哪一步）、破冰（结束留下什么）、
线上（远程靠什么成立）都不同 —— 这是全库第五套切法，混在一起最容易挑错。
"""
import io
import os
import re

# 跨分类：带「沟通表达」标签但分类不在 communication 的游戏（comm.html 必须逐一点名）
CROSS_COMM = [
    'crazy-kitchen', 'human-knot',                                   # 🤝 协作
    'name-chain', 'human-bingo', 'two-truths-one-lie',
    'explorer-journal', 'line-master', 'celestial-gala',             # 🧊 破冰
    'blind-walk',                                                    # 🔐 信任
    'online-pictionary', 'never-have-i-ever', 'team-quiz',           # 💻 线上
]

# 分组组名（供 README / 挑款页核对用）
COMM_GROUP_NAMES = ['🗣️ 说的人说不清', '🔁 传的人传不准',
                    '🧩 信息凑不齐', '⚖️ 有分歧说不拢']

SECTION_TITLE = '💬 沟通挑款：这一款练的是哪一环'

# 尾部锚点：必须锚到带标签的 <h2>，纯文本「💬 沟通不只是这 8 款」在上一节的
# blockquote 里也出现过一次（经验 98/101）
TAIL = '<h2>💬 沟通不只是这 8 款</h2>'


def _comm_anchor_keys(html):
    return re.findall(r'<div class="group-card" id="g-([a-z]+)">', html)


def _comm_group_blocks(html):
    """返回 {key: 该组的 HTML 段}。"""
    keys = _comm_anchor_keys(html)
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
        r'<a href="games/communication/([a-z0-9-]+)\.html" '
        r'class="card" data-comm="([a-z]+)"', idx))


# ---------------- [33] 沟通二级索引 ----------------
def check_comm_index(errors, TB):
    idx = io.open(os.path.join(TB, 'index.html'), encoding='utf-8').read()
    cm = io.open(os.path.join(TB, 'comm.html'), encoding='utf-8').read()
    rm = io.open(os.path.join(TB, 'README.md'), encoding='utf-8').read()
    bad = 0

    # 1) 目录里的 8 款 == index.html 里带 data-comm 的 8 款
    on_disk = set()
    for f in os.listdir(os.path.join(TB, 'games', 'communication')):
        if f.endswith('.md'):
            on_disk.add(f[:-3])
    tagged = _tagged(idx)
    if set(tagged) != on_disk:
        errors.append('沟通卡片的 data-comm 与目录不一致：缺 %s 多 %s'
                      % (sorted(on_disk - set(tagged)), sorted(set(tagged) - on_disk)))
        bad += 1
    if len(tagged) != 8:
        errors.append('沟通卡片 data-comm 数量 %d != 8' % len(tagged))
        bad += 1

    # 2) 筛选行必须存在，且只在选中沟通分类时出现
    if 'id="comm-filter"' not in idx:
        errors.append('index.html 缺「沟通坏在哪一环」筛选行')
        bad += 1
    # ⚠️ 注意变量名：index.html 用的是 currentFilters（生成器才用 userSelections）
    # ⚠️ 光查函数名不够 —— 函数名在定义处也存在，删掉 toggleFilter 里的调用分支
    #    照样能骗过检查（negative_test_comm.py 用例③就是这么抓出来的漏洞）。
    #    必须连整条分支一起断言。
    for needle in ('resetComm', 'setCommRow', 'currentFilters.comm',
                   "card.getAttribute('data-comm') !== currentFilters.comm",
                   "value === 'communication'",
                   "if (value === 'communication') { setCommRow(true); }",
                   "else { resetComm(); setCommRow(false); }"):
        if needle not in idx:
            errors.append('index.html 缺沟通筛选逻辑片段：%s' % needle)
            bad += 1
    btns = re.findall(r"onclick=\"toggleFilter\('comm', '([a-z]+)', this\)\"", idx)
    if len(btns) != 5 or set(btns) != set(tagged.values()) | set(['all']):
        errors.append('index.html 的 comm 按钮 %s 与分组 %s 不对应'
                      % (sorted(btns), sorted(set(tagged.values()))))
        bad += 1

    # 2b) 沟通网格**不应有** .subhead 小标题 —— 全站只有协作网格（39 款）用小标题
    m_cm = re.search(r'<div class="grid" id="grid-communication">(.*?)\n    </div>', idx, re.S)
    if not m_cm:
        errors.append('index.html 未找到 grid-communication 网格')
        bad += 1
    elif 'class="subhead"' in m_cm.group(1):
        errors.append('index.html 沟通网格不应有小标题（.subhead）—— '
                      '全站只有协作网格用小标题，沟通应与破冰 / 线上网格同款')
        bad += 1
    # 每张卡都要带肌肉标签胶囊
    for gid in sorted(tagged):
        mm = re.search(r'<a href="games/communication/%s\.html" class="card"[^>]*>(.*?)</a>'
                       % re.escape(gid), idx, re.S)
        if not mm:
            errors.append('index.html 缺沟通卡片 %s' % gid)
            bad += 1
            continue
        if 'card-tags' not in mm.group(1):
            errors.append('index.html 沟通卡片 %s 缺肌肉标签胶囊' % gid)
            bad += 1

    # 3) comm.html 的 4 组锚点 == index.html 的 data-comm 取值集合
    anchors = _comm_anchor_keys(cm)
    if set(anchors) != set(tagged.values()):
        errors.append('comm.html 分组锚点 %s 与 index.html data-comm %s 不一致'
                      % (sorted(set(anchors)), sorted(set(tagged.values()))))
        bad += 1
    if len(anchors) != 4:
        errors.append('comm.html 分组数 %d != 4' % len(anchors))
        bad += 1

    # 4) 边界说明必须在挑款页上（这是本次二级索引的核心：把混淆讲清）
    if '「沟通」不等于「练说话」' not in cm:
        errors.append('comm.html 缺「沟通 ≠ 练说话」边界说明')
        bad += 1
    if '沟通不只是这 8 款' not in cm:
        errors.append('comm.html 缺「沟通不只是这 8 款」跨分类说明')
        bad += 1
    for gid in CROSS_COMM:
        if any(('games/%s/%s.html' % (c, gid)) in cm
               for c in ('collaboration', 'icebreaker', 'trust', 'online')):
            continue
        errors.append('comm.html 未列出带「沟通表达」标签的跨分类游戏：%s' % gid)
        bad += 1

    # 5) 每组：首选 + 「什么时候别选它」+ 表格款数与标题一致
    blocks = _comm_group_blocks(cm)
    for key in sorted(anchors):
        blk = blocks[key]
        m = re.search(r'<h3>(.*?)（(\d+) 款）</h3>', blk)
        if not m:
            errors.append('comm.html 组 %s 缺标题款数' % key)
            bad += 1
            continue
        n_title = int(m.group(2))
        rows = re.findall(r'<tr><td><a href="games/communication/([a-z0-9-]+)\.html">', blk)
        if len(rows) != n_title:
            errors.append('comm.html 组 %s 表格 %d 款，标题写 %d 款'
                          % (key, len(rows), n_title))
            bad += 1
        n_card = sum(1 for v in tagged.values() if v == key)
        if n_card != n_title:
            errors.append('comm.html 组 %s 标题写 %d 款，index.html 该组 %d 款'
                          % (key, n_title, n_card))
            bad += 1
        if '什么情况下选它' not in blk or '什么时候别选它' not in blk:
            errors.append('comm.html 组 %s 缺「何时选 / 何时别选」' % key)
            bad += 1
        pick = re.search(r'🎯 拿不准就先拿：<a href="games/communication/([a-z0-9-]+)\.html"', blk)
        if not pick:
            errors.append('comm.html 组 %s 缺组内首选' % key)
            bad += 1
        elif pick.group(1) not in rows:
            errors.append('comm.html 组 %s 的首选 %s 不在本组表格里'
                          % (key, pick.group(1)))
            bad += 1

    # 6) README 已重排为 4 组 + 挑款页入口齐全
    if '沟通挑款指南' not in rm:
        errors.append('README 缺沟通挑款指南入口')
        bad += 1
    for name in COMM_GROUP_NAMES:
        if name not in rm:
            errors.append('README 沟通小节缺分组：%s' % name)
            bad += 1
    for href in ('index.html', 'README.md', 'toolbox/generator.html'):
        if href not in cm:
            errors.append('comm.html 缺相关入口：%s' % href)
            bad += 1

    print('[33] 沟通二级索引：%d 款 / %d 组（%s）；挑款页收录 %d 次；异常 %d 项'
          % (len(tagged), len(anchors),
             ', '.join('%s=%d' % (k, sum(1 for v in tagged.values() if v == k))
                       for k in sorted(set(tagged.values()))),
             rm.count('comm.html'), bad))
    return bad


# ---------------- [34] 沟通挑款反向互链 ----------------
def check_comm_backlinks(errors, TB):
    idx = io.open(os.path.join(TB, 'index.html'), encoding='utf-8').read()
    tagged = _tagged(idx)
    bad = 0
    n_md = n_html = 0
    n_link = 0
    anchors = set()

    for gid in sorted(tagged):
        for ext in ('md', 'html'):
            p = os.path.join(TB, 'games', 'communication', gid + '.' + ext)
            if not os.path.exists(p):
                errors.append('沟通游戏页缺失：%s.%s' % (gid, ext))
                bad += 1
                continue
            t = io.open(p, encoding='utf-8').read()
            if SECTION_TITLE not in t:
                errors.append('%s.%s 缺「沟通挑款」章节' % (gid, ext))
                bad += 1
                continue
            if ext == 'md':
                n_md += 1
                m = re.search(r'\[沟通挑款指南 · [^]]*\]\(\.\./\.\./comm\.html#g-([a-z]+)\)', t)
            else:
                n_html += 1
                m = re.search(r'<a href="\.\./\.\./comm\.html#g-([a-z]+)">沟通挑款指南 · ', t)
            if not m:
                errors.append('%s.%s 缺沟通挑款页锚点链接' % (gid, ext))
                bad += 1
                continue
            n_link += 1
            anchors.add(m.group(1))
            if m.group(1) != tagged[gid]:
                errors.append('%s.%s 的锚点组 %s 与 index.html data-comm %s 不一致'
                              % (gid, ext, m.group(1), tagged[gid]))
                bad += 1
            # 每页至少一条挑款页首页链接（不带锚点）
            home = '](../../comm.html)' if ext == 'md' else 'href="../../comm.html"'
            if home not in t:
                errors.append('%s.%s 缺挑款页首页链接' % (gid, ext))
                bad += 1

    if anchors != set(tagged.values()):
        errors.append('沟通挑款反向互链锚点集合 %s 与分组 %s 不一致'
                      % (sorted(anchors), sorted(set(tagged.values()))))
        bad += 1

    print('[34] 沟通挑款反向互链：md %d 次 / html %d 次，锚点链接 %d 条，分组 %d 个；异常 %d 项'
          % (n_md, n_html, n_link, len(anchors), bad))
    return bad


# ---------------- [35] 生成器沟通子类 ----------------
_GROUP_RE = (
    r"\{ key: '([a-z]+)', name: '([^']*)', short: '([^']*)', n: (\d+),\s*"
    r"lead: '((?:[^'\\]|\\.)*)',\s*"
    r"when: '((?:[^'\\]|\\.)*)',\s*"
    r"avoid: '((?:[^'\\]|\\.)*)',\s*"
    r"pick: '([a-z0-9-]+)',\s*"
    r"ids: \[([^\]]*)\] \}")


def check_generator_comm_sub(errors, TB):
    g = io.open(os.path.join(TB, 'toolbox', 'generator.html'), encoding='utf-8').read()
    cm = io.open(os.path.join(TB, 'comm.html'), encoding='utf-8').read()
    idx = io.open(os.path.join(TB, 'index.html'), encoding='utf-8').read()
    bad = 0

    idx_sub = _tagged(idx)
    blk = re.search(r'var COMM_GROUPS = \[([\s\S]*?)\n\];', g)
    if not blk:
        errors.append('generator.html 缺 COMM_GROUPS 定义')
        return 1
    blocks = re.findall(
        r"\{ key: '([a-z]+)', name: '([^']*)', short: '([^']*)', n: (\d+),", blk.group(1))
    if len(blocks) != 4:
        errors.append('generator.html COMM_GROUPS 组数 %d != 4' % len(blocks))
        bad += 1
    gen_sub = {}
    for m in re.finditer(_GROUP_RE, blk.group(1)):
        key = m.group(1)
        # ⚠️ 捕获组编号：1=key 2=name 3=short 4=n 5=lead 6=when 7=avoid
        #    8=pick 9=ids —— ids 是第 9 组，写成 8 会把「首选」当成「成员」
        ids = [x.strip().strip("'") for x in m.group(9).split(',') if x.strip()]
        for gid in ids:
            if gid in gen_sub:
                errors.append('generator.html 游戏 %s 同时属于多组' % gid)
                bad += 1
            gen_sub[gid] = key
    if set(gen_sub) != set(idx_sub):
        errors.append('generator.html 沟通分组覆盖 %s 与 index.html %s 不一致'
                      % (sorted(set(gen_sub)), sorted(set(idx_sub))))
        bad += 1
    else:
        for gid, sub in idx_sub.items():
            if gen_sub[gid] != sub:
                errors.append('generator.html 游戏 %s 归组 %s 与 index.html %s 不一致'
                              % (gid, gen_sub[gid], sub))
                bad += 1

    # 2) 按钮：4 个组 + 1 个「不限」
    vals = re.findall(r"data-value=\"([a-z]+)\" onclick=\"selectOption\(this, 'commSub'\)\"", g)
    if len(vals) != 5 or set(vals) != set(gen_sub.values()) | set(['any']):
        errors.append('generator.html commSub 按钮取值 %s 与分组 %s 不对应'
                      % (sorted(vals), sorted(set(gen_sub.values()))))
        bad += 1

    # 3) 四段逻辑缺一不可
    for needle in ('refreshCommSub', 'renderCommSubHint',
                   "userSelections.purpose === 'communication'",
                   'COMM_SUB_OF[game.id] === commKey',
                   'lastCommFallback', 'COMM_ALL_IDS', 'commAll'):
        if needle not in g:
            errors.append('generator.html 缺沟通子类逻辑片段：%s' % needle)
            bad += 1

    # 4) URL 参数 ?comm=
    if "params.get('comm')" not in g:
        errors.append('generator.html 缺 ?comm= URL 参数')
        bad += 1

    # 5) 组文案与 comm.html 双向逐字相等（防生成器另写一份）
    #    ⚠️ 必须双向：只查「包含」的话，改写 comm.html 的文案时生成器旧文案仍能被找到
    blocks_html = _comm_group_blocks(cm)
    for m in re.finditer(_GROUP_RE, blk.group(1)):
        key = m.group(1)
        hblk = blocks_html.get(key)
        if hblk is None:
            errors.append('generator.html 组 %s 在 comm.html 里没有对应分组' % key)
            bad += 1
            continue
        h_lead = re.search(r'<div class="group-lead">(.*?)</div>', hblk, re.S).group(1).strip()
        h_when = re.search(r'<div class="when-box"><b>✅ 什么情况下选它</b><br>(.*?)</div>',
                           hblk, re.S).group(1).strip()
        h_avoid = re.search(r'<div class="avoid-box"><b>⛔ 什么时候别选它</b><br>(.*?)</div>',
                            hblk, re.S).group(1).strip()
        h_pick = re.search(r'🎯 拿不准就先拿：<a href="games/communication/([a-z0-9-]+)\.html"',
                           hblk).group(1)
        h_name = re.search(r'<h3>(.*?)（\d+ 款）</h3>', hblk).group(1).strip()
        for label, gv, hv in (('组名', m.group(2), h_name),
                              ('组导语', m.group(5), h_lead),
                              ('何时选', m.group(6), h_when),
                              ('何时别选', m.group(7), h_avoid),
                              ('首选', m.group(8), h_pick)):
            gv = gv.replace("\\'", "'")
            if gv != hv:
                errors.append('generator.html 组 %s 的%s与 comm.html 不一致：%r != %r'
                              % (key, label, gv, hv))
                bad += 1

    # 6) 挑款页须指回生成器的这一能力
    if 'comm.html' not in g:
        errors.append('generator.html 缺沟通挑款页入口')
        bad += 1

    print('[35] 生成器沟通子类：%d 款 / %d 组；按钮 %d 个；文案与 comm.html 逐字比对 %d 组；异常 %d 项'
          % (len(gen_sub), len(set(gen_sub.values())), len(vals), len(blocks), bad))
    return bad
