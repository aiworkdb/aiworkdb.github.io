# -*- coding: utf-8 -*-
"""故意破坏 6 处，验证第 36–41 项检查真的能抓住（不是只查到函数名就放行）。

用法：python teambuilding/negative_test_lead_trust.py
每个用例：改文件 → 跑对应检查 → 断言「报错了」→ 还原。
最后一例特意验证「只删 toggleFilter 里的调用分支」这种最隐蔽的破坏也能被抓住
（第 33 项曾有的同型漏洞：函数名在定义处也存在，光 grep 函数名会漏）。
"""
import io
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import site_check_lead          # noqa: E402
import site_check_trust         # noqa: E402

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


case('① 删掉 index.html 里 toggleFilter 的 leadership 调用分支',
     'index.html',
     "    if (value === 'leadership') { setLeadRow(true); }\n",
     '', site_check_lead.check_lead_index, 'setLeadRow')

case('② 删掉 index.html 里 toggleFilter 的 trust 调用分支',
     'index.html',
     "    if (value === 'trust') { setTrustRow(true); }\n",
     '', site_check_trust.check_trust_index, 'setTrustRow')

case('③ 删掉 lead.html 的「领导力 ≠ 有人站出来」边界说明',
     'lead.html',
     '<h2>🚧 「领导力」不等于「有人站出来」：6 款里只有 2 款真的在练「把事交出去」</h2>',
     '<h2>🚧 边界说明</h2>', site_check_lead.check_lead_index, '边界说明')

case('④ 删掉 trust.html 的「信任 ≠ 敢把后背交出去」边界说明',
     'trust.html',
     '<h2>🚧 「信任」不等于「敢把后背交出去」：6 款里只有 2 款在玩身体托付</h2>',
     '<h2>🚧 边界说明</h2>', site_check_trust.check_trust_index, '边界说明')

case('⑤ 删掉 silent-leader.md 的挑款页锚点链接',
     'games/leadership/silent-leader.md',
     '- [领导力挑款指南 · 📣 不带权也能带这一组](../../lead.html#g-informal)',
     '', site_check_lead.check_lead_backlinks, '锚点链接')

case('⑥ 删掉 trust-fall.html 的挑款章节',
     'games/trust/trust-fall.html',
     '<h2>🔐 信任挑款：这一款托付出去的是什么</h2>',
     '<h2>🔐 信任挑款</h2>', site_check_trust.check_trust_backlinks, '章节')

case('⑦ 生成器改掉 lead 组的组导语（与 lead.html 漂移）',
     'toolbox/generator.html',
     "    lead: '这两款问的都是「这一局往哪打、这个决定怎么拍出来」",
     "    lead: '这两款问的都是「这一局往哪打」", site_check_lead.check_generator_lead_sub, '组导语')

case('⑧ 生成器删掉 ?trust= URL 参数',
     'toolbox/generator.html',
     "  var trust = params.get('trust');",
     '', site_check_trust.check_generator_trust_sub, '?trust=')


def run():
    bad = 0
    for c in CASES:
        p = os.path.join(TB, c['rel'])
        bak = p + '.bak'
        shutil.copy2(p, bak)
        try:
            t = io.open(p, encoding='utf-8', newline='').read()
            # ⚠️ index.html / generator.html 是 CRLF：写死 '\n' 的锚点会命中 0 次
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
