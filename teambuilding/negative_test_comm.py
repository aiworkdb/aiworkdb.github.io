# -*- coding: utf-8 -*-
"""负向验证：故意破坏 7 处，确认 site_check 第 33 / 34 / 35 项真的抓得住。

正向全绿不等于检查有效 —— 只有「破坏 → 被抓住」闭环跑通，
这几项才算真的在把关（经验：第 21 / 24 / 27 / 30 项都各自做过这一步）。

用法：
    python teambuilding/negative_test_comm.py
（脚本会在内存里备份并在 finally 中还原，正常退出后磁盘内容不变）
"""
import io
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

TB = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TB)
import site_check_comm as C  # noqa: E402

FILES = {}
CASES = []


def rd(rel):
    return io.open(os.path.join(TB, rel), encoding='utf-8', newline='').read()


def wr(rel, s):
    io.open(os.path.join(TB, rel), 'w', encoding='utf-8', newline='').write(s)


def backup(*rels):
    for r in rels:
        FILES[r] = rd(r)


def restore():
    for r, s in FILES.items():
        wr(r, s)


def case(label, rel, mutate, checks):
    CASES.append((label, rel, mutate, checks))


def swap(old, new):
    """生成一次替换的破坏动作。

    ⚠️ index.html / generator.html 是 CRLF，破坏串里写死 '\\n' 会命中 0 次
    —— 那样用例会「静默失效」，看起来像检查有效，其实什么都没验（经验 98）。
    """
    def _f(t):
        nl = '\r\n' if '\r\n' in t else '\n'
        return t.replace(old.replace('\n', nl), new.replace('\n', nl), 1)
    return _f


# ---------------- 破坏用例 ----------------
case('① 删 comm.html 的「沟通 ≠ 练说话」边界说明', 'comm.html',
     swap('「沟通」不等于「练说话」', '沟通游戏怎么挑'),
     [C.check_comm_index])

case('② 把 time-agents 的 data-comm 换成别的组', 'index.html',
     swap('data-comm="clash" data-people="medium" data-duration="medium">\n'
          '        <div class="card-icon">⏰</div>',
          'data-comm="pool" data-people="medium" data-duration="medium">\n'
          '        <div class="card-icon">⏰</div>'),
     [C.check_comm_index, C.check_generator_comm_sub])

case('③ 删 index.html 的 resetComm 复位逻辑', 'index.html',
     swap("    else { resetComm(); setCommRow(false); }\n", ''),
     [C.check_comm_index])

case('④ comm.html 删掉一个跨分类链接（盲行）', 'comm.html',
     swap('<a href="games/trust/blind-walk.html">盲行</a>', '盲行'),
     [C.check_comm_index])

# ⚠️ 不能只「改写标题但仍含原标题子串」—— SECTION_TITLE 用的是 in 判定，
#    那样破坏不会生效，会伪装成一条通过的用例
case('⑤ 删某款游戏页（画图接龙 md）的沟通挑款章节', 'games/communication/drawing-relay.md',
     swap('## ' + C.SECTION_TITLE, '## 💬 沟通挑款（章节已删）'),
     [C.check_comm_backlinks])

case('⑥ 生成器改写组导语（两边漂移）', 'toolbox/generator.html',
     swap("lead: '这两款把「说的人看不见对方理解到哪了」做成硬规则",
          "lead: '随便写一句不一样的导语"),
     [C.check_generator_comm_sub])

case('⑦ 生成器删掉 ?comm= URL 参数', 'toolbox/generator.html',
     swap("  var comm = params.get('comm');", "  var comm = null;"),
     [C.check_generator_comm_sub])


def main():
    rels = sorted(set([c[1] for c in CASES]))
    backup(*rels)
    caught = 0
    try:
        for label, rel, mutate, checks in CASES:
            restore()
            cur = rd(rel)
            new = mutate(cur)
            if new == cur:
                print('⚠️  %s —— 破坏未生效（锚点已失效，需更新用例）' % label)
                continue
            wr(rel, new)
            errors = []
            for fn in checks:
                fn(errors, TB)
            if errors:
                caught += 1
                print('✅ %s —— 被抓住：%s' % (label, errors[0][:70]))
            else:
                print('❌ %s —— 没有被抓住（该项检查有漏洞）' % label)
    finally:
        restore()
    print('\n%d/%d 处破坏被抓住' % (caught, len(CASES)))
    return 0 if caught == len(CASES) else 1


if __name__ == '__main__':
    sys.exit(main())
