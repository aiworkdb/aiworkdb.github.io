# -*- coding: utf-8 -*-
"""👑 领导力 6 款的二级索引：改 index.html + README.md（lead.html 另建）。

背景（ROADMAP 下一步建议 · 2026-10-31 首选）：
    领导力 6 款 + 信任建立 6 款是最后两类没有二级索引的。这是**全库第六套分组口径**：
    协作按「练哪种协作」、创意解题按「卡在哪一步」、破冰按「结束留下什么」、
    线上按「远程靠什么成立」、沟通按「这一局坏在哪一环」，
    **领导力按「带人这件事卡在哪一层」** —— 五套都不能互相套用。

核心澄清（lead.html 上那节）：
    「领导力」不等于「有人站出来」——6 款里真正练「授权 / 带人」的只有 🔑 那 2 款；
    🧭 那 2 款练的是「决定怎么拍出来」，📣 那 2 款练的是「没有职位权力也能带」。
    另外领导力是全库最贵的一类：6 款里 5 款要 60 分钟以上。

用法（可重复执行，含幂等跳过）：
    python teambuilding/build_lead_index.py
    python teambuilding/build_lead_index.py --force   # 已改过也强制覆盖
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

# 3 组：key / 组名 / 短名 / 成员顺序
GROUPS = [
    ('decide', '🧭 定方向与拍板', '拍板', ['red-black-game', 'vice-city-empire']),
    ('delegate', '🔑 授权与放手', '授权', ['stellar-conqueror', 'heavenly-quest']),
    ('informal', '📣 不带权也能带', '不带权', ['silent-leader', 'tangram']),
]
GROUP_NAME = dict((k, n) for k, n, s, ids in GROUPS)
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
    r'[ \t]*<a href="games/leadership/([a-z0-9-]+)\.html" class="card"(.*?)</a>',
    re.S)


def patch_cards(idx, nl):
    """重排领导力网格 → 3 组顺序；每张卡补 data-lead + 肌肉标签胶囊。"""
    m = re.search(r'<div class="grid" id="grid-leadership">(.*?)\n    </div>', idx, re.S)
    assert m, 'index.html 未找到 grid-leadership'
    body = m.group(1)
    cards = {}
    for cm in CARD_RE.finditer(body):
        cards[cm.group(1)] = cm.group(0)
    on_disk = set()
    for f in os.listdir(os.path.join(TB, 'games', 'leadership')):
        if f.endswith('.md'):
            on_disk.add(f[:-3])
    assert set(cards) == on_disk, '网格 %d 款与目录 %d 款不一致：缺 %s 多 %s' % (
        len(cards), len(on_disk), sorted(on_disk - set(cards)), sorted(set(cards) - on_disk))

    out = []
    for k, name, short, ids in GROUPS:
        for gid in ids:
            c = cards[gid]
            if 'data-lead=' in c:
                c = re.sub(r' data-lead="[a-z]+"', '', c)
            c = c.replace('class="card"', 'class="card" data-lead="%s"' % k, 1)
            assert 'data-lead="%s"' % k in c, '%s 未写入 data-lead' % gid
            # 肌肉标签胶囊：同组口径直接印在卡片上（与破冰 / 线上 / 沟通网格同款）
            if '<span class="tag">%s</span>' % name not in c:
                c2 = re.sub(r'(<div class="card-tags">(?:<span class="tag">.*?</span>)*)(</div>)',
                            lambda mm: mm.group(1) + '<span class="tag">%s</span>' % name + mm.group(2),
                            c, count=1, flags=re.S)
                assert c2 != c, '%s 未找到 card-tags 收尾位置' % gid
                c = c2
            out.append(c)
    new_body = nl.join(out)
    new_grid = ('<div class="grid" id="grid-leadership">' + nl + new_body + nl + '    </div>')
    return idx[:m.start()] + new_grid + idx[m.end():]


def patch_filter_row(idx, nl):
    """新增「带人卡在哪一层」二级筛选行（只在选中 👑领导力 时出现）。"""
    if 'id="lead-filter"' in idx:
        return idx
    # ⚠️ index.html 是 CRLF，锚点必须跟着文件换行符走（写死 '\n' 会命中 0 次）
    anchor = '</div>' + nl + '    <div class="filter-group" id="idea-filter"'
    assert idx.count(anchor) == 1, 'idea-filter 之前的锚点命中 %d 次' % idx.count(anchor)
    row = ['    <div class="filter-group" id="lead-filter" style="display:none;">']
    row.append('      <span class="filter-label">带人卡在哪一层：</span>')
    row.append('      <button class="filter-btn active" onclick="toggleFilter(\'lead\', \'all\', this)">全部</button>')
    for k, name, short, ids in GROUPS:
        row.append('      <button class="filter-btn" onclick="toggleFilter(\'lead\', \'%s\', this)">%s</button>'
                   % (k, name))
    row.append('    </div>')
    # ⚠️ 锚点的 `</div>` 是上一行的收尾，必须先把它原样写回再开 lead-filter，
    #    否则 lead-filter 会被嵌套进上一行里（隐藏上一行会连带隐藏领导力行）
    repl = '</div>' + nl + nl.join(row) + nl + '    <div class="filter-group" id="idea-filter"'
    return idx.replace(anchor, repl, 1)


def patch_js(idx, nl):
    """currentFilters + setLeadRow/resetLead + toggleFilter 分支 + filterCards 分支。"""
    # 1) 状态位
    if "  lead: 'all'," not in idx:
        old = "  comm: 'all'," + nl + "};"
        assert idx.count(old) == 1, 'currentFilters 尾部锚点命中 %d 次' % idx.count(old)
        idx = idx.replace(old, "  comm: 'all'," + nl + "  lead: 'all'," + nl + "};", 1)

    # 2) 显隐 + 复位函数（照 setCommRow / resetComm 的同款写法）
    if 'function setLeadRow' not in idx:
        anchor = 'function resetSub() {'
        assert idx.count(anchor) == 1, 'resetSub 锚点命中 %d 次' % idx.count(anchor)
        fn = [
            '// 👑领导力 6 款按「带人这件事卡在哪一层」分 3 组，第二级筛选只在选中领导力时出现',
            'function setLeadRow(on) {',
            "  var row = document.getElementById('lead-filter');",
            "  if (row) { row.style.display = on ? '' : 'none'; }",
            '}',
            '',
            'function resetLead() {',
            "  currentFilters.lead = 'all';",
            "  var row = document.getElementById('lead-filter');",
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

    # 3) toggleFilter：切走领导力分类时复位
    if "value === 'leadership'" not in idx:
        anchor = ("    if (value === 'communication') { setCommRow(true); }" + nl
                  + "    else { resetComm(); setCommRow(false); }" + nl)
        assert idx.count(anchor) == 1, 'toggleFilter 的 comm 分支锚点命中 %d 次' % idx.count(anchor)
        add = ("    // 「带人卡在哪一层」只在选中 👑领导力 时出现；离开领导力分类才复位" + nl
               + "    if (value === 'leadership') { setLeadRow(true); }" + nl
               + "    else { resetLead(); setLeadRow(false); }" + nl)
        idx = idx.replace(anchor, anchor + add, 1)

    # 4) filterCards：按 data-lead 过滤
    if "card.getAttribute('data-lead')" not in idx:
        anchor = ("      // 「沟通坏在哪一环」筛选（仅沟通分类下的 4 组）" + nl)
        assert idx.count(anchor) == 1, 'filterCards 的沟通子类注释锚点命中 %d 次' % idx.count(anchor)
        blk = [
            '      // 「带人卡在哪一层」筛选（仅领导力分类下的 3 组）',
            "      if (visible && currentFilters.lead !== 'all') {",
            "        if (card.getAttribute('data-lead') !== currentFilters.lead) {",
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
    old = '<div style="font-weight:600;color:#555;margin:18px 0 10px;">👑 领导力（leadership）</div>'
    if old in idx:
        new = ('<div style="font-weight:600;color:#555;margin:18px 0 10px;">👑 领导力（leadership） '
               '<span style="font-weight:400;">· 6 款 · 想按「卡在哪一层」挑，见 '
               '<a href="lead.html" style="color:#3366cc;">领导力挑款指南</a></span></div>')
        idx = idx.replace(old, new, 1)
    chip_anchor = '<a href="comm.html" class="res-chip">💬 沟通共 8 款，帮我挑</a>'
    if chip_anchor in idx and 'lead.html" class="res-chip"' not in idx:
        idx = idx.replace(chip_anchor,
                          chip_anchor + nl + '        <a href="lead.html" class="res-chip">👑 领导力共 6 款，帮我挑</a>',
                          1)
    return idx


# ------------------------------------------------------------------ README.md
README_ROWS = {
    'red-black-game': '[红黑游戏](games/leadership/red-black-game.md) | 室内 · 智力 | 12-40人 | 45-60 min | 培训',
    'vice-city-empire': '[帝国董事会 · 增长与负债（改造版）](games/leadership/vice-city-empire.md) | 室内 · 经营+决策 | 6–16人 | 60–90 min | 领导力/培训/工作坊',
    'stellar-conqueror': '[星域远征 · 继任与授权（改造版）](games/leadership/stellar-conqueror.md) | 室内 · 策略+授权 | 8–20人（6–8人/组） | 70–100 min | 领导力/培训/工作坊',
    'heavenly-quest': '[天庭远征 · 出师与传功（改造版）](games/leadership/heavenly-quest.md) | 室内 · 策略+带教 | 8–24人（6–8人/组） | 75–100 min | 领导力/导师制/工作坊',
    'silent-leader': '[沉默领袖](games/leadership/silent-leader.md) | 室内/户外 · 体力+观察 | 8-20人 | 30-40 min | 培训/工作坊',
    'tangram': '[七巧板](games/leadership/tangram.md) | 室内 · 策略+协作 | 24-49人 | 60-90 min | 培训/工作坊',
}

CROSS_NOTE = ('> 全库带「领导力」标签的共 **9 款**，本页这 6 款之外还有 3 款落在 🤝团队协作分类下'
              '（星际矿工 / 病毒危机 / 怪兽守护者）——按分类挑会漏掉它们，详见 [领导力挑款指南](lead.html)。')


def build_lead_section(nl):
    L = []
    a = L.append
    a('#### 👑 领导力（leadership）')
    a('')
    a('> 领导力是全库最「贵」的一类：6 款里 **5 款要 60 分钟以上**。本节已按'
      '**「带人这件事卡在哪一层」**重排为 3 组（拍板 / 授权 / 不带权）；'
      '不确定选哪组时先看 [领导力挑款指南](lead.html)（含 30 秒决策表与「什么时候别选它」）。')
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
    start = rm.index('#### 👑 领导力（leadership）')
    end = rm.index('#### 💡 创意与解题（creativity')
    # 整块重建（幂等、自愈：不管先前有没有被改成 3 组，都按现值重建）
    seg = rm[start:end].rstrip()
    if 'lead.html' in seg and not FORCE:
        return rm, 'skip'
    rm = rm[:start] + build_lead_section(nl) + nl + rm[end:]

    # 决策表加一行
    row = ('| 👑 目的就是领导力，但 6 款挑不过来 | [领导力挑款指南](lead.html) | '
           '按「带人卡在哪一层」把 6 款分成 3 组（拍板 / 授权 / 不带权），'
           '每组给了首选与「什么时候别选它」；首页选「👑 领导力」会出现同样的 3 个子类按钮 |')
    if '领导力挑款指南](lead.html) |' not in rm:
        anchor = '| 💬 目的就是沟通，但 8 款挑不过来 |'
        assert rm.count(anchor) == 1, 'README 决策表沟通行命中 %d 次' % rm.count(anchor)
        i = rm.index(anchor)
        j = rm.index('\n', i) + 1
        rm = rm[:j] + row + nl + rm[j:]

    # 网页版清单补一条
    # ⚠️ 必须锚到唯一的那一行（`[物资与效率工具](toolbox/checklist.html)` 全文出现 2 次）
    head = '以上 5 份教练资料与生成器均有网页版：'
    assert rm.count(head) == 1, 'README 网页版清单锚点命中 %d 次' % rm.count(head)
    i = rm.index(head)
    j = rm.index(nl, i)
    line = rm[i:j]
    if 'lead.html' not in line:
        rm = rm[:j] + ' · [领导力挑款指南](lead.html)' + rm[j:]
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
    print('README.md：%s' % ('已更新' if st == 'ok' else '已含 lead.html（幂等跳过）'))

    # 自检
    idx = rd(os.path.join(TB, 'index.html'))
    n = len(re.findall(r'data-lead="([a-z]+)"', idx))
    print('领导力卡片 data-lead：%d 张；分组：%s'
          % (n, ', '.join('%s=%d' % (k, len(re.findall(r'data-lead="%s"' % k, idx)))
                          for k, n_, s_, ids_ in GROUPS)))


if __name__ == '__main__':
    main()
