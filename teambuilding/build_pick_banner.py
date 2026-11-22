# -*- coding: utf-8 -*-
"""给 7 个挑款页的页首（H1 下方、信息卡之上）加一条「本页是七套切法中的第 N 套」横条。

背景：`pick.html` 建成后，7 个挑款页里回指总表的入口只有页面最底部「🔗 相关的入口」里
的一条 li —— 位置太深，教练翻到某一页时几乎不可能看见「还有另外六套切法」。本次把这条
信息提到页首横条。

设计约束：
1. **序号与维度必须只在一个地方定义**（本文件的 PAGES），生成时写死到页面上，再由
   `site_check.py` 第 43 项反向核对「横条序号 == pick.html 30 秒定位表顺序 == 页脚 li 序号」。
2. **配色随页**：横条背景 / 左侧色条 / 徽标取该页自己的 palette（从 `.container` 背景、
   `.header` 渐变里现算），不引入第 8 套配色，避免破坏「116 页 / 116 色」的既有格局。
3. **幂等**：页面已有 `class="pick-master"` 则整页跳过；重复运行不叠加。

用法：python build_pick_banner.py [--dry]
"""
import io
import os
import re
import sys

TB = os.path.dirname(os.path.abspath(__file__))

# (挑款页, 序号, 切的维度, 这一套「问的是什么」, 套错了会怎样)
PAGES = [
    ('collab.html', 1, '动作', '这群人凑在一起，是谁的哪一步没对上',
     '套到别处就会把「信息传不准」判成「配合不熟」，于是加练配合，传话那关照样过不去'),
    ('idea.html', 2, '思考位置', '团队此刻卡在「想不出」还是「解不开」',
     '套到破冰上会挑出一批根本不产出「思考」的游戏，热完场什么也没留下'),
    ('comm.html', 3, '通道', '这一局里，信息坏在说、传、凑、还是谈不拢',
     '套到信任上，会把传话游戏判成「彼此不敢托付」，其实那只是通道被堵住了'),
    ('ice.html', 4, '存量', '这一场结束，团队手里还剩下什么',
     '套到协作上会以为「热闹过就等于配合过」，第二天的活还是没人接'),
    ('online.html', 5, '成立条件', '这一场在远程，靠什么才开得起来',
     '套到领导力上会挑到 6 款里只有 2 款写了线上改造段的游戏，剩下 4 款根本开不了'),
    ('lead.html', 6, '权力层级', '带人这件事，卡在定方向、交出去、还是没职位也要带',
     '套到协作上会把「没人拍板」当成「配合不齐」，练十遍配合也没人做决定'),
    ('trust.html', 7, '托付内容', '这一局，到底把什么交到了对方手上',
     '套到沟通上会把「说清楚了」当成「敢托付了」，说清楚和敢交出去是两件事'),
]

BANNER_TPL = (
    '    <div class="pick-master">\n'
    '        <span class="pm-no">第 {no} / 7 套</span>\n'
    '        <span class="pm-dim">本页切的是「{dim}」</span>\n'
    '        <span class="pm-note">问的是「{ask}」—— 另外 6 套问的是别的维度：'
    '{wrong}。</span>\n'
    '        <a class="pm-link" href="pick.html">🧭 七套切法总表</a>\n'
    '    </div>\n'
)

CSS_TPL = (
    '    .pick-master {{\n'
    '        display: flex; flex-wrap: wrap; align-items: center; gap: 8px 14px;\n'
    '        padding: 13px 40px; background: {bg}; border-left: 5px solid {accent};\n'
    '        border-bottom: 1px solid {border}; font-size: 0.92em; color: {fg};\n'
    '    }}\n'
    '    .pick-master .pm-no {{\n'
    '        background: {accent}; color: {headerfg}; border-radius: 14px;\n'
    '        padding: 3px 12px; font-weight: 700; font-size: 0.95em; white-space: nowrap;\n'
    '    }}\n'
    '    .pick-master .pm-dim {{ font-weight: 700; color: {accent2}; }}\n'
    '    .pick-master .pm-note {{ flex: 1 1 340px; opacity: 0.82; line-height: 1.55; }}\n'
    '    .pick-master .pm-link {{\n'
    '        white-space: nowrap; color: {accent2}; text-decoration: none;\n'
    '        border: 1px solid {accent}; border-radius: 16px; padding: 4px 14px;\n'
    '        font-size: 0.92em;\n'
    '    }}\n'
    '    .pick-master .pm-link:hover {{ background: {bg2}; }}\n'
)


def eol_of(t):
    return '\r\n' if '\r\n' in t else '\n'


def _block(t, sel):
    m = re.search(re.escape(sel) + r'\s*\{[^}]*\}', t)
    return m.group(0) if m else ''


def palette(t):
    """从页面自己的 CSS 里取横条配色（背景 / 色条 / 描边 / 正文 / 页首字色）。"""
    header = _block(t, '.header')
    cont = _block(t, '.container')
    body = _block(t, 'body')
    hx = re.findall(r'#([0-9a-fA-F]{6})', header)
    if len(hx) < 3:
        raise SystemExit('取不到 .header 渐变主色')
    accent = '#' + hx[0]
    accent2 = '#' + hx[2]
    bg = re.search(r'background:\s*(#[0-9a-fA-F]{6})', cont)
    bd = re.search(r'border:\s*1px solid\s*(#[0-9a-fA-F]{6})', cont)
    fg = re.search(r'color:\s*(#[0-9a-fA-F]{6})', body)
    hfg = re.search(r'color:\s*(#[0-9a-fA-F]{6})', header)
    return dict(
        accent=accent, accent2=accent2,
        bg=bg.group(1) if bg else '#0d210f',
        bg2=(bd.group(1) if bd else '#2b6431'),
        border=bd.group(1) if bd else '#2b6431',
        fg=fg.group(1) if fg else '#cfe2d1',
        headerfg=hfg.group(1) if hfg else '#f2fbf3',
    )


def patch(page, no, dim, ask, wrong, dry=False):
    p = os.path.join(TB, page)
    t = io.open(p, encoding='utf-8', newline='').read()
    if 'class="pick-master"' in t:
        return 'skip', '已有横条'
    if '<div class="info-grid">' not in t:
        return 'fail', '找不到 <div class="info-grid"> 锚点'
    if '</style>' not in t:
        return 'fail', '找不到 </style> 锚点'

    nl = eol_of(t)
    pal = palette(t)

    css = CSS_TPL.format(**pal).replace('\n', nl)
    banner = BANNER_TPL.format(no=no, dim=dim, ask=ask, wrong=wrong).replace('\n', nl)

    # CSS 贴在 </style> 前；横条插在信息卡网格前（= H1 之下第一屏）
    t = t.replace('</style>', css + '</style>', 1)
    t = t.replace('    <div class="info-grid">', banner + nl + '    <div class="info-grid">', 1)

    if not dry:
        io.open(p, 'w', encoding='utf-8', newline='').write(t)
    return 'ok', '第 %d 套 · 切「%s」' % (no, dim)


def patch_master(dry=False):
    """总表侧对称：每张卡标题前加「第 N / 7 套 ·」，并说明七页页首有横条。"""
    p = os.path.join(TB, 'pick.html')
    t = io.open(p, encoding='utf-8', newline='').read()
    nl = eol_of(t)
    changed = []

    for page, no, dim, ask, wrong in PAGES:
        slug = page[:-5]
        key = '<div class="group-card" id="p-%s">%s            <h3>' % (slug, nl)
        if key not in t:
            changed.append('%s 锚点未命中' % slug)
            continue
        if re.search(r'id="p-%s">\s*<h3>第 \d+ / 7 套' % slug, t):
            changed.append('%s 已有序号' % slug)
            continue
        t = t.replace(key, key + '第 %d / 7 套 · ' % no, 1)
        changed.append('%s → 第 %d 套' % (slug, no))

    note_anchor = '<p>每张卡里的组名都可以直接点进去（锚到那一页的对应分组）—— 不用先跳页再找。</p>'
    note = ('<p>每张卡里的组名都可以直接点进去（锚到那一页的对应分组）—— 不用先跳页再找。'
            '七页的<strong>页首各有一条横条</strong>，写着「第 N / 7 套 · 本页切的是「X」」，'
            '并跟一句「把这套套到别处会发生什么」；从任何一页都点得回这张总表。</p>')
    if note_anchor in t:
        t = t.replace(note_anchor, note, 1)
        changed.append('总表补「页首横条」说明')
    elif note not in t:
        changed.append('总表说明锚点未命中')

    if not dry:
        io.open(p, 'w', encoding='utf-8', newline='').write(t)
    return changed


def main():
    dry = '--dry' in sys.argv
    for page, no, dim, ask, wrong in PAGES:
        st, msg = patch(page, no, dim, ask, wrong, dry)
        print('%-12s %-4s %s' % (page, st, msg))
    print('--- pick.html ---')
    for line in patch_master(dry):
        print('pick.html    ' + line)


if __name__ == '__main__':
    main()
