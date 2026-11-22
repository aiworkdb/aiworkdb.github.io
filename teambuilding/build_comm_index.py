# -*- coding: utf-8 -*-
"""💬 沟通表达 8 款的二级索引：改 index.html + README.md，并新建 comm.html。

背景（ROADMAP 下一步建议 · 2026-10-28 首选）：
    沟通 8 款是剩余 20 款无二级索引里最大的一块。破冰 / 线上 / 创意解题之后，
    这是**全库第五套分组口径**：协作按「练哪种协作」、创意解题按「卡在哪一步」、
    破冰按「结束留下什么」、线上按「远程靠什么成立」，
    **沟通按「这一局，沟通坏在哪一环」** —— 四套不能互相套用。

核心澄清（comm.html 上那节）：
    「沟通」不等于「练说话」——8 款里 4 款先把一条通道堵死
    （盲人方阵不许看 / 你说我画不许问 / 传话游戏只许说一遍 / 画图接龙不许擦），
    法庭风云反着来（不先复述就不许反驳）。只有 🗣️那 2 款真的在练「怎么说」。

用法（可重复执行，含幂等跳过）：
    python teambuilding/build_comm_index.py
    python teambuilding/build_comm_index.py --force   # 已改过也强制覆盖
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
FORCE = '--force' in sys.argv

# 4 组：key / 组名 / 短名 / 成员顺序
GROUPS = [
    ('express', '🗣️ 说的人说不清', '说不清', ['blind-polygon', 'draw-guess']),
    ('relay', '🔁 传的人传不准', '传不准', ['telephone-game', 'rumor-factory']),
    ('pool', '🧩 信息凑不齐', '凑不齐', ['drawing-relay', 'animal-detective']),
    ('clash', '⚖️ 有分歧说不拢', '说不拢', ['courtroom-debate', 'time-agents']),
]
GROUP_NAME = dict((k, n) for k, n, s, ids in GROUPS)
GROUP_SHORT = dict((k, s) for k, n, s, ids in GROUPS)
SUB_OF = {}
for k, n, s, ids in GROUPS:
    for gid in ids:
        assert gid not in SUB_OF, '游戏 %s 同时属于多组' % gid
        SUB_OF[gid] = k


def rd(p):
    return io.open(p, encoding='utf-8', newline='').read()


def wr(p, s):
    io.open(p, 'w', encoding='utf-8', newline='').write(s)


def eol_of(t):
    return '\r\n' if '\r\n' in t else '\n'


# ---------------------------------------------------------------- index.html
CARD_RE = re.compile(
    r'[ \t]*<a href="games/communication/([a-z0-9-]+)\.html" class="card"(.*?)</a>',
    re.S)


def patch_cards(idx, nl):
    """重排沟通网格 → 4 组顺序；每张卡补 data-comm + 肌肉标签胶囊。"""
    m = re.search(r'<div class="grid" id="grid-communication">(.*?)\n    </div>', idx, re.S)
    assert m, 'index.html 未找到 grid-communication'
    body = m.group(1)
    cards = {}
    for cm in CARD_RE.finditer(body):
        cards[cm.group(1)] = cm.group(0)
    on_disk = set()
    for f in os.listdir(os.path.join(TB, 'games', 'communication')):
        if f.endswith('.md'):
            on_disk.add(f[:-3])
    assert set(cards) == on_disk, '网格 %d 款与目录 %d 款不一致：缺 %s 多 %s' % (
        len(cards), len(on_disk), sorted(on_disk - set(cards)), sorted(set(cards) - on_disk))

    out = []
    for k, name, short, ids in GROUPS:
        for gid in ids:
            c = cards[gid]
            if 'data-comm=' in c:
                c = re.sub(r' data-comm="[a-z]+"', '', c)
            c = c.replace('class="card"', 'class="card" data-comm="%s"' % k, 1)
            assert 'data-comm="%s"' % k in c, '%s 未写入 data-comm' % gid
            # 肌肉标签胶囊：同组口径直接印在卡片上（与破冰 / 线上网格同款）
            if '<span class="tag">%s</span>' % name not in c:
                c2 = re.sub(r'(<div class="card-tags">(?:<span class="tag">.*?</span>)*)(</div>)',
                            lambda mm: mm.group(1) + '<span class="tag">%s</span>' % name + mm.group(2),
                            c, count=1, flags=re.S)
                assert c2 != c, '%s 未找到 card-tags 收尾位置' % gid
                c = c2
            out.append(c)
    new_body = nl.join(out)
    new_grid = ('<div class="grid" id="grid-communication">' + nl + new_body + nl + '    </div>')
    return idx[:m.start()] + new_grid + idx[m.end():]


def patch_filter_row(idx, nl):
    """新增「沟通坏在哪一环」二级筛选行（只在选中 💬沟通 时出现）。"""
    if 'id="comm-filter"' in idx:
        return idx
    # ⚠️ index.html 是 CRLF，锚点必须跟着文件换行符走（写死 '\n' 会命中 0 次）
    anchor = '</div>' + nl + '    <div class="filter-group" id="idea-filter"'
    assert idx.count(anchor) == 1, 'online-filter / idea-filter 之间的锚点命中 %d 次' % idx.count(anchor)
    row = ['    <div class="filter-group" id="comm-filter" style="display:none;">']
    row.append('      <span class="filter-label">沟通坏在哪一环：</span>')
    row.append('      <button class="filter-btn active" onclick="toggleFilter(\'comm\', \'all\', this)">全部</button>')
    for k, name, short, ids in GROUPS:
        row.append('      <button class="filter-btn" onclick="toggleFilter(\'comm\', \'%s\', this)">%s</button>'
                   % (k, name))
    row.append('    </div>')
    # ⚠️ 锚点的 `</div>` 是 online-filter 的收尾，必须先把它原样写回再开 comm-filter，
    #    否则 comm-filter 会被嵌套进 online-filter 里（隐藏线上行会连带隐藏沟通行）
    repl = '</div>' + nl + nl.join(row) + nl + '    <div class="filter-group" id="idea-filter"'
    return idx.replace(anchor, repl, 1)


def patch_js(idx, nl):
    """currentFilters + setCommRow/resetComm + toggleFilter 分支 + filterCards 分支。"""
    # 1) 状态位
    if "  comm: 'all'," not in idx:
        old = "  online: 'all'" + nl + "};"
        assert idx.count(old) == 1, 'currentFilters 尾部锚点命中 %d 次' % idx.count(old)
        idx = idx.replace(old, "  online: 'all'," + nl + "  comm: 'all'," + nl + "};", 1)

    # 2) 显隐 + 复位函数（照 setOnlineRow / resetOnline 的同款写法）
    if 'function setCommRow' not in idx:
        anchor = 'function resetSub() {'
        assert idx.count(anchor) == 1, 'resetSub 锚点命中 %d 次' % idx.count(anchor)
        fn = [
            '// 💬沟通 8 款按「这一局，沟通坏在哪一环」分 4 组，第二级筛选只在选中沟通时出现',
            'function setCommRow(on) {',
            "  var row = document.getElementById('comm-filter');",
            "  if (row) { row.style.display = on ? '' : 'none'; }",
            '}',
            '',
            'function resetComm() {',
            "  currentFilters.comm = 'all';",
            "  var row = document.getElementById('comm-filter');",
            '  if (!row) { return; }',
            "  row.querySelectorAll('.filter-btn').forEach(function(b) {",
            "    if (b.textContent === '全部') { b.classList.add('active'); }",
            "    else { b.classList.remove('active'); }",
            '  });',
            '}',
            '',
            '',
        ]
        idx = idx.replace(anchor, nl.join(fn) + anchor, 1)

    # 3) toggleFilter：切走沟通分类时复位
    if "value === 'communication'" not in idx:
        anchor = ("    if (value === 'online') { setOnlineRow(true); }" + nl
                  + "    else { resetOnline(); setOnlineRow(false); }" + nl)
        assert idx.count(anchor) == 1, 'toggleFilter 的 online 分支锚点命中 %d 次' % idx.count(anchor)
        add = ("    // 「沟通坏在哪一环」只在选中 💬沟通 时出现；离开沟通分类才复位" + nl
               + "    if (value === 'communication') { setCommRow(true); }" + nl
               + "    else { resetComm(); setCommRow(false); }" + nl)
        idx = idx.replace(anchor, anchor + add, 1)

    # 4) filterCards：按 data-comm 过滤
    if "card.getAttribute('data-comm')" not in idx:
        anchor = ("      // 协作子类筛选（仅协作分类下的 6 组）" + nl)
        assert idx.count(anchor) == 1, 'filterCards 的协作子类注释锚点命中 %d 次' % idx.count(anchor)
        blk = [
            '      // 「沟通坏在哪一环」筛选（仅沟通分类下的 4 组）',
            "      if (visible && currentFilters.comm !== 'all') {",
            "        if (card.getAttribute('data-comm') !== currentFilters.comm) {",
            '          visible = false;',
            '        }',
            '      }',
            '',
            '',
        ]
        idx = idx.replace(anchor, nl.join(blk) + anchor, 1)
    return idx


def patch_title_and_chip(idx, nl):
    """分类小标题加挑款页入口 + 首屏 res-chip 加一枚。"""
    old = '<div style="font-weight:600;color:#555;margin:18px 0 10px;">💬 沟通表达（communication）</div>'
    if old in idx:
        new = ('<div style="font-weight:600;color:#555;margin:18px 0 10px;">💬 沟通表达（communication） '
               '<span style="font-weight:400;">· 8 款 · 想按「坏在哪一环」挑，见 '
               '<a href="comm.html" style="color:#3366cc;">沟通挑款指南</a></span></div>')
        idx = idx.replace(old, new, 1)
    chip_anchor = '<a href="online.html" class="res-chip">💻 线上共 8 款，帮我挑</a>'
    if chip_anchor in idx and 'comm.html" class="res-chip"' not in idx:
        idx = idx.replace(chip_anchor,
                          chip_anchor + nl + '        <a href="comm.html" class="res-chip">💬 沟通共 8 款，帮我挑</a>',
                          1)
    return idx


# ------------------------------------------------------------------ README.md
README_ROWS = {
    'blind-polygon': '[盲人方阵](games/communication/blind-polygon.md) | 室内/户外 · 混合 | 8-24人 | 30-45 min | 团建/培训',
    'draw-guess': '[你说我画](games/communication/draw-guess.md) | 室内 · 智力+趣味 | 2人/组 | 20-30 min | 培训/团建/工作坊',
    'telephone-game': '[传话游戏](games/communication/telephone-game.md) | 室内/户外 · 智力+趣味 | 8-30人 | 15-25 min | 培训/团建/破冰',
    'rumor-factory': '[谣言工厂（改造版）](games/communication/rumor-factory.md) | 室内 · 倾听+传递 | 6-16人 | 30-45 min | 团建/培训/信任建设',
    'drawing-relay': '[画图接龙](games/communication/drawing-relay.md) | 室内 · 趣味+创意 | 4-8人/组 | 20-30 min | 团建/培训/破冰',
    'animal-detective': '[动物城大侦探（改造版）](games/communication/animal-detective.md) | 室内 · 推理+讨论 | 4-12人 | 30-45 min | 培训/团建',
    'courtroom-debate': '[法庭风云 · 换位陈词（改造版）](games/communication/courtroom-debate.md) | 室内 · 辩论+换位 | 4-12人 | 45-75 min | 培训/工作坊/冲突修复',
    'time-agents': '[时间特工（改造版）](games/communication/time-agents.md) | 室内 · 推理+心理博弈 | 6-12人 | 30-45 min | 团建/培训/破冰',
}

CROSS_NOTE = ('> 全库带「沟通表达」标签的共 **20 款**，本页这 8 款之外还有 12 款落在别的分类里'
              '（🧊破冰：名字接龙 / 人类宾果 / 两真一假 / 探险家日记 / 台词之王 / 天庭年会；'
              '🤝协作：疯狂厨房 / 人结；🔐信任：盲行；💻线上：画图猜词 / 我从未 / 知识竞答）'
              '——按分类挑会漏掉它们，详见 [沟通挑款指南](comm.html)。')


def build_comm_section(nl):
    L = []
    a = L.append
    a('#### 💬 沟通表达（communication）')
    a('')
    a('> 沟通是最常被点名、也最常被挑错的一类。本节已按**「这一局，沟通坏在哪一环」**重排为 4 组'
      '（说不清 / 传不准 / 凑不齐 / 说不拢）；不确定选哪组时先看 [沟通挑款指南](comm.html)'
      '（含 30 秒决策表与「什么时候别选它」）。')
    a('')
    a('| 游戏名称 | 形式 | 人数 | 时长 | 场景标签 |')
    a('|---------|------|------|------|---------|')
    for k, name, short, ids in GROUPS:
        a('| **%s（%d 款）** | | | | |' % (name, len(ids)))
        for gid in ids:
            a('| %s |' % README_ROWS[gid])
    a('')
    a(CROSS_NOTE)
    return nl.join(L) + nl


def patch_readme(rm):
    nl = eol_of(rm)
    start = rm.index('#### 💬 沟通表达（communication）')
    end = rm.index('#### 🤝 团队协作（collaboration）')
    # 整块重建（幂等、自愈：不管先前有没有被改成 4 组，都按现值重建）
    seg = rm[start:end].rstrip()
    if 'comm.html' in seg and not FORCE:
        return rm, 'skip'
    rm = rm[:start] + build_comm_section(nl) + nl + rm[end:]

    # 决策表加一行
    row = ('| 💬 目的就是沟通，但 8 款挑不过来 | [沟通挑款指南](comm.html) | '
           '按「这一局坏在哪一环」把 8 款分成 4 组（说不清 / 传不准 / 凑不齐 / 说不拢），'
           '每组给了首选与「什么时候别选它」；首页选「💬 沟通」会出现同样的 4 个子类按钮 |')
    if '沟通挑款指南](comm.html) |' not in rm:
        anchor = '| 💻 目的就是远程团建，但 8 款挑不过来 |'
        assert rm.count(anchor) == 1, 'README 决策表线上行命中 %d 次' % rm.count(anchor)
        i = rm.index(anchor)
        j = rm.index('\n', i) + 1
        rm = rm[:j] + row + nl + rm[j:]

    # 网页版清单补一条
    # ⚠️ `[物资与效率工具](toolbox/checklist.html)` 全文出现 2 次（挑款清单 + 教练资料清单），
    #    用 count == 1 作幂等判定会静默失效 —— 必须锚到唯一的那一行
    head = '以上 5 份教练资料与生成器均有网页版：'
    assert rm.count(head) == 1, 'README 网页版清单锚点命中 %d 次' % rm.count(head)
    i = rm.index(head)
    j = rm.index(nl, i)
    line = rm[i:j]
    if 'comm.html' not in line:
        rm = rm[:j] + ' · [沟通挑款指南](comm.html)' + rm[j:]
    return rm, 'ok'


def main():
    # index.html
    p = os.path.join(TB, 'index.html')
    idx = rd(p)
    nl = eol_of(idx)
    before = idx
    idx = patch_cards(idx, nl)
    idx = patch_filter_row(idx, nl)
    idx = patch_js(idx, nl)
    idx = patch_title_and_chip(idx, nl)
    changed = idx != before
    if changed or FORCE:
        wr(p, idx)
    print('index.html：%s' % ('已更新' if changed else '无变化（幂等跳过）'))

    # README.md
    p = os.path.join(TB, 'README.md')
    rm = rd(p)
    new, st = patch_readme(rm)
    if new != rm:
        wr(p, new)
    print('README.md：%s' % ('已更新' if st == 'ok' else '已含 comm.html（幂等跳过）'))

    # 自检
    idx = rd(os.path.join(TB, 'index.html'))
    n = len(re.findall(r'data-comm="([a-z]+)"', idx))
    print('沟通卡片 data-comm：%d 张；分组：%s'
          % (n, ', '.join('%s=%d' % (k, len(re.findall(r'data-comm="%s"' % k, idx)))
                          for k, n_, s_, ids_ in GROUPS)))


if __name__ == '__main__':
    main()
