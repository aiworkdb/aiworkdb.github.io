# -*- coding: utf-8 -*-
"""site_check.py 的第 45 项：游戏页「被哪些流程用过」的文案必须与事实一致。

单独成模块，由 site_check.py 在 main() 里 import 调用。

  [45] 真实收录文案一致性
       - **真实收录款**（存在于某套流程的「本方案配套游戏」表里）：
           ① md/html 都不得再写「还没有任何现成流程收录它」
           ② md/html 都必须带「已真实收录」标记（防旧模板被批量脚本重新盖回去）
           ③ md 的反向表格行数必须 == 真实收录的流程套数（不多写也不漏写）
       - **建议落点款**（没有任何流程真实收录）：md 必须出现「建议」二字 ——
         否则读者会把「塞得进去」当成「已经被收录」

固化原因：第 18 项只校验**链接是否对称**，不看**文案是否与事实相符**。2026-11-04
发现 49 款建议落点的说明文字是同一套模板批量生成的，其中的事实早已漂移（线上模板
当时写「只配了 2 款游戏」，实际已 5 款；还指向一套根本没有空格的远程方案）。这类
错误链接照样通得过第 18 项 —— 因为「写了链接」和「链接对应的流程真的收了它」是
两件事。本轮把 6 款升级为真实收录时，一并把这条口径固化成断言。
"""
import io
import os
import re

FWD = re.compile(r"\]\(\.\./\.\./games/([a-z-]+)/([a-z0-9-]+)\.md\)")
CLAIM_EMPTY = '还没有任何现成流程收录它'
MARK_REAL = '已真实收录'
# 历史批次（2026-10-18 ~ 11-03）用的是这句，同样算「明确写了真实收录」
MARK_LEGACY = re.compile(r'下面 \d+ 套现成流程方案用到了它')


def _is_real_section(t):
    return MARK_REAL in t or bool(MARK_LEGACY.search(t))


def _read(p):
    return io.open(p, encoding='utf-8', newline='').read()


def check_flow_real(errors, TB):
    flows_dir = os.path.join(TB, 'flows')
    games_dir = os.path.join(TB, 'games')

    fwd = {}
    for dirp, dirs, files in os.walk(flows_dir):
        for fn in files:
            if not fn.endswith('.md'):
                continue
            p = os.path.join(dirp, fn)
            rel = os.path.relpath(p, flows_dir).replace('\\', '/')[:-3]
            fwd[rel] = set(FWD.findall(_read(p)))

    real = sugg = bad = 0
    for cat in sorted(os.listdir(games_dir)):
        cdir = os.path.join(games_dir, cat)
        if not os.path.isdir(cdir):
            continue
        for fn in sorted(os.listdir(cdir)):
            if not fn.endswith('.md'):
                continue
            gid = fn[:-3]
            md_p = os.path.join(cdir, fn)
            ht_p = os.path.join(cdir, gid + '.html')
            md = _read(md_p)
            ht = _read(ht_p) if os.path.exists(ht_p) else ''
            key = (cat, gid)
            mine = {k for k, v in fwd.items() if key in v}
            # md 反向表格行数（只数指向 flows 的表格行）
            rows = len([ln for ln in md.split('\n')
                        if ln.startswith('| [') and '(../../flows/' in ln])

            if mine:
                real += 1
                if CLAIM_EMPTY in md:
                    errors.append('文案与事实不符（%s 已被 %d 套流程收录，md 仍写「还没有任何现成流程收录它」）：%s/%s.md'
                                  % (gid, len(mine), cat, gid))
                    bad += 1
                if CLAIM_EMPTY in ht:
                    errors.append('文案与事实不符（%s 已被收录，html 仍写「还没有任何现成流程收录它」）：%s/%s.html'
                                  % (gid, cat, gid))
                    bad += 1
                if not _is_real_section(md):
                    errors.append('真实收录款缺「已真实收录」标记（旧模板可能被覆盖回来）：%s/%s.md'
                                  % (cat, gid))
                    bad += 1
                if not _is_real_section(ht):
                    errors.append('真实收录款缺「已真实收录」标记：%s/%s.html' % (cat, gid))
                    bad += 1
                if rows != len(mine):
                    errors.append('真实收录款反向表格行数 %d != 收录套数 %d：%s/%s.md'
                                  % (rows, len(mine), cat, gid))
                    bad += 1
            else:
                sugg += 1
                if '建议' not in md:
                    errors.append('建议落点款未标注「建议」（会被读成已被收录）：%s/%s.md' % (cat, gid))
                    bad += 1

    print('[45] 真实收录文案一致性：%d 款真实收录 / %d 款建议落点；文案与事实一致 异常 %d 项'
          % (real, sugg, bad))
