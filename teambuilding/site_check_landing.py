# -*- coding: utf-8 -*-
"""落点体检：游戏页「建议落点」与流程页时间轴必须对得上。

为什么单独写这一个：site_check.py 的第 18 项只查「游戏页有没有链回流程」，
第 45 项只查「真实收录款的文案有没有说反」。两者都不看**声称的那个环节到底存不存在**。
2026-11-05 体检发现：领导力觉醒工作坊最长单环节是 40 min，三款领导力游戏页却写着
「主体环节（45–90 min）」；创新 Sprint 的发散环节是 40 min、造东西是 120 min，
两款创意游戏却写「发散 / 造物环节（60–90 min）」。这类错话链接照样通得过所有旧检查。

本脚本守四件事：
  [L1] 表格完整性：flows / games 下的 md，每个表格块必须有表头 + 分隔行
       （线上流程页曾整段丢表头，渲染出 4 张「没有表头的表」）
  [L2] 落点里的时间窗必须真实存在：`（HH:MM–HH:MM，N min）` 必须能在目标流程时间轴里
       找到同一时段、同一时长的一行
  [L3] 游戏时长必须装得下：目标环节时长 < 游戏最短时长时，正文必须明说「砍 / 压缩 / 装不下」
  [L4] 覆盖率统计：既无真实收录、也无建议落点的游戏数量（当前最大的内容缺口）

用法：python teambuilding/site_check_landing.py
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
GAMES = os.path.join(TB, 'games')
FLOWS = os.path.join(TB, 'flows')

RANGE = re.compile(r'(\d{2}:\d{2})[–-](\d{2}:\d{2})')
CLAIM = re.compile(r'（(\d{2}:\d{2})[–-](\d{2}:\d{2})，\s*(\d+)\s*min）')
FLOW_LINK = re.compile(r'\]\(\.\./\.\./flows/([a-z0-9-]+)/[a-z0-9-]+\.md\)')


def read(p):
    return io.open(p, encoding='utf-8', newline='').read()


def lines_of(p):
    """按真实换行切行并去掉 \r —— CRLF 文件里残留的 \r 会让所有表格判定失败"""
    return [ln.rstrip('\r') for ln in read(p).split('\n')]


def hhmm_to_min(s):
    h, m = s.split(':')
    return int(h) * 60 + int(m)


def load_flows():
    """flow key -> {(start,end): minutes}；key 取目录名（workshop 取文件名）"""
    out = {}
    for dirp, _dirs, files in os.walk(FLOWS):
        for fn in files:
            if not fn.endswith('.md'):
                continue
            p = os.path.join(dirp, fn)
            key = os.path.basename(dirp)
            if key == 'workshop':
                key = 'workshop'
            stages = {}
            for ln in read(p).split('\n'):
                if not ln.startswith('|'):
                    continue
                m = RANGE.search(ln)
                if not m:
                    continue
                s, e = m.group(1), m.group(2)
                mins = hhmm_to_min(e) - hhmm_to_min(s)
                if mins > 0:
                    stages[(s, e)] = mins
            out.setdefault(key, {}).update(stages)
    return out


def check_tables(errors):
    """[L1] 每个表格块必须有表头 + 分隔行"""
    bad = 0
    files = []
    for base in (FLOWS, GAMES):
        for dirp, _dirs, fs in os.walk(base):
            for fn in fs:
                if fn.endswith('.md'):
                    files.append(os.path.join(dirp, fn))
    for p in files:
        lines = lines_of(p)
        i, n = 0, len(lines)
        while i < n:
            if not lines[i].startswith('|'):
                i += 1
                continue
            j = i
            while j < n and lines[j].startswith('|'):
                j += 1
            block = lines[i:j]
            has_sep = any(re.match(r'^\|[\s:\-|]+\|$', b) for b in block[1:2])
            # 老页面顶部是「键值对表」（| **人数** | 8–20 人 |），两列、首格加粗，
            # 本来就没有表头，属既有排版约定，不判错
            cells = [c.strip() for c in block[0].strip().strip('|').split('|')]
            if len(cells) == 2 and cells[0].startswith('**'):
                i = j
                continue
            if not has_sep:
                bad += 1
                errors.append('[L1] 表格缺表头/分隔行：%s 第 %d 行起（%d 行）'
                              % (os.path.relpath(p, TB), i + 1, len(block)))
            i = j
    print('[L1] 表格结构：%d 个 md，缺表头 %d 处' % (len(files), bad))


def check_claims(errors):
    """[L2][L3] 落点时间窗必须真实存在；装不下必须明说"""
    flows = load_flows()
    checked = bad = 0
    games = []
    for cat in sorted(os.listdir(GAMES)):
        cdir = os.path.join(GAMES, cat)
        if not os.path.isdir(cdir):
            continue
        for fn in sorted(os.listdir(cdir)):
            if not fn.endswith('.md') or fn.lower() in ('readme.md', 'index.md'):
                continue
            games.append((cat, fn[:-3], read(os.path.join(cdir, fn))))

    for cat, gid, txt in games:
        i = txt.find('## 🧩 这套游戏被哪些流程用过')
        if i < 0:
            continue
        j = txt.find('\n## ', i + 5)
        seg = txt[i:j if j > 0 else len(txt)]
        keys = FLOW_LINK.findall(seg)
        claims = CLAIM.findall(seg)
        for s, e, mins in claims:
            checked += 1
            mins = int(mins)
            hit = None
            for k in keys:
                if (s, e) in flows.get(k, {}):
                    hit = (k, flows[k][(s, e)])
                    break
            if not hit:
                bad += 1
                errors.append('[L2] 落点时间窗在目标流程里不存在：%s/%s 写「%s–%s，%d min」（链接的流程：%s）'
                              % (cat, gid, s, e, mins, ','.join(keys) or '无'))
            elif hit[1] != mins:
                bad += 1
                errors.append('[L2] 落点时长与流程不符：%s/%s 写 %d min，流程 %s 该时段实为 %d min'
                              % (cat, gid, mins, hit[0], hit[1]))
        # [L3] 游戏时长 vs 声称环节
        m = re.search(r'\*\*(?:游戏时长|时长)\*\*\s*\|\s*([^\n|]*)', txt)
        dmin = None
        if m:
            nums = re.findall(r'\d+', m.group(1))
            if nums:
                dmin = int(nums[0])
        if dmin and claims:
            fits = any(int(c[2]) >= dmin for c in claims)
            soft = any(w in seg for w in ('砍', '压缩', '装不下'))
            if not fits and not soft:
                bad += 1
                errors.append('[L3] 装不下却没说：%s/%s 最短 %d min，声称环节 %s'
                              % (cat, gid, dmin, '、'.join(c[2] + ' min' for c in claims)))
    print('[L2/L3] 落点时间窗：核对 %d 处，异常 %d 处' % (checked, bad))
    return games, flows


def main():
    errors = []
    check_tables(errors)
    games, _ = check_claims(errors)

    # 真实收录 = 该游戏能被任一流程页的链接指到；否则看页面上有没有落点段
    ABS = re.compile(r'/games/([a-z-]+)/([a-z0-9-]+)\.html')
    REL = re.compile(r'\.\./\.\./games/([a-z-]+)/([a-z0-9-]+)\.md')
    real_ids = set()
    for dirp, _dirs, fs in os.walk(FLOWS):
        for fn in fs:
            if fn.endswith('.md'):
                t = read(os.path.join(dirp, fn))
                real_ids |= set(ABS.findall(t)) | set(REL.findall(t))

    real = sugg = none = 0
    for cat, gid, txt in games:
        has_flow = '(../../flows/' in txt or '/teambuilding/flows/' in txt
        if (cat, gid) in real_ids:
            real += 1
        elif has_flow:
            sugg += 1
        else:
            none += 1
    print('[L4] 落点覆盖：真实收录 %d ｜ 只有建议落点 %d ｜ 完全没落点 %d ｜ 合计 %d'
          % (real, sugg, none, len(games)))

    print('-' * 70)
    if errors:
        for e in errors:
            print('❌', e)
        print('\n合计 %d 项异常' % len(errors))
        return 1
    print('✅ 全部通过（L1 表格结构 / L2 时间窗真实存在 / L3 装得下或已明说）')
    return 0


if __name__ == '__main__':
    sys.exit(main())
