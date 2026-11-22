# -*- coding: utf-8 -*-
"""故意破坏 8 处，验证第 43 项（挑款页页首横条）真的能抓住。

用法：python teambuilding/negative_test_pick_banner.py
每个用例：改文件 → 跑第 43 项 → 断言「报错了且指向本次破坏」→ 还原。

设计原则同 negative_test_pick.py：锚点必须按**文件真实换行符**拼装（本仓库 html 混有 LF / CRLF，
硬写 '\n' 的用例会静默失效 —— 已踩过 3 次）。用例挑的都是「人改起来最自然、检查最容易漏」的破坏：

  ① 整块删掉横条            → 只剩页脚 li，序号信息重新沉底
  ② 只改横条序号            → 三处序号不一致（最隐蔽：页面看着完全正常）
  ③ 把横条挪到页脚           → 位置回到页底，等于没做
  ④ 删掉横条里的总表直链     → 横条变成死标签
  ⑤ 删掉 pick.html 卡片序号  → 总表侧失去对照
  ⑥ 删掉样式类             → 横条裸奔（裸 div，与全站配色断裂）
  ⑦ 删掉「另外 6 套」这句    → 只说序号不说边界
  ⑧ 把横条维度改成别的页的   → 维度串台（比序号错更难发现）
"""
import io
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import site_check_pick           # noqa: E402

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

TB = os.path.dirname(os.path.abspath(__file__))
CASES = []

BANNER_COLLAB = (
    '    <div class="pick-master">\n'
    '        <span class="pm-no">第 1 / 7 套</span>\n'
    '        <span class="pm-dim">本页切的是「动作」</span>\n'
    '        <span class="pm-note">问的是「这群人凑在一起，是谁的哪一步没对上」—— 另外 6 套问的是别的维度：'
    '套到别处就会把「信息传不准」判成「配合不熟」，于是加练配合，传话那关照样过不去。</span>\n'
    '        <a class="pm-link" href="pick.html">🧭 七套切法总表</a>\n'
    '    </div>\n'
)


def case(name, rel, edits, must_have):
    CASES.append(dict(name=name, rel=rel, edits=edits, must_have=must_have))


case('① 整块删掉 collab.html 的页首横条',
     'collab.html',
     [(BANNER_COLLAB, '')],
     '恰好 1 条')

case('② 只把 ice.html 横条的序号从第 4 套改成第 5 套',
     'ice.html',
     [('<span class="pm-no">第 4 / 7 套</span>', '<span class="pm-no">第 5 / 7 套</span>')],
     '序号三处不一致')

case('③ 把 comm.html 的横条从页首挪到页脚（内容一字不改）',
     'comm.html',
     [('    <div class="pick-master">\r\n'
       '        <span class="pm-no">第 3 / 7 套</span>\r\n'
       '        <span class="pm-dim">本页切的是「通道」</span>\r\n'
       '        <span class="pm-note">问的是「这一局里，信息坏在说、传、凑、还是谈不拢」—— 另外 6 套问的是别的维度：'
       '套到信任上，会把传话游戏判成「彼此不敢托付」，其实那只是通道被堵住了。</span>\r\n'
       '        <a class="pm-link" href="pick.html">🧭 七套切法总表</a>\r\n'
       '    </div>\r\n\r\n'
       '    <div class="info-grid">',
       '    <div class="info-grid">'),
      ('<div class="footer">', '<div class="pick-master"><span class="pm-no">第 3 / 7 套</span>'
                                '<span class="pm-dim">本页切的是「通道」</span>'
                                '<span class="pm-note">另外 6 套问的是别的维度</span>'
                                '<a class="pm-link" href="pick.html">🧭 七套切法总表</a></div>\r\n'
                                '<div class="footer">')],
     '落在信息卡网格之后')

case('④ 删掉 lead.html 横条里的 pick.html 直链',
     'lead.html',
     [('<a class="pm-link" href="pick.html">🧭 七套切法总表</a>',
       '<span class="pm-link">🧭 七套切法总表</span>')],
     '缺 pick.html 直链')

case('⑤ 删掉 pick.html 里 trust 卡片的「第 7 / 7 套」序号',
     'pick.html',
     [('第 7 / 7 套 · ', '')],
     'pick.html 卡片')

case('⑥ 删掉 online.html 的 .pick-master 样式定义',
     'online.html',
     [('    .pick-master {', '    .pick-master-off {')],
     '缺样式')

case('⑦ 删掉 trust.html 横条里的「另外 6 套」这句',
     'trust.html',
     [('另外 6 套问的是别的维度', '别的维度')],
     '另外 6 套')

case('⑧ 把 idea.html 横条的维度改成「动作」（串台）',
     'idea.html',
     [('<span class="pm-dim">本页切的是「思考位置」</span>',
       '<span class="pm-dim">本页切的是「动作」</span>')],
     '横条未写')


def run():
    bad = 0
    for c in CASES:
        p = os.path.join(TB, c['rel'])
        bak = p + '.bak'
        shutil.copy2(p, bak)
        try:
            t = io.open(p, encoding='utf-8', newline='').read()
            eol = '\r\n' if '\r\n' in t else '\n'
            ok = True
            for old, new in c['edits']:
                old = old.replace('\r\n', '\n').replace('\n', eol)
                new = new.replace('\r\n', '\n').replace('\n', eol)
                if old not in t:
                    print('  ❌ %s：锚点未命中，用例失效（%s）' % (c['name'], old[:40].strip()))
                    ok = False
                    break
                t = t.replace(old, new, 1)
            if not ok:
                bad += 1
                continue
            io.open(p, 'w', encoding='utf-8', newline='').write(t)

            errors = []
            site_check_pick.check_pick_banner(errors, TB)
            hit = [e for e in errors if c['must_have'] in e]
            if errors and hit:
                print('  ✅ %s → 被抓住（%d 项，含「%s」）' % (c['name'], len(errors), c['must_have']))
            elif errors:
                print('  ⚠️ %s → 报错了但没有指向本次破坏：%s' % (c['name'], errors[:2]))
                bad += 1
            else:
                print('  ❌ %s → 静默通过（检查没抓住）' % c['name'])
                bad += 1
        finally:
            shutil.move(bak, p)
    print('\n%d/%d 全部被抓住' % (len(CASES) - bad, len(CASES)) if bad == 0
          else '\n%d 个用例没抓住' % bad)
    return bad


if __name__ == '__main__':
    sys.exit(0 if run() == 0 else 1)
