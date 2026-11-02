#!/usr/bin/env python3
"""
团建游戏库构建脚本（单入口，参数化，不批量误伤）

用法：
  python3 build.py meta            # 只提取元数据，输出 _data/games.json + 诊断表
  python3 build.py pages           # 生成 games/*/*.html
  python3 build.py index           # 生成 index.html
  python3 build.py all             # meta + pages + index

设计原则：
  1. .md 是唯一事实源；index.html / *.html 都是产物，不手改
  2. 无参数 -> 不执行任何写操作（只打印用法），避免误跑覆盖
  3. 移动优先：详情页与首页均以 390px 为第一优先级设计
"""
import argparse
import html
import json
import os
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
GAMES = BASE / 'games'
DATA = BASE / '_data'

CATEGORIES = [
    ('icebreaker',      '🧊', '破冰热场',   '#38bdf8', '#0ea5e9'),
    ('communication',   '💬', '沟通表达',   '#a78bfa', '#7c3aed'),
    ('collaboration',   '🤝', '团队协作',   '#34d399', '#059669'),
    ('trust',           '🫱', '信任建立',   '#fbbf24', '#d97706'),
    ('leadership',      '👑', '领导力',     '#f87171', '#dc2626'),
    ('creativity',      '💡', '创意激发',   '#f472b6', '#db2777'),
    ('problem-solving', '🔧', '问题解决',   '#22d3ee', '#0891b2'),
    ('jubensha',        '🎭', '剧本杀改编', '#c084fc', '#9333ea'),
    ('variety',         '📺', '综艺娱乐',   '#fb923c', '#ea580c'),
    ('boardgame',       '🎲', '桌游团建',   '#94a3b8', '#475569'),
]
CAT_MAP = {c[0]: c for c in CATEGORIES}
TOTAL_GAMES = 0


# ────────────────────────────────────────────────────────────
# 1. Markdown 渲染（行内 + 块级，零依赖，正确性优先）
# ────────────────────────────────────────────────────────────

def strip_frontmatter(text):
    """剥离 YAML front matter，返回 (meta_dict, body)"""
    meta = {}
    if text.startswith('---'):
        end = text.find('\n---', 3)
        if end != -1:
            raw = text[3:end]
            for line in raw.split('\n'):
                if ':' in line and not line.strip().startswith('#'):
                    k, v = line.split(':', 1)
                    meta[k.strip()] = v.strip().strip('"').strip("'")
            body = text[end + 4:]
            return meta, body.lstrip('\n')
    return meta, text


def inline(t):
    """行内元素：code > bold > italic > link > strikethrough"""
    # 先保护行内代码
    codes = []

    def stash(m):
        codes.append(m.group(1))
        return f'\x00{len(codes) - 1}\x00'

    t = re.sub(r'`([^`]+)`', stash, t)
    t = html.escape(t, quote=False)
    # 图片 ![alt](src) 必须先于链接处理，否则会残留一个孤立的 !
    t = re.sub(r'!\[([^\]]*)\]\(([^)\s]+)\)',
               lambda m: (f'<img src="{m.group(2)}" alt="{m.group(1)}" '
                          f'loading="lazy" decoding="async">'), t)
    # 链接 [text](url)
    t = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)',
               lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', t)
    # 裸链接
    t = re.sub(r'(?<!["\'=])(https?://[^\s<）)]+)',
               lambda m: f'<a href="{m.group(1)}">{m.group(1)}</a>', t)
    # 加粗 / 斜体 / 删除线
    t = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', r'<em>\1</em>', t)
    t = re.sub(r'~~([^~]+)~~', r'<del>\1</del>', t)
    # 还原代码
    for i, c in enumerate(codes):
        t = t.replace(f'\x00{i}\x00', f'<code>{html.escape(c)}</code>')
    return t


def slugify_anchor(s):
    return re.sub(r'[^\w\u4e00-\u9fff-]+', '-', s).strip('-').lower()


def fix_links(html_text, out_path):
    """把正文里的相对链接修正到真实位置：
    md 里的 ../toolbox/x.md 是按 games/ 这一层写的，页面实际在 games/<cat>/，
    直接引用会 404；这里统一解析成相对 out_path 的正确路径。
    另外把历史遗留的绝对站内 URL 也降级成相对链接，避免域名迁移后整片失效。"""
    out_dir = out_path.parent

    def repo_rel(href):
        """把 https://<旧域名>/teambuilding/xxx.html 还原成仓库内相对路径"""
        for host in ('ai.aitboy.cn', 'aiworkdb.github.io'):
            for scheme in ('https://', 'http://'):
                pre = f'{scheme}{host}/teambuilding/'
                if href.startswith(pre):
                    return href[len(pre):]
        return None

    def repl(m):
        attr, quote, href = m.group(1), m.group(2), m.group(3)
        legacy = repo_rel(href)
        if legacy:
            href = legacy          # 落到下面的相对解析逻辑里统一处理
        elif href.startswith(('http://', 'https://', '#', 'mailto:', 'data:', '/', 'tel:')):
            return m.group(0)
        raw = href.split('#')[0]
        anchor = ('#' + href.split('#', 1)[1]) if '#' in href else ''
        html_form = re.sub(r'\.md$', '.html', raw)

        def emit(p):
            rel = os.path.relpath(p, out_dir).replace(os.sep, '/')
            if not rel.startswith('.'):
                rel = './' + rel
            return f'{attr}={quote}{rel}{anchor}{quote}'

        # 1) 相对当前输出目录（已经写对了）
        for cand in (out_dir / raw, out_dir / html_form):
            if path_exists(cand):
                return f'{attr}={quote}{raw if cand is out_dir / raw else html_form}{anchor}{quote}'

        # 2) 按仓库根解析（md 里的 ../ 是按 games/ 这一层写的）
        logical = re.sub(r'^(\.\./)+', '', raw).lstrip('./')
        for cand_rel in (re.sub(r'\.md$', '.html', logical), logical):
            cand = BASE / cand_rel
            if path_exists(cand):
                return emit(cand)

        # 3) 兜底：仓库内同名文件（唯一命中才用）
        for name in {Path(html_form).name, Path(raw).name}:
            hits = [p for p in BASE.rglob(name)
                    if 'wechat' not in p.parts and p.is_file()]
            if len(hits) == 1:
                return emit(hits[0])

        BROKEN.append(f'{out_path} -> {href}')
        return f'{attr}={quote}{raw}{anchor}{quote}'

    return re.sub(r'(href|src)=(["\'])([^"\']+)\2', repl, html_text)


def li_text(content):
    """列表项渲染：把 `- [ ]` / `- [x]` 转成真正的勾选方块，而不是裸的方括号"""
    m = re.match(r'^\[([ xX])\]\s*(.*)$', content)
    if m:
        glyph = '☑' if m.group(1).lower() == 'x' else '☐'
        return f'<span class="ck">{glyph}</span> ' + inline(m.group(2))
    return inline(content)


BROKEN = []

# 本次构建「将要写出」的文件（相对 BASE，'/' 分隔）。
# 用途：同批次新页面在渲染时还没落盘，fix_links 若只看磁盘会把它误判成死链。
# 干净构建 vs 增量构建的结果必须一致，否则 CI 每次构建结果不同。
PENDING = set()


def path_exists(p):
    """文件存在 —— 除了磁盘上的，还要认「本次构建将要写出」的。"""
    if p.exists():
        return True
    try:
        rel = p.resolve().relative_to(BASE.resolve())
    except (ValueError, OSError):
        return False
    return rel.as_posix() in PENDING


def render_markdown(body, with_toc=False):
    """返回 (html, toc_list)"""
    lines = body.split('\n')
    out, toc = [], []
    i, n = 0, len(lines)

    def flush_table(rows, align_hint=None):
        if not rows:
            return ''
        KV_HEADS = {('项目', '内容'), ('属性', '说明'), ('字段', '值'),
                    ('项目', '说明'), ('名称', '说明'), ('属性', '内容'),
                    ('项', '内容'), ('维度', '说明')}
        # 0) 若首行是「项目/内容」这类表头，先剥掉，避免它变成一条无意义的记录
        head2 = tuple(re.sub(r'\*\*|\s', '', c) for c in rows[0][:2]) \
            if len(rows[0]) == 2 else None
        if head2 in KV_HEADS:
            rows = rows[1:]
            if not rows:
                return ''
        # 1) 键值表：列数全为 2，且首列是短标签
        #    单行也算 —— 元信息表被 strip_body_dupes 滤到只剩「主题/能量等级」这类一行时，
        #    按表头渲染会变成一个只有 thead、tbody 全空的假表格（24 个详情页踩过）
        kv_like = all(len(r) == 2 for r in rows) and all(
            re.match(r'^\s*(\*\*)?[^*|]{1,12}(\*\*)?\s*$', r[0] or '') for r in rows
        )
        if kv_like:
            cells = []
            for r in rows:
                k = re.sub(r'\*\*', '', r[0]).strip()
                v = r[1].strip()
                cells.append(
                    f'<div class="kv"><div class="kv-k">{inline(k)}</div>'
                    f'<div class="kv-v">{inline(v)}</div></div>')
            return '<div class="kv-grid">' + ''.join(cells) + '</div>'

        # 2) 标准表格：首行为表头
        head, bodyrows = rows[0], rows[1:]
        ncol = len(head)
        cls = ' class="wide"' if ncol >= 3 else ''
        th = ''.join(f'<th>{inline(c)}</th>' for c in head)
        trs = ''.join(
            '<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in r) + '</tr>'
            for r in bodyrows) if bodyrows else ''
        return ('<div class="tw"><div class="table-wrap"><table' + cls +
                '><thead><tr>' + th + '</tr></thead><tbody>' + trs +
                '</tbody></table></div></div>')

    while i < n:
        line = lines[i]
        s = line.strip()

        # 代码块
        if s.startswith('```'):
            i += 1
            buf = []
            while i < n and not lines[i].strip().startswith('```'):
                buf.append(html.escape(lines[i]))
                i += 1
            i += 1
            out.append('<pre><code>' + '\n'.join(buf) + '</code></pre>')
            continue

        # 表格
        if s.startswith('|') and s.count('|') >= 2:
            rows = []
            while i < n and lines[i].strip().startswith('|'):
                raw = lines[i].strip()
                if not re.match(r'^\|[\s:|-]+\|?$', raw):
                    cells = [c.strip() for c in raw.strip('|').split('|')]
                    rows.append(cells)
                i += 1
            out.append(flush_table(rows))
            continue

        # 标题
        m = re.match(r'^(#{1,6})\s+(.*)$', s)
        if m:
            lvl, txt = len(m.group(1)), m.group(2).strip()
            if lvl == 1:
                out.append(f'<h1>{inline(txt)}</h1>')
            else:
                aid = slugify_anchor(txt)
                if lvl <= 3:
                    toc.append((lvl, txt, aid))
                out.append(f'<h{lvl} id="{aid}">{inline(txt)}</h{lvl}>')
            i += 1
            continue

        # 分隔线
        if re.match(r'^---+$', s):
            out.append('<hr>')
            i += 1
            continue

        # 引用
        if s.startswith('>'):
            buf = []
            started = i
            while i < n and lines[i].strip().startswith('>'):
                buf.append(lines[i].strip().lstrip('>').strip())
                i += 1
            quote = ' '.join(buf)
            # 与页面顶部导语重复的「一句话」不再渲染第二遍
            if re.match(r'^\*\*(一句话|核心目标|一句话简介)\*\*\s*[：:]', quote):
                continue
            # 多行引用保留换行（多是「适用场景／时长／人数」这类分行信息，用空格拼会糊成一段）
            parts = [inline(x) for x in buf if x]
            out.append('<blockquote>' + '<br>'.join(parts) + '</blockquote>')
            continue

        # 列表（支持嵌套一层）
        if re.match(r'^([-*+]|\d+\.)\s', s):
            ordered = bool(re.match(r'^\d+\.', s))
            items, depth_stack = [], 0
            while i < n:
                cur = lines[i]
                cs = cur.strip()
                indent = len(cur) - len(cur.lstrip(' '))
                mm = re.match(r'^([-*+]|\d+\.)\s+(.*)$', cs)
                if not mm:
                    if cs == '':
                        # 空行后若还是列表项则继续
                        if i + 1 < n and re.match(r'^\s*([-*+]|\d+\.)\s', lines[i + 1]):
                            i += 1
                            continue
                        break
                    break
                content = mm.group(2)
                sub = indent >= 2
                if sub:
                    items.append(('<sub>', content))
                else:
                    items.append(('<li>', content))
                i += 1
            tag = 'ol' if ordered else 'ul'
            buf = [f'<{tag}>']
            in_sub = False
            for kind, content in items:
                if kind == '<sub>':
                    if not in_sub:
                        buf.append('<ul class="sub">')
                        in_sub = True
                    buf.append(f'<li>{li_text(content)}</li>')
                else:
                    if in_sub:
                        buf.append('</ul>')
                        in_sub = False
                    buf.append(f'<li>{li_text(content)}</li>')
            if in_sub:
                buf.append('</ul>')
            buf.append(f'</{tag}>')
            out.append(''.join(buf))
            continue

        # 普通段落
        if s:
            buf = []
            while i < n and lines[i].strip() and not re.match(
                    r'^(#{1,6}\s|\||```|>|[-*+]\s|\d+\.\s|---+$)', lines[i].strip()):
                buf.append(lines[i].strip())
                i += 1
            out.append('<p>' + inline(' '.join(buf)) + '</p>')
            continue

        i += 1

    return '\n'.join(out), toc


# ────────────────────────────────────────────────────────────
# 2. 元数据提取
# ────────────────────────────────────────────────────────────

DUR_KEYS = ['团建总时长', '游戏时长', '时长', '总时长', '单局时长', '时间']
# 桌游类：本体时长与团建总时长是两回事，后者才是「实际要占多久」
BASE_DUR_KEYS = ['桌游本体时长']
PEOPLE_KEYS = ['团建人数', '人数', '玩家人数', '参与人数', '建议人数', '团队规模', '适合人数']
VENUE_KEYS = ['场地', '场景标签', '形式标签', '场合', '适合场景', '适用场景']
DIFF_KEYS = ['难度', '上手难度']
PROP_KEYS = ['道具需求', '道具', '物资', '道具准备']


def table_pairs(txt):
    """收集全文所有 2 列表格的 (标签, 值) 对，跨三种文档格式通用"""
    pairs = []
    for line in txt.split('\n'):
        s = line.strip()
        if not s.startswith('|'):
            continue
        cells = [c.strip() for c in s.strip('|').split('|')]
        if len(cells) != 2:
            continue
        if re.match(r'^[\s:|-]+$', s.strip('|')):
            continue
        k = re.sub(r'\*\*|__', '', cells[0]).strip().rstrip('：:').strip()
        v = cells[1].strip()
        if k and v:
            pairs.append((k, v))
    return pairs


# 这些词出现在「值」的位置，说明抓到的是表头而不是数据
HEADER_VALS = {'数量', '说明', '备注', '值', '内容', '用途', '用量', '单位', '序号'}


def parse_total_people(ppl_raw):
    """从「（全场 12–40 人）」里解析全场上限，返回 (min, max) 或 None。

    人数有两种口径：每组人数（怎么分组）和全场上限（我能带多少人去）。
    筛选用前者，决定要不要带人用后者，页面两个都要给。
    """
    m = re.search(r'全场\s*(\d+)\s*[–\-~]?\s*(\d*)\s*人', ppl_raw or '')
    if not m:
        return None
    lo = int(m.group(1))
    hi = int(m.group(2)) if m.group(2) else lo
    return (min(lo, hi), max(lo, hi))


def detect_unit(ppl_raw):
    """判断人数口径：group=每组人数（可多组并行）/ total=全场总人数。

    坑：「20-40人（分4-6人/队，至少4队）」的主数字是全场 20-40，
    不能因为串里出现了「/队」就当成每组人数。
    """
    s = re.sub(r'^(?:建议|推荐)\s*', '', (ppl_raw or '').strip())
    m = re.match(r'^\s*(\d+)\s*[–\-~]?\s*(\d*)\s*人\s*(.*)$', s)
    if m:
        # 主数字紧跟「/组 /队 /桌 /公司」→ 分组口径。
        # 括号里的说明不算：「8–30 人（2–6 队，每队 3–10 人）」主数字是全场。
        tail = (m.group(3) or '')[:8]
        if re.match(r'^/\s*(组|队|桌|公司)', tail):
            return 'group'
        return 'total'
    # 「每组 6–20 人」这种：数字前面带量词
    if re.match(r'^\s*每\s*(组|队|桌|公司|摊|场)', s):
        return 'group'
    return 'total'


def field(pairs, keys):
    """先精确匹配再后缀匹配——「团建人数」优先于「桌游库人数」"""
    for key in keys:
        for k, v in pairs:
            if k == key and v not in HEADER_VALS:
                return v
    for k, v in pairs:
        if v in HEADER_VALS:
            continue
        for key in keys:
            if k.endswith(key) and len(k) <= len(key) + 4:
                return v
    return ''


def parse_minutes(s, default=(20, 40)):
    """从时长文案解析 (min, max)。只取前两个数字，避开「含15-20分钟复盘」"""
    if not s:
        return default
    nums = [int(x) for x in re.findall(r'\d+', s)]
    if not nums:
        return default
    if len(nums) >= 2:
        a, b = nums[0], nums[1]
        return (min(a, b), max(a, b))
    return (nums[0], nums[0])


def parse_stars(s):
    """难度文案 -> 1~3 星"""
    if not s:
        return 2
    n = s.count('⭐')
    if n:
        return max(1, min(3, n))
    if re.search(r'简单|容易|零门槛|低门槛|轻松', s):
        return 1
    if re.search(r'困难|高难|挑战|硬核|复杂', s):
        return 3
    return 2


def parse_people(s):
    """返回 (min, max, raw_label)"""
    if not s:
        return (0, 0, '不限')
    if re.search(r'任意|不限|无限制', s):
        # 「任意人数（建议 8–50 人）」：下限用建议值，否则会解析成 0–50，
        # 首页显示「0 人」，筛选也失去意义。
        m = re.search(r'(\d+)\s*[–\-~]\s*(\d+)', s)
        if m:
            return (int(m.group(1)), int(m.group(2)), s)
        return (0, 0, '不限')
    nums = [int(x) for x in re.findall(r'\d+', s)]
    if not nums:
        return (0, 0, s)
    if len(nums) >= 2:
        return (min(nums[0], nums[1]), max(nums[0], nums[1]), s)
    return (nums[0], nums[0], s)


def parse_ability(txt):
    """从「团建核心价值 / 核心学习目标」小节抽 3 个短标签"""
    m = re.search(r'(团建核心价值|核心学习目标|核心价值)[^\n]*\n', txt)
    if not m:
        return []
    rest = txt[m.end():]
    end = re.search(r'^##\s', rest, re.M)
    seg = rest[:end.start()] if end else rest[:800]
    out = []
    for line in seg.split('\n'):
        mm = re.match(r'^[-*+]\s+(.+)$', line.strip())
        if not mm:
            continue
        item = re.sub(r'^[^\w\u4e00-\u9fff]+', '', mm.group(1))
        item = item.replace('**', '')
        tag = re.split(r'[：:]', item, maxsplit=1)[0].strip()
        tag = re.sub(r'^[^\w\u4e00-\u9fff]+', '', tag)
        if 2 <= len(tag) <= 12 and tag not in out:
            out.append(tag)
    return out[:3]


def parse_summary(txt, name, pairs=None, abilities=None):
    """一句话简介，按可信度依次取：
    1) 信息表里的「核心目标 / 一句话简介」字段
    2) 「核心目标：」行内写法
    3) 「游戏概述 / 简介 / 背景」小节首段
    4) 任意非列表、非规则句的段落
    5) 兜底：用能力标签拼一句（不编造内容）
    """
    pairs = pairs or []
    raw = ''

    if pairs:
        for key in ('核心目标', '核心价值', '一句话简介', '一句话', '游戏简介', '简介'):
            v = field(pairs, [key])
            if v and len(v) >= 8:
                raw = v
                break

    if not raw:
        m = re.search(r'\*\*核心目标\*\*\s*[：:]\s*([^\n]+)', txt)
        if m:
            raw = m.group(1)

    if not raw:
        # 概述类小节的首段
        m = re.search(r'^#{2,3}\s*[^\n]*(概述|简介|背景|关于本游戏)[^\n]*\n(.+?)(?=\n#{2,3}\s|\Z)',
                      txt, re.S | re.M)
        if m:
            for para in m.group(2).split('\n'):
                p = para.strip()
                if p and not re.match(r'^[|\->*#`]', p) and len(p) >= 20:
                    raw = p
                    break

    if not raw:
        # 引言行 `> **一句话**：…`
        m = re.search(r'^>\s*\*\*(?:一句话|核心目标|一句话简介)\*\*\s*[：:]\s*([^\n]+)',
                      txt, re.M)
        if m:
            raw = m.group(1)

    def usable(s):
        """排除规则步骤、列表项、标题残片、改造说明"""
        if not s or len(s) < 8:
            return False
        if re.match(r'^[\d０-９]+\s*[.、)）]', s):      # 1. 2. 3. 步骤
            return False
        if re.match(r'^[（(]?\d+[）)]', s):
            return False
        if re.match(r'^(准备|流程|道具|物资|分组|规则|步骤|玩法|角色|时长|人数|'
                    r'原版|原规则|原作|本游戏|改造|本节|下面|以上|注：|说明：)', s):
            return False
        if re.match(r'^[|\->*#`_~]', s):
            return False
        if s.count('|') >= 2:
            return False
        return True

    if not usable(raw):
        raw = ''
        for line in txt.split('\n'):
            s = line.strip()
            if usable(s) and name[:6] not in s:
                raw = s
                break

    if raw:
        s = re.sub(r'\*\*|`', '', raw).strip().rstrip('，,、')
        if len(s) > 78:
            # 优先整句收口；无句号则硬截并加省略号，绝不以逗号结尾
            m2 = re.search(r'^.{20,78}?[。！？]', s)
            s = m2.group(0) if m2 else s[:74].rstrip('，,、；;') + '…'
        return s.strip()

    if abilities:
        return '训练 ' + '、'.join(abilities[:3]) + '。'
    return ''


def load_game(md_path):
    txt = md_path.read_text(encoding='utf-8')
    meta, body = strip_frontmatter(txt)

    m = re.search(r'^#\s+(.+)$', body, re.M)
    name = (m.group(1).strip() if m else meta.get('title', md_path.stem))
    name = re.sub(r'\*\*', '', name).strip()

    # 英文名（括号内）
    en = ''
    mm = re.search(r'[（(]([A-Za-z][A-Za-z\s:\'’\-]+)[）)]', name)
    if mm:
        en = mm.group(1).strip()

    cat = md_path.parent.name
    cinfo = CAT_MAP.get(cat, (cat, '🎲', cat, '#94a3b8', '#475569'))

    pairs = table_pairs(txt)
    dur_raw = field(pairs, DUR_KEYS)
    base_dur_raw = field(pairs, BASE_DUR_KEYS)
    ppl_raw = field(pairs, PEOPLE_KEYS)
    total_ppl = parse_total_people(ppl_raw)
    venue_raw = field(pairs, VENUE_KEYS)
    diff_raw = field(pairs, DIFF_KEYS)
    prop_raw = field(pairs, PROP_KEYS)
    abilities = parse_ability(body)

    dmin, dmax = parse_minutes(dur_raw)
    pmin, pmax, plabel = parse_people(ppl_raw)
    # 人数口径：多数游戏写的是「每组 N-M 人」，多组可并行，总人数上限远大于组规模。
    # 注意「20-40人（分4-6人/队）」这类写法主数字是全场，不能被后面的「/队」带偏。
    unit = detect_unit(ppl_raw)

    # 场地
    venue, vkey = detect_venue(venue_raw, txt)

    stars = parse_stars(diff_raw)

    return {
        'slug': md_path.stem,
        'cat': cat,
        'cat_name': cinfo[2],
        'cat_icon': cinfo[1],
        'name': name,
        'en': en,
        'summary': parse_summary(body, name, pairs, abilities),
        'duration_raw': dur_raw,
        'base_duration_raw': base_dur_raw,
        'total_ppl': list(total_ppl) if total_ppl else None,
        'dmin': dmin,
        'dmax': dmax,
        'people_raw': ppl_raw,
        'pmin': pmin,
        'pmax': pmax,
        'unit': unit,
        'venue': venue,
        'vkey': vkey,
        'stars': stars,
        'props': prop_raw,
        'abilities': abilities,
        'md': str(md_path.relative_to(BASE)),
        'html': str(md_path.with_suffix('.html').relative_to(BASE)),
        'words': len(txt),
    }


def cmd_meta():
    if not DATA.exists():
        DATA.mkdir()
    games = []
    for cat_id, *_ in CATEGORIES:
        d = GAMES / cat_id
        if not d.exists():
            continue
        for md in sorted(d.glob('*.md')):
            games.append(load_game(md))

    (DATA / 'games.json').write_text(
        json.dumps(games, ensure_ascii=False, indent=1), encoding='utf-8')

    # 诊断
    print(f"{'游戏':26s} {'时长':>10s} {'人数':>12s} {'场地':6s} {'简介':4s} 能力")
    print('-' * 96)
    bad_sum, bad_ab = 0, 0
    for g in games:
        ds = f'{g["dmin"]}-{g["dmax"]}'
        ps = '不限' if g['pmax'] == 0 else f'{g["pmin"]}-{g["pmax"]}'
        s_flag = 'OK' if len(g['summary']) > 8 else '缺!'
        a_flag = str(len(g['abilities']))
        if s_flag == '缺!':
            bad_sum += 1
        if not g['abilities']:
            bad_ab += 1
        print(f'{g["name"][:24]:26s} {ds:>10s} {ps:>12s} {g["venue"]:6s} '
              f'{len(g["summary"]):>3d}{s_flag if s_flag=="缺!" else "  "} '
              f'{"·".join(g["abilities"])}')

    print('-' * 96)
    print(f'共 {len(games)} 款 | 缺简介 {bad_sum} | 缺能力标签 {bad_ab}')
    from collections import Counter
    cc = Counter(g['cat_name'] for g in games)
    print('分类分布：' + '  '.join(f'{k}{v}' for k, v in cc.items()))
    print(f'已写入 {DATA / "games.json"}')


def fmt_dur(g):
    a, b = g['dmin'], g['dmax']
    return f'{a} 分钟' if a == b else f'{a}–{b} 分钟'


def fmt_people(g):
    a, b, u = g['pmin'], g['pmax'], g.get('unit', 'total')
    suffix = '/组' if u == 'group' else ''
    if b == 0:
        return '不限人数'
    if a == 0:
        return f'≤ {b} 人' + suffix
    return (f'{a}–{b} 人{suffix}' if a != b else f'{a} 人{suffix}')


# ────────────────────────────────────────────────────────────
# 3. 详情页
# ────────────────────────────────────────────────────────────

PAGE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="{a2}">
<meta name="description" content="{desc}">
<title>{name} · 团建游戏库</title>
<link rel="stylesheet" href="../../assets/lib.css">
<link rel="manifest" href="../../manifest.webmanifest">
<link rel="apple-touch-icon" href="../../assets/icon-192.png">
<style>:root{{--accent:{a1};--accent-ink:{a2};--accent-bg:{a3};}}</style>
</head>
<body>

<header class="topbar">
  <a class="topbar-btn" href="../../index.html" aria-label="返回游戏库">←</a>
  <div class="topbar-title" id="tbar">{name}</div>
  <button class="topbar-btn" id="share" aria-label="分享">↗</button>
</header>

<section class="hero" style="--a1:{a1};--a2:{a2};">
  <span class="hero-cat">{cat_icon} {cat_name}</span>
  <h1>{name}</h1>
  {en_html}
  {lede_html}
</section>

<div class="facts">
  <div class="fact"><div class="fact-k">⏱ 时长</div><div class="fact-v">{dur}{base_dur_html}</div></div>
  <div class="fact"><div class="fact-k">👥 人数</div><div class="fact-v">{people}{total_ppl_html}</div></div>
  <div class="fact"><div class="fact-k">📍 场地</div><div class="fact-v">{venue}</div></div>
  <div class="fact"><div class="fact-k">📊 难度</div><div class="fact-v">{stars}</div></div>
  {prop_fact}
</div>

{abil_html}
{toc_html}
<article class="doc">
{body}
</article>

<nav class="pager">
  {prev}
  {next}
</nav>

{rel_html}

<footer class="foot">
  <div>{cat_icon} {cat_name} · 第 {idx} / {total} 款</div>
  <div><a href="../../index.html">返回全部 {total_all} 款游戏</a></div>
  <div style="margin-top:6px;opacity:.75">规则与时长以原文档为准，现场执行前请核对场地与道具。</div>
</footer>

<script>
(function(){{
  var t=document.getElementById('tbar'),h=document.querySelector('.hero');
  if(t&&h&&'IntersectionObserver'in window){{
    new IntersectionObserver(function(e){{t.classList.toggle('on',!e[0].isIntersecting);}},
      {{rootMargin:'-56px 0px 0px 0px'}}).observe(h);
  }}
  var s=document.getElementById('share');
  if(s)s.addEventListener('click',function(){{
    var d={{title:document.title,url:location.href}};
    if(navigator.share){{navigator.share(d).catch(function(){{}});}}
    else if(navigator.clipboard){{navigator.clipboard.writeText(location.href)
      .then(function(){{s.textContent='✓';setTimeout(function(){{s.textContent='↗';}},1200);}});}}
  }});
  // 仅当表格真的溢出时才提示可横滑
  function markTables(){{
    document.querySelectorAll('.tw').forEach(function(w){{
      var box=w.querySelector('.table-wrap');
      if(!box)return;
      w.classList.toggle('scrollable', box.scrollWidth - box.clientWidth > 4);
    }});
  }}
  markTables();
  window.addEventListener('resize',markTables,{{passive:true}});
}})();
</script>
</body>
</html>'''


HERO_KEYS = set(DUR_KEYS + BASE_DUR_KEYS + PEOPLE_KEYS + VENUE_KEYS
                + DIFF_KEYS + PROP_KEYS)


def _norm(s):
    return re.sub(r'[\s，。、；：「」『』（）()【】!！?？…—\-·]', '', s or '')


def strip_body_dupes(body_md, g):
    """去掉正文里和页面顶部重复的信息：
    顶部 facts 已显示 时长/人数/场地/难度/道具，hero 已显示一句话导语，
    正文开头那张元信息表和「核心目标」段落就是重复的。"""
    lines = body_md.split('\n')
    out, i, n = [], 0, len(lines)
    while i < n:
        s = lines[i].strip()
        if s.startswith('|'):
            j = i
            while j < n and lines[j].strip().startswith('|'):
                j += 1
            keep = []
            for r in lines[i:j]:
                cells = [c.strip() for c in r.strip().strip('|').split('|')]
                if len(cells) == 2:
                    k = re.sub(r'\*\*|\s', '', cells[0])
                    if k in HERO_KEYS:
                        continue
                keep.append(r)
            has_data = any(not re.match(r'^\|[\s:|-]+\|$', r.strip()) for r in keep)
            if keep and has_data:
                out.extend(keep)
            i = j
            continue
        out.append(lines[i])
        i += 1

    body_md = '\n'.join(out)

    # 去掉与导语重复的「核心目标」段落
    summ = _norm(g.get('summary') or '')
    if summ:
        body_md = re.sub(
            r'^\s*\*\*(?:核心目标|一句话|一句话简介)\*\*\s*[：:][^\n]*\n?',
            lambda m: '' if summ in _norm(m.group(0)) or _norm(m.group(0)) in summ else m.group(0),
            body_md, count=1, flags=re.M)
    return re.sub(r'\n{3,}', '\n\n', strip_leading_title(body_md))


def strip_leading_title(body_md):
    """页面顶部 hero 已显示标题，正文里的 # 大标题与紧跟的分隔线是重复的"""
    body_md = body_md.lstrip('\n')
    body_md = re.sub(r'^#\s+[^\n]*\n', '', body_md, count=1)
    body_md = body_md.lstrip('\n')
    body_md = re.sub(r'^(?:[ \t]*-{3,}[ \t]*\n)+', '', body_md)
    return body_md.lstrip('\n')


def build_page(g, prev_g, next_g, related, idx, total):
    md_path = BASE / g['md']
    txt = md_path.read_text(encoding='utf-8')
    _, body_md = strip_frontmatter(txt)
    body_md = strip_body_dupes(body_md, g)
    body, toc = render_markdown(body_md)

    c = CAT_MAP.get(g['cat'], ('', '🎲', g['cat'], '#0d9488', '#0f766e'))
    a1, a2 = c[3], c[4]
    a3 = a1 + '1f'

    en_html = (f'<div class="hero-en">{html.escape(g["en"])}</div>'
               if g['en'] and g['en'].lower() not in g['name'].lower() else '')
    lede_html = (f'<p class="hero-lede">{html.escape(g["summary"])}</p>'
                 if g['summary'] else '')

    abil_html = ''
    if g['abilities']:
        chips = ''.join(f'<span class="ab">{html.escape(a)}</span>' for a in g['abilities'])
        abil_html = f'<div class="abilities">{chips}</div>'

    # 目录：h2 全收，h3 仅在数量不多时收
    toc_html = ''
    h2s = [t for t in toc if t[0] == 2]
    h3s = [t for t in toc if t[0] == 3]
    entries = h2s + (h3s if len(h3s) <= 8 else [])
    if len(entries) >= 3:
        lis = ''.join(
            f'<li class="lv{lvl}"><a href="#{aid}">{html.escape(txt_)}</a></li>'
            for lvl, txt_, aid in entries)
        toc_html = ('<div class="toc"><details><summary>📑 本页目录'
                    f'（{len(entries)} 节）</summary><ol>{lis}</ol></details></div>')

    def pager_item(x, arrow, label, cls):
        if not x:
            return f'<a class="{cls} disabled" href="#"><span>{label}</span><div class="p-title">—</div></a>'
        return (f'<a class="{cls}" href="{Path(x["html"]).name}">'
                f'<span>{label} {arrow}</span>'
                f'<div class="p-title">{html.escape(x["name"])}</div></a>')

    rel_html = ''
    if related:
        items = ''.join(
            f'<a class="rel" href="{Path(r["html"]).name}">'
            f'<span class="r-ico">{r["cat_icon"]}</span>'
            f'<span class="r-body"><span class="r-name">{html.escape(r["name"])}</span>'
            f'<span class="r-meta">{fmt_dur(r)} · {fmt_people(r)}</span></span>'
            f'<span class="r-go">›</span></a>' for r in related)
        rel_html = (f'<div class="related"><h2>🔗 同类推荐</h2>'
                    f'<div class="rel-list">{items}</div></div>')

    # 道具字段里可能带 md 链接（旧文档写法），facts 里只保留文字
    props_txt = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', g.get('props') or '')
    prop_fact = (f'<div class="fact fact-wide"><div class="fact-k">🧰 道具</div>'
                 f'<div class="fact-v">{html.escape(props_txt)}</div></div>'
                 if props_txt else '')
    tp = g.get('total_ppl')
    if tp:
        ttxt = (f'{tp[0]}–{tp[1]} 人' if tp[0] != tp[1] else f'{tp[0]} 人')
        total_ppl_html = f'<small>全场 {html.escape(ttxt)}</small>'
    else:
        total_ppl_html = ''
    base_raw = (g.get('base_duration_raw') or '').strip()
    if base_raw:
        btxt = re.sub(r'\s*min\s*$', '', base_raw).strip()
        base_dur_html = (f'<small>桌游本体 {html.escape(btxt)} 分钟</small>')
    else:
        base_dur_html = ''
    desc = html.escape((g['summary'] or g['name'])[:110])
    page = PAGE.format(
        name=html.escape(g['name']),
        desc=desc,
        a1=a1, a2=a2, a3=a3,
        cat_icon=g['cat_icon'], cat_name=g['cat_name'],
        en_html=en_html, lede_html=lede_html,
        dur=fmt_dur(g), people=fmt_people(g), venue=g['venue'],
        stars='★' * g['stars'] + '☆' * (3 - g['stars']),
        prop_fact=prop_fact,
        base_dur_html=base_dur_html,
        total_ppl_html=total_ppl_html,
        abil_html=abil_html, toc_html=toc_html, body=body,
        prev=pager_item(prev_g, '←', '上一个', 'prev'),
        next=pager_item(next_g, '→', '下一个', 'next'),
        rel_html=rel_html, idx=idx, total=total,
        total_all=TOTAL_GAMES,
    )
    return fix_links(page, BASE / g['html'])


def cmd_pages():
    global TOTAL_GAMES
    games = json.loads((DATA / 'games.json').read_text(encoding='utf-8'))
    TOTAL_GAMES = len(games)
    by_cat = {}
    for g in games:
        by_cat.setdefault(g['cat'], []).append(g)
    for v in by_cat.values():
        v.sort(key=lambda x: x['name'])

    # 先全部渲染到内存，最后统一落盘 —— 否则 A 页的相关推荐指向还没写出的 B 页时，
    # fix_links 会把 B 误判成死链。
    # 同时登记 PENDING：即使磁盘上还没有这些文件，也算「存在」。
    for g in games:
        register_pending(BASE / g['html'])
    register_pending(BASE / 'index.html')
    rendered = []
    for cat, lst in by_cat.items():
        for i, g in enumerate(lst):
            prev_g = lst[i - 1] if i > 0 else None
            nxt = lst[i + 1] if i < len(lst) - 1 else None
            # 相关推荐：同分类、共享能力标签最多
            others = [o for o in lst if o['slug'] != g['slug']]
            others.sort(key=lambda o: -len(set(o['abilities']) & set(g['abilities'])))
            out = build_page(g, prev_g, nxt, others[:4], i + 1, len(lst))
            rendered.append((BASE / g['html'], out))
    for path, out in rendered:
        path.write_text(out, encoding='utf-8')
    print(f'[pages] 已生成 {len(rendered)} 个详情页')


FLOWS = [
    ('flows/one-day/01-schedule.html', '📅', '一日团建模板',
     '6–8 小时 · 15–50 人 · 破冰 + 协作 + 复盘完整闭环'),
    ('flows/half-day/01-schedule.html', '⏱️', '半日团建模板',
     '3–4 小时 · 10–30 人 · 快速凝聚，适合周五下午'),
    ('flows/workshop/leadership-awakening.html', '🎓', '主题工作坊：领导力觉醒',
     '2.5–3 小时 · 12–24 人 · 深度引导，非娱乐向'),
    ('flows/cross-dept/01-schedule.html', '🤝', '跨部门协作方案',
     '半天 · 20–40 人 · 打散部门重组，专治部门墙'),
    ('flows/onboarding/01-schedule.html', '🌱', '新人融入方案',
     '2–3 小时 · 6–20 人 · 让新人在第一个月被记住'),
    ('flows/online/01-schedule.html', '💻', '线上团建模板',
     '2–2.5 小时 · 8–30 人 · 远程团队，全程可在线完成'),
]

TOOLS = [
    ('toolbox/facilitation.html', '🗣️', '引导话术库', '开场白 / 规则讲解 / 介入干预模板'),
    ('toolbox/debrief.html', '🔍', '复盘引导框架', '4F 模型 + 提问清单 + 典型场景话术'),
    ('toolbox/safety.html', '🛡️', '安全与管理', '户外安全清单 / 突发预案 / 免责声明'),
    ('toolbox/checklist.html', '✅', '物资与效率', '通用物资清单 / 分组方法 / 评估问卷'),
]

INDEX = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#0b1120">
<meta name="description" content="{n_games} 款团建游戏库：按人数、时长、场地、团队能力四维筛选，含完整规则、引导要点与 4F 复盘框架，支持在线直接玩。">
<title>团建 &amp; 培训游戏库 · 按人数·时长·场地选游戏</title>
<link rel="stylesheet" href="assets/lib.css">
<link rel="stylesheet" href="assets/home.css">
<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="assets/icon-192.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
</head>
<body>

<header class="h-hero">
 <div class="h-hero-in">
  <h1>团建 &amp; 培训游戏库</h1>
  <p class="sub">先定团队要练什么，再选玩什么。<br>按人数、时长、场地筛选，每款含完整规则与复盘框架。</p>
  <div class="h-stats">
    <div><b>{n_games}</b><i>款游戏</i></div>
    <div><b>{n_cats}</b><i>个分类</i></div>
    <div><b>{n_flows}</b><i>套流程</i></div>
    <div><b>{n_online}</b><i>款在线可玩</i></div>
  </div>
  <div class="quick" id="quick">
    <button data-preset="ice">🧊 10 分钟破冰</button>
    <button data-preset="small">👥 30 人以内</button>
    <button data-preset="long">🕐 1 小时以上</button>
    <button data-preset="indoor">🏢 纯室内</button>
    <button data-preset="jubensha">🎭 剧本杀</button>
    <button data-preset="boardgame">🎲 桌游改编</button>
  </div>
  <a class="h-guide" href="guide.html">
    <span class="hg-ico">📖</span>
    <span class="hg-t"><b>第一次带团建？</b>读这份 5 分钟指南：怎么选、怎么带、怎么收</span>
    <span class="hg-a">›</span>
  </a>
 </div>
</header>

<div class="filters">
  <div class="f-inner">
    <div class="search">
      <span class="ico">🔍</span>
      <input id="q" type="search" placeholder="搜游戏名、能力标签、场景…" autocomplete="off" enterkeyhint="search">
      <button class="clr" id="clr" aria-label="清空">✕</button>
    </div>
    <div class="frow" id="f-ppl">
      <span class="lab">人数</span>
      <button data-v="">不限</button>
      <button data-v="u10">≤10</button>
      <button data-v="10-30">10–30</button>
      <button data-v="30-60">30–60</button>
      <button data-v="60p">60+</button>
    </div>
    <div class="frow" id="f-dur">
      <span class="lab">时长</span>
      <button data-v="">不限</button>
      <button data-v="d15">≤15 分</button>
      <button data-v="d30">15–30</button>
      <button data-v="d60">30–60</button>
      <button data-v="d120">60–120</button>
      <button data-v="d120p">120+</button>
    </div>
    <div class="f-more" id="f-more">
      <div class="frow" id="f-ven">
        <span class="lab">场地</span>
        <button data-v="">不限</button>
        <button data-v="indoor">室内</button>
        <button data-v="outdoor">户外</button>
        <button data-v="both">室内外都行</button>
      </div>
      <div class="frow" id="f-ab">
        <span class="lab">能力</span>
        <button data-v="">不限</button>
{ab_buttons}
      </div>
    </div>
    <button class="f-toggle" id="f-toggle" aria-expanded="false">更多筛选 ⌄</button>
    <div class="f-count">
      <span>共 <b id="hits">{n_games}</b> 款</span>
      <span id="hint"></span>
      <button class="reset" id="reset">清空条件</button>
    </div>
  </div>
</div>

<main class="h-main" id="list">
{cats_html}

<div class="empty" id="empty">
  <span class="e-ico">🫧</span>
  这个组合下暂时没有游戏。<br>试着放宽人数或时长，或<a href="#" id="relax">清空所有条件</a>。
</div>

<div class="blk" id="flows">
  <div class="blk-h">📋 团建流程方案</div>
  <div class="flow-list">
{flows_html}
  </div>
</div>

<div class="blk" id="toolbox">
  <div class="blk-h">🧰 教练工具箱</div>
  <div class="flow-list">
{tools_html}
  </div>
</div>

<div class="blk">
  <div class="blk-h">📱 在线直接玩</div>
  <a class="flow" href="play/index.html">
    <span class="f-ico">🎮</span>
    <span class="f-b">
      <span class="f-t">{n_online} 款在线游戏 + 教练工具</span>
      <span class="f-d">手机打开即用，无需下载。评分、计时、分组、方案生成器</span>
    </span>
    <span class="f-a">›</span>
  </a>
</div>

<footer class="h-foot">
  <div>共 {n_games} 款游戏 · 内容持续更新</div>
  <div style="margin-top:4px">
    <a href="guide.md">教练使用指南</a> ·
    <a href="https://github.com/aiworkdb/aiworkdb.github.io">GitHub</a>
  </div>
  <div style="margin-top:6px;opacity:.8">时长与人数为常规建议，现场请按实际场地、道具与人员状态调整。</div>
</footer>
</main>

<nav class="tabbar">
  <a class="on" href="index.html"><span class="t-ico">🎲</span>游戏库</a>
  <a href="#flows"><span class="t-ico">📋</span>流程方案</a>
  <a href="#toolbox"><span class="t-ico">🧰</span>工具箱</a>
  <a href="play/index.html"><span class="t-ico">🎮</span>在线玩</a>
</nav>

<script>
(function(){{
  var q=document.getElementById('q'),clr=document.getElementById('clr'),
      hits=document.getElementById('hits'),hint=document.getElementById('hint'),
      reset=document.getElementById('reset'),empty=document.getElementById('empty'),
      cards=[].slice.call(document.querySelectorAll('.gcard')),
      cats=[].slice.call(document.querySelectorAll('.cat')),
      st={{ppl:'',dur:'',ven:'',ab:'',q:''}};

  var P={{'u10':[0,10],'10-30':[10,30],'30-60':[30,60],'60p':[60,9999]}};
  var D={{'d15':[0,15],'d30':[15,30],'d60':[30,60],'d120':[60,120],'d120p':[120,9999]}};

  function ov(a,b,lo,hi){{ return a<=hi && b>=lo; }}

  function ok(el){{
    if(st.ppl){{
      var p=el.dataset.p.split(',').map(Number), r=P[st.ppl];
      if(el.dataset.u==='group'){{
        // 每组人数：能凑出一组即可（多组并行），只排除「目标人数少于最小成组人数」
        if(r[1] < p[0]) return false;
      }} else {{
        if(!ov(p[0], p[1]===0?9999:p[1], r[0], r[1])) return false;
      }}
    }}
    if(st.dur){{ var d=el.dataset.d.split(',').map(Number), r2=D[st.dur];
        if(!ov(d[0],d[1],r2[0],r2[1])) return false; }}
    if(st.ven){{
      var v=el.dataset.v;
      if(st.ven==='both'){{ if(v!=='both') return false; }}
      else if(v!==st.ven && v!=='both') return false;
    }}
    if(st.ab){{
      if((el.dataset.ab||'').indexOf(st.ab)<0) return false;
    }}
    if(st.q){{
      if((el.dataset.s||'').indexOf(st.q)<0) return false;
    }}
    return true;
  }}

  function apply(){{
    var n=0;
    cards.forEach(function(c){{ var m=ok(c); c.style.display=m?'':'none'; if(m)n++; }});
    cats.forEach(function(sec){{
      var vis=[].slice.call(sec.querySelectorAll('.gcard')).filter(function(c){{return c.style.display!=='none';}});
      sec.style.display=vis.length?'':'none';
      var cnt=sec.querySelector('.c-n'); if(cnt)cnt.textContent=vis.length+' 款';
    }});
    hits.textContent=n;
    empty.classList.toggle('on',n===0);
    if((st.ven||st.ab)&&!more.classList.contains('on')){{
      more.classList.add('on'); tog.setAttribute('aria-expanded','true');
      tog.textContent='收起筛选 ⌃';
    }}
    var active=[st.ppl,st.dur,st.ven,st.ab,st.q].filter(Boolean).length;
    reset.classList.toggle('on',active>0);
    hint.textContent = st.ppl ? '· 标「/组」的可多组并行' 
                      : (active?('· 已用 '+active+' 个条件'):'');
  }}

  function bind(rowId,key){{
    var row=document.getElementById(rowId);
    if(!row)return;
    row.addEventListener('click',function(e){{
      var b=e.target.closest('button'); if(!b)return;
      var cur=b.dataset.v===st[key];
      row.querySelectorAll('button').forEach(function(x){{x.classList.remove('on');}});
      if(cur){{ st[key]=''; }} else {{ st[key]=b.dataset.v; b.classList.add('on'); }}
      apply();
    }});
  }}
  bind('f-ppl','ppl'); bind('f-dur','dur'); bind('f-ven','ven'); bind('f-ab','ab');

  var more=document.getElementById('f-more'), tog=document.getElementById('f-toggle');
  tog.addEventListener('click',function(){{
    var on=more.classList.toggle('on');
    tog.setAttribute('aria-expanded',on?'true':'false');
    tog.textContent=on?'收起筛选 ⌃':'更多筛选 ⌄';
  }});

  q.addEventListener('input',function(){{
    st.q=q.value.trim().toLowerCase();
    clr.classList.toggle('on',!!q.value);
    apply();
  }});
  clr.addEventListener('click',function(){{ q.value=''; st.q=''; clr.classList.remove('on'); apply(); q.focus(); }});

  function clearAll(){{
    st.ppl=st.dur=st.ven=st.ab=st.q='';
    q.value=''; clr.classList.remove('on');
    ['f-ppl','f-dur','f-ven','f-ab'].forEach(function(id){{
      var row=document.getElementById(id); if(!row)return;
      row.querySelectorAll('button').forEach(function(x){{x.classList.remove('on');}});
    }});
    document.querySelectorAll('#quick button').forEach(function(x){{x.classList.remove('on');}});
    more.classList.remove('on'); tog.setAttribute('aria-expanded','false'); tog.textContent='更多筛选 ⌄';
    apply();
  }}
  reset.addEventListener('click',clearAll);
  document.getElementById('relax').addEventListener('click',function(e){{e.preventDefault();clearAll();}});

  // 快速入口
  var presets={{
    ice:  {{ppl:'',dur:'d15',ven:'',ab:'',cat:'icebreaker'}},
    small:{{ppl:'10-30',dur:'',ven:'',ab:'',cat:''}},
    long: {{ppl:'',dur:'d60',ven:'',ab:'',cat:''}},
    indoor:{{ppl:'',dur:'',ven:'indoor',ab:'',cat:''}},
    jubensha:{{ppl:'',dur:'',ven:'',ab:'',cat:'jubensha'}},
    boardgame:{{ppl:'',dur:'',ven:'',ab:'',cat:'boardgame'}}
  }};
  document.getElementById('quick').addEventListener('click',function(e){{
    var b=e.target.closest('button'); if(!b)return;
    var on=b.classList.contains('on');
    var all=this.querySelectorAll('button');
    all.forEach(function(x){{x.classList.remove('on');}});
    if(on){{ clearAll(); return; }}
    b.classList.add('on');
    var p=presets[b.dataset.preset];
    clearAll();
    b.classList.add('on');
    st.ppl=p.ppl; st.dur=p.dur; st.ven=p.ven; st.ab=p.ab;
    [['f-ppl','ppl'],['f-dur','dur'],['f-ven','ven'],['f-ab','ab']].forEach(function(pair){{
      var row=document.getElementById(pair[0]); if(!row||!st[pair[1]])return;
      row.querySelectorAll('button').forEach(function(x){{
        x.classList.toggle('on',x.dataset.v===st[pair[1]]);
      }});
    }});
    apply();
    if(p.cat){{
      var sec=document.querySelector('[data-cat="'+p.cat+'"]');
      if(sec)sec.scrollIntoView({{behavior:'smooth',block:'start'}});
    }} else {{
      document.getElementById('list').scrollIntoView({{behavior:'smooth',block:'start'}});
    }}
  }});

  apply();
}})();
</script>
</body>
</html>'''


DOC_PAGE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="{theme}">
<meta name="description" content="{desc}">
<title>{name} · 团建游戏库</title>
<link rel="stylesheet" href="{css}">
<link rel="manifest" href="{manifest}">
<link rel="apple-touch-icon" href="{icon}">
<style>:root{{--accent:{a1};--accent-ink:{a2};--accent-bg:{a3};}}</style>
</head>
<body>

<header class="topbar">
  <a class="topbar-btn" href="{home}">←</a>
  <div class="topbar-title on">{name}</div>
</header>

<section class="hero" style="--a1:{a1};--a2:{a2};">
  <span class="hero-cat">{kind}</span>
  <h1>{name}</h1>
  {lede}
</section>

{toc_html}
<article class="doc">
{body}
</article>

<footer class="foot">
  <div><a href="{home}">返回游戏库</a></div>
  <div style="margin-top:6px;opacity:.75">内容为教练使用参考，现场执行前请按实际情况调整。</div>
</footer>

<script>
function markTables(){{
  document.querySelectorAll('.tw').forEach(function(w){{
    var box=w.querySelector('.table-wrap');
    if(!box)return;
    w.classList.toggle('scrollable', box.scrollWidth - box.clientWidth > 4);
  }});
}}
markTables();
window.addEventListener('resize',markTables,{{passive:true}});
</script>
</body>
</html>'''


def _render_doc(md_path, kind_label, a1, a2, depth):
    """生成 flows/ 与 toolbox/ 下的单页文档"""
    txt = md_path.read_text(encoding='utf-8')
    _, body_md = strip_frontmatter(txt)
    body, toc = render_markdown(strip_leading_title(body_md))
    m = re.search(r'^#\s+(.+)$', body_md, re.M)
    name = re.sub(r'\*\*', '', m.group(1)).strip() if m else md_path.stem

    up = '../' * depth
    toc_html = ''
    entries = [t for t in toc if t[0] == 2]
    if len(entries) >= 3:
        lis = ''.join(f'<li class="lv2"><a href="#{a}">{html.escape(x)}</a></li>'
                      for lvl, x, a in entries)
        toc_html = ('<div class="toc"><details><summary>📑 本页目录'
                    f'（{len(entries)} 节）</summary><ol>{lis}</ol></details></div>')

    m = re.search(r'^>\s*\*\*(?:一句话|核心目标|一句话简介)\*\*\s*[：:]\s*(.+)$',
                  body_md, re.M)
    lede = m.group(1).strip() if m else ''
    lede_html = f'<p class="hero-lede">{inline(lede)}</p>' if lede else ''

    out = DOC_PAGE.format(
        name=html.escape(name), desc=html.escape(lede or name), lede=lede_html,
        theme=a2, css=up + 'assets/lib.css',
        manifest=up + 'manifest.webmanifest',
        icon=up + 'assets/icon-192.png',
        home=up + 'index.html',
        a1=a1, a2=a2, a3=a1 + '1f',
        kind=kind_label, toc_html=toc_html, body=body,
    )
    dst = md_path.with_suffix('.html')
    dst.write_text(fix_links(out, dst), encoding='utf-8')
    return dst


def register_pending(*paths):
    """把将要产出的文件登记进 PENDING（相对 BASE，'/' 分隔）"""
    for q in paths:
        try:
            PENDING.add(q.resolve().relative_to(BASE.resolve()).as_posix())
        except (ValueError, OSError):
            pass


def cmd_docs():
    made = []
    # 本批次的文档页与游戏页都还没落盘，先全部登记，
    # 否则渲染第一个文档页时，后面兄弟页的链接会被误判成死链。
    try:
        for g in json.loads((DATA / 'games.json').read_text(encoding='utf-8')):
            register_pending(BASE / g['html'])
    except Exception:
        pass
    guide = BASE / 'guide.md'
    if guide.exists():
        register_pending(guide.with_suffix('.html'))
    for d in sorted((BASE / 'flows').glob('*')):
        if d.is_dir():
            for md in sorted(d.glob('*.md')):
                register_pending(md.with_suffix('.html'))
    for md in sorted((BASE / 'toolbox').glob('*.md')):
        register_pending(md.with_suffix('.html'))
    register_pending(BASE / 'index.html')
    # 根目录的新手指南（先建，否则 flows 里的 guide.html 链接会判为死链）
    guide = BASE / 'guide.md'
    if guide.exists():
        made.append(_render_doc(guide, '📖 新手指南',
                                '#0891b2', '#0e7490', depth=0))
    # 流程图：flows/<类型>/01-schedule.md
    FLOW_LABEL = {
        'one-day': '📅 一日团建方案',
        'half-day': '⏱️ 半日团建方案',
        'workshop': '🎓 主题工作坊',
        'online': '💻 线上团建方案',
        'cross-dept': '🤝 跨部门协作方案',
        'onboarding': '🌱 新人融入方案',
    }
    for d in sorted((BASE / 'flows').glob('*')):
        if not d.is_dir():
            continue
        for md in sorted(d.glob('*.md')):
            made.append(_render_doc(md, '📋 团建流程方案 · ' + FLOW_LABEL.get(d.name, '通用').split(' ',1)[-1],
                                    '#2563eb', '#1d4ed8', depth=2))
    # 工具箱
    TOOL_LABEL = {
        'facilitation': '🗣️ 引导话术库',
        'debrief': '🔍 复盘引导框架',
        'safety': '🛡️ 安全与管理',
        'checklist': '✅ 物资与效率',
    }
    for md in sorted((BASE / 'toolbox').glob('*.md')):
        made.append(_render_doc(md, '🧰 教练工具箱',
                                '#7c3aed', '#6d28d9', depth=1))
    print(f'[docs] 已生成 {len(made)} 个流程/工具页面')


def cmd_index():
    games = json.loads((DATA / 'games.json').read_text(encoding='utf-8'))
    by_cat = {}
    for g in games:
        by_cat.setdefault(g['cat'], []).append(g)

    # 能力标签全集（按出现频次取前 14）
    from collections import Counter
    ab_cnt = Counter(a for g in games for a in g['abilities'])
    top_ab = [a for a, _ in ab_cnt.most_common(14)]
    ab_buttons = '\n'.join(
        f'      <button data-v="{html.escape(a)}">{html.escape(a)}</button>'
        for a in top_ab)

    cats_html = []
    for cat_id, icon, cat_name, a1, a2 in CATEGORIES:
        lst = sorted(by_cat.get(cat_id, []), key=lambda x: x['name'])
        if not lst:
            continue
        cards = []
        for g in lst:
            search_blob = ' '.join([g['name'], g['summary'], g['cat_name'],
                                    ' '.join(g['abilities'])]).lower()
            cards.append(
                f'''<a class="gcard" href="{g['html']}"
   data-p="{g['pmin']},{g['pmax']}" data-d="{g['dmin']},{g['dmax']}"
   data-v="{g['vkey']}" data-u="{g['unit']}" data-ab="{html.escape('|'.join(g['abilities']))}"
   data-s="{html.escape(search_blob, quote=True)}"
   style="--cc:{a1}">
  <div class="gc-name">{html.escape(g['name'])}</div>
  <div class="gc-desc">{html.escape(g['summary'] or '—')}</div>
  <div class="gc-meta"><span>{fmt_dur(g)}</span><span>{fmt_people(g)}</span><span>{g['venue']}</span><span class="gc-star">{'★' * g['stars']}</span></div>
  <div class="gc-ab">{''.join(f'<span>{html.escape(a)}</span>' for a in g['abilities'])}</div>
</a>''')
        cats_html.append(
            f'''<section class="cat" data-cat="{cat_id}" id="cat-{cat_id}">
  <div class="cat-h"><span class="c-ico">{icon}</span>{cat_name}<span class="c-n">{len(lst)} 款</span></div>
  <div class="cards">
{chr(10).join(cards)}
  </div>
</section>''')

    flows_html = '\n'.join(
        f'''    <a class="flow" href="{u}">
      <span class="f-ico">{i}</span>
      <span class="f-b"><span class="f-t">{t}</span><span class="f-d">{d}</span></span>
      <span class="f-a">›</span>
    </a>''' for u, i, t, d in FLOWS)

    tools_html = '\n'.join(
        f'''    <a class="flow" href="{u}">
      <span class="f-ico">{i}</span>
      <span class="f-b"><span class="f-t">{t}</span><span class="f-d">{d}</span></span>
      <span class="f-a">›</span>
    </a>''' for u, i, t, d in TOOLS)

    online_n = len(list((BASE / 'play' / 'games').glob('*/index.html'))) + \
        len(list((BASE / 'play' / 'tools').glob('*.html'))) if (BASE / 'play').exists() else 0

    out = INDEX.format(
        n_games=len(games),
        n_cats=len(by_cat),
        n_flows=len(FLOWS),
        n_online=online_n,
        ab_buttons=ab_buttons,
        cats_html='\n\n'.join(cats_html),
        flows_html=flows_html,
        tools_html=tools_html,
    )
    (BASE / 'index.html').write_text(out, encoding='utf-8')
    print(f'[index] 已生成 index.html（{len(games)} 款，{len(out)//1024} KB）')


def main():
    ap = argparse.ArgumentParser(description='团建游戏库构建')
    ap.add_argument('cmd', nargs='?',
                    choices=['meta', 'pages', 'docs', 'index', 'all'],
                    help='meta=元数据 pages=游戏详情页 docs=流程/工具页 index=首页 all=全部')
    a = ap.parse_args()
    if not a.cmd:
        ap.print_help()
        return
    if a.cmd in ('meta', 'all'):
        cmd_meta()
    if a.cmd in ('docs', 'all'):
        cmd_docs()
    if a.cmd in ('pages', 'all'):
        cmd_pages()
    if a.cmd == 'all' and BROKEN:
        print(f'[链接] 仍有 {len(BROKEN)} 处无法解析：')
        for b in BROKEN[:8]:
            print('   ', b)
    if a.cmd in ('index', 'all'):
        cmd_index()


if __name__ == '__main__':
    main()
