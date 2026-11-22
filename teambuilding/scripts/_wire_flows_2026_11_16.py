# -*- coding: utf-8 -*-
"""2026-11-16：把新流程接进两个「入口」——build.py 的 FLOWS（首页流程卡）与 README 流程表。

背景：这两处都只写死 6 套，而 flows/ 下实际有 19 套。新流程如果只落一个 md 文件，
就是又一次「隐身内容」（第 17 项反复踩过的坑）。本轮把两处补成 19 套。
"""
import io
import os
import re
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

TB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (目录/文件名, 图标, 名称, 时长, 人数, 一句话)
ROWS = [
    ('flows/one-day/01-schedule', '📅', '一日团建模板', '6–8 小时', '15–50 人', '破冰 + 协作 + 复盘完整闭环'),
    ('flows/half-day/01-schedule', '⏱️', '半日团建模板', '3–4 小时', '10–30 人', '快速凝聚，适合周五下午'),
    ('flows/annual-party/01-party', '🎉', '年会 / 联欢流程', '4–5 小时', '20–80 人', '不产出、只颁奖与合影 —— 综艺与桌游唯一有格可放的一套'),
    ('flows/workshop/leadership-awakening', '🎓', '主题工作坊：领导力觉醒', '2.5–3 小时', '12–24 人', '深度引导，非娱乐向'),
    ('flows/cross-dept/01-schedule', '🤝', '跨部门协作方案', '6–7 小时', '15–30 人', '打散部门重组，专治部门墙'),
    ('flows/onboarding/01-schedule', '🌱', '新人融入方案', '3–4 小时', '8–20 人', '让新人在第一个月被记住'),
    ('flows/online/01-schedule', '💻', '线上团建模板', '2–2.5 小时', '8–30 人', '远程团队，全程可在线完成'),
    ('flows/debrief/01-workshop', '🔁', '复盘专项工作坊', '2.5–3 小时', '10–30 人', '把一次经历变成团队资产'),
    ('flows/hybrid/01-schedule', '🔀', '混合办公半日团建', '3–3.5 小时', '10–40 人', '线上线下同权同场'),
    ('flows/generational/01-schedule', '👨‍👩‍👧', '跨代际融合团建', '3.5–4 小时', '12–36 人', '经验互换市场，各组必须跨代混编'),
    ('flows/conflict/01-workshop', '⚖️', '冲突调解工作坊', '2.5–3 小时', '6–16 人', '从「谁对」到「什么条件下都会炸」'),
    ('flows/innovation/01-sprint', '💡', '创新 Sprint 工作坊', '6–7 小时', '12–30 人', '一天做出能给人看的东西'),
    ('flows/remote-onboarding/01-schedule', '🖥️', '远程新人融入半日团建', '3–3.5 小时', '8–24 人', '让新同事半天内有人可找'),
    ('flows/annual-review/01-workshop', '📒', '年度总结与展望工作坊', '3–3.5 小时', '8–30 人', '把一年做成一本能交出去的账本'),
    ('flows/strategy-alignment/01-workshop', '🎯', '战略对齐工作坊', '3–4 小时', '10–40 人', '用「不做什么」换出真正的优先级'),
    ('flows/crisis/01-review', '🚨', '危机复盘工作坊', '2–2.5 小时', '6–20 人', '事故之后先接住信号，再谈原因'),
    ('flows/cross-region/01-workshop', '🌍', '跨地域团队融合工作坊', '3–3.5 小时', '12–40 人', '把「时区差」从障碍改成制度'),
    ('flows/merge-integration/01-workshop', '🧬', '团队合并整合工作坊', '3.5–4 小时', '10–30 人', '先摊开两套默认规则，再谈文化融合'),
    ('flows/okr-alignment/01-workshop', '🧭', 'OKR 对齐工作坊', '3–3.5 小时', '8–24 人', '先写「失败的样子」，再谈对齐'),
]

# ------------------------------------------------------------------ build.py
bp = os.path.join(TB, 'build.py')
raw = io.open(bp, encoding='utf-8', newline='').read()
eol = '\r\n' if '\r\n' in raw else '\n'

lines = []
for path, ico, name, dur, ppl, desc in ROWS:
    lines.append("    ('%s.html', '%s', '%s'," % (path, ico, name))
    lines.append("     '%s · %s · %s')," % (dur, ppl, desc))
new_flows = 'FLOWS = [' + eol + eol.join(lines) + eol + ']'

m = re.search(r'FLOWS = \[.*?\r?\n\]', raw, re.S)
assert m, 'build.py 里找不到 FLOWS 列表'
assert raw.count('FLOWS = [') == 1
old_block = m.group(0)
assert 'annual-party' not in old_block, 'FLOWS 已含 annual-party'
raw2 = raw[:m.start()] + new_flows + raw[m.end():]

# FLOW_LABEL：新目录不加会退回「通用」
if "'annual-party'" not in raw2:
    anchor = "        'onboarding': '🌱 新人融入方案',"
    if anchor not in raw2:
        anchor = anchor.replace('        ', '    ')
    assert anchor in raw2, '找不到 FLOW_LABEL 锚点'
    add = anchor + eol + anchor[:len(anchor) - len(anchor.lstrip())] + "'annual-party': '🎉 年会 / 联欢方案',"
    raw2 = raw2.replace(anchor, add, 1)
assert "annual-party': '🎉 年会 / 联欢方案'" in raw2

io.open(bp, 'w', encoding='utf-8', newline='').write(raw2)
print('[build.py] FLOWS %d 条，FLOW_LABEL 已含 annual-party' % len(ROWS))

# ------------------------------------------------------------------ README
rp = os.path.join(TB, 'README.md')
rmd = io.open(rp, encoding='utf-8', newline='').read()
reol = '\r\n' if '\r\n' in rmd else '\n'

head = ('| 方案名称 | 总时长 | 适合人数 | 核心目标 |' + reol +
        '|---------|--------|---------|---------|' + reol)
body = []
for path, ico, name, dur, ppl, desc in ROWS:
    body.append('| [%s](%s.md) | %s | %s | %s |' % (name, path, dur, ppl, desc))
table = head + reol.join(body)

i = rmd.index('| 方案名称 | 总时长 | 适合人数 | 核心目标 |')
j = rmd.index('👉 流程方案在', i)
old_readme = rmd[i:j]
assert old_readme.count('\n| [') == 5, 'README 流程表行数异常：%d' % old_readme.count('\n| [')
rmd2 = rmd[:i] + table + reol + reol + rmd[j:]
assert 'annual-party' in rmd2
assert rmd2.count('| [年会 / 联欢流程]') == 1
io.open(rp, 'w', encoding='utf-8', newline='').write(rmd2)
print('[README] 流程表 6 → %d 行' % len(ROWS))

# 顺手校验：每行路径真实存在
for path, *_ in ROWS:
    assert os.path.exists(os.path.join(TB, path + '.md')), path
    assert os.path.exists(os.path.join(TB, path + '.html')) or 'annual-party' in path, path + ' 无 html'
print('[ok] 19 条路径全部存在（annual-party 的 html 待 build 生成）')
