# -*- coding: utf-8 -*-
"""给 toolbox/generator.html 接入「创意与解题」的 4 组子类（2026-10-26 自动化第四十次）。

背景：
    生成器是全站唯一「按处境一次出一组」的入口。此前它只有协作 6 组子类，
    而 💡创新思维 / 🔧问题解决 这 10 款既没有独立入口，也没法按组挑 ——
    选了「团队协作」时 39 款协作 + 10 款创意解题混在一起，教练还是挑不动。

做法（与 2026-10-25 的协作子类接入完全同构）：
  1) 目的按钮新增「💡 创意与解题」（purpose=idea），只筛这 10 款
  2) 新增「卡在哪一步」4 组子类筛选行，只在「拼游戏 + 目的=创意与解题」时出现
  3) 组名 / 组导语 / 何时选 / 何时别选 / 组内首选，全部照搬 idea.html 的原文，
     不在生成器里另写一份（否则两边必然漂移）
  4) 子类 × 人数/时长 无解时显式回退并说明，不静默换口径
  5) URL 参数 ?idea=<key> 可直接分享某一组

复用原则（经验 91）：文案一律取自 idea.html，本脚本生成后由 site_check 第 26 项
逐字比对，漂移即红。

用法：
    python teambuilding/build_idea_generator.py
幂等：已含 IDEA_GROUPS 时跳过。
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


def parse_idea_groups():
    """从 idea.html 抽 4 组的原文（组名 / 导语 / 何时选 / 何时别选 / 首选 / 成员）。"""
    t = rd(os.path.join(TB, 'idea.html'))
    keys = re.findall(r'<div class="group-card" id="g-([a-z]+)">', t)
    assert len(keys) == 4, 'idea.html 分组数 %d != 4' % len(keys)
    groups = []
    for k in keys:
        start = t.index('<div class="group-card" id="g-%s">' % k)
        nxt = [t.index('<div class="group-card" id="g-%s">' % x)
               for x in keys if t.index('<div class="group-card" id="g-%s">' % x) > start]
        end = min(nxt) if nxt else t.index('⚠️ 三个最容易挑错的地方')
        seg = t[start:end]
        h3 = re.search(r'<h3>(.*?)（(\d+) 款）</h3>', seg, re.S)
        title = h3.group(1).strip()
        n = int(h3.group(2))
        lead = re.search(r'<div class="group-lead">(.*?)</div>', seg, re.S).group(1).strip()
        when = re.search(r'<div class="when-box"><b>✅ 什么情况下选它</b><br>(.*?)</div>',
                         seg, re.S).group(1).strip()
        avoid = re.search(r'<div class="avoid-box"><b>⛔ 什么时候别选它</b><br>(.*?)</div>',
                          seg, re.S).group(1).strip()
        pick = re.search(r'🎯 拿不准就先拿：<a href="games/(?:creativity|problem-solving)/'
                         r'([a-z0-9-]+)\.html"', seg).group(1)
        ids = re.findall(r'<tr><td><a href="games/(?:creativity|problem-solving)/'
                         r'([a-z0-9-]+)\.html">', seg)
        assert len(ids) == n, '组 %s 表格 %d 款，标题写 %d 款' % (k, len(ids), n)
        # short：按钮与胶囊用的短名（去掉组名里的副标题）
        short = title.split(' · ')[0] if ' · ' in title else title
        groups.append(dict(key=k, title=title, short=short, n=n, lead=lead, when=when,
                           avoid=avoid, pick=pick, ids=ids))
    return groups


def js_str(s):
    """转义成 JS 单引号字符串字面量（含引号本身）。"""
    return "'" + s.replace('\\', '\\\\').replace("'", "\\'") + "'"


def main():
    g = rd(GEN)
    if 'IDEA_GROUPS' in g:
        print('generator.html 已含创意解题子类，跳过')
        return
    groups = parse_idea_groups()

    # 1) 目的按钮新增「💡 创意与解题」
    g = rep(g,
            "        <button class=\"btn-option\" data-value=\"collaboration\" onclick=\"selectOption(this, 'purpose')\">🤝 团队协作</button>\n",
            "        <button class=\"btn-option\" data-value=\"collaboration\" onclick=\"selectOption(this, 'purpose')\">🤝 团队协作</button>\n"
            "        <button class=\"btn-option\" data-value=\"idea\" onclick=\"selectOption(this, 'purpose')\">💡 创意与解题</button>\n",
            '目的按钮（加 创意与解题）')

    g = rep(g,
            "      <div class=\"form-hint\">「综合训练」覆盖破冰 / 沟通 / 协作 / 信任 / 领导力；「线上团建」只推荐远程可玩的游戏</div>\n",
            "      <div class=\"form-hint\">「创意与解题」只推荐💡创新思维 + 🔧问题解决这 10 款；"
            "「综合训练」覆盖破冰 / 沟通 / 协作 / 信任 / 领导力；「线上团建」只推荐远程可玩的游戏</div>\n",
            '目的说明')

    # 2) 新增「卡在哪一步」子类筛选行（放在协作子类行之后）
    collab_group_block = (
        "    <div class=\"form-group\" id=\"collab-sub-form-group\" style=\"display:none;\">\n")
    i = g.index(collab_group_block)
    # 找到协作子类整块（到下一个 </div> 之后的空行）
    j = g.index("    <div class=\"form-group\" id=\"scene-form-group\">", i)
    idea_block = (
        "    <div class=\"form-group\" id=\"idea-sub-form-group\" style=\"display:none;\">\n"
        "      <label class=\"form-label\">🔍 团队当下卡在哪一步（4 组子类）</label>\n"
        "      <div class=\"btn-group\" id=\"idea-sub-group\">\n"
        + ''.join("        <button class=\"btn-option\" data-value=\"%s\" "
                  "onclick=\"selectOption(this, 'ideaSub')\">%s（%d）</button>\n"
                  % (x['key'], x['short'], x['n'])
                  for x in groups) +
        "        <button class=\"btn-option\" data-value=\"any\" onclick=\"selectOption(this, 'ideaSub')\">🎯 不限，10 款都看</button>\n"
        "      </div>\n"
        "      <div class=\"form-hint\" id=\"idea-sub-hint\">选「💡 创意与解题」后可以在这里再收一层："
        "这 10 款横跨创新与解题两个分类，按「团队卡在哪一步」分 4 组</div>\n"
        "    </div>\n"
        "\n")
    g = g[:j] + idea_block + g[j:]

    # 3) userSelections 增加 ideaSub
    g = rep(g,
            "var userSelections = {\n  people: '',\n  duration: '',\n  purpose: '',\n  collabSub: 'any'\n};",
            "var userSelections = {\n  people: '',\n  duration: '',\n  purpose: '',\n  collabSub: 'any',\n  ideaSub: 'any'\n};",
            'userSelections')

    g = rep(g,
            "// 最近一次生成是否因\"协作子类 × 人数/时长\"无解而退回整个协作类（null = 没退回）\nvar lastSubFallback = null;\n",
            "// 最近一次生成是否因\"协作子类 × 人数/时长\"无解而退回整个协作类（null = 没退回）\nvar lastSubFallback = null;\n\n"
            "// 最近一次生成是否因\"创意解题子类 × 人数/时长\"无解而退回整个创意解题类（null = 没退回）\nvar lastIdeaFallback = null;\n",
            'lastIdeaFallback 声明')

    # 4) IDEA_GROUPS / IDEA_SUB_OF / ideaGroup —— 文案全部照搬 idea.html
    glines = ["// ============ 创意与解题 4 组子类（2026-10-26 接入「拼游戏」模式）============\n",
              "// 与 idea.html 的 4 个分组、index.html 的 data-idea 完全同源：\n",
              "// 组名 / 组导语 / 何时选 / 何时别选 / 组内首选，全部照搬 idea.html 现成文案，\n",
              "// 不在生成器里另写一份（否则两边会漂移）。由 site_check.py 第 26 项把关。\n",
              "var IDEA_GROUPS = [\n"]
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
    glines.append("var IDEA_SUB_OF = {};\n")
    glines.append("IDEA_GROUPS.forEach(function(g) {\n")
    glines.append("  g.ids.forEach(function(id) { IDEA_SUB_OF[id] = g.key; });\n")
    glines.append("});\n\n")
    glines.append("function ideaGroup(key) {\n")
    glines.append("  return IDEA_GROUPS.filter(function(g) { return g.key === key; })[0] || null;\n")
    glines.append("}\n\n")

    anchor = "var currentMode = 'flow';\n"
    g = rep(g, anchor, ''.join(glines) + anchor, 'IDEA_GROUPS 插入点')

    # 5) refreshIdeaSub / renderIdeaSubHint
    g = rep(g,
            "// 提示文案全部取自 collab.html 现成表述，不另写一份（两边永远一致）\n",
            "// 「卡在哪一步」子类只在「拼游戏 + 目的=创意与解题」时出现；切走时复位为「不限」\n"
            "function refreshIdeaSub() {\n"
            "  var box = document.getElementById('idea-sub-form-group');\n"
            "  var on = (currentMode === 'game' && userSelections.purpose === 'idea');\n"
            "  box.style.display = on ? '' : 'none';\n"
            "  if (!on) {\n"
            "    userSelections.ideaSub = 'any';\n"
            "    document.getElementById('idea-sub-group').querySelectorAll('.btn-option').forEach(function(b) {\n"
            "      b.classList.remove('active');\n"
            "    });\n"
            "  }\n"
            "  renderIdeaSubHint();\n"
            "}\n\n"
            "// 提示文案全部取自 idea.html 现成表述，不另写一份（两边永远一致）\n"
            "function renderIdeaSubHint() {\n"
            "  var el = document.getElementById('idea-sub-hint');\n"
            "  var g = ideaGroup(userSelections.ideaSub);\n"
            "  if (!g) {\n"
            "    el.innerHTML = '选「💡 创意与解题」后可以在这里再收一层：这 10 款横跨创新与解题两个分类，'\n"
            "      + '按「团队卡在哪一步」分 4 组。拿不准看 '\n"
            "      + '<a href=\"../idea.html\">创意与解题挑款指南</a>（4 组 + 每组首选 + 什么时候别选它）';\n"
            "    return;\n"
            "  }\n"
            "  var p = gamesDB.filter(function(x) { return x.id === g.pick; })[0];\n"
            "  el.innerHTML = '<b>' + g.name + '（' + g.n + ' 款）</b><br>' + g.lead +\n"
            "    '<br>✅ <b>什么情况下选它</b>：' + g.when +\n"
            "    '<br>⛔ <b>什么时候别选它</b>：' + g.avoid +\n"
            "    '<br>🎯 <b>拿不准就先拿</b>：' + (p ? '<a href=\"' + gameUrl(p) + '\" target=\"_blank\">' + p.name + '</a>' : '') +\n"
            "    '（<a href=\"../idea.html#g-' + g.key + '\">看这一组全部 ' + g.n + ' 款</a>）';\n"
            "}\n\n"
            "// 提示文案全部取自 collab.html 现成表述，不另写一份（两边永远一致）\n",
            'refreshIdeaSub 插入点')

    # 6) selectMode / selectOption 联动
    g = rep(g,
            "  document.getElementById('result-section').classList.remove('show');\n  refreshCollabSub();\n}",
            "  document.getElementById('result-section').classList.remove('show');\n"
            "  refreshCollabSub();\n  refreshIdeaSub();\n}",
            'selectMode 联动')

    g = rep(g,
            "  // 目的变了要重算协作子类的显隐与提示（切走协作时复位，避免带着上次的条件）\n"
            "  if (type === 'purpose') refreshCollabSub();\n"
            "  if (type === 'collabSub') renderCollabSubHint();\n",
            "  // 目的变了要重算协作子类的显隐与提示（切走协作时复位，避免带着上次的条件）\n"
            "  if (type === 'purpose') { refreshCollabSub(); refreshIdeaSub(); }\n"
            "  if (type === 'collabSub') renderCollabSubHint();\n"
            "  if (type === 'ideaSub') renderIdeaSubHint();\n",
            'selectOption 联动')

    # 7) recommendGames：新增 idea 目的 + 子类过滤 + 回退
    g = rep(g,
            "  } else if (purpose === 'trust') {\n    categoryFilter = ['trust', 'communication'];\n",
            "  } else if (purpose === 'idea') {\n    categoryFilter = ['creativity', 'problem-solving'];\n"
            "  } else if (purpose === 'trust') {\n    categoryFilter = ['trust', 'communication'];\n",
            'categoryFilter（加 idea）')

    g = rep(g,
            "  var buildFilter = function(subKey) {\n"
            "    return gamesDB.filter(function(game) {\n"
            "      var matchPeople = game.people.includes(people) || (people === 'xlarge' && game.people.includes('large'));\n"
            "      var matchCategory = categoryFilter.includes(game.category);\n"
            "      var matchScene = wantOnline ? game.online === true : game.online !== true;\n"
            "      var matchSub = !subKey || COLLAB_SUB_OF[game.id] === subKey;\n"
            "      return matchPeople && matchCategory && matchScene && matchSub;\n"
            "    });\n"
            "  };\n",
            "  // 「卡在哪一步」子类：只在目的＝创意与解题且用户选了具体某一组时生效\n"
            "  var ideaSub = (purpose === 'idea' && userSelections.ideaSub &&\n"
            "             userSelections.ideaSub !== 'any') ? userSelections.ideaSub : null;\n"
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
            'buildFilter（加 idea 子类）')

    g = rep(g,
            "  var filtered = buildFilter(sub);\n"
            "  // 子类 + 人数/时长 装不出结果时，退回整个协作类，并明说是退回来的（不要静默换口径）\n"
            "  lastSubFallback = null;\n"
            "  if (filtered.length === 0 && sub) {\n"
            "    lastSubFallback = sub;\n"
            "    sub = null;\n"
            "    filtered = buildFilter(null);\n"
            "  }\n",
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
            'recommendGames 回退')

    # 8) 结果区：回退提示 + 卡片上的子类胶囊
    g = rep(g,
            "  if (games.length === 0) {\n",
            "  // 创意解题子类 × 人数/时长 无解时，明说「已经把子类条件放掉了」\n"
            "  if (lastIdeaFallback) {\n"
            "    var ifb = ideaGroup(lastIdeaFallback);\n"
            "    html += '<div class=\"notice\">「' + (ifb ? ifb.name : lastIdeaFallback) + '」这一组在「' +\n"
            "      PEOPLE_LABEL[userSelections.people] + ' / ' + DURATION_LABEL[userSelections.duration] +\n"
            "      '」下没有能玩完的一款——已<strong>自动放宽到全部 10 款创意与解题游戏</strong>，下面是放宽后的结果。' +\n"
            "      '想守住这一组，可以放宽人数或时长再生成一次；也可以去 <a href=\"../idea.html#g-' + lastIdeaFallback +\n"
            "      '\" target=\"_blank\">挑款页看这一组的真实人数与时长</a>。</div>';\n"
            "  }\n\n"
            "  if (games.length === 0) {\n",
            '结果区回退提示')

    g = rep(g,
            "      var skey = COLLAB_SUB_OF[game.id];\n"
            "      if (skey) {\n"
            "        var sg = collabGroup(skey);\n"
            "        html += '<span class=\"game-tag\"><a href=\"../collab.html#g-' + skey + '\" target=\"_blank\" style=\"color:inherit;text-decoration:none;\">' + sg.short + '</a></span>';\n"
            "      }\n",
            "      var skey = COLLAB_SUB_OF[game.id];\n"
            "      if (skey) {\n"
            "        var sg = collabGroup(skey);\n"
            "        html += '<span class=\"game-tag\"><a href=\"../collab.html#g-' + skey + '\" target=\"_blank\" style=\"color:inherit;text-decoration:none;\">' + sg.short + '</a></span>';\n"
            "      }\n"
            "      var ikey = IDEA_SUB_OF[game.id];\n"
            "      if (ikey) {\n"
            "        var ig = ideaGroup(ikey);\n"
            "        html += '<span class=\"game-tag\"><a href=\"../idea.html#g-' + ikey + '\" target=\"_blank\" style=\"color:inherit;text-decoration:none;\">' + (ig ? ig.short : ikey) + '</a></span>';\n"
            "      }\n",
            '卡片子类胶囊')

    # 9) URL 参数 ?idea=
    g = rep(g,
            "  // 协作子类：必须排在 purpose 之后（purpose 变了会复位子类）\n"
            "  var sub = params.get('sub');\n"
            "  if (sub) {\n"
            "    var subbtn = document.querySelector('#collab-sub-group .btn-option[data-value=\"' + sub + '\"]');\n"
            "    if (subbtn) selectOption(subbtn, 'collabSub');\n"
            "  }\n",
            "  // 协作子类：必须排在 purpose 之后（purpose 变了会复位子类）\n"
            "  var sub = params.get('sub');\n"
            "  if (sub) {\n"
            "    var subbtn = document.querySelector('#collab-sub-group .btn-option[data-value=\"' + sub + '\"]');\n"
            "    if (subbtn) selectOption(subbtn, 'collabSub');\n"
            "  }\n"
            "  // 创意解题子类：同样排在 purpose 之后\n"
            "  var idea = params.get('idea');\n"
            "  if (idea) {\n"
            "    var ideabtn = document.querySelector('#idea-sub-group .btn-option[data-value=\"' + idea + '\"]');\n"
            "    if (ideabtn) selectOption(ideabtn, 'ideaSub');\n"
            "  }\n",
            'URL 参数 idea')

    # 10) 页脚：加挑款指南入口
    g = rep(g,
            "  <p style=\"margin-top:6px;\">团建 &amp; 培训游戏库 · <a href=\"https://github.com/aiworkdb/aiworkdb.github.io\">GitHub 仓库</a></p>\n",
            "  <p style=\"margin-top:6px;\">只想要创新或解题类？「🎲 拼一组单个游戏」选「💡 创意与解题」后会再出一层 4 组子类筛选"
            "（先定义问题 / 试错前先写赌注 / 限制下取舍 / 先留余地）；拿不准时看 "
            "<a href=\"../idea.html\">创意与解题挑款指南</a>（每组首选 + 什么时候别选它）</p>\n"
            "  <p style=\"margin-top:6px;\">团建 &amp; 培训游戏库 · <a href=\"https://github.com/aiworkdb/aiworkdb.github.io\">GitHub 仓库</a></p>\n",
            '页脚入口')

    wr(GEN, g)
    print('generator.html 已更新：新增「💡 创意与解题」目的 + 4 组「卡在哪一步」子类（%s）'
          % ', '.join('%s=%d' % (x['key'], x['n']) for x in groups))


if __name__ == '__main__':
    main()
