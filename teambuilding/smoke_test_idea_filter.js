// 创意与解题二级筛选的 DOM 仿真（不依赖浏览器，node 直接跑）
//   node teambuilding/smoke_test_idea_filter.js
//
// 复刻 index.html 的 toggleFilter 联动 + filterCards 筛选逻辑，喂入真实卡片清单，
// 模拟真实点击序列，验证：
//   1) 💡创意 / 🔧解题 两个分类各自只出 5 款
//   2) 「卡在哪一步」4 组各自跨两个分类的成员集合正确
//   3) 切分类时不相干的子类会复位（否则协作类会被 idea 条件误杀、反之亦然）
//   4) 协作类原有的 6 组子类不受影响
const fs = require('fs');
const path = require('path');

const TB = path.join(__dirname);
const html = fs.readFileSync(path.join(TB, 'index.html'), 'utf8');

// ---- 从真实 HTML 抽取网格与卡片 ----
const gridRe = /<div class="grid" id="(grid-[a-z-]+)">([\s\S]*?)<\/div>\s*(?=\n\s*(?:<!--|<div class="grid"))/g;
const grids = [];
let gm;
while ((gm = gridRe.exec(html)) !== null) {
  const cards = [];
  const cardRe = /<a href="games\/([a-z-]+)\/([a-z0-9-]+)\.html" class="card"([^>]*)>/g;
  let cm;
  while ((cm = cardRe.exec(gm[2])) !== null) {
    const attrs = cm[3];
    cards.push({
      id: cm[2],
      idea: (attrs.match(/data-idea="([a-z]+)"/) || [])[1] || null,
      sub: (attrs.match(/data-sub="([a-z]+)"/) || [])[1] || null,
      people: (attrs.match(/data-people="([a-z]+)"/) || [])[1] || null,
      duration: (attrs.match(/data-duration="([a-z]+)"/) || [])[1] || null,
    });
  }
  grids.push({ id: gm[1], cards });
}
if (grids.length !== 8) {
  console.log('FAIL 网格数 ' + grids.length + ' != 8');
  process.exit(1);
}

const F = { category: 'all', people: 'all', duration: 'all', sub: 'all', idea: 'all' };

// ---- 复刻 toggleFilter 的联动 ----
function clickCategory(value) {
  F.category = value;
  if (value !== 'collaboration') { F.sub = 'all'; }          // 切走协作时复位协作子类
  if (value !== 'creativity' && value !== 'problem-solving') { F.idea = 'all'; }
  // 注意：💡创意 ↔ 🔧解题 之间切换时 idea 保留（每组都横跨两个分类）
}

// ---- 复刻 filterCards 的筛选逻辑 ----
function visible() {
  const out = [];
  grids.forEach((grid) => {
    grid.cards.forEach((card) => {
      let vis = true;
      if (vis && F.category !== 'all' && grid.id.replace('grid-', '') !== F.category) { vis = false; }
      if (vis && F.idea !== 'all' && card.idea !== F.idea) { vis = false; }
      if (vis && F.sub !== 'all' && card.sub !== F.sub) { vis = false; }
      if (vis && F.people !== 'all' && card.people !== F.people) { vis = false; }
      if (vis && F.duration !== 'all' && card.duration !== F.duration) { vis = false; }
      if (vis) { out.push(card.id); }
    });
  });
  return out.sort();
}

let fail = 0;
function expect(label, want) {
  const got = visible();
  const w = want.slice().sort();
  if (JSON.stringify(got) !== JSON.stringify(w)) {
    fail++;
    console.log('FAIL ' + label + '\n  期望 ' + JSON.stringify(w) + '\n  实得 ' + JSON.stringify(got));
  } else {
    console.log('OK   ' + label + ' -> ' + got.length + ' 款');
  }
}
function reset() { F.category = 'all'; F.people = 'all'; F.duration = 'all'; F.sub = 'all'; F.idea = 'all'; }

// 从 index.html 现取各组真实成员，避免手写清单与实际漂移
function membersOf(pred) {
  const out = [];
  grids.forEach((g) => g.cards.forEach((c) => { if (pred(c, g)) { out.push(c.id); } }));
  return out;
}
const CREA = membersOf((c, g) => g.id === 'grid-creativity');
const PROB = membersOf((c, g) => g.id === 'grid-problem-solving');
const COLLAB_ALL = membersOf((c, g) => g.id === 'grid-collaboration');
const COLLAB_PHYS = membersOf((c) => c.sub === 'physical');

// 1) 初始：全部 85 款
reset();
const ALL = membersOf(() => true);
expect('初始全部', ALL);
if (ALL.length !== 85) { fail++; console.log('FAIL 全库卡片数 ' + ALL.length + ' != 85'); }

// 2) 两个分类各 5 款
clickCategory('creativity');
expect('💡创意', CREA);
if (CREA.length !== 5) { fail++; console.log('FAIL 💡创意 ' + CREA.length + ' != 5'); }
clickCategory('problem-solving');
expect('🔧解题', PROB);
if (PROB.length !== 5) { fail++; console.log('FAIL 🔧解题 ' + PROB.length + ' != 5'); }

// 3) 四组「卡在哪一步」：跨两个分类的成员集合
reset();
const GROUPS = ['define', 'hypothesis', 'constraint', 'deliberate'];
GROUPS.forEach((k) => {
  reset();
  F.idea = k;
  const want = membersOf((c) => c.idea === k);
  expect('全部+卡在哪一步=' + k, want);
  if (want.length === 0) { fail++; console.log('FAIL 组 ' + k + ' 无成员'); }
  // 该组成员必须横跨💡/🔧两个分类（这正是本次二级索引的意义）
  const inCrea = want.filter((id) => CREA.indexOf(id) >= 0).length;
  const inProb = want.filter((id) => PROB.indexOf(id) >= 0).length;
  if (inCrea === 0 || inProb === 0) {
    fail++;
    console.log('FAIL 组 ' + k + ' 未横跨两个分类（💡' + inCrea + ' / 🔧' + inProb + '）');
  }
});

// 4) 联动复位：💡创意(选了组) → 切到🤝协作，idea 必须复位（否则协作类被误杀）
reset();
clickCategory('creativity');
F.idea = 'define';
clickCategory('collaboration');
expect('💡创意(先定义问题) → 切到🤝协作', COLLAB_ALL);

// 5) 联动复位：🤝协作(选了子类) → 切到💡创意，sub 必须复位
reset();
clickCategory('collaboration');
F.sub = 'physical';
clickCategory('creativity');
expect('🤝协作(身体默契) → 切到💡创意', CREA);

// 5b) 跨分类保留：💡创意(选了组) → 切到🔧解题，idea 保留（每组都横跨两个分类）
reset();
clickCategory('creativity');
F.idea = 'define';
clickCategory('problem-solving');
expect('💡创意(先定义问题) → 切到🔧解题', ['cyber-maze']);

// 6) 协作类原有 6 组子类不受影响
reset();
clickCategory('collaboration');
F.sub = 'physical';
expect('🤝协作+身体默契', COLLAB_PHYS);
if (COLLAB_PHYS.length !== 5) { fail++; console.log('FAIL 协作身体默契 ' + COLLAB_PHYS.length + ' != 5'); }

console.log(fail === 0 ? '\nALL PASS' : '\n' + fail + ' 项失败');
process.exit(fail === 0 ? 0 : 1);
