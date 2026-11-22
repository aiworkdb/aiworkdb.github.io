# -*- coding: utf-8 -*-
"""生成器「拼游戏」模式接入 💬沟通 4 组子类（不新增目的按钮 —— 复用既有「💬 沟通表达」）。

背景（ROADMAP 下一步建议 · 2026-10-28 首选）：
    沟通二级索引（comm.html + index 二级筛选行）建好后，生成器选「💬 沟通表达」
    仍会一次性把 communication + trust 两个分类一起吐出来（trust 的盲行等并不在
    那 4 组里）。与「拼游戏 + 目的=线上」接入 4 组子类完全同型。

做法（经验 91：文案一律从挑款页现场抽取，零重写）：
    COMM_GROUPS 的 组名 / 组导语 / 何时选 / 何时别选 / 组内首选 全部从 comm.html
    现成表格抽取，两边永远不会漂移（由 site_check_comm.py 第 35 项双向把关）。

用法（可重复执行，含幂等跳过）：
    python teambuilding/build_comm_generator.py
    python teambuilding/build_comm_generator.py --force
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

# 短名（按钮文案 + 结果卡胶囊用）—— 长名与 n 一律从 comm.html 抽
SHORT = {'express': '说不清', 'relay': '传不准', 'pool': '凑不齐', 'clash': '说不拢'}
TAIL = '<h2>💬 沟通不只是这 8 款</h2>'


def rd(p):
    return io.open(p, encoding='utf-8', newline='').read()


def wr(p, s):
    io.open(p, 'w', encoding='utf-8', newline='').write(s)


def js(s):
    """JS 单引号字符串转义。"""
    return s.replace('\\', '\\\\').replace("'", "\\'")


def parse_comm():
    t = rd(os.path.join(TB, 'comm.html'))
    keys = re.findall(r'<div class="group-card" id="g-([a-z]+)">', t)
    assert len(keys) == 4, 'comm.html 分组数 %d != 4' % len(keys)
    assert t.count(TAIL) == 1, 'comm.html 尾部锚点命中 %d 次' % t.count(TAIL)
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
        pick = re.search(r'🎯 拿不准就先拿：<a href="games/communication/([a-z0-9-]+)\.html"',
                         seg).group(1)
        ids = re.findall(r'<tr><td><a href="games/communication/([a-z0-9-]+)\.html">', seg)
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
    groups = parse_comm()
    all_ids = []
    for g in groups:
        all_ids.extend(g['ids'])
    assert len(set(all_ids)) == 8, '沟通 8 款有重复：%s' % all_ids

    t = rd(GEN)
    # generator.html 是纯 CRLF：先归一化成 LF 再打补丁，写回时还原
    assert t.count('\r\n') == t.count('\n'), 'generator.html 换行符不统一，拒绝改写'
    crlf = '\r\n' in t
    if crlf:
        t = t.replace('\r\n', '\n')

    if 'COMM_GROUPS' in t and not FORCE:
        print('generator.html 已含 COMM_GROUPS（幂等跳过）')
        return

    # ---------- 1) 表单：4 组子类按钮（只在「拼游戏 + 目的=沟通」时出现）----------
    if 'id="comm-sub-form-group"' not in t:
        anchor = '    <div class="form-group" id="collab-sub-form-group" style="display:none;">'
        rows = ['    <div class="form-group" id="comm-sub-form-group" style="display:none;">',
                '      <label class="form-label">💬 沟通坏在哪一环（4 组子类）</label>',
                '      <div class="btn-group" id="comm-sub-group">']
        for g in groups:
            rows.append('        <button class="btn-option" data-value="%s" '
                        'onclick="selectOption(this, \'commSub\')">%s（%d）</button>'
                        % (g['key'], g['short'], g['n']))
        rows.append('        <button class="btn-option" data-value="any" '
                    'onclick="selectOption(this, \'commSub\')">🎯 不限，8 款都看</button>')
        rows.append('      </div>')
        rows.append('      <div class="form-hint" id="comm-sub-hint">选「💬 沟通表达」后'
                    '可以在这里再收一层：这 8 款按「这一局，沟通坏在哪一环」分 4 组</div>')
        rows.append('    </div>')
        rows.append('')
        rows.append(anchor)
        t = sub1(anchor, '\n'.join(rows), t, 'collab-sub-form-group')

    # ---------- 2) 状态位 ----------
    if 'commSub:' not in t:
        t = sub1("  onlineSub: 'any'\n};", "  onlineSub: 'any',\n  commSub: 'any'\n};",
                 t, 'userSelections')
    if 'var lastCommFallback' not in t:
        t = sub1("var lastOnlineFallback = null;\n",
                 "var lastOnlineFallback = null;\n"
                 "\n"
                 "// 最近一次生成是否因\"沟通子类 × 人数/时长\"无解而退回全部 8 款沟通游戏（null = 没退回）\n"
                 "var lastCommFallback = null;\n", t, 'lastOnlineFallback')

    # ---------- 3) COMM_GROUPS / COMM_SUB_OF / COMM_ALL_IDS / commGroup ----------
    if 'var COMM_GROUPS' not in t:
        L = ["// ============ 沟通 4 组子类（2026-10-31 接入「拼游戏」模式）============",
             "// 与 comm.html 的 4 个分组、index.html 的 data-comm 完全同源：",
             "// 组名 / 组导语 / 何时选 / 何时别选 / 组内首选，全部照搬 comm.html 现成文案，",
             "// 不在生成器里另写一份（否则两边会漂移）。由 site_check_comm.py 第 35 项把关。",
             "var COMM_GROUPS = ["]
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
        L.append("var COMM_SUB_OF = {};")
        L.append("COMM_GROUPS.forEach(function(g) {")
        L.append("  g.ids.forEach(function(id) { COMM_SUB_OF[id] = g.key; });")
        L.append("});")
        L.append("")
        L.append("// 沟通 8 款全集：子类无解时回退到这里，而不是放宽到「沟通表达」目的")
        L.append("// （该目的还含 trust 分类的盲行等，它们并不在这 4 组里）")
        L.append("var COMM_ALL_IDS = ['%s'];" % "', '".join(all_ids))
        L.append("")
        L.append("function commGroup(key) {")
        L.append("  return COMM_GROUPS.filter(function(g) { return g.key === key; })[0] || null;")
        L.append("}")
        L.append("")
        L.append("var currentMode = 'flow';")
        t = sub1("var currentMode = 'flow';", '\n'.join(L), t, 'currentMode')

    # ---------- 4) refreshCommSub / renderCommSubHint ----------
    if 'function refreshCommSub' not in t:
        L = ["// 「沟通坏在哪一环」子类只在「拼游戏 + 目的=沟通表达」时出现；切走时复位为「不限」",
             "function refreshCommSub() {",
             "  var box = document.getElementById('comm-sub-form-group');",
             "  var on = (currentMode === 'game' && userSelections.purpose === 'communication');",
             "  box.style.display = on ? '' : 'none';",
             "  if (!on) {",
             "    userSelections.commSub = 'any';",
             "    document.getElementById('comm-sub-group').querySelectorAll('.btn-option').forEach(function(b) {",
             "      b.classList.remove('active');",
             "    });",
             "  }",
             "  renderCommSubHint();",
             "}",
             "",
             "// 提示文案全部取自 comm.html 现成表述，不另写一份（两边永远一致）",
             "function renderCommSubHint() {",
             "  var el = document.getElementById('comm-sub-hint');",
             "  var g = commGroup(userSelections.commSub);",
             "  if (!g) {",
             "    el.innerHTML = '选「💬 沟通表达」后可以在这里再收一层：这 8 款按「这一局，沟通坏在哪一环」'",
             "      + '分 4 组。拿不准看 '",
             "      + '<a href=\"../comm.html\">沟通挑款指南</a>（4 组 + 每组首选 + 什么时候别选它）';",
             "    return;",
             "  }",
             "  var p = gamesDB.filter(function(x) { return x.id === g.pick; })[0];",
             "  el.innerHTML = '<b>' + g.name + '（' + g.n + ' 款）</b><br>' + g.lead +",
             "    '<br>✅ <b>什么情况下选它</b>：' + g.when +",
             "    '<br>⛔ <b>什么时候别选它</b>：' + g.avoid +",
             "    '<br>🎯 <b>拿不准就先拿</b>：' + (p ? '<a href=\"' + gameUrl(p) + '\" target=\"_blank\">' + p.name + '</a>' : '') +",
             "    '（<a href=\"../comm.html#g-' + g.key + '\">看这一组全部 ' + g.n + ' 款</a>）';",
             "}",
             "",
             "// 提示文案全部取自 idea.html 现成表述，不另写一份（两边永远一致）"]
        t = sub1("// 提示文案全部取自 idea.html 现成表述，不另写一份（两边永远一致）",
                 '\n'.join(L), t, 'renderIdeaSubHint 注释')

    # ---------- 5) 调用点：selectMode / selectOption ----------
    if "refreshCommSub();" not in t:
        t = sub1("  refreshOnlineSub();\n}", "  refreshOnlineSub();\n  refreshCommSub();\n}",
                 t, 'selectMode 尾部')
    if "refreshCommSub(); }" not in t:
        t = sub1("if (type === 'purpose') { refreshCollabSub(); refreshIdeaSub(); "
                 "refreshIceSub(); refreshOnlineSub(); }",
                 "if (type === 'purpose') { refreshCollabSub(); refreshIdeaSub(); "
                 "refreshIceSub(); refreshOnlineSub(); refreshCommSub(); }",
                 t, 'selectOption purpose 分支')
    if "type === 'commSub'" not in t:
        t = sub1("  if (type === 'onlineSub') renderOnlineSubHint();",
                 "  if (type === 'onlineSub') renderOnlineSubHint();\n"
                 "  if (type === 'commSub') renderCommSubHint();",
                 t, 'selectOption onlineSub 分支')

    # ---------- 6) 筛选：buildFilter 增第 5 个参数 ----------
    if 'commKey' not in t:
        t = sub1("  var buildFilter = function(subKey, ideaKey, iceKey, onlineKey) {",
                 "  var buildFilter = function(subKey, ideaKey, iceKey, onlineKey, commKey) {",
                 t, 'buildFilter 签名')
        t = sub1("      return matchPeople && matchCategory && matchScene && matchSub "
                 "&& matchIdea && matchIce && matchOnline;",
                 "      // commKey === 'commAll' 表示「全部 8 款沟通」（回退用），不是某一组\n"
                 "      var matchComm = !commKey || (commKey === 'commAll'\n"
                 "        ? COMM_ALL_IDS.indexOf(game.id) >= 0\n"
                 "        : COMM_SUB_OF[game.id] === commKey);\n"
                 "      return matchPeople && matchCategory && matchScene && matchSub "
                 "&& matchIdea && matchIce && matchOnline && matchComm;",
                 t, 'buildFilter return')
        # commSub 取值
        t = sub1("  var onlineSub = (purpose === 'online' && userSelections.onlineSub &&\n"
                 "             userSelections.onlineSub !== 'any') ? userSelections.onlineSub : null;",
                 "  var onlineSub = (purpose === 'online' && userSelections.onlineSub &&\n"
                 "             userSelections.onlineSub !== 'any') ? userSelections.onlineSub : null;\n"
                 "  // 「沟通坏在哪一环」子类：只在目的＝沟通表达且用户选了具体某一组时生效\n"
                 "  var commSub = (purpose === 'communication' && userSelections.commSub &&\n"
                 "           userSelections.commSub !== 'any') ? userSelections.commSub : null;",
                 t, 'onlineSub 取值')
        # 5 处调用点全部补第 5 个参数
        for old, new in (
            ("var filtered = buildFilter(sub, ideaSub, iceSub, onlineSub);",
             "var filtered = buildFilter(sub, ideaSub, iceSub, onlineSub, commSub);"),
            ("filtered = buildFilter(null, ideaSub, iceSub, onlineSub);",
             "filtered = buildFilter(null, ideaSub, iceSub, onlineSub, commSub);"),
            ("filtered = buildFilter(sub, null, iceSub, onlineSub);",
             "filtered = buildFilter(sub, null, iceSub, onlineSub, commSub);"),
            ("filtered = buildFilter(sub, null, 'iceAll', onlineSub);",
             "filtered = buildFilter(sub, null, 'iceAll', onlineSub, commSub);"),
            ("filtered = buildFilter(sub, null, null, 'onlineAll');",
             "filtered = buildFilter(sub, null, null, 'onlineAll', commSub);"),
        ):
            t = sub1(old, new, t, 'buildFilter 调用点')

    # ---------- 7) 无解回退 ----------
    if 'lastCommFallback = commSub' not in t:
        t = sub1("  lastOnlineFallback = null;\n",
                 "  lastOnlineFallback = null;\n  lastCommFallback = null;\n",
                 t, '回退复位')
        # ⚠️ 上一节已经把这一行的 buildFilter 补上了第 5 个参数，
        #    锚点必须用「改过之后」的文本，否则命中 0 次
        t = sub1("    lastOnlineFallback = onlineSub;\n"
                 "    onlineSub = null;\n"
                 "    filtered = buildFilter(sub, null, null, 'onlineAll', commSub);\n"
                 "  }\n",
                 "    lastOnlineFallback = onlineSub;\n"
                 "    onlineSub = null;\n"
                 "    filtered = buildFilter(sub, null, null, 'onlineAll', commSub);\n"
                 "  }\n"
                 "  if (filtered.length === 0 && commSub) {\n"
                 "    // 回退落在「全部 8 款沟通」而不是整个「沟通表达」目的 ——\n"
                 "    // 该目的还含 trust 分类（盲行等），它们并不在这 4 组里\n"
                 "    lastCommFallback = commSub;\n"
                 "    commSub = null;\n"
                 "    filtered = buildFilter(sub, null, null, null, 'commAll');\n"
                 "  }\n",
                 t, '线上回退分支')

    # ---------- 8) 结果区提示 + 组内胶囊 ----------
    if "if (lastCommFallback)" not in t:
        t = sub1("  if (games.length === 0) {\n"
                 "    html += '<p style=\"color:#888;font-size:0.9em;\">未找到完全匹配的游戏，"
                 "建议调整人数或目的条件。</p>';",
                 "  // 沟通子类 × 人数/时长 无解时，明说「已经把子类条件放掉了」\n"
                 "  if (lastCommFallback) {\n"
                 "    var cfb = commGroup(lastCommFallback);\n"
                 "    html += '<div class=\"notice\">「' + (cfb ? cfb.name : lastCommFallback) + '」这一组在「' +\n"
                 "      PEOPLE_LABEL[userSelections.people] + ' / ' + DURATION_LABEL[userSelections.duration] +\n"
                 "      '」下没有能玩完的一款——已<strong>自动放宽到全部 8 款沟通游戏</strong>，下面是放宽后的结果。' +\n"
                 "      '想守住这一组，可以放宽人数或时长再生成一次；也可以去 <a href=\"../comm.html#g-' + lastCommFallback +\n"
                 "      '\" target=\"_blank\">挑款页看这一组的真实人数与时长</a>。</div>';\n"
                 "  }\n"
                 "\n"
                 "  if (games.length === 0) {\n"
                 "    html += '<p style=\"color:#888;font-size:0.9em;\">未找到完全匹配的游戏，"
                 "建议调整人数或目的条件。</p>';",
                 t, '结果区 games.length 分支')
    if 'COMM_SUB_OF[game.id]' not in t:
        t = sub1("      if (game.parallel) html += '<span class=\"game-tag\">👥 可分多组并行</span>';",
                 "      var ckey = COMM_SUB_OF[game.id];\n"
                 "      if (ckey) {\n"
                 "        var cg = commGroup(ckey);\n"
                 "        html += '<span class=\"game-tag\"><a href=\"../comm.html#g-' + ckey + "
                 "'\" target=\"_blank\" style=\"color:inherit;text-decoration:none;\">' + "
                 "(cg ? cg.short : ckey) + '</a></span>';\n"
                 "      }\n"
                 "      if (game.parallel) html += '<span class=\"game-tag\">👥 可分多组并行</span>';",
                 t, '结果卡 parallel 标签')

    # ---------- 9) URL 参数 ?comm= ----------
    if "params.get('comm')" not in t:
        t = sub1("  // 如果所有参数都有，自动生成",
                 "  // 沟通子类：同样排在 purpose 之后\n"
                 "  var comm = params.get('comm');\n"
                 "  if (comm) {\n"
                 "    var cbtn = document.querySelector('#comm-sub-group .btn-option[data-value=\"' + comm + '\"]');\n"
                 "    if (cbtn) selectOption(cbtn, 'commSub');\n"
                 "  }\n"
                 "\n"
                 "  // 如果所有参数都有，自动生成",
                 t, 'URL 参数尾部')

    if crlf:
        t = t.replace('\n', '\r\n')
    wr(GEN, t)
    print('generator.html：已接入沟通 4 组子类（%s）'
          % ', '.join('%s=%d' % (g['key'], g['n']) for g in groups))


if __name__ == '__main__':
    main()
