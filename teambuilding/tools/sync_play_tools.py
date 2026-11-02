#!/usr/bin/env python3
"""把游戏库的数据同步进 play/tools/ 下三个手写静态页的内嵌游戏清单。

这三个工具都是手写 HTML，游戏数据以 JS 对象字面量内嵌在 <script> 里。
手工维护的后果：
  - 只覆盖 20–22 款（库里已有 86 款），工具选不到新游戏
  - plan-generator 的 purpose 分类名与游戏库不一致（工具写「创新思维」，
    库里叫「创意激发」），导致按目的筛选永远匹配不上

本脚本从 _data/games.json 重新生成三份清单，并修正分类名。

用法：python3 tools/sync_play_tools.py [--check]
"""
import json
import pathlib
import re
import sys

BASE = pathlib.Path(__file__).resolve().parent.parent
DATA = BASE / '_data/games.json'
TOOLS = BASE / 'play/tools'

# 有在线版的游戏：在线版 slug -> 游戏库 slug
ONLINE = {
    'human-bingo': 'human-bingo',
    'island-survival': 'island-survival',
    'never-have-i-ever': 'never-have-i-ever',
    'pictionary': 'you-draw-i-guess',
    'red-black': 'red-black-game',
    'team-quiz': 'team-quiz',
    'two-truths-one-lie': 'two-truths-one-lie',
    'virtual-escape': 'virtual-escape',
}

PEOPLE_BUCKETS = [('10人以下', 1, 10), ('10-30人', 10, 30), ('30人以上', 30, 10 ** 6)]
DUR_BUCKETS = [('30分钟内', 1, 30), ('30-60分钟', 30, 60), ('60分钟以上', 60, 10 ** 6)]


def overlaps(a, b, c, d):
    return a <= d and c <= b


def people_buckets(g):
    """该游戏适配哪些人数档。group 口径按「多组并行」估算全场上限。"""
    if g['unit'] == 'group':
        tp = g.get('total_ppl')
        if tp:
            lo, hi = tp
        else:
            lo, hi = g['pmin'], g['pmax'] * 4      # 约 4 组并行
    else:
        lo, hi = g['pmin'], g['pmax']
    return [name for name, a, b in PEOPLE_BUCKETS if overlaps(lo, hi, a, b)]


def dur_buckets(g):
    lo, hi = g['dmin'], g['dmax']
    return [name for name, a, b in DUR_BUCKETS if overlaps(lo, hi, a, b)]


def forms(g):
    out = []
    if g['vkey'] in ('indoor', 'both'):
        out.append('室内')
    if g['vkey'] in ('outdoor', 'both'):
        out.append('户外')
    if g['slug'] in ONLINE.values():
        out.append('线上')
    return out or ['室内']


def link_of(g):
    """在线版优先给「在线玩」按钮，否则给库文档。"""
    for oslug, lslug in ONLINE.items():
        if lslug == g['slug']:
            return f'../../games/{oslug}/', '在线玩'
    return '../../../' + g['html'], '查看玩法'


# ── 物资清单：从游戏库 md 的「物资清单」小节提取，没有就用元信息「道具需求」兜底 ──

QTY_RX = re.compile(r'(\d[\d\-–~ ]*\s*(?:张|个|支|块|根|条|副|米|颗|包|盒|只|人|份|圈|叠|把|卷|袋|组|台|套))')


def split_qty(txt):
    """把「意面 20 根/组（干、直条）」拆成 (「意面」, 「20 根/组」)。

    数量不一定在末尾，且常带「/组」「/人」后缀；数量之后的括号注释直接丢弃。"""
    txt = txt.strip()
    m = QTY_RX.search(txt)
    if not m:
        return (txt, '若干')
    name = txt[:m.start()].strip(' ，,、/')
    qty = m.group(1).strip()
    # 量词后缀：20 根/组 → 20 根/组
    mm = re.match(r'\s*/\s*([^\s（(、，,]{1,3})', txt[m.end():])
    if mm:
        qty += '/' + mm.group(1)
    name = re.sub(r'\s{2,}', ' ', name) or txt
    return (name, qty)


def dedupe(items):
    """同名物资只保留第一条（md 里偶尔会重复写同一项）"""
    seen, out = set(), []
    for n, q in items:
        key = re.sub(r'\s+', '', n)
        if key in seen:
            continue
        seen.add(key)
        out.append((n, q))
    return out


def parse_materials(md_path, g):
    t = md_path.read_text(encoding='utf-8')
    m = re.search(r'^#{2,3}\s*(?:6\.\s*)?物资清单.*$', t, re.M)
    if m:
        rest = t[m.end():]
        nxt = re.search(r'^#{2,3}\s', rest, re.M)
        seg = rest[:nxt.start()] if nxt else rest
        items = []
        for line in seg.split('\n'):
            s = line.strip()
            if not s:
                continue
            if s.startswith('|'):
                cells = [c.strip() for c in s.strip('|').split('|')]
                if len(cells) < 2:
                    continue
                if re.fullmatch(r'[-: ]+', cells[0]) or cells[0] in ('物资', '物品', '名称'):
                    continue
                name, qty = cells[0], cells[1]
                if name:
                    items.append((re.sub(r'\*\*', '', name), re.sub(r'\*\*', '', qty) or '若干'))
            else:
                mm = re.match(r'^[-*+]\s+(?:\[[ xX]\]\s*)?(.+)$', s)
                if not mm:
                    continue
                txt = re.sub(r'\*\*', '', mm.group(1)).strip()
                if not txt:
                    continue
                nm, qty = split_qty(txt)
                items.append((nm, qty))
        if items:
            return dedupe(items)[:8]

    # 兜底：用元信息的「道具需求」
    raw = (g.get('props') or '').strip()
    if not raw:
        return [('无特殊物资（仅需场地）', '1 块'), ('计时器（可选）', '1 个')]
    raw = re.sub(r'\*\*(.+?)\*\*', r'\1', raw)
    # 桌游的「道具需求」带 markdown 链接（[printables 打印页](https://...)），
    # 不剥掉会被后面的分隔符切成一堆碎片
    raw = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', raw)
    raw = re.sub(r'https?://\S+', '', raw).strip()
    raw = raw.replace('printables 打印页', '打印页')
    raw = re.sub(r'^\s*(有|无)\s*[（(]?\s*', '', raw)
    raw = raw.rstrip('）)').strip()
    parts = [p.strip() for p in re.split(r'[+、,，/]', raw) if p.strip()]
    if not parts:
        parts = [raw]
    out = []
    for p in parts[:6]:
        nm, qty = split_qty(p)
        out.append((nm, qty))
    return dedupe(out) or [('无特殊物资（仅需场地）', '1 块')]


# ── 生成三份清单 ──

# 线上专有游戏：没有 md 源文件，只能手工维护条目。
# online-bingo 是手写静态页（games/online/online-bingo.html），不进 games.json。
EXTRA_PLAN = [{
    'name': '线上宾果',
    'purpose': '破冰热场',
    'forms': ['线上'],
    'peoples': ['10人以下', '10-30人', '30人以上'],
    'durations': ['30分钟内'],
    'play': '线上版人类宾果，用视频会议完成特征确认与标记。',
    'link': '../../../games/online/online-bingo.html',
    'linkLabel': '查看玩法',
}]

EXTRA_MATERIALS = [{
    'name': '线上宾果',
    'materials': [
        {'name': '电脑或投影', 'qty': '1 台'},
        {'name': '网络连接', 'qty': '1 路'},
        {'name': '线上工具账号', 'qty': '1 个'},
    ],
}]


def gen_plan(games):
    out = list(EXTRA_PLAN)
    for g in games:
        out.append({
            'name': g['name'],
            'purpose': g['cat_name'],
            'forms': forms(g),
            'peoples': people_buckets(g),
            'durations': dur_buckets(g),
            'play': g['summary'],
            'link': link_of(g)[0],
            'linkLabel': link_of(g)[1],
        })
    return out


def gen_wheel(games):
    out = []
    for g in games:
        out.append({
            'name': g['name'],
            'cat': g['cat_name'],
            'pmin': g['pmin'],
            'pmax': g['pmax'],
            'venue': g['vkey'],
            'mins': (f'{g["dmin"]}–{g["dmax"]} 分钟' if g['dmin'] != g['dmax']
                     else f'{g["dmax"]} 分钟'),
            'rule': g['summary'],
            'url': '../../../' + g['html'],
        })
    return out


def gen_materials(games):
    out = list(EXTRA_MATERIALS)
    for g in games:
        items = parse_materials(BASE / g['md'], g)
        out.append({
            'name': g['name'],
            'materials': [{'name': n, 'qty': q} for n, q in items],
        })
    return out


# ── 写回 ──

def js_quote(s):
    return "'" + str(s).replace('\\', '\\\\').replace("'", "\\'") + "'"


def dump_plan(arr):
    lines = ["var GAMES = ["]
    for it in arr:
        lines.append(
            f"  {{ name: {js_quote(it['name'])}, purpose: {js_quote(it['purpose'])}, "
            f"forms: [{', '.join(js_quote(x) for x in it['forms'])}], "
            f"peoples: [{', '.join(js_quote(x) for x in it['peoples'])}], "
            f"durations: [{', '.join(js_quote(x) for x in it['durations'])}], "
            f"play: {js_quote(it['play'])}, link: {js_quote(it['link'])}, "
            f"linkLabel: {js_quote(it['linkLabel'])} }},")
    lines.append("];")
    return '\n'.join(lines)


def dump_wheel(arr):
    lines = ["var GAMES = ["]
    for it in arr:
        lines.append(
            f"  {{ name: {js_quote(it['name'])}, cat: {js_quote(it['cat'])}, "
            f"pmin: {it['pmin']}, pmax: {it['pmax']}, venue: {js_quote(it['venue'])}, "
            f"mins: {js_quote(it['mins'])}, rule: {js_quote(it['rule'])}, "
            f"url: {js_quote(it['url'])} }},")
    lines.append("];")
    return '\n'.join(lines)


def dump_materials(arr):
    lines = ["var GAMES = ["]
    for it in arr:
        lines.append(f"  {{ name: {js_quote(it['name'])}, materials: [")
        for m in it['materials']:
            lines.append(f"    {{ name: {js_quote(m['name'])}, qty: {js_quote(m['qty'])} }},")
        lines.append("  ]},")
    lines.append("];")
    return '\n'.join(lines)


def replace_array(html, new_js):
    m = re.search(r'var GAMES = \[[\s\S]*?\n\];', html)
    if not m:
        return None
    return html[:m.start()] + new_js + html[m.end():]


def main():
    check = '--check' in sys.argv
    games = json.loads(DATA.read_text(encoding='utf-8'))
    games.sort(key=lambda g: g['name'])

    targets = [
        ('plan-generator', 'plan-generator/index.html', dump_plan(gen_plan(games))),
        ('variety-wheel', 'variety-wheel/index.html', dump_wheel(gen_wheel(games))),
        ('materials', 'materials/index.html', dump_materials(gen_materials(games))),
    ]

    for name, rel, new_js in targets:
        f = TOOLS / rel
        html = f.read_text(encoding='utf-8')

        if name == 'plan-generator':
            # 目的维度选项必须与游戏库分类名一致（原来写「创新思维」，库里叫「创意激发」）
            cats = sorted({g['cat_name'] for g in games})
            # 重写 purpose 选项按钮
            html, n = re.subn(
                r'(<div class="dim-label">目的</div>\s*<div class="opts">)([\s\S]*?)(</div>)',
                lambda mm: mm.group(1)
                + '\n' + '\n'.join(
                    f'        <button type="button" class="opt" data-dim="purpose" '
                    f'data-val="{c}" onclick="toggleOpt(this)">{c}</button>'
                    for c in cats)
                + '\n      ' + mm.group(3),
                html, count=1)
            if not n:
                print('! plan-generator: 找不到 purpose 选项容器，跳过选项重写')

        html2 = replace_array(html, new_js)
        if html2 is None:
            print(f'✗ {name}: 找不到 GAMES 数组')
            return 1
        if check:
            print(f'{name:16s} 待同步 {len(games)} 款')
        else:
            f.write_text(html2, encoding='utf-8')
            print(f'✓ {name:16s} 已同步 {len(games)} 款')
    return 0


if __name__ == '__main__':
    sys.exit(main())
