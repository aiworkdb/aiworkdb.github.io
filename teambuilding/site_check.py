# -*- coding: utf-8 -*-
"""
团建资料库全站校验脚本（teambuilding/site_check.py）

用法：
    python teambuilding/site_check.py

检查项：
  1. 断链扫描（排除 JS 模板字符串中带 '+' 的拼接链接）
  2. HTML 结构校验（HTMLParser 标签平衡）
  3. grid-* 容器的 div 深度跨度异常检测（能抓出"多开多闭互相抵消"的隐蔽缺陷）
  4. md / html 配对检查
  5. index.html 卡片总数 == games/**/*.md 总数；各 grid-* 卡片数之和 == 总数
  6. 每个 games/*/*.md 都能在 README.md 中被 grep 到（防"隐身内容"）
  11. 流程方案 md/html 配对 + index.html / README.md 双索引收录（2026-10-11 新增）
  12. 教练页（guide.md + toolbox/*.md）：md/html 配对、双索引、代码围栏闭合、
      表格分隔符、内容长度下限（2026-10-12 新增）
  13. 流程页脚互链完整性：每套流程页脚必须互链其余全部流程（n-1 条）
      ——2026-10-13 发现旧页脚不随新增流程更新，缺口会静默累积
  14. md 侧 Markdown 链接断链扫描（[文字](路径)）
      ——2026-10-14 发现：历次"断链 0"只扫 href="..." 属性，md 的 [x](y) 从未被校验，
        实际存在 21 个文件 / 81 处坏链（层级写错 + 指向从未创建的文件）
  15. 互链闭环：83 款游戏页（md + html）必须各含 ≥2 条教练资料链接；
      5 份教练资料必须各含 ≥3 条游戏链接
  16. 流程↔游戏互链：12 套流程的 md 与 html 必须各含 ≥2 条相对游戏链接，且两侧链接集合一致
      5 份教练资料（md + html）必须各含 ≥3 条具体游戏链接
  17. 首屏决策路径覆盖：index.html（id="start-here"）与 README.md（「不知道从哪开始？」）
      必须各自收录全部流程方案与 5 份教练资料（2026-10-17 新增）
  18. 游戏 → 流程 反向互链：83 款游戏的 md + html 各需 ≥1 条流程链接、两侧集合一致，
      且凡是流程「配套游戏」表里出现过的游戏，其页面必须反向指回该流程（双向对称）
      ——2026-10-18 新增，补齐互链单向缺口（方向 C 新缺口 11）
  22. 协作游戏页 → collab.html 挑款页 反向互链：39 款协作游戏的 md + html 各需
      ① 指向自己那一组的锚点链接（../../collab.html#g-<key>）且 key 与其 data-sub 一致、
      ② 至少 1 条挑款页首页链接；md / html 两侧锚点集合必须一致
      ——2026-10-24 新增，补齐「挑款页只有 4 个入口、39 款游戏页不知道它存在」的缺口
  23. 生成器接入协作 6 组子类：toolbox/generator.html 的「拼游戏」模式在目的＝协作时
      必须能用 collab.html 的 6 组再收一层——分组集合 / 每组成员与 index.html 的
      data-sub 完全同源，组内文案（组导语 / 何时选 / 何时别选 / 首选）与 collab.html 逐字一致，
      切走协作时子类复位
      ——2026-10-25 新增：否则「上一轮的降噪会在生成器里被原样吐回去」
"""
import os
import re
import io
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TB = os.path.join(ROOT, 'teambuilding')

# Windows 控制台默认 GBK，打印 ❌ 等字符会 UnicodeEncodeError
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

errors = []
warns = []


def walk(exts):
    """遍历 teambuilding/ 下指定扩展名的文件。

    ⚠️ 坑：项目根目录名为 aiworkdb.github.io，含子串 ".git"，
    因此绝不能用 `if '.git' in dirpath: continue` 过滤，否则全站被跳过、校验静默失效。
    正确做法：按目录名精确排除。
    """
    for dirpath, dirnames, filenames in os.walk(TB):
        dirnames[:] = [d for d in dirnames if d != '.git']
        for fn in filenames:
            if any(fn.endswith(e) for e in exts):
                yield os.path.join(dirpath, fn)


# ---------- 1. 断链扫描 ----------
def check_links():
    bad = 0
    for f in walk(('.html', '.md')):
        d = os.path.dirname(f)
        try:
            txt = io.open(f, encoding='utf-8').read()
        except Exception:
            continue
        for link in re.findall(r'href="([^"]*)"', txt):
            if link.startswith(('http', '#', 'mailto:')):
                continue
            if '+' in link:          # JS 模板拼接，跳过（含 "' + '" 及 "' + game" 等形式）
                continue
            target = link.split('#')[0]
            if not target:
                continue
            if not os.path.exists(os.path.join(d, target)):
                bad += 1
                errors.append('断链: %s -> %s' % (os.path.relpath(f, ROOT), link))
    print('[1] 断链扫描：%d 处' % bad)


# ---------- 2. HTML 结构校验 ----------
class P(HTMLParser):
    VOID = {'meta', 'br', 'hr', 'img', 'input', 'link', 'area',
            'base', 'col', 'embed', 'source', 'track', 'wbr'}

    def __init__(self):
        super().__init__()
        self.stack = []
        self.err = []

    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if not self.stack:
            self.err.append('多余闭合: ' + tag)
            return
        if self.stack[-1] == tag:
            self.stack.pop()
        else:
            self.err.append('不匹配: 期望 </%s> 实得 </%s>' % (self.stack[-1], tag))


def check_structure():
    bad = 0
    for f in walk(('.html',)):
        p = P()
        try:
            p.feed(io.open(f, encoding='utf-8').read())
        except Exception as e:
            errors.append('解析失败 %s: %s' % (f, e))
            bad += 1
            continue
        if p.err or p.stack:
            bad += 1
            errors.append('结构异常: %s | %s | 未闭合 %s'
                          % (os.path.relpath(f, ROOT), '; '.join(p.err[:3]), p.stack[:5]))
    print('[2] HTML 结构校验：%d 个文件异常' % bad)


# ---------- 3. grid-* 跨度异常检测 ----------
def check_grid_spans():
    idx = os.path.join(TB, 'index.html')
    h = io.open(idx, encoding='utf-8').read()
    ids = re.findall(r'id="(grid-[a-z-]+)"', h)
    spans = {}
    for gid in ids:
        start = h.find('id="%s"' % gid)
        gt = h.find('>', start) + 1
        depth, i = 1, gt
        pat = re.compile(r'<div\b|</div>')
        while depth > 0:
            m = pat.search(h, i)
            if not m:
                break
            depth += 1 if m.group().startswith('<div') else -1
            i = m.end()
        spans[gid] = h.count('\n', 0, i) - h.count('\n', 0, gt)
    if not spans:
        print('[3] 网格跨度检测：未找到 grid-* 容器')
        return
    avg = sum(spans.values()) / float(len(spans))
    for gid, ln in spans.items():
        # 卡片最多的网格跨度自然更大，仅对远超均值 3 倍且 >150 行的报警
        if ln > 150 and ln > avg * 3:
            errors.append('网格跨度异常: %s = %d 行（均值 %.0f）' % (gid, ln, avg))
    print('[3] 网格跨度检测：%d 个容器，均值 %.0f 行 -> %s'
          % (len(spans), avg, ', '.join('%s:%d' % (k, v) for k, v in spans.items())))


# ---------- 4. md/html 配对 ----------
def check_pairs():
    mds = sorted(walk(('.md',)))
    game_mds = [f for f in mds if os.sep + 'games' + os.sep in f]
    miss = [f for f in game_mds if not os.path.exists(f[:-3] + '.html')]
    for f in miss:
        errors.append('缺 HTML: ' + os.path.relpath(f, ROOT))
    orphan = []
    for f in walk(('.html',)):
        if os.sep + 'games' + os.sep in f and f.endswith('.html'):
            base = f[:-5]
            if os.path.basename(base) in ('index',):
                continue
            if not os.path.exists(base + '.md'):
                orphan.append(f)
    for f in orphan:
        errors.append('孤儿 HTML: ' + os.path.relpath(f, ROOT))
    print('[4] md/html 配对：游戏 md %d 款，缺 HTML %d，孤儿 HTML %d'
          % (len(game_mds), len(miss), len(orphan)))
    return len(game_mds)


# ---------- 5. 卡片总数 ----------
def check_cards(total_md):
    idx = os.path.join(TB, 'index.html')
    h = io.open(idx, encoding='utf-8').read()
    cards = len(re.findall(r'<a href="games/[^"]+\.html" class="card"', h))
    per_grid = {}
    for m in re.finditer(r'id="(grid-[a-z-]+)"(.*?)(?=\n    <!-- |\n  </div>)', h, re.S):
        per_grid[m.group(1)] = len(re.findall(r'class="card"', m.group(2)))
    s = sum(per_grid.values())
    if cards != total_md:
        errors.append('卡片总数 %d != 游戏总数 %d' % (cards, total_md))
    if s != cards:
        warns.append('各网格卡片之和 %d != 卡片总数 %d（可能有卡片不在 grid-* 内）' % (s, cards))
    print('[5] index 卡片：总数 %d / 游戏 %d；分网格 %s（合计 %d）'
          % (cards, total_md, ', '.join('%s=%d' % (k, v) for k, v in per_grid.items()), s))


# ---------- 6. README 收录 ----------
def check_readme():
    readme = io.open(os.path.join(TB, 'README.md'), encoding='utf-8').read()
    missing = []
    for f in walk(('.md',)):
        if os.sep + 'games' + os.sep not in f:
            continue
        rel = os.path.relpath(f, TB).replace('\\', '/')
        if rel not in readme:
            missing.append(rel)
    for m in missing:
        errors.append('README 未收录: ' + m)
    print('[6] README 索引：未收录 %d 款 %s' % (len(missing), missing if missing else ''))


# ---------- 7. 空章节检测（2026-09-05 新增） ----------
def check_empty_sections():
    """检测 md / html 中"只有标题没有内容"的章节。

    2026-09-05 全库摸底发现 21 个文件共 39 处空章节（4F 复盘框架、讲解话术等），
    均源自 2026-06-24 的批量生成只写了骨架。已全部补全，此处固化为回归检查。

    注意：父标题下直接跟更深层子标题（无引言）是正常写法，不算空。
    """
    bad = 0
    for f in walk(('.md',)):
        if os.sep + 'games' + os.sep not in f:
            continue
        t = io.open(f, encoding='utf-8').read()
        t = re.sub(r'^---\r?\n.*?\r?\n---\r?\n', '', t, flags=re.S)
        heads = [(m.start(), m.end(), len(m.group(1)), m.group(2).strip())
                 for m in re.finditer(r'^(#{2,4}) (.+)$', t, re.M)]
        empty = []
        for i, (s, e, lvl, title) in enumerate(heads):
            j = i + 1
            while j < len(heads) and heads[j][2] > lvl:
                j += 1
            nxt = heads[j][0] if j < len(heads) else len(t)
            body = re.sub(r'^[-*_]{3,}$', '', t[e:nxt].strip(), flags=re.M).strip()
            if not body:
                empty.append(title)
        if empty:
            bad += 1
            errors.append('空章节 %s: %s' % (os.path.relpath(f, ROOT),
                                             ' | '.join(empty[:6])))
    # HTML 侧：同 md 侧一样，父标题下直接跟更深层子标题属正常，不算空
    for f in walk(('.html',)):
        if os.sep + 'games' + os.sep not in f:
            continue
        t = io.open(f, encoding='utf-8').read()
        heads = [(m.start(), m.end(), int(m.group(1)))
                 for m in re.finditer(r'<h([234])[^>]*>.*?</h\1>', t, re.S)]
        empty = []
        for i, (s, e, lvl) in enumerate(heads):
            j = i + 1
            while j < len(heads) and heads[j][2] > lvl:
                j += 1
            nxt = heads[j][0] if j < len(heads) else len(t)
            body = t[e:nxt]
            body = re.sub(r'</?(article|main|section|div|body|html)[^>]*>', '', body)
            body = re.sub(r'<hr\s*/?>', '', body)
            if not body.strip():
                empty.append(t[s:e][:40])
        if empty:
            bad += 1
            errors.append('HTML 空标题 %d 处 %s: %s'
                          % (len(empty), os.path.relpath(f, ROOT),
                             ' | '.join(x[:24] for x in empty[:4])))
    print('[7] 空章节检测：%d 个文件异常' % bad)


# ---------- 8. </html> 之后残留内容（2026-09-05 新增） ----------
def check_tail():
    """插入位置算错时，内容会被写到 </html> 之后——浏览器可能不渲染，且结构错误。"""
    bad = 0
    for f in walk(('.html',)):
        t = io.open(f, encoding='utf-8').read()
        i = t.rfind('</html>')
        if i >= 0 and t[i + len('</html>'):].strip():
            bad += 1
            errors.append('</html> 后有残留: %s' % os.path.relpath(f, ROOT))
    print('[8] 尾部残留检测：%d 个文件异常' % bad)


def check_color_clash():
    """每款游戏应有独立主色（.header 渐变首色），重复会让两款看起来像同一款。"""
    used = {}
    for f in walk(('.html',)):
        t = io.open(f, encoding='utf-8').read()
        m = re.search(r'\.header\s*\{[^}]*?linear-gradient\(135deg,\s*(#[0-9a-fA-F]{6})', t, re.S)
        if m:
            used.setdefault(m.group(1).lower(), []).append(os.path.relpath(f, ROOT))
    dup = {c: v for c, v in used.items() if len(v) > 1}
    for c, v in dup.items():
        errors.append('撞色 %s：%s' % (c, ', '.join(v)))
    print('[9] 主色撞色检测：%d 个页面 / %d 种主色，撞色 %d 组'
          % (sum(len(v) for v in used.values()), len(used), len(dup)))


def check_orphan_heading():
    """h2 单独闭合在一个 section 里、内容外溢到下一个 section——包壳类改动最易犯的错。"""
    bad = 0
    for f in walk(('.html',)):
        t = io.open(f, encoding='utf-8').read().replace('\r\n', '\n')
        for m in re.finditer(r'<div class="section">\s*<h2>(.*?)</h2>\s*</div>', t, re.S):
            bad += 1
            if bad <= 3:
                errors.append('空壳 section: %s / %s'
                              % (os.path.relpath(f, ROOT), re.sub(r'<[^>]+>', '', m.group(1)).strip()[:30]))
    print('[10] 空壳 section 检测：%d 处异常' % bad)


# ---------- 11. 流程方案 md/html 配对 + 双索引收录（2026-10-11 新增） ----------
def check_flows():
    """2026-10-11：9 套流程方案此前全部只有 .md（GitHub Pages 上是纯文本），
    已全部补齐 rich HTML。此处固化为回归检查，防止新增流程再次漏掉 HTML / 索引。

    与游戏侧（第 4/5/6 项）分开的原因：
      1. 目录不同（flows/ vs games/）
      2. index.html 收录的是 .html，README.md 收录的是 .md —— 必须分别校验
    """
    idx = io.open(os.path.join(TB, 'index.html'), encoding='utf-8').read()
    readme = io.open(os.path.join(TB, 'README.md'), encoding='utf-8').read()
    mds, htmls = [], []
    for dirpath, dirnames, filenames in os.walk(os.path.join(TB, 'flows')):
        dirnames[:] = [d for d in dirnames if d != '.git']
        for fn in filenames:
            rel = os.path.relpath(os.path.join(dirpath, fn), TB).replace('\\', '/')
            if fn.endswith('.md'):
                mds.append(rel)
            elif fn.endswith('.html'):
                htmls.append(rel)
    for m in sorted(mds):
        if m[:-3] + '.html' not in htmls:
            errors.append('流程缺 HTML: ' + m)
    for h in sorted(htmls):
        if h[:-5] + '.md' not in mds:
            errors.append('孤儿流程 HTML: ' + h)
    no_idx = [h for h in sorted(htmls) if ('href="%s"' % h) not in idx]
    no_rm = [m for m in sorted(mds) if ('(%s)' % m) not in readme]
    for h in no_idx:
        errors.append('index 未收录流程: ' + h)
    for m in no_rm:
        errors.append('README 未收录流程: ' + m)
    print('[11] 流程方案：md %d / html %d；index 收录 %d/%d；README 收录 %d/%d'
          % (len(mds), len(htmls), len(htmls) - len(no_idx), len(htmls),
             len(mds) - len(no_rm), len(mds)))


# ---------- 12. 教练页（guide + toolbox）专项（2026-10-12 新增） ----------
COACH_MD = ['guide.md'] + ['toolbox/%s.md' % n
                           for n in ('facilitation', 'debrief', 'safety', 'checklist')]


def check_coach():
    """2026-10-12：guide.md 与 toolbox/*.md 共 5 页此前全部只有 .md，
    且内容被历史截断（大段正文缺失、代码围栏不闭合、章节标题丢失），
    而 index.html 首屏直接链到它们——新用户第一次点击就遇到纯文本。
    已重写 5 份 md 并生成 rich HTML，此处固化为回归检查。

    检查四项：
      1. md/html 配对
      2. index.html 收录 .html、README.md 收录 .md（分别校验，见经验 18）
      3. md 侧 ``` 围栏数量必须为偶数——内容被截断的典型症状
      4. 管道表块必须有分隔符行，否则 GFM 下不渲染成表格（经验 56）
    """
    idx = io.open(os.path.join(TB, 'index.html'), encoding='utf-8').read()
    readme = io.open(os.path.join(TB, 'README.md'), encoding='utf-8').read()
    bad = 0
    for rel in COACH_MD:
        p = os.path.join(TB, rel.replace('/', os.sep))
        if not os.path.exists(p):
            errors.append('教练页缺失: ' + rel)
            bad += 1
            continue
        t = io.open(p, encoding='utf-8').read()
        # 1. 配对
        hp = p[:-3] + '.html'
        if not os.path.exists(hp):
            errors.append('教练页缺 HTML: ' + rel)
            bad += 1
        else:
            hrel = rel[:-3] + '.html'
            if ('href="%s"' % hrel) not in idx:
                errors.append('index 未收录教练页: ' + hrel)
                bad += 1
        if ('(%s)' % rel) not in readme:
            errors.append('README 未收录教练页: ' + rel)
            bad += 1
        # 3. 代码围栏
        if t.count('```') % 2:
            errors.append('代码围栏不闭合（疑似内容截断）: ' + rel)
            bad += 1
        # 4. 管道表分隔符
        lines = t.replace('\r\n', '\n').split('\n')
        blk = []
        for i, s in enumerate(lines + ['']):
            if s.strip().startswith('|') and s.count('|') >= 2:
                blk.append(s)
            else:
                if blk and not any(re.match(r'^\|[\s:|-]+\|?$', b.strip()) for b in blk):
                    errors.append('表格缺分隔符 %s（第 %d 行起）' % (rel, i - len(blk) + 1))
                    bad += 1
                blk = []
        # 5. 内容长度下限（防再次被截断成骨架）
        if len(re.sub(r'^---\r?\n.*?\r?\n---\r?\n', '', t, flags=re.S)) < 1200:
            errors.append('教练页内容过短（疑似骨架）: ' + rel)
            bad += 1
    print('[12] 教练页：%d 页，异常 %d 项' % (len(COACH_MD), bad))


# ---------- 13. 流程页脚互链完整性（2026-10-13 新增） ----------
def check_flow_footer():
    """2026-10-13：新增 3 套流程时发现，既有 9 套的页脚只互链了 8 套——
    每新增一套，旧页脚不会自动更新，缺口会静默累积（与经验 18「隐身内容」同型）。

    此处固化为回归检查：每套流程页脚必须互链其余全部流程（n-1 条）。
    """
    base = os.path.join(TB, 'flows')
    rels = []
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d != '.git']
        for fn in filenames:
            if fn.endswith('.html'):
                rels.append(os.path.relpath(os.path.join(dirpath, fn), base).replace('\\', '/'))
    n = len(rels)
    bad = 0
    for rel in sorted(rels):
        t = io.open(os.path.join(base, rel.replace('/', os.sep)), encoding='utf-8').read()
        sib = set(re.findall(r'href="\.\./([^/"?]+/[^/"]+\.html)"', t))
        sib = {s for s in sib if s in rels and s != rel}
        if len(sib) != n - 1:
            bad += 1
            errors.append('流程页脚互链不全 %s：%d/%d' % (rel, len(sib), n - 1))
    print('[13] 流程页脚互链：%d 套，异常 %d 项' % (n, bad))


# ---------- 14. md 侧 Markdown 链接断链扫描（2026-10-14 新增） ----------
def check_md_links():
    """第 1 项只扫 href="..."（HTML 属性），md 里的 [文字](路径) 从未被校验。

    2026-10-14 首次扫描即发现 21 个文件 / 81 处坏链，两类根因：
      1. 层级写错：games/<cat>/x.md 里写 ../toolbox/x.md（应为 ../../toolbox/）
      2. 指向从未创建的文件：printables/*.zip、tools/timer.html、images/cover.png
    这些坏链在 GitHub Pages 上表现为"点了没反应"，且历次校验全部漏过。
    """
    pat = re.compile(r"!?\[([^\]]*)\]\(([^)\s]+)\)")
    tot = 0
    bad = 0
    for f in walk(('.md',)):
        d = os.path.dirname(f)
        t = io.open(f, encoding='utf-8').read()
        # 行内代码里的 `[文字](路径)` 是语法示例，不是链接（ROADMAP 里有 3 处），先剥离
        t = re.sub(r'`[^`\n]*`', '', t)
        for m in pat.finditer(t):
            tgt = m.group(2)
            if tgt.startswith(('http', '#', 'mailto:')):
                continue
            tot += 1
            if not os.path.exists(os.path.join(d, tgt.split('#')[0])):
                bad += 1
                errors.append('md 断链: %s -> %s' % (os.path.relpath(f, ROOT), tgt))
    print('[14] md Markdown 链接：%d 条，断链 %d 处' % (tot, bad))


# ---------- 15. 游戏页 ↔ 教练资料 互链闭环（2026-10-14 新增） ----------
def check_xlink():
    """2026-10-14 完成「方向 C 新缺口 8」：游戏页与教练资料此前没有互链，
    未形成「选游戏 → 带游戏 → 复盘」闭环（教练资料侧引用游戏数为 0）。

    双向把关：
      - 每款游戏的 md + html 各含 ≥2 条指向 ../../toolbox/*.html 或 ../../guide.html 的链接
      - 每份教练资料的 md + html 各含 ≥3 条指向 games/<cat>/<id>.(md|html) 的链接
    """
    GAME_MD = r"\]\(\.\./\.\./(?:toolbox/[a-z]+\.html|guide\.html)\)"
    GAME_HTML = r'href="\.\./\.\./(?:toolbox/[a-z]+\.html|guide\.html)"'
    COACH_MD_RE = r"\]\((?:\.\./)?games/[a-z-]+/[a-z0-9-]+\.md\)"
    COACH_HTML_RE = r'href="(?:\.\./)?games/[a-z-]+/[a-z0-9-]+\.html"'
    n_md = n_html = 0
    for f in walk(('.md',)):
        if os.sep + 'games' + os.sep not in f:
            continue
        t = io.open(f, encoding='utf-8').read()
        if len(re.findall(GAME_MD, t)) >= 2:
            n_md += 1
        else:
            errors.append('游戏页缺教练资料互链(md): ' + os.path.relpath(f, ROOT))
    for f in walk(('.html',)):
        if os.sep + 'games' + os.sep not in f or os.path.basename(f) == 'index.html':
            continue
        t = io.open(f, encoding='utf-8').read()
        if len(re.findall(GAME_HTML, t)) >= 2:
            n_html += 1
        else:
            errors.append('游戏页缺教练资料互链(html): ' + os.path.relpath(f, ROOT))
    c_md = c_html = 0
    for rel in COACH_MD:
        p = os.path.join(TB, rel.replace('/', os.sep))
        t = io.open(p, encoding='utf-8').read()
        if len(re.findall(COACH_MD_RE, t)) >= 3:
            c_md += 1
        else:
            errors.append('教练资料缺游戏互链(md): ' + rel)
        h = io.open(p[:-3] + '.html', encoding='utf-8').read()
        if len(re.findall(COACH_HTML_RE, h)) >= 3:
            c_html += 1
        else:
            errors.append('教练资料缺游戏互链(html): ' + rel)
    print('[15] 互链闭环：游戏页 md %d / html %d；教练资料 md %d/5、html %d/5'
          % (n_md, n_html, c_md, c_html))


# ---------- 16. 流程方案 ↔ 游戏 互链闭环（2026-10-15 新增） ----------
def check_flow_game_xlink():
    """2026-10-15 完成「方向 C 新缺口 9」：12 套流程方案此前 md 侧只有站内绝对链接
    （https://ai.aitboy.cn/... / https://aiworkdb.github.io/...），且 conflict / innovation
    两套连一条游戏链接都没有。现要求：
      - 每套流程的 md 含 ≥2 条相对链接 ../../games/<cat>/<id>.md
      - 每套流程的 html 含 ≥2 条相对链接 ../../games/<cat>/<id>.html
      - 两侧链接集合去重后必须一致（防止只改一侧）
    """
    import collections
    MD_RE = re.compile(r"\]\(\.\./\.\./games/([a-z-]+)/([a-z0-9-]+)\.md\)")
    HTML_RE = re.compile(r'href="\.\./\.\./games/([a-z-]+)/([a-z0-9-]+)\.html"')
    ok = 0
    total = 0
    for f in walk(('.md',)):
        if os.sep + 'flows' + os.sep not in f:
            continue
        total += 1
        rel = os.path.relpath(f, ROOT).replace('\\', '/')
        t = io.open(f, encoding='utf-8').read()
        ms = set(MD_RE.findall(t))
        hp = f[:-3] + '.html'
        if not os.path.exists(hp):
            errors.append('流程缺 html：' + rel)
            continue
        hs = set(HTML_RE.findall(io.open(hp, encoding='utf-8').read()))
        if len(ms) < 2:
            errors.append('流程游戏互链不足(md, %d 条)：%s' % (len(ms), rel))
        elif len(hs) < 2:
            errors.append('流程游戏互链不足(html, %d 条)：%s' % (len(hs), rel))
        elif ms - hs:
            errors.append('流程游戏链接 md 有而 html 无：%s %s' % (rel, sorted(ms - hs)))
        elif hs - ms:
            errors.append('流程游戏链接 html 有而 md 无：%s %s' % (rel, sorted(hs - ms)))
        else:
            ok += 1
    print('[16] 流程↔游戏互链：%d/%d 套双侧齐备（md 与 html 链接集合一致）' % (ok, total))


# ---------- 17. 首屏决策路径覆盖（2026-10-17 新增） ----------
def check_start_path():
    """2026-10-17 完成「方向 C 新缺口 10」：index.html / README.md 首屏此前只讲游戏分类，
    没有一条指向 15 套流程方案与 5 份教练资料的引导路径——流程与教练资料长期
    「被索引但不被引导」，新用户从首页进来只会直接挑游戏。

    现要求两处决策区（index: id="start-here" / README: 「不知道从哪开始？」）
    各自收录全部流程与教练资料。固化原因与经验 18 同型：新增流程/教练页不会
    自动进入决策区，缺口会静默累积（见第 13 项页脚互链的教训）。
    """
    idx = io.open(os.path.join(TB, 'index.html'), encoding='utf-8').read()
    readme = io.open(os.path.join(TB, 'README.md'), encoding='utf-8').read()

    flows_md, flows_html = [], []
    for dirpath, dirnames, filenames in os.walk(os.path.join(TB, 'flows')):
        dirnames[:] = [d for d in dirnames if d != '.git']
        for fn in filenames:
            rel = os.path.relpath(os.path.join(dirpath, fn), TB).replace('\\', '/')
            if fn.endswith('.md'):
                flows_md.append(rel)
            elif fn.endswith('.html'):
                flows_html.append(rel)
    coach_html = [c[:-3] + '.html' for c in COACH_MD]

    def region(t, start, end):
        i = t.find(start)
        if i < 0:
            return None
        j = t.find(end, i)
        return t[i:j if j > 0 else len(t)]

    idx_reg = region(idx, 'id="start-here"', '<div class="search-box">')
    rm_reg = region(readme, '## 🧭 不知道从哪开始？', '## 游戏索引')
    if idx_reg is None:
        errors.append('index.html 缺少决策路径区块 id="start-here"')
        idx_reg = ''
    if rm_reg is None:
        errors.append('README.md 缺少决策路径区块「🧭 不知道从哪开始？」')
        rm_reg = ''

    miss = []
    miss += ['index 漏流程 ' + f for f in sorted(flows_html)
             if ('href="%s"' % f) not in idx_reg]
    miss += ['index 漏教练资料 ' + c for c in coach_html
             if ('href="%s"' % c) not in idx_reg]
    miss += ['README 漏流程 ' + f for f in sorted(flows_md)
             if ('](%s)' % f) not in rm_reg]
    miss += ['README 漏教练资料 ' + c for c in COACH_MD
             if ('](%s)' % c) not in rm_reg]
    for m in miss:
        errors.append('决策路径覆盖不全：' + m)
    print('[17] 首屏决策路径：index 流程 %d/%d、教练 %d/%d；README 流程 %d/%d、教练 %d/%d'
          % (len(flows_html) - sum(1 for f in flows_html if ('href="%s"' % f) not in idx_reg),
             len(flows_html),
             len(coach_html) - sum(1 for c in coach_html if ('href="%s"' % c) not in idx_reg),
             len(coach_html),
             len(flows_md) - sum(1 for f in flows_md if ('](%s)' % f) not in rm_reg),
             len(flows_md),
             len(COACH_MD) - sum(1 for c in COACH_MD if ('](%s)' % c) not in rm_reg),
             len(COACH_MD)))


# ---------- 18. 游戏 → 流程 反向互链（2026-10-18 新增） ----------
def check_game_flow_xlink():
    """2026-10-18 完成「方向 C 新缺口 11」：互链此前是单向的——15 套流程各自写了
    「用哪些游戏、为什么用它」（md/html 各 131 条），但 83 款游戏页反过来不知道自己
    被哪些方案用过（游戏 → 流程 为 0）。教练最常走的路线恰恰是反的：先挑中一款游戏，
    再决定往哪个半天里塞。

    现要求：
      - 每款游戏的 md 含 ≥1 条 ../../flows/<x>/<y>.md、html 含 ≥1 条 .html
      - 两侧集合必须一致（防只改一侧）
      - 双向对称：流程配套游戏表里出现过的游戏，其页面必须反向指回该流程
    """
    FWD = re.compile(r"\]\(\.\./\.\./games/([a-z-]+)/([a-z0-9-]+)\.md\)")
    REV_MD = re.compile(r"\]\(\.\./\.\./flows/([a-z-]+/[a-z0-9-]+)\.md\)")
    REV_HTML = re.compile(r'href="\.\./\.\./flows/([a-z-]+/[a-z0-9-]+)\.html"')

    fwd = {}   # flow(无后缀) -> set((cat,gid))
    for f in walk(('.md',)):
        if os.sep + 'flows' + os.sep not in f:
            continue
        rel = os.path.relpath(f, TB).replace('\\', '/')[:-3]
        # 与游戏页反向链接的写法对齐：去掉 'flows/' 前缀
        fwd[rel[len('flows/'):]] = set(FWD.findall(io.open(f, encoding='utf-8').read()))

    ok = tot = asym = 0
    total_links = 0
    for f in sorted(walk(('.md',))):
        if os.sep + 'games' + os.sep not in f:
            continue
        tot += 1
        rel = os.path.relpath(f, ROOT).replace('\\', '/')
        cat = rel.split('/')[-2]
        gid = os.path.basename(f)[:-3]
        key = (cat, gid)
        t = io.open(f, encoding='utf-8').read()
        ms = set(REV_MD.findall(t))
        hp = f[:-3] + '.html'
        hs = set(REV_HTML.findall(io.open(hp, encoding='utf-8').read()))
        expect = {k for k, v in fwd.items() if key in v}
        total_links += len(ms)
        if len(ms) < 1:
            errors.append('游戏缺流程反向链接(md)：' + rel)
        elif len(hs) < 1:
            errors.append('游戏缺流程反向链接(html)：' + rel)
        elif ms != hs:
            errors.append('游戏流程链接 md/html 不一致 %s：md-only=%s html-only=%s'
                          % (rel, sorted(ms - hs), sorted(hs - ms)))
        elif expect - ms:
            errors.append('反向互链不对称（流程写了它、它没指回流程）%s：%s'
                          % (rel, sorted(expect - ms)))
        else:
            ok += 1
            if expect:
                asym += 1
    print('[18] 游戏→流程反向互链：%d/%d 款双侧齐备；其中 %d 款为真实收录（对称），'
          '%d 款为建议落点；反向链接合计 %d 条'
          % (ok, tot, asym, tot - asym, total_links))


# ---------- 19. 生成器流程覆盖（2026-10-20 新增） ----------
def check_generator_flows():
    """toolbox/generator.html 此前只认 83 款游戏、完全不知道 18 套流程方案的存在
    （用户最常问的恰恰是「我这个情况该用哪一套」）。2026-10-20 升级为「整套流程 +
    游戏拼盘」双模式，此处固化为回归检查。

    固化原因与第 13 项（页脚互链）完全一致：**新增流程不会自动进生成器**，
    缺口会静默累积 —— 而这里是全站唯一「按处境索引流程」的入口，漏一套就少一条路径。
    """
    g = io.open(os.path.join(TB, 'toolbox', 'generator.html'), encoding='utf-8').read()
    n_flow_md = len([1 for d, _, fs in os.walk(os.path.join(TB, 'flows'))
                     for f in fs if f.endswith('.md')])

    urls = re.findall(r"url: '\.\./(flows/[^']+\.html)'", g)
    slugs = re.findall(r"\{ id: '([a-z\-]+)', url: '\.\./flows/", g)
    bad = 0
    if len(urls) != len(set(urls)):
        errors.append('生成器流程条目有重复：%d 条 / 去重 %d' % (len(urls), len(set(urls))))
        bad += 1
    # 注意：正则已吃掉开头的 '../'，因此 u 是相对于 teambuilding/ 的路径，不能再拼 toolbox/
    for u in sorted(set(urls)):
        if not os.path.exists(os.path.join(TB, u)):
            errors.append('生成器流程断链: ' + u)
            bad += 1
    if len(set(slugs)) < n_flow_md:
        miss = n_flow_md - len(set(slugs))
        errors.append('生成器未收录流程 %d 套（应有 %d，实有 %d）' % (miss, n_flow_md, len(set(slugs))))
        bad += 1

    # 生成器里引用的游戏 id 必须真实存在于 gamesDB
    gid = set(re.findall(r"\{ id: '([a-z0-9\-]+)', name:", g))
    for m in re.finditer(r"games: \[([^\]]*)\]", g):
        for x in re.findall(r"'([a-z0-9\-]+)'", m.group(1)):
            if x not in gid:
                errors.append('生成器流程引用了不存在的游戏: ' + x)
                bad += 1

    for needle, what in (('id="mode-group"', '整套流程 / 游戏拼盘 模式开关'),
                         ('id="scene-group"', '处境选择组'),
                         ('function scoreFlows()', '流程打分函数')):
        if needle not in g:
            errors.append('生成器缺少 %s（%s）' % (what, needle))
            bad += 1

    n_scene = len(re.findall(r"selectOption\(this, 'scene'\)", g))
    if n_scene < 6:
        errors.append('生成器处境选项只有 %d 个（应 ≥6）' % n_scene)
        bad += 1
    print('[19] 生成器流程覆盖：收录 %d/%d 套，流程链接 %d 条，处境选项 %d 个，异常 %d 项'
          % (len(set(slugs)), n_flow_md, len(urls), n_scene, bad))


# ---------- 20. 双生成器分工与交叉入口（2026-10-21 新增） ----------
def check_generator_split():
    """全站有两个生成器：`toolbox/generator.html`（全库 83 款 + 18 套流程，按处境）
    与 `play/tools/plan-generator/`（T1 快速版，22 款精选，四维筛）。
    2026-10-21 之前两者并存却互不相认 —— 用户从 teambuilding/ 和 play/ 两个入口进去
    会拿到口径不同的答案，且都不知道对面还有一个。

    固化原因：这类「两套并存」的缺口不会自己报错，只会静默各长各的。
    这里把分工与双向互链钉死：任一侧删了对方的入口、或精选库新增游戏却漏了文档链接，都会红。
    """
    main_p = os.path.join(TB, 'toolbox', 'generator.html')
    t1_p = os.path.join(TB, 'play', 'tools', 'plan-generator', 'index.html')
    t1_dir = os.path.dirname(t1_p)
    main = io.open(main_p, encoding='utf-8').read()
    t1 = io.open(t1_p, encoding='utf-8').read()
    bad = 0

    # 1) T1 → 主生成器：至少 3 处入口（顶部 notice / 结果区 split-box / 页脚）
    n_to_main = len(re.findall(r'toolbox/generator\.html', t1))
    if n_to_main < 3:
        errors.append('T1 指向主生成器只有 %d 处（应 ≥3：notice / 结果区 / 页脚）' % n_to_main)
        bad += 1
    if 'MAIN_GENERATOR' not in t1:
        errors.append('T1 缺少 MAIN_GENERATOR 常量（结果区与空结果提示都靠它）')
        bad += 1

    # 2) 主 → T1：至少 1 处反向入口
    n_to_t1 = len(re.findall(r'play/tools/plan-generator', main))
    if n_to_t1 < 1:
        errors.append('主生成器没有指向 T1 快速版的入口（分工是双向的）')
        bad += 1

    # 3) 精选库 22 款：每款都必须有 doc（主库文档页），且文件真实存在
    docs = re.findall(r"doc: '([^']+)'", t1)
    names = re.findall(r"\{ name: '([^']+)'", t1)
    if len(docs) != len(names):
        errors.append('T1 精选库 %d 款中只有 %d 款带主库文档链接' % (len(names), len(docs)))
        bad += 1
    for d in sorted(set(docs)):
        if not os.path.exists(os.path.normpath(os.path.join(t1_dir, d))):
            errors.append('T1 游戏文档断链: %s -> %s' % (d, os.path.normpath(os.path.join(t1_dir, d))))
            bad += 1

    # 4) 交互版链接（link）若存在，路径也必须真实存在
    for lk in sorted(set(re.findall(r"link: '([^']+)'", t1))):
        if not os.path.exists(os.path.normpath(os.path.join(t1_dir, lk))):
            errors.append('T1 在线玩链接断链: ' + lk)
            bad += 1

    # 5) 分工说明文案与口径对照表（PURPOSE_MAP）必须在场
    for needle, what in (('id="split-notice"', '分工说明区块'),
                         ('PURPOSE_MAP', '目的↔分类 口径对照表'),
                         ('function splitFooterHtml()', '结果区分工提示')):
        if needle not in t1:
            errors.append('T1 缺少 %s（%s）' % (what, needle))
            bad += 1

    # 6) play/index.html 须把主生成器也收录进去（否则从 play/ 入口永远看不到全库版）
    pi = io.open(os.path.join(TB, 'play', 'index.html'), encoding='utf-8').read()
    if '../toolbox/generator.html' not in pi:
        errors.append('play/index.html 未收录主生成器（全库版）')
        bad += 1

    # 7) 两个 README 都要讲清分工
    rm = io.open(os.path.join(TB, 'README.md'), encoding='utf-8').read()
    if 'toolbox/generator.html' not in rm or 'play/tools/plan-generator' not in rm:
        errors.append('teambuilding/README.md 未同时列出两个生成器')
        bad += 1
    prm = io.open(os.path.join(TB, 'play', 'README.md'), encoding='utf-8').read()
    if 'T1+' not in prm:
        errors.append('play/README.md 未写明 T1+ 主生成器（全库版）')
        bad += 1

    print('[20] 双生成器分工：T1→主 %d 处 / 主→T1 %d 处；精选 %d 款，文档链接 %d 条，在线玩 %d 条，异常 %d 项'
          % (n_to_main, n_to_t1, len(names), len(docs),
             len(set(re.findall(r"link: '([^']+)'", t1))), bad))


# ---------- 21. 协作类二级索引 / 挑款降噪（2026-10-23 新增） ----------
def check_collab_index():
    """协作占全库 46%（39/85），index.html 的协作网格 123 行、是全站最大容器
    （均值 45 行）。教练按目的筛到「协作」后面对 39 张卡，等于没筛。

    2026-10-23 按「这个游戏到底在练哪种协作」切成 6 组：
      index.html 网格内加 6 个二级小标题 + 卡片 data-sub + 协作子类筛选行；
      新建 collab.html 挑款专页（30 秒决策表 + 每组首选 / 何时别选）；
      README.md 协作表按组重排。

    固化原因与第 13 项（页脚互链）、第 19 项（生成器流程）同型：
    **新增协作游戏不会自动归入某一组，也不会自动进挑款页** —— 缺口会静默累积。
    """
    idx = io.open(os.path.join(TB, 'index.html'), encoding='utf-8').read()
    cb = io.open(os.path.join(TB, 'collab.html'), encoding='utf-8').read()
    rm = io.open(os.path.join(TB, 'README.md'), encoding='utf-8').read()
    bad = 0

    # 1) 39 款协作游戏全部带 data-sub，且恰好覆盖 games/collaboration 全集
    gids = set()
    for f in walk(('.md',)):
        if os.sep + 'games' + os.sep + 'collaboration' + os.sep in f:
            gids.add(os.path.basename(f)[:-3])
    tagged = dict((gid, sub) for gid, sub in
                  re.findall(r'<a href="games/collaboration/([a-z0-9-]+)\.html" '
                             r'class="card" data-sub="([a-z]+)"', idx))
    if set(tagged) != gids:
        miss = sorted(gids - set(tagged))
        extra = sorted(set(tagged) - gids)
        errors.append('协作卡片 data-sub 与目录不一致：缺 %s 多 %s' % (miss, extra))
        bad += 1

    # 2) 6 个二级小标题与 6 个子类筛选按钮一一对应
    heads = re.findall(r'<div class="subhead" data-sub="([a-z]+)"', idx)
    # 排除「全部」按钮（它的值是 all，不是分组）
    btns = [b for b in re.findall(r"toggleFilter\('sub', '([a-z]+)', this\)", idx)
            if b != 'all']
    if len(set(heads)) != 6 or set(heads) != set(btns):
        errors.append('二级小标题 %s 与子类按钮 %s 不对应' % (sorted(set(heads)), sorted(set(btns))))
        bad += 1
    if set(tagged.values()) != set(heads):
        errors.append('卡片的 data-sub 取值 %s 超出小标题定义的分组 %s'
                      % (sorted(set(tagged.values())), sorted(set(heads))))
        bad += 1

    # 3) 挑款页：39 款链接齐全 + 6 个分组锚点 + 每组「首选」与「别选它」
    links = set(re.findall(r'<a href="games/collaboration/([a-z0-9-]+)\.html"', cb))
    if links != gids:
        errors.append('collab.html 收录 %d 款，应为 %d；缺 %s'
                      % (len(links), len(gids), sorted(gids - links)[:6]))
        bad += 1
    anchors = re.findall(r'id="g-([a-z]+)"', cb)
    if set(anchors) != set(heads):
        errors.append('collab.html 分组锚点 %s 与 index 小标题 %s 不一致'
                      % (sorted(set(anchors)), sorted(set(heads))))
        bad += 1
    if cb.count('🎯 拿不准就先拿') != len(heads):
        errors.append('collab.html 每组应有 1 个「首选」，实际 %d 个 / 应 %d 个'
                      % (cb.count('🎯 拿不准就先拿'), len(heads)))
        bad += 1
    if cb.count('⛔ 什么时候别选它') != len(heads):
        errors.append('collab.html 每组应有 1 段「别选它」，实际 %d 个'
                      % cb.count('⛔ 什么时候别选它'))
        bad += 1

    # 4) 两个入口都要指到挑款页（否则从某一侧进去永远看不到它）
    if 'href="collab.html"' not in idx:
        errors.append('index.html 未指向 collab.html')
        bad += 1
    if '(collab.html)' not in rm:
        errors.append('README.md 未指向 collab.html')
        bad += 1

    # 5) 每组款数：index 小标题标注的款数 == README 组标题行 == 实际卡片数
    for key in sorted(set(heads)):
        m = re.search(r'data-sub="%s">[^<]*<span class="sub-n">（(\d+) 款' % key, idx)
        n_idx = int(m.group(1)) if m else -1
        n_card = sum(1 for v in tagged.values() if v == key)
        m2 = re.search(r'data-sub="%s">(.{0,60}?)（%d 款' % (key, n_card), idx)
        n_rm = len(re.findall(r'\*\*[^\n|]*（%d 款）\*\* \| \| \| \| \|' % n_card, rm))
        if n_idx != n_card:
            errors.append('分组 %s 小标题写 %d 款，实际 %d 款' % (key, n_idx, n_card))
            bad += 1
        if n_rm < 1:
            errors.append('README 未找到分组 %s 的「%d 款」标题行' % (key, n_card))
            bad += 1

    print('[21] 协作二级索引：%d 款 / %d 组（%s）；挑款页收录 %d 款、锚点 %d 个；异常 %d 项'
          % (len(tagged), len(set(heads)),
             ', '.join('%s=%d' % (k, sum(1 for v in tagged.values() if v == k))
                       for k in sorted(set(heads))),
             len(links), len(set(anchors)), bad))


def check_collab_backlinks():
    """collab.html 挑款页建成后只有 4 个入口（index 分类标题 / 首屏胶囊 / generator
    页脚 / README 决策表），39 款协作游戏页自己都不知道它存在。而教练最常走的路线
    恰恰是「先翻到某一款，再想还有没有同类」——与第 18 项「游戏 → 流程反向互链」同构。

    2026-10-24 为 39 款的 md + html 各加一节「🤝 协作挑款：这一款练的是哪一种协作」，
    带 ① 本组锚点链接 ② 挑款页首页链接。

    固化原因与第 13 / 19 / 21 项同型：**新增协作游戏不会自动长出这一节，
    已有游戏换组后锚点也不会自动跟着改** —— 缺口会静默累积、且锚点错组比没链接更难发现。
    """
    idx = io.open(os.path.join(TB, 'index.html'), encoding='utf-8').read()
    cb = io.open(os.path.join(TB, 'collab.html'), encoding='utf-8').read()
    tagged = dict((gid, sub) for gid, sub in re.findall(
        r'<a href="games/collaboration/([a-z0-9-]+)\.html"\s+class="card" data-sub="([a-z]+)"', idx))
    anchors = set(re.findall(r'id="g-([a-z]+)"', cb))
    sec = '🤝 协作挑款：这一款练的是哪一种协作'
    bad = 0
    n_md = n_html = n_link = 0
    for gid in sorted(tagged):
        want = tagged[gid]
        got = {}
        for ext in ('.md', '.html'):
            p = os.path.join(TB, 'games', 'collaboration', gid + ext)
            if not os.path.exists(p):
                errors.append('协作游戏缺 %s：%s' % (ext, gid))
                bad += 1
                continue
            t = io.open(p, encoding='utf-8').read()
            if sec not in t:
                errors.append('协作游戏页缺挑款章节（%s）：%s' % (ext, gid))
                bad += 1
            keys = set(re.findall(r'\.\./\.\./collab\.html#g-([a-z]+)', t))
            got[ext] = keys
            n_link += len(re.findall(r'\.\./\.\./collab\.html#g-', t))
            if keys != set([want]):
                errors.append('协作游戏 %s 的 %s 锚点 %s 应为其所属组 %s'
                              % (gid, ext, sorted(keys), want))
                bad += 1
            if t.count('../../collab.html"') + t.count('../../collab.html)') < 1:
                errors.append('协作游戏 %s 的 %s 缺挑款页首页链接' % (gid, ext))
                bad += 1
            if ext == '.md':
                n_md += 1
            else:
                n_html += 1
        if got.get('.md') is not None and got.get('.html') is not None \
                and got['.md'] != got['.html']:
            errors.append('协作游戏 %s 的 md/html 锚点不一致：%s vs %s'
                          % (gid, sorted(got['.md']), sorted(got['.html'])))
            bad += 1
    for k in sorted(anchors):
        if k not in set(tagged.values()):
            errors.append('collab.html 锚点 g-%s 无任何游戏归属' % k)
            bad += 1
    print('[22] 协作挑款反向互链：md %d 款 / html %d 款，锚点链接 %d 条，分组 %d 个；异常 %d 项'
          % (n_md, n_html, n_link, len(anchors), bad))


def check_generator_collab_sub():
    """协作类二级索引（第 21 项）建在 index.html 与 collab.html 上，但生成器是全站
    唯一「按处境一次出一组」的入口——选目的＝协作时它仍然一次性给出全部 39 张卡，
    等于把第 21 项的降噪原样吐回去。

    2026-10-25 在「🎲 拼一组单个游戏」模式下接入同一套 6 组子类：
      子类行只在「拼游戏 + 目的=协作」时出现，切走即复位（与 index.html 同款处理）；
      组内文案全部照搬 collab.html，不另写一份（否则两边必然漂移）；
      子类 × 人数/时长 无解时显式回退到全部协作类并说明，而不是静默换口径。

    固化原因与第 13 / 19 / 21 项同型：**新增协作游戏不会自动归入某一组，
    collab.html 改了组导语生成器也不会跟着改** —— 缺口会静默累积。
    """
    gen = io.open(os.path.join(TB, 'toolbox', 'generator.html'), encoding='utf-8').read()
    idx = io.open(os.path.join(TB, 'index.html'), encoding='utf-8').read()
    cb = io.open(os.path.join(TB, 'collab.html'), encoding='utf-8').read()
    bad = 0

    idx_sub = dict((gid, sub) for gid, sub in re.findall(
        r'<a href="games/collaboration/([a-z0-9-]+)\.html"\s+class="card" data-sub="([a-z]+)"', idx))

    # 1) 生成器的 6 组与 index.html 的 data-sub 完全同源（分组集合 + 每组成员）
    # 只在 COLLAB_GROUPS 这一段里找 —— 生成器里现在还有 IDEA_GROUPS，
    # 用全文正则会把两组一起数进去（经验 100：同形结构必须按变量名切段）
    collab_blk = re.search(r'var COLLAB_GROUPS = \[([\s\S]*?)\n\];', gen)
    if not collab_blk:
        errors.append('generator.html 缺 COLLAB_GROUPS 定义')
        return
    blocks = re.findall(r"\{ key: '([a-z]+)'[\s\S]*?ids: \[([\s\S]*?)\] \}", collab_blk.group(1))
    if len(blocks) != 6:
        errors.append('generator.html 协作子类分组应为 6 个，实际 %d 个' % len(blocks))
        return
    gen_sub = {}
    for key, ids_raw in blocks:
        for gid in re.findall(r"'([a-z0-9-]+)'", ids_raw):
            gen_sub[gid] = key
    if gen_sub != idx_sub:
        diff = sorted(set(gen_sub.items()) ^ set(idx_sub.items()))
        errors.append('生成器协作子类与 index.html data-sub 不一致：%s' % diff[:6])
        bad += 1

    # 2) 6 个子类按钮 + 1 个「不限」，取值必须等于分组 key
    btns = re.findall(r"onclick=\"selectOption\(this, 'collabSub'\)\"", gen)
    vals = re.findall(r"data-value=\"([a-z]+)\" onclick=\"selectOption\(this, 'collabSub'\)\"", gen)
    if len(btns) != 7 or set(vals) != set(k for k, _ in blocks) | set(['any']):
        errors.append('子类按钮 %s 与分组 %s 不对应'
                      % (sorted(vals), sorted(k for k, _ in blocks)))
        bad += 1

    # 3) 显隐 / 复位 / 过滤 / 回退 四段逻辑缺一不可
    for needle in ("refreshCollabSub", "userSelections.purpose === 'collaboration'",
                   "COLLAB_SUB_OF[game.id] === subKey", "lastSubFallback"):
        if needle not in gen:
            errors.append('generator.html 缺协作子类逻辑片段：%s' % needle)
            bad += 1

    # 4) 组内文案逐字取自 collab.html（经验 91：两边各写一份必然漂移）
    starts = [(m.start(), m.group(1)) for m in
              re.finditer(r'<div class="group-card" id="g-([a-z]+)">', cb)]
    tail = cb.index('⚠️ 三个最容易挑错的地方')   # 真实存在的结构边界（不用偏移量凑）
    for i, (pos, key) in enumerate(starts):
        end = starts[i + 1][0] if i + 1 < len(starts) else tail
        blk = cb[pos:end]
        m = re.search(r"\{ key: '%s',[\s\S]*?ids: \[[\s\S]*?\] \}" % key, gen)
        if not m:
            errors.append('generator.html 缺分组 %s 的定义' % key)
            bad += 1
            continue
        seg = m.group(0)
        for field in ('lead', 'when', 'avoid'):
            f = re.search(r"%s: '([^']*)'" % field, seg)
            if not f:
                errors.append('分组 %s 缺 %s 文案' % (key, field))
                bad += 1
            elif f.group(1).replace('\\\'', "'") not in blk:
                errors.append('分组 %s 的 %s 与 collab.html 不一致（生成器另写了一份）' % (key, field))
                bad += 1
        p = re.search(r"pick: '([a-z0-9-]+)'", seg)
        if not p or ('games/collaboration/%s.html' % p.group(1)) not in blk:
            errors.append('分组 %s 的首选与 collab.html 的「拿不准就先拿」不一致' % key)
            bad += 1

    # 5) 挑款页要指回生成器的这一能力（否则教练不知道生成器里也能按组挑）
    if '拼一组单个游戏' not in cb:
        errors.append('collab.html 未说明生成器已支持按这 6 组挑款')
        bad += 1

    print('[23] 生成器协作子类：%d 款 / %d 组；按钮 %d 个；文案与 collab.html 逐字比对 %d 组；异常 %d 项'
          % (len(gen_sub), len(blocks), len(vals), len(starts), bad))


# ---------- 24. 创意与解题二级索引（2026-10-26 新增） ----------
def check_idea_index():
    """2026-10-26 完成「协作之外的 46 款仍无二级索引」的第一块：💡创新思维(5) +
    🔧问题解决(5) 共 10 款此前在 index.html 共用 grid-creativity 一个网格 ——
    协作之外最大的一块，且「创新」与「解决问题」最常被混为一谈。

    现按「团队当下卡在哪一步」重切为 4 组（横跨💡/🔧两个分类）：
      - index.html 拆成 grid-creativity(5) + grid-problem-solving(5)，
        补上一直缺失的「🔧 解题」分类按钮；10 款各带 data-idea + 肌肉标签胶囊
      - 新建 idea.html 挑款专页（30 秒决策表 + 创新vs解题边界说明 + 4 组详解）
      - README.md 两节合并重排为 4 组，并加「分类」列把边界摆在明面上

    固化原因与第 21 项同型：**新增游戏不会自动归入某一组，也不会自动进挑款页**；
    且这 10 款的分组横跨两个分类文件夹，靠目录名分组必然漂移。

    同时守两件事：
      1) index.html 的 data-idea 与 idea.html 的分组必须同源（不是「集合相等」，
         而是同一款不能换组）；
      2) 「创新 vs 解题」边界说明必须在挑款页上，且每个💡/🔧分组都要能查到
         自己那一侧有哪些款 —— 否则边界又变成一句没人核对的空话。
    """
    idx = io.open(os.path.join(TB, 'index.html'), encoding='utf-8').read()
    idea = io.open(os.path.join(TB, 'idea.html'), encoding='utf-8').read()
    rm = io.open(os.path.join(TB, 'README.md'), encoding='utf-8').read()
    bad = 0

    # 1) 目录里的 10 款 == index.html 里带 data-idea 的 10 款
    on_disk = set()
    for cat in ('creativity', 'problem-solving'):
        for f in os.listdir(os.path.join(TB, 'games', cat)):
            if f.endswith('.md'):
                on_disk.add(f[:-3])
    tagged = dict((gid, sub) for gid, sub in re.findall(
        r'<a href="games/(?:creativity|problem-solving)/([a-z0-9-]+)\.html" '
        r'class="card" data-idea="([a-z]+)"', idx))
    if set(tagged) != on_disk:
        errors.append('创意/解题卡片的 data-idea 与目录不一致：缺 %s 多 %s'
                      % (sorted(on_disk - set(tagged)), sorted(set(tagged) - on_disk)))
        bad += 1

    # 2) 两个分类网格各 5 款，且都有分类按钮
    for gid, grid in (('grid-creativity', 'creativity'), ('grid-problem-solving', 'problem-solving')):
        if 'id="%s"' % gid not in idx:
            errors.append('index.html 缺网格 %s' % gid)
            bad += 1
        n = len(re.findall(r'<a href="games/(?:creativity|problem-solving)/[a-z0-9-]+\.html" '
                           r'class="card" data-idea="[a-z]+"', idx))
        if n != 10:
            errors.append('创意+解题网格卡片数 %d != 10' % n)
            bad += 1
    for cat, label in (('creativity', '💡 创意'), ('problem-solving', '🔧 解题')):
        if "toggleFilter('category', '%s'" % cat not in idx:
            errors.append('index.html 缺「%s」分类按钮' % label)
            bad += 1

    # 3) idea.html 的 4 组锚点 == index.html 的 data-idea 取值集合
    anchors = re.findall(r'<div class="group-card" id="g-([a-z]+)">', idea)
    if set(anchors) != set(tagged.values()):
        errors.append('idea.html 分组锚点 %s 与 index.html data-idea %s 不一致'
                      % (sorted(set(anchors)), sorted(set(tagged.values()))))
        bad += 1
    if len(anchors) != 4:
        errors.append('idea.html 分组数 %d != 4' % len(anchors))
        bad += 1

    # 4) 边界说明必须在挑款页上，且两个分类的分组对照表齐全
    if '创新 vs 解题：不是两个抽屉' not in idea:
        errors.append('idea.html 缺「创新 vs 解题」边界说明')
        bad += 1
    if idea.count('<th>💡 创新思维</th>') != 1 or idea.count('<th>🔧 问题解决</th>') != 1:
        errors.append('idea.html 缺💡/🔧分组对照表')
        bad += 1

    # 5) 每组：首选 + 「什么时候别选它」+ 表格款数与标题一致
    for key in sorted(set(anchors)):
        blk_start = idea.index('<div class="group-card" id="g-%s">' % key)
        nxt = [idea.index('<div class="group-card" id="g-%s">' % x)
               for x in anchors if idea.index('<div class="group-card" id="g-%s">' % x) > blk_start]
        blk = idea[blk_start:min(nxt) if nxt else idea.index('⚠️ 三个最容易挑错的地方')]
        m = re.search(r'<h3>(.*?)（(\d+) 款）</h3>', blk)
        if not m:
            errors.append('idea.html 组 %s 缺标题款数' % key)
            bad += 1
            continue
        n_title = int(m.group(2))
        n_rows = len(re.findall(r'<tr><td><a href="games/(?:creativity|problem-solving)/'
                                r'[a-z0-9-]+\.html">', blk))
        n_card = sum(1 for v in tagged.values() if v == key)
        if n_rows != n_title or n_card != n_title:
            errors.append('组 %s 款数不一致：标题 %d / 表格 %d / index %d'
                          % (key, n_title, n_rows, n_card))
            bad += 1
        if blk.count('🎯 拿不准就先拿') != 1:
            errors.append('idea.html 组 %s 缺 1 个「拿不准就先拿」' % key)
            bad += 1
        if blk.count('⛔ 什么时候别选它') != 1:
            errors.append('idea.html 组 %s 缺 1 段「别选它」' % key)
            bad += 1
        # 首选必须真实存在，且属于本组
        pk = re.search(r'🎯 拿不准就先拿：<a href="games/(?:creativity|problem-solving)/'
                       r'([a-z0-9-]+)\.html"', blk)
        if not pk or tagged.get(pk.group(1)) != key:
            errors.append('组 %s 的首选不存在或不属于本组' % key)
            bad += 1

    # 6) README 必须重排为 4 组，且保留「分类」列
    if '#### 💡 创意与解题（creativity & problem-solving）' not in rm:
        errors.append('README.md 未重排为「💡 创意与解题」一节')
        bad += 1
    if '| 游戏名称 | 分类 | 形式 | 人数 | 时长 | 场景标签 |' not in rm:
        errors.append('README.md 创意与解题表缺「分类」列')
        bad += 1
    for key in sorted(set(anchors)):
        n_card = sum(1 for v in tagged.values() if v == key)
        if not re.search(r'\*\*[^\n|]*（%d 款）\*\* \| \| \| \| \| \|' % n_card, rm):
            errors.append('README 未找到分组 %s 的「%d 款」标题行' % (key, n_card))
            bad += 1
    if rm.count('#### 💡 创新思维（creativity）') or rm.count('#### 🔧 问题解决（problem-solving）'):
        errors.append('README 仍保留旧的「💡 创新思维」/「🔧 问题解决」两节')
        bad += 1

    # 7) 三个入口都要指向挑款页
    if 'href="idea.html"' not in idx:
        errors.append('index.html 未指向 idea.html')
        bad += 1
    if '(idea.html)' not in rm:
        errors.append('README.md 未指向 idea.html')
        bad += 1

    print('[24] 创意与解题二级索引：%d 款 / %d 组（%s）；挑款页收录 %d 款；异常 %d 项'
          % (len(tagged), len(set(anchors)),
             ', '.join('%s=%d' % (k, sum(1 for v in tagged.values() if v == k))
                       for k in sorted(set(anchors))),
             len(re.findall(r'<a href="games/(?:creativity|problem-solving)/[a-z0-9-]+\.html"',
                            idea)), bad))


# ---------- 25. 创意与解题挑款反向互链（2026-10-26 新增） ----------
def check_idea_backlinks():
    """idea.html 挑款页建好后只有 4 个入口（index 分类标题 / 首屏胶囊 / README 决策表 /
    README 网页版清单），10 款创意与解题游戏页自己都不知道它存在。而教练最常走的路线
    恰恰是「先翻到某一款，再想还有没有同类」——与第 22 项同构。

    2026-10-26 为 10 款的 md + html 各加一节「💡 创意与解题挑款：这一款练的是哪一步」，
    带 ① 本组锚点链接 ② 挑款页首页链接。

    固化原因与第 22 项同型：**新增游戏不会自动长出这一节，换组后锚点也不会自动跟着改**。
    """
    idx = io.open(os.path.join(TB, 'index.html'), encoding='utf-8').read()
    idea = io.open(os.path.join(TB, 'idea.html'), encoding='utf-8').read()
    tagged = dict((gid, sub) for gid, sub in re.findall(
        r'<a href="games/(?:creativity|problem-solving)/([a-z0-9-]+)\.html" '
        r'class="card" data-idea="([a-z]+)"', idx))
    anchors = set(re.findall(r'<div class="group-card" id="g-([a-z]+)">', idea))
    sec = '💡 创意与解题挑款：这一款练的是哪一步'
    bad = 0
    n_md = n_html = n_link = 0
    for gid in sorted(tagged):
        want = tagged[gid]
        got = {}
        for ext in ('.md', '.html'):
            p = None
            for cat in ('creativity', 'problem-solving'):
                cand = os.path.join(TB, 'games', cat, gid + ext)
                if os.path.exists(cand):
                    p = cand
                    break
            if not p:
                errors.append('创意/解题游戏缺 %s：%s' % (ext, gid))
                bad += 1
                continue
            t = io.open(p, encoding='utf-8').read()
            if sec not in t:
                errors.append('创意/解题游戏页缺挑款章节（%s）：%s' % (ext, gid))
                bad += 1
            keys = set(re.findall(r'idea\.html#g-([a-z]+)', t))
            got[ext] = keys
            n_link += len(re.findall(r'idea\.html#g-', t))
            if keys != set([want]):
                errors.append('创意/解题游戏 %s 的 %s 锚点 %s 应为其所属组 %s'
                              % (gid, ext, sorted(keys), want))
                bad += 1
            if ext == '.md':
                if t.count('../../idea.html)') < 1:
                    errors.append('创意/解题游戏 %s 的 %s 缺挑款页首页链接' % (gid, ext))
                    bad += 1
                n_md += 1
            else:
                if t.count('href="../../idea.html"') < 1:
                    errors.append('创意/解题游戏 %s 的 %s 缺挑款页首页链接' % (gid, ext))
                    bad += 1
                n_html += 1
        if got.get('.md') is not None and got.get('.html') is not None \
                and got['.md'] != got['.html']:
            errors.append('创意/解题游戏 %s 的 md/html 锚点不一致：%s vs %s'
                          % (gid, sorted(got['.md']), sorted(got['.html'])))
            bad += 1
    for k in sorted(anchors):
        if k not in set(tagged.values()):
            errors.append('idea.html 锚点 g-%s 无任何游戏归属' % k)
            bad += 1
    print('[25] 创意与解题挑款反向互链：md %d 款 / html %d 款，锚点链接 %d 条，分组 %d 个；异常 %d 项'
          % (n_md, n_html, n_link, len(anchors), bad))


# ---------- 26. 生成器创意与解题子类（2026-10-26 新增） ----------
def check_generator_idea_sub():
    """生成器是全站唯一「按处境一次出一组」的入口。此前它只有协作 6 组子类，
    💡创新思维 / 🔧问题解决 这 10 款既没有独立入口，也没法按组挑 —— 选了
    「团队协作」时 39 款协作 + 10 款创意解题混在一起。

    2026-10-26 接入同一套 4 组：
      - 目的按钮新增「💡 创意与解题」（purpose=idea），只筛这 10 款
      - 新增「卡在哪一步」4 组子类筛选行，只在「拼游戏 + 目的=创意与解题」时出现
      - 组名 / 组导语 / 何时选 / 何时别选 / 组内首选，全部照搬 idea.html
      - 子类 × 人数/时长 无解时显式回退并说明，不静默换口径

    固化原因与第 23 项同型：**新增游戏不会自动归入某一组，
    idea.html 改了文案生成器也不会跟着改** —— 缺口会静默累积、两边必然漂移。
    """
    g = io.open(os.path.join(TB, 'toolbox', 'generator.html'), encoding='utf-8').read()
    idea = io.open(os.path.join(TB, 'idea.html'), encoding='utf-8').read()
    idx = io.open(os.path.join(TB, 'index.html'), encoding='utf-8').read()
    bad = 0

    # 1) 生成器的分组必须与 index.html 的 data-idea 完全同源（同一款不能换组）
    idx_sub = dict((gid, sub) for gid, sub in re.findall(
        r'<a href="games/(?:creativity|problem-solving)/([a-z0-9-]+)\.html" '
        r'class="card" data-idea="([a-z]+)"', idx))
    idea_blk = re.search(r'var IDEA_GROUPS = \[([\s\S]*?)\n\];', g)
    if not idea_blk:
        errors.append('generator.html 缺 IDEA_GROUPS 定义')
        return
    blocks = re.findall(r"\{ key: '([a-z]+)', name: '([^']*)', short: '([^']*)', n: (\d+),"
                        r"[\s\S]*?pick: '([a-z0-9-]+)',\s*\n\s*ids: \[([^\]]*)\] \}", idea_blk.group(1))
    if len(blocks) != 4:
        errors.append('generator.html 创意解题子类分组应为 4 个，实际 %d 个' % len(blocks))
        return
    gen_sub = {}
    for key, name, short, n, pick, ids_raw in blocks:
        for gid in re.findall(r"'([a-z0-9-]+)'", ids_raw):
            gen_sub[gid] = key
    if gen_sub != idx_sub:
        diff = sorted(set(gen_sub.items()) ^ set(idx_sub.items()))
        errors.append('生成器创意解题子类与 index.html data-idea 不一致：%s' % diff[:6])
        bad += 1

    # 2) 4 个子类按钮 + 1 个「不限」，取值必须等于分组 key
    btns = re.findall(r"data-value=\"([a-z]+)\" onclick=\"selectOption\(this, 'ideaSub'\)\"", g)
    if len(btns) != 5 or set(btns) != set(k for k, _, _, _, _, _ in blocks) | set(['any']):
        errors.append('ideaSub 按钮 %s 与分组 %s 不对应'
                      % (sorted(btns), sorted(k for k, _, _, _, _, _ in blocks)))
        bad += 1

    # 3) 显隐 / 复位 / 过滤 / 回退 四段逻辑缺一不可
    for needle in ("refreshIdeaSub", "userSelections.purpose === 'idea'",
                   "IDEA_SUB_OF[game.id] === ideaKey", "lastIdeaFallback"):
        if needle not in g:
            errors.append('generator.html 缺创意解题子类逻辑片段：%s' % needle)
            bad += 1

    # 4) 组内文案须与 idea.html 逐字一致（防生成器另写一份）
    starts = [(m.start(), m.group(1)) for m in
              re.finditer(r'<div class="group-card" id="g-([a-z]+)">', idea)]
    tail = idea.index('⚠️ 三个最容易挑错的地方')   # 真实存在的结构边界（不用偏移量凑）
    for i, (pos, key) in enumerate(starts):
        end = starts[i + 1][0] if i + 1 < len(starts) else tail
        blk = idea[pos:end]
        m = re.search(r"\{ key: '%s',[\s\S]*?ids: \[[\s\S]*?\] \}" % key, idea_blk.group(1))
        if not m:
            errors.append('generator.html 缺分组 %s 的定义' % key)
            bad += 1
            continue
        seg = m.group(0)
        # 从 idea.html 现抽该组的原文（组导语 / 何时选 / 何时别选）
        src = {
            'lead': re.search(r'<div class="group-lead">(.*?)</div>', blk, re.S),
            'when': re.search(r'<div class="when-box"><b>✅ 什么情况下选它</b><br>(.*?)</div>',
                              blk, re.S),
            'avoid': re.search(r'<div class="avoid-box"><b>⛔ 什么时候别选它</b><br>(.*?)</div>',
                               blk, re.S),
        }
        for field in ('lead', 'when', 'avoid'):
            assert src[field], 'idea.html 组 %s 缺 %s 原文' % (key, field)
            html_txt = re.sub(r'\s+', ' ', src[field].group(1)).strip()
            f = re.search(r"%s: '([^']*)'" % field, seg)
            if not f:
                errors.append('分组 %s 缺 %s 文案' % (key, field))
                bad += 1
                continue
            gen_txt = f.group(1).replace("\\'", "'")
            # 双向**相等**比对：只做单向包含的话，改写 idea.html 的文案时
            # 生成器那份旧文案仍然「能被找到」，漂移会漏过去（经验 104）
            if gen_txt != html_txt:
                errors.append('分组 %s 的 %s 与 idea.html 不一致（生成器另写了一份或已漂移）'
                              % (key, field))
                bad += 1
        p = re.search(r"pick: '([a-z0-9-]+)'", seg)
        # 首选在 idea.html 里的链接是 games/<分类>/<id>.html，分类要从 index.html 反查
        if not p:
            errors.append('分组 %s 缺 pick 字段' % key)
            bad += 1
        else:
            pick_gid = p.group(1)
            pick_cat = None
            for gid, sub in idx_sub.items():
                if sub == key and gid == pick_gid:
                    pick_cat = gid
            m3 = re.search(r'🎯 拿不准就先拿：<a href="games/([a-z-]+)/%s\.html"' % pick_gid, blk)
            if not m3:
                errors.append('分组 %s 的首选 %s 在 idea.html 的「拿不准就先拿」里找不到'
                              % (key, pick_gid))
                bad += 1

    # 5) 目的按钮与独立入口必须存在
    if "data-value=\"idea\"" not in g:
        errors.append('generator.html 缺「💡 创意与解题」目的按钮')
        bad += 1
    if 'params.get(\'idea\')' not in g:
        errors.append('generator.html 缺 ?idea= URL 参数')
        bad += 1
    if '../idea.html' not in g:
        errors.append('generator.html 未指向 idea.html 挑款页')
        bad += 1

    print('[26] 生成器创意解题子类：%d 款 / %d 组；按钮 %d 个；文案与 idea.html 逐字比对 %d 组；异常 %d 项'
          % (len(gen_sub), len(blocks), len(btns), len(starts), bad))


# ---------- 27. 破冰二级索引（2026-10-27 新增） ----------
def check_ice_index():
    """2026-10-27：破冰 8 款是教练最常用于开场的一类，此前既无二级索引，
    也不像协作 / 创意解题那样有挑款专页 —— 8 张卡按名字挑几乎必挑错。

    现按「破冰之后，团队手里剩下什么」切 4 组：
      - index.html 破冰网格：8 张卡按组重排 + 加 data-ice + 肌肉标签胶囊；
        新增「破冰要什么」二级筛选行（只在选中 🧊破冰 时出现）
      - 新建 ice.html 挑款专页（30 秒决策表 + 暴露度边界说明 + 4 组详解）
      - README.md 破冰小节按 4 组重排

    固化原因与第 21 / 24 项同型：**新增游戏不会自动归入某一组，
    也不会自动进挑款页**；且破冰的分组口径（按「留下什么」而非按分类）
    与协作（按「练哪种协作」）、创意解题（按「卡在哪一步」）都不同，
    三套切法混在一起最容易挑错。

    额外守一件事：**破冰标签 ≠ 破冰分类**。全库带「破冰」场景标签的共 11 款，
    其中 6 款在沟通 / 协作分类下 —— 挑款页必须把这 6 款点出来，
    否则教练按分类挑会漏掉它们。
    """
    idx = io.open(os.path.join(TB, 'index.html'), encoding='utf-8').read()
    ice = io.open(os.path.join(TB, 'ice.html'), encoding='utf-8').read()
    rm = io.open(os.path.join(TB, 'README.md'), encoding='utf-8').read()
    bad = 0

    # 1) 目录里的 8 款 == index.html 里带 data-ice 的 8 款
    on_disk = set()
    for f in os.listdir(os.path.join(TB, 'games', 'icebreaker')):
        if f.endswith('.md'):
            on_disk.add(f[:-3])
    tagged = dict((gid, sub) for gid, sub in re.findall(
        r'<a href="games/icebreaker/([a-z0-9-]+)\.html" '
        r'class="card" data-ice="([a-z]+)"', idx))
    if set(tagged) != on_disk:
        errors.append('破冰卡片的 data-ice 与目录不一致：缺 %s 多 %s'
                      % (sorted(on_disk - set(tagged)), sorted(set(tagged) - on_disk)))
        bad += 1
    if len(tagged) != 8:
        errors.append('破冰卡片 data-ice 数量 %d != 8' % len(tagged))
        bad += 1

    # 2) 筛选行必须存在，且只在选中破冰分类时出现
    if 'id="ice-filter"' not in idx:
        errors.append('index.html 缺「破冰要什么」筛选行')
        bad += 1
    # ⚠️ 注意变量名：index.html 用的是 currentFilters（生成器才用 userSelections）
    # ⚠️ 光查函数名不够（函数名在定义处也存在），必须连 toggleFilter 里的**整条调用分支**一起断言。
    #    第 27 项最初只查 "value === 'icebreaker'" 子串 —— 删掉调用分支仍能通过（第 33 项同型漏洞，
    #    2026-11-02 按第 36 / 39 项的新标准收紧）
    for needle in ('resetIce', 'setIceRow', 'currentFilters.ice',
                   "card.getAttribute('data-ice') !== currentFilters.ice",
                   "if (value === 'icebreaker') { setIceRow(true); }",
                   "else { resetIce(); setIceRow(false); }"):
        if needle not in idx:
            errors.append('index.html 缺破冰筛选逻辑片段：%s' % needle)
            bad += 1
    # 4 个组按钮 + 1 个「全部」
    btns = re.findall(r"onclick=\"toggleFilter\('ice', '([a-z]+)', this\)\"", idx)
    if len(btns) != 5 or set(btns) != set(tagged.values()) | set(['all']):
        errors.append('index.html 的 ice 按钮 %s 与分组 %s 不对应'
                      % (sorted(btns), sorted(set(tagged.values()))))
        bad += 1

    # 3) ice.html 的 4 组锚点 == index.html 的 data-ice 取值集合
    anchors = re.findall(r'<div class="group-card" id="g-([a-z]+)">', ice)
    if set(anchors) != set(tagged.values()):
        errors.append('ice.html 分组锚点 %s 与 index.html data-ice %s 不一致'
                      % (sorted(set(anchors)), sorted(set(tagged.values()))))
        bad += 1
    if len(anchors) != 4:
        errors.append('ice.html 分组数 %d != 4' % len(anchors))
        bad += 1

    # 4) 边界说明必须在挑款页上（这是本次二级索引的核心：把混淆讲清）
    if '破冰不等于「认识彼此」' not in ice:
        errors.append('ice.html 缺「破冰 ≠ 认识彼此」暴露度边界说明')
        bad += 1
    if '破冰不只是这 8 款' not in ice:
        errors.append('ice.html 缺「破冰不只是这 8 款」跨分类说明')
        bad += 1
    # 跨分类那 6 款必须列出（破冰标签 ≠ 破冰分类）
    for gid in ('drawing-relay', 'telephone-game', 'time-agents',
                'body-letters', 'crazy-kitchen', 'monster-chef'):
        if ('games/communication/%s.html' % gid) in ice or \
           ('games/collaboration/%s.html' % gid) in ice:
            continue
        errors.append('ice.html 未列出带「破冰」标签的跨分类游戏：%s' % gid)
        bad += 1

    # 5) 每组：首选 + 「什么时候别选它」+ 表格款数与标题一致
    for key in sorted(set(anchors)):
        blk_start = ice.index('<div class="group-card" id="g-%s">' % key)
        nxt = [ice.index('<div class="group-card" id="g-%s">' % x)
               for x in anchors if ice.index('<div class="group-card" id="g-%s">' % x) > blk_start]
        # 尾部边界必须锚到带标签的 <h2>：纯文本在前面 blockquote 里也出现过
        tail = '<h2>🧊 破冰不只是这 8 款</h2>'
        blk = ice[blk_start:min(nxt) if nxt else ice.index(tail)]
        m = re.search(r'<h3>(.*?)（(\d+) 款）</h3>', blk)
        if not m:
            errors.append('ice.html 组 %s 缺标题款数' % key)
            bad += 1
            continue
        n_title = int(m.group(2))
        n_rows = len(re.findall(r'<tr><td><a href="games/icebreaker/[a-z0-9-]+\.html">', blk))
        n_card = sum(1 for v in tagged.values() if v == key)
        if n_rows != n_title or n_card != n_title:
            errors.append('组 %s 款数不一致：标题 %d / 表格 %d / index %d'
                          % (key, n_title, n_rows, n_card))
            bad += 1
        if blk.count('🎯 拿不准就先拿') != 1:
            errors.append('ice.html 组 %s 缺 1 个「拿不准就先拿」' % key)
            bad += 1
        if blk.count('⛔ 什么时候别选它') != 1:
            errors.append('ice.html 组 %s 缺 1 段「别选它」' % key)
            bad += 1
        # 首选必须真实存在，且属于本组
        pk = re.search(r'🎯 拿不准就先拿：<a href="games/icebreaker/([a-z0-9-]+)\.html"', blk)
        if not pk or tagged.get(pk.group(1)) != key:
            errors.append('组 %s 的首选不存在或不属于本组' % key)
            bad += 1

    # 6) README 必须重排为 4 组
    if '🪪 只认名字' not in rm:
        errors.append('README.md 破冰小节未重排为 4 组')
        bad += 1
    for key in sorted(set(anchors)):
        n_card = sum(1 for v in tagged.values() if v == key)
        # 破冰表是 5 列（游戏名称|形式|人数|时长|场景标签），组标题行后面跟 4 个空单元格
        # → 标题行共 6 根竖线。协作表也是 5 列；创意解题表加了「分类」列是 6 列 7 根竖线。
        if not re.search(r'\*\*[^\n|]*（%d 款）\*\* \| \| \| \| \|' % n_card, rm):
            errors.append('README 未找到分组 %s 的「%d 款」标题行' % (key, n_card))
            bad += 1

    # 7) 三个入口都要指向挑款页
    if 'href="ice.html"' not in idx:
        errors.append('index.html 未指向 ice.html')
        bad += 1
    if '(ice.html)' not in rm:
        errors.append('README.md 未指向 ice.html')
        bad += 1

    print('[27] 破冰二级索引：%d 款 / %d 组（%s）；挑款页收录 %d 款；异常 %d 项'
          % (len(tagged), len(set(anchors)),
             ', '.join('%s=%d' % (k, sum(1 for v in tagged.values() if v == k))
                       for k in sorted(set(anchors))),
             len(re.findall(r'<a href="games/icebreaker/[a-z0-9-]+\.html"', ice)), bad))


# ---------- 28. 破冰挑款反向互链（2026-10-27 新增） ----------
def check_ice_backlinks():
    """ice.html 挑款页建好后只有几个入口（index 分类标题 / 首屏胶囊 /
    README 决策表 / 分类筛选行），8 款破冰游戏页自己都不知道它存在。
    而教练最常走的路线恰恰是「先翻到某一款，再想还有没有同类」
    ——与第 22 / 25 项同构。

    2026-10-27 为 8 款的 md + html 各加一节「🧊 破冰挑款：这一款留下的是什么」，
    带 ① 本组锚点链接 ② 挑款页首页链接。

    固化原因与第 22 / 25 项同型：**新增游戏不会自动长出这一节，
    换组后锚点也不会自动跟着改**。
    """
    idx = io.open(os.path.join(TB, 'index.html'), encoding='utf-8').read()
    ice = io.open(os.path.join(TB, 'ice.html'), encoding='utf-8').read()
    tagged = dict((gid, sub) for gid, sub in re.findall(
        r'<a href="games/icebreaker/([a-z0-9-]+)\.html" '
        r'class="card" data-ice="([a-z]+)"', idx))
    anchors = set(re.findall(r'<div class="group-card" id="g-([a-z]+)">', ice))
    sec = '🧊 破冰挑款：这一款留下的是什么'
    bad = 0
    n_md = n_html = n_link = 0
    for gid in sorted(tagged):
        want = tagged[gid]
        got = {}
        for ext in ('.md', '.html'):
            p = os.path.join(TB, 'games', 'icebreaker', gid + ext)
            if not os.path.exists(p):
                errors.append('破冰游戏缺 %s：%s' % (ext, gid))
                bad += 1
                continue
            t = io.open(p, encoding='utf-8').read()
            if sec not in t:
                errors.append('破冰游戏页缺挑款章节（%s）：%s' % (ext, gid))
                bad += 1
            keys = set(re.findall(r'ice\.html#g-([a-z]+)', t))
            got[ext] = keys
            n_link += len(re.findall(r'ice\.html#g-', t))
            if keys != set([want]):
                errors.append('破冰游戏 %s 的 %s 锚点 %s 应为其所属组 %s'
                              % (gid, ext, sorted(keys), want))
                bad += 1
            if ext == '.md':
                if t.count('../../ice.html)') < 1:
                    errors.append('破冰游戏 %s 的 %s 缺挑款页首页链接' % (gid, ext))
                    bad += 1
                n_md += 1
            else:
                if t.count('href="../../ice.html"') < 1:
                    errors.append('破冰游戏 %s 的 %s 缺挑款页首页链接' % (gid, ext))
                    bad += 1
                n_html += 1
        if got.get('.md') is not None and got.get('.html') is not None \
                and got['.md'] != got['.html']:
            errors.append('破冰游戏 %s 的 md/html 锚点不一致：%s vs %s'
                          % (gid, sorted(got['.md']), sorted(got['.html'])))
            bad += 1
    for k in sorted(anchors):
        if k not in set(tagged.values()):
            errors.append('ice.html 锚点 g-%s 无任何游戏归属' % k)
            bad += 1

    print('[28] 破冰挑款反向互链：md %d 款 / html %d 款，锚点链接 %d 条，分组 %d 个；异常 %d 项'
          % (n_md, n_html, n_link, len(anchors), bad))


# ---------- 29. 生成器破冰子类（2026-10-27 新增） ----------
def check_generator_ice_sub():
    """生成器是全站唯一「按处境一次出一组」的入口。此前它只有协作 6 组、
    创意解题 4 组两层子类，🧊破冰热场 这一目的既没有二层筛选也无法按组挑 ——
    选了「破冰热场」时 8 款破冰 + 8 款沟通混在一起出。

    2026-10-27 接入同一套 4 组：
      - 在既有的「🧊 破冰热场」目的下新增「破冰要什么」4 组子类筛选行
        （不新增目的按钮 —— 破冰热场本来就有，重复加会让两个入口口径打架）
      - 组名 / 组导语 / 何时选 / 何时别选 / 组内首选，全部照搬 ice.html
      - 子类 × 人数/时长 无解时显式回退，并说明；回退落在「全部 8 款破冰」
        而不是整个「破冰热场」目的（含沟通 8 款）

    固化原因与第 23 / 26 项同型：**新增游戏不会自动归入某一组，
    ice.html 改了文案生成器也不会跟着改**。
    """
    g = io.open(os.path.join(TB, 'toolbox', 'generator.html'), encoding='utf-8').read()
    ice = io.open(os.path.join(TB, 'ice.html'), encoding='utf-8').read()
    idx = io.open(os.path.join(TB, 'index.html'), encoding='utf-8').read()
    bad = 0

    # 1) 生成器的分组必须与 index.html 的 data-ice 完全同源（同一款不能换组）
    idx_sub = dict((gid, sub) for gid, sub in re.findall(
        r'<a href="games/icebreaker/([a-z0-9-]+)\.html" '
        r'class="card" data-ice="([a-z]+)"', idx))
    ice_blk = re.search(r'var ICE_GROUPS = \[([\s\S]*?)\n\];', g)
    if not ice_blk:
        errors.append('generator.html 缺 ICE_GROUPS 定义')
        return
    blocks = re.findall(r"\{ key: '([a-z]+)', name: '([^']*)', short: '([^']*)', n: (\d+),"
                        r"[\s\S]*?pick: '([a-z0-9-]+)',\s*\n\s*ids: \[([^\]]*)\] \}", ice_blk.group(1))
    if len(blocks) != 4:
        errors.append('generator.html 破冰子类分组应为 4 个，实际 %d 个' % len(blocks))
        return
    gen_sub = {}
    for key, name, short, n, pick, ids_raw in blocks:
        for gid in re.findall(r"'([a-z0-9-]+)'", ids_raw):
            gen_sub[gid] = key
    if gen_sub != idx_sub:
        diff = sorted(set(gen_sub.items()) ^ set(idx_sub.items()))
        errors.append('生成器破冰子类与 index.html data-ice 不一致：%s' % diff[:6])
        bad += 1

    # 2) 4 个子类按钮 + 1 个「不限」，取值必须等于分组 key
    btns = re.findall(r"data-value=\"([a-z]+)\" onclick=\"selectOption\(this, 'iceSub'\)\"", g)
    if len(btns) != 5 or set(btns) != set(k for k, _, _, _, _, _ in blocks) | set(['any']):
        errors.append('iceSub 按钮 %s 与分组 %s 不对应'
                      % (sorted(btns), sorted(k for k, _, _, _, _, _ in blocks)))
        bad += 1

    # 3) 显隐 / 复位 / 过滤 / 回退 四段逻辑缺一不可
    # ⚠️ 锚点要写到「声明/用法」这一级，不能只查标识符本身 ——
    #    只查 'lastIceFallback' 的话，把声明改名成 lastIceFallbackRemoved
    #    就能蒙混过关（其余 6 处引用还在，字符串依然存在）。
    for needle in ("function refreshIceSub()", "userSelections.purpose === 'icebreaker'",
                   "ICE_SUB_OF[game.id] === iceKey", "var lastIceFallback = null;",
                   "if (lastIceFallback) {", "var ICE_ALL_IDS = ["):
        if needle not in g:
            errors.append('generator.html 缺破冰子类逻辑片段：%s' % needle)
            bad += 1

    # 4) 组内文案须与 ice.html **逐字相等**（双向，防生成器另写一份）
    #    ⚠️ 早先只做「生成器的文案能在 ice.html 里找到」（单向包含）——
    #    那样改写 ice.html 的导语时，生成器那份旧文案仍然「能被找到」，
    #    漂移就漏过去了。必须做双向**相等**比对：
    #      生成器 lead  == ice.html  lead
    #      ice.html lead 出现在生成器 lead 里 = False
    starts = [(m.start(), m.group(1)) for m in
              re.finditer(r'<div class="group-card" id="g-([a-z]+)">', ice)]
    tail = ice.index('<h2>🧊 破冰不只是这 8 款</h2>')   # 真实存在的结构边界
    for i, (pos, key) in enumerate(starts):
        end = starts[i + 1][0] if i + 1 < len(starts) else tail
        blk = ice[pos:end]
        m = re.search(r"\{ key: '%s',[\s\S]*?ids: \[[\s\S]*?\] \}" % key, ice_blk.group(1))
        if not m:
            errors.append('generator.html 缺分组 %s 的定义' % key)
            bad += 1
            continue
        seg = m.group(0)
        # 从 ice.html 现抽该组的原文（组导语 / 何时选 / 何时别选）
        src = {
            'lead': re.search(r'<div class="group-lead">(.*?)</div>', blk, re.S),
            'when': re.search(r'<div class="when-box"><b>✅ 什么情况下选它</b><br>(.*?)</div>',
                              blk, re.S),
            'avoid': re.search(r'<div class="avoid-box"><b>⛔ 什么时候别选它</b><br>(.*?)</div>',
                               blk, re.S),
        }
        for field in ('lead', 'when', 'avoid'):
            assert src[field], 'ice.html 组 %s 缺 %s 原文' % (key, field)
            html_txt = re.sub(r'\s+', ' ', src[field].group(1)).strip()
            f = re.search(r"%s: '([^']*)'" % field, seg)
            if not f:
                errors.append('分组 %s 缺 %s 文案' % (key, field))
                bad += 1
                continue
            gen_txt = f.group(1).replace("\\'", "'")
            # 双向：既不能缺，也不能多（多 = 生成器自编了一份）
            if gen_txt != html_txt:
                errors.append('分组 %s 的 %s 与 ice.html 不一致（生成器另写了一份或已漂移）'
                              % (key, field))
                bad += 1
        p = re.search(r"pick: '([a-z0-9-]+)'", seg)
        if not p:
            errors.append('分组 %s 缺 pick 字段' % key)
            bad += 1
        else:
            pick_gid = p.group(1)
            m3 = re.search(r'🎯 拿不准就先拿：<a href="games/icebreaker/%s\.html"' % pick_gid, blk)
            if not m3:
                errors.append('分组 %s 的首选 %s 在 ice.html 的「拿不准就先拿」里找不到'
                              % (key, pick_gid))
                bad += 1
            # 首选必须真属于本组（生成器侧）
            if pick_gid not in [i for i in re.findall(r"'([a-z0-9-]+)'", seg)]:
                errors.append('分组 %s 的首选 %s 不在本组成员里' % (key, pick_gid))
                bad += 1

    # 5) 入口必须存在
    if 'params.get(\'ice\')' not in g:
        errors.append('generator.html 缺 ?ice= URL 参数')
        bad += 1
    if '../ice.html' not in g:
        errors.append('generator.html 未指向 ice.html 挑款页')
        bad += 1

    print('[29] 生成器破冰子类：%d 款 / %d 组；按钮 %d 个；文案与 ice.html 逐字比对 %d 组；异常 %d 项'
          % (len(gen_sub), len(blocks), len(btns), len(starts), bad))


if __name__ == '__main__':
    check_links()
    check_structure()
    check_grid_spans()
    n = check_pairs()
    check_cards(n)
    check_readme()
    check_empty_sections()
    check_tail()
    check_color_clash()
    check_orphan_heading()
    check_flows()
    check_coach()
    check_flow_footer()
    check_md_links()
    check_xlink()
    check_flow_game_xlink()
    check_start_path()
    check_game_flow_xlink()
    check_generator_flows()
    check_generator_split()
    check_collab_index()
    check_collab_backlinks()
    check_generator_collab_sub()
    check_idea_index()
    check_idea_backlinks()
    check_generator_idea_sub()
    check_ice_index()
    check_ice_backlinks()
    check_generator_ice_sub()
    # 第 30 / 31 / 32 项：线上二级索引（2026-10-28 新增）
    # 单独放在 site_check_online.py —— site_check.py 本身已够长
    import site_check_online
    site_check_online.check_online_index(errors, TB)
    site_check_online.check_online_backlinks(errors, TB)
    site_check_online.check_generator_online_sub(errors, TB)
    # 第 33 / 34 / 35 项：沟通二级索引（2026-10-31 新增）
    import site_check_comm
    site_check_comm.check_comm_index(errors, TB)
    site_check_comm.check_comm_backlinks(errors, TB)
    site_check_comm.check_generator_comm_sub(errors, TB)
    # 第 36 / 37 / 38 项：领导力二级索引（2026-11-01 新增）
    import site_check_lead
    site_check_lead.check_lead_index(errors, TB)
    site_check_lead.check_lead_backlinks(errors, TB)
    site_check_lead.check_generator_lead_sub(errors, TB)
    # 第 39 / 40 / 41 项：信任二级索引（2026-11-01 新增）
    import site_check_trust
    site_check_trust.check_trust_index(errors, TB)
    site_check_trust.check_trust_backlinks(errors, TB)
    site_check_trust.check_generator_trust_sub(errors, TB)
    # 第 42 项：挑款总入口（2026-11-02 新增）—— 七套切法的横向对照表
    import site_check_pick
    site_check_pick.check_pick_index(errors, TB)
    # 第 43 项：挑款页页首横条（2026-11-03 新增）—— 从任一页都看得见「这是七套里的第几套」
    site_check_pick.check_pick_banner(errors, TB)
    # 第 44 项：生成器「换一整套切法」跨类出口（2026-11-03 新增）
    site_check_pick.check_generator_pick_switch(errors, TB)
    # 第 45 项：真实收录文案一致性（2026-11-04 新增）—— 文案不能与「流程是否真的收了它」打架
    import site_check_flow_real
    site_check_flow_real.check_flow_real(errors, TB)
    print('-' * 60)
    for w in warns:
        print('[警告]', w)
    if errors:
        print('❌ 失败 %d 项：' % len(errors))
        for e in errors:
            print('   ', e)
        sys.exit(1)
    print('✅ 全部检查通过')
