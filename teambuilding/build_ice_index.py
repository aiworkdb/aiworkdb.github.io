# -*- coding: utf-8 -*-
"""破冰类二级索引 / 挑款指南（2026-10-27 自动化第四十一次）

背景（ROADMAP 下一步建议 · 2026-10-26 首选）：
    协作 39 款与创意解题 10 款都已有二级索引，剩下没做二级索引的分类里，
    **破冰 8 款**是教练最常用于开场的一类，且它的切法与前两批都不同：
      - 协作按「练哪种协作」切（练的是动作）
      - 创意解题按「团队当下卡在哪一步」切（练的是思考位置）
    破冰该按什么切？ROADMAP 给的提示是「认识彼此 / 单纯热场 / 破冰后要不要接协作」。

做法：按「**破冰之后，团队手里剩下什么**」切 4 组：
  1) 🪪 只认名字 —— 剩下「名字和人脸对上了」
  2) 🎭 只图热闹 —— 剩下「一屋子笑声」
  3) 💬 谈自己的事 —— 剩下「彼此知道对方一件私事」
  4) 🍳 带协作 —— 剩下「一支能配合的小队」
  另加一档「🧊 破冰不只是这 8 款」：全库 11 款带「破冰」场景标签，
  其中 6 款并不在 icebreaker 分类里（沟通 3 + 协作 3）。

  1) index.html 的破冰网格：8 张卡按组重排 + 加 data-ice + 肌肉标签胶囊；
     新增「破冰要什么」二级筛选行（只在选中 🧊破冰 时出现）
  2) 新建 ice.html 挑款专页（30 秒决策表 + 暴露度边界说明 + 4 组详解）
  3) README.md 破冰小节按 4 组重排

复用原则（经验 91：A 页介绍 B 内容，一律复用 B 的原文）：
    每款的一句话描述 / 人数 / 时长 / 形式 / 场景标签全部从 index.html 与
    README.md 现成表格抽取，不另写一份。

顺带修掉的静默缺口：
    - line-master 的时长在 md / README 是「30–50 min」，index.html 卡片与
      generator.html 却写「20–30 min」（同款游戏三个地方两个数）——
      统一到 md 口径 30–50 min，并同步 data-duration 分桶（short → medium）。

用法：
    python teambuilding/build_ice_index.py
幂等：index.html 已带 data-ice / README 已重排时会跳过相应部分。
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

# ---------------- 分组定义（顺序 = 从最轻到最重：先认人 → 热闹 → 讲私事 → 能配合） ----------------
GROUPS = [
    {
        'key': 'name', 'icon': '🪪', 'name': '只认名字', 'short': '只认名字',
        'lead': '破冰最省事的一种：不要求任何人讲自己的事，只要求你把名字和人脸对上。'
                '代价最小、见效最快，也是唯一能在 10 分钟内跑完的一档。',
        'when': '新人刚进来 / 人多到两两聊不开 / 时间只剩十分钟 / '
                '团队气氛已经不错，只是还不够熟。',
        'avoid': '别指望靠它建立深层了解——玩完之后大家还是不知道对方是做什么的；'
                 '已经互相认识的老团队玩它等于白花时间。',
        'pick': 'name-chain',
        'ids': ['name-chain', 'human-bingo'],
    },
    {
        'key': 'hype', 'icon': '🎭', 'name': '只图热闹', 'short': '只图热闹',
        'lead': '这两款都不需要你讲自己的事——玩的是现成的卡牌素材（场景卡、职场人设），'
                '热闹是唯一目标。适合气氛太闷、需要先把人逗松的场合。',
        'when': '会前气氛太沉 / 刚做完一个紧张的环节需要泄压 / '
                '跨部门第一次见面还没熟到能互聊私事 / 年会、聚餐的娱乐环节。',
        'avoid': '想借它加深了解就别选——玩完还是「同事」；'
                 '台词之王 30–50 分钟，人多时又吵又拖，散场得比预期晚。',
        'pick': 'celestial-gala',
        'ids': ['celestial-gala', 'line-master'],
    },
    {
        'key': 'know', 'icon': '💬', 'name': '谈自己的事', 'short': '谈自己的事',
        'lead': '这两款都要你先开口讲自己的事——这是所有破冰里暴露度最高的一档，'
                '风险和收益都在这里：说开了就真的认识，没说开就是冷场。',
        'when': '团队已经混过脸但还不够熟 / 培训需要一点心理安全垫 / '
                '半天以上的团建，破冰之后还有深度环节要接。',
        'avoid': '别在领导在场、上下级混编、或者刚吵过架的场合用——'
                 '真话一旦说出口收不回来；两真一假讲究的是「老员工先自曝一条假的，'
                 '新人才敢开口」，顺序反了就不灵。',
        'pick': 'two-truths-one-lie',
        'ids': ['two-truths-one-lie', 'explorer-journal'],
    },
    {
        'key': 'team', 'icon': '🍳', 'name': '带协作', 'short': '带协作',
        'lead': '这两款其实是小组协作游戏，只是长着破冰的外壳——'
                '玩完顺手就多了一支已经配合过的小队，不必再单独做一次破冰。',
        'when': '破冰之后紧接着要分组做正事 / 想一次解决「破冰」和'
                '「看看大家能不能配合」两件事 / 半天团建要先试探团队结构。',
        'avoid': '别拿它当纯粹的破冰——盲盒神话 30–40 分钟已经很满；'
                 '人少到凑不出 4–8 人一组也开不起来。',
        'pick': 'blind-box-myth',
        'ids': ['blind-box-myth', 'food-challenge'],
    },
]

# 决策表：你现在的麻烦 → 去哪一组 → 直接拿这款
DECIDE = [
    ('全场都是生面孔，先把名字和脸对上', 'name', 'name-chain'),
    ('想让大家动起来，别一直坐着听', 'name', 'human-bingo'),
    ('上一场太闷，需要先笑一场', 'hype', 'celestial-gala'),
    ('想让大家开始讲自己的事', 'know', 'two-truths-one-lie'),
    ('破冰完就要分组干活', 'team', 'blind-box-myth'),
]

# 分类标签（破冰这 8 款同属一个分类，保留「分类」列是为了跟 README 其余小节对齐）
CAT_LABEL = {'icebreaker': '🧊 破冰热场'}

# 配色：hue 184（全站 110 页里 179↔189 之间 11° 空档的中点），HSL 单色相派生
C = {
    'primary': '#1e7a80', 'mid': '#2ea5ad', 'light': '#5ddce5',
    'bg': '#091116', 'container': '#121f26', 'gridbg': '#050a0d',
    'border': '#2f515b', 'text': '#cde0e4', 'muted': '#85a5ad',
    'quote': '#1a2f37', 'whenbox': '#172c36',
    'avoidbox': '#301b18', 'avoidborder': '#7b3c32', 'avoidtext': '#e29983',
    'headtext': '#0a151a',
}


# ---------------- 工具（经验 81/87：整块替换前必须断言锚点唯一且命中） ----------------
def rd(p):
    """读入并统一成 '\\n'（universal newlines）。写回时再统一转 CRLF。"""
    return io.open(p, encoding='utf-8').read()


def wr(p, s, crlf=True):
    """写回。index.html / README.md / ice.html 全站统一 CRLF。"""
    if crlf:
        s = s.replace('\r\n', '\n').replace('\n', '\r\n')
    io.open(p, 'w', encoding='utf-8', newline='').write(s)


def rep(text, old, new, what):
    assert text.count(old) == 1, '锚点不唯一(%d)或未命中: %s' % (text.count(old), what)
    return text.replace(old, new)


def short_people(s):
    """README 里的人数常带「（8-50人）」后缀，展示时取主数值。"""
    return re.sub(r'（[^）]*）\s*$', '', s).strip()


# ---------------- 采集现成数据（一律复用，不另写） ----------------
def collect():
    """从 README.md 取 名称/形式/人数/时长/场景标签，从 index.html 取 标题与一句话描述。"""
    rm = rd(os.path.join(TB, 'README.md'))
    meta = {}
    # ⚠️ 坑：这里必须用 [^|\n]* 而不是 [^|]* —— 后者能匹配换行，
    # 贪婪的 {4,5} 会跨行吞掉下一行的开头，导致一行只匹配到 4 次（经验 100）。
    for m in re.finditer(
            r'\|\s*\[([^\]]+)\]\(games/icebreaker/([a-z0-9-]+)\.md\)\s*'
            r'((?:\|[^|\n]*){4,5})\|', rm):
        gid = m.group(2)
        cells = [c.strip() for c in m.group(3).split('|')[1:]]
        if len(cells) != 4:
            continue
        meta[gid] = {
            'name': m.group(1), 'cat': 'icebreaker', 'form': cells[0],
            'people': cells[1], 'dur': cells[2], 'tags': cells[3],
            'people_short': short_people(cells[1]),
        }
    idx = rd(os.path.join(TB, 'index.html'))
    for m in re.finditer(
            r'<a href="games/icebreaker/([a-z0-9-]+)\.html" '
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
def patch_index():
    p = os.path.join(TB, 'index.html')
    h = rd(p)

    # 1a. 顺带修掉 line-master 的两处口径分裂（两个修复各自独立判定，可分别重跑）：
    #     ① 时长：md / README 是「30–50 min」，index.html 卡片与 generator.html
    #        却写「20–30 min」（同款游戏三个地方两个数）
    #     ② 描述：写的是「用电影台词猜谜」，但这款游戏实际是
    #        **抽场景卡+角色卡+情绪卡的即兴表演**（见 games/icebreaker/line-master.md
    #        与 boardgames/category/party/line-master/README.md），
    #        没有任何「猜谜」环节 —— 描述与玩法不符，教练按它准备道具会带错
    #
    # ⚠️ 判定条件要锚在这一款游戏上：写 `'data-duration="short"' in h` 是全局匹配，
    #    别的卡片（传话游戏、你说我画…）也有 short，改一处就会误判成「还没修过」。
    lm_old_bucket = ('<a href="games/icebreaker/line-master.html" class="card" '
                     'data-people="medium" data-duration="short">')
    if lm_old_bucket in h:
        h = rep(h, lm_old_bucket,
                '<a href="games/icebreaker/line-master.html" class="card" '
                'data-people="medium" data-duration="medium">',
                'line-master data-duration 分桶')
        print('index.html: line-master 时长口径已统一为 30–50 min（分桶 short → medium）')

    lm_old_desc = ('<div class="card-desc">用电影台词猜谜的聚会游戏改造，轻松破冰、笑声不断。</div>\n'
                   '        <div class="card-tags"><span class="tag">室内</span>'
                   '<span class="tag">20–30 min</span><span class="tag">团建/培训</span></div>')
    if lm_old_desc in h:
        # 这次同时改描述与时长标签 —— 两者原本都写错，必须一起改
        h = rep(h, lm_old_desc,
                '<div class="card-desc">抽场景卡+角色卡+情绪卡即兴表演的聚会游戏改造，'
                '笑声不断、破冰够快。</div>\n'
                '        <div class="card-tags"><span class="tag">室内</span>'
                '<span class="tag">30–50 min</span><span class="tag">团建/培训</span></div>',
                'line-master 描述与时长标签')
        print('index.html: line-master 描述已改为「即兴表演」实况（原描述与玩法不符），'
              '时长标签已改为 30–50 min')

    if 'data-ice=' in h:
        print('index.html 已含肌肉标签，跳过网格改造')
    else:
        # 1b. 取出 grid-icebreaker 内的 8 张卡片
        # 用网格切块定位原网格整体（开标签 → 收尾 </div>），只替换这一段。
        s = h.find('    <div class="grid" id="grid-icebreaker">')
        assert s > 0, '未找到 grid-icebreaker 开标签'
        gt = h.find('>', s) + 1
        depth, i = 1, gt
        pat = re.compile(r'<div\b|</div>')
        while depth > 0:
            m = pat.search(h, i)
            assert m, 'grid-icebreaker 未闭合'
            depth += 1 if m.group().startswith('<div') else -1
            i = m.end()
        end = i - len('</div>')
        body = h[gt:end]

        # 卡片以「      <a href="games/…」开头。网格内共 8 个 </a>（卡片内无嵌套 <a>），
        # 所以非贪婪匹配到第一个 </a> 即为整张卡；不要加「后面必须跟换行」的前瞻——
        # 最后一张卡的 </a> 后面直接接网格的 </div>，加前瞻会漏掉它（经验 99）。
        CARD = re.compile(r'<a href="games/icebreaker/([a-z0-9-]+)\.html" '
                          r'class="card"[^>]*>.*?</a>', re.S)
        cards = {}
        order = []
        for m in CARD.finditer(body):
            cards[m.group(1)] = m.group(0)
            order.append(m.group(1))
        assert len(cards) == 8, '破冰网格卡片数 %d != 8' % len(cards)
        assert body.count('</a>') == 8, '网格内 </a> 数 %d != 8（卡片内有嵌套 a？）' % body.count('</a>')

        sub_of = {}
        for g in GROUPS:
            for gid in g['ids']:
                assert gid in cards, '分组引用了网格里没有的游戏: ' + gid
                assert gid not in sub_of, '游戏同时属于多组: ' + gid
                sub_of[gid] = g['key']
        assert set(sub_of) == set(cards), '分组与卡片集合不一致: %s' % (set(sub_of) ^ set(cards))

        gk = {g['key']: g for g in GROUPS}

        def rebuild(ids):
            """重排卡片：加 data-ice、加肌肉标签胶囊。原卡片缩进 6 空格、每张一行。"""
            out = ''
            for gid in ids:
                c = cards[gid]
                g = gk[sub_of[gid]]
                c2 = c.replace(' class="card" data-people=',
                               ' class="card" data-ice="%s" data-people=' % g['key'], 1)
                assert c2 != c, 'data-ice 未插入: ' + gid
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

        new_block = '\n' + rebuild(by_group(order))
        h = h[:gt] + new_block + h[end:]
        print('index.html 破冰网格已按 4 组重排（8 张卡 + data-ice + 肌肉标签）')

    # 1c. 新增「破冰要什么」二级筛选行（只在选中 🧊破冰 时出现）
    if 'id="ice-filter"' not in h:
        h = rep(h,
                '    <div class="filter-group" id="idea-filter" style="display:none;">',
                '    <div class="filter-group" id="ice-filter" style="display:none;">\n'
                '      <span class="filter-label">破冰要什么：</span>\n'
                '      <button class="filter-btn active" onclick="toggleFilter(\'ice\', \'all\', this)">全部</button>\n'
                + ''.join('      <button class="filter-btn" onclick="toggleFilter(\'ice\', \'%s\', this)">%s %s</button>\n'
                          % (g['key'], g['icon'], g['short']) for g in GROUPS) +
                '    </div>\n'
                '    <div class="filter-group" id="idea-filter" style="display:none;">',
                '破冰要什么筛选行')
    else:
        print('index.html 已有 ice-filter，跳过')

    # 1d. JS：状态 + 显隐 + 过滤
    if 'resetIce' not in h:
        h = rep(h,
                "var currentFilters = {\n  category: 'all',\n  people: 'all',\n  duration: 'all',\n  sub: 'all',\n  idea: 'all'\n};",
                "var currentFilters = {\n  category: 'all',\n  people: 'all',\n  duration: 'all',\n  sub: 'all',\n  idea: 'all',\n  ice: 'all'\n};",
                'JS currentFilters')

        h = rep(h,
                "function resetSub() {",
                "// 🧊破冰 8 款按「破冰之后留下什么」分 4 组，第二级筛选只在选中破冰时出现\n"
                "function setIceRow(on) {\n"
                "  var row = document.getElementById('ice-filter');\n"
                "  if (row) { row.style.display = on ? '' : 'none'; }\n"
                "}\n\n"
                "function resetIce() {\n"
                "  currentFilters.ice = 'all';\n"
                "  var row = document.getElementById('ice-filter');\n"
                "  if (!row) { return; }\n"
                "  row.querySelectorAll('.filter-btn').forEach(function(b) {\n"
                "    if (b.textContent === '全部') { b.classList.add('active'); }\n"
                "    else { b.classList.remove('active'); }\n"
                "  });\n"
                "}\n\n"
                "function resetSub() {",
                'JS ice 筛选函数')

        h = rep(h,
                "    if (value === 'creativity' || value === 'problem-solving') { setIdeaRow(true); }\n"
                "    else { resetIdea(); setIdeaRow(false); }\n",
                "    if (value === 'creativity' || value === 'problem-solving') { setIdeaRow(true); }\n"
                "    else { resetIdea(); setIdeaRow(false); }\n"
                "    // 「破冰要什么」只在选中 🧊破冰 时出现；离开破冰分类才复位\n"
                "    if (value === 'icebreaker') { setIceRow(true); }\n"
                "    else { resetIce(); setIceRow(false); }\n",
                'JS toggleFilter 联动')

        h = rep(h,
                "      // 协作子类筛选（仅协作分类下的 6 组）\n",
                "      // 「破冰要什么」筛选（仅破冰分类下的 4 组）\n"
                "      if (visible && currentFilters.ice !== 'all') {\n"
                "        if (card.getAttribute('data-ice') !== currentFilters.ice) {\n"
                "          visible = false;\n"
                "        }\n"
                "      }\n\n"
                "      // 协作子类筛选（仅协作分类下的 6 组）\n",
                'JS ice 过滤')
        print('index.html JS 已接入 ice 筛选')
    else:
        print('index.html JS 已含 resetIce，跳过')

    # 1e. 首屏胶囊：加破冰挑款入口
    if 'href="ice.html"' not in h:
        h = rep(h,
                '        <a href="idea.html" class="res-chip">💡 创意与解题共 10 款，帮我挑</a>\n',
                '        <a href="idea.html" class="res-chip">💡 创意与解题共 10 款，帮我挑</a>\n'
                '        <a href="ice.html" class="res-chip">🧊 破冰共 8 款，帮我挑</a>\n',
                '首屏胶囊')
    else:
        print('index.html 已有 ice.html 入口，跳过')

    wr(p, h)
    print('index.html 已更新：破冰 4 组子类（%s）'
          % ', '.join('%s=%d' % (g['key'], len(g['ids'])) for g in GROUPS))


# ---------------- 2. ice.html ----------------
CSS = """
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.6; color: %(text)s;
        background: linear-gradient(135deg, %(bg)s 0%%, #0b141a 55%%, #10222b 100%%);
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


def build_ice_html(meta):
    parts = []
    a = parts.append
    a('<!DOCTYPE html>')
    a('<html lang="zh-CN">')
    a('<head>')
    a('    <meta charset="UTF-8">')
    a('    <meta name="viewport" content="width=device-width, initial-scale=1.0">')
    a('    <title>破冰挑款指南 · 8 款分成 4 组 - 团建 & 培训游戏库</title>')
    a(CSS)
    a('</head>')
    a('<body>')
    a('<div class="container">')
    a('    <div class="header">')
    a('        <h1>🧊 破冰挑款指南</h1>')
    a('        <div class="subtitle">8 款破冰 —— 按「破冰之后，团队手里剩下什么」分成 4 组</div>')
    a('        <div class="tag">8 款 · 4 组 · 每组给了首选与「什么时候别选它」</div>')
    a('    </div>')
    a('')
    a('    <div class="info-grid">')
    for icon, label, value in (('🎲', '覆盖范围', '8 款（🧊 破冰热场）'),
                               ('🧭', '分组口径', '按「破冰之后剩下什么」分 4 组'),
                               ('⚡', '最快的一款', '名字接龙 5–10 min'),
                               ('👥', '人数跨度', '任意人数 ～ 50 人')):
        a('        <div class="info-card"><div class="icon">%s</div>'
          '<div class="label">%s</div><div class="value">%s</div></div>' % (icon, label, value))
    a('    </div>')
    a('')
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
          '<td><a href="games/icebreaker/%s.html">%s</a> <span style="color:%s;">（%s / %s）</span></td></tr>'
          % (trouble, key, g['icon'], g['name'], gid, m['title'], C['muted'],
             m['people_short'], m['dur']))
    a('        </table>')
    a('        <blockquote>四组是按<strong>「破冰之后，团队手里剩下什么」</strong>切的，'
      '不是按玩法或题材切的。同样是「让气氛热起来」，只图热闹和谈自己的事完全是两回事 —— '
      '一个玩的是公共素材，一个要你先开口交底。</blockquote>')
    a('    </div>')
    a('')
    # 边界说明（本次二级索引的核心：把混淆讲清）
    a('    <div class="section">')
    a('        <h2>🔀 破冰不等于「认识彼此」：四档暴露度</h2>')
    a('        <p>「破冰」这个词只说了<strong>开始</strong>，没说<strong>结束时要留下什么</strong>。'
      '四组里真正在「让人认识」的只有两组，另两组分别只留下笑声和一支能干活的小队。</p>')
    a('        <table class="data-table">')
    a('            <tr><th></th><th>🪪 只认名字</th><th>🎭 只图热闹</th>'
      '<th>💬 谈自己的事</th><th>🍳 带协作</th></tr>')
    a('            <tr><td><b>产出的是什么</b></td>'
      '<td>名字和人脸对上了</td><td>一屋子笑声</td>'
      '<td>彼此知道对方一件私事</td><td>一支能配合的小队</td></tr>')
    a('            <tr><td><b>要不要讲自己的事</b></td>'
      '<td>不要</td><td>不要</td><td><b>要（真话）</b></td>'
      '<td>不要，但要说需求</td></tr>')
    a('            <tr><td><b>风险在哪</b></td>'
      '<td>几乎没有</td><td>几乎没有</td>'
      '<td>高：说出口收不回来</td>'
      '<td>中：道具没备好就冷场</td></tr>')
    a('            <tr><td><b>成功长什么样</b></td>'
      '<td>开场能叫出大部分人的名字</td><td>没人低头看手机</td>'
      '<td>有人开始讲真事</td>'
      '<td>下一场分组不用重新磨合</td></tr>')
    a('            <tr><td><b>失败长什么样</b></td>'
      '<td>还是记不住名字</td><td>笑完还是陌生</td>'
      '<td>冷场，有人开始自我保护</td>'
      '<td>变成一场卡牌比赛</td></tr>')
    a('        </table>')
    a('        <p style="margin-top:18px;">把四组横过来看，暴露度是唯一那条真正递增的轴：'
      '<strong>零 → 零 → 高 → 中</strong>。挑款时问的应该是「我这半小时要拿到什么」，'
          '而不是「哪个游戏看起来更好玩」。</p>')
    a('        <table class="data-table">')
    a('            <tr><th>破冰之后剩下什么</th><th>组</th><th>组内首选</th></tr>')
    for g in GROUPS:
        pick = meta[g['pick']]
        a('            <tr><td><a href="#g-%s">%s %s</a></td>'
          '<td>%d 款</td><td>%s（%s / %s）</td></tr>'
          % (g['key'], g['icon'], g['name'], len(g['ids']), pick['title'],
             pick['people_short'], pick['dur']))
    a('        </table>')
    a('        <blockquote>再提醒一句：<strong>这 8 款只是带「破冰」场景标签的 11 款里的 8 款</strong>。'
      '另外 6 款（沟通类的画图接龙 / 传话游戏 / 时间特工，协作类的人体拼字 / 疯狂厨房 / 怪物厨师）'
          '也标了「破冰」，只是它们的分类在别处 —— 见下方「🧊 破冰不只是这 8 款」。</blockquote>')
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
        a('            <div class="pick">🎯 拿不准就先拿：<a href="games/icebreaker/%s.html" '
          'style="color:%s;text-decoration:underline;">%s</a>（%s / %s）</div>'
          % (g['pick'], C['headtext'], pick['title'], pick['people_short'], pick['dur']))
        a('            <table class="data-table">')
        a('                <tr><th>游戏</th><th>分类</th><th>形式</th><th>人数</th><th>时长</th>'
          '<th>这一款在练什么</th></tr>')
        for gid in g['ids']:
            m = meta[gid]
            a('                <tr><td><a href="games/icebreaker/%s.html">%s</a></td>'
              '<td class="cat">%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>'
              % (gid, m['title'], CAT_LABEL[m['cat']], m['form'],
                 m['people_short'], m['dur'], m['desc']))
        a('            </table>')
        a('        </div>')
    a('    </div>')
    a('')
    a('    <div class="section">')
    a('        <h2>🧊 破冰不只是这 8 款</h2>')
    a('        <p>全库带「破冰」场景标签的游戏共 <strong>11 款</strong>，'
      '除了本页这 8 款，还有 6 款落在别的分类里 —— 按分类挑会漏掉它们：</p>')
    a('        <table class="data-table">')
    a('            <tr><th>分类</th><th>游戏</th><th>人数</th><th>时长</th></tr>')
    for cat, gid, title, people, dur in CROSS_CATEGORY:
        a('            <tr><td class="cat">%s</td>'
          '<td><a href="games/%s/%s.html">%s</a></td><td>%s</td><td>%s</td></tr>'
          % (cat, gid.split('/')[0], gid.split('/')[1], title, people, dur))
    a('        </table>')
    a('        <blockquote>这 6 款之所以标「破冰」却不归在破冰分类，是因为它们各自还有'
          '<strong>更主要的训练目标</strong>（沟通 / 协作 / 信任）—— 破冰只是它们的一个用法。'
          '如果你要的是「纯破冰」，看上面 8 款；如果要的是「顺便练点别的」，它们才是主角。</blockquote>')
    a('    </div>')
    a('')
    a('    <div class="section">')
    a('        <h2>⚠️ 四个最容易挑错的地方</h2>')
    a('        <table class="data-table">')
    a('            <tr><th>坑</th><th>为什么</th></tr>')
    a('            <tr><td><b>把「热闹」当成「认识」</b></td>'
      '<td>🎭那 2 款（天庭年会、台词之王）玩完大家笑了，但仍然不知道对方是做什么的。'
      '想加深了解必须去💬「谈自己的事」那一组。</td></tr>')
    a('            <tr><td><b>大团队挑错了</b></td>'
      '<td>8 款里有 3 款是 4–8 人/组的小组制（盲盒神话、美食挑战赛、天庭年会）——'
      '全场 40 人时等于开 5 局。真正能撑住全场的只有🪪「名字接龙」和「人类宾果」两款。</td></tr>')
    a('            <tr><td><b>暴露度选错比选错游戏更糟</b></td>'
      '<td>领导在场、上下级混编、刚吵过架的场合选💬会冷场；'
      '反过来，全新团队上来只玩🎭，热完还是一盘散沙。</td></tr>')
    a('            <tr><td><b>按分类找破冰会漏 6 款</b></td>'
      '<td>带「破冰」标签的共 11 款，其中 6 款（画图接龙 / 传话游戏 / 时间特工 / '
      '人体拼字 / 疯狂厨房 / 怪物厨师）分别在沟通与协作分类下。</td></tr>')
    a('        </table>')
    a('        <blockquote>这 8 款只占全库 9%，却是每场团建的<strong>第一分钟</strong>。'
          '先确认你要的是「名字 / 笑声 / 私事 / 配合」里的哪一个，再回去挑 —— '
          '按玩法名字挑是最容易出错的方式。</blockquote>')
    a('    </div>')
    a('')
    a('    <div class="section">')
    a('        <h2>🔗 相关的入口</h2>')
    a('        <ul>')
    a('            <li><a href="index.html">全部 85 款游戏（按 8 个分类）</a> —— '
      '🧊破冰分类下已有「破冰要什么」二级筛选行</li>')
    a('            <li><a href="README.md">README 索引表</a> —— 纯文本版，这 8 款已按四组排好</li>')
    a('            <li><a href="flows/onboarding/01-schedule.html">新员工融入团建流程</a> —— '
      '新人场的破冰就是这 8 款里的选择题</li>')
    a('            <li><a href="toolbox/generator.html">团建方案生成器（全库版）</a> —— '
      '有整块时间、想要一整套流程时用</li>')
    a('            <li><a href="play/tools/plan-generator/">T1 快速版生成器</a> —— '
      '现场临时只要几个游戏，30 秒出一组</li>')
    a('            <li><a href="guide.html">教练使用指南</a> —— 第一次带团先读 5 分钟</li>')
    a('            <li><a href="toolbox/debrief.html">复盘引导框架</a> —— '
      '💬那 2 款的价值大半在复盘那 15–30 分钟</li>')
    a('        </ul>')
    a('    </div>')
    a('')
    a('    <div class="footer">')
    a('        <div>')
    a('            <a href="index.html" class="back-link">← 回到游戏库</a>')
    a('            <a href="README.md" class="back-link">README 索引</a>')
    a('            <a href="toolbox/generator.html" class="back-link">方案生成器</a>')
    a('        </div>')
    a('        <div style="margin-top:14px;">团建 & 培训游戏库 · 破冰二级索引 · 8 款 / 4 组</div>')
    a('    </div>')
    a('</div>')
    a('</body>')
    a('</html>')
    text = '\n'.join(parts) + '\n'
    p = os.path.join(TB, 'ice.html')
    wr(p, text)
    print('ice.html 已生成：%d 行 / 4 组 / 8 款' % text.count('\n'))


# 全库带「破冰」场景标签、但不在 icebreaker 分类里的 6 款
# （数据取自 README.md 现成表格，不另写）
CROSS_CATEGORY = [
    ('💬 沟通表达', 'communication/drawing-relay', '画图接龙', '4-8人/组', '20-30 min'),
    ('💬 沟通表达', 'communication/telephone-game', '传话游戏', '8-30人', '15-25 min'),
    ('💬 沟通表达', 'communication/time-agents', '时间特工（改造版）', '6-12人', '30-45 min'),
    ('🤝 团队协作', 'collaboration/body-letters', '人体拼字', '6-20人/组', '20-30 min'),
    ('🤝 团队协作', 'collaboration/crazy-kitchen', '疯狂厨房（改造版）', '4-8人', '30-45 min'),
    ('🤝 团队协作', 'collaboration/monster-chef', '怪物厨师（改造版）', '3-6人', '50-70 min'),
]


# ---------------- 3. README.md ----------------
def patch_readme(meta):
    p = os.path.join(TB, 'README.md')
    rm = rd(p)
    if '🧊 破冰热场（icebreaker）' in rm and '🪪 只认名字' in rm:
        print('README.md 破冰小节已重排，跳过')
        return

    m_head = re.search(r'^#### 🧊 破冰热场（icebreaker）$', rm, re.M)
    assert m_head, 'README 未找到破冰小节'
    m_next = re.search(r'^#### 💬 沟通表达（communication）$', rm, re.M)
    assert m_next and m_next.start() > m_head.end(), 'README 未找到沟通表达小节'

    # 先把这一节的原始行抽出来（复用现成文案，不重写）
    sec = rm[m_head.start():m_next.start()]
    rows = {}
    for line in sec.split('\n'):
        m = re.match(r'\| \[([^\]]+)\]\(games/icebreaker/([a-z0-9-]+)\.md\)'
                     r'\s*((?:\|[^|\n]*){4})\|', line)
        if m:
            rows[m.group(2)] = (m.group(1), m.group(3))
    assert len(rows) == 8, 'README 破冰表 %d 行 != 8' % len(rows)

    new = ('#### 🧊 破冰热场（icebreaker）\n'
           '\n'
           '> 破冰是每场团建的第一分钟，但「破冰」只说了开始、没说结束时要留下什么。'
           '本节已按**「破冰之后，团队手里剩下什么」**重排为 4 组（名字 / 笑声 / 私事 / 配合）；'
           '不确定选哪组时先看 [破冰挑款指南](ice.html)（含 30 秒决策表与「什么时候别选它」）。\n'
           '\n'
           '| 游戏名称 | 形式 | 人数 | 时长 | 场景标签 |\n'
           '|---------|------|------|------|---------|\n')
    for g in GROUPS:
        new += ('| **%s %s（%d 款）** | | | | |\n'
                % (g['icon'], g['name'], len(g['ids'])))
        for gid in g['ids']:
            name, rest = rows[gid]
            # rest = '| 形式 | 人数 | 时长 | 场景标签'（末格前有空格），原样保留。
            # ⚠️ rest 不含行尾那根 |（正则把它吃掉了），要自己补回去 ——
            # 否则整表每一行都少一个竖线，markdown 表格会散（经验 102）。
            new += '| [%s](games/icebreaker/%s.md) %s |\n' % (name, gid, rest.rstrip())
    new += '\n'
    # 破冰小节末尾补一条「跨分类」的提示（6 款带破冰标签但分类在别处）
    new += ('> 全库带「破冰」场景标签的共 **11 款**，本页这 8 款之外还有 6 款落在别的分类里'
            '（💬沟通：画图接龙 / 传话游戏 / 时间特工；🤝协作：人体拼字 / 疯狂厨房 / 怪物厨师）——'
            '按分类挑会漏掉它们，详见 [破冰挑款指南](ice.html)。\n'
            '\n')

    rm = rm[:m_head.start()] + new + rm[m_next.start():]

    # 决策表补一行
    rm = rep(rm,
              '| 🤝 目的就是协作，但 39 款挑不过来 | [协作类挑款指南](collab.html) |',
              '| 🧊 目的就是开场破冰，但 8 款挑不过来 | [破冰挑款指南](ice.html) | '
              '按「破冰之后留下什么」把 8 款分成 4 组（名字 / 笑声 / 私事 / 配合），'
              '每组给了首选与「什么时候别选它」；首页选「🧊 破冰」会出现同样的 4 个子类按钮 |\n'
              '| 🤝 目的就是协作，但 39 款挑不过来 | [协作类挑款指南](collab.html) |',
              'README 决策表')

    # 网页版资源清单补一条
    rm = rep(rm,
              '· [创意与解题挑款指南](idea.html) ·',
              '· [创意与解题挑款指南](idea.html) · [破冰挑款指南](ice.html) ·',
              'README 网页版清单')

    # 快速检索表的「目的」行补一句
    rm = rep(rm,
              '| **目的** | 破冰热场 · 沟通表达 · 团队协作 · 信任建立 · 领导力 · 创新思维 · 问题解决 · 线上团建'
              '（💡创新思维与🔧问题解决合为 10 款，按「卡在哪一步」分 4 组，见下方） |',
              '| **目的** | 破冰热场 · 沟通表达 · 团队协作 · 信任建立 · 领导力 · 创新思维 · 问题解决 · 线上团建'
              '（💡创新思维与🔧问题解决合为 10 款，按「卡在哪一步」分 4 组；'
              '🧊破冰 8 款按「破冰之后留下什么」分 4 组，均见下方） |',
              'README 快速检索表')

    wr(p, rm)
    print('README.md 已重排：🧊 破冰 8 款 → 4 组')


def main():
    # ⚠️ 顺序要紧：patch_index 会先修正 index.html 上的**过时描述与时长**
    #    （比如台词之王原写「用电影台词猜谜」，实际玩法是抽卡即兴表演）。
    #    collect() 又是从 index.html 抽「这一款在练什么」这句话的 ——
    #    所以必须先修再抽，否则 ice.html 与 16 个游戏页会拿到**修正前**的旧描述，
    #    错误就此扩散到全站（经验 105）。
    patch_index()

    meta = collect()
    need = set()
    for g in GROUPS:
        need |= set(g['ids'])
    miss = [gid for gid in sorted(need) if gid not in meta]
    assert not miss, '缺元信息: %s' % miss
    no_desc = [gid for gid in sorted(need) if not meta[gid].get('desc')]
    assert not no_desc, '缺一句话描述: %s' % no_desc
    # 交叉分类的 6 款：文件必须真实存在（防止 CROSS_CATEGORY 写错路径）
    for _, gid, _, _, _ in CROSS_CATEGORY:
        sub, name = gid.split('/')
        assert os.path.exists(os.path.join(TB, 'games', sub, name + '.html')), \
            '跨分类破冰游戏不存在: ' + gid
    build_ice_html(meta)
    patch_readme(meta)
    print('完成')


if __name__ == '__main__':
    main()
