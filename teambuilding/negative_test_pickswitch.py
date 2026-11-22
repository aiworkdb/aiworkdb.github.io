# -*- coding: utf-8 -*-
"""故意破坏 5 处，验证第 44 项（生成器「🔀 换一整套切法」）真的能抓住。

用法：python teambuilding/negative_test_pickswitch.py
每个用例：改 generator.html → 跑第 44 项 → 断言「报错了且指向本次破坏」→ 还原。

用例挑的是「改起来最自然、最不容易被发现」的破坏：
  ① 删掉一个胶囊            → 那一套切法在生成器里彻底进不去（其余六套照常能用，很难发现）
  ② 漏复位一个子类           → 会带着「瓶颈与流水线」去筛沟通，静默出 0 款
  ③ 删掉整套流程分支的显隐     → 选「推荐整套流程」后这条横条还赖在结果区
  ④ 删掉顶部目的按钮同步       → 上方按钮亮着「协作」、下方胶囊亮着「信任」，两处打脸
  ⑤ 删掉胶囊 active 样式      → 选中态看不出来，等于没有当前口径提示
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


def case(name, old, new, must_have):
    CASES.append(dict(name=name, old=old, new=new, must_have=must_have))


case('① 删掉「🔐 托付内容」那个胶囊',
     '<button class="pick-chip" data-purpose="trust" onclick="switchPickClass(this)">🔐 托付内容 · 信任</button>\n',
     '',
     '不同序或不同集合')

case('② switchPickClass 漏掉 refreshCommSub()',
     '  refreshCommSub(); refreshLeadSub(); refreshTrustSub();',
     '  refreshLeadSub(); refreshTrustSub();',
     '漏复位子类')

case('③ 删掉整套流程分支里对横条的显隐',
     "    setCardVisible('pick-switch-bar', !flowMode);\n",
     '',
     '整套流程分支没有按 flowMode 显隐')

case('④ switchPickClass 不同步顶部「🎯 主要目的」按钮',
     "  var pg = document.getElementById('purpose-group');",
     "  var pg = document.getElementById('purpose-group-x');",
     '顶部「🎯 主要目的」按钮')

case('⑤ 删掉 .pick-chip.active 样式',
     '    .pick-chip.active { background: #5b8cfe; border-color: #5b8cfe; color: #fff; }\n',
     '',
     '缺样式')


def run():
    bad = 0
    p = os.path.join(TB, 'toolbox', 'generator.html')
    for c in CASES:
        bak = p + '.bak'
        shutil.copy2(p, bak)
        try:
            t = io.open(p, encoding='utf-8', newline='').read()
            eol = '\r\n' if '\r\n' in t else '\n'
            old = c['old'].replace('\r\n', '\n').replace('\n', eol)
            new = c['new'].replace('\r\n', '\n').replace('\n', eol)
            if old not in t:
                print('  ❌ %s：锚点未命中，用例失效（%s）' % (c['name'], old[:36].strip()))
                bad += 1
                continue
            io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(old, new, 1))

            errors = []
            site_check_pick.check_generator_pick_switch(errors, TB)
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
