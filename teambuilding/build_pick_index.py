# -*- coding: utf-8 -*-
"""生成 teambuilding/pick.html（挑款总入口 · 七套切法对照）+ 打三处补丁。

补丁（全部幂等，重复执行不会重复插入）：
  1. index.html 首屏 res-row 加一个 pick.html 胶囊
  2. 7 个挑款页的「🔗 相关的入口」各加一条指回 pick.html
  3. README.md 决策表加一行 + 网页版清单加一条

数字全部从源文件现算（分类目录款数 / 各页 group-card 组数），不手写，
避免以后新增游戏时总表与挑款页漂移。只创建/更新文件，不做 git 操作。
"""
import io
import os
import re

TB = os.path.dirname(os.path.abspath(__file__))


# ---------------- 读写（保留原换行符） ----------------
def read_raw(p):
    return io.open(p, encoding='utf-8', newline='').read()


def write_raw(p, s):
    io.open(p, 'w', encoding='utf-8', newline='').write(s)


def eol_of(p):
    """⚠️ index.html / README 是 CRLF，挑款页是 LF —— 锚点必须用真实换行符拼装。"""
    return '\r\n' if b'\r\n' in io.open(p, 'rb').read() else '\n'


# ---------------- 7 套切法的口径（手工撰写，其余全部自动取数） ----------------
PAGES = [
    dict(slug='collab', file='collab.html', emoji='🤝', title='团队协作',
         cats=['collaboration'],
         dimension='动作',
         question='这一局练的是哪一种协作',
         symptom='一群人凑在一起干不成活，说不清是力气不齐、分工不齐，还是信息不齐',
         when='干活的配合出问题（接力卡住 / 资源不够分 / 人只看见自己那块），'
              '或者带完一场想复盘「我们哪一段没接上」。',
         avoid='别用它回答「这个团队关系好不好」——39 款只观察配合动作，'
               '不碰信任、情绪与权力；也别拿它当破冰目录，6 组里没有一组是纯热场。',
         note='全站只有这一页的首页网格带小标题（6 组），因为组与组之间的动作差别足够大、'
              '值得在首页就分开；其余 6 页都只用 data-* 属性 + 肌肉标签胶囊。'),
    dict(slug='idea', file='idea.html', emoji='💡🔧', title='创意与解题',
         cats=['creativity', 'problem-solving'],
         dimension='思考位置',
         question='团队当下卡在哪一步',
         symptom='方案要么不新、要么解不开；会上出的主意都像同一个',
         when='团队卡在「想」这一步：问题没定义清 / 没人敢写赌注 / 资源不够还得选 / 或者急着定方案。',
         avoid='别当「想不出点子」的万灵药——4 组里有 2 组（限制下取舍 / 先留余地）'
               '练的是「别急着定」，不是「多出主意」。',
         note='这是唯一一组横跨两个分类的切法：💡创新思维 5 款 + 🔧问题解决 5 款，'
              '因为「创新」和「解题」在教练手上本来就是同一个动作的两端。'),
    dict(slug='comm', file='comm.html', emoji='💬', title='沟通表达',
         cats=['communication'],
         dimension='通道',
         question='这一局沟通坏在哪一环',
         symptom='说了半天对方没听懂，或者传着传着就变味了',
         when='信息在人与人之间掉了（说不清 / 传不准 / 凑不齐 / 说不拢）——先定位断在哪一环，再挑游戏。',
         avoid='别把它当「表达训练」——8 款里 4 款先把一条通道堵死（不许看 / 不许问 / 只说一遍 / 不许擦），'
               '真正练「怎么说」的只有 🗣️ 那 2 款。',
         note=''),
    dict(slug='ice', file='ice.html', emoji='🧊', title='破冰热场',
         cats=['icebreaker'],
         dimension='存量',
         question='破冰之后，团队手里剩下什么',
         symptom='开场十分钟，散场后要留下点什么 —— 名字？笑声？还是一点真话？',
         when='每场团建的第一分钟，要先确定「散场时手里多出什么」：'
              '名字 / 笑声 / 私事 / 一支能配合的小队。',
         avoid='领导在场、上下级混编、刚吵完架的场合别选 💬 那组（真话收不回来）；'
               '反过来，全新团队只玩 🎭 那组，热完还是一盘散沙。',
         note=''),
    dict(slug='online', file='online.html', emoji='💻', title='线上团建',
         cats=['online'],
         dimension='成立条件',
         question='远程这一局靠什么成立',
         symptom='人散在各地 / 凑不齐整块时间，先问这一场到底能不能开起来',
         when='人不在同一个房间，要先确认「这一局靠什么成立」：要不要专用工具 / 要不要共享屏 / '
              '要不要一份文档 / 人要不要同时在线。',
         avoid='跨时区团队别按「线上」挑——8 款里只有 1 款真异步，其余 7 款都要求全员同时在线、同时开始。',
         note='七套里只有这一套是「减法」：其余六套问「要练哪一层」，它问「这场开不开得起来」。'
              '所以线上永远该最先问 —— 开不起来，后面六套都白挑。'),
    dict(slug='lead', file='lead.html', emoji='👑', title='领导力',
         cats=['leadership'],
         dimension='权力层级',
         question='带人这件事卡在哪一层',
         symptom='管理者什么都自己扛，或者一放手就出事',
         when='管理者要练「拍板方式 / 授权边界 / 没有职位权力也能带」里的某一层。',
         avoid='别指望半小时做完——6 款里 5 款要 60 min 以上，只有沉默领袖 30–40 min；'
               '也别指望它练「沟通」或「信任」。',
         note=''),
    dict(slug='trust', file='trust.html', emoji='🔐', title='信任建立',
         cats=['trust'],
         dimension='托付内容',
         question='托付出去的是什么',
         symptom='团队不敢说真话，也不敢把一件事真正交给别人',
         when='要练「把什么交给了对方」：身体与安全 / 会受伤的自己 / 一件事的成败。',
         avoid='别把背摔、盲行当成信任训练的全部——它们最不留沉淀（20–40 min）；'
               '分水岭是「接住」是不是强制的，能被选择不接住的那 4 款才对应工作里的信任。',
         note=''),
]

# ---------------- 从源文件取数 ----------------
def groups_of(slug_file):
    t = read_raw(os.path.join(TB, slug_file))
    out = []
    for m in re.finditer(r'<div class="group-card" id="g-([a-z]+)">\s*<h3>(.*?)（(\d+) 款）</h3>', t):
        out.append((m.group(1), m.group(2).strip(), int(m.group(3))))
    return out


def border_of(slug_file):
    """该页的边界澄清大标题（🔀 / 🚧 那一条），没有就返回空。"""
    t = read_raw(os.path.join(TB, slug_file))
    for m in re.finditer(r'<h2>([^<]*(?:不等于|不是两个抽屉)[^<]*)</h2>', t):
        # 去掉标题自带的 🔀 / 🚧 前导 emoji（本页会自己加一个），否则会「🔀 🔀 …」
        return re.sub(r'^[\U0001F300-\U0001FAFF\u2190-\u21FF\u2600-\u27BF\s]+', '',
                      m.group(1).strip())
    return ''


def disk_count(cats):
    n = 0
    for c in cats:
        d = os.path.join(TB, 'games', c)
        n += len([f for f in os.listdir(d) if f.endswith('.md')])
    return n


for p in PAGES:
    p['groups'] = groups_of(p['file'])
    p['border'] = border_of(p['file'])
    p['n_disk'] = disk_count(p['cats'])

N_GROUPS = sum(len(p['groups']) for p in PAGES)
N_GAMES = sum(p['n_disk'] for p in PAGES)


# ---------------- 配色（主色 #358c4a，hue 134.5，落在全站 126.8↔142.4 的 15.6° 空档） ----------------
MAIN = '#358c4a'
INK = '#07120a'
BODY1, BODY2, BODY3 = '#0a160d', '#07120a', '#0d1b11'
CONTAINER = '#142d1a'
BORDER = '#2a5735'
TABLE_ALT = '#183522'
TEXT = '#a9ebb9'
MUTED = '#6f9e7a'
HEAD1_2, HEAD1_3 = '#53b86b', '#82e099'
H2C, H3C = '#5ac774', '#53b86b'
QUOTE_BG = '#1b3a23'
WHEN_BG, AVOID_BG = '#22432e', '#3a2a1c'
DEEP = '#08130b'

CSS = """<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.6; color: %(text)s;
        background: linear-gradient(135deg, %(body1)s 0%%, %(body2)s 55%%, %(body3)s 100%%);
        padding: 20px;
    }
    .container {
        max-width: 1100px; margin: 0 auto; background: %(container)s;
        border-radius: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.7);
        overflow: hidden; border: 1px solid %(border)s;
    }
    .header {
        background: linear-gradient(135deg, %(main)s 0%%, %(head12)s 45%%, %(head13)s 100%%);
        color: %(ink)s; padding: 40px; text-align: center;
    }
    .header h1 { font-size: 2.1em; margin-bottom: 10px; text-shadow: 0 1px 3px rgba(255,255,255,0.25); }
    .header .subtitle { font-size: 1.05em; opacity: 0.95; }
    .header .tag {
        display: inline-block; margin-top: 14px; padding: 6px 18px;
        background: rgba(0,0,0,0.22); border-radius: 20px; font-size: 0.9em; border: 1px solid %(head13)s;
    }
    .info-grid {
        display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 20px; padding: 30px; background: %(deep)s;
    }
    .info-card {
        background: %(container)s; padding: 20px; border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.4); text-align: center; border: 1px solid %(border)s;
    }
    .info-card .icon { font-size: 2em; margin-bottom: 8px; }
    .info-card .label { font-size: 0.9em; color: %(muted)s; }
    .info-card .value { font-size: 1.05em; font-weight: bold; color: %(text)s; }
    .section { padding: 30px 40px; }
    .section h2 {
        color: %(h2c)s; border-left: 5px solid %(main)s; padding-left: 15px;
        margin-bottom: 20px; font-size: 1.55em;
    }
    .section h3 { color: %(h3c)s; margin: 22px 0 10px; font-size: 1.18em; }
    .section p, .section li { color: %(text)s; margin-bottom: 10px; }
    .section ul, .section ol { padding-left: 25px; }
    .data-table {
        width: 100%%; border-collapse: collapse; margin-top: 15px;
        background: %(deep)s; border-radius: 10px; overflow: hidden;
    }
    .data-table th { background: %(main)s; color: %(ink)s; padding: 12px; text-align: left; font-size: 0.95em; }
    .data-table td { padding: 10px 12px; border-top: 1px solid %(border)s; color: %(text)s; font-size: 0.92em; }
    .data-table tr:nth-child(even) { background: %(alt)s; }
    .data-table .cat { white-space: nowrap; color: %(muted)s; font-size: 0.9em; }
    .data-table .num { font-weight: 700; color: %(h2c)s; }
    .group-card {
        background: %(container)s; border: 1px solid %(border)s; border-radius: 12px;
        padding: 22px 24px; margin-top: 18px;
    }
    .group-card h3 { margin-top: 0; font-size: 1.2em; color: %(h2c)s; }
    .group-lead { font-size: 0.96em; color: %(text)s; margin-bottom: 14px; }
    .chips { display: flex; flex-wrap: wrap; gap: 8px; margin: 0 0 14px; }
    .chips a {
        background: %(quote)s; border: 1px solid %(border)s; border-radius: 16px;
        padding: 5px 12px; font-size: 0.85em; color: %(text)s; text-decoration: none;
    }
    .chips a:hover { background: %(border)s; }
    .when-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 14px; margin-bottom: 16px; }
    .when-box, .avoid-box { border-radius: 10px; padding: 14px 16px; font-size: 0.92em; }
    .when-box { background: %(whenbg)s; border: 1px solid %(border)s; }
    .avoid-box { background: %(avoidbg)s; border: 1px solid #7a5330; }
    .when-box b { color: %(h2c)s; }
    .avoid-box b { color: #ddb188; }
    .pick {
        display: inline-block; padding: 8px 16px; border-radius: 20px;
        background: %(main)s; color: %(ink)s; font-size: 0.92em; font-weight: 600;
    }
    blockquote {
        background: %(quote)s; border-left: 4px solid %(h2c)s; border-radius: 8px;
        padding: 14px 18px; margin: 14px 0; color: %(text)s; font-size: 0.95em;
    }
    a { color: %(h2c)s; }
    .footer {
        background: %(deep)s; color: %(muted)s; text-align: center; padding: 25px;
        font-size: 0.9em; border-top: 1px solid %(border)s;
    }
    .footer a { color: %(h2c)s; }
    .back-link {
        display: inline-block; margin: 8px 6px 0; padding: 8px 20px;
        background: %(main)s; color: %(ink)s; text-decoration: none; border-radius: 20px; font-size: 0.9em;
    }
    .back-link:hover { background: %(head13)s; }
</style>""" % dict(text=TEXT, main=MAIN, ink=INK, body1=BODY1, body2=BODY2, body3=BODY3,
                 container=CONTAINER, border=BORDER, muted=MUTED, h2c=H2C, h3c=H3C,
                 head12=HEAD1_2, head13=HEAD1_3, deep=DEEP, alt=TABLE_ALT, quote=QUOTE_BG,
                 whenbg=WHEN_BG, avoidbg=AVOID_BG)


# ---------------- 各段内容 ----------------
def sec_locate():
    rows = []
    for p in PAGES:
        rows.append(
            '            <tr><td>%s</td><td class="cat">%s</td>'
            '<td><a href="%s">%s挑款指南</a></td>'
            '<td class="num">%d 款 / %d 组</td></tr>'
            % (p['symptom'], p['dimension'], p['file'], p['title'], p['n_disk'], len(p['groups'])))
    return """    <div class="section">
        <h2>⚡ 30 秒定位：你手上的问题属于哪一种</h2>
        <p>不用读完整个站。先认出你手上是<strong>哪一种问题</strong>，再进对应的那一页 —— 七页的分组口径完全不同，进错了页，后面怎么挑都是错的。</p>
        <table class="data-table">
            <tr><th>你手上的问题长什么样</th><th>要切的是哪一层</th><th>去哪一页</th><th>页内规模</th></tr>
%s
        </table>
        <blockquote>七个问题听起来都能叫「团队有问题」，但它们切的是<strong>七个不同的维度</strong> —— 这不是七种风格，是七把不同的刀。用错刀，切出来的形状一样，结论完全不同。</blockquote>
    </div>

""" % '\n'.join(rows)


def sec_dimensions():
    rows = ['            <tr><td class="cat">%s %s</td><td><b>%s</b></td><td>%s</td>'
            '<td class="num">%d 组</td><td class="num">%d 款</td></tr>'
            % (p['emoji'], p['title'], p['dimension'], p['question'], len(p['groups']), p['n_disk'])
            for p in PAGES]
    rows.append('            <tr><td class="cat">合计</td><td>7 个维度</td><td>—</td>'
                '<td class="num">%d 组</td><td class="num">%d 款</td></tr>' % (N_GROUPS, N_GAMES))
    return """    <div class="section">
        <h2>🔀 七套切法：切的是七个不同的维度</h2>
        <table class="data-table">
            <tr><th>分类</th><th>切的维度</th><th>那一页问的那句话</th><th>组数</th><th>覆盖</th></tr>
%s
        </table>
        <p style="margin-top:18px;">七个维度彼此独立，<strong>没有高低、也不能互相代入</strong>：一个团队完全可能「配合动作很熟，但彼此不敢托付」，也可能「沟通很顺，但没人敢拍板」。所以七套切法不是「同一件事的七种说法」，而是七个不同的问题。</p>
        <blockquote>⚠️ 两件可以相加、两件不能相加：<strong>能相加的是「分类」</strong> —— 8 个分类加起来正好 %d 款（其中 💡创意 5 款 + 🔧解题 5 款合在一套切法里），没有一款落在挑款体系之外；<strong>不能相加的是「带标签的款数」</strong> —— 各页的标签口径不同（破冰按场景标签、线上按改造段、沟通 / 领导力 / 信任按目的标签），所以各页的「XX 不只是这 N 款」只能各自读，不能求总和。</blockquote>
        <blockquote>七套里只有 💻 线上是<strong>减法</strong>：其余六套问「要练哪一层」，它问「这一场开不开得起来」（要不要专用工具 / 要不要共享屏 / 人要不要同时在线）。所以线上永远该<strong>最先问</strong> —— 开不起来，后面六套都白挑。</blockquote>
    </div>

""" % ('\n'.join(rows), N_GAMES)


def sec_cards():
    out = []
    for i, p in enumerate(PAGES, 1):
        chips = ' '.join('<a href="%s#g-%s">%s（%d 款）</a>' % (p['file'], k, name, n)
                         for k, name, n in p['groups'])
        border = ''
        if p['border']:
            border = ('            <p style="margin-bottom:12px;">🔀 这一页要澄清的混淆：'
                      '<b>%s</b></p>\n' % p['border'])
        note = ''
        if p['note']:
            note = '            <blockquote>%s</blockquote>\n' % p['note']
        out.append(
            '        <div class="group-card" id="p-%s">\n'
            '            <h3>%s %s挑款指南（%d 款 / %d 组 · 切「%s」）</h3>\n'
            '            <div class="group-lead">这一套问的是「<b>%s</b>」，把 %d 款分成 %d 组：%s。</div>\n'
            '            <div class="chips">%s</div>\n'
            '%s'
            '            <div class="when-row">\n'
            '                <div class="when-box"><b>✅ 什么时候进这一页</b><br>%s</div>\n'
            '                <div class="avoid-box"><b>⛔ 什么时候别进这一页</b><br>%s</div>\n'
            '            </div>\n'
            '%s'
            '            <div class="pick">🎯 进这一页：<a href="%s" style="color:%s;text-decoration:underline;">%s挑款指南 · %d 款 / %d 组</a></div>\n'
            '        </div>\n'
            % (p['slug'], p['emoji'], p['title'], p['n_disk'], len(p['groups']), p['dimension'],
               p['question'], p['n_disk'], len(p['groups']),
               ' / '.join(name for _, name, _ in p['groups']),
               chips, border, p['when'], p['avoid'], note,
               p['file'], INK, p['title'], p['n_disk'], len(p['groups'])))
    return """    <div class="section">
        <h2>🧭 七个挑款页：一页一个维度</h2>
        <p>每张卡里的组名都可以直接点进去（锚到那一页的对应分组）—— 不用先跳页再找。</p>
%s    </div>

""" % ''.join(out)


def sec_mistakes():
    return """    <div class="section">
        <h2>⚠️ 三个最容易出错的用法</h2>
        <h3>① 只看「团队有问题」，就按最熟的那一页挑</h3>
        <p>手里那页最熟，不代表它切的就是你现在这个维度。三组真实的套错现场：</p>
        <table class="data-table">
            <tr><th>把哪一套套到哪一类</th><th>会得到什么</th></tr>
            <tr><td><b>「卡在哪一步」（创意解题）→ 破冰</b></td><td>破冰没有「思考步骤」可言：名字接龙会被硬说成「先定义问题」、两真一假会被硬说成「先写赌注」—— 其实它们练的是「敢不敢讲自己的事」。8 款里 4 款（🪪只认名字 / 🎭只图热闹）根本不产出「思考」。</td></tr>
            <tr><td><b>「托付什么」（信任）→ 沟通</b></td><td>沟通 8 款里 6 款的问题不在「敢不敢交」，而在「话有没有传到」（传不准 / 凑不齐）；真正碰到「信不信对方」的只有 2 款。拿信任的尺子量沟通，会把「传话游戏」判成「信任不足」。</td></tr>
            <tr><td><b>「远程靠什么成立」（线上）→ 领导力</b></td><td>领导力 6 款里只有 2 款（沉默领袖 / 七巧板）写了「搬到线上怎么玩」，其余 4 款没有改造段 —— 硬搬会丢掉「换人复述上任判断」「当面投票」这类只有身体在场才成立的规则。</td></tr>
        </table>

        <h3>② 只按分类挑，漏掉带标签但分类在别处的款</h3>
        <p>这是全站反复出现的同一个坑：<strong>分类只写「主要训练目标」，标签才写「还能用来干什么」</strong>。每页都单独有一节「XX 不只是这 N 款」就是为这个 —— 但漏掉的量级不一样：</p>
        <table class="data-table">
            <tr><th>页</th><th>本分类</th><th>带这个标签 / 改造段的</th><th>按分类挑会漏</th></tr>
            <tr><td><a href="comm.html">💬 沟通</a></td><td>8 款</td><td>20 款</td><td class="num">12 款</td></tr>
            <tr><td><a href="online.html">💻 线上</a></td><td>8 款</td><td>14 款（有远程改造段）</td><td class="num">6 款</td></tr>
            <tr><td><a href="ice.html">🧊 破冰</a></td><td>8 款</td><td>11 款（场景标签；本页 8 款里只有 5 款带）</td><td class="num">6 款</td></tr>
            <tr><td><a href="trust.html">🔐 信任</a></td><td>6 款</td><td>10 款</td><td class="num">4 款</td></tr>
            <tr><td><a href="lead.html">👑 领导力</a></td><td>6 款</td><td>9 款</td><td class="num">3 款</td></tr>
        </table>
        <blockquote>⚠️ 这张表的数字<strong>不能相加</strong>（各页标签口径不同，同一款可能同时出现在两行里），也不能用它算「全库有多少款没被收录」—— 那个数只该用分类算：<strong>8 个分类 = %d 款</strong>。表里真正要读的是「漏掉的量级」：沟通按分类挑会漏掉一半以上。</blockquote>

        <h3>③ 看 emoji 认组 —— 同一个 emoji 在两页里含义不同</h3>
        <p>七页一共 %d 组，有 4 对 emoji 撞车。撞车不是笔误，是因为两页问的维度不同；但<strong>认 emoji 不认页面</strong>就会挑错：</p>
        <table class="data-table">
            <tr><th>emoji</th><th>在这一页是</th><th>在那一页是</th><th>差别在哪</th></tr>
            <tr><td>🍳</td><td><a href="collab.html#g-pipeline">协作 · 瓶颈与流水线</a>（6 款）</td><td><a href="ice.html#g-team">破冰 · 带协作</a>（2 款）</td><td>前者练「工位卡住时怎么调」，后者只要求「热完能配合」，不练流水线</td></tr>
            <tr><td>🧭</td><td><a href="collab.html#g-resource">协作 · 资源与取舍</a>（9 款）</td><td><a href="lead.html#g-decide">领导力 · 定方向与拍板</a>（2 款）</td><td>前者是「东西不够怎么分」，后者是「这个决定用什么方式做出来」</td></tr>
            <tr><td>🎭</td><td><a href="collab.html#g-role">协作 · 角色互补</a>（8 款）</td><td><a href="ice.html#g-hype">破冰 · 只图热闹</a>（2 款）</td><td>前者要「不一样才有用」，后者只要「笑一笑」</td></tr>
            <tr><td>💬</td><td><a href="ice.html#g-know">破冰 · 谈自己的事</a>（2 款）</td><td><a href="trust.html#g-truth">信任 · 交出会受伤的自己</a>（2 款）</td><td>暴露度相近，但破冰「说完就完了」，信任要看「对方接不接」</td></tr>
        </table>
        <blockquote>同一个 emoji 还在别处出现：分类按钮上的 💬 是「沟通」、首页 🧭 是「不知道从哪开始」。点之前先确认自己在哪一页 —— 这也是本页存在的理由：<strong>七套切法需要一张对照表，而不是七张各自为政的目录</strong>。</blockquote>
    </div>

""" % (N_GAMES, N_GROUPS)


def sec_entries():
    lips = ['            <li><a href="index.html">全部 %d 款游戏（按 8 个分类）</a> —— 每个分类下都有对应的二级筛选行</li>' % N_GAMES,
            '            <li><a href="README.md">README 索引表</a> —— 纯文本版，7 个分类都已按各自的口径分好组</li>']
    for p in PAGES:
        lips.append('            <li><a href="%s">%s %s挑款指南</a> —— %d 款 / %d 组，切「%s」</li>'
                    % (p['file'], p['emoji'], p['title'], p['n_disk'], len(p['groups']), p['dimension']))
    lips += [
        '            <li><a href="toolbox/generator.html">团建方案生成器（全库版）</a> —— 选完目的后可按对应那一套再收一层（协作 / 创意解题 / 破冰 / 线上 / 沟通 / 领导力 / 信任 都已接入）</li>',
        '            <li><a href="play/tools/plan-generator/">T1 快速版生成器</a> —— 现场临时只要几个游戏，30 秒出一组</li>',
        '            <li><a href="guide.html">教练使用指南</a> —— 第一次带团先读 5 分钟</li>',
    ]
    return """    <div class="section">
        <h2>🔗 相关的入口</h2>
        <ul>
%s
        </ul>
    </div>

""" % '\n'.join(lips)


HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>挑款总入口 · 七套切法对照 - 团建 &amp; 培训游戏库</title>

%s
</head>
<body>
<div class="container">
    <div class="header">
        <h1>🧭 挑款总入口 · 七套切法对照</h1>
        <div class="subtitle">8 个分类 · 7 套切法 · %d 组 · %d 款 —— 每套切的是不同的一个维度，不能互相套用</div>
        <div class="tag">7 个挑款页 · %d 组 · 全库 %d 款没有一款落在挑款体系之外</div>
    </div>

    <div class="info-grid">
        <div class="info-card"><div class="icon">🗂️</div><div class="label">挑款专页</div><div class="value">7 个（一页一套）</div></div>
        <div class="info-card"><div class="icon">🧩</div><div class="label">分组合计</div><div class="value">%d 组</div></div>
        <div class="info-card"><div class="icon">🎲</div><div class="label">覆盖</div><div class="value">全库 %d 款</div></div>
        <div class="info-card"><div class="icon">🔀</div><div class="label">切的维度</div><div class="value">7 个，互不代入</div></div>
    </div>

%s%s%s%s%s
    <div class="footer">
        <div>
            <a href="index.html" class="back-link">← 回到游戏库</a>
            <a href="README.md" class="back-link">README 索引</a>
            <a href="toolbox/generator.html" class="back-link">方案生成器</a>
        </div>
        <div style="margin-top:14px;">团建 &amp; 培训游戏库 · 挑款总入口 · 7 个挑款页 / %d 组 / %d 款</div>
    </div>
</div>
</body>
</html>
""" % (CSS, N_GROUPS, N_GAMES, N_GROUPS, N_GAMES, N_GROUPS, N_GAMES,
       sec_locate(), sec_dimensions(), sec_cards(), sec_mistakes(), sec_entries(),
       N_GROUPS, N_GAMES)

write_raw(os.path.join(TB, 'pick.html'), HTML)
print('pick.html written: %d 款 / %d 组' % (N_GAMES, N_GROUPS))


# ---------------- 补丁 1：index.html 首屏胶囊 ----------------
p = os.path.join(TB, 'index.html')
t = read_raw(p)
nl = eol_of(p)
anchor = ('<a href="play/tools/plan-generator/" class="res-chip">'
          '⚡ 现场临时只要几个游戏（T1 快速版）</a>')
if 'href="pick.html"' in t:
    print('[1] index.html 已有 pick.html 入口，跳过')
elif t.count(anchor) == 1:
    chip = ('<a href="pick.html" class="res-chip">'
            '🧭 8 个分类怎么挑？七套切法对照</a>')
    t = t.replace(anchor, anchor + nl + '        ' + chip)
    write_raw(p, t)
    print('[1] index.html 首屏已补 pick.html 胶囊')
else:
    print('[1] ⚠️ index.html 锚点命中 %d 次，未打补丁' % t.count(anchor))


# ---------------- 补丁 2：7 个挑款页加回指 ----------------
for i, pg in enumerate(PAGES, 1):
    p = os.path.join(TB, pg['file'])
    t = read_raw(p)
    nl = eol_of(p)
    if 'href="pick.html"' in t:
        print('[2] %s 已有回指，跳过' % pg['file'])
        continue
    h2 = '<h2>🔗 相关的入口</h2>'
    m = re.search(re.escape(h2) + r'(\s*<ul>)', t)
    if not m:
        print('[2] ⚠️ %s 未找到「相关的入口」列表' % pg['file'])
        continue
    li = ('%s    <li><a href="pick.html">🧭 挑款总入口 · 七套切法对照</a>'
          ' —— 本页是其中第 %d 套：切「%s」，另外 6 套问的是别的维度</li>'
          % (nl, i, pg['dimension']))
    t = t[:m.end(1)] + li + t[m.end(1):]
    write_raw(p, t)
    print('[2] %s 已加回指' % pg['file'])


# ---------------- 补丁 3：README ----------------
p = os.path.join(TB, 'README.md')
t = read_raw(p)
nl = eol_of(p)
if 'pick.html' in t:
    print('[3] README 已有 pick.html，跳过')
else:
    # 3a 决策表：插在 🤝 协作那一行之后（表尾）
    anchor = ('| 🤝 目的就是协作，但 39 款挑不过来 | [协作类挑款指南](collab.html) |')
    rows = [l for l in t.split(nl) if l.startswith(anchor)]
    if len(rows) == 1:
        row = ('| 🧭 七个分类各有一套切法，想先看清它们差在哪 | [挑款总入口 · 七套切法对照](pick.html) | '
               '7 个挑款页 / %d 组 / 全库 %d 款：七套切法切的是七个不同的维度'
               '（动作 / 思考位置 / 通道 / 存量 / 成立条件 / 权力层级 / 托付内容），'
               '另附「套错了会得到什么」的三组现场与 4 对撞车 emoji |' % (N_GROUPS, N_GAMES))
        t = t.replace(rows[0], rows[0] + nl + row)
        print('[3a] README 决策表已加一行')
    else:
        print('[3a] ⚠️ README 决策表锚点命中 %d 次，未打补丁' % len(rows))
    # 3b 网页版清单：行尾追加
    lines = t.split(nl)
    hits = [i for i, l in enumerate(lines) if l.startswith('以上 5 份教练资料与生成器均有网页版：')]
    if len(hits) == 1:
        i = hits[0]
        lines[i] = lines[i] + ' · [挑款总入口](pick.html)'
        t = nl.join(lines)
        print('[3b] README 网页版清单已加一条')
    else:
        print('[3b] ⚠️ README 网页版清单锚点命中 %d 次' % len(hits))
    write_raw(p, t)
