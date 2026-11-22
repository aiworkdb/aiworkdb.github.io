# -*- coding: utf-8 -*-
"""给「💻 线上团建」8 款建二级索引 + 新建 online.html 挑款专页（2026-10-28 自动化第四十二次）。

背景（ROADMAP 下一步建议 · 2026-10-27 首选）：
    线上 8 款是「协作之外 46 款无二级索引」里最后一块。此前它们在 index.html 里
    挤在一个网格里，8 张卡只有「线上」一个标签，按名字挑必然挑错：
      - 异步接力是全库唯一一款**异步**游戏，其余 7 款都要求全员同时在线；
      - 线上还牵涉「不能真做」的物理限制（线下道具搬不上去）。

现按「**远程这一局怎么玩**」（而不是「练什么能力」）重切 4 组 —— 全库第四套口径：
    - 🎤 不用专用工具（一张卡 / 一句话就够；人必须同时在线）
    - 🖥️ 要一块共享屏（白板 / 绘图 / 投票；人必须同时在线）
    - 🧾 要一份文档承载（发言筹码 / 能量值 / 求助券；人必须同时在线）
    - ⏳ 不用同时在线（错峰接力 —— 全库唯一一款异步游戏）

与前三套口径都不同：
    协作问「练哪种动作」、创意解题问「卡在哪一步」、破冰问「结束留下什么」，
    线上问「**这一局在远程靠什么成立**」—— 要不要专用工具、要不要一块屏、
    人到底需不需要同时在线。

同时记录一个长期缺口：**线上场景标签 ≠ 线上分类**。
    全库带「线上场景 / 远程场景」改造段的共 14 款（协作 6 / 沟通 4 / 破冰 2 / 领导力 2），
    它们分类在别处 —— 按「线上」分类挑会漏掉它们。

用法：
    python teambuilding/build_online_index.py
幂等：index.html 已含 data-online 时跳过网格改造；online.html 每次重建。
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
DIR = 'online'

# ---------------- 分组定义（全库第四套口径） ----------------
GROUPS = [
    dict(key='voice', icon='🎤', name='不用专用工具', short='不用专用工具', n=2,
         sub='一张卡或一句话就够；缺点是人必须同时在线',
         lead='这两款不需要任何专用平台 —— 会议软件加一张在共享文档里手写就能画的卡就够了。'
              '开场五分钟就能开，是线上团建最省事的两款，也最适合 50 人以上的大场子。',
         when='会议刚开场要暖场 / 临时加十分钟 / 50 人以上的大场子 / 线下道具搬不上去的时候',
         avoid='两款都不产生任何结论，玩完只剩笑声和几个共同点；'
               '线上宾果在 40 人以上是灾难 —— 每人要签 24 个格子，实际会变成失控的私聊；'
               '「我从未」在 20 人以上基本要冷场两次以上。',
         pick='never-have-i-ever',
         ids=['never-have-i-ever', 'online-bingo']),

    dict(key='screen', icon='🖥️', name='要一块共享屏', short='要一块共享屏', n=3,
         sub='白板 / 绘图 / 投票工具；缺工具就开不起来',
         lead='这三款都要一块大家都点得到的界面 —— 白板、绘图工具或投票平台，'
              '而且都要**提前准备内容**：词表、谜题链、题库。'
              '教练的功课全在这半小时里，工具没试过就别开。',
         when='破冰之后要大家真的动手做一次 / 需要一点输赢和紧张感 / 全员大会要覆盖公司与行业知识',
         avoid='工具没提前试过就开不起来：白板卡顿、不会用都会直接毁掉这一场；'
               '虚拟逃脱的谜题链不提前设计必然散架；'
               '知识竞答要 35 道题、四个环节，提前量不足就是一场灾难；'
               '虚拟逃脱 30 分钟解不出来，团队会瘫在那里互相看。',
         pick='online-pictionary',
         ids=['online-pictionary', 'virtual-escape', 'team-quiz']),

    dict(key='doc', icon='🧾', name='要一份文档承载', short='要一份文档承载', n=2,
         sub='产出物是留在文档里的记录',
         lead='这两款玩完会留下一样东西：一张发言筹码表、一张能量值分栏表、'
              '一条条匿名求助券。线下会议里「谁在说话」「谁快撑不住了」转眼就散，'
              '远程把它写进文档就留住了 —— 这是 8 款里唯一在治「远程看不见人」的。',
         when='线上会总是几个人说话、其余人在潜水 / 团队状态互相看不见想摸个底 / '
              '开完会要一份能复盘能追责的记录',
         avoid='两款都不是破冰 —— 能量明牌要每个人先讲自己的状态，第一次见面就做非常冒犯；'
               '无声会议的能量值环节会暴露个体差异，团队刚组建时别急着上；'
               '两款都要 40 分钟以上（含 18 分钟复盘），短会做不完。',
         pick='silent-meeting',
         ids=['silent-meeting', 'energy-checkin']),

    dict(key='async', icon='⏳', name='不用同时在线', short='不用同时在线', n=1,
         sub='人不必同时在线 —— 全库唯一一款异步游戏',
         lead='全库唯一一款**异步**线上游戏 —— 你上线的时候别人可以下线。'
              '上一棒把三栏便签写清楚就下线，下一棒上线只读不许问，'
              '哪怕他就在群里也不能问，追问要付「回看税」。',
         when='跨时区 / 混合办公 / 人根本凑不齐同一时刻 / '
              '真正想练的是「交接质量」而不是「一起玩得开心」',
         avoid='别把它当团建用 —— 45–60 分钟里真正能让人「一起玩」的只有十几分钟，'
               '其余时间都在写便签和等下一棒；'
               '「不许问已下线的人」这条规则非常反直觉，团队不认就会直接破功；'
               '它要求所有人愿意异步工作，纯同步团队会觉得被晾着。',
         pick='async-relay',
         ids=['async-relay']),
]

# 30 秒决策表
DECIDE = [
    ('远程会议冷场，十几个人谁都不开口', 'voice', 'never-have-i-ever'),
    ('刚建团队，想让大家先找到几个共同点', 'voice', 'online-bingo'),
    ('破冰之后想让大家真的动手做一次', 'screen', 'online-pictionary'),
    ('需要一点紧张感和输赢，把气氛提上来', 'screen', 'virtual-escape'),
    ('全员大会，想把公司文化讲成一件具体的事', 'screen', 'team-quiz'),
    ('线上开会永远是几个人说话，其余人在潜水', 'doc', 'silent-meeting'),
    ('远程团队状态互相看不见，想摸个底', 'doc', 'energy-checkin'),
    ('跨时区，人凑不齐同一时刻', 'async', 'async-relay'),
]

# 跨分类：带「线上场景 / 远程场景」改造段但分类在别处的游戏（14 款）
CROSS = [
    ('games/collaboration/ball-relay.html', '🤝 团队协作', '珠行万里',
     '改为「在线接力」—— 用在线白板，每人画一段轨道，球（图标）依次经过'),
    ('games/collaboration/body-letters.html', '🤝 团队协作', '人体拼字',
     '用摄像头 + 身体拼字，截图后发到群里投票'),
    ('games/collaboration/eyebrow-stick.html', '🤝 团队协作', '齐眉棍',
     '改为「同步鼓掌」挑战 —— 全组通过视频会议，实现完全同步的鼓掌'),
    ('games/collaboration/island-survival.html', '🤝 团队协作', '岛屿求生',
     '用 Tabletopia 或类似工具，视频会议讨论'),
    ('games/collaboration/secret-mission.html', '🤝 团队协作', '绝密行动',
     '用 Tabletopia 或类似工具，视频会议讨论；用在线白板记录警戒值和时间'),
    ('games/collaboration/wind-fire-wheel.html', '🤝 团队协作', '风火轮',
     '改为「线上接力」—— 每人用自己家的报纸做一段，视频会议拼接'),
    ('games/communication/animal-detective.html', '💬 沟通表达', '动物城大侦探',
     '用在线白板共享线索卡，视频会议讨论'),
    ('games/communication/draw-guess.html', '💬 沟通表达', '你说我画',
     '用在线白板（Miro / Figma），描述者用语音，画图者用鼠标'),
    ('games/communication/drawing-relay.html', '💬 沟通表达', '画图接龙',
     '用在线白板（Miro / Figma），每人用鼠标画'),
    ('games/communication/telephone-game.html', '💬 沟通表达', '传话游戏',
     '用私信 / 微信一对一传递，最后一个人把结果发到群里'),
    ('games/icebreaker/blind-box-myth.html', '🧊 破冰热场', '盲盒神话',
     '用在线卡牌工具（如 Tabletopia）或微信群发卡牌图片交易'),
    ('games/icebreaker/food-challenge.html', '🧊 破冰热场', '美食挑战赛',
     '用在线白板，每人放食材图片，拼出「虚拟菜」'),
    ('games/leadership/silent-leader.html', '👑 领导力', '沉默领袖',
     '用视频会议 + 聊天框（领袖不能发消息，只能用摄像头手势）'),
    ('games/leadership/tangram.html', '👑 领导力', '七巧板',
     '用在线拼图工具（如 Miro 的拼图插件），分组用 breakout rooms'),
]

# 配色：hue 304（品红紫）—— 落在全站 297↔312 的 15° 空档正中，距最近已有色相 7°
C = {
    'primary': '#7c2776', 'mid': '#aa3ca2', 'light': '#da81d4',
    'bg': '#190b18', 'container': '#2c172a', 'gridbg': '#120712',
    'border': '#532d50', 'text': '#e9d2e8', 'muted': '#af83ac',
    'quote': '#381e37', 'whenbox': '#3e233c',
    'avoidbox': '#371d1b', 'avoidborder': '#7a332e', 'avoidtext': '#dd9488',
    'headtext': '#20091e',
}


# ---------------- 工具 ----------------
def rd(p):
    return io.open(p, encoding='utf-8').read()


def wr(p, s, crlf=True):
    if crlf:
        s = s.replace('\r\n', '\n').replace('\n', '\r\n')
    io.open(p, 'w', encoding='utf-8', newline='').write(s)


def rep(text, old, new, what):
    assert text.count(old) == 1, '锚点不唯一(%d)或未命中: %s' % (text.count(old), what)
    return text.replace(old, new)


def short_people(s):
    return re.sub(r'（[^）]*）\s*$', '', s).strip()


# ---------------- 采集现成数据 ----------------
def collect():
    """从 README.md 取 名称/形式/人数/时长/场景标签，从 index.html 取 标题/描述/图标。"""
    rm = rd(os.path.join(TB, 'README.md'))
    meta = {}
    # ⚠️ 必须用 [^|\n]* 而不是 [^|]* —— 后者能匹配换行，贪婪的 {4,5} 会跨行吞行（经验 100）
    for m in re.finditer(
            r'\|\s*\[([^\]]+)\]\(games/online/([a-z0-9-]+)\.md\)\s*'
            r'((?:\|[^|\n]*){4,5})\|', rm):
        gid = m.group(2)
        cells = [c.strip() for c in m.group(3).split('|')[1:]]
        if len(cells) != 4:
            continue
        meta[gid] = {
            'name': m.group(1), 'cat': 'online', 'form': cells[0],
            'people': cells[1], 'dur': cells[2], 'tags': cells[3],
            'people_short': short_people(cells[1]),
        }
    idx = rd(os.path.join(TB, 'index.html'))
    for m in re.finditer(
            r'<a href="games/online/([a-z0-9-]+)\.html" '
            r'class="card"[^>]*>(.*?)</a>', idx, re.S):
        gid = m.group(1)
        if gid not in meta:
            continue
        d = re.search(r'class="card-desc">(.*?)</div>', m.group(2), re.S)
        t = re.search(r'class="card-title">(.*?)</div>', m.group(2), re.S)
        ic = re.search(r'class="card-icon">(.*?)</div>', m.group(2), re.S)
        meta[gid]['desc'] = re.sub(r'\s+', ' ', d.group(1)).strip() if d else ''
        meta[gid]['title'] = re.sub(r'\s+', ' ', t.group(1)).strip() if t else meta[gid]['name']
        meta[gid]['icon'] = ic.group(1).strip() if ic else '🎲'
    on_disk = set(f[:-3] for f in os.listdir(os.path.join(TB, 'games', DIR)) if f.endswith('.md'))
    got = set(meta)
    assert got == on_disk, '采集到 %d 款，目录 %d 款；缺 %s 多 %s' % (
        len(got), len(on_disk), sorted(on_disk - got), sorted(got - on_disk))
    return meta


# ---------------- 1. index.html ----------------
def patch_index():
    p = os.path.join(TB, 'index.html')
    h = rd(p)

    if 'data-online=' in h:
        print('index.html 已含 data-online，跳过网格改造')
    else:
        s = h.find('    <div class="grid" id="grid-online">')
        assert s > 0, '未找到 grid-online 开标签'
        gt = h.find('>', s) + 1
        depth, i = 1, gt
        pat = re.compile(r'<div\b|</div>')
        while depth > 0:
            m = pat.search(h, i)
            assert m, 'grid-online 未闭合'
            depth += 1 if m.group().startswith('<div') else -1
            i = m.end()
        end = i - len('</div>')
        body = h[gt:end]

        CARD = re.compile(r'<a href="games/online/([a-z0-9-]+)\.html" '
                          r'class="card"[^>]*>.*?</a>', re.S)
        cards = {}
        order = []
        for m in CARD.finditer(body):
            cards[m.group(1)] = m.group(0)
            order.append(m.group(1))
        assert len(cards) == 8, '线上网格卡片数 %d != 8' % len(cards)
        assert body.count('</a>') == 8, '网格内 </a> 数 %d != 8（卡片内有嵌套 a？）' % body.count('</a>')

        sub_of = {}
        for g in GROUPS:
            for gid in g['ids']:
                assert gid in cards, '分组引用了网格里没有的游戏: ' + gid
                assert gid not in sub_of, '游戏同时属于多组: ' + gid
                sub_of[gid] = g['key']
        assert set(sub_of) == set(cards), '分组与卡片集合不一致: %s' % (set(sub_of) ^ set(cards))

        out = '\n'
        for g in GROUPS:
            # ⚠️ 这里**不加** .subhead 小标题 —— 全站只有协作网格（39 款）用小标题。
            #    破冰网格（8 款，带二级索引 + 挑款页）与创意解题网格（10 款）都只用
            #    data-* 属性 + 肌肉标签胶囊 —— 线上 8 款按破冰的先例来。
            #    （小标题是 39 款量级才需要的视觉分节；8 款不需要，
            #      且 smoke_test_collab.js 有一条「全站小标题应为 6」的断言。）
            for gid in g['ids']:
                c = cards[gid]
                c2 = c.replace(' class="card" data-people=',
                               ' class="card" data-online="%s" data-people=' % g['key'], 1)
                assert c2 != c, 'data-online 未插入: ' + gid
                chip = '<span class="tag">%s %s</span>' % (g['icon'], g['short'])
                c2, n = re.subn(r'(<div class="card-tags">)(.*?)(</div>)',
                                lambda mm: mm.group(1) + mm.group(2) + chip + mm.group(3),
                                c2, count=1, flags=re.S)
                assert n == 1, 'card-tags 未命中: ' + gid
                out += '      ' + c2 + '\n'
        h = h[:gt] + out + h[end:]
        print('index.html 线上网格已按 4 组重排（8 张卡 + data-online + 肌肉标签）')

    if 'id="online-filter"' not in h:
        h = rep(h,
                '    <div class="filter-group" id="idea-filter" style="display:none;">',
                '    <div class="filter-group" id="online-filter" style="display:none;">\n'
                '      <span class="filter-label">线上怎么玩：</span>\n'
                '      <button class="filter-btn active" onclick="toggleFilter(\'online\', \'all\', this)">全部</button>\n'
                + ''.join('      <button class="filter-btn" onclick="toggleFilter(\'online\', \'%s\', this)">%s %s</button>\n'
                          % (g['key'], g['icon'], g['short']) for g in GROUPS) +
                '    </div>\n'
                '    <div class="filter-group" id="idea-filter" style="display:none;">',
                '线上怎么玩筛选行')
    else:
        print('index.html 已有 online-filter，跳过')

    if 'resetOnline' not in h:
        h = rep(h,
                "var currentFilters = {\n  category: 'all',\n  people: 'all',\n  duration: 'all',\n  sub: 'all',\n  idea: 'all',\n  ice: 'all'\n};",
                "var currentFilters = {\n  category: 'all',\n  people: 'all',\n  duration: 'all',\n  sub: 'all',\n  idea: 'all',\n  ice: 'all',\n  online: 'all'\n};",
                'JS currentFilters')

        h = rep(h,
                "function resetSub() {",
                "// 💻线上 8 款按「远程这一局怎么玩」分 4 组，第二级筛选只在选中线上时出现\n"
                "function setOnlineRow(on) {\n"
                "  var row = document.getElementById('online-filter');\n"
                "  if (row) { row.style.display = on ? '' : 'none'; }\n"
                "}\n\n"
                "function resetOnline() {\n"
                "  currentFilters.online = 'all';\n"
                "  var row = document.getElementById('online-filter');\n"
                "  if (!row) { return; }\n"
                "  row.querySelectorAll('.filter-btn').forEach(function(b) {\n"
                "    if (b.textContent === '全部') { b.classList.add('active'); }\n"
                "    else { b.classList.remove('active'); }\n"
                "  });\n"
                "}\n\n"
                "function resetSub() {",
                'JS online 筛选函数')

        h = rep(h,
                "    // 「破冰要什么」只在选中 🧊破冰 时出现；离开破冰分类才复位\n"
                "    if (value === 'icebreaker') { setIceRow(true); }\n"
                "    else { resetIce(); setIceRow(false); }\n",
                "    // 「破冰要什么」只在选中 🧊破冰 时出现；离开破冰分类才复位\n"
                "    if (value === 'icebreaker') { setIceRow(true); }\n"
                "    else { resetIce(); setIceRow(false); }\n"
                "    // 「线上怎么玩」只在选中 💻线上 时出现；离开线上分类才复位\n"
                "    if (value === 'online') { setOnlineRow(true); }\n"
                "    else { resetOnline(); setOnlineRow(false); }\n",
                'JS toggleFilter 联动')

        h = rep(h,
                "      // 协作子类筛选（仅协作分类下的 6 组）\n",
                "      // 「线上怎么玩」筛选（仅线上分类下的 4 组）\n"
                "      if (visible && currentFilters.online !== 'all') {\n"
                "        if (card.getAttribute('data-online') !== currentFilters.online) {\n"
                "          visible = false;\n"
                "        }\n"
                "      }\n\n"
                "      // 协作子类筛选（仅协作分类下的 6 组）\n",
                'JS online 过滤')

        h = rep(h,
                "    // 子类小标题：该组一张卡都不显示时，小标题也要跟着消失\n"
                "    grid.querySelectorAll('.subhead').forEach(function(sh) {\n"
                "      var key = sh.getAttribute('data-sub');\n"
                "      var any = false;\n"
                "      grid.querySelectorAll('.card[data-sub=\"' + key + '\"]').forEach(function(c) {\n"
                "        if (c.style.display !== 'none') { any = true; }\n"
                "      });\n"
                "      sh.style.display = any ? '' : 'none';\n"
                "    });\n",
                "    // 子类小标题：该组一张卡都不显示时，小标题也要跟着消失\n"
                "    // （只有协作网格有小标题；破冰 / 创意解题 / 线上网格没有）\n"
                "    grid.querySelectorAll('.subhead').forEach(function(sh) {\n"
                "      var key = sh.getAttribute('data-sub');\n"
                "      var any = false;\n"
                "      grid.querySelectorAll('.card[data-sub=\"' + key + '\"]').forEach(function(c) {\n"
                "        if (c.style.display !== 'none') { any = true; }\n"
                "      });\n"
                "      sh.style.display = any ? '' : 'none';\n"
                "    });\n",
                'JS subhead 显隐（仅 data-sub）')
        print('index.html JS 已接入 online 筛选')
    else:
        print('index.html JS 已含 resetOnline，跳过')

    if 'href="online.html"' not in h:
        h = rep(h,
                '        <a href="ice.html" class="res-chip">🧊 破冰共 8 款，帮我挑</a>\n',
                '        <a href="ice.html" class="res-chip">🧊 破冰共 8 款，帮我挑</a>\n'
                '        <a href="online.html" class="res-chip">💻 线上共 8 款，帮我挑</a>\n',
                '首屏胶囊')
    else:
        print('index.html 已有 online.html 入口，跳过')

    wr(p, h)
    print('index.html 已更新：线上 4 组子类（%s）'
          % ', '.join('%s=%d' % (g['key'], len(g['ids'])) for g in GROUPS))


# ---------------- 2. online.html ----------------
CSS = """
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.6; color: %(text)s;
        background: linear-gradient(135deg, %(bg)s 0%%, #150815 55%%, #1f0c1e 100%%);
        padding: 20px;
    }
    .container {
        max-width: 1100px; margin: 0 auto; background: %(container)s;
        border-radius: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.7);
        overflow: hidden; border: 1px solid %(border)s;
    }
    .header {
        background: linear-gradient(135deg, %(primary)s 0%%, %(mid)s 45%%, %(light)s 100%%);
        color: %(headtext)s; padding: 40px; text-align: center;
    }
    .header h1 { font-size: 2.1em; margin-bottom: 10px; text-shadow: 0 1px 3px rgba(255,255,255,0.25); }
    .header .subtitle { font-size: 1.05em; opacity: 0.95; }
    .header .tag {
        display: inline-block; margin-top: 14px; padding: 6px 18px;
        background: rgba(0,0,0,0.22); border-radius: 20px; font-size: 0.9em; border: 1px solid %(light)s;
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
    .data-table th { background: %(primary)s; color: %(headtext)s; padding: 12px; text-align: left; font-size: 0.95em; }
    .data-table td { padding: 10px 12px; border-top: 1px solid %(border)s; color: %(text)s; font-size: 0.92em; }
    .data-table tr:nth-child(even) { background: %(container)s; }
    .data-table .cat { white-space: nowrap; color: %(muted)s; font-size: 0.9em; }
    .group-card {
        background: %(container)s; border: 1px solid %(border)s; border-radius: 12px;
        padding: 22px 24px; margin-top: 18px;
    }
    .group-card h3 { margin-top: 0; font-size: 1.2em; color: %(light)s; }
    .group-lead { font-size: 0.96em; color: %(text)s; margin-bottom: 14px; }
    .when-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 14px; margin-bottom: 16px; }
    .when-box, .avoid-box { border-radius: 10px; padding: 14px 16px; font-size: 0.92em; }
    .when-box { background: %(whenbox)s; border: 1px solid %(border)s; }
    .avoid-box { background: %(avoidbox)s; border: 1px solid %(avoidborder)s; }
    .when-box b { color: %(light)s; }
    .avoid-box b { color: %(avoidtext)s; }
    .pick {
        display: inline-block; margin-bottom: 14px; padding: 8px 16px; border-radius: 20px;
        background: %(primary)s; color: %(headtext)s; font-size: 0.92em; font-weight: 600;
    }
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
        background: %(primary)s; color: %(headtext)s; text-decoration: none; border-radius: 20px; font-size: 0.9em;
    }
    .back-link:hover { background: %(light)s; }
</style>
""" % C


def build_online_html(meta):
    parts = []
    a = parts.append
    a('<!DOCTYPE html>')
    a('<html lang="zh-CN">')
    a('<head>')
    a('    <meta charset="UTF-8">')
    a('    <meta name="viewport" content="width=device-width, initial-scale=1.0">')
    a('    <title>线上挑款指南 · 8 款分成 4 组 - 团建 &amp; 培训游戏库</title>')
    a(CSS)
    a('</head>')
    a('<body>')
    a('<div class="container">')
    a('    <div class="header">')
    a('        <h1>💻 线上挑款指南</h1>')
    a('        <div class="subtitle">8 款线上团建 —— 按「远程这一局怎么玩」分成 4 组</div>')
    a('        <div class="tag">8 款 · 4 组 · 每组给了首选与「什么时候别选它」</div>')
    a('    </div>')
    a('')
    a('    <div class="info-grid">')
    for icon, label, value in (('🎲', '覆盖范围', '8 款（💻 线上团建）'),
                               ('🧭', '分组口径', '按「远程怎么玩」分 4 组'),
                               ('⏳', '唯一异步的一款', '异步接力 45–60 min'),
                               ('👥', '人数跨度', '5 人 ～ 50 人')):
        a('        <div class="info-card"><div class="icon">%s</div>'
          '<div class="label">%s</div><div class="value">%s</div></div>' % (icon, label, value))
    a('    </div>')
    a('')
    # ---- 30 秒挑款表 ----
    a('    <div class="section">')
    a('        <h2>⚡ 30 秒挑款：你现在想要什么</h2>')
    a('        <p>不用读完全页。找到你此刻的麻烦，直接拿最后那款；想再看同类，点组名跳下去。</p>')
    a('        <table class="data-table">')
    a('            <tr><th>你现在的麻烦</th><th>去哪一组</th><th>直接拿这款</th></tr>')
    gk = {g['key']: g for g in GROUPS}
    for trouble, key, gid in DECIDE:
        g = gk[key]
        m = meta[gid]
        a('            <tr><td>%s</td><td><a href="#g-%s">%s %s</a></td>'
          '<td><a href="games/online/%s.html">%s</a> <span style="color:%s;">（%s / %s）</span></td></tr>'
          % (trouble, key, g['icon'], g['name'], gid, m['title'], C['muted'],
             m['people_short'], m['dur']))
    a('        </table>')
    a('        <blockquote>四组是按<strong>「远程这一局怎么玩」</strong>切的，'
      '不是按「练什么能力」切的。同样是线上游戏，'
      '「不用任何工具开口就行」和「要先备好一块白板和一份词表」完全是两回事 —— '
      '一个教练五分钟就能开，另一个要提前半小时准备。</blockquote>')
    a('    </div>')
    a('')
    # ---- 边界说明 ----
    a('    <div class="section">')
    a('        <h2>🔀 「线上」不等于「能异步」：七款要全员同时在线</h2>')
    a('        <p>「线上」这个词只说了<strong>地点</strong>，没说<strong>时间</strong>。'
      '8 款里只有 1 款是真正异步的，其余 7 款都要求所有人<strong>同时在线、同时开始</strong>。'
      '跨时区团队按「线上」分类挑，7/8 的概率是根本开不起来。</p>')
    a('        <table class="data-table">')
    a('            <tr><th></th><th>🎤 不用专用工具</th><th>🖥️ 要一块共享屏</th>'
      '<th>🧾 要一份文档承载</th><th>⏳ 不用同时在线</th></tr>')
    a('            <tr><td><b>人必须同时在线</b></td>'
      '<td><b>要</b></td><td><b>要</b></td><td><b>要</b></td>'
      '<td><b style="color:#da81d4;">不要</b></td></tr>')
    a('            <tr><td><b>教练要准备什么</b></td>'
      '<td>零 —— 一张手写卡</td><td>一块白板 / 投票工具 + 词表 / 谜题 / 题库</td>'
      '<td>一份共享文档 + 筹码行 / 能量值分栏</td>'
      '<td>一份共享文档 + 群聊便签区</td></tr>')
    a('            <tr><td><b>线下道具搬得上去吗</b></td>'
      '<td>本来就没有道具</td><td>要换成线上的等价物（Skribbl / Miro）</td>'
      '<td>筹码、能量牌变成文档里的行和格</td>'
      '<td>传纸条变成写便签</td></tr>')
    a('            <tr><td><b>产出的是什么</b></td>'
      '<td>几个共同点、一些笑声</td><td>一张画、一个分数、一个解开的谜</td>'
      '<td>一份留下来的记录（谁在说话、谁的状态）</td>'
      '<td>一条写得清楚的三栏便签</td></tr>')
    a('            <tr><td><b>最容易翻车在哪</b></td>'
      '<td>大场子冷场；50 人宾果签不完</td>'
      '<td>工具没试过；内容没备够</td>'
      '<td>暴露度太高，团队刚组建就做会冒犯</td>'
      '<td>团队不认「不许问已下线的人」这条规则</td></tr>')
    a('        </table>')
    a('        <p style="margin-top:18px;">把四组横过来看，真正在递增的轴是'
      '<strong>「教练要准备多少」</strong>：<strong>零 → 一块屏 + 一份内容 → 一份文档 → 一份文档 + 跨时段</strong>。'
      '挑款时该问的是「我这半小时能准备出什么」，而不是「哪个游戏看起来更线上」。</p>')
    a('        <table class="data-table">')
    a('            <tr><th>远程怎么玩</th><th>组</th><th>组内首选</th></tr>')
    for g in GROUPS:
        pick = meta[g['pick']]
        a('            <tr><td><a href="#g-%s">%s %s</a></td>'
          '<td>%d 款</td><td>%s（%s / %s）</td></tr>'
          % (g['key'], g['icon'], g['name'], len(g['ids']), pick['title'],
             pick['people_short'], pick['dur']))
    a('        </table>')
    a('        <blockquote>再提醒一句：<strong>这 8 款只是带「线上场景 / 远程场景」改造段的 14 款里的 8 款</strong>。'
      '另外 6 款（协作类的珠行万里 / 人体拼字 / 齐眉棍 / 岛屿求生 / 绝密行动 / 风火轮，'
      '沟通类的动物城大侦探 / 你说我画 / 画图接龙 / 传话游戏，'
      '破冰类的盲盒神话 / 美食挑战赛，领导力类的沉默领袖 / 七巧板）'
      '也各自写好了怎么搬到线上，只是它们的分类在别处 —— 见下方「💻 线上不只是这 8 款」。</blockquote>')
    a('    </div>')
    a('')
    # ---- 4 组详解 ----
    a('    <div class="section">')
    a('        <h2>🧭 四组分别是什么</h2>')
    for g in GROUPS:
        pick = meta[g['pick']]
        a('        <div class="group-card" id="g-%s">' % g['key'])
        a('            <h3>%s %s（%d 款）</h3>' % (g['icon'], g['name'], len(g['ids'])))
        a('            <div class="group-lead">%s</div>' % g['lead'])
        a('            <div class="when-row">')
        a('                <div class="when-box"><b>✅ 什么情况下选它</b><br>%s</div>' % g['when'])
        a('                <div class="avoid-box"><b>⛔ 什么时候别选它</b><br>%s</div>' % g['avoid'])
        a('            </div>')
        a('            <div class="pick">🎯 拿不准就先拿：'
          '<a href="games/online/%s.html" style="color:%s;text-decoration:underline;">%s</a>（%s / %s）</div>'
          % (g['pick'], C['headtext'], pick['title'], pick['people_short'], pick['dur']))
        a('            <table class="data-table">')
        a('                <tr><th>游戏</th><th>形式</th><th>人数</th><th>时长</th>'
          '<th>远程要准备什么</th><th>这一款在练什么</th></tr>')
        for gid in g['ids']:
            m = meta[gid]
            a('                <tr><td><a href="games/online/%s.html">%s</a></td>'
              '<td class="cat">%s</td><td>%s</td><td>%s</td>'
              '<td>%s</td><td>%s</td></tr>'
              % (gid, m['title'], m['form'], m['people'], m['dur'],
                 REMOTE_NEED.get(gid, '—'), m['desc']))
        a('            </table>')
        a('        </div>')
    a('    </div>')
    a('')
    # ---- 跨分类说明 ----
    a('    <div class="section">')
    a('        <h2>💻 线上不只是这 8 款</h2>')
    a('        <p>全库带<strong>「线上场景 / 远程场景」改造段</strong>的游戏共 <strong>14 款</strong>，'
      '除了本页这 8 款，还有 6 款落在别的分类里 —— '
      '它们各自都写好了「搬到线上怎么玩」，按分类挑会漏掉它们：</p>')
    a('        <table class="data-table">')
    a('            <tr><th>分类</th><th>游戏</th><th>它的线上改造</th></tr>')
    for href, cat, name, how in CROSS:
        a('            <tr><td class="cat">%s</td><td><a href="%s">%s</a></td>'
          '<td>%s</td></tr>' % (cat, href, name, how))
    a('        </table>')
    a('        <blockquote>这 14 款之所以标了「线上场景」却不归在线上分类，'
          '是因为它们各自还有<strong>更主要的训练目标</strong>（协作 / 沟通 / 破冰 / 领导力）—— '
      '线上只是它们的一个用法。如果你要的是「专为远程写的游戏」，看上面 8 款；'
      '如果要的是「顺便能在线上开一把」，它们才是主角。</blockquote>')
    a('    </div>')
    a('')
    # ---- 易挑错 ----
    a('    <div class="section">')
    a('        <h2>⚠️ 四个最容易挑错的地方</h2>')
    a('        <table class="data-table">')
    a('            <tr><th>坑</th><th>为什么</th></tr>')
    a('            <tr><td><b>以为「线上」就能异步开</b></td>'
      '<td>8 款里只有 ⏳异步接力 一款是真的异步，其余 7 款都要求全员同时在线。'
      '跨时区 / 混合办公团队按「线上」分类挑，七成会直接开不起来。</td></tr>')
    a('            <tr><td><b>没试工具就开</b></td>'
      '<td>🖥️那 3 款（画图猜词 / 虚拟逃脱 / 知识竞答）全部依赖一块能多人同时操作的屏或投票工具。'
      '白板卡顿、不会用、没提前试，现场就是冷场 15 分钟。</td></tr>')
    a('            <tr><td><b>把「不用专用工具」当成「不用准备」</b></td>'
      '<td>🎤那 2 款确实零工具，但同样也不产生任何结论 —— '
      '玩完只剩笑声和几个共同点，不能拿来当主活动。</td></tr>')
    a('            <tr><td><b>按分类找线上会漏 6 款</b></td>'
      '<td>带「线上场景」改造段的共 14 款，其中 6 款（珠行万里 / 人体拼字 / 齐眉棍 / '
      '岛屿求生 / 绝密行动 / 风火轮 / 动物城大侦探 / 你说我画 / 画图接龙 / 传话游戏 / '
      '盲盒神话 / 美食挑战赛 / 沉默领袖 / 七巧板）分别在协作、沟通、破冰、领导力分类下。</td></tr>')
    a('        </table>')
    a('        <blockquote>线上游戏最大的坑不是不好玩，是<strong>「远程做不了这件事」</strong>。'
      '先确认你这半小时能备出什么，再回去挑 —— '
      '按玩法名字挑是最容易出错的方式。</blockquote>')
    a('    </div>')
    a('')
    # ---- 入口 ----
    a('    <div class="section">')
    a('        <h2>🔗 相关的入口</h2>')
    a('        <ul>')
    a('            <li><a href="index.html">全部 85 款游戏（按 8 个分类）</a> —— 💻线上分类下已有「线上怎么玩」二级筛选行</li>')
    a('            <li><a href="README.md">README 索引表</a> —— 纯文本版，这 8 款已按四组排好</li>')
    a('            <li><a href="flows/online/01-schedule.html">线上团建流程模板</a> —— 2–2.5h 完整时间轴，配套 5 款游戏</li>')
    a('            <li><a href="flows/remote-onboarding/01-schedule.html">远程新人融入半日团建</a> —— 新人场的线上版</li>')
    a('            <li><a href="toolbox/generator.html">团建方案生成器（全库版）</a> —— 有整块时间、想要一整套流程时用</li>')
    a('            <li><a href="play/tools/plan-generator/">T1 快速版生成器</a> —— 现场临时只要几个游戏，30 秒出一组</li>')
    a('            <li><a href="guide.html">教练使用指南</a> —— 第一次带远程团先读 5 分钟</li>')
    a('            <li><a href="toolbox/debrief.html">复盘引导框架</a> —— 🧾那 2 款的价值大半在复盘那 18 分钟</li>')
    a('        </ul>')
    a('    </div>')
    a('')
    a('    <div class="footer">')
    a('        <div>')
    a('            <a href="index.html" class="back-link">← 回到游戏库</a>')
    a('            <a href="README.md" class="back-link">README 索引</a>')
    a('            <a href="toolbox/generator.html" class="back-link">方案生成器</a>')
    a('        </div>')
    a('        <div style="margin-top:14px;">团建 &amp; 培训游戏库 · 线上二级索引 · 8 款 / 4 组</div>')
    a('    </div>')
    a('</div>')
    a('</body>')
    a('</html>')
    return '\n'.join(parts) + '\n'


# 每款远程要准备什么（供 online.html 表格与游戏页反向互链复用）
REMOTE_NEED = {
    'never-have-i-ever': '零 —— 会议软件 + 手指计数（用摄像头展示）',
    'online-bingo': '一张数字宾果卡（共享文档 / 在线白板 / 小程序）+ 计时器',
    'online-pictionary': '在线白板（Skribbl.io 或 Miro）+ 词表 + 计时器 + 计分表',
    'virtual-escape': '在线白板（Miro / Mural）+ 提前设计谜题链 + 计时器',
    'team-quiz': '投票工具（Kahoot / 腾讯问卷）+ 幻灯片 + 35 道题 + 计分表',
    'silent-meeting': '共享文档（每人一行发言筹码）+ 匿名便签区',
    'energy-checkin': '在线白板（能量值分栏）+ 分组会议室 + 求助券',
    'async-relay': '共享文档 + 群聊便签区（唯一的异步，45–60 min）',
}


# ---------------- 3. README.md ----------------
def patch_readme(meta):
    p = os.path.join(TB, 'README.md')
    r = rd(p)

    # 3a. 线上小节：加引言 + 按 4 组重排
    # ⚠️ 幂等做法：不管当前小节长什么样，都从「游戏行」抽出 8 款的原始数据，
    #    再整块重建。这样重复跑、或前一次跑出了半成品，都能自愈。
    # ⚠️ 坑：整块替换时**不能**只替换表体（group 2）——
    #    正则里「表头后面的分隔行」是「匹配但未捕获」的，它会留在原地，
    #    结果新表（自带表头）插在旧分隔行之后 → 表头出现两次。
    #    所以要连表头一起替换（group 1 起算）。
    m = re.search(r'#### 💻 线上团建（online）\n(.*?)(?=\n(?:## |---))', r, re.S)
    assert m, '未找到 README 线上小节'
    seg = m.group(0)

    # 从当前小节里抽出 8 款游戏的原始行（表头重复 / 中间插入说明行都不影响）
    rows = {}
    for line in seg.split('\n'):
        mm = re.match(r'\|\s*\[([^\]]+)\]\(games/online/([a-z0-9-]+)\.md\)\s*'
                      r'\|([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\|', line)
        if mm:
            rows[mm.group(2)] = (mm.group(1), mm.group(3).strip(), mm.group(4).strip(),
                                 mm.group(5).strip(), mm.group(6).strip())
    assert len(rows) == 8, 'README 线上小节里只找到 %d 款游戏行 != 8' % len(rows)

    new_intro = (
        '> 远程 / 混合办公专用，含 rich HTML 版（2026-09-01 补齐）。'
        '本节已按**「远程这一局怎么玩」**重排为 4 组（不用专用工具 / 要一块共享屏 / '
        '要一份文档承载 / 不用同时在线）；不确定选哪组时先看 '
        '[线上挑款指南](online.html)（含 30 秒决策表与「什么时候别选它」）。')
    table = ['| 游戏名称 | 形式 | 人数 | 时长 | 场景标签 |',
             '|---------|------|------|------|---------|']
    for g in GROUPS:
        table.append('| **%s %s（%d 款）** | | | | |' % (g['icon'], g['name'], len(g['ids'])))
        for gid in g['ids']:
            name, form, ppl, dur, tags = rows[gid]
            table.append('| [%s](games/online/%s.md) | %s | %s | %s | %s |'
                         % (name, gid, form, ppl, dur, tags))
    # 跨分类说明放在**整张表之后**（不是某一行后面 —— 表格中间的引用行会把表截断）
    table.append('')
    table.append('> 全库带「线上场景 / 远程场景」改造段的共 **14 款**，'
                 '本页这 8 款之外还有 6 款落在别的分类里'
                 '（🤝协作：珠行万里 / 人体拼字 / 齐眉棍 / 岛屿求生 / 绝密行动 / 风火轮；'
                 '💬沟通：动物城大侦探 / 你说我画 / 画图接龙 / 传话游戏；'
                 '🧊破冰：盲盒神话 / 美食挑战赛；👑领导力：沉默领袖 / 七巧板）'
                 '——按分类挑会漏掉它们，详见 [线上挑款指南](online.html)。')
    new_section = ('#### 💻 线上团建（online）\n' + new_intro + '\n' + '\n'.join(table) + '\n')
    r = r[:m.start()] + new_section + r[m.end():]

    # 3b. 决策表补一行（幂等：已存在就跳过）
    old_row = ('| 🧊 目的就是开场破冰，但 8 款挑不过来 | [破冰挑款指南](ice.html) | '
               '按「破冰之后留下什么」把 8 款分成 4 组（名字 / 笑声 / 私事 / 配合），'
               '每组给了首选与「什么时候别选它」；首页选「🧊 破冰」会出现同样的 4 个子类按钮 |\n')
    assert r.count(old_row) == 1, 'README 决策表破冰行锚点未命中'
    new_row = ('| 💻 目的就是远程团建，但 8 款挑不过来 | [线上挑款指南](online.html) | '
               '按「远程这一局怎么玩」把 8 款分成 4 组（不用专用工具 / 要一块共享屏 / '
               '要一份文档承载 / 不用同时在线），每组给了首选与「什么时候别选它」；'
               '首页选「💻 线上」会出现同样的 4 个子类按钮 |\n')
    if new_row not in r:
        r = r.replace(old_row, old_row + new_row)

    # 3c. 网页版清单 +1 条（幂等）
    # ⚠️ 这行用的是 .html 链接（引导话术库 → toolbox/facilitation.html），
    #    不是 .md —— 照抄成 .md 找不到锚点。
    old_list = '[破冰挑款指南](ice.html) · [引导话术库](toolbox/facilitation.html)'
    new_list = '[破冰挑款指南](ice.html) · [线上挑款指南](online.html) · [引导话术库](toolbox/facilitation.html)'
    if new_list not in r:
        assert r.count(old_list) == 1, 'README 网页版清单锚点未命中'
        r = r.replace(old_list, new_list)

    wr(p, r)
    print('README.md 线上小节已按 4 组重排 + 决策表 +1 行 + 网页版清单 +1 条')


def main():
    meta = collect()
    patch_index()
    html = build_online_html(meta)
    wr(os.path.join(TB, 'online.html'), html)
    print('online.html 已生成：%d 行 / 4 组 / 跨分类 %d 款'
          % (html.count('\n'), len(CROSS)))
    patch_readme(meta)


if __name__ == '__main__':
    main()
