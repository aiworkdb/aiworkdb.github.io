# -*- coding: utf-8 -*-
"""生成器「拼游戏」模式接入 👑领导力 3 组子类（不新增目的按钮 —— 复用既有「👑 领导力」）。

背景（ROADMAP 下一步建议 · 2026-10-31 首选）：
    领导力二级索引（lead.html + index 二级筛选行）建好后，生成器选「👑 领导力」
    仍会一次性把 leadership + collaboration 两个分类一起吐出来（39 款协作并不在
    那 3 组里）。与「拼游戏 + 目的=线上 / 沟通」接入子类完全同型。

做法（经验 91：文案一律从挑款页现场抽取，零重写）：
    LEAD_GROUPS 的 组名 / 组导语 / 何时选 / 何时别选 / 组内首选 全部从 lead.html
    现成表格抽取，两边永远不会漂移（由 site_check_lead.py 把关）。

用法（可重复执行，含幂等跳过）：
    python teambuilding/build_lead_generator.py
    python teambuilding/build_lead_generator.py --force
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
GEN = os.path.join(TB, 'toolbox', 'generator.html')
FORCE = '--force' in sys.argv

# 短名（按钮文案 + 结果卡胶囊用）—— 长名与 n 一律从 lead.html 抽
SHORT = {'decide': '拍板', 'delegate': '授权', 'informal': '不带权'}
TAIL = '<h2>👑 领导力不只是这 6 款</h2>'


def rd(p):
    return io.open(p, encoding='utf-8', newline='').read()


def wr(p, s):
    io.open(p, 'w', encoding='utf-8', newline='').write(s)


def js(s):
    """JS 单引号字符串转义。"""
    return s.replace('\\', '\\\\').replace("'", "\\'")


def parse_lead():
    t = rd(os.path.join(TB, 'lead.html'))
    keys = re.findall(r'<div class="group-card" id="g-([a-z]+)">', t)
    assert len(keys) == 3, 'lead.html 分组数 %d != 3' % len(keys)
    assert t.count(TAIL) == 1, 'lead.html 尾部锚点命中 %d 次' % t.count(TAIL)
    out = []
    for k in keys:
        start = t.index('<div class="group-card" id="g-%s">' % k)
        nxt = [t.index('<div class="group-card" id="g-%s">' % x)
               for x in keys if t.index('<div class="group-card" id="g-%s">' % x) > start]
        end = min(nxt) if nxt else t.index(TAIL)
        seg = t[start:end]
        h3 = re.search(r'<h3>(.*?)（(\d+) 款）</h3>', seg, re.S)
        name = h3.group(1).strip()
        n = int(h3.group(2))
        lead = re.search(r'<div class="group-lead">(.*?)</div>', seg, re.S).group(1).strip()
        when = re.search(r'<div class="when-box"><b>✅ 什么情况下选它</b><br>(.*?)</div>',
                         seg, re.S).group(1).strip()
        avoid = re.search(r'<div class="avoid-box"><b>⛔ 什么时候别选它</b><br>(.*?)</div>',
                          seg, re.S).group(1).strip()
        pick = re.search(r'🎯 拿不准就先拿：<a href="games/leadership/([a-z0-9-]+)\.html"',
                         seg).group(1)
        ids = re.findall(r'<tr><td><a href="games/leadership/([a-z0-9-]+)\.html">', seg)
        assert len(ids) == n, '组 %s 表格 %d 款，标题写 %d 款' % (k, len(ids), n)
        assert pick in ids, '组 %s 的首选 %s 不在本组' % (k, pick)
        out.append(dict(key=k, name=name, short=SHORT[k], n=n, lead=lead,
                        when=when, avoid=avoid, pick=pick, ids=ids))
    return out


def sub1(old, new, t, label):
    """单次替换 + 命中次数断言（写错锚点要立刻炸，不能静默跳过）。"""
    assert t.count(old) == 1, '%s 锚点命中 %d 次' % (label, t.count(old))
    return t.replace(old, new, 1)


def main():
    groups = parse_lead()
    all_ids = []
    for g in groups:
        all_ids.extend(g['ids'])
    assert len(set(all_ids)) == 6, '领导力 6 款有重复：%s' % all_ids

    t = rd(GEN)
    # generator.html 是纯 CRLF：先归一化成 LF 再打补丁，写回时还原
    assert t.count('\r\n') == t.count('\n'), 'generator.html 换行符不统一，拒绝改写'
    crlf = '\r\n' in t
    if crlf:
        t = t.replace('\r\n', '\n')

    if 'LEAD_GROUPS' in t and not FORCE:
        print('generator.html 已含 LEAD_GROUPS（幂等跳过）')
        return

    # ---------- 1) 表单：3 组子类按钮（只在「拼游戏 + 目的=领导力」时出现）----------
    if 'id="lead-sub-form-group"' not in t:
        anchor = '    <div class="form-group" id="collab-sub-form-group" style="display:none;">'
        rows = ['    <div class="form-group" id="lead-sub-form-group" style="display:none;">',
                '      <label class="form-label">👑 带人卡在哪一层（3 组子类）</label>',
                '      <div class="btn-group" id="lead-sub-group">']
        for g in groups:
            rows.append('        <button class="btn-option" data-value="%s" '
                        'onclick="selectOption(this, \'leadSub\')">%s（%d）</button>'
                        % (g['key'], g['short'], g['n']))
        rows.append('        <button class="btn-option" data-value="any" '
                    'onclick="selectOption(this, \'leadSub\')">🎯 不限，6 款都看</button>')
        rows.append('      </div>')
        rows.append('      <div class="form-hint" id="lead-sub-hint">选「👑 领导力」后'
                    '可以在这里再收一层：这 6 款按「带人这件事卡在哪一层」分 3 组</div>')
        rows.append('    </div>')
        rows.append('')
        rows.append(anchor)
        t = sub1(anchor, '\n'.join(rows), t, 'collab-sub-form-group')

    # ---------- 2) 状态位 ----------
    if 'leadSub:' not in t:
        t = sub1("  onlineSub: 'any',\n  commSub: 'any'\n};",
                 "  onlineSub: 'any',\n  commSub: 'any',\n  leadSub: 'any'\n};",
                 t, 'userSelections')
    if 'var lastLeadFallback' not in t:
        t = sub1("var lastCommFallback = null;\n",
                 "var lastCommFallback = null;\n"
                 "\n"
                 "// 最近一次生成是否因\"领导力子类 × 人数\"无解而退回全部 6 款领导力（null = 没退回）\n"
                 "var lastLeadFallback = null;\n", t, 'lastCommFallback')

    # ---------- 3) LEAD_GROUPS / LEAD_SUB_OF / LEAD_ALL_IDS / leadGroup ----------
    if 'var LEAD_GROUPS' not in t:
        L = ["// ============ 领导力 3 组子类（2026-11-01 接入「拼游戏」模式）============",
             "// 与 lead.html 的 3 个分组、index.html 的 data-lead 完全同源：",
             "// 组名 / 组导语 / 何时选 / 何时别选 / 组内首选，全部照搬 lead.html 现成文案，",
             "// 不在生成器里另写一份（否则两边会漂移）。由 site_check_lead.py 把关。",
             "var LEAD_GROUPS = ["]
        for g in groups:
            L.append("  { key: '%s', name: '%s', short: '%s', n: %d," % (
                g['key'], js(g['name']), js(g['short']), g['n']))
            L.append("    lead: '%s'," % js(g['lead']))
            L.append("    when: '%s'," % js(g['when']))
            L.append("    avoid: '%s'," % js(g['avoid']))
            L.append("    pick: '%s'," % g['pick'])
            L.append("    ids: ['%s'] }," % "', '".join(g['ids']))
        L.append("];")
        L.append("")
        L.append("var LEAD_SUB_OF = {};")
        L.append("LEAD_GROUPS.forEach(function(g) {")
        L.append("  g.ids.forEach(function(id) { LEAD_SUB_OF[id] = g.key; });")
        L.append("});")
        L.append("")
        L.append("// 领导力 6 款全集：子类无解时回退到这里，而不是放宽到「领导力」目的")
        L.append("// （该目的还含 collaboration 分类的 39 款协作，它们并不在这 3 组里）")
        L.append("var LEAD_ALL_IDS = ['%s'];" % "', '".join(all_ids))
        L.append("")
        L.append("function leadGroup(key) {")
        L.append("  return LEAD_GROUPS.filter(function(g) { return g.key === key; })[0] || null;")
        L.append("}")
        L.append("")
        L.append("var currentMode = 'flow';")
        t = sub1("var currentMode = 'flow';", '\n'.join(L), t, 'currentMode')

    # ---------- 4) refreshLeadSub / renderLeadSubHint ----------
    if 'function refreshLeadSub' not in t:
        L = ["// 「带人卡在哪一层」子类只在「拼游戏 + 目的=领导力」时出现；切走时复位为「不限」",
             "function refreshLeadSub() {",
             "  var box = document.getElementById('lead-sub-form-group');",
             "  var on = (currentMode === 'game' && userSelections.purpose === 'leadership');",
             "  box.style.display = on ? '' : 'none';",
             "  if (!on) {",
             "    userSelections.leadSub = 'any';",
             "    document.getElementById('lead-sub-group').querySelectorAll('.btn-option').forEach(function(b) {",
             "      b.classList.remove('active');",
             "    });",
             "  }",
             "  renderLeadSubHint();",
             "}",
             "",
             "// 提示文案全部取自 lead.html 现成表述，不另写一份（两边永远一致）",
             "function renderLeadSubHint() {",
             "  var el = document.getElementById('lead-sub-hint');",
             "  var g = leadGroup(userSelections.leadSub);",
             "  if (!g) {",
             "    el.innerHTML = '选「👑 领导力」后可以在这里再收一层：这 6 款按「带人这件事卡在哪一层」'",
             "      + '分 3 组。拿不准看 '",
             "      + '<a href=\"../lead.html\">领导力挑款指南</a>（3 组 + 每组首选 + 什么时候别选它）';",
             "    return;",
             "  }",
             "  var p = gamesDB.filter(function(x) { return x.id === g.pick; })[0];",
             "  el.innerHTML = '<b>' + g.name + '（' + g.n + ' 款）</b><br>' + g.lead +",
             "    '<br>✅ <b>什么情况下选它</b>：' + g.when +",
             "    '<br>⛔ <b>什么时候别选它</b>：' + g.avoid +",
             "    '<br>🎯 <b>拿不准就先拿</b>：' + (p ? '<a href=\"' + gameUrl(p) + '\" target=\"_blank\">' + p.name + '</a>' : '') +",
             "    '（<a href=\"../lead.html#g-' + g.key + '\">看这一组全部 ' + g.n + ' 款</a>）';",
             "}",
             "",
             "// 提示文案全部取自 idea.html 现成表述，不另写一份（两边永远一致）"]
        t = sub1("// 提示文案全部取自 idea.html 现成表述，不另写一份（两边永远一致）",
                 '\n'.join(L), t, 'renderIdeaSubHint 注释')

    # ---------- 5) 调用点：selectMode / selectOption ----------
    if "refreshLeadSub();" not in t:
        t = sub1("  refreshOnlineSub();\n  refreshCommSub();\n}",
                 "  refreshOnlineSub();\n  refreshCommSub();\n  refreshLeadSub();\n}",
                 t, 'selectMode 尾部')
    if "refreshLeadSub(); }" not in t:
        t = sub1("if (type === 'purpose') { refreshCollabSub(); refreshIdeaSub(); "
                 "refreshIceSub(); refreshOnlineSub(); refreshCommSub(); }",
                 "if (type === 'purpose') { refreshCollabSub(); refreshIdeaSub(); "
                 "refreshIceSub(); refreshOnlineSub(); refreshCommSub(); refreshLeadSub(); }",
                 t, 'selectOption purpose 分支')
    if "type === 'leadSub'" not in t:
        t = sub1("  if (type === 'commSub') renderCommSubHint();",
                 "  if (type === 'commSub') renderCommSubHint();\n"
                 "  if (type === 'leadSub') renderLeadSubHint();",
                 t, 'selectOption commSub 分支')

    # ---------- 6) 筛选：buildFilter 增第 6 个参数 ----------
    if 'leadKey' not in t:
        t = sub1("  var buildFilter = function(subKey, ideaKey, iceKey, onlineKey, commKey) {",
                 "  var buildFilter = function(subKey, ideaKey, iceKey, onlineKey, commKey, leadKey) {",
                 t, 'buildFilter 签名')
        t = sub1("      return matchPeople && matchCategory && matchScene && matchSub "
                 "&& matchIdea && matchIce && matchOnline && matchComm;",
                 "      // leadKey === 'leadAll' 表示「全部 6 款领导力」（回退用），不是某一组\n"
                 "      var matchLead = !leadKey || (leadKey === 'leadAll'\n"
                 "        ? LEAD_ALL_IDS.indexOf(game.id) >= 0\n"
                 "        : LEAD_SUB_OF[game.id] === leadKey);\n"
                 "      return matchPeople && matchCategory && matchScene && matchSub "
                 "&& matchIdea && matchIce && matchOnline && matchComm && matchLead;",
                 t, 'buildFilter return')
        # leadSub 取值
        t = sub1("  var commSub = (purpose === 'communication' && userSelections.commSub &&\n"
                 "           userSelections.commSub !== 'any') ? userSelections.commSub : null;",
                 "  var commSub = (purpose === 'communication' && userSelections.commSub &&\n"
                 "           userSelections.commSub !== 'any') ? userSelections.commSub : null;\n"
                 "  // 「带人卡在哪一层」子类：只在目的＝领导力且用户选了具体某一组时生效\n"
                 "  var leadSub = (purpose === 'leadership' && userSelections.leadSub &&\n"
                 "           userSelections.leadSub !== 'any') ? userSelections.leadSub : null;",
                 t, 'commSub 取值')
        # 6 处调用点全部补第 6 个参数
        for old, new in (
            ("var filtered = buildFilter(sub, ideaSub, iceSub, onlineSub, commSub);",
             "var filtered = buildFilter(sub, ideaSub, iceSub, onlineSub, commSub, leadSub);"),
            ("filtered = buildFilter(null, ideaSub, iceSub, onlineSub, commSub);",
             "filtered = buildFilter(null, ideaSub, iceSub, onlineSub, commSub, leadSub);"),
            ("filtered = buildFilter(sub, null, iceSub, onlineSub, commSub);",
             "filtered = buildFilter(sub, null, iceSub, onlineSub, commSub, leadSub);"),
            ("filtered = buildFilter(sub, null, 'iceAll', onlineSub, commSub);",
             "filtered = buildFilter(sub, null, 'iceAll', onlineSub, commSub, leadSub);"),
            ("filtered = buildFilter(sub, null, null, 'onlineAll', commSub);",
             "filtered = buildFilter(sub, null, null, 'onlineAll', commSub, leadSub);"),
            ("filtered = buildFilter(sub, null, null, null, 'commAll');",
             "filtered = buildFilter(sub, null, null, null, 'commAll', leadSub);"),
        ):
            t = sub1(old, new, t, 'buildFilter 调用点')

    # ---------- 7) 无解回退 ----------
    if 'lastLeadFallback = leadSub' not in t:
        t = sub1("  lastCommFallback = null;\n",
                 "  lastCommFallback = null;\n  lastLeadFallback = null;\n",
                 t, '回退复位')
        # ⚠️ 上一节已经把这一行的 buildFilter 补上了第 6 个参数，
        #    锚点必须用「改过之后」的文本，否则命中 0 次
        t = sub1("    lastCommFallback = commSub;\n"
                 "    commSub = null;\n"
                 "    filtered = buildFilter(sub, null, null, null, 'commAll', leadSub);\n"
                 "  }\n",
                 "    lastCommFallback = commSub;\n"
                 "    commSub = null;\n"
                 "    filtered = buildFilter(sub, null, null, null, 'commAll', leadSub);\n"
                 "  }\n"
                 "  if (filtered.length === 0 && leadSub) {\n"
                 "    // 回退落在「全部 6 款领导力」而不是整个「领导力」目的 ——\n"
                 "    // 该目的还含 collaboration 分类（39 款协作），它们并不在这 3 组里\n"
                 "    lastLeadFallback = leadSub;\n"
                 "    leadSub = null;\n"
                 "    filtered = buildFilter(sub, null, null, null, null, 'leadAll');\n"
                 "  }\n",
                 t, '沟通回退分支')

    # ---------- 8) 结果区提示 + 组内胶囊 ----------
    if "if (lastLeadFallback)" not in t:
        t = sub1("  if (games.length === 0) {\n"
                 "    html += '<p style=\"color:#888;font-size:0.9em;\">未找到完全匹配的游戏，"
                 "建议调整人数或目的条件。</p>';",
                 "  // 领导力子类 × 人数 无解时，明说「已经把子类条件放掉了」\n"
                 "  if (lastLeadFallback) {\n"
                 "    var lfb = leadGroup(lastLeadFallback);\n"
                 "    html += '<div class=\"notice\">「' + (lfb ? lfb.name : lastLeadFallback) + '」这一组在「' +\n"
                 "      PEOPLE_LABEL[userSelections.people] + '」这个人数下没有能玩完的一款——已"
                 "<strong>自动放宽到全部 6 款领导力游戏</strong>，下面是放宽后的结果。' +\n"
                 "      '想守住这一组，可以放宽人数再生成一次；也可以去 <a href=\"../lead.html#g-' + lastLeadFallback +\n"
                 "      '\" target=\"_blank\">挑款页看这一组的真实人数与时长</a>。</div>';\n"
                 "  }\n"
                 "\n"
                 "  if (games.length === 0) {\n"
                 "    html += '<p style=\"color:#888;font-size:0.9em;\">未找到完全匹配的游戏，"
                 "建议调整人数或目的条件。</p>';",
                 t, '结果区 games.length 分支')
    if 'LEAD_SUB_OF[game.id]' not in t:
        t = sub1("      if (game.parallel) html += '<span class=\"game-tag\">👥 可分多组并行</span>';",
                 "      var lkey = LEAD_SUB_OF[game.id];\n"
                 "      if (lkey) {\n"
                 "        var lg = leadGroup(lkey);\n"
                 "        html += '<span class=\"game-tag\"><a href=\"../lead.html#g-' + lkey + "
                 "'\" target=\"_blank\" style=\"color:inherit;text-decoration:none;\">' + "
                 "(lg ? lg.short : lkey) + '</a></span>';\n"
                 "      }\n"
                 "      if (game.parallel) html += '<span class=\"game-tag\">👥 可分多组并行</span>';",
                 t, '结果卡 parallel 标签')

    # ---------- 9) URL 参数 ?lead= ----------
    if "params.get('lead')" not in t:
        t = sub1("  // 如果所有参数都有，自动生成",
                 "  // 领导力子类：同样排在 purpose 之后\n"
                 "  var lead = params.get('lead');\n"
                 "  if (lead) {\n"
                 "    var lbtn = document.querySelector('#lead-sub-group .btn-option[data-value=\"' + lead + '\"]');\n"
                 "    if (lbtn) selectOption(lbtn, 'leadSub');\n"
                 "  }\n"
                 "\n"
                 "  // 如果所有参数都有，自动生成",
                 t, 'URL 参数尾部')

    if crlf:
        t = t.replace('\n', '\r\n')
    wr(GEN, t)
    print('generator.html：已接入领导力 3 组子类（%s）'
          % ', '.join('%s=%d' % (g['key'], g['n']) for g in groups))


if __name__ == '__main__':
    main()
