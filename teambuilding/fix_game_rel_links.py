# -*- coding: utf-8 -*-
"""把游戏页「返回XX游戏目录」指向首页对应分类锚点。

原链接是 `../../README.md#协作类`：README 渲染成 README.html 后并不存在，点进去 404；
首页每个分类网格都有 `id="cat-<分类>"`，锚点稳定。
"""
import io, os, re

TB = r'd:\mycode\aiworkdb.github.io\teambuilding'
G = os.path.join(TB, 'games')
fixed = []
for cat in sorted(os.listdir(G)):
    cdir = os.path.join(G, cat)
    if not os.path.isdir(cdir):
        continue
    for fn in sorted(os.listdir(cdir)):
        if not fn.endswith('.md'):
            continue
        p = os.path.join(cdir, fn)
        t = io.open(p, encoding='utf-8', newline='').read()
        o = t
        # 带锚点的：一律改到本页所属分类
        t = re.sub(r'\]\(\.\./\.\./README\.md#[^)]*\)',
                   '](../../index.html#cat-%s)' % cat, t)
        # 不带锚点的（如「返回游戏库」）：也归到本分类
        t = re.sub(r'\]\(\.\./\.\./README\.md\)',
                   '](../../index.html#cat-%s)' % cat, t)
        if t != o:
            io.open(p, 'w', encoding='utf-8', newline='').write(t)
            fixed.append('%s/%s' % (cat, fn))
print('修复 %d 个文件' % len(fixed))
print('\n'.join(fixed))
