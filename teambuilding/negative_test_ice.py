# -*- coding: utf-8 -*-
"""负向验证：新检查项 27 / 28 / 29 能不能真的抓住回归。

做法：逐个故意破坏一处，跑 site_check 看它是否报错；跑完立刻还原。
每个破坏点对应一个「自动化保证不了、但会静默累积」的缺口类型。
"""
import io
import os
import shutil
import subprocess
import sys

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

TB = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
CHECK = os.path.join(TB, 'site_check.py')


def rd(p):
    return io.open(p, encoding='utf-8').read()


def wr(p, s):
    io.open(p, 'w', encoding='utf-8', newline='').write(s)


def run_check():
    """跑 site_check，返回是否失败（退出码非 0 即为失败）。"""
    r = subprocess.run([PY, CHECK], capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    return r.returncode != 0, r.stdout


def apply(path, old, new, label, expect_in_output=None):
    """改一处 → 跑校验 → 还原 → 报告是否被抓到。"""
    full = os.path.join(TB, path)
    bak = full + '.negbak'
    shutil.copy(full, bak)
    try:
        t = rd(full)
        assert t.count(old) == 1, '破坏锚点不唯一(%d): %s' % (t.count(old), label)
        wr(full, t.replace(old, new))
        failed, out = run_check()
        caught = failed
        detail = ''
        if expect_in_output and expect_in_output in out:
            detail = '（命中「%s」）' % expect_in_output
        elif failed:
            # 没命中预期关键词，就报第一条错误
            for line in out.split('\n'):
                if line.startswith('    '):
                    detail = '（' + line.strip()[:60] + '）'
                    break
        print('%-46s %s%s' % (label, '✅ 已抓住' if caught else '❌ 漏过', detail))
        return caught
    finally:
        shutil.move(bak, full)


def main():
    results = []

    # 1) index.html：把 blind-box-myth 从「带协作」挪到「只认名字」
    results.append(apply(
        'index.html',
        '<a href="games/icebreaker/blind-box-myth.html" class="card" '
        'data-ice="team" data-people="medium" data-duration="medium">',
        '<a href="games/icebreaker/blind-box-myth.html" class="card" '
        'data-ice="name" data-people="medium" data-duration="medium">',
        'index: 一款破冰游戏换组',
        'data-ice 与目录不一致'))

    # 2) index.html：删掉「破冰要什么」筛选行
    results.append(apply(
        'index.html',
        '    <div class="filter-group" id="ice-filter" style="display:none;">',
        '    <div class="filter-group" id="ice-filter-removed" style="display:none;">',
        'index: 删掉破冰筛选行',
        '缺「破冰要什么」筛选行'))

    # 3) index.html：把「离开破冰就复位」的联动删掉
    results.append(apply(
        'index.html',
        "    if (value === 'icebreaker') { setIceRow(true); }\n"
        "    else { resetIce(); setIceRow(false); }\n",
        '',
        'index: 删掉破冰子类的复位联动',
        '缺破冰筛选逻辑片段'))

    # 4) ice.html：改写某一组的导语（生成器那侧会漂移）
    results.append(apply(
        'ice.html',
        '<div class="group-lead">破冰最省事的一种：不要求任何人讲自己的事，',
        '<div class="group-lead">【改写测试】破冰最省事的一种：不要求任何人讲自己的事，',
        'ice.html: 改写组导语',
        '与 ice.html 不一致'))

    # 5) ice.html：删掉「破冰 ≠ 认识彼此」边界说明
    results.append(apply(
        'ice.html',
        '<h2>🔀 破冰不等于「认识彼此」：四档暴露度</h2>',
        '<h2>（已删除的边界说明）</h2>',
        'ice.html: 删掉暴露度边界说明',
        '缺「破冰 ≠ 认识彼此」暴露度边界说明'))

    # 6) ice.html：删掉跨分类破冰游戏的一行
    results.append(apply(
        'ice.html',
        '<tr><td class="cat">💬 沟通表达</td>'
        '<td><a href="games/communication/telephone-game.html">传话游戏</a></td>',
        '<tr><td class="cat">💬 沟通表达</td>'
        '<td><a href="games/communication/removed.html">已移除</a></td>',
        'ice.html: 删掉跨分类破冰游戏',
        '未列出带「破冰」标签的跨分类游戏'))

    # 7) 游戏页：删掉某款破冰游戏的挑款章节
    results.append(apply(
        'games/icebreaker/name-chain.md',
        '## 🧊 破冰挑款：这一款留下的是什么',
        '## （已删除的挑款章节）',
        '游戏页: 删掉破冰挑款章节',
        '缺挑款章节'))

    # 8) 游戏页：把锚点指向别的组
    results.append(apply(
        'games/icebreaker/two-truths-one-lie.md',
        '../../ice.html#g-know',
        '../../ice.html#g-team',
        '游戏页: 锚点指向别的组',
        '应为其所属组'))

    # 9) generator.html：改写生成器里的组文案
    results.append(apply(
        'toolbox/generator.html',
        "lead: '破冰最省事的一种：不要求任何人讲自己的事，",
        "lead: '【改写测试】破冰最省事的一种：不要求任何人讲自己的事，",
        'generator: 改写组文案（应与 ice.html 逐字比对报错）',
        '与 ice.html 不一致'))

    # 10) generator.html：删掉回退逻辑
    results.append(apply(
        'toolbox/generator.html',
        'var lastIceFallback = null;',
        'var lastIceFallbackRemoved = null;',
        'generator: 删掉回退标记',
        '缺破冰子类逻辑片段'))

    # 11) generator.html：删掉 ICE_ALL_IDS（回退目标）
    results.append(apply(
        'toolbox/generator.html',
        'var ICE_ALL_IDS = [',
        'var ICE_ALL_IDS_REMOVED = [',
        'generator: 删掉 ICE_ALL_IDS',
        '缺破冰子类逻辑片段'))

    # 12) generator.html：删掉 ?ice= URL 参数
    results.append(apply(
        'toolbox/generator.html',
        "var ice = params.get('ice');",
        "var iceRemoved = null;",
        'generator: 删掉 ?ice= 参数',
        '缺 ?ice= URL 参数'))

    ok = sum(1 for r in results if r)
    print()
    print('负向验证：%d / %d 处破坏被抓住' % (ok, len(results)))
    if ok != len(results):
        print('❌ 有破坏没被抓住 —— 检查项有盲区')
        sys.exit(1)
    print('✅ 全部破坏均被抓住')


if __name__ == '__main__':
    main()
