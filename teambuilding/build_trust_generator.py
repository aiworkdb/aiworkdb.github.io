# -*- coding: utf-8 -*-
"""生成器「拼游戏」模式接入 🔐信任 3 组子类（不新增目的按钮 —— 复用既有「🔐 信任建立」）。

背景（ROADMAP 下一步建议 · 2026-10-31 首选）：
    信任二级索引（trust.html + index 二级筛选行）建好后，生成器选「🔐 信任建立」
    仍会一次性把 trust + communication 两个分类一起吐出来（8 款沟通并不在那 3 组里）。
    与「拼游戏 + 目的=线上 / 沟通 / 领导力」接入子类完全同型。

做法（经验 91：文案一律从挑款页现场抽取，零重写）：
    TRUST_GROUPS 的 组名 / 组导语 / 何时选 / 何时别选 / 组内首选 全部从 trust.html
    现成表格抽取，两边永远不会漂移（由 site_check_trust.py 把关）。

用法（可重复执行，含幂等跳过）：
    python teambuilding/build_trust_generator.py
    python teambuilding/build_trust_generator.py --force
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

SHORT = {'body': '托付身体', 'truth': '托付真话', 'outcome': '托付结果'}
TAIL = '<h2>🔐 信任不只是这 6 款</h2>'


def rd(p):
    return io.open(p, encoding='utf-8', newline='').read()


def wr(p, s):
    io.open(p, 'w', encoding='utf-8', newline='').write(s)


def js(s):
    """JS 单引号字符串转义。"""
    return s.replace('\\', '\\\\').replace("'", "\\'")


def parse_trust():
    t = rd(os.path.join(TB, 'trust.html'))
    keys = re.findall(r'<div class="group-card" id="g-([a-z]+)">', t)
    assert len(keys) == 3, 'trust.html 分组数 %d != 3' % len(keys)
    assert t.count(TAIL) == 1, 'trust.html 尾部锚点命中 %d 次' % t.count(TAIL)
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
        pick = re.search(r'🎯 拿不准就先拿：<a href="games/trust/([a-z0-9-]+)\.html"',
                         seg).group(1)
        ids = re.findall(r'<tr><td><a href="games/trust/([a-z0-9-]+)\.html">', seg)
        assert len(ids) == n, '组 %s 表格 %d 款，标题写 %d 款' % (k, len(ids), n)
        assert pick in ids, '组 %s 的首选 %s 不在本组' % (k, pick)
        out.append(dict(key=k, name=name, short=SHORT[k], n=n, lead=lead,
                        when=when, avoid=avoid, pick=pick, ids=ids))
    return out


def sub1(old, new, t, label):
    assert t.count(old) == 1, '%s 锚点命中 %d 次' % (label, t.count(old))
    return t.replace(old, new, 1)


def main():
    groups = parse_trust()
    all_ids = []
    for g in groups:
        all_ids.extend(g['ids'])
    assert len(set(all_ids)) == 6, '信任 6 款有重复：%s' % all_ids

    t = rd(GEN)
    assert t.count('\r\n') == t.count('\n'), 'generator.html 换行符不统一，拒绝改写'
    crlf = '\r\n' in t
    if crlf:
        t = t.replace('\r\n', '\n')

    if 'TRUST_GROUPS' in t and not FORCE:
        print('generator.html 已含 TRUST_GROUPS（幂等跳过）')
        return

    # ---------- 1) 表单 ----------
    if 'id="trust-sub-form-group"' not in t:
        anchor = '    <div class="form-group" id="collab-sub-form-group" style="display:none;">'
        rows = ['    <div class="form-group" id="trust-sub-form-group" style="display:none;">',
                '      <label class="form-label">🔐 托付出去的是什么（3 组子类）</label>',
                '      <div class="btn-group" id="trust-sub-group">']
        for g in groups:
            rows.append('        <button class="btn-option" data-value="%s" '
                        'onclick="selectOption(this, \'trustSub\')">%s（%d）</button>'
                        % (g['key'], g['short'], g['n']))
        rows.append('        <button class="btn-option" data-value="any" '
                    'onclick="selectOption(this, \'trustSub\')">🎯 不限，6 款都看</button>')
        rows.append('      </div>')
        rows.append('      <div class="form-hint" id="trust-sub-hint">选「🔐 信任建立」后'
                    '可以在这里再收一层：这 6 款按「托付出去的是什么」分 3 组</div>')
        rows.append('    </div>')
        rows.append('')
        rows.append(anchor)
        t = sub1(anchor, '\n'.join(rows), t, 'collab-sub-form-group')

    # ---------- 2) 状态位 ----------
    if 'trustSub:' not in t:
        t = sub1("  onlineSub: 'any',\n  commSub: 'any',\n  leadSub: 'any'\n};",
                 "  onlineSub: 'any',\n  commSub: 'any',\n  leadSub: 'any',\n  trustSub: 'any'\n};",
                 t, 'userSelections')
    if 'var lastTrustFallback' not in t:
        t = sub1("var lastLeadFallback = null;\n",
                 "var lastLeadFallback = null;\n"
                 "\n"
                 "// 最近一次生成是否因\"信任子类 × 人数\"无解而退回全部 6 款信任（null = 没退回）\n"
                 "var lastTrustFallback = null;\n", t, 'lastLeadFallback')

    # ---------- 3) TRUST_GROUPS / TRUST_SUB_OF / TRUST_ALL_IDS / trustGroup ----------
    if 'var TRUST_GROUPS' not in t:
        L = ["// ============ 信任 3 组子类（2026-11-01 接入「拼游戏」模式）============",
             "// 与 trust.html 的 3 个分组、index.html 的 data-trust 完全同源：",
             "// 组名 / 组导语 / 何时选 / 何时别选 / 组内首选，全部照搬 trust.html 现成文案，",
             "// 不在生成器里另写一份（否则两边会漂移）。由 site_check_trust.py 把关。",
             "var TRUST_GROUPS = ["]
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
        L.append("var TRUST_SUB_OF = {};")
        L.append("TRUST_GROUPS.forEach(function(g) {")
        L.append("  g.ids.forEach(function(id) { TRUST_SUB_OF[id] = g.key; });")
        L.append("});")
        L.append("")
        L.append("// 信任 6 款全集：子类无解时回退到这里，而不是放宽到「信任建立」目的")
        L.append("// （该目的还含 communication 分类的 8 款沟通，它们并不在这 3 组里）")
        L.append("var TRUST_ALL_IDS = ['%s'];" % "', '".join(all_ids))
        L.append("")
        L.append("function trustGroup(key) {")
        L.append("  return TRUST_GROUPS.filter(function(g) { return g.key === key; })[0] || null;")
        L.append("}")
        L.append("")
        L.append("var currentMode = 'flow';")
        t = sub1("var currentMode = 'flow';", '\n'.join(L), t, 'currentMode')

    # ---------- 4) refreshTrustSub / renderTrustSubHint ----------
    if 'function refreshTrustSub' not in t:
        L = ["// 「托付出去的是什么」子类只在「拼游戏 + 目的=信任建立」时出现；切走时复位为「不限」",
             "function refreshTrustSub() {",
             "  var box = document.getElementById('trust-sub-form-group');",
             "  var on = (currentMode === 'game' && userSelections.purpose === 'trust');",
             "  box.style.display = on ? '' : 'none';",
             "  if (!on) {",
             "    userSelections.trustSub = 'any';",
             "    document.getElementById('trust-sub-group').querySelectorAll('.btn-option').forEach(function(b) {",
             "      b.classList.remove('active');",
             "    });",
             "  }",
             "  renderTrustSubHint();",
             "}",
             "",
             "// 提示文案全部取自 trust.html 现成表述，不另写一份（两边永远一致）",
             "function renderTrustSubHint() {",
             "  var el = document.getElementById('trust-sub-hint');",
             "  var g = trustGroup(userSelections.trustSub);",
             "  if (!g) {",
             "    el.innerHTML = '选「🔐 信任建立」后可以在这里再收一层：这 6 款按「托付出去的是什么」'",
             "      + '分 3 组。拿不准看 '",
             "      + '<a href=\"../trust.html\">信任挑款指南</a>（3 组 + 每组首选 + 什么时候别选它）';",
             "    return;",
             "  }",
             "  var p = gamesDB.filter(function(x) { return x.id === g.pick; })[0];",
             "  el.innerHTML = '<b>' + g.name + '（' + g.n + ' 款）</b><br>' + g.lead +",
             "    '<br>✅ <b>什么情况下选它</b>：' + g.when +",
             "    '<br>⛔ <b>什么时候别选它</b>：' + g.avoid +",
             "    '<br>🎯 <b>拿不准就先拿</b>：' + (p ? '<a href=\"' + gameUrl(p) + '\" target=\"_blank\">' + p.name + '</a>' : '') +",
             "    '（<a href=\"../trust.html#g-' + g.key + '\">看这一组全部 ' + g.n + ' 款</a>）';",
             "}",
             "",
             "// 提示文案全部取自 idea.html 现成表述，不另写一份（两边永远一致）"]
        t = sub1("// 提示文案全部取自 idea.html 现成表述，不另写一份（两边永远一致）",
                 '\n'.join(L), t, 'renderIdeaSubHint 注释')

    # ---------- 5) 调用点 ----------
    if "refreshTrustSub();" not in t:
        t = sub1("  refreshOnlineSub();\n  refreshCommSub();\n  refreshLeadSub();\n}",
                 "  refreshOnlineSub();\n  refreshCommSub();\n  refreshLeadSub();\n  refreshTrustSub();\n}",
                 t, 'selectMode 尾部')
    if "refreshTrustSub(); }" not in t:
        t = sub1("if (type === 'purpose') { refreshCollabSub(); refreshIdeaSub(); "
                 "refreshIceSub(); refreshOnlineSub(); refreshCommSub(); refreshLeadSub(); }",
                 "if (type === 'purpose') { refreshCollabSub(); refreshIdeaSub(); "
                 "refreshIceSub(); refreshOnlineSub(); refreshCommSub(); refreshLeadSub(); "
                 "refreshTrustSub(); }",
                 t, 'selectOption purpose 分支')
    if "type === 'trustSub'" not in t:
        t = sub1("  if (type === 'leadSub') renderLeadSubHint();",
                 "  if (type === 'leadSub') renderLeadSubHint();\n"
                 "  if (type === 'trustSub') renderTrustSubHint();",
                 t, 'selectOption leadSub 分支')

    # ---------- 6) 筛选：buildFilter 增第 7 个参数 ----------
    if 'trustKey' not in t:
        t = sub1("  var buildFilter = function(subKey, ideaKey, iceKey, onlineKey, commKey, leadKey) {",
                 "  var buildFilter = function(subKey, ideaKey, iceKey, onlineKey, commKey, leadKey, trustKey) {",
                 t, 'buildFilter 签名')
        t = sub1("      return matchPeople && matchCategory && matchScene && matchSub "
                 "&& matchIdea && matchIce && matchOnline && matchComm && matchLead;",
                 "      // trustKey === 'trustAll' 表示「全部 6 款信任」（回退用），不是某一组\n"
                 "      var matchTrust = !trustKey || (trustKey === 'trustAll'\n"
                 "        ? TRUST_ALL_IDS.indexOf(game.id) >= 0\n"
                 "        : TRUST_SUB_OF[game.id] === trustKey);\n"
                 "      return matchPeople && matchCategory && matchScene && matchSub "
                 "&& matchIdea && matchIce && matchOnline && matchComm && matchLead && matchTrust;",
                 t, 'buildFilter return')
        t = sub1("  var leadSub = (purpose === 'leadership' && userSelections.leadSub &&\n"
                 "           userSelections.leadSub !== 'any') ? userSelections.leadSub : null;",
                 "  var leadSub = (purpose === 'leadership' && userSelections.leadSub &&\n"
                 "           userSelections.leadSub !== 'any') ? userSelections.leadSub : null;\n"
                 "  // 「托付出去的是什么」子类：只在目的＝信任建立且用户选了具体某一组时生效\n"
                 "  var trustSub = (purpose === 'trust' && userSelections.trustSub &&\n"
                 "           userSelections.trustSub !== 'any') ? userSelections.trustSub : null;",
                 t, 'leadSub 取值')
        for old, new in (
            ("var filtered = buildFilter(sub, ideaSub, iceSub, onlineSub, commSub, leadSub);",
             "var filtered = buildFilter(sub, ideaSub, iceSub, onlineSub, commSub, leadSub, trustSub);"),
            ("filtered = buildFilter(null, ideaSub, iceSub, onlineSub, commSub, leadSub);",
             "filtered = buildFilter(null, ideaSub, iceSub, onlineSub, commSub, leadSub, trustSub);"),
            ("filtered = buildFilter(sub, null, iceSub, onlineSub, commSub, leadSub);",
             "filtered = buildFilter(sub, null, iceSub, onlineSub, commSub, leadSub, trustSub);"),
            ("filtered = buildFilter(sub, null, 'iceAll', onlineSub, commSub, leadSub);",
             "filtered = buildFilter(sub, null, 'iceAll', onlineSub, commSub, leadSub, trustSub);"),
            ("filtered = buildFilter(sub, null, null, 'onlineAll', commSub, leadSub);",
             "filtered = buildFilter(sub, null, null, 'onlineAll', commSub, leadSub, trustSub);"),
            ("filtered = buildFilter(sub, null, null, null, 'commAll', leadSub);",
             "filtered = buildFilter(sub, null, null, null, 'commAll', leadSub, trustSub);"),
            ("filtered = buildFilter(sub, null, null, null, null, 'leadAll');",
             "filtered = buildFilter(sub, null, null, null, null, 'leadAll', trustSub);"),
        ):
            t = sub1(old, new, t, 'buildFilter 调用点')

    # ---------- 7) 无解回退 ----------
    if 'lastTrustFallback = trustSub' not in t:
        t = sub1("  lastLeadFallback = null;\n",
                 "  lastLeadFallback = null;\n  lastTrustFallback = null;\n",
                 t, '回退复位')
        t = sub1("    lastLeadFallback = leadSub;\n"
                 "    leadSub = null;\n"
                 "    filtered = buildFilter(sub, null, null, null, null, 'leadAll', trustSub);\n"
                 "  }\n",
                 "    lastLeadFallback = leadSub;\n"
                 "    leadSub = null;\n"
                 "    filtered = buildFilter(sub, null, null, null, null, 'leadAll', trustSub);\n"
                 "  }\n"
                 "  if (filtered.length === 0 && trustSub) {\n"
                 "    // 回退落在「全部 6 款信任」而不是整个「信任建立」目的 ——\n"
                 "    // 该目的还含 communication 分类（8 款沟通），它们并不在这 3 组里\n"
                 "    lastTrustFallback = trustSub;\n"
                 "    trustSub = null;\n"
                 "    filtered = buildFilter(sub, null, null, null, null, null, 'trustAll');\n"
                 "  }\n",
                 t, '领导力回退分支')

    # ---------- 8) 结果区提示 + 组内胶囊 ----------
    if "if (lastTrustFallback)" not in t:
        t = sub1("  if (games.length === 0) {\n"
                 "    html += '<p style=\"color:#888;font-size:0.9em;\">未找到完全匹配的游戏，"
                 "建议调整人数或目的条件。</p>';",
                 "  // 信任子类 × 人数 无解时，明说「已经把子类条件放掉了」\n"
                 "  if (lastTrustFallback) {\n"
                 "    var tfb = trustGroup(lastTrustFallback);\n"
                 "    html += '<div class=\"notice\">「' + (tfb ? tfb.name : lastTrustFallback) + '」这一组在「' +\n"
                 "      PEOPLE_LABEL[userSelections.people] + '」这个人数下没有能玩完的一款——已"
                 "<strong>自动放宽到全部 6 款信任游戏</strong>，下面是放宽后的结果。' +\n"
                 "      '想守住这一组，可以放宽人数再生成一次；也可以去 <a href=\"../trust.html#g-' + lastTrustFallback +\n"
                 "      '\" target=\"_blank\">挑款页看这一组的真实人数与时长</a>。</div>';\n"
                 "  }\n"
                 "\n"
                 "  if (games.length === 0) {\n"
                 "    html += '<p style=\"color:#888;font-size:0.9em;\">未找到完全匹配的游戏，"
                 "建议调整人数或目的条件。</p>';",
                 t, '结果区 games.length 分支')
    if 'TRUST_SUB_OF[game.id]' not in t:
        t = sub1("      if (game.parallel) html += '<span class=\"game-tag\">👥 可分多组并行</span>';",
                 "      var tkey = TRUST_SUB_OF[game.id];\n"
                 "      if (tkey) {\n"
                 "        var tg = trustGroup(tkey);\n"
                 "        html += '<span class=\"game-tag\"><a href=\"../trust.html#g-' + tkey + "
                 "'\" target=\"_blank\" style=\"color:inherit;text-decoration:none;\">' + "
                 "(tg ? tg.short : tkey) + '</a></span>';\n"
                 "      }\n"
                 "      if (game.parallel) html += '<span class=\"game-tag\">👥 可分多组并行</span>';",
                 t, '结果卡 parallel 标签')

    # ---------- 9) URL 参数 ?trust= ----------
    if "params.get('trust')" not in t:
        t = sub1("  // 如果所有参数都有，自动生成",
                 "  // 信任子类：同样排在 purpose 之后\n"
                 "  var trust = params.get('trust');\n"
                 "  if (trust) {\n"
                 "    var tbtn = document.querySelector('#trust-sub-group .btn-option[data-value=\"' + trust + '\"]');\n"
                 "    if (tbtn) selectOption(tbtn, 'trustSub');\n"
                 "  }\n"
                 "\n"
                 "  // 如果所有参数都有，自动生成",
                 t, 'URL 参数尾部')

    if crlf:
        t = t.replace('\n', '\r\n')
    wr(GEN, t)
    print('generator.html：已接入信任 3 组子类（%s）'
          % ', '.join('%s=%d' % (g['key'], g['n']) for g in groups))


if __name__ == '__main__':
    main()
