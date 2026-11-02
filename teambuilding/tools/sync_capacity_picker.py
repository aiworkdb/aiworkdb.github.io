#!/usr/bin/env python3
"""把游戏库的数据同步进 play/tools/capacity-picker/index.html 的内嵌 GAMES 数组。

背景：这个工具页是手写静态页，游戏数据直接内嵌在 <script> 里。
手工维护导致三个问题：
  1. 缺新游戏（库里 86 款，它只有 74 款）
  2. URL 相对路径写错（少了两级 ../），74 个链接全死
  3. 人数口径与游戏库不一致（没区分「每组人数」和「全场人数」）

所以这里从 _data/games.json 重新生成整个数组，并同步改写筛选逻辑
（人数筛选要支持 group 口径，与首页一致）。

用法：python3 tools/sync_capacity_picker.py [--check]
"""
import json
import pathlib
import re
import sys

BASE = pathlib.Path(__file__).resolve().parent.parent
TOOL = BASE / 'play/tools/capacity-picker/index.html'
DATA = BASE / '_data/games.json'


def build_array():
    games = json.loads(DATA.read_text(encoding='utf-8'))
    out = []
    for g in sorted(games, key=lambda x: x['name']):
        out.append({
            'name': g['name'],
            'cat': g['cat'],
            'abilities': g['abilities'],
            'pmin': g['pmin'],
            'pmax': g['pmax'],
            'mins': g['dmax'],
            'venue': g['vkey'],
            'unit': g['unit'],
            # 工具页在 play/tools/capacity-picker/ 下，回游戏库要退三级
            # play/tools/capacity-picker -> play/tools -> play -> teambuilding/
            'url': '../../../' + g['html'],
        })
    return out


def main():
    check = '--check' in sys.argv
    html = TOOL.read_text(encoding='utf-8')
    arr = build_array()
    new_js = 'var GAMES = ' + json.dumps(arr, ensure_ascii=False, separators=(',', ':')) + ';'

    m = re.search(r'var GAMES = \[.*?\];', html, re.S)
    if not m:
        print('✗ 找不到 GAMES 数组')
        return 1

    # 筛选逻辑：人数要支持 group 口径（每组 N 人，可多组并行）
    old_filter = ("if (state.people && !(g.pmin <= state.people && g.pmax >= state.people)) return false;")
    new_filter = ("if (state.people) { if (g.unit === 'group') { if (state.people < g.pmin) return false; }"
                  " else if (!(g.pmin <= state.people && g.pmax >= state.people)) return false; }")
    if new_filter not in html:
        if old_filter not in html:
            print('✗ 找不到人数筛选逻辑')
            return 1
        html = html.replace(old_filter, new_filter, 1)

    # 文案里的游戏总数
    html = re.sub(r'全库 \d+ 款游戏', f'全库 {len(arr)} 款游戏', html)

    if check:
        cur = json.loads(m.group(0)[len('var GAMES = '):-1])
        print(f'当前内嵌 {len(cur)} 款，库中 {len(arr)} 款 → '
              + ('一致' if cur == arr else '【不一致，需重跑】'))
        return 0 if cur == arr else 1

    html = html[:m.start()] + new_js + html[m.end():]
    TOOL.write_text(html, encoding='utf-8')
    print(f'✓ 已同步 {len(arr)} 款游戏到 capacity-picker')
    return 0


if __name__ == '__main__':
    sys.exit(main())
