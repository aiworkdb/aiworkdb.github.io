# -*- coding: utf-8 -*-
"""README 流程表：6 行 → 19 行（补上一直隐身的 13 套 + 新增的年会流程）。"""
import io
import os
import re
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

TB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ROWS = [
    ('flows/one-day/01-schedule', '一日团建模板', '6–8 小时', '15–50人', '破冰+协作+复盘'),
    ('flows/half-day/01-schedule', '半日团建模板', '3–4 小时', '10–30人', '快速凝聚'),
    ('flows/annual-party/01-party', '年会 / 联欢流程', '4–5 小时', '20–80人', '**不产出**、只颁奖与合影（综艺与桌游唯一有格可放的一套）'),
    ('flows/workshop/leadership-awakening', '主题工作坊模板', '2.5–3 小时', '12–24人', '领导力深度培训'),
    ('flows/cross-dept/01-schedule', '跨部门协作团建流程', '6–7 小时', '15–30人', '打破部门墙，提升跨部门协作效率'),
    ('flows/onboarding/01-schedule', '新员工融入团建流程', '3–4 小时', '8–20人', '帮助新员工快速融入团队'),
    ('flows/online/01-schedule', '线上团建模板', '2–2.5 小时', '8–30人', '远程团队团建'),
    ('flows/debrief/01-workshop', '复盘专项工作坊', '2.5–3 小时', '10–30人', '把一次经历变成团队资产'),
    ('flows/hybrid/01-schedule', '混合办公半日团建', '3–3.5 小时', '10–40人', '线上线下同权同场'),
    ('flows/generational/01-schedule', '跨代际融合团建', '3.5–4 小时', '12–36人', '经验互换市场，跨代混编'),
    ('flows/conflict/01-workshop', '冲突调解工作坊', '2.5–3 小时', '6–16人', '从「谁对」到「什么条件下都会炸」'),
    ('flows/innovation/01-sprint', '创新 Sprint 工作坊', '6–7 小时', '12–30人', '一天做出能给人看的东西'),
    ('flows/remote-onboarding/01-schedule', '远程新人融入半日团建', '3–3.5 小时', '8–24人', '让新同事半天内有人可找'),
    ('flows/annual-review/01-workshop', '年度总结与展望工作坊', '3–3.5 小时', '8–30人', '把一年做成一本能交出去的账本'),
    ('flows/strategy-alignment/01-workshop', '战略对齐工作坊', '3–4 小时', '10–40人', '用「不做什么」换出真正的优先级'),
    ('flows/crisis/01-review', '危机复盘工作坊', '2–2.5 小时', '6–20人', '事故后先接住信号，再谈原因'),
    ('flows/cross-region/01-workshop', '跨地域团队融合工作坊', '3–3.5 小时', '12–40人', '把「时区差」从障碍改成制度'),
    ('flows/merge-integration/01-workshop', '团队合并整合工作坊', '3.5–4 小时', '10–30人', '先摊开两套默认规则，再谈文化融合'),
    ('flows/okr-alignment/01-workshop', 'OKR 对齐工作坊', '3–3.5 小时', '8–24人', '先写「失败的样子」，再谈对齐'),
]

rp = os.path.join(TB, 'README.md')
rmd = io.open(rp, encoding='utf-8', newline='').read()
reol = '\r\n' if '\r\n' in rmd else '\n'

head = ('| 方案名称 | 总时长 | 适合人数 | 核心目标 |' + reol +
        '|---------|--------|---------|---------|')
body = ['| [%s](%s.md) | %s | %s | %s |' % (n, p, t, pp, c) for p, n, t, pp, c in ROWS]
table = head + reol + reol.join(body)

i = rmd.index('| 方案名称 | 总时长 | 适合人数 | 核心目标 |')
j = rmd.index('👉 流程方案在', i)
old = rmd[i:j]
n_rows = len([ln for ln in old.split(reol) if ln.startswith('| [')])
assert n_rows in (6, 19), 'README 流程表行数异常：%d' % n_rows

rmd2 = rmd[:i] + table + reol + reol + rmd[j:]
assert rmd2.count('| [年会 / 联欢流程]') == 1
assert rmd2.count('| [OKR 对齐工作坊]') == 1
io.open(rp, 'w', encoding='utf-8', newline='').write(rmd2)
print('[README] 流程表 %d → %d 行' % (n_rows, len(ROWS)))

for p, *_ in ROWS:
    assert os.path.exists(os.path.join(TB, p + '.md')), p
print('[ok] 19 条 md 路径全部存在')
