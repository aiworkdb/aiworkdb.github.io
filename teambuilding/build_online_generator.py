# -*- coding: utf-8 -*-
"""给 toolbox/generator.html 接入「线上」的 4 组子类（2026-10-28 自动化第四十二次）。

背景：
    生成器是全站唯一「按处境一次出一组」的入口。此前它只有协作 6 组、创意解题 4 组、
    破冰 4 组三层子类，而 💻线上团建 这一目的既没有二层筛选，也无法按组挑 ——
    选了「线上团建」时 8 款线上游戏混在一起出，教练还是挑不动。

做法（与 2026-10-25 协作子类、2026-10-26 创意解题子类、2026-10-27 破冰子类完全同构）：
  1) 在既有的「💻 线上团建」目的下新增「线上怎么玩」4 组子类筛选行
     （不新增目的按钮 —— 线上团建本来就有，重复加会让两个入口口径打架）
  2) 组名 / 组导语 / 何时选 / 何时别选 / 组内首选，全部照搬 online.html 的原文，
     不在生成器里另写一份（否则两边必然漂移）
  3) 子类 × 人数/时长 无解时显式回退并说明，不静默换口径；
     回退的目标是**全部 8 款线上游戏**（而不是放宽到整个「线上团建」目的）
  4) URL 参数 ?online=<key> 可直接分享某一组

复用原则（经验 91）：文案一律取自 online.html，本脚本生成后由 site_check.py
第 32 项逐字比对，漂移即红。

用法：
    python teambuilding/build_online_generator.py
幂等：已含 ONLINE_GROUPS 时跳过。
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


def rd(p):
    return io.open(p, encoding='utf-8').read()


def wr(p, s):
    s = s.replace('\r\n', '\n').replace('\n', '\r\n')
    io.open(p, 'w', encoding='utf-8', newline='').write(s)


def rep(text, old, new, what):
    assert text.count(old) == 1, '锚点不唯一(%d)或未命中: %s' % (text.count(old), what)
    return text.replace(old, new)


def parse_online_groups():
    """从 online.html 抽 4 组的原文（组名 / 导语 / 何时选 / 何时别选 / 首选 / 成员）。"""
    t = rd(os.path.join(TB, 'online.html'))
    keys = re.findall(r'<div class="group-card" id="g-([a-z]+)">', t)
    assert len(keys) == 4, 'online.html 分组数 %d != 4' % len(keys)
    tail = '<h2>💻 线上不只是这 8 款</h2>'
    assert t.count(tail) == 1, 'online.html 尾部锚点命中 %d 次' % t.count(tail)
    groups = []
    for k in keys:
        start = t.index('<div class="group-card" id="g-%s">' % k)
        nxt = [t.index('<div class="group-card" id="g-%s">' % x)
               for x in keys if t.index('<div class="group-card" id="g-%s">' % x) > start]
        end = min(nxt) if nxt else t.index(tail)
        seg = t[start:end]
        h3 = re.search(r'<h3>(.*?)（(\d+) 款）</h3>', seg, re.S)
        title = h3.group(1).strip()
        n = int(h3.group(2))
        lead = re.search(r'<div class="group-lead">(.*?)</div>', seg, re.S).group(1).strip()
        when = re.search(r'<div class="when-box"><b>✅ 什么情况下选它</b><br>(.*?)</div>',
                         seg, re.S).group(1).strip()
        avoid = re.search(r'<div class="avoid-box"><b>⛔ 什么时候别选它</b><br>(.*?)</div>',
                          seg, re.S).group(1).strip()
        pick = re.search(r'🎯 拿不准就先拿：<a href="games/online/([a-z0-9-]+)\.html"',
                         seg).group(1)
        ids = re.findall(r'<tr><td><a href="games/online/([a-z0-9-]+)\.html">', seg)
        assert len(ids) == n, '组 %s 表格 %d 款，标题写 %d 款' % (k, len(ids), n)
        short = title.split(' ', 1)[1] if ' ' in title else title
        groups.append(dict(key=k, title=title, short=short, n=n, lead=lead, when=when,
                           avoid=avoid, pick=pick, ids=ids))
    return groups


def js_str(s):
    return "'" + s.replace('\\', '\\\\').replace("'", "\\'") + "'"


def main():
    g = rd(GEN)

    if 'ONLINE_GROUPS' in g:
        print('generator.html 已含线上子类，跳过')
        return
    groups = parse_online_groups()
    all_ids = [gid for x in groups for gid in x['ids']]
    assert len(all_ids) == 8, '线上 4 组合计 %d 款 != 8' % len(all_ids)

    # 1) 新增「线上怎么玩」子类筛选行（放在破冰子类行之后，与「线上团建」目的相邻）
    anchor = '    <div class="form-group" id="collab-sub-form-group" style="display:none;">\n'
    i = g.index(anchor)
    online_block = (
        "    <div class=\"form-group\" id=\"online-sub-form-group\" style=\"display:none;\">\n"
        "      <label class=\"form-label\">💻 线上怎么玩（4 组子类）</label>\n"
        "      <div class=\"btn-group\" id=\"online-sub-group\">\n"
        + ''.join("        <button class=\"btn-option\" data-value=\"%s\" "
                  "onclick=\"selectOption(this, 'onlineSub')\">%s（%d）</button>\n"
                  % (x['key'], x['short'], x['n'])
                  for x in groups) +
        "        <button class=\"btn-option\" data-value=\"any\" onclick=\"selectOption(this, 'onlineSub')\">🎯 不限，线上全看</button>\n"
        "      </div>\n"
        "      <div class=\"form-hint\" id=\"online-sub-hint\">选「💻 线上团建」后可以在这里再收一层："
        "这 8 款按「远程这一局怎么玩」分 4 组</div>\n"
        "    </div>\n"
        "\n")
    g = g[:i] + online_block + g[i:]

    # 2) 目的说明补一句（线上团建目的会带出 8 款线上游戏）
    g = rep(g,
            "「综合训练」覆盖破冰 / 沟通 / 协作 / 信任 / 领导力；「线上团建」只推荐远程可玩的游戏",
            "「综合训练」覆盖破冰 / 沟通 / 协作 / 信任 / 领导力；"
            "「线上团建」只推荐远程可玩的 8 款，选具体那一组时只给该组",
            '目的说明')

    # 3) userSelections 增加 onlineSub
    g = rep(g,
            "var userSelections = {\n  people: '',\n  duration: '',\n  purpose: '',\n  collabSub: 'any',\n  ideaSub: 'any',\n  iceSub: 'any'\n};",
            "var userSelections = {\n  people: '',\n  duration: '',\n  purpose: '',\n  collabSub: 'any',\n  ideaSub: 'any',\n  iceSub: 'any',\n  onlineSub: 'any'\n};",
            'userSelections')

    # 4) lastOnlineFallback 声明
    g = rep(g,
            "// 最近一次生成是否因\"破冰子类 × 人数/时长\"无解而退回全部 8 款破冰游戏（null = 没退回）\nvar lastIceFallback = null;\n",
            "// 最近一次生成是否因\"破冰子类 × 人数/时长\"无解而退回全部 8 款破冰游戏（null = 没退回）\nvar lastIceFallback = null;\n\n"
            "// 最近一次生成是否因\"线上子类 × 人数/时长\"无解而退回全部 8 款线上游戏（null = 没退回）\nvar lastOnlineFallback = null;\n",
            'lastOnlineFallback 声明')

    # 5) ONLINE_GROUPS / ONLINE_SUB_OF / onlineGroup —— 文案全部照搬 online.html
    glines = ["// ============ 线上 4 组子类（2026-10-28 接入「拼游戏」模式）============\n",
              "// 与 online.html 的 4 个分组、index.html 的 data-online 完全同源：\n",
              "// 组名 / 组导语 / 何时选 / 何时别选 / 组内首选，全部照搬 online.html 现成文案，\n",
              "// 不在生成器里另写一份（否则两边会漂移）。由 site_check.py 第 32 项把关。\n",
              "var ONLINE_GROUPS = [\n"]
    for x in groups:
        glines.append(
            "  { key: %s, name: %s, short: %s, n: %d,\n"
            "    lead: %s,\n"
            "    when: %s,\n"
            "    avoid: %s,\n"
            "    pick: %s,\n"
            "    ids: [%s] },\n"
            % (js_str(x['key']), js_str(x['title']), js_str(x['short']),
               x['n'], js_str(x['lead']), js_str(x['when']), js_str(x['avoid']),
               js_str(x['pick']), ', '.join(js_str(i) for i in x['ids'])))
    glines.append("];\n\n")
    glines.append("var ONLINE_SUB_OF = {};\n")
    glines.append("ONLINE_GROUPS.forEach(function(g) {\n")
    glines.append("  g.ids.forEach(function(id) { ONLINE_SUB_OF[id] = g.key; });\n")
    glines.append("});\n\n")
    # 线上 8 款全集：回退时用它，而不是放宽到整个库
    glines.append("// 线上 8 款全集：子类无解时回退到这里，而不是放宽到整个游戏库\n")
    glines.append("var ONLINE_ALL_IDS = [%s];\n\n" % ', '.join(js_str(i) for i in all_ids))
    glines.append("function onlineGroup(key) {\n")
    glines.append("  return ONLINE_GROUPS.filter(function(g) { return g.key === key; })[0] || null;\n")
    glines.append("}\n\n")

    anchor = "var currentMode = 'flow';\n"
    g = rep(g, anchor, ''.join(glines) + anchor, 'ONLINE_GROUPS 插入点')

    # 6) refreshOnlineSub / renderOnlineSubHint
    g = rep(g,
            "// 提示文案全部取自 idea.html 现成表述，不另写一份（两边永远一致）\n",
            "// 「线上怎么玩」子类只在「拼游戏 + 目的=线上团建」时出现；切走时复位为「不限」\n"
            "function refreshOnlineSub() {\n"
            "  var box = document.getElementById('online-sub-form-group');\n"
            "  var on = (currentMode === 'game' && userSelections.purpose === 'online');\n"
            "  box.style.display = on ? '' : 'none';\n"
            "  if (!on) {\n"
            "    userSelections.onlineSub = 'any';\n"
            "    document.getElementById('online-sub-group').querySelectorAll('.btn-option').forEach(function(b) {\n"
            "      b.classList.remove('active');\n"
            "    });\n"
            "  }\n"
            "  renderOnlineSubHint();\n"
            "}\n\n"
            "// 提示文案全部取自 online.html 现成表述，不另写一份（两边永远一致）\n"
            "function renderOnlineSubHint() {\n"
            "  var el = document.getElementById('online-sub-hint');\n"
            "  var g = onlineGroup(userSelections.onlineSub);\n"
            "  if (!g) {\n"
            "    el.innerHTML = '选「💻 线上团建」后可以在这里再收一层：这 8 款按「远程这一局怎么玩」'\n"
            "      + '分 4 组。拿不准看 '\n"
            "      + '<a href=\"../online.html\">线上挑款指南</a>（4 组 + 每组首选 + 什么时候别选它）';\n"
            "    return;\n"
            "  }\n"
            "  var p = gamesDB.filter(function(x) { return x.id === g.pick; })[0];\n"
            "  el.innerHTML = '<b>' + g.name + '（' + g.n + ' 款）</b><br>' + g.lead +\n"
            "    '<br>✅ <b>什么情况下选它</b>：' + g.when +\n"
            "    '<br>⛔ <b>什么时候别选它</b>：' + g.avoid +\n"
            "    '<br>🎯 <b>拿不准就先拿</b>：' + (p ? '<a href=\"' + gameUrl(p) + '\" target=\"_blank\">' + p.name + '</a>' : '') +\n"
            "    '（<a href=\"../online.html#g-' + g.key + '\">看这一组全部 ' + g.n + ' 款</a>）';\n"
            "}\n\n"
            "// 提示文案全部取自 idea.html 现成表述，不另写一份（两边永远一致）\n",
            'refreshOnlineSub 插入点')

    # 7) selectMode / selectOption 联动
    g = rep(g,
            "  document.getElementById('result-section').classList.remove('show');\n  refreshCollabSub();\n  refreshIdeaSub();\n  refreshIceSub();\n}",
            "  document.getElementById('result-section').classList.remove('show');\n"
            "  refreshCollabSub();\n  refreshIdeaSub();\n  refreshIceSub();\n  refreshOnlineSub();\n}",
            'selectMode 联动')

    g = rep(g,
            "  // 目的变了要重算协作子类的显隐与提示（切走协作时复位，避免带着上次的条件）\n"
            "  if (type === 'purpose') { refreshCollabSub(); refreshIdeaSub(); refreshIceSub(); }\n"
            "  if (type === 'collabSub') renderCollabSubHint();\n"
            "  if (type === 'ideaSub') renderIdeaSubHint();\n"
            "  if (type === 'iceSub') renderIceSubHint();\n",
            "  // 目的变了要重算协作子类的显隐与提示（切走协作时复位，避免带着上次的条件）\n"
            "  if (type === 'purpose') { refreshCollabSub(); refreshIdeaSub(); refreshIceSub(); refreshOnlineSub(); }\n"
            "  if (type === 'collabSub') renderCollabSubHint();\n"
            "  if (type === 'ideaSub') renderIdeaSubHint();\n"
            "  if (type === 'iceSub') renderIceSubHint();\n"
            "  if (type === 'onlineSub') renderOnlineSubHint();\n",
            'selectOption 联动')

    # 8) recommendGames：子类过滤 + 回退
    g = rep(g,
            "  var buildFilter = function(subKey, ideaKey, iceKey) {\n"
            "    return gamesDB.filter(function(game) {\n"
            "      var matchPeople = game.people.includes(people) || (people === 'xlarge' && game.people.includes('large'));\n"
            "      var matchCategory = categoryFilter.includes(game.category);\n"
            "      var matchScene = wantOnline ? game.online === true : game.online !== true;\n"
            "      var matchSub = !subKey || COLLAB_SUB_OF[game.id] === subKey;\n"
            "      var matchIdea = !ideaKey || IDEA_SUB_OF[game.id] === ideaKey;\n"
            "      // iceKey === 'iceAll' 表示「全部 8 款破冰」（回退用），不是某一组\n"
            "      var matchIce = !iceKey || (iceKey === 'iceAll'\n"
            "        ? ICE_ALL_IDS.indexOf(game.id) >= 0\n"
            "        : ICE_SUB_OF[game.id] === iceKey);\n"
            "      return matchPeople && matchCategory && matchScene && matchSub && matchIdea && matchIce;\n"
            "    });\n"
            "  };\n",
            "  // 「线上怎么玩」子类：只在目的＝线上团建且用户选了具体某一组时生效\n"
            "  var onlineSub = (purpose === 'online' && userSelections.onlineSub &&\n"
            "             userSelections.onlineSub !== 'any') ? userSelections.onlineSub : null;\n"
            "  var buildFilter = function(subKey, ideaKey, iceKey, onlineKey) {\n"
            "    return gamesDB.filter(function(game) {\n"
            "      var matchPeople = game.people.includes(people) || (people === 'xlarge' && game.people.includes('large'));\n"
            "      var matchCategory = categoryFilter.includes(game.category);\n"
            "      var matchScene = wantOnline ? game.online === true : game.online !== true;\n"
            "      var matchSub = !subKey || COLLAB_SUB_OF[game.id] === subKey;\n"
            "      var matchIdea = !ideaKey || IDEA_SUB_OF[game.id] === ideaKey;\n"
            "      // iceKey === 'iceAll' 表示「全部 8 款破冰」（回退用），不是某一组\n"
            "      var matchIce = !iceKey || (iceKey === 'iceAll'\n"
            "        ? ICE_ALL_IDS.indexOf(game.id) >= 0\n"
            "        : ICE_SUB_OF[game.id] === iceKey);\n"
            "      // onlineKey === 'onlineAll' 表示「全部 8 款线上」（回退用），不是某一组\n"
            "      var matchOnline = !onlineKey || (onlineKey === 'onlineAll'\n"
            "        ? ONLINE_ALL_IDS.indexOf(game.id) >= 0\n"
            "        : ONLINE_SUB_OF[game.id] === onlineKey);\n"
            "      return matchPeople && matchCategory && matchScene && matchSub && matchIdea && matchIce && matchOnline;\n"
            "    });\n"
            "  };\n",
            'buildFilter（加 online 子类）')

    g = rep(g,
            "  var filtered = buildFilter(sub, ideaSub, iceSub);\n"
            "  // 子类 + 人数/时长 装不出结果时，退回整个协作类，并明说是退回来的（不要静默换口径）\n"
            "  lastSubFallback = null;\n"
            "  lastIdeaFallback = null;\n"
            "  lastIceFallback = null;\n"
            "  if (filtered.length === 0 && sub) {\n"
            "    lastSubFallback = sub;\n"
            "    sub = null;\n"
            "    filtered = buildFilter(null, ideaSub, iceSub);\n"
            "  }\n"
            "  if (filtered.length === 0 && ideaSub) {\n"
            "    lastIdeaFallback = ideaSub;\n"
            "    ideaSub = null;\n"
            "    filtered = buildFilter(sub, null, iceSub);\n"
            "  }\n"
            "  if (filtered.length === 0 && iceSub) {\n"
            "    // 回退落在「全部 8 款破冰」而不是整个破冰热场目的（含沟通 8 款）——\n"
            "    // 用户既然选了「破冰要什么」，放宽也该留在破冰这一类里\n"
            "    lastIceFallback = iceSub;\n"
            "    iceSub = null;\n"
            "    filtered = buildFilter(sub, null, 'iceAll');\n"
            "  }\n",
            "  var filtered = buildFilter(sub, ideaSub, iceSub, onlineSub);\n"
            "  // 子类 + 人数/时长 装不出结果时，退回整个协作类，并明说是退回来的（不要静默换口径）\n"
            "  lastSubFallback = null;\n"
            "  lastIdeaFallback = null;\n"
            "  lastIceFallback = null;\n"
            "  lastOnlineFallback = null;\n"
            "  if (filtered.length === 0 && sub) {\n"
            "    lastSubFallback = sub;\n"
            "    sub = null;\n"
            "    filtered = buildFilter(null, ideaSub, iceSub, onlineSub);\n"
            "  }\n"
            "  if (filtered.length === 0 && ideaSub) {\n"
            "    lastIdeaFallback = ideaSub;\n"
            "    ideaSub = null;\n"
            "    filtered = buildFilter(sub, null, iceSub, onlineSub);\n"
            "  }\n"
            "  if (filtered.length === 0 && iceSub) {\n"
            "    // 回退落在「全部 8 款破冰」而不是整个破冰热场目的（含沟通 8 款）——\n"
            "    // 用户既然选了「破冰要什么」，放宽也该留在破冰这一类里\n"
            "    lastIceFallback = iceSub;\n"
            "    iceSub = null;\n"
            "    filtered = buildFilter(sub, null, 'iceAll', onlineSub);\n"
            "  }\n"
            "  if (filtered.length === 0 && onlineSub) {\n"
            "    // 回退落在「全部 8 款线上游戏」而不是整个游戏库 ——\n"
            "    // 用户既然选了「线上怎么玩」，放宽也该留在线上这一类里\n"
            "    lastOnlineFallback = onlineSub;\n"
            "    onlineSub = null;\n"
            "    filtered = buildFilter(sub, null, null, 'onlineAll');\n"
            "  }\n",
            'recommendGames 回退')

    # 9) 结果区：回退提示 + 卡片上的子类胶囊
    g = rep(g,
            "  if (games.length === 0) {\n",
            "  // 线上子类 × 人数/时长 无解时，明说「已经把子类条件放掉了」\n"
            "  if (lastOnlineFallback) {\n"
            "    var ofb = onlineGroup(lastOnlineFallback);\n"
            "    html += '<div class=\"notice\">「' + (ofb ? ofb.name : lastOnlineFallback) + '」这一组在「' +\n"
            "      PEOPLE_LABEL[userSelections.people] + ' / ' + DURATION_LABEL[userSelections.duration] +\n"
            "      '」下没有能玩完的一款——已<strong>自动放宽到全部 8 款线上游戏</strong>，下面是放宽后的结果。' +\n"
            "      '想守住这一组，可以放宽人数或时长再生成一次；也可以去 <a href=\"../online.html#g-' + lastOnlineFallback +\n"
            "      '\" target=\"_blank\">挑款页看这一组的真实人数与时长</a>。</div>';\n"
            "  }\n\n"
            "  if (games.length === 0) {\n",
            '结果区回退提示')

    g = rep(g,
            "      var ikeyk = ICE_SUB_OF[game.id];\n"
            "      if (ikeyk) {\n"
            "        var ig2 = iceGroup(ikeyk);\n"
            "        html += '<span class=\"game-tag\"><a href=\"../ice.html#g-' + ikeyk + '\" target=\"_blank\" style=\"color:inherit;text-decoration:none;\">' + (ig2 ? ig2.short : ikeyk) + '</a></span>';\n"
            "      }\n",
            "      var ikeyk = ICE_SUB_OF[game.id];\n"
            "      if (ikeyk) {\n"
            "        var ig2 = iceGroup(ikeyk);\n"
            "        html += '<span class=\"game-tag\"><a href=\"../ice.html#g-' + ikeyk + '\" target=\"_blank\" style=\"color:inherit;text-decoration:none;\">' + (ig2 ? ig2.short : ikeyk) + '</a></span>';\n"
            "      }\n"
            "      var onlkey = ONLINE_SUB_OF[game.id];\n"
            "      if (onlkey) {\n"
            "        var og = onlineGroup(onlkey);\n"
            "        html += '<span class=\"game-tag\"><a href=\"../online.html#g-' + onlkey + '\" target=\"_blank\" style=\"color:inherit;text-decoration:none;\">' + (og ? og.short : onlkey) + '</a></span>';\n"
            "      }\n",
            '卡片子类胶囊')

    # 10) URL 参数 ?online=
    g = rep(g,
            "  // 破冰子类：同样排在 purpose 之后\n"
            "  var ice = params.get('ice');\n"
            "  if (ice) {\n"
            "    var icebtn = document.querySelector('#ice-sub-group .btn-option[data-value=\"' + ice + '\"]');\n"
            "    if (icebtn) selectOption(icebtn, 'iceSub');\n"
            "  }\n",
            "  // 破冰子类：同样排在 purpose 之后\n"
            "  var ice = params.get('ice');\n"
            "  if (ice) {\n"
            "    var icebtn = document.querySelector('#ice-sub-group .btn-option[data-value=\"' + ice + '\"]');\n"
            "    if (icebtn) selectOption(icebtn, 'iceSub');\n"
            "  }\n"
            "  // 线上子类：同样排在 purpose 之后\n"
            "  var online = params.get('online');\n"
            "  if (online) {\n"
            "    var onlbtn = document.querySelector('#online-sub-group .btn-option[data-value=\"' + online + '\"]');\n"
            "    if (onlbtn) selectOption(onlbtn, 'onlineSub');\n"
            "  }\n",
            'URL 参数 online')

    # 11) 页脚：加挑款指南入口
    g = rep(g,
            "  <p style=\"margin-top:6px;\">团建 &amp; 培训游戏库 · <a href=\"https://github.com/aiworkdb/aiworkdb.github.io\">GitHub 仓库</a></p>\n",
            "  <p style=\"margin-top:6px;\">只想要远程能开的游戏？「🎲 拼一组单个游戏」选「💻 线上团建」后会再出一层 4 组子类筛选"
            "（不用专用工具 / 要一块共享屏 / 要一份文档承载 / 不用同时在线）；拿不准时看 "
            "<a href=\"../online.html\">线上挑款指南</a>（每组首选 + 什么时候别选它）</p>\n"
            "  <p style=\"margin-top:6px;\">团建 &amp; 培训游戏库 · <a href=\"https://github.com/aiworkdb/aiworkdb.github.io\">GitHub 仓库</a></p>\n",
            '页脚入口')

    wr(GEN, g)
    print('generator.html 已更新：线上团建目的下新增 4 组「线上怎么玩」子类（%s）'
          % ', '.join('%s=%d' % (x['key'], x['n']) for x in groups))


if __name__ == '__main__':
    main()
