# -*- coding: utf-8 -*-
"""site_check.py 的第 42 项：挑款总入口 pick.html（七套切法对照）。

单独成模块，由 site_check.py 在 main() 里 import 调用。

  [42] 挑款总入口：7 个挑款页 × 7 套切法
       - pick.html 里 7 张卡（id="p-<slug>"）与 7 个挑款页一一对应，一张不多一张不少
       - 每张卡申报的「N 款 / M 组」必须与**磁盘真相**一致（分类目录款数 / 该页 group-card 数）
       - 每张卡的组名胶囊必须覆盖该页**全部**分组锚点（少一个就点不进那一组）
       - 每张卡必须写出该页的「边界澄清」大标题（源页有 🔀/🚧 那一节时）
       - 7 个分类加起来 == 全库 85 款，且每页在自己分类里**逐款覆盖**（不靠 pick.html 自证）
       - 每组切法的「维度」名互不相同（7 个维度）
       - 7 个挑款页 + index.html + README 都必须指回 pick.html（否则入口是单向的）
       - 「破冰 11 款 = 本页 5 款带标签 + 6 款在别处」三处口径一致（pick / ice / README）

固化原因与前几项同型：**新增游戏不会自动进总表，改了挑款页的分组大纲也会让总表悄悄过期**。
而且总表是全站唯一一张「七套切法横向对照」的地方 —— 它一旦漂移，教练会按错维度挑游戏，
比单个页面写错更难发现（页面错只影响一款，总表错影响整套口径）。
"""
import io
import os
import re

PICK = 'pick.html'

# (挑款页, 分类目录, 该页切的维度)
PAGES = [
    ('collab.html', ['collaboration'], '动作'),
    ('idea.html', ['creativity', 'problem-solving'], '思考位置'),
    ('comm.html', ['communication'], '通道'),
    ('ice.html', ['icebreaker'], '存量'),
    ('online.html', ['online'], '成立条件'),
    ('lead.html', ['leadership'], '权力层级'),
    ('trust.html', ['trust'], '托付内容'),
]


def _read(p):
    return io.open(p, encoding='utf-8', newline='').read()


def _groups(t):
    """[(key, name, n)] —— 挑款页里的分组（h3 带「（n 款）」）。"""
    return re.findall(r'<div class="group-card" id="g-([a-z]+)">\s*<h3>(.*?)（(\d+) 款）</h3>', t)


def _card(t, slug):
    m = re.search(r'<div class="group-card" id="p-%s">(.*?)\n        </div>' % slug, t, re.S)
    return m.group(1) if m else None


def _confusion(t):
    """源页的边界澄清大标题（去掉前导 emoji）。"""
    for m in re.finditer(r'<h2>([^<]*(?:不等于|不是两个抽屉)[^<]*)</h2>', t):
        return re.sub(r'^[\U0001F300-\U0001FAFF\u2190-\u21FF\u2600-\u27BF\s]+', '',
                      m.group(1).strip())
    return ''


def _disk_games(TB, cats):
    ids = set()
    for c in cats:
        d = os.path.join(TB, 'games', c)
        for f in os.listdir(d):
            if f.endswith('.md'):
                ids.add('%s/%s' % (c, f[:-3]))
    return ids


def _linked_games(TB, page_text, cats):
    """该页**自己分类下**被链接到的游戏（用来断言「逐款覆盖」，不依赖 pick.html）。"""
    ids = set()
    for c in cats:
        for gid in re.findall(r'games/%s/([a-z0-9-]+)\.html' % re.escape(c), page_text):
            ids.add('%s/%s' % (c, gid))
    return ids


def check_pick_index(errors, TB):
    p = os.path.join(TB, PICK)
    if not os.path.exists(p):
        errors.append('缺挑款总入口：%s' % PICK)
        print('[42] 挑款总入口：文件缺失；异常 1 项')
        return 1

    pick = _read(p)
    idx = _read(os.path.join(TB, 'index.html'))
    rm = _read(os.path.join(TB, 'README.md'))
    bad = 0

    # 1) 7 张卡与 7 个挑款页一一对应
    slugs = re.findall(r'<div class="group-card" id="p-([a-z]+)">', pick)
    want = [f[:-5] for f, _, _ in PAGES]
    if slugs != want:
        errors.append('pick.html 卡片 %s 与 7 个挑款页 %s 不对应（或顺序变了）'
                      % (slugs, want))
        bad += 1

    # 2) 每张卡：申报数字 == 磁盘真相；胶囊覆盖全部分组；边界澄清在场
    all_games = set()
    sum_games = sum_groups = 0
    dims = []
    for fname, cats, dim in PAGES:
        slug = fname[:-5]
        fp = os.path.join(TB, fname)
        if not os.path.exists(fp):
            errors.append('挑款页缺失：%s' % fname)
            bad += 1
            continue
        page = _read(fp)
        groups = _groups(page)
        keys = [k for k, _, _ in groups]
        disk = _disk_games(TB, cats)
        linked = _linked_games(TB, page, cats)
        all_games |= disk
        sum_games += len(disk)
        sum_groups += len(groups)
        dims.append(dim)

        # 2a) 挑款页自己必须逐款覆盖本分类（这条不依赖 pick.html）
        if linked != disk:
            errors.append('%s 未逐款覆盖本分类：缺 %s 多 %s'
                          % (fname, sorted(disk - linked)[:4], sorted(linked - disk)[:4]))
            bad += 1

        card = _card(pick, slug)
        if card is None:
            errors.append('pick.html 缺 %s 的卡片（id="p-%s"）' % (fname, slug))
            bad += 1
            continue
        m = re.search(r'<h3>.*?（(\d+) 款 / (\d+) 组 · 切「(.+?)」）</h3>', card)
        if not m:
            errors.append('pick.html %s 卡片缺「N 款 / M 组 · 切「维度」」标题' % fname)
            bad += 1
        else:
            if int(m.group(1)) != len(disk):
                errors.append('pick.html 写 %s 有 %s 款，磁盘 %d 款'
                              % (fname, m.group(1), len(disk)))
                bad += 1
            if int(m.group(2)) != len(groups):
                errors.append('pick.html 写 %s 有 %s 组，该页实际 %d 组'
                              % (fname, m.group(2), len(groups)))
                bad += 1
            if m.group(3) != dim:
                errors.append('pick.html 写 %s 切「%s」，应为「%s」'
                              % (fname, m.group(3), dim))
                bad += 1

        chips = set(re.findall(r'href="%s#g-([a-z]+)"' % re.escape(fname), card))
        if chips != set(keys):
            errors.append('pick.html %s 的组名胶囊 %s 与该页分组 %s 不一致（少一个就点不进那一组）'
                          % (fname, sorted(chips), sorted(keys)))
            bad += 1
        if ('href="%s"' % fname) not in card:
            errors.append('pick.html %s 卡片缺该页直链' % fname)
            bad += 1

        conf = _confusion(page)
        if conf and conf not in card:
            errors.append('pick.html %s 卡片未写出该页的边界澄清：%s' % (fname, conf[:24]))
            bad += 1

    # 3) 覆盖合计 == 全库，维度互不相同
    disk_all = _disk_games(TB, [c for _, cats, _ in PAGES for c in cats])
    if all_games != disk_all:
        errors.append('7 个挑款页覆盖 %d 款，全库 %d 款：漏 %s'
                      % (len(all_games), len(disk_all), sorted(disk_all - all_games)[:6]))
        bad += 1
    if sum_games != len(disk_all):
        errors.append('7 页款数相加 %d != 全库 %d（有分类被重复计入或漏计）'
                      % (sum_games, len(disk_all)))
        bad += 1
    if len(set(dims)) != 7:
        errors.append('七套切法的维度名重复：%s' % dims)
        bad += 1
    for d in dims:
        if d not in pick:
            errors.append('pick.html 缺维度名：%s' % d)
            bad += 1
    if str(sum_groups) not in pick:
        errors.append('pick.html 未写出分组合计 %d' % sum_groups)
        bad += 1

    # 4) 反向入口：7 个挑款页 + index + README 都要指回 pick.html
    for fname, _, _ in PAGES:
        page = _read(os.path.join(TB, fname))
        if 'href="pick.html"' not in page:
            errors.append('%s 缺回指 pick.html 的入口（总表不该是单向入口）' % fname)
            bad += 1
    if 'href="pick.html"' not in idx:
        errors.append('index.html 首屏缺 pick.html 入口')
        bad += 1
    if '(pick.html)' not in rm:
        errors.append('README 缺 pick.html 入口')
        bad += 1

    # 5) 破冰口径三处一致（「11 款 = 本页 5 款带标签 + 6 款在别处」）
    ice = _read(os.path.join(TB, 'ice.html'))
    for name, t in (('pick.html', pick), ('ice.html', ice), ('README.md', rm)):
        if '本页 8 款里只有' not in t:
            errors.append('%s 缺「破冰 11 款里本页只有 5 款带标签」的口径说明' % name)
            bad += 1

    print('[42] 挑款总入口：%d 个挑款页 / %d 组 / %d 款（全库 %d 款）；'
          '维度 %d 个；胶囊锚点与边界澄清逐页核对；异常 %d 项'
          % (len(PAGES), sum_groups, sum_games, len(disk_all), len(set(dims)), bad))
    return bad


def check_pick_banner(errors, TB):
    """[43] 挑款页页首横条：本页是七套切法里的第几套。

    为什么值得固化：`pick.html` 的入口原先只落在每页**页脚**「🔗 相关的入口」的一条 li 上，
    教练翻进某一页后基本看不见「还有另外六套切法」，于是很自然地把手上这套口径套到别的分类。
    横条把「序号 + 切的维度 + 套到别处会怎样」提到页首；本项守住三件事：
      a) 横条在**页首**（信息卡 / 第一个 section 之前），不是又一个页脚条
      b) 序号在**三处同源**：横条、该页页脚 li、pick.html 卡片标题 —— 任一处改号都会立刻报错
      c) 配色类（`.pick-master` / `.pm-no`）随页定义，不新增第 8 套配色
    """
    bad = 0
    pick = _read(os.path.join(TB, PICK))
    seen = []

    for idx, (fname, _cats, dim) in enumerate(PAGES, 1):
        page = _read(os.path.join(TB, fname))

        # 1) 横条唯一
        if page.count('class="pick-master"') != 1:
            errors.append('%s 的页首横条应恰好 1 条，实际 %d 条'
                          % (fname, page.count('class="pick-master"')))
            bad += 1
            continue
        m = re.search(r'<div class="pick-master">(.*?)\n    </div>', page, re.S)
        if not m:
            errors.append('%s 的页首横条结构不完整（找不到收尾）' % fname)
            bad += 1
            continue
        banner = m.group(1)

        # 2) 横条在页首：必须在信息卡与第一个 section 之前
        pos = page.index('class="pick-master"')
        for anchor, label in (('<div class="info-grid">', '信息卡网格'),
                              ('<div class="section">', '正文第一节')):
            if anchor in page and pos > page.index(anchor):
                errors.append('%s 的横条落在%s之后 —— 页脚条起不到页首提示的作用'
                              % (fname, label))
                bad += 1

        # 3) 序号：横条 / 页脚 li / pick.html 卡片 三处同源
        banner_no = re.search(r'第 (\d+) / 7 套', banner)
        foot_no = re.search(r'本页是其中第 (\d+) 套', page)
        if not banner_no:
            errors.append('%s 横条缺「第 N / 7 套」序号' % fname)
            bad += 1
        if not foot_no:
            errors.append('%s 页脚「🔗 相关的入口」缺「本页是其中第 N 套」' % fname)
            bad += 1
        card_no = re.search(r'id="p-%s">\s*<h3>第 (\d+) / 7 套' % fname[:-5], pick)
        if not card_no:
            errors.append('pick.html 卡片 %s 缺「第 N / 7 套」序号' % fname[:-5])
            bad += 1
        nums = [int(x.group(1)) for x in (banner_no, foot_no, card_no) if x]
        if len(set(nums)) > 1:
            errors.append('%s 的序号三处不一致：横条 %s / 页脚 %s / 总表卡片 %s'
                          % (fname,
                             banner_no.group(1) if banner_no else '-',
                             foot_no.group(1) if foot_no else '-',
                             card_no.group(1) if card_no else '-'))
            bad += 1
        if nums:
            seen.append(nums[0])

        # 4) 横条必须写清「切的是哪个维度」并指回总表
        if ('本页切的是「%s」' % dim) not in banner:
            errors.append('%s 横条未写「本页切的是「%s」」' % (fname, dim))
            bad += 1
        if 'href="pick.html"' not in banner:
            errors.append('%s 横条缺 pick.html 直链（横条要能点回总表）' % fname)
            bad += 1
        if '另外 6 套' not in banner:
            errors.append('%s 横条缺「另外 6 套问的是别的维度」这句（只说序号不说边界等于没说）'
                          % fname)
            bad += 1

        # 5) 配色类随页定义（不新增第 8 套配色）
        for sel in ('.pick-master {', '.pick-master .pm-no {'):
            if sel not in page:
                errors.append('%s 缺样式 %s（横条会裸奔）' % (fname, sel))
                bad += 1

    if sorted(seen) != list(range(1, len(PAGES) + 1)):
        errors.append('七页横条序号不是 1..%d 各一次：%s' % (len(PAGES), seen))
        bad += 1

    print('[43] 挑款页首横条：%d 页 / 序号 %s；页首位置、维度文案、回指总表、'
          '三处序号同源、配色类随页；异常 %d 项'
          % (len(PAGES), ','.join(str(n) for n in sorted(seen)), bad))
    return bad


PURPOSE_OF = {
    'collab.html': 'collaboration',
    'idea.html': 'idea',
    'comm.html': 'communication',
    'ice.html': 'icebreaker',
    'online.html': 'online',
    'lead.html': 'leadership',
    'trust.html': 'trust',
}


def check_generator_pick_switch(errors, TB):
    """[44] 生成器「🔀 换一整套切法」跨类出口。

    为什么值得固化：子类行**一次只能显示一套口径**（选了协作才出协作 6 组），教练往往是
    「看完结果」才意识到自己该问的是另一个问题 —— 那时只能滚回顶部重选目的，而顶部并不知道
    「还有另外六套切法」。结果区顶部的 7 个胶囊就是补这个出口；本项守四件事：
      a) 7 个胶囊的 data-purpose 与 pick.html 七套切法**同序同集合**（少一个就有一套切法进不去）
      b) 切换时**上一套的子类必须清空**（否则会带着「瓶颈与流水线」去筛沟通，静默出 0 款）
      c) 顶部「🎯 主要目的」按钮的选中态要同步（否则上下两处打脸）
      d) 整套流程模式不显示（那套看的是「处境」，七套切法不适用）
    """
    gpath = os.path.join(TB, 'toolbox', 'generator.html')
    if not os.path.exists(gpath):
        errors.append('缺生成器：toolbox/generator.html')
        print('[44] 生成器换切法出口：文件缺失；异常 1 项')
        return 1
    gen = _read(gpath)
    pick = _read(os.path.join(TB, PICK))
    bad = 0

    # 1) 横条在场且位置在结果区第一张卡之前
    if gen.count('id="pick-switch-bar"') != 1:
        errors.append('生成器应恰好 1 条 #pick-switch-bar，实际 %d 条'
                      % gen.count('id="pick-switch-bar"'))
        bad += 1
    pos = gen.find('id="pick-switch-bar"')
    flow = gen.find('id="flow-section"')
    if pos < 0 or flow < 0 or pos > flow:
        errors.append('换切法横条不在结果区第一张卡之前（应排在 flow-section 前面）')
        bad += 1

    # 2) 7 个胶囊与七套切法同序同集合 + 维度名与 pick.html 同源
    want = [PURPOSE_OF[f] for f, _c, _d in PAGES]
    got = re.findall(r'<button class="pick-chip" data-purpose="([a-z]+)"', gen)
    if got != want:
        errors.append('生成器胶囊 %s 与七套切法 %s 不同序或不同集合' % (got, want))
        bad += 1
    for fname, _c, dim in PAGES:
        if ('data-purpose="%s"' % PURPOSE_OF[fname]) not in gen:
            errors.append('生成器缺 %s 那一套的口袋（data-purpose="%s"）' % (fname, PURPOSE_OF[fname]))
            bad += 1
        if ('切「%s」' % dim) not in pick:
            errors.append('维度名「%s」在 pick.html 里找不到（两边命名已漂移）' % dim)
            bad += 1
    if ('href="../pick.html"' % ()) not in gen:
        errors.append('换切法横条缺 ../pick.html 总表入口')
        bad += 1

    # 3) switchPickClass 必须做全四件事
    m = re.search(r'function switchPickClass\(btn\) \{(.*?)\n\}', gen, re.S)
    if not m:
        errors.append('生成器缺 switchPickClass()')
        bad += 1
    else:
        body = m.group(1)
        if 'userSelections.purpose = purpose' not in body:
            errors.append('switchPickClass 没有真正切换 purpose')
            bad += 1
        lapsed = [fn for fn in ('refreshCollabSub', 'refreshIdeaSub', 'refreshIceSub',
                                'refreshOnlineSub', 'refreshCommSub', 'refreshLeadSub',
                                'refreshTrustSub') if (fn + '()') not in body]
        if lapsed:
            errors.append('switchPickClass 漏复位子类：%s（会带着上一套的组名去筛新分类）'
                          % '/'.join(lapsed))
            bad += 1
        if "'purpose-group'" not in body:
            errors.append('switchPickClass 没有同步顶部「🎯 主要目的」按钮的选中态（上下会打脸）')
            bad += 1
        if 'generatePlan()' not in body:
            errors.append('switchPickClass 没有触发重算')
            bad += 1
        if 'markPickSwitch()' not in body:
            errors.append('switchPickClass 没有更新胶囊选中态')
            bad += 1

    # 4) 显隐：整套流程模式不出现，拼游戏模式出现
    if "setCardVisible('pick-switch-bar', !flowMode)" not in gen:
        errors.append('generatePlan 的整套流程分支没有按 flowMode 显隐换切法横条')
        bad += 1
    if "setCardVisible('pick-switch-bar', true)" not in gen:
        errors.append('generatePlan 的拼游戏分支没有显式显示换切法横条')
        bad += 1
    mk = re.search(r'function markPickSwitch\(\) \{(.*?)\n\}', gen, re.S)
    if not mk:
        errors.append('生成器缺 markPickSwitch()')
        bad += 1
    elif "currentMode !== 'game'" not in mk.group(1):
        errors.append('markPickSwitch 没有在非拼游戏模式下收起横条')
        bad += 1

    # 5) 样式在场
    for sel in ('.pick-switch {', '.pick-chip.active {'):
        if sel not in gen:
            errors.append('生成器缺样式 %s（胶囊会裸奔）' % sel)
            bad += 1

    print('[44] 生成器换切法出口：%d 个胶囊（与七套切法同序）；切换复位 / 顶部同步 / '
          '显隐分流 / 样式；异常 %d 项' % (len(got), bad))
    return bad
