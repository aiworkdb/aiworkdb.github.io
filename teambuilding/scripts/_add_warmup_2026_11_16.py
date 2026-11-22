# -*- coding: utf-8 -*-
"""3 款被年会流程正文链接到的暖场游戏（我从未线下版 / 名字接龙 / 综艺传声筒）：
把它们从「没有落点 / 文案过期」改成真实收录，避免第 45 项出现新增异常。
每节仍只允许 1 行反向表格行（第 45 项按行数断言）。"""
import io
import os
import re
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

TB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FLOW = '../../flows/annual-party/01-party.md'
HEAD = '## 🧩 这套游戏被哪些流程用过'

TXT = {
    'icebreaker/never-have-i-ever': """{h}

> **已真实收录 1 套**：[年会 / 联欢流程]({f}) 的开场暖场（18:20–18:50，30 min）· 12 卡工作题版。

| 流程 | 用在哪一步 | 一次几人 | 为什么是这一格 |
| :--- | :--- | :--- | :--- |
| [年会 / 联欢流程]({f}) | 暖场 · 一桌先熟（18:20–18:50，30 min） | 6–12 人围一桌 | 年会的暖场只需要「散场时这桌人能叫出彼此名字」——它用**承认**替代自我介绍，比「我叫什么、在哪个部门」快得多；30 min 里跑 12 张卡正好 |

**别和[线上版](../online/never-have-i-ever.md)搞混**：线上版早已被[远程新人融入](../remote-onboarding/01-schedule.md) 的破冰段真实收录，那是隔着屏幕玩；本页是**围坐一圈的线下版**，落点完全不同。

**必须改造的三件事**（照搬原版会毁掉这一格）：
1. **工作题与生活题按 1:2 混**——年会不是事故复盘，全是工作题会让人绷着；但至少要留 4 张工作题（「我从未在周五下午合并过代码」这类），否则同桌认不出彼此在做什么
2. **只跑 12 张卡**——30 min = 讲规矩 3 + 12 张各 1.5 + 收尾 3
3. **三条禁区写在桌上**：不问收入、不问健康、不问情感。跳过不计分、不追问

**另一处可塞（建议，非收录）**：危机复盘 00:00–00:20 的开场 & 无责契约 —— 那一格只有 20 min，本页要压到 12 张卡，而且必须在**不涉及裁员 / 绩效敏感背景**的场次才成立；它要求「承认」，而那种场次需要的是「先不承认也没关系」。

""",
    'variety/whisper-chain': """{h}

> **已真实收录 1 套**：[年会 / 联欢流程]({f}) 的暖场（18:20–18:50，30 min），作为[我从未（线下版）](../icebreaker/never-have-i-ever.md) 的替换款。

| 流程 | 用在哪一步 | 一组几人 / 开几组 | 为什么是这一格 |
| :--- | :--- | :--- | :--- |
| [年会 / 联欢流程]({f}) | 暖场 · 一桌先熟（18:20–18:50，30 min） | 8–30 人，分 2 队，每队 4–8 人 | 20–30 min 装进 30 min 不砍；**它不要求任何人说真话** —— 这一条在年会里比在别处重要得多：同桌可能还有第一次见面的同事，甚至领导 |

**同格怎么选**：想让人**认人**选[我从未](../icebreaker/never-have-i-ever.md)；只想**先笑起来**、且这桌人互相不熟到不想自我暴露，选本款。

**它进不了的地方**：跨区域工作坊的信息衰减实验（那一段要证明「不是他们不上心，是通道在丢东西」，必须用日常真正在用的渠道传，综艺版只能在同一个房间里演，通道损耗变成表演）；那一段现挂 [传话游戏](../communication/telephone-game.md)，本款只适合「异地团队第一次见面、开场冷到没人开口」的场。

**30 分钟怎么切**：引入与分队 3 + 三轮各 6（18）+ 原文与最终版并排 6 + 收 3。**最后那一轮「限定式」（只允许说一个字）别省**——它是后面整晚「一句话传三手就变形」的唯一伏笔。

""",
    'icebreaker/name-chain': """{h}

> **已真实收录 1 套**：[年会 / 联欢流程]({f}) 的开场暖场（18:20–18:50，30 min），作为同桌认人的第一款。

| 流程 | 用在哪一步 | 一次几人 | 为什么是这一格 |
| :--- | :--- | :--- | :--- |
| [年会 / 联欢流程]({f}) | 暖场 · 一桌先熟（18:20–18:50，30 min） | 6–10 人／桌 | 本页只要 5–10 min，**它顶不满 30 min，也不该顶满** —— 名字接完之后剩下的 20 min 正好交给同桌互相问「你在做什么项目」，那才是年会暖场真正要的东西 |

**用法要改一处**：年会按**桌**做，不按全场做。全场 40 人围一圈会觉得像小学生开学；一桌 8 人接一轮，两分钟就笑起来了。

**别指望它留下什么**：它只认名字，不留任何沉淀。所以它在本流程里是「开场的第一件事」，不是「暖场的主体」——主体是后面 20 分钟的自由交谈。

""",
}


def read(p):
    return io.open(p, encoding='utf-8', newline='').read()


def main():
    for rel, tpl in TXT.items():
        p = os.path.join(TB, 'games', rel + '.md')
        raw = read(p)
        eol = '\r\n' if '\r\n' in raw else '\n'
        body = tpl.format(h=HEAD, f=FLOW).replace('\n', eol)

        if HEAD in raw:
            i = raw.index(HEAD)
            m = re.search(r'\r?\n## ', raw[i + len(HEAD):])
            if m:
                j = i + len(HEAD) + m.start() + 1
                while raw[j:j + 1] in ('\n', '\r'):
                    j += 1
                new = raw[:i] + body + raw[j:]
            else:
                # 落点节就是全文最后一节（never-have-i-ever 这页如此）
                new = raw[:i] + body
        else:
            anchor = '## 📚 延伸阅读'
            if anchor not in raw:
                cands = re.findall(r'^## .+$', raw, re.M)
                print('  !! %s 无落点节，末节为：%s' % (rel, cands[-1] if cands else '-'))
                anchor = cands[-1]
            assert anchor in raw, rel
            new = raw.replace(anchor, body + anchor, 1)

        rows = len([ln for ln in new.split(eol) if ln.startswith('| [') and '(../../flows/' in ln])
        assert rows == 1, '%s 反向表格行数 %d != 1' % (rel, rows)
        assert '已真实收录' in new, rel
        assert '还没有任何现成流程收录它' not in new, rel
        assert '（18:20–18:50，30 min）' in new, rel
        io.open(p, 'w', encoding='utf-8', newline='').write(new)
        print('  ok  games/%s.md' % rel)


if __name__ == '__main__':
    main()
