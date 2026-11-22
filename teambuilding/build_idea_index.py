# -*- coding: utf-8 -*-
"""创意与解题类二级索引 / 挑款指南（2026-10-26 自动化第四十次）

背景（ROADMAP 下一步建议 · 2026-10-25 首选）：
    协作之外的 46 款仍无二级索引。💡创新思维(5) + 🔧问题解决(5) 共 10 款在
    index.html 共用 grid-creativity 一个网格 —— 是协作之外最大的一块，且
    「创新」与「解决问题」最常被混为一谈（教练按分类挑，经常挑错）。

做法：把这 10 款按「团队当下卡在哪一步」重切成 4 组，横跨 💡/🔧 两个分类：
  1) index.html 拆成 grid-creativity(5) + grid-problem-solving(5)，
     补上一直缺失的「🔧 解题」分类按钮；卡片按组重排 + 加「肌肉」标签胶囊
     + 新增「卡在哪一步」二级筛选行（跨两个网格生效）
  2) 新建 idea.html 挑款专页（30 秒决策表 + 创新vs解题边界说明 + 4 组详解）
  3) README.md 两节合并重排为 4 组，并加「分类」列把边界摆在明面上

复用原则（经验 91：A 页介绍 B 内容，一律复用 B 的原文）：
    每款的一句话描述 / 人数 / 时长 / 形式 / 场景标签全部从 index.html 与
    README.md 现成表格抽取，不另写一份。

用法：
    python teambuilding/build_idea_index.py
幂等：index.html 已带 data-idea / README 已重排时会跳过相应部分。
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

# ---------------- 分组定义（顺序即排序顺序，也是「卡在哪一步」的推进顺序） ----------------
GROUPS = [
    {
        'key': 'define', 'icon': '🔍', 'name': '先定义问题，再动手', 'short': '先定义问题',
        'tag': '最贵的错误不是解不出来，是解错了题',
        'lead': '最贵的错误不是解不出来，是解错了题——这两款都把「先说清要解决什么」'
                '设成一道不许跳过的闸门。',
        'when': '需求方自己也说不清要什么 / 复盘总在争「到底是谁的问题」/'
                '上一轮做完的东西没人认账。',
        'avoid': '已经明确到「做什么都定了」的阶段别选——这两款的开场就是逼你把问题'
                 '重写一遍，没有歧义可挖时会空转。',
        'pick': 'cyber-maze',
        'ids': ['cyber-maze', 'witches-garden'],
    },
    {
        'key': 'hypothesis', 'icon': '🧪', 'name': '试错之前，先写下赌注', 'short': '先写赌注',
        'tag': '试错本身不产生价值，带着假设的试错才产生价值',
        'lead': '试错本身不产生价值，带着假设的试错才产生价值——这三款都要求动手之前'
                '先落一笔「我们以为是 X」，事后拿结果对账。',
        'when': '每次试完都说不出学到了什么 / 复盘只剩一句「下次注意」/'
                '想练「敢不敢承认自己猜错了」。',
        'avoid': '只有 45 分钟、或者这次只想玩个痛快的时候别选——这三款的价值都在'
                 '复盘那 15–20 分钟，游戏部分反而最省事。',
        'pick': 'newspaper-tower',
        'ids': ['newspaper-tower', 'egg-drop', 'arctic-expedition'],
    },
    {
        'key': 'constraint', 'icon': '⛓️', 'name': '资源不够：在限制下取舍', 'short': '限制下取舍',
        'tag': '资源不是借口，是设计输入',
        'lead': '资源不是借口，是设计输入——这三款把预算、材料或行动力卡死，逼你在剩下的'
                '缝里想办法，而且每次取舍都要记进账本。',
        'when': '项目永远缺人缺钱缺时间 / 团队习惯说「等条件齐了再开始」/'
                '要练「每一份资源换回了什么」。',
        'avoid': '团队正处在士气低的时候别选——硬上限会被当成压力而不是约束，'
                 '先把气氛做起来再用。',
        'pick': '10-yuan-idea',
        'ids': ['10-yuan-idea', 'another-world-workshop', 'treasure-hunter'],
    },
    {
        'key': 'deliberate', 'icon': '🕰️', 'name': '别急着定：先留一块余地', 'short': '先留余地',
        'tag': '「等不及」和「排太满」是同一个毛病的两种长相',
        'lead': '「等不及」和「排太满」是同一个毛病的两种长相——这两款都故意给团队留一块'
                '不许动的余地：一个人先独立想清楚，大家先别把格子占满。',
        'when': '开会一上来就随大流 / 什么都要今天做完 / 讨论完的结论总不如某个人的判断。',
        'avoid': '必须当场拍板定死的场合别选——这两款都要留出「再想一轮」的时间，'
                 '跟硬截止日期冲突。',
        'pick': 'desert-survival',
        'ids': ['desert-survival', 'enchanted-garden'],
    },
]

# 决策表：你现在的麻烦 → 去哪一组 → 直接拿这款
DECIDE = [
    ('需求方自己都说不清要什么', 'define', 'witches-garden'),
    ('事故复盘卡在「到底是什么原因」', 'define', 'cyber-maze'),
    ('每次试完都说不出学到了什么', 'hypothesis', 'newspaper-tower'),
    ('团队习惯说「等条件齐了再开始」', 'constraint', '10-yuan-idea'),
    ('开会一上来就随大流，散会各干各的', 'deliberate', 'desert-survival'),
]

# 分类标签（把「创新 vs 解题」的边界摆在每一行上）
CAT_LABEL = {'creativity': '💡 创新思维', 'problem-solving': '🔧 问题解决'}

# 配色：hue 73（全站 110 页里 60↔86 之间 26° 空档的中点），HSL 单色相派生
C = {
    'primary': '#8a7f1e', 'mid': '#a89c2e', 'light': '#c8bc5a',
    'bg': '#121005', 'container': '#1e1a09', 'gridbg': '#0d0b03',
    'border': '#463f1c', 'text': '#e6e2c9', 'muted': '#b0a888',
    'quote': '#2c2711',
}


# ---------------- 工具（经验 81/87：整块替换前必须断言锚点唯一且命中） ----------------
def rd(p):
    """读入并统一成 '\\n'（universal newlines）。写回时再统一转 CRLF。"""
    return io.open(p, encoding='utf-8').read()


def wr(p, s, crlf=True):
    """写回。index.html / README.md / idea.html 全站统一 CRLF（与 collab.html 一致）。"""
    if crlf:
        s = s.replace('\r\n', '\n').replace('\n', '\r\n')
    io.open(p, 'w', encoding='utf-8', newline='').write(s)


def rep(text, old, new, what):
    assert text.count(old) == 1, '锚点不唯一(%d)或未命中: %s' % (text.count(old), what)
    return text.replace(old, new)


def short_people(s):
    """README 里的人数常带「（4–8人/组）」后缀，展示时取主数值。"""
    return re.sub(r'（[^）]*）\s*$', '', s).strip()


# ---------------- 采集现成数据（一律复用，不另写） ----------------
def collect():
    """从 README.md 取 名称/形式/人数/时长/场景标签，从 index.html 取 标题与一句话描述。

    README 的这 10 款在本脚本跑之前是 5 列（无「分类」列），跑之后是 6 列 ——
    两种都要能解析，否则脚本不可重跑。所以这里先抓「名称 + 后面所有格」，
    再判断首格是不是「分类」标签来还原列序。
    """
    rm = rd(os.path.join(TB, 'README.md'))
    meta = {}
    for m in re.finditer(
            r'\|\s*\[([^\]]+)\]\(games/(creativity|problem-solving)/([a-z0-9-]+)\.md\)\s*'
            r'((?:\|[^|\n]*){4,5})\|', rm):
        gid = m.group(3)
        cells = [c.strip() for c in m.group(4).split('|')[1:]]
        if cells and cells[0] in CAT_LABEL.values():   # 6 列格式：首格是「分类」标签
            cells = cells[1:]
        assert len(cells) == 4, 'README 行 %s 列数 %d != 4' % (gid, len(cells))
        meta[gid] = {
            'name': m.group(1), 'cat': m.group(2), 'form': cells[0],
            'people': cells[1], 'dur': cells[2], 'tags': cells[3],
            'people_short': short_people(cells[1]),
        }
    idx = rd(os.path.join(TB, 'index.html'))
    for m in re.finditer(
            r'<a href="games/(?:creativity|problem-solving)/([a-z0-9-]+)\.html" '
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
    return meta


# ---------------- 1. index.html ----------------
def patch_index(meta):
    p = os.path.join(TB, 'index.html')
    h = rd(p)
    if 'data-idea=' in h:
        print('index.html 已含肌肉标签，跳过')
        return

    # 1a. 取出 grid-creativity 内的 10 张卡片
    # 用网格切块定位原网格整体（开标签 → 收尾 </div>），只替换这一段。
    # 注意收尾的 </div> 属于被替换的网格，必须一起吃掉 —— 否则会多出一个 </div>
    # （结构校验会报「不匹配: 期望 </body> 实得 </div>」）。
    s = h.find('    <div class="grid" id="grid-creativity">')
    assert s > 0, '未找到 grid-creativity 开标签'
    gt = h.find('>', s) + 1
    depth, i = 1, gt
    pat = re.compile(r'<div\b|</div>')
    while depth > 0:
        m = pat.search(h, i)
        assert m, 'grid-creativity 未闭合'
        depth += 1 if m.group().startswith('<div') else -1
        i = m.end()
    end = i - len('</div>')
    body = h[gt:end]

    # 卡片以「      <a href="games/…」开头。网格内共 10 个 </a>（卡片内无嵌套 <a>），
    # 所以非贪婪匹配到第一个 </a> 即为整张卡；不要加「后面必须跟换行」的前瞻——
    # 最后一张卡的 </a> 后面直接接网格的 </div>，加前瞻会漏掉它（经验 99）。
    CARD = re.compile(r'<a href="games/(?:creativity|problem-solving)/([a-z0-9-]+)\.html" '
                      r'class="card"[^>]*>.*?</a>', re.S)
    cards = {}
    order = []
    for m in CARD.finditer(body):
        cards[m.group(1)] = m.group(0)
        order.append(m.group(1))
    assert len(cards) == 10, '创意网格卡片数 %d != 10' % len(cards)
    assert body.count('</a>') == 10, '网格内 </a> 数 %d != 10（卡片内有嵌套 a？）' % body.count('</a>')

    sub_of = {}
    for g in GROUPS:
        for gid in g['ids']:
            assert gid in cards, '分组引用了网格里没有的游戏: ' + gid
            assert gid not in sub_of, '游戏同时属于多组: ' + gid
            sub_of[gid] = g['key']
    assert set(sub_of) == set(cards), '分组与卡片集合不一致: %s' % (set(sub_of) ^ set(cards))

    gk = {g['key']: g for g in GROUPS}

    def rebuild(ids):
        """重排卡片：加 data-idea、加肌肉标签胶囊。原卡片缩进 6 空格、每张一行。"""
        out = ''
        for gid in ids:
            c = cards[gid]
            g = gk[sub_of[gid]]
            c2 = c.replace(' class="card" data-people=',
                           ' class="card" data-idea="%s" data-people=' % g['key'], 1)
            assert c2 != c, 'data-idea 未插入: ' + gid
            chip = '<span class="tag">%s %s</span>' % (g['icon'], g['short'])
            c2, n = re.subn(r'(<div class="card-tags">)(.*?)(</div>)',
                            lambda mm: mm.group(1) + mm.group(2) + chip + mm.group(3),
                            c2, count=1, flags=re.S)
            assert n == 1, 'card-tags 未命中: ' + gid
            out += '      ' + c2 + '\n'
        return out

    def by_group(ids):
        out = []
        for g in GROUPS:
            out += [gid for gid in ids if sub_of[gid] == g['key']]
        return out

    crea_ids = [gid for gid in order if meta[gid]['cat'] == 'creativity']
    prob_ids = [gid for gid in order if meta[gid]['cat'] == 'problem-solving']
    assert len(crea_ids) == 5 and len(prob_ids) == 5, \
        '分类拆分失败：💡%d 🔧%d' % (len(crea_ids), len(prob_ids))

    # 1b. 替换「原注释 + 原标题 + 原网格」整块 → 两个新网格
    c_start = h.find('    <!-- 创意与解决问题 -->')
    assert c_start > 0 and c_start < s, '未找到原「创意与解决问题」注释'
    new_block = (
        '    <!-- 创新思维 -->\n'
        '    <div style="font-weight:600;color:#555;margin:18px 0 10px;">'
        '💡 创新思维（creativity）'
        ' <span style="font-weight:400;">· 5 款 · 想按「卡在哪一步」挑，见 '
        '<a href="idea.html" style="color:#3366cc;">创意与解题挑款指南</a></span></div>\n'
        '    <div class="grid" id="grid-creativity">\n'
        + rebuild(by_group(crea_ids)) +
        '    </div>\n'
        '\n'
        '    <!-- 问题解决 -->\n'
        '    <div style="font-weight:600;color:#555;margin:18px 0 10px;">'
        '🔧 问题解决（problem-solving）'
        ' <span style="font-weight:400;">· 5 款 · 与 💡 创新思维共用一套挑款指南，见 '
        '<a href="idea.html" style="color:#3366cc;">创意与解题挑款指南</a></span></div>\n'
        '    <div class="grid" id="grid-problem-solving">\n'
        + rebuild(by_group(prob_ids)) +
        '    </div>\n'
    )
    h = h[:c_start] + new_block + h[end + len('</div>'):]

    # 1c. 补上一直缺失的「🔧 解题」分类按钮
    h = rep(h,
            '      <button class="filter-btn" onclick="toggleFilter(\'category\', \'creativity\', this)">💡 创意</button>\n',
            '      <button class="filter-btn" onclick="toggleFilter(\'category\', \'creativity\', this)">💡 创意</button>\n'
            '      <button class="filter-btn" onclick="toggleFilter(\'category\', \'problem-solving\', this)">🔧 解题</button>\n',
            '分类按钮（补 问题解决）')

    # 1d. 新增「卡在哪一步」二级筛选行（跨 💡/🔧 两个网格生效）
    h = rep(h,
            '    <div class="filter-group">\n      <span class="filter-label">人数：</span>',
            '    <div class="filter-group" id="idea-filter" style="display:none;">\n'
            '      <span class="filter-label">卡在哪一步：</span>\n'
            '      <button class="filter-btn active" onclick="toggleFilter(\'idea\', \'all\', this)">全部</button>\n'
            + ''.join('      <button class="filter-btn" onclick="toggleFilter(\'idea\', \'%s\', this)">%s %s</button>\n'
                      % (g['key'], g['icon'], g['short']) for g in GROUPS) +
            '    </div>\n'
            '    <div class="filter-group">\n      <span class="filter-label">人数：</span>',
            '卡在哪一步筛选行')

    # 1e. JS：状态 + 显隐 + 过滤
    h = rep(h,
            "var currentFilters = {\n  category: 'all',\n  people: 'all',\n  duration: 'all',\n  sub: 'all'\n};",
            "var currentFilters = {\n  category: 'all',\n  people: 'all',\n  duration: 'all',\n  sub: 'all',\n  idea: 'all'\n};",
            'JS currentFilters')

    h = rep(h,
            "function resetSub() {",
            "// 💡创新思维 + 🔧问题解决 共 10 款、跨两个网格，第二级筛选只在选中这两类时出现\n"
            "function setIdeaRow(on) {\n"
            "  var row = document.getElementById('idea-filter');\n"
            "  if (row) { row.style.display = on ? '' : 'none'; }\n"
            "}\n\n"
            "function resetIdea() {\n"
            "  currentFilters.idea = 'all';\n"
            "  var row = document.getElementById('idea-filter');\n"
            "  if (!row) { return; }\n"
            "  row.querySelectorAll('.filter-btn').forEach(function(b) {\n"
            "    if (b.textContent === '全部') { b.classList.add('active'); }\n"
            "    else { b.classList.remove('active'); }\n"
            "  });\n"
            "}\n\n"
            "function resetSub() {",
            'JS idea 筛选函数')

    h = rep(h,
            "  // 切走协作时把子类筛选项一并复位，否则下次再点协作会带着上次的条件\n"
            "  if (type === 'category') {\n"
            "    if (value !== 'collaboration') { resetSub(); setSubRow(false); }\n"
            "    else { setSubRow(true); }\n"
            "  }\n",
            "  // 切走协作时把子类筛选项一并复位，否则下次再点协作会带着上次的条件\n"
            "  if (type === 'category') {\n"
            "    if (value !== 'collaboration') { resetSub(); setSubRow(false); }\n"
            "    else { setSubRow(true); }\n"
            "    // 「卡在哪一步」只在 💡创意 / 🔧解题 时出现；离开这两类才复位\n"
            "    // （两类之间切换时保留 —— 因为每组都横跨两个分类）\n"
            "    if (value === 'creativity' || value === 'problem-solving') { setIdeaRow(true); }\n"
            "    else { resetIdea(); setIdeaRow(false); }\n"
            "  }\n",
            'JS toggleFilter 联动')

    h = rep(h,
            "      // 协作子类筛选（仅协作分类下的 6 组）\n",
            "      // 「卡在哪一步」筛选：💡创意 + 🔧解题 共 10 款，跨两个网格\n"
            "      if (visible && currentFilters.idea !== 'all') {\n"
            "        if (card.getAttribute('data-idea') !== currentFilters.idea) {\n"
            "          visible = false;\n"
            "        }\n"
            "      }\n\n"
            "      // 协作子类筛选（仅协作分类下的 6 组）\n",
            'JS idea 过滤')

    # 1f. 首屏胶囊：加创意与解题挑款入口
    h = rep(h,
            '        <a href="collab.html" class="res-chip">🤝 协作有 39 款，帮我挑</a>\n',
            '        <a href="collab.html" class="res-chip">🤝 协作有 39 款，帮我挑</a>\n'
            '        <a href="idea.html" class="res-chip">💡 创意与解题共 10 款，帮我挑</a>\n',
            '首屏胶囊')

    wr(p, h)
    print('index.html 已更新：拆分 💡5 / 🔧5 两网格、%d 组肌肉标签、补「🔧 解题」按钮与「卡在哪一步」筛选行'
          % len(GROUPS))


# ---------------- 2. idea.html ----------------
CSS = """
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.6; color: %(text)s;
        background: linear-gradient(135deg, %(bg)s 0%%, #171305 55%%, #221c08 100%%);
        padding: 20px;
    }
    .container {
        max-width: 1100px; margin: 0 auto; background: %(container)s;
        border-radius: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.7);
        overflow: hidden; border: 1px solid %(border)s;
    }
    .header {
        background: linear-gradient(135deg, %(primary)s 0%%, %(mid)s 45%%, %(light)s 100%%);
        color: #141104; padding: 40px; text-align: center;
    }
    .header h1 { font-size: 2.1em; margin-bottom: 10px; text-shadow: 0 1px 3px rgba(255,255,255,0.35); }
    .header .subtitle { font-size: 1.05em; opacity: 0.92; }
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
    .data-table th { background: %(primary)s; color: #141104; padding: 12px; text-align: left; font-size: 0.95em; }
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
    .when-box { background: #26210b; border: 1px solid %(border)s; }
    .avoid-box { background: #2a1410; border: 1px solid #7a3a2a; }
    .when-box b { color: %(light)s; }
    .avoid-box b { color: #e8917a; }
    .pick {
        display: inline-block; margin-bottom: 14px; padding: 8px 16px; border-radius: 20px;
        background: %(primary)s; color: #141104; font-size: 0.92em; font-weight: 600;
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
        background: %(primary)s; color: #141104; text-decoration: none; border-radius: 20px; font-size: 0.9em;
    }
    .back-link:hover { background: %(light)s; }
</style>
""" % C


def build_idea_html(meta):
    parts = []
    a = parts.append
    a('<!DOCTYPE html>')
    a('<html lang="zh-CN">')
    a('<head>')
    a('    <meta charset="UTF-8">')
    a('    <meta name="viewport" content="width=device-width, initial-scale=1.0">')
    a('    <title>创意与解题挑款指南 · 10 款分成 4 组 - 团建 & 培训游戏库</title>')
    a(CSS)
    a('</head>')
    a('<body>')
    a('<div class="container">')
    a('    <div class="header">')
    a('        <h1>💡 创意与解题挑款指南</h1>')
    a('        <div class="subtitle">💡创新思维 5 款 + 🔧问题解决 5 款 —— 按「团队当下卡在哪一步」重切成 4 组</div>')
    a('        <div class="tag">10 款 · 4 组 · 每组给了首选与「什么时候别选它」</div>')
    a('    </div>')
    a('')
    a('    <div class="info-grid">')
    for icon, label, value in (('🎲', '覆盖范围', '10 款（💡创新 5 + 🔧解题 5）'),
                               ('🧭', '分组口径', '按「卡在哪一步」分 4 组'),
                               ('⚡', '最快的一款', '报纸塔挑战 30–40 min'),
                               ('👥', '人数跨度', '6 人 ～ 40 人')):
        a('        <div class="info-card"><div class="icon">%s</div>'
          '<div class="label">%s</div><div class="value">%s</div></div>' % (icon, label, value))
    a('    </div>')
    a('')
    a('    <div class="section">')
    a('        <h2>⚡ 30 秒挑款：你现在卡在哪一步</h2>')
    a('        <p>不用读完全页。找到你此刻的处境，直接拿最后那款；想再看同类，点组名跳下去。</p>')
    a('        <table class="data-table">')
    a('            <tr><th>你现在的麻烦</th><th>去哪一组</th><th>直接拿这款</th></tr>')
    gk = {g['key']: g for g in GROUPS}
    for trouble, key, gid in DECIDE:
        g = gk[key]
        m = meta[gid]
        a('            <tr><td>%s</td><td><a href="#g-%s">%s %s</a></td>'
          '<td><a href="games/%s/%s.html">%s</a> <span style="color:%s;">（%s / %s）</span></td></tr>'
          % (trouble, key, g['icon'], g['name'], m['cat'], gid, m['title'], C['muted'],
             m['people_short'], m['dur']))
    a('        </table>')
    a('        <blockquote>四组是按<strong>「团队当下卡在哪一步」</strong>切的，不是按💡/🔧两个文件夹切的。'
      '同一个文件夹里的两款可能差三步，同一步上的两款可能分属不同分类 —— 这正是「创新」与'
      '「解决问题」最常被混为一谈的原因。</blockquote>')
    a('    </div>')
    a('')
    # 边界说明（本次二级索引的核心：把混淆讲清）
    a('    <div class="section">')
    a('        <h2>🔀 创新 vs 解题：不是两个抽屉</h2>')
    a('        <p>「创新思维」和「问题解决」这两个名字说的是<strong>产出物</strong>，'
      '不是<strong>练的动作</strong>——所以按名字挑，几乎一定会挑错。</p>')
    a('        <table class="data-table">')
    a('            <tr><th></th><th>💡 创新思维（5 款）</th><th>🔧 问题解决（5 款）</th></tr>')
    a('            <tr><td><b>产出的是什么</b></td>'
      '<td>一个从无到有的东西（作品、方案、机制）</td>'
      '<td>一个被解决掉的具体障碍（故障、瓶颈、卡点）</td></tr>')
    a('            <tr><td><b>成功长什么样</b></td>'
      '<td>「原来还能这样」——有人愿意用它</td>'
      '<td>「原来卡在这儿」——绕过去而且说得清为什么</td></tr>')
    a('            <tr><td><b>失败长什么样</b></td>'
      '<td>做出来了但没人要 / 做错了问题</td>'
      '<td>修好了但不知道为什么修好</td></tr>')
    a('            <tr><td><b>最容易混在哪</b></td>'
      '<td>需求没对齐，却以为是自己「创新不够」</td>'
      '<td>复盘没沉淀，却以为是「方案不行」</td></tr>')
    a('        </table>')
    a('        <p style="margin-top:18px;">把四组横过来看，边界就清楚了 —— '
      '<strong>每一组都同时横跨💡与🔧两个分类</strong>：</p>')
    a('        <table class="data-table">')
    a('            <tr><th>卡在哪一步</th><th>💡 创新思维</th><th>🔧 问题解决</th></tr>')
    for g in GROUPS:
        crea = [gid for gid in g['ids'] if meta[gid]['cat'] == 'creativity']
        prob = [gid for gid in g['ids'] if meta[gid]['cat'] == 'problem-solving']
        a('            <tr><td><a href="#g-%s">%s %s</a></td><td>%s</td><td>%s</td></tr>'
          % (g['key'], g['icon'], g['name'],
             '、'.join(meta[gid]['title'] for gid in crea) or '—',
             '、'.join(meta[gid]['title'] for gid in prob) or '—'))
    a('        </table>')
    a('        <blockquote>所以挑款时问的应该是「<strong>我们此刻卡在哪一步</strong>」，'
      '而不是「这算创新还是算解题」。💡那 5 款里只有 2 款在练「从限制里挤出东西」；'
      '🔧那 5 款里也只有 1 款真的在查因。</blockquote>')
    a('    </div>')
    a('')
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
        a('            <div class="pick">🎯 拿不准就先拿：<a href="games/%s/%s.html" '
          'style="color:#141104;text-decoration:underline;">%s</a>（%s / %s）</div>'
          % (pick['cat'], g['pick'], pick['title'], pick['people_short'], pick['dur']))
        a('            <table class="data-table">')
        a('                <tr><th>游戏</th><th>分类</th><th>人数</th><th>时长</th>'
          '<th>这一款在练什么</th></tr>')
        for gid in g['ids']:
            m = meta[gid]
            a('                <tr><td><a href="games/%s/%s.html">%s</a></td>'
              '<td class="cat">%s</td><td>%s</td><td>%s</td><td>%s</td></tr>'
              % (m['cat'], gid, m['title'], CAT_LABEL[m['cat']],
                 m['people_short'], m['dur'], m['desc']))
        a('            </table>')
        a('        </div>')
    a('    </div>')
    a('')
    a('    <div class="section">')
    a('        <h2>⚠️ 三个最容易挑错的地方</h2>')
    a('        <table class="data-table">')
    a('            <tr><th>坑</th><th>为什么</th></tr>')
    a('            <tr><td><b>想做创新，别在「创新思维」里挑齐</b></td>'
      '<td>💡那 5 款里只有 2 款（10元买创意、异世界工坊）在练「从限制里挤出东西」；'
      '另 3 款（报纸塔挑战、女巫花园、魔法花园）练的其实是假设、定义与留白 —— '
      '这三样在🔧那 5 款里同样能练到。</td></tr>')
    a('            <tr><td><b>问题解决 ≠ 查原因</b></td>'
      '<td>🔧那 5 款里只有赛博迷宫一款真的在查因。其余 4 款练的是带假设的试错'
      '（鸡蛋坠落、极地探险）、在限制下取舍（宝藏猎人）、别急着拍板（沙漠逃生）。</td></tr>')
    a('            <tr><td><b>时间不够时可选的只有 3 款</b></td>'
      '<td>报纸塔挑战（30–40 min）、10元买创意（30–45 min）、沙漠逃生（30–45 min）'
      '能在 45 分钟内收尾；其余 7 款都要 45 分钟以上，其中 4 款要 60 分钟以上、'
      '女巫花园与宝藏猎人要 70 分钟以上。</td></tr>')
    a('        </table>')
    a('        <blockquote>这 10 款占全库 12%，却横跨「产出新东西」和「解决旧问题」两种完全不同的'
      '目标。先确认你要的是哪一个，再回到四组里挑 —— 按文件名挑是最容易出错的方式。</blockquote>')
    a('    </div>')
    a('')
    a('    <div class="section">')
    a('        <h2>🔗 相关的入口</h2>')
    a('        <ul>')
    a('            <li><a href="index.html">全部 85 款游戏（按 8 个分类）</a> —— '
      '💡创意与🔧解题已拆成两个分类入口，各自 5 款</li>')
    a('            <li><a href="README.md">README 索引表</a> —— 纯文本版，这 10 款已按四组排好</li>')
    a('            <li><a href="toolbox/generator.html">团建方案生成器（全库版）</a> —— '
      '有整块时间、想要一整套流程时用</li>')
    a('            <li><a href="play/tools/plan-generator/">T1 快速版生成器</a> —— '
      '现场临时只要几个游戏，30 秒出一组</li>')
    a('            <li><a href="guide.html">教练使用指南</a> —— 第一次带团先读 5 分钟</li>')
    a('            <li><a href="toolbox/debrief.html">复盘引导框架</a> —— '
      '这 10 款的价值大半在复盘那 15–30 分钟</li>')
    a('        </ul>')
    a('    </div>')
    a('')
    a('    <div class="footer">')
    a('        <div>')
    a('            <a href="index.html" class="back-link">← 回到游戏库</a>')
    a('            <a href="README.md" class="back-link">README 索引</a>')
    a('            <a href="toolbox/generator.html" class="back-link">方案生成器</a>')
    a('        </div>')
    a('        <div style="margin-top:14px;">团建 & 培训游戏库 · 创意与解题二级索引 · 10 款 / 4 组</div>')
    a('    </div>')
    a('</div>')
    a('</body>')
    a('</html>')
    text = '\n'.join(parts) + '\n'
    p = os.path.join(TB, 'idea.html')
    wr(p, text)
    print('idea.html 已生成：%d 行 / 4 组 / 10 款' % text.count('\n'))


# ---------------- 3. README.md ----------------
def patch_readme(meta):
    p = os.path.join(TB, 'README.md')
    rm = rd(p)
    if '#### 💡 创意与解题（creativity & problem-solving）' in rm:
        print('README.md 已重排，跳过')
        return

    m_head = re.search(r'^#### 💡 创新思维（creativity）$', rm, re.M)
    assert m_head, 'README 未找到创新思维小节'
    m_next = re.search(r'^#### 💻 线上团建（online）$', rm, re.M)
    assert m_next and m_next.start() > m_head.end(), 'README 未找到线上团建小节'

    # 先把两节的原始行抽出来（复用现成文案，不重写）
    # 注意行内格式是「| [名称](路径) | 形式 | 人数 | 时长 | 场景标签 |」——
    # 链接与第一个「|」之间有一个空格，后缀要用 \s* 吃掉它（否则整行匹配不上）
    sec = rm[m_head.start():m_next.start()]
    rows = {}
    for line in sec.split('\n'):
        m = re.match(r'\| \[([^\]]+)\]\(games/(creativity|problem-solving)/([a-z0-9-]+)\.md\)'
                     r'\s*((?:\|[^|]*){4})\|', line)
        if m:
            rows[m.group(3)] = (m.group(1), m.group(2), m.group(4))
    assert len(rows) == 10, 'README 创意+解题表 %d 行 != 10' % len(rows)

    new = ('#### 💡 创意与解题（creativity & problem-solving）\n'
           '\n'
           '> 这 10 款在首页曾共用一个网格，💡创新思维与🔧问题解决最常被混为一谈。'
           '本节已按**「团队当下卡在哪一步」**重排为 4 组（每组都横跨💡/🔧两个分类）；'
           '不确定选哪组时先看 [创意与解题挑款指南](idea.html)（含 30 秒决策表与「什么时候别选它」）。\n'
           '\n'
           '| 游戏名称 | 分类 | 形式 | 人数 | 时长 | 场景标签 |\n'
           '|---------|------|------|------|------|---------|\n')
    for g in GROUPS:
        new += ('| **%s %s（%d 款）** | | | | | |\n'
                % (g['icon'], g['name'], len(g['ids'])))
        for gid in g['ids']:
            name, cat, rest = rows[gid]
            # rest = '| 形式 | 人数 | 时长 | 场景标签'（末格前有空格），原样保留，
            # 只在前面插入「分类」列
            new += '| [%s](games/%s/%s.md) | %s %s |\n' % (
                name, cat, gid, CAT_LABEL[cat], rest.rstrip())
    new += '\n'

    rm = rm[:m_head.start()] + new + rm[m_next.start():]

    # 决策表补一行
    rm = rep(rm,
              '| 🤝 目的就是协作，但 39 款挑不过来 | [协作类挑款指南](collab.html) |',
              '| 💡 目的就是创新或解题，但 10 款挑不过来 | [创意与解题挑款指南](idea.html) | '
              '按「卡在哪一步」把 10 款分成 4 组，每组给了首选与「什么时候别选它」；'
              '首页选「💡 创意」或「🔧 解题」都会看到同一份口径 |\n'
              '| 🤝 目的就是协作，但 39 款挑不过来 | [协作类挑款指南](collab.html) |',
              'README 决策表')

    # 网页版资源清单补一条
    rm = rep(rm,
              '· [协作类挑款指南](collab.html) ·',
              '· [协作类挑款指南](collab.html) · [创意与解题挑款指南](idea.html) ·',
              'README 网页版清单')

    wr(p, rm)
    print('README.md 已重排：💡+🔧 两节合并为 4 组（10 款）')


def main():
    meta = collect()
    need = set()
    for g in GROUPS:
        need |= set(g['ids'])
    miss = [gid for gid in sorted(need) if gid not in meta]
    assert not miss, '缺元信息: %s' % miss
    no_desc = [gid for gid in sorted(need) if not meta[gid].get('desc')]
    assert not no_desc, '缺一句话描述: %s' % no_desc
    patch_index(meta)
    build_idea_html(meta)
    patch_readme(meta)
    print('完成')


if __name__ == '__main__':
    main()
