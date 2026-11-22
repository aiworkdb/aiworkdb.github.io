# -*- coding: utf-8 -*-
"""协作类二级索引 / 挑款降噪（2026-10-23 自动化第三十七次）

背景：协作占全库 46%（39/85），index.html 的协作网格 118 行、是全站最大容器
（均值 44 行）。教练按目的筛到「协作」后面对 39 张卡，等于没筛。

做法：把 39 款按「这个游戏到底在练哪种协作」切成 6 组，
  1) index.html 协作网格内加 6 个二级小标题 + 卡片 data-sub + 子类筛选行
  2) 新建 collab.html 挑款专页（30 秒决策表 + 6 组详解 + 每组首选 / 何时别选）
  3) README.md 协作表按组重排并加组标题行
  4) 39 款数字与分组口径全部从 README / index.html 现成数据复用，不另写一份

可重复执行：所有替换点都 assert 锚点唯一。
"""
import io
import os
import re

TB = os.path.dirname(os.path.abspath(__file__))

# ---------------- 分组定义（顺序即排序顺序） ----------------
GROUPS = [
    {
        'key': 'physical', 'icon': '🪢', 'name': '身体默契 · 一动就知道',
        'tag': '不用讲道理，身体会先把问题暴露出来',
        'lead': '不用讲道理，身体会先把问题暴露出来——全组被「卡住」的那一下，就是协作最真实的样子。',
        'when': '开场或破冰后的第一个协作环节 / 只有 20–45 分钟 / 没道具没桌子 / 队伍还互相不认识。',
        'avoid': '想复盘「资源怎么分」「信息怎么传」这类组织问题时别选：它照出来的是身体同步，迁移不到流程上。',
        'pick': 'human-knot',
        'ids': ['human-knot', 'eyebrow-stick', 'ball-relay', 'wind-fire-wheel', 'body-letters'],
    },
    {
        'key': 'pipeline', 'icon': '🍳', 'name': '瓶颈与流水线 · 卡在哪一工位',
        'tag': '交付是一串环节，堵点往往不是最弱的那一个',
        'lead': '交付是一串环节，不是一堆人。任一工位堵住全队都堵——而堵点往往不是最弱的那一个。',
        'when': '「每个人都很忙，整体却不前进」/ 刚做完一轮交付想复盘流程 / 要讲局部最优害全局。',
        'avoid': '少于 4 人（凑不出多个工位），或真正的问题是「人不愿意开口」——那是沟通类，不是这一类。',
        'pick': 'crazy-kitchen',
        'ids': ['crazy-kitchen', 'team-chef', 'monster-chef', 'star-rail-legends',
                'lychee-express', 'steam-revolution'],
    },
    {
        'key': 'resource', 'icon': '🧭', 'name': '资源与取舍 · 不够分的时候怎么办',
        'tag': '总量固定，真正的分歧是「先保哪一个」',
        'lead': '总量是固定的，给这边就没那边。真正的分歧不在「怎么分」，在「先保哪一个」。',
        'when': '要练取舍 / 长期主义 vs 救火 / 跨部门抢资源 / 预算被砍之后的优先级共识。',
        'avoid': '团队还互相不熟（没信任时取舍会变成吵架），或只想做一场轻松的活动。',
        'pick': 'island-survival',
        'ids': ['island-survival', 'space-miners', 'abyss-dive', 'doomsday-vault',
                'kaiju-defenders', 'destined-one', 'space-diner-escape', 'star-pioneers',
                'mars-colony'],
    },
    {
        'key': 'info', 'icon': '🔦', 'name': '信息不对称 · 谁手里有那块拼图',
        'tag': '谁的拼图都不全，不互通就一定做不成',
        'lead': '真相分散在每个人手里，谁的都不全。不互通就一定做不成——而「我以为对方知道」是最贵的错觉。',
        'when': '跨职能团队 / 出过「我以为你处理了」这类事 / 要讲信息孤岛与主动同步。',
        'avoid': '彼此不信任时别选：信息会被当成筹码藏着，复盘会跑偏到人际关系上。',
        'pick': 'data-detective',
        'ids': ['virus-outbreak', 'secret-mission', 'gene-therapy', 'ghost-castle',
                'stellar-medics', 'expedition-33', 'data-detective'],
    },
    {
        'key': 'role', 'icon': '🎭', 'name': '角色互补 · 不一样才需要配合',
        'tag': '能力不同才需要配合，练的是认别人的账',
        'lead': '每人能力不同、视角不同，谁都没法单独完成。练的是「认别人的账」和「把后背交给专才」。',
        'when': '职能差异大的团队（研发 / 销售 / 运营）/ 要练传帮带 / 想讲「能者多劳」是怎么拖垮团队的。',
        'avoid': '少于 3 人（角色凑不齐），或只想做一场所有人同质参与的活动。',
        'pick': 'magic-academy',
        'ids': ['magic-academy', 'frieren-journey', 'wukong-quest', 'demon-slayer-train',
                'mythic-rift', 'jujutsu-united', 'stellar-lighthouse', 'solo-hunter-squad'],
    },
    {
        'key': 'whole', 'icon': '🏗️', 'name': '共享总账 · 一荣俱荣的那本看不见的账',
        'tag': '各忙各的，头顶却挂着一本共享的账',
        'lead': '各小组都在忙自己的活，头顶却挂着一本全队共享的账（健康度 / 繁荣指数 / 结界能量 / 经验沉淀）。它掉下去，没人能单独赢。',
        'when': '要讲部门墙 / 局部最优害全局 / 组织健康度 / 长期主义；其中未来城市建造师、丝绸之路支持 6–12 人分多组同时开局。',
        'avoid': '只有一个小组（这一类的张力全来自组与组之间），或时间少于 45 分钟。',
        'pick': 'future-city-builder',
        'ids': ['loop-dungeon', 'huntrix-honmoon', 'future-city-builder', 'silk-road'],
    },
]

# 决策表：你现在的麻烦 → 去哪一组 → 直接拿这款
DECIDE = [
    ('要开场，只有 20–45 分钟，手上没道具', 'physical', 'human-knot'),
    ('每个人都很忙，整体却不往前走', 'pipeline', 'crazy-kitchen'),
    ('资源 / 预算不够分，谁都想先保自己那份', 'resource', 'island-survival'),
    ('刚出过「我以为你知道」这类事', 'info', 'data-detective'),
    ('职能差得远，各干各的，谁也接不上谁', 'role', 'magic-academy'),
    ('各部门都把自己做到最好，公司整体却变差', 'whole', 'future-city-builder'),
]

PITFALL = [
    ('想练「说清楚 / 问明白」别在协作里找',
     '协作 39 款里只有「🔦 信息不对称」这组跟沟通沾边，其余练的是配合。真要练表达，去 💬 沟通表达（8 款）。'),
    ('人数少于 4 人时，两类开不起来',
     '🍳 瓶颈与流水线（要多个工位）和 🏗️ 共享总账（要多个小组）都靠「组」产生张力，人少了只能从 🪢 / 🧭 / 🔦 / 🎭 四组里挑。'),
    ('赶时间先看前两组',
     '🪢 身体默契（20–45 min）和 🍳 瓶颈与流水线（30–90 min）里有多款 45 分钟以内的；🧭 / 🎭 / 🏗️ 三组最短也要 45 min。'),
]

# 配色：hue 127（全站 108 页中 112↔142 之间 30° 空档的中点），HSL 单色相派生
C = {
    'primary': '#3b9c46', 'mid': '#54b65f', 'light': '#7cde88',
    'bg': '#071809', 'container': '#0d210f', 'gridbg': '#061308',
    'border': '#2b6431', 'text': '#cfe2d1', 'muted': '#96b699',
    'quote': '#19341c',
}


# ---------------- 工具 ----------------
def read(p):
    return io.open(p, encoding='utf-8').read()


def is_crlf(p):
    raw = open(p, 'rb').read()
    return raw.count(b'\r\n') * 2 > raw.count(b'\n')


def write(p, text, crlf=None):
    if crlf is None:
        crlf = is_crlf(p) if os.path.exists(p) else True
    if crlf:
        text = text.replace('\r\n', '\n').replace('\n', '\r\n')
    io.open(p, 'w', encoding='utf-8', newline='').write(text)


def rep(text, old, new, what):
    """经验 87：整块替换前必须断言锚点唯一且命中。"""
    assert text.count(old) == 1, '锚点不唯一(%d)或未命中: %s' % (text.count(old), what)
    return text.replace(old, new)


def grid_block(h, gid):
    """返回 (开标签含 '>' 之前的内容, 网格内部内容, 收尾 '</div>' 起的内容)。

    注意：head 必须保留完整的开标签（含 id 属性与 '>'）—— 经验 88 同型，
    切块时吃掉属性会静默毁掉 id，第 3/5 项检查会把整个网格判为不存在。
    """
    s = h.find('id="%s"' % gid)
    assert s > 0, '未找到 ' + gid
    gt = h.find('>', s) + 1
    depth, i = 1, gt
    pat = re.compile(r'<div\b|</div>')
    while depth > 0:
        m = pat.search(h, i)
        assert m, 'grid %s 未闭合' % gid
        depth += 1 if m.group().startswith('<div') else -1
        i = m.end()
    end = i - len('</div>')
    return h[:gt], h[gt:end], h[end:]


# ---------------- 采集现成数据（一律复用，不另写） ----------------
def collect():
    """从 README.md 取 名称/人数/时长，从 index.html 取一句话描述。"""
    rm = read(os.path.join(TB, 'README.md'))
    sec = rm.split('#### 🤝 团队协作（collaboration）')[1].split('#### 🔐')[0]
    meta = {}
    for m in re.finditer(
            r'\|\s*\[([^\]]+)\]\(games/collaboration/([a-z0-9-]+)\.md\)\s*\|'
            r'\s*([^|]*?)\s*\|\s*([^|]*?)\s*\|\s*([^|]*?)\s*\|', sec):
        meta[m.group(2)] = {
            'name': m.group(1), 'form': m.group(3),
            'people': m.group(4), 'dur': m.group(5),
        }
    idx = read(os.path.join(TB, 'index.html'))
    for m in re.finditer(
            r'<a href="games/collaboration/([a-z0-9-]+)\.html" class="card"[^>]*>'
            r'(.*?)</a>', idx, re.S):
        gid = m.group(1)
        if gid not in meta:
            continue
        d = re.search(r'class="card-desc">(.*?)</div>', m.group(2), re.S)
        t = re.search(r'class="card-title">(.*?)</div>', m.group(2), re.S)
        meta[gid]['desc'] = d.group(1).strip() if d else ''
        meta[gid]['title'] = t.group(1).strip() if t else meta[gid]['name']
    return meta


# ---------------- 1. index.html ----------------
SUBHEAD_HTML = ('      <div class="subhead" data-sub="%s">%s %s '
                '<span class="sub-n">（%d 款 · %s）</span></div>\n')


def patch_index(meta):
    p = os.path.join(TB, 'index.html')
    h = read(p)
    if 'class="subhead"' in h:      # 幂等：已打过补丁就跳过，避免重复插入
        print('index.html 已含二级分组，跳过')
        return

    # 1a. CSS
    h = rep(h,
            '    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px; }\n',
            '    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px; }\n'
            '    .subhead { grid-column: 1 / -1; font-weight: 600; font-size: 0.94em; color: #1a1a2e; margin: 14px 0 -6px; padding-bottom: 7px; border-bottom: 1px dashed #d3d9e6; }\n'
            '    .subhead:first-child { margin-top: 0; }\n'
            '    .subhead .sub-n { font-weight: 400; font-size: 0.88em; color: #6b7280; }\n',
            'CSS .subhead')

    # 1b. 协作网格：重排 + data-sub + 二级小标题
    head, body, tail = grid_block(h, 'grid-collaboration')
    cards = {}
    for m in re.finditer(r'      <a href="games/collaboration/([a-z0-9-]+)\.html"'
                         r' class="card"(.*?)</a>\n', body, re.S):
        cards[m.group(1)] = m.group(0)
    assert len(cards) == 39, '协作卡片数 %d != 39' % len(cards)
    assigned = [gid for g in GROUPS for gid in g['ids']]
    assert sorted(assigned) == sorted(cards), '分组与卡片集合不一致: %s' % (
        set(assigned) ^ set(cards))
    assert len(assigned) == len(set(assigned)), '分组内有重复款'

    assert head.rstrip().endswith('id="grid-collaboration">'), '开标签被切坏：%r' % head[-60:]

    new_body = ''
    for g in GROUPS:
        new_body += SUBHEAD_HTML % (g['key'], g['icon'], g['name'],
                                    len(g['ids']), g['tag'])
        for gid in g['ids']:
            c = cards[gid]
            c2 = c.replace(' class="card" data-people=',
                           ' class="card" data-sub="%s" data-people=' % g['key'], 1)
            assert c2 != c, 'data-sub 未插入: ' + gid
            new_body += c2
    h = head + '\n' + new_body + tail

    # 1c. 分类标题加挑款入口
    h = rep(h,
            '<div style="font-weight:600;color:#555;margin:18px 0 10px;">🤝 团队协作（collaboration）</div>',
            '<div style="font-weight:600;color:#555;margin:18px 0 10px;">🤝 团队协作（collaboration）'
            ' <span style="font-weight:400;">· 39 款先看 <a href="collab.html" style="color:#3366cc;">挑款指南</a>'
            '，或直接用下面的「协作子类」筛</span></div>',
            '协作分类标题')

    # 1d. 子类筛选行
    h = rep(h,
            '    <div class="filter-group">\n      <span class="filter-label">人数：</span>',
            '    <div class="filter-group" id="sub-filter" style="display:none;">\n'
            '      <span class="filter-label">协作子类：</span>\n'
            '      <button class="filter-btn active" onclick="toggleFilter(\'sub\', \'all\', this)">全部</button>\n'
            + ''.join('      <button class="filter-btn" onclick="toggleFilter(\'sub\', \'%s\', this)">%s %s</button>\n'
                      % (g['key'], g['icon'], g['name'].split(' · ')[0]) for g in GROUPS)
            + '    </div>\n'
            '    <div class="filter-group">\n      <span class="filter-label">人数：</span>',
            '子类筛选行')

    # 1e. JS：状态 + 联动 + 子类过滤 + 小标题显隐
    h = rep(h,
            "var currentFilters = {\n  category: 'all',\n  people: 'all',\n  duration: 'all'\n};",
            "var currentFilters = {\n  category: 'all',\n  people: 'all',\n  duration: 'all',\n  sub: 'all'\n};\n\n"
            "// 协作 39 款占全库 46%，单靠分类筛完还是 39 张卡 —— 子类只在选中协作时出现\n"
            "function setSubRow(on) {\n"
            "  var row = document.getElementById('sub-filter');\n"
            "  if (row) { row.style.display = on ? '' : 'none'; }\n"
            "}\n\n"
            "function resetSub() {\n"
            "  currentFilters.sub = 'all';\n"
            "  var row = document.getElementById('sub-filter');\n"
            "  if (!row) { return; }\n"
            "  row.querySelectorAll('.filter-btn').forEach(function(b) {\n"
            "    if (b.textContent === '全部') { b.classList.add('active'); }\n"
            "    else { b.classList.remove('active'); }\n"
            "  });\n"
            "}",
            'JS currentFilters')

    h = rep(h,
            "  // 更新按钮样式\n  var filterGroup = btn.parentElement;",
            "  // 切走协作时把子类筛选项一并复位，否则下次再点协作会带着上次的条件\n"
            "  if (type === 'category') {\n"
            "    if (value !== 'collaboration') { resetSub(); setSubRow(false); }\n"
            "    else { setSubRow(true); }\n"
            "  }\n\n"
            "  // 更新按钮样式\n  var filterGroup = btn.parentElement;",
            'JS toggleFilter 联动')

    h = rep(h,
            "      // 人数筛选\n",
            "      // 协作子类筛选（仅协作分类下的 6 组）\n"
            "      if (visible && currentFilters.sub !== 'all') {\n"
            "        if (card.getAttribute('data-sub') !== currentFilters.sub) {\n"
            "          visible = false;\n"
            "        }\n"
            "      }\n\n"
            "      // 人数筛选\n",
            'JS 子类过滤')

    h = rep(h,
            "    // 找到grid的标题（前一个div）",
            "    // 子类小标题：该组一张卡都不显示时，小标题也要跟着消失\n"
            "    grid.querySelectorAll('.subhead').forEach(function(sh) {\n"
            "      var key = sh.getAttribute('data-sub');\n"
            "      var any = false;\n"
            "      grid.querySelectorAll('.card[data-sub=\"' + key + '\"]').forEach(function(c) {\n"
            "        if (c.style.display !== 'none') { any = true; }\n"
            "      });\n"
            "      sh.style.display = any ? '' : 'none';\n"
            "    });\n\n"
            "    // 找到grid的标题（前一个div）",
            'JS 小标题显隐')

    # 1f. 首屏胶囊
    h = rep(h,
            '<a href="play/tools/plan-generator/" class="res-chip">⚡ 现场临时只要几个游戏（T1 快速版）</a>',
            '<a href="play/tools/plan-generator/" class="res-chip">⚡ 现场临时只要几个游戏（T1 快速版）</a>\n'
            '        <a href="collab.html" class="res-chip">🤝 协作有 39 款，帮我挑</a>',
            '首屏胶囊')

    write(p, h)
    print('index.html 已更新：6 组 / %d 款 / 子类筛选行 / 首屏入口' % len(assigned))


# ---------------- 2. collab.html ----------------
CSS = """
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.6; color: %(text)s;
        background: linear-gradient(135deg, %(bg)s 0%%, #0a1f0d 55%%, #103018 100%%);
        padding: 20px;
    }
    .container {
        max-width: 1100px; margin: 0 auto; background: %(container)s;
        border-radius: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.7);
        overflow: hidden; border: 1px solid %(border)s;
    }
    .header {
        background: linear-gradient(135deg, %(primary)s 0%%, %(mid)s 45%%, %(light)s 100%%);
        color: #f2fbf3; padding: 40px; text-align: center;
    }
    .header h1 { font-size: 2.1em; margin-bottom: 10px; text-shadow: 2px 2px 6px rgba(0,0,0,0.5); }
    .header .subtitle { font-size: 1.05em; opacity: 0.96; }
    .header .tag {
        display: inline-block; margin-top: 14px; padding: 6px 18px;
        background: rgba(0,0,0,0.32); border-radius: 20px; font-size: 0.9em; border: 1px solid %(light)s;
    }
    .info-grid {
        display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 20px; padding: 30px; background: %(gridbg)s;
    }
    .info-card {
        background: %(container)s; padding: 20px; border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.4); text-align: center; border: 1px solid %(border)s;
    }
    .info-card .icon { font-size: 2em; margin-bottom: 8px; }
    .info-card .label { font-size: 0.9em; color: %(muted)s; }
    .info-card .value { font-size: 1.05em; font-weight: bold; color: %(text)s; }
    .section { padding: 30px 40px; }
    .section h2 {
        color: %(light)s; border-left: 5px solid %(primary)s; padding-left: 15px;
        margin-bottom: 20px; font-size: 1.55em;
    }
    .section h3 { color: %(mid)s; margin: 22px 0 10px; font-size: 1.18em; }
    .section p, .section li { color: %(text)s; margin-bottom: 10px; }
    .section ul, .section ol { padding-left: 25px; }
    .data-table {
        width: 100%%; border-collapse: collapse; margin-top: 15px;
        background: %(gridbg)s; border-radius: 10px; overflow: hidden;
    }
    .data-table th { background: %(primary)s; color: #f2fbf3; padding: 12px; text-align: left; font-size: 0.95em; }
    .data-table td { padding: 10px 12px; border-top: 1px solid %(border)s; color: %(text)s; font-size: 0.92em; }
    .data-table tr:nth-child(even) { background: %(container)s; }
    .group-card {
        background: %(container)s; border: 1px solid %(border)s; border-radius: 12px;
        padding: 22px 24px; margin-top: 18px;
    }
    .group-card h3 { margin-top: 0; font-size: 1.2em; color: %(light)s; }
    .group-lead { font-size: 0.96em; color: %(text)s; margin-bottom: 14px; }
    .when-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 14px; margin-bottom: 16px; }
    .when-box, .avoid-box { border-radius: 10px; padding: 14px 16px; font-size: 0.92em; }
    .when-box { background: %(quote)s; border: 1px solid %(border)s; }
    .avoid-box { background: #2a1410; border: 1px solid #7a3a2a; }
    .when-box b { color: %(light)s; }
    .avoid-box b { color: #e8917a; }
    .pick {
        display: inline-block; margin-bottom: 14px; padding: 8px 16px; border-radius: 20px;
        background: %(primary)s; color: #0b1a0c; font-size: 0.92em; font-weight: 600;
    }
    .flow-box {
        background: %(quote)s; border: 1px dashed %(mid)s; border-radius: 12px;
        padding: 20px; margin-top: 15px; font-size: 0.95em; color: %(text)s;
    }
    .flow-box pre { white-space: pre-wrap; margin: 0; font-family: inherit; color: inherit; line-height: 1.9; }
    blockquote {
        background: %(quote)s; border-left: 4px solid %(light)s; border-radius: 8px;
        padding: 14px 18px; margin: 14px 0; color: %(text)s; font-size: 0.95em;
    }
    a { color: %(light)s; }
    .footer {
        background: %(gridbg)s; color: %(muted)s; text-align: center; padding: 25px;
        font-size: 0.9em; border-top: 1px solid %(border)s;
    }
    .footer a { color: %(light)s; }
    .back-link {
        display: inline-block; margin: 8px 6px 0; padding: 8px 20px;
        background: %(primary)s; color: #0b1a0c; text-decoration: none; border-radius: 20px; font-size: 0.9em;
    }
    .back-link:hover { background: %(light)s; }
</style>
""" % C


def build_collab_html(meta):
    parts = []
    a = parts.append
    a('<!DOCTYPE html>')
    a('<html lang="zh-CN">')
    a('<head>')
    a('    <meta charset="UTF-8">')
    a('    <meta name="viewport" content="width=device-width, initial-scale=1.0">')
    a('    <title>协作类挑款指南 · 39 款分成 6 组 - 团建 & 培训游戏库</title>')
    a(CSS)
    a('</head>')
    a('<body>')
    a('<div class="container">')
    a('    <div class="header">')
    a('        <h1>🤝 协作类挑款指南</h1>')
    a('        <div class="subtitle">39 款协作游戏太多，等于没有目录——按「你想解决什么」拆成 6 组</div>')
    a('        <div class="tag">39 款 · 6 组 · 每组给了首选与「什么时候别选它」</div>')
    a('    </div>')
    a('')
    a('    <div class="info-grid">')
    for icon, label, value in (('🎲', '协作类总数', '39 款（占全库 46%）'),
                               ('🧭', '分组口径', '按「练哪种协作」分 6 组'),
                               ('⚡', '最快的一款', '齐眉棍 20–30 min'),
                               ('👥', '人数跨度', '2 人 ～ 20 人')):
        a('        <div class="info-card"><div class="icon">%s</div>'
          '<div class="label">%s</div><div class="value">%s</div></div>' % (icon, label, value))
    a('    </div>')
    a('')
    a('    <div class="section">')
    a('        <h2>⚡ 30 秒挑款：你现在是哪一种麻烦</h2>')
    a('        <p>不用读完全页。找到你现在的处境，直接拿最后那款；想再看同类，点组名跳下去。</p>')
    a('        <table class="data-table">')
    a('            <tr><th>你现在的麻烦</th><th>去哪一组</th><th>直接拿这款</th></tr>')
    gk = {g['key']: g for g in GROUPS}
    for trouble, key, gid in DECIDE:
        g = gk[key]
        m = meta[gid]
        a('            <tr><td>%s</td><td><a href="#g-%s">%s %s</a></td>'
          '<td><a href="games/collaboration/%s.html">%s</a> <span style="color:%s;">（%s / %s）</span></td></tr>'
          % (trouble, key, g['icon'], g['name'], gid, m['title'], C['muted'],
             m['people'], m['dur']))
    a('        </table>')
    a('        <blockquote>六组是按<strong>「这个游戏到底在练哪种协作」</strong>切的，不是按题材切的。'
      '同样都是太空 / 地下城 / 古装皮，练的东西可能完全不同——皮相相同的两款往往分在不同组。</blockquote>')
    a('    </div>')
    a('')
    a('    <div class="section">')
    a('        <h2>🧭 六组分别是什么</h2>')
    for g in GROUPS:
        pick = meta[g['pick']]
        a('        <div class="group-card" id="g-%s">' % g['key'])
        a('            <h3>%s %s（%d 款）</h3>' % (g['icon'], g['name'], len(g['ids'])))
        a('            <div class="group-lead">%s</div>' % g['lead'])
        a('            <div class="when-row">')
        a('                <div class="when-box"><b>✅ 什么情况下选它</b><br>%s</div>' % g['when'])
        a('                <div class="avoid-box"><b>⛔ 什么时候别选它</b><br>%s</div>' % g['avoid'])
        a('            </div>')
        a('            <div class="pick">🎯 拿不准就先拿：<a href="games/collaboration/%s.html" '
          'style="color:#0b1a0c;text-decoration:underline;">%s</a>（%s / %s）</div>'
          % (g['pick'], pick['title'], pick['people'], pick['dur']))
        a('            <table class="data-table">')
        a('                <tr><th>游戏</th><th>人数</th><th>时长</th><th>这一款在练什么</th></tr>')
        for gid in g['ids']:
            m = meta[gid]
            a('                <tr><td><a href="games/collaboration/%s.html">%s</a></td>'
              '<td>%s</td><td>%s</td><td>%s</td></tr>'
              % (gid, m['title'], m['people'], m['dur'], m['desc']))
        a('            </table>')
        a('        </div>')
    a('    </div>')
    a('')
    a('    <div class="section">')
    a('        <h2>⚠️ 三个最容易挑错的地方</h2>')
    a('        <table class="data-table">')
    a('            <tr><th>坑</th><th>为什么</th></tr>')
    for t, why in PITFALL:
        a('            <tr><td><b>%s</b></td><td>%s</td></tr>' % (t, why))
    a('        </table>')
    a('        <blockquote>协作是全库最大的分类（39/85，46%），但它同时也是最容易被误用的一个：'
      '很多人想解决的其实是「沟通」或「信任」，却在协作里翻了半天。'
      '先确认你要的是<strong>「一起把事做成」</strong>，再回来挑。</blockquote>')
    a('    </div>')
    a('')
    a('    <div class="section">')
    a('        <h2>🔗 相关的入口</h2>')
    a('        <ul>')
    a('            <li><a href="index.html">全部 85 款游戏（按 8 个分类）</a> —— 首页也能直接按人数 / 时长筛，选「🤝 协作」后会出现同样的 6 个子类按钮</li>')
    a('            <li><a href="README.md">README 索引表</a> —— 纯文本版，协作一节已按这 6 组排好</li>')
    a('            <li><a href="toolbox/generator.html">团建方案生成器（全库版）</a> —— 有整块时间、想要一整套流程时用</li>')
    a('            <li><a href="play/tools/plan-generator/">T1 快速版生成器</a> —— 现场临时只要几个游戏，30 秒出一组</li>')
    a('            <li><a href="guide.html">教练使用指南</a> —— 第一次带团先读 5 分钟</li>')
    a('            <li><a href="toolbox/debrief.html">复盘引导框架</a> —— 协作类游戏的复盘最容易退化成「大家都很努力」</li>')
    a('        </ul>')
    a('    </div>')
    a('')
    a('    <div class="footer">')
    a('        <div>')
    a('            <a href="index.html" class="back-link">← 回到游戏库</a>')
    a('            <a href="README.md" class="back-link">README 索引</a>')
    a('            <a href="toolbox/generator.html" class="back-link">方案生成器</a>')
    a('        </div>')
    a('        <div style="margin-top:14px;">团建 & 培训游戏库 · 协作类二级索引 · 39 款 / 6 组</div>')
    a('    </div>')
    a('</div>')
    a('</body>')
    a('</html>')
    text = '\n'.join(parts) + '\n'
    p = os.path.join(TB, 'collab.html')
    write(p, text, crlf=True)
    print('collab.html 已生成：%d 行' % text.count('\n'))


# ---------------- 3. README.md ----------------
def patch_readme(meta):
    p = os.path.join(TB, 'README.md')
    rm = read(p)
    # 用正则定位而不是 partition：整块切分时若锚点命中在文件尾会静默拿到空 body
    m_head = re.search(r'^#### 🤝 团队协作（collaboration）$', rm, re.M)
    assert m_head, 'README 未找到协作小节'
    m_next = re.search(r'^#### 🔐 信任建立（trust）$', rm, re.M)
    assert m_next and m_next.start() > m_head.end(), 'README 未找到信任小节'
    body = rm[m_head.end():m_next.start()]
    assert len(body) > 2000, '协作小节过短（%d 字符），疑似锚点错位' % len(body)
    head, rest = rm[:m_head.start()], rm[m_next.start():]

    rows = {}
    for line in body.split('\n'):
        m = re.match(r'\| \[([^\]]+)\]\(games/collaboration/([a-z0-9-]+)\.md\)', line)
        if m:
            rows[m.group(2)] = line
    assert len(rows) == 39, 'README 协作表 %d 行 != 39' % len(rows)

    new = ('#### 🤝 团队协作（collaboration）\n'
           '\n'
           '> 39 款占全库 46%，光看名字挑不出来。这一节已按「练哪种协作」排成 6 组；'
           '不确定选哪组时先看 [协作类挑款指南](collab.html)（含 30 秒决策表与「什么时候别选它」）。\n'
           '\n')
    new += '| 游戏名称 | 形式 | 人数 | 时长 | 场景标签 |\n|---------|------|------|------|---------|\n'
    for g in GROUPS:
        new += ('| **%s %s（%d 款）** | | | | |\n'
                % (g['icon'], g['name'], len(g['ids'])))
        for gid in g['ids']:
            new += rows[gid] + '\n'
    write(p, head + new + '\n' + rest)
    print('README.md 已更新：协作表按 6 组重排')


if __name__ == '__main__':
    meta = collect()
    miss = [gid for g in GROUPS for gid in g['ids'] if gid not in meta]
    assert not miss, '缺元信息: %s' % miss
    missing_desc = [k for k, v in meta.items() if not v.get('desc')]
    assert not missing_desc, '缺一句话描述: %s' % missing_desc
    patch_index(meta)
    build_collab_html(meta)
    patch_readme(meta)
    print('完成')
