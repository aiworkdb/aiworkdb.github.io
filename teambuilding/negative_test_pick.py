# -*- coding: utf-8 -*-
"""故意破坏 8 处，验证第 42 项（挑款总入口）与收紧后的第 27 / 30 项真的能抓住。

用法：python teambuilding/negative_test_pick.py
每个用例：改文件 → 跑对应检查 → 断言「报错了且指向本次破坏」→ 还原。

最后两例专门验证 2026-11-02 的**检查收紧**：
第 27 / 30 项此前只 grep "value === 'icebreaker'" / "value === 'online'" 子串，
把 toggleFilter 里的调用分支整条删掉仍能通过（第 33 项曾有同型漏洞）。
"""
import io
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import site_check                # noqa: E402
import site_check_pick           # noqa: E402
import site_check_online        # noqa: E402

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

TB = os.path.dirname(os.path.abspath(__file__))
CASES = []


def case(name, rel, old, new, checker, must_have):
    CASES.append(dict(name=name, rel=rel, old=old, new=new,
                      checker=checker, must_have=must_have))


def _legacy(fn):
    """第 27 项还是旧式写法（无参数，直接往 site_check.errors 全局里写）——包一层适配。"""
    def _run(errors, _tb):
        site_check.errors[:] = []
        fn()
        errors.extend(site_check.errors)
    return _run


def _pick_all(errors, tb):
    """第 42 + 43 项一起跑。

    ⚠️ 2026-11-03 起：第 42 项「页脚必须有 pick.html 直链」这一断言**被页首横条顶替了**
    —— 横条里也有 href="pick.html"，删掉页脚 li 时第 42 项仍会通过（静默漏洞）。
    页脚那条 li 现在由第 43 项的「三处序号同源」兜住（它要求页脚出现「本页是其中第 N 套」），
    所以本用例必须两项一起跑，否则会误报「静默通过」。
    """
    site_check_pick.check_pick_index(errors, tb)
    site_check_pick.check_pick_banner(errors, tb)


case('① 删掉 pick.html 里协作卡片的一个组名胶囊',
     'pick.html',
     'href="collab.html#g-whole"',
     'href="collab.html#g-whole-typo"',
     site_check_pick.check_pick_index, '组名胶囊')

case('② 把 pick.html 里沟通卡片的款数改成 9 款',
     'pick.html',
     '（8 款 / 4 组 · 切「通道」）',
     '（9 款 / 4 组 · 切「通道」）',
     site_check_pick.check_pick_index, 'comm.html 有 9 款')

case('③ 删掉 pick.html 里破冰卡片的边界澄清',
     'pick.html',
     '<b>破冰不等于「认识彼此」：四档暴露度</b>',
     '<b>边界说明</b>',
     site_check_pick.check_pick_index, '边界澄清')

case('④ 删掉 trust.html 回指 pick.html 的页脚入口',
     'trust.html',
     '            <li><a href="pick.html">🧭 挑款总入口 · 七套切法对照</a> —— 本页是其中第 7 套：切「托付内容」，另外 6 套问的是别的维度</li>\n',
     '',
     _pick_all, '页脚')

case('⑤ 删掉 index.html 首屏的 pick.html 胶囊',
     'index.html',
     '        <a href="pick.html" class="res-chip">🧭 8 个分类怎么挑？七套切法对照</a>\n',
     '',
     site_check_pick.check_pick_index, 'index.html 首屏缺')

case('⑥ 把 ice.html 的破冰算术改回「8 + 6」的错误说法',
     'ice.html',
     '本页 8 款里只有',
     '除了本页这 8 款，另有',
     site_check_pick.check_pick_index, '口径说明')

case('⑦【收紧】删掉 index.html 里 toggleFilter 的 icebreaker 调用分支',
     'index.html',
     "    if (value === 'icebreaker') { setIceRow(true); }\n",
     '',
     _legacy(site_check.check_ice_index), 'setIceRow')

case('⑧【收紧】删掉 index.html 里 toggleFilter 的 online 调用分支',
     'index.html',
     "    if (value === 'online') { setOnlineRow(true); }\n",
     '',
     site_check_online.check_online_index, 'setOnlineRow')


def run():
    bad = 0
    for c in CASES:
        p = os.path.join(TB, c['rel'])
        bak = p + '.bak'
        shutil.copy2(p, bak)
        try:
            t = io.open(p, encoding='utf-8', newline='').read()
            # ⚠️ pick.html / 挑款页是 LF，index.html 是 CRLF：锚点必须按文件真实换行符拼装
            eol = '\r\n' if '\r\n' in t else '\n'
            old = c['old'].replace('\n', eol)
            new = c['new'].replace('\n', eol)
            if old not in t:
                print('  ❌ %s：锚点未命中，用例失效' % c['name'])
                bad += 1
                continue
            io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))
            errors = []
            c['checker'](errors, TB)
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
