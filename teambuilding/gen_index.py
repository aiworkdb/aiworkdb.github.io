#!/usr/bin/env python3
"""
根据 games/ 下所有 .md 文件，自动生成 teambuilding/index.html
"""
import re
from pathlib import Path

BASE = Path('d:/mycode/aiworkdb.github.io/teambuilding')
GAMES_DIR = BASE / 'games'

# 分类配置：顺序、图标、中文名
CATEGORIES = [
    ('icebreaker',   '🧊', '破冰热场',   'icebreaker'),
    ('communication','💬', '沟通表达',   'communication'),
    ('collaboration','🤝', '团队协作',   'collaboration'),
    ('trust',        '🤖', '信任建立',   'trust'),
    ('leadership',   '👑', '领导力',     'leadership'),
    ('creativity',   '💡', '创意与解决问题', 'creativity'),
    ('problem-solving', '🔧', '问题解决', 'problem-solving'),
]

# 图标映射（根据游戏名称自动选择）
ICON_MAP = {
    '宾果': '🎯', '两真': '🤥', '名字': '🔗', '盲盒': '📦', '美食': '🍳',
    '探险': '🗺️', '台词': '🎭',
    '盲人方阵': '📐', '传话': '📞', '你说我画': '✏️', '画图接龙': '🎨',
    '动物城': '🕵️', '时间特工': '⏰', '谣言': '📢',
    '人结': '🧩', '齐眉棍': '📏', '珠行万里': '⚽', '风火轮': '🌪️',
    '岛屿': '🏝️', '魔法学院': '🧙', '星际': '🚀', '疯狂厨房': '🍳',
    '人体拼字': '✋',
    '信任背摔': '🤝', '盲行': '👀',
    '红黑': '⚫', '七巧板': '🧩', '沉默': '🤫',
    '10元': '💰', '报纸塔': '🗞️',
    '沙漠': '🏜️', '鸡蛋': '🥚',
}

def guess_icon(name: str) -> str:
    for k, v in ICON_MAP.items():
        if k in name:
            return v
    return '🎲'

def parse_md_brief(md_path: Path):
    """快速解析 .md 文件，提取名称和简介"""
    text = md_path.read_text(encoding='utf-8')
    lines = text.split('\n')
    name = ''
    desc = ''
    duration = ''
    scene_tags = []

    for i, line in enumerate(lines):
        s = line.strip()
        if not name and s.startswith('# '):
            name = s[2:].strip()
        if not desc and s.startswith('>'):
            desc = s.lstrip('> ').strip()
        # 从概览表格提取时长
        if '时长' in s or ('|' in s and 'min' in s):
            m = re.search(r'(\d+–\d+\s*min|\d+–\d+\s*分钟)', s)
            if m:
                duration = m.group(1)
        # 场景标签
        if '团建' in s or '培训' in s or '通用' in s:
            if '团建' in s: scene_tags.append('团建/培训')
            break

    if not duration:
        # 从文本中搜索
        m = re.search(r'(\d+–\d+)\s*(min|分钟)', text)
        if m:
            duration = m.group(0)

    if not scene_tags:
        scene_tags = ['团建/培训']

    return name, desc, duration, scene_tags


def build_index_html():
    cats_html = []

    for cat_id, icon, cat_name, folder in CATEGORIES:
        cat_dir = GAMES_DIR / folder
        if not cat_dir.exists():
            continue

        md_files = sorted(cat_dir.glob('*.md'))
        if not md_files:
            continue

        cards = []
        for md_path in md_files:
            html_path = md_path.with_suffix('.html')
            if not html_path.exists():
                continue
            rel_link = 'games/' + folder + '/' + html_path.name

            name, desc, duration, scene_tags = parse_md_brief(md_path)
            if not name:
                name = md_path.stem
            if not desc:
                desc = '团建游戏'

            card_icon = guess_icon(name)
            # 时长标签
            dur_tag = duration.replace(' ', '') if duration else '20–40 min'
            # 场景标签
            tag_html = f'<span class="tag">{"室内/户外" if "户外" in text else "室内"}</span>'
            # 重新读取获取更准的标签
            try:
                txt = md_path.read_text(encoding='utf-8')
                if '户外' in txt and '室内' in txt:
                    tag_html = '<span class="tag">室内/户外</span>'
                elif '室内' in txt:
                    tag_html = '<span class="tag">室内</span>'
                else:
                    tag_html = '<span class="tag">室内/户外</span>'

                dur_m = re.search(r'\|\s*\*\*时长\*\*\s*\|\s*([^\n]+)', txt)
                if dur_m:
                    dur_tag = dur_m.group(1).strip()
                else:
                    dur_m2 = re.search(r'(\d+–\d+\s*(min|分钟))', txt)
                    if dur_m2:
                        dur_tag = dur_m2.group(1)
            except:
                pass

            cards.append(f'''      <a href="{rel_link}" class="card">
        <div class="card-icon">{card_icon}</div>
        <div class="card-title">{name}</div>
        <div class="card-desc">{desc}</div>
        <div class="card-tags">{tag_html}<span class="tag">{dur_tag}</span><span class="tag">{"团建/培训"}</span></div>
      </a>''')

        if cards:
            cats_html.append(f'''
    <div style="font-weight:600;color:#555;margin:18px 0 10px;">{icon} {cat_name}（{folder}）</div>
    <div class="grid" id="grid-{folder}">
{chr(10).join(cards)}
    </div>''')

    # 统计数量
    total_games = 0
    for cat_id, icon, cat_name, folder in CATEGORIES:
        cat_dir = GAMES_DIR / folder
        if cat_dir.exists():
            total_games += len(list(cat_dir.glob('*.md')))

    # 组装完整 HTML
    games_section = '\n'.join(cats_html)

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>团建 & 培训游戏库</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #f5f7fa; color: #1a1a2e; }}
    a {{ text-decoration: none; color: inherit; }}
    a:hover {{ text-decoration: none; }}

    .hero {{ background: linear-gradient(135deg, #1a1a2e 0%, #2d2d5e 50%, #1a1a2e 100%); color: #fff; padding: 60px 20px 50px; text-align: center; }}
    .hero h1 {{ font-size: 2.2em; margin-bottom: 12px; }}
    .hero p {{ font-size: 1.05em; opacity: 0.82; max-width: 600px; margin: 0 auto; line-height: 1.6; }}

    .stats {{ display: flex; justify-content: center; gap: 32px; margin-top: 32px; flex-wrap: wrap; }}
    .stat {{ text-align: center; }}
    .stat-n {{ font-size: 2em; font-weight: 700; color: #5b8cfe; }}
    .stat-l {{ font-size: 0.82em; opacity: 0.7; margin-top: 2px; }}

    .container {{ max-width: 960px; margin: 0 auto; padding: 0 20px 60px; }}

    .section {{ margin-top: 48px; }}
    .section-title {{ font-size: 1.25em; font-weight: 700; margin-bottom: 18px; padding-bottom: 10px; border-bottom: 2px solid #e2e6ee; }}

    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px; }}

    .card {{ background: #fff; border-radius: 10px; padding: 20px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); transition: box-shadow 0.2s, transform 0.15s; }}
    .card:hover {{ box-shadow: 0 4px 16px rgba(0,0,0,0.12); transform: translateY(-2px); }}
    .card-icon {{ font-size: 1.6em; margin-bottom: 8px; }}
    .card-title {{ font-size: 1em; font-weight: 600; margin-bottom: 6px; color: #1a1a2e; }}
    .card-desc {{ font-size: 0.85em; color: #555; line-height: 1.55; }}
    .card-tags {{ margin-top: 10px; display: flex; flex-wrap: wrap; gap: 6px; }}
    .tag {{ font-size: 0.75em; background: #eef2ff; color: #3366cc; padding: 2px 8px; border-radius: 4px; }}

    .flow-card {{ background: #fff; border-radius: 10px; padding: 20px 24px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); display: flex; justify-content: space-between; align-items: center; }}
    .flow-info h3 {{ font-size: 1em; font-weight: 600; margin-bottom: 4px; }}
    .flow-info p {{ font-size: 0.85em; color: #555; }}
    .flow-arrow {{ font-size: 1.2em; color: #5b8cfe; }}

    .tool-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 14px; }}
    .tool-card {{ background: #fff; border-radius: 10px; padding: 16px 20px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); display: flex; align-items: center; gap: 12px; }}
    .tool-icon {{ font-size: 1.3em; }}
    .tool-name {{ font-size: 0.9em; font-weight: 600; }}

    .search-box {{ margin: 24px 0 32px; }}
    .search-box input {{ width: 100%; padding: 12px 16px; border: 1px solid #d0d5e0; border-radius: 8px; font-size: 0.95em; background: #fff; }}
    .search-box input:focus {{ outline: none; border-color: #5b8cfe; box-shadow: 0 0 0 3px rgba(91,140,254,0.18); }}

    .footer {{ text-align: center; padding: 32px 20px; color: #888; font-size: 0.85em; }}
    .footer a {{ color: #5b8cfe; }}
  </style>
</head>
<body>

<div class="hero">
  <h1>🏕️ 团建 & 培训游戏库</h1>
  <p>面向培训老师、团建教练的实用游戏与流程资源库。所有游戏统一收录，通过标签区分使用场景。</p>
  <div class="stats">
    <div class="stat"><div class="stat-n">{total_games}</div><div class="stat-l">款游戏</div></div>
    <div class="stat"><div class="stat-n">4</div><div class="stat-l">套流程方案</div></div>
    <div class="stat"><div class="stat-n">4</div><div class="stat-l">个教练工具</div></div>
  </div>
</div>

<div class="container">

  <div class="search-box">
    <input type="text" id="search" placeholder="搜索游戏名称、目的标签或场景…" oninput="filterCards()">
  </div>

  <!-- 游戏库 -->
  <div class="section">
    <div class="section-title">🎲 游戏库（按目的分类）</div>
    <p style="font-size:0.9em;color:#555;margin-bottom:16px;">点击游戏名称查看完整规则、引导要点和复盘问题。</p>
    {games_section}
  </div>

  <!-- 团建流程方案 -->
  <div class="section">
    <div class="section-title">📋 团建流程方案</div>
    <p style="font-size:0.9em;color:#555;margin-bottom:16px;">每套方案包含：时间轴 + 游戏选配 + 引导要点 + 复盘设计。</p>
    <a href="flows/one-day/" class="flow-card" style="margin-bottom:12px;">
      <div class="flow-info"><h3>📅 一日团建模板</h3><p>总时长 6–8 小时 · 适合 15–50 人 · 破冰 + 协作 + 复盘</p></div>
      <div class="flow-arrow">→</div>
    </a>
    <a href="flows/half-day/01-schedule.html" class="flow-card" style="margin-bottom:12px;">
      <div class="flow-info"><h3>⏱️ 半日团建模板</h3><p>总时长 3–4 小时 · 适合 10–30 人 · 快速凝聚</p></div>
      <div class="flow-arrow">→</div>
    </a>
    <a href="flows/workshop/leadership-awakening.html" class="flow-card" style="margin-bottom:12px;">
      <div class="flow-info"><h3>🎓 主题工作坊模板：领导力觉醒</h3><p>总时长 2.5–3 小时 · 适合 12–24 人 · 领导力深度培训</p></div>
      <div class="flow-arrow">→</div>
    </a>
    <a href="flows/online/01-schedule.html" class="flow-card">
      <div class="flow-info"><h3>💻 线上团建模板</h3><p>总时长 2–2.5 小时 · 适合 8–30 人 · 远程团队团建</p></div>
      <div class="flow-arrow">→</div>
    </a>
  </div>

  <!-- 教练工具箱 -->
  <div class="section">
    <div class="section-title">🧰 教练工具箱</div>
    <p style="font-size:0.9em;color:#555;margin-bottom:16px;">教练/培训师专属工具，即拿即用。</p>
    <div class="tool-grid">
      <a href="toolbox/facilitation.html" class="tool-card">
        <div class="tool-icon">🗣️</div>
        <div><div class="tool-name">引导话术库</div><div style="font-size:0.8em;color:#888;margin-top:2px;">开场白、规则讲解、介入干预的话术模板</div></div>
      </a>
      <a href="toolbox/debrief.html" class="tool-card">
        <div class="tool-icon">🔍</div>
        <div><div class="tool-name">复盘引导框架</div><div style="font-size:0.8em;color:#888;margin-top:2px;">4F 模型、提问清单、典型场景复盘话术</div></div>
      </a>
      <a href="toolbox/safety.html" class="tool-card">
        <div class="tool-icon">🛡️</div>
        <div><div class="tool-name">安全与管理</div><div style="font-size:0.8em;color:#888;margin-top:2px;">户外安全清单、突发情况预案、免责声明</div></div>
      </a>
      <a href="toolbox/checklist.html" class="tool-card">
        <div class="tool-icon">✅</div>
        <div><div class="tool-name">物资与效率工具</div><div style="font-size:0.8em;color:#888;margin-top:2px;">通用物资清单、分组方法、效果评估问卷</div></div>
      </a>
    </div>
  </div>

  <!-- 使用指南 -->
  <div class="section">
    <div class="section-title">🚀 首次使用？</div>
    <div style="background:#fff;border-radius:10px;padding:20px 24px;box-shadow:0 1px 4px rgba(0,0,0,0.08);line-height:1.8;font-size:0.92em;">
      <p>👉 先读 <a href="guide.html" style="color:#3366cc;font-weight:600;">教练使用指南</a> —— 5 分钟了解如何选游戏、如何引导、如何复盘。</p>
      <p style="margin-top:10px;">每款游戏文档包含 <strong>六个章节</strong>：概览与标签 · 核心规则 · 引导要点 · 复盘问题（4F 模型）· 变体适配 · 物资清单。</p>
    </div>
  </div>

</div>

<div class="footer">
  <p>团建 & 培训游戏库 · <a href="https://github.com/aiworkdb/aiworkdb.github.io">GitHub 仓库</a> · 最后更新：2026-06-28</p>
</div>

<script>
function filterCards() {{
  var q = document.getElementById('search').value.toLowerCase();
  var grids = document.querySelectorAll('.grid, .tool-grid');
  grids.forEach(function(g) {{
    var cards = g.querySelectorAll('.card, .tool-card');
    cards.forEach(function(c) {{
      var t = c.innerText.toLowerCase();
      c.style.display = t.indexOf(q) >= 0 || q === '' ? '' : 'none';
    }});
  }});
}}
</script>

</body>
</html>'''.format(total_games=total_games, games_section=games_section)

    return html


def main():
    html = build_index_html()
    out = BASE / 'index.html'
    out.write_text(html, encoding='utf-8')
    print(f"已生成: {out}")


if __name__ == '__main__':
    main()
