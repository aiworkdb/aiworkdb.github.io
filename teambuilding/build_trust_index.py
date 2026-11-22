# -*- coding: utf-8 -*-
"""🔐 信任建立 6 款的二级索引：改 index.html + README.md（trust.html 另建）。

背景（ROADMAP 下一步建议 · 2026-10-31 首选）：
    与领导力同属最后两类没有二级索引的。这是**全库第七套分组口径**：
    协作按「练哪种协作」、创意解题按「卡在哪一步」、破冰按「结束留下什么」、
    线上按「远程靠什么成立」、沟通按「这一局坏在哪一环」、领导力按「带人卡在哪一层」，
    **信任按「托付出去的是什么」** —— 六套都不能互相套用。

核心澄清（trust.html 上那节）：
    「信任」不等于「敢把后背交出去」——6 款里只有 2 款在玩身体托付，而且那 2 款
    恰恰是最不留沉淀的（20–40 min，摔完就完了）。真正的分水岭是**「接住」是不是
    强制的**：前 2 款里不接住会出事，后 4 款里对方可以选择不接住。

用法（可重复执行，含幂等跳过）：
    python teambuilding/build_trust_index.py
    python teambuilding/build_trust_index.py --force
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
    ('body', '🫱 交出身体与安全', '托付身体', ['trust-fall', 'blind-walk']),
    ('truth', '💬 交出会受伤的自己', '托付真话', ['spy-family-trust', 'chef-undercover']),
    ('outcome', '🤝 交出一件事的成败', '托付结果', ['baxian-crossing-sea', 'three-monkeys-defuse']),
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
    r'[ \t]*<a href="games/trust/([a-z0-9-]+)\.html" class="card"(.*?)</a>',
    re.S)


def patch_cards(idx, nl):
    """重排信任网格 → 3 组顺序；每张卡补 data-trust + 肌肉标签胶囊。"""
    m = re.search(r'<div class="grid" id="grid-trust">(.*?)\n    </div>', idx, re.S)
    assert m, 'index.html 未找到 grid-trust'
    body = m.group(1)
    cards = {}
    for cm in CARD_RE.finditer(body):
        cards[cm.group(1)] = cm.group(0)
    on_disk = set()
    for f in os.listdir(os.path.join(TB, 'games', 'trust')):
        if f.endswith('.md'):
            on_disk.add(f[:-3])
    assert set(cards) == on_disk, '网格 %d 款与目录 %d 款不一致：缺 %s 多 %s' % (
        len(cards), len(on_disk), sorted(on_disk - set(cards)), sorted(set(cards) - on_disk))

    out = []
    for k, name, short, ids in GROUPS:
        for gid in ids:
            c = cards[gid]
            if 'data-trust=' in c:
                c = re.sub(r' data-trust="[a-z]+"', '', c)
            c = c.replace('class="card"', 'class="card" data-trust="%s"' % k, 1)
            assert 'data-trust="%s"' % k in c, '%s 未写入 data-trust' % gid
            if '<span class="tag">%s</span>' % name not in c:
                c2 = re.sub(r'(<div class="card-tags">(?:<span class="tag">.*?</span>)*)(</div>)',
                            lambda mm: mm.group(1) + '<span class="tag">%s</span>' % name + mm.group(2),
                            c, count=1, flags=re.S)
                assert c2 != c, '%s 未找到 card-tags 收尾位置' % gid
                c = c2
            out.append(c)
    new_body = nl.join(out)
    new_grid = ('<div class="grid" id="grid-trust">' + nl + new_body + nl + '    </div>')
    return idx[:m.start()] + new_grid + idx[m.end():]


def patch_filter_row(idx, nl):
    """新增「托付出去的是什么」二级筛选行（只在选中 🔐信任 时出现）。"""
    if 'id="trust-filter"' in idx:
        return idx
    anchor = '</div>' + nl + '    <div class="filter-group" id="idea-filter"'
    assert idx.count(anchor) == 1, 'idea-filter 之前的锚点命中 %d 次' % idx.count(anchor)
    row = ['    <div class="filter-group" id="trust-filter" style="display:none;">']
    row.append('      <span class="filter-label">托付出去的是什么：</span>')
    row.append('      <button class="filter-btn active" onclick="toggleFilter(\'trust\', \'all\', this)">全部</button>')
    for k, name, short, ids in GROUPS:
        row.append('      <button class="filter-btn" onclick="toggleFilter(\'trust\', \'%s\', this)">%s</button>'
                   % (k, name))
    row.append('    </div>')
    repl = '</div>' + nl + nl.join(row) + nl + '    <div class="filter-group" id="idea-filter"'
    return idx.replace(anchor, repl, 1)


def patch_js(idx, nl):
    """currentFilters + setTrustRow/resetTrust + toggleFilter 分支 + filterCards 分支。"""
    # 1) 状态位
    if "  trust: 'all'," not in idx:
        old = "  lead: 'all'," + nl + "};"
        assert idx.count(old) == 1, 'currentFilters 尾部锚点命中 %d 次' % idx.count(old)
        idx = idx.replace(old, "  lead: 'all'," + nl + "  trust: 'all'," + nl + "};", 1)

    # 2) 显隐 + 复位函数
    if 'function setTrustRow' not in idx:
        anchor = 'function resetSub() {'
        assert idx.count(anchor) == 1, 'resetSub 锚点命中 %d 次' % idx.count(anchor)
        fn = [
            '// 🔐信任 6 款按「托付出去的是什么」分 3 组，第二级筛选只在选中信任时出现',
            'function setTrustRow(on) {',
            "  var row = document.getElementById('trust-filter');",
            "  if (row) { row.style.display = on ? '' : 'none'; }",
            '}',
            '',
            'function resetTrust() {',
            "  currentFilters.trust = 'all';",
            "  var row = document.getElementById('trust-filter');",
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

    # 3) toggleFilter：切走信任分类时复位
    if "value === 'trust'" not in idx:
        anchor = ("    if (value === 'leadership') { setLeadRow(true); }" + nl
                  + "    else { resetLead(); setLeadRow(false); }" + nl)
        assert idx.count(anchor) == 1, 'toggleFilter 的 lead 分支锚点命中 %d 次' % idx.count(anchor)
        add = ("    // 「托付出去的是什么」只在选中 🔐信任 时出现；离开信任分类才复位" + nl
               + "    if (value === 'trust') { setTrustRow(true); }" + nl
               + "    else { resetTrust(); setTrustRow(false); }" + nl)
        idx = idx.replace(anchor, anchor + add, 1)

    # 4) filterCards：按 data-trust 过滤
    if "card.getAttribute('data-trust')" not in idx:
        anchor = ("      // 「带人卡在哪一层」筛选（仅领导力分类下的 3 组）" + nl)
        assert idx.count(anchor) == 1, 'filterCards 的领导力子类注释锚点命中 %d 次' % idx.count(anchor)
        blk = [
            '      // 「托付出去的是什么」筛选（仅信任分类下的 3 组）',
            "      if (visible && currentFilters.trust !== 'all') {",
            "        if (card.getAttribute('data-trust') !== currentFilters.trust) {",
            '          visible = false;',
            '        }',
            '      }',
            '',
            '',
        ]
        idx = idx.replace(anchor, nl.join(blk) + anchor, 1)
    return idx


def patch_title_and_chip(idx, nl):
    """分类小标题加挑款页入口（顺手把 🤖 修正为 🔐，与 README / 全站口径一致）+ 首屏胶囊。"""
    old = '<div style="font-weight:600;color:#555;margin:18px 0 10px;">🤖 信任建立（trust）</div>'
    if old in idx:
        new = ('<div style="font-weight:600;color:#555;margin:18px 0 10px;">🔐 信任建立（trust） '
               '<span style="font-weight:400;">· 6 款 · 想按「托付出去的是什么」挑，见 '
               '<a href="trust.html" style="color:#3366cc;">信任挑款指南</a></span></div>')
        idx = idx.replace(old, new, 1)
    chip_anchor = '<a href="lead.html" class="res-chip">👑 领导力共 6 款，帮我挑</a>'
    if chip_anchor in idx and 'trust.html" class="res-chip"' not in idx:
        idx = idx.replace(chip_anchor,
                          chip_anchor + nl + '        <a href="trust.html" class="res-chip">🔐 信任共 6 款，帮我挑</a>',
                          1)
    return idx


# ------------------------------------------------------------------ README.md
README_ROWS = {
    'trust-fall': '[信任背摔](games/trust/trust-fall.md) | 室内/户外 · 体力 | 8-20人 | 20-40 min | 团建',
    'blind-walk': '[盲行](games/trust/blind-walk.md) | 室内/户外 · 混合 | 任意偶数 | 20-35 min | 团建/培训',
    'spy-family-trust': '[间谍过家家 · 真心之家（改造版）](games/trust/spy-family-trust.md) | 室内 · 信任+心理安全 | 6-16人 | 60-90 min | 团建/培训/工作坊',
    'chef-undercover': '[信任厨房 · 隐患与澄清（改造版）](games/trust/chef-undercover.md) | 室内 · 推理+澄清 | 6–16人 | 50–75 min | 信任修复/培训/工作坊',
    'baxian-crossing-sea': '[八仙渡海 · 回渡与结缆（改造版）](games/trust/baxian-crossing-sea.md) | 室内 · 托付+回渡 | 8-24人 | 60-90 min | 团建/培训/工作坊',
    'three-monkeys-defuse': '[三猿拆弹 · 无声引信（改造版）](games/trust/three-monkeys-defuse.md) | 室内 · 链式信任+示弱 | 8-24人 | 55-80 min | 团建/培训/工作坊',
}

CROSS_NOTE = ('> 全库带「信任」标签的共 **10 款**，本页这 6 款之外还有 4 款落在别的分类里'
              '（🤝协作：黄金结界；💬沟通：盲人方阵 / 谣言工厂；👑领导力：红黑游戏）'
              '——按分类挑会漏掉它们，详见 [信任挑款指南](trust.html)。')


def build_trust_section(nl):
    L = []
    a = L.append
    a('#### 🔐 信任建立（trust）')
    a('')
    a('> 信任是最常被点名、也最常被简化成「背摔 + 盲行」的一类 —— 而那两款恰恰是'
      '**最不留沉淀**的两款（20–40 min）。本节已按**「托付出去的是什么」**重排为 3 组'
      '（身体 / 真话 / 结果）；不确定选哪组时先看 [信任挑款指南](trust.html)'
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
    start = rm.index('#### 🔐 信任建立（trust）')
    end = rm.index('#### 👑 领导力（leadership）')
    seg = rm[start:end].rstrip()
    if 'trust.html' in seg and not FORCE:
        return rm, 'skip'
    rm = rm[:start] + build_trust_section(nl) + nl + rm[end:]

    row = ('| 🔐 目的就是信任，但 6 款挑不过来 | [信任挑款指南](trust.html) | '
           '按「托付出去的是什么」把 6 款分成 3 组（身体 / 真话 / 结果），'
           '每组给了首选与「什么时候别选它」；首页选「🔐 信任」会出现同样的 3 个子类按钮 |')
    if '信任挑款指南](trust.html) |' not in rm:
        anchor = '| 👑 目的就是领导力，但 6 款挑不过来 |'
        assert rm.count(anchor) == 1, 'README 决策表领导力行命中 %d 次' % rm.count(anchor)
        i = rm.index(anchor)
        j = rm.index('\n', i) + 1
        rm = rm[:j] + row + nl + rm[j:]

    head = '以上 5 份教练资料与生成器均有网页版：'
    assert rm.count(head) == 1, 'README 网页版清单锚点命中 %d 次' % rm.count(head)
    i = rm.index(head)
    j = rm.index(nl, i)
    line = rm[i:j]
    if 'trust.html' not in line:
        rm = rm[:j] + ' · [信任挑款指南](trust.html)' + rm[j:]
    return rm, 'ok'


def main():
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

    p = os.path.join(TB, 'README.md')
    rm = rd(p)
    new, st = patch_readme(rm)
    if new != rm:
        wr(p, new)
    print('README.md：%s' % ('已更新' if st == 'ok' else '已含 trust.html（幂等跳过）'))

    idx = rd(os.path.join(TB, 'index.html'))
    n = len(re.findall(r'data-trust="([a-z]+)"', idx))
    print('信任卡片 data-trust：%d 张；分组：%s'
          % (n, ', '.join('%s=%d' % (k, len(re.findall(r'data-trust="%s"' % k, idx)))
                          for k, n_, s_, ids_ in GROUPS)))


if __name__ == '__main__':
    main()
