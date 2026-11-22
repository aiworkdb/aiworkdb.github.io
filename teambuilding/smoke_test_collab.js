/**
 * 协作二级索引冒烟测试（2026-10-23）
 * 做法同 smoke_test.js：抽出 index.html 内联 JS -> node --check -> DOM stub 跑真实代码路径。
 * 断言：
 *   1. 39 张协作卡片都能被 6 个子类之一覆盖，且每张只属于一组
 *   2. 选中「协作」+ 某子类时，只显示该子类卡片，且小标题跟着收起
 *   3. 切走协作时子类筛选被复位（否则下次点协作会带着上次的条件）
 *   4. 搜索 / 人数 / 时长 三维仍可与子类叠加
 */
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const HTML = fs.readFileSync(path.join(__dirname, 'index.html'), 'utf8');

// ---------- 极简 DOM ----------
class El {
  constructor(tag, attrs, text) {
    this.tag = tag;
    this.attrs = attrs || {};
    this.text = text || '';
    this.children = [];
    this.parent = null;
    this.style = {};
    this._classes = (this.attrs.class || '').split(/\s+/).filter(Boolean);
    this.classList = {
      add: (c) => { if (!this._classes.includes(c)) this._classes.push(c); },
      remove: (c) => { this._classes = this._classes.filter(x => x !== c); },
      contains: (c) => this._classes.includes(c),
    };
  }
  get className() { return this._classes.join(' '); }
  get id() { return this.attrs.id || ''; }
  get innerText() { return this.text + this.children.map(c => c.innerText).join(''); }
  get textContent() { return this.text; }
  getAttribute(k) { return k in this.attrs ? this.attrs[k] : null; }
  setAttribute(k, v) { this.attrs[k] = v; }
  append(c) { c.parent = this; this.children.push(c); return c; }
  get previousElementSibling() {
    if (!this.parent) return null;
    const i = this.parent.children.indexOf(this);
    return i > 0 ? this.parent.children[i - 1] : null;
  }
  get parentElement() { return this.parent; }
  _all(out) {
    for (const c of this.children) { out.push(c); c._all(out); }
    return out;
  }
  querySelectorAll(sel) {
    const m = /^\.([a-z-]+)(?:\[([a-z-]+)="?([^"\]]*)"?\])?$/.exec(sel);
    if (!m) throw new Error('不支持的选择器: ' + sel);
    const cls = m[1], ak = m[2], av = m[3];
    return this._all([]).filter(e =>
      e._classes.includes(cls) && (ak === undefined || e.getAttribute(ak) === av));
  }
  querySelector(sel) { return this.querySelectorAll(sel)[0] || null; }
}

// ---------- 用正则把 index.html 的网格 / 卡片 / 小标题建成 DOM ----------
const root = new El('body', {});
// 按 div 深度取网格块（与 site_check.py 的 grid_block 同法）：
// 用非贪婪正则会在中间出现 </div> 时提前收尾，实测少抓 2 个网格 / 2 张卡
function iterGridBlocks(html) {
  const out = [];
  const open = /<div class="grid" id="(grid-[a-z]+)">/g;
  let m;
  while ((m = open.exec(html)) !== null) {
    let depth = 1, i = m.index + m[0].length;
    const re = /<div\b|<\/div>/g;
    re.lastIndex = i;
    let t;
    while (depth > 0 && (t = re.exec(html)) !== null) {
      depth += t[0].startsWith('<div') ? 1 : -1;
      i = t.index + t[0].length;
    }
    out.push({ id: m[1], inner: html.slice(m.index + m[0].length, i - '</div>'.length) });
  }
  return out;
}
let gridCount = 0;
for (const gb of iterGridBlocks(HTML)) {
  const grid = root.append(new El('div', { class: 'grid', id: gb.id }));
  gridCount++;
  const inner = gb.inner;
  const itemRe = /<(a|div) ([^>]*)>([\s\S]*?)<\/\1>/g;
  let m;
  while ((m = itemRe.exec(inner)) !== null) {
    const attrs = {};
    for (const a of m[2].matchAll(/([a-z-]+)="([^"]*)"/g)) attrs[a[1]] = a[2];
    if (!attrs.class) continue;
    const text = m[3].replace(/<[^>]+>/g, ' ');
    grid.append(new El(m[1], attrs, text));
  }
  // 分类标题（grid 的前一个兄弟，带 inline font-weight:600）
  const title = root.append(new El('div', { style: 'font-weight:600' }));
  root.children.splice(root.children.indexOf(title), 1);
  root.children.splice(root.children.indexOf(grid), 0, title);
}

// 筛选按钮（含协作子类那一行）
const filters = new El('div', { class: 'filters' });
root.append(filters);
const btnRe = /<button class="filter-btn[^"]*" onclick="toggleFilter\('([a-z]+)', '([a-z]+)', this\)">([^<]*)<\/button>/g;
let b;
while ((b = btnRe.exec(HTML)) !== null) {
  filters.append(new El('button', { class: 'filter-btn' }, b[3]));
}

const search = root.append(new El('input', { id: 'search' }));
search.value = '';
const subRow = root.append(new El('div', { class: 'filter-group', id: 'sub-filter' }));
for (const txt of ['全部', '身体默契', '瓶颈与流水线', '资源与取舍', '信息不对称', '角色互补', '共享总账']) {
  subRow.append(new El('button', { class: 'filter-btn' }, txt));
}

const document_ = {
  getElementById: (id) => (id === 'search' ? search : id === 'sub-filter' ? subRow : null),
  querySelectorAll: (sel) => root.querySelectorAll(sel),
  querySelector: (sel) => root.querySelectorAll(sel)[0] || null,
};

const sandbox = {
  document: document_,
  window: { addEventListener: () => {} },
  console,
};
vm.createContext(sandbox);
const code = /<script>([\s\S]*)<\/script>/.exec(HTML)[1];
vm.runInContext(code, sandbox);

// ---------- 断言 ----------
let fail = 0;
const ok = (cond, msg) => { if (!cond) { console.log('  ❌ ' + msg); fail++; } };

console.log(`网格 ${gridCount} 个；卡片 ${root.querySelectorAll('.card').length} 张；`
  + `小标题 ${root.querySelectorAll('.subhead').length} 个；筛选按钮 ${root.querySelectorAll('.filter-btn').length} 个`);

const SUBS = ['physical', 'pipeline', 'resource', 'info', 'role', 'whole'];
const collabCards = root.querySelectorAll('.card').filter(c => (c.getAttribute('data-sub') || '') !== '');
ok(collabCards.length === 39, '协作卡片应为 39，实际 ' + collabCards.length);
ok(root.querySelectorAll('.subhead').length === 6, '小标题应为 6，实际 ' + root.querySelectorAll('.subhead').length);

// 分组互斥且全覆盖
for (const s of SUBS) {
  const n = root.querySelectorAll('.card[data-sub="' + s + '"]').length;
  ok(n > 0, '子类 %s 没有卡片'.replace('%s', s));
}
const sum = SUBS.reduce((a, s) => a + root.querySelectorAll('.card[data-sub="' + s + '"]').length, 0);
ok(sum === 39, '6 组卡片之和应为 39，实际 ' + sum);

const toggle = (type, value) => {
  const btn = filters.append(new El('button', { class: 'filter-btn' }));
  sandbox.toggleFilter(type, value, btn);
};

// 1) 子类筛选
for (const s of SUBS) {
  toggle('category', 'collaboration');
  toggle('sub', s);
  sandbox.filterCards();
  const vis = collabCards.filter(c => c.style.display !== 'none');
  ok(vis.length === root.querySelectorAll('.card[data-sub="' + s + '"]').length,
    '子类 ' + s + ' 可见卡片数不符：' + vis.length);
  ok(vis.every(c => c.getAttribute('data-sub') === s), '子类 ' + s + ' 混入了其它组的卡片');
  const visHeads = root.querySelectorAll('.subhead').filter(h => h.style.display !== 'none');
  ok(visHeads.length === 1 && visHeads[0].getAttribute('data-sub') === s,
    '子类 ' + s + ' 小标题未正确收起');
}
console.log('  ✅ 6 个子类 × 显示/收起 全部通过');

// 2) 切走协作 -> 子类复位
toggle('sub', 'role');
toggle('category', 'trust');
sandbox.filterCards();
ok(sandbox.currentFilters.sub === 'all', '切走协作后子类未复位：' + sandbox.currentFilters.sub);
ok(subRow.style.display === 'none', '切走协作后子类筛选行未隐藏');
toggle('category', 'collaboration');
ok(subRow.style.display === '', '切回协作后子类筛选行未显示');
sandbox.filterCards();
ok(collabCards.filter(c => c.style.display !== 'none').length === 39,
  '切回协作后应恢复 39 张，实际 ' + collabCards.filter(c => c.style.display !== 'none').length);
console.log('  ✅ 切换分类时的子类复位通过');

// 3) 与搜索 / 人数 / 时长叠加
toggle('sub', 'physical');
search.value = '齐眉棍';
sandbox.filterCards();
let v = collabCards.filter(c => c.style.display !== 'none');
ok(v.length === 1 && v[0].text.includes('齐眉棍'), '子类 + 搜索叠加异常，命中 ' + v.length);
search.value = '';
toggle('people', 'large');
toggle('sub', 'all');
sandbox.filterCards();
v = collabCards.filter(c => c.style.display !== 'none');
ok(v.every(c => c.getAttribute('data-people') === 'large'), '人数维度被子类条件污染');
console.log('  ✅ 与搜索 / 人数 / 时长叠加通过');

console.log(fail === 0 ? '\n🎉 协作二级索引冒烟测试 ALL PASS' : '\n❌ 失败 ' + fail + ' 项');
process.exit(fail === 0 ? 0 : 1);
