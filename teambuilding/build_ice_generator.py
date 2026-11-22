# -*- coding: utf-8 -*-
"""给 toolbox/generator.html 接入「破冰」的 4 组子类（2026-10-27 自动化第四十一次）。

背景：
    生成器是全站唯一「按处境一次出一组」的入口。此前它只有协作 6 组、创意解题 4 组
    两层子类，而 🧊破冰热场 这一目的既没有二层筛选，也无法按组挑 —— 选了「破冰热场」
    时 8 款破冰 + 8 款沟通混在一起出，教练还是挑不动。

做法（与 2026-10-25 协作子类、2026-10-26 创意解题子类完全同构）：
  1) 在既有的「🧊 破冰热场」目的下新增「破冰要什么」4 组子类筛选行
     （不新增目的按钮 —— 破冰热场本来就有，重复加会让两个入口口径打架）
  2) 组名 / 组导语 / 何时选 / 何时别选 / 组内首选，全部照搬 ice.html 的原文，
     不在生成器里另写一份（否则两边必然漂移）
  3) 子类 × 人数/时长 无解时显式回退并说明，不静默换口径；
     回退的目标是**全部 8 款破冰游戏**（而不是放宽到 16 款破冰+沟通）——
     用户既然选了「破冰要什么」，回退就该落在破冰这一类里
  4) URL 参数 ?ice=<key> 可直接分享某一组

复用原则（经验 91）：文案一律取自 ice.html，本脚本生成后由 site_check 第 29 项
逐字比对，漂移即红。

用法：
    python teambuilding/build_ice_generator.py
幂等：已含 ICE_GROUPS 时跳过。
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
    """统一成 '\\n' 读入；写回时统一转 CRLF。"""
    return io.open(p, encoding='utf-8').read()


def wr(p, s):
    s = s.replace('\r\n', '\n').replace('\n', '\r\n')
    io.open(p, 'w', encoding='utf-8', newline='').write(s)


def rep(text, old, new, what):
    assert text.count(old) == 1, '锚点不唯一(%d)或未命中: %s' % (text.count(old), what)
    return text.replace(old, new)


def parse_ice_groups():
    """从 ice.html 抽 4 组的原文（组名 / 导语 / 何时选 / 何时别选 / 首选 / 成员）。"""
    t = rd(os.path.join(TB, 'ice.html'))
    keys = re.findall(r'<div class="group-card" id="g-([a-z]+)">', t)
    assert len(keys) == 4, 'ice.html 分组数 %d != 4' % len(keys)
    # 尾部边界必须锚到带标签的 <h2>：纯文本「🧊 破冰不只是这 8 款」在前面
    # 的 blockquote 里也出现过，用 t.index 会命中那一处、把最后一组切成空段。
    tail = '<h2>🧊 破冰不只是这 8 款</h2>'
    assert t.count(tail) == 1, 'ice.html 尾部锚点命中 %d 次' % t.count(tail)
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
        pick = re.search(r'🎯 拿不准就先拿：<a href="games/icebreaker/([a-z0-9-]+)\.html"',
                         seg).group(1)
        ids = re.findall(r'<tr><td><a href="games/icebreaker/([a-z0-9-]+)\.html">', seg)
        assert len(ids) == n, '组 %s 表格 %d 款，标题写 %d 款' % (k, len(ids), n)
        # short：按钮与胶囊用的短名（组名里去掉图标前缀）
        short = title.split(' ', 1)[1] if ' ' in title else title
        groups.append(dict(key=k, title=title, short=short, n=n, lead=lead, when=when,
                           avoid=avoid, pick=pick, ids=ids))
    return groups


def js_str(s):
    """转义成 JS 单引号字符串字面量（含引号本身）。"""
    return "'" + s.replace('\\', '\\\\').replace("'", "\\'") + "'"


def main():
    g = rd(GEN)
    # 0) 顺带修掉 line-master 的时长与描述：md / README 是「30–50 min」且
    #    玩法是抽场景卡+角色卡+情绪卡的即兴表演，生成器里却写「20-30 min」
    #    和「用电影台词猜谜」（这款游戏根本没有猜谜环节）——两处都与实况不符。
    #    ⚠️ 判定锚在这一款游戏上：不能写 `'duration: 25' in g` 这种全局匹配，
    #    别的游戏也可能是 25，改过一处就会误判成「还没修过」。
    lm_old = ("  { id: 'line-master', name: '台词之王', category: 'icebreaker', categoryName: '破冰热场', "
              "people: ['medium'], duration: 25, durationLabel: '20-30 min', "
              "materials: ['电影台词卡片'], indoor: true, outdoor: false, "
              "desc: '用电影台词猜谜的聚会游戏改造，轻松破冰、笑声不断。', "
              "icon: '🎭', parallel: false, online: false },")
    if lm_old in g:
        g = rep(g, lm_old,
                "  { id: 'line-master', name: '台词之王', category: 'icebreaker', categoryName: '破冰热场', "
                "people: ['medium'], duration: 50, durationLabel: '30-50 min', "
                "materials: ['场景卡', '角色卡', '情绪卡'], indoor: true, outdoor: false, "
                "desc: '抽场景卡+角色卡+情绪卡即兴表演的聚会游戏改造，笑声不断、破冰够快。', "
                "icon: '🎭', parallel: false, online: false },",
                'line-master 时长与描述')
        print('generator.html: line-master 时长已改为 30–50 min，描述已改为「即兴表演」实况')

    if 'ICE_GROUPS' in g:
        print('generator.html 已含破冰子类，跳过')
        return
    groups = parse_ice_groups()
    all_ids = [gid for x in groups for gid in x['ids']]
    assert len(all_ids) == 8, '破冰 4 组合计 %d 款 != 8' % len(all_ids)

    # 1) 新增「破冰要什么」子类筛选行（放在协作子类行之前，与「破冰热场」目的相邻）
    collab_group_block = (
        "    <div class=\"form-group\" id=\"collab-sub-form-group\" style=\"display:none;\">\n")
    i = g.index(collab_group_block)
    ice_block = (
        "    <div class=\"form-group\" id=\"ice-sub-form-group\" style=\"display:none;\">\n"
        "      <label class=\"form-label\">🧊 破冰要什么（4 组子类）</label>\n"
        "      <div class=\"btn-group\" id=\"ice-sub-group\">\n"
        + ''.join("        <button class=\"btn-option\" data-value=\"%s\" "
                  "onclick=\"selectOption(this, 'iceSub')\">%s（%d）</button>\n"
                  % (x['key'], x['short'], x['n'])
                  for x in groups) +
        "        <button class=\"btn-option\" data-value=\"any\" onclick=\"selectOption(this, 'iceSub')\">🎯 不限，破冰全看</button>\n"
        "      </div>\n"
        "      <div class=\"form-hint\" id=\"ice-sub-hint\">选「🧊 破冰热场」后可以在这里再收一层："
        "这 8 款按「破冰之后，团队手里剩下什么」分 4 组</div>\n"
        "    </div>\n"
        "\n")
    g = g[:i] + ice_block + g[i:]

    # 2) 目的说明补一句（破冰热场目的会带出 8 款破冰 + 8 款沟通）
    g = rep(g,
            "      <div class=\"form-hint\">「创意与解题」只推荐💡创新思维 + 🔧问题解决这 10 款；",
            "      <div class=\"form-hint\">「破冰热场」会带出 8 款破冰 + 8 款沟通，选具体那一组时只给该组；"
            "「创意与解题」只推荐💡创新思维 + 🔧问题解决这 10 款；",
            '目的说明')

    # 3) userSelections 增加 iceSub
    g = rep(g,
            "var userSelections = {\n  people: '',\n  duration: '',\n  purpose: '',\n  collabSub: 'any',\n  ideaSub: 'any'\n};",
            "var userSelections = {\n  people: '',\n  duration: '',\n  purpose: '',\n  collabSub: 'any',\n  ideaSub: 'any',\n  iceSub: 'any'\n};",
            'userSelections')

    # 4) lastIceFallback 声明
    g = rep(g,
            "// 最近一次生成是否因\"创意解题子类 × 人数/时长\"无解而退回整个创意解题类（null = 没退回）\nvar lastIdeaFallback = null;\n",
            "// 最近一次生成是否因\"创意解题子类 × 人数/时长\"无解而退回整个创意解题类（null = 没退回）\nvar lastIdeaFallback = null;\n\n"
            "// 最近一次生成是否因\"破冰子类 × 人数/时长\"无解而退回全部 8 款破冰游戏（null = 没退回）\nvar lastIceFallback = null;\n",
            'lastIceFallback 声明')

    # 5) ICE_GROUPS / ICE_SUB_OF / iceGroup —— 文案全部照搬 ice.html
    glines = ["// ============ 破冰 4 组子类（2026-10-27 接入「拼游戏」模式）============\n",
              "// 与 ice.html 的 4 个分组、index.html 的 data-ice 完全同源：\n",
              "// 组名 / 组导语 / 何时选 / 何时别选 / 组内首选，全部照搬 ice.html 现成文案，\n",
              "// 不在生成器里另写一份（否则两边会漂移）。由 site_check.py 第 29 项把关。\n",
              "var ICE_GROUPS = [\n"]
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
    glines.append("var ICE_SUB_OF = {};\n")
    glines.append("ICE_GROUPS.forEach(function(g) {\n")
    glines.append("  g.ids.forEach(function(id) { ICE_SUB_OF[id] = g.key; });\n")
    glines.append("});\n\n")
    # 破冰 8 款全集：回退时用它，而不是放宽到 16 款（破冰 + 沟通）
    glines.append("// 破冰 8 款全集：子类无解时回退到这里，而不是放宽到整个「破冰热场」目的（含沟通 8 款）\n")
    glines.append("var ICE_ALL_IDS = [%s];\n\n" % ', '.join(js_str(i) for i in all_ids))
    glines.append("function iceGroup(key) {\n")
    glines.append("  return ICE_GROUPS.filter(function(g) { return g.key === key; })[0] || null;\n")
    glines.append("}\n\n")

    anchor = "var currentMode = 'flow';\n"
    g = rep(g, anchor, ''.join(glines) + anchor, 'ICE_GROUPS 插入点')

    # 6) refreshIceSub / renderIceSubHint
    g = rep(g,
            "// 提示文案全部取自 idea.html 现成表述，不另写一份（两边永远一致）\n",
            "// 「破冰要什么」子类只在「拼游戏 + 目的=破冰热场」时出现；切走时复位为「不限」\n"
            "function refreshIceSub() {\n"
            "  var box = document.getElementById('ice-sub-form-group');\n"
            "  var on = (currentMode === 'game' && userSelections.purpose === 'icebreaker');\n"
            "  box.style.display = on ? '' : 'none';\n"
            "  if (!on) {\n"
            "    userSelections.iceSub = 'any';\n"
            "    document.getElementById('ice-sub-group').querySelectorAll('.btn-option').forEach(function(b) {\n"
            "      b.classList.remove('active');\n"
            "    });\n"
            "  }\n"
            "  renderIceSubHint();\n"
            "}\n\n"
            "// 提示文案全部取自 ice.html 现成表述，不另写一份（两边永远一致）\n"
            "function renderIceSubHint() {\n"
            "  var el = document.getElementById('ice-sub-hint');\n"
            "  var g = iceGroup(userSelections.iceSub);\n"
            "  if (!g) {\n"
            "    el.innerHTML = '选「🧊 破冰热场」后可以在这里再收一层：这 8 款按「破冰之后，团队手里剩下什么」'\n"
            "      + '分 4 组。拿不准看 '\n"
            "      + '<a href=\"../ice.html\">破冰挑款指南</a>（4 组 + 每组首选 + 什么时候别选它）';\n"
            "    return;\n"
            "  }\n"
            "  var p = gamesDB.filter(function(x) { return x.id === g.pick; })[0];\n"
            "  el.innerHTML = '<b>' + g.name + '（' + g.n + ' 款）</b><br>' + g.lead +\n"
            "    '<br>✅ <b>什么情况下选它</b>：' + g.when +\n"
            "    '<br>⛔ <b>什么时候别选它</b>：' + g.avoid +\n"
            "    '<br>🎯 <b>拿不准就先拿</b>：' + (p ? '<a href=\"' + gameUrl(p) + '\" target=\"_blank\">' + p.name + '</a>' : '') +\n"
            "    '（<a href=\"../ice.html#g-' + g.key + '\">看这一组全部 ' + g.n + ' 款</a>）';\n"
            "}\n\n"
            "// 提示文案全部取自 idea.html 现成表述，不另写一份（两边永远一致）\n",
            'refreshIceSub 插入点')

    # 7) selectMode / selectOption 联动
    g = rep(g,
            "  document.getElementById('result-section').classList.remove('show');\n  refreshCollabSub();\n  refreshIdeaSub();\n}",
            "  document.getElementById('result-section').classList.remove('show');\n"
            "  refreshCollabSub();\n  refreshIdeaSub();\n  refreshIceSub();\n}",
            'selectMode 联动')

    g = rep(g,
            "  // 目的变了要重算协作子类的显隐与提示（切走协作时复位，避免带着上次的条件）\n"
            "  if (type === 'purpose') { refreshCollabSub(); refreshIdeaSub(); }\n"
            "  if (type === 'collabSub') renderCollabSubHint();\n"
            "  if (type === 'ideaSub') renderIdeaSubHint();\n",
            "  // 目的变了要重算协作子类的显隐与提示（切走协作时复位，避免带着上次的条件）\n"
            "  if (type === 'purpose') { refreshCollabSub(); refreshIdeaSub(); refreshIceSub(); }\n"
            "  if (type === 'collabSub') renderCollabSubHint();\n"
            "  if (type === 'ideaSub') renderIdeaSubHint();\n"
            "  if (type === 'iceSub') renderIceSubHint();\n",
            'selectOption 联动')

    # 8) recommendGames：子类过滤 + 回退
    g = rep(g,
            "  var buildFilter = function(subKey, ideaKey) {\n"
            "    return gamesDB.filter(function(game) {\n"
            "      var matchPeople = game.people.includes(people) || (people === 'xlarge' && game.people.includes('large'));\n"
            "      var matchCategory = categoryFilter.includes(game.category);\n"
            "      var matchScene = wantOnline ? game.online === true : game.online !== true;\n"
            "      var matchSub = !subKey || COLLAB_SUB_OF[game.id] === subKey;\n"
            "      var matchIdea = !ideaKey || IDEA_SUB_OF[game.id] === ideaKey;\n"
            "      return matchPeople && matchCategory && matchScene && matchSub && matchIdea;\n"
            "    });\n"
            "  };\n",
            "  // 「破冰要什么」子类：只在目的＝破冰热场且用户选了具体某一组时生效\n"
            "  var iceSub = (purpose === 'icebreaker' && userSelections.iceSub &&\n"
            "             userSelections.iceSub !== 'any') ? userSelections.iceSub : null;\n"
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
            'buildFilter（加 ice 子类）')

    g = rep(g,
            "  var filtered = buildFilter(sub, ideaSub);\n"
            "  // 子类 + 人数/时长 装不出结果时，退回整个协作类，并明说是退回来的（不要静默换口径）\n"
            "  lastSubFallback = null;\n"
            "  lastIdeaFallback = null;\n"
            "  if (filtered.length === 0 && sub) {\n"
            "    lastSubFallback = sub;\n"
            "    sub = null;\n"
            "    filtered = buildFilter(null, ideaSub);\n"
            "  }\n"
            "  if (filtered.length === 0 && ideaSub) {\n"
            "    lastIdeaFallback = ideaSub;\n"
            "    ideaSub = null;\n"
            "    filtered = buildFilter(sub, null);\n"
            "  }\n",
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
            'recommendGames 回退')

    # 9) 结果区：回退提示 + 卡片上的子类胶囊
    g = rep(g,
            "  if (games.length === 0) {\n",
            "  // 破冰子类 × 人数/时长 无解时，明说「已经把子类条件放掉了」\n"
            "  if (lastIceFallback) {\n"
            "    var ifb2 = iceGroup(lastIceFallback);\n"
            "    html += '<div class=\"notice\">「' + (ifb2 ? ifb2.name : lastIceFallback) + '」这一组在「' +\n"
            "      PEOPLE_LABEL[userSelections.people] + ' / ' + DURATION_LABEL[userSelections.duration] +\n"
            "      '」下没有能玩完的一款——已<strong>自动放宽到全部 8 款破冰游戏</strong>，下面是放宽后的结果。' +\n"
            "      '想守住这一组，可以放宽人数或时长再生成一次；也可以去 <a href=\"../ice.html#g-' + lastIceFallback +\n"
            "      '\" target=\"_blank\">挑款页看这一组的真实人数与时长</a>。</div>';\n"
            "  }\n\n"
            "  if (games.length === 0) {\n",
            '结果区回退提示')

    g = rep(g,
            "      var ikey = IDEA_SUB_OF[game.id];\n"
            "      if (ikey) {\n"
            "        var ig = ideaGroup(ikey);\n"
            "        html += '<span class=\"game-tag\"><a href=\"../idea.html#g-' + ikey + '\" target=\"_blank\" style=\"color:inherit;text-decoration:none;\">' + (ig ? ig.short : ikey) + '</a></span>';\n"
            "      }\n",
            "      var ikey = IDEA_SUB_OF[game.id];\n"
            "      if (ikey) {\n"
            "        var ig = ideaGroup(ikey);\n"
            "        html += '<span class=\"game-tag\"><a href=\"../idea.html#g-' + ikey + '\" target=\"_blank\" style=\"color:inherit;text-decoration:none;\">' + (ig ? ig.short : ikey) + '</a></span>';\n"
            "      }\n"
            "      var ikeyk = ICE_SUB_OF[game.id];\n"
            "      if (ikeyk) {\n"
            "        var ig2 = iceGroup(ikeyk);\n"
            "        html += '<span class=\"game-tag\"><a href=\"../ice.html#g-' + ikeyk + '\" target=\"_blank\" style=\"color:inherit;text-decoration:none;\">' + (ig2 ? ig2.short : ikeyk) + '</a></span>';\n"
            "      }\n",
            '卡片子类胶囊')

    # 10) URL 参数 ?ice=
    g = rep(g,
            "  // 创意解题子类：同样排在 purpose 之后\n"
            "  var idea = params.get('idea');\n"
            "  if (idea) {\n"
            "    var ideabtn = document.querySelector('#idea-sub-group .btn-option[data-value=\"' + idea + '\"]');\n"
            "    if (ideabtn) selectOption(ideabtn, 'ideaSub');\n"
            "  }\n",
            "  // 创意解题子类：同样排在 purpose 之后\n"
            "  var idea = params.get('idea');\n"
            "  if (idea) {\n"
            "    var ideabtn = document.querySelector('#idea-sub-group .btn-option[data-value=\"' + idea + '\"]');\n"
            "    if (ideabtn) selectOption(ideabtn, 'ideaSub');\n"
            "  }\n"
            "  // 破冰子类：同样排在 purpose 之后\n"
            "  var ice = params.get('ice');\n"
            "  if (ice) {\n"
            "    var icebtn = document.querySelector('#ice-sub-group .btn-option[data-value=\"' + ice + '\"]');\n"
            "    if (icebtn) selectOption(icebtn, 'iceSub');\n"
            "  }\n",
            'URL 参数 ice')

    # 11) 页脚：加挑款指南入口
    g = rep(g,
            "  <p style=\"margin-top:6px;\">团建 &amp; 培训游戏库 · <a href=\"https://github.com/aiworkdb/aiworkdb.github.io\">GitHub 仓库</a></p>\n",
            "  <p style=\"margin-top:6px;\">只想要开场破冰？「🎲 拼一组单个游戏」选「🧊 破冰热场」后会再出一层 4 组子类筛选"
            "（只认名字 / 只图热闹 / 谈自己的事 / 带协作）；拿不准时看 "
            "<a href=\"../ice.html\">破冰挑款指南</a>（每组首选 + 什么时候别选它）</p>\n"
            "  <p style=\"margin-top:6px;\">团建 &amp; 培训游戏库 · <a href=\"https://github.com/aiworkdb/aiworkdb.github.io\">GitHub 仓库</a></p>\n",
            '页脚入口')

    wr(GEN, g)
    print('generator.html 已更新：破冰热场目的下新增 4 组「破冰要什么」子类（%s）'
          % ', '.join('%s=%d' % (x['key'], x['n']) for x in groups))


if __name__ == '__main__':
    main()
