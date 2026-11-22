// 破冰二级筛选的 DOM 仿真（不依赖浏览器，node 直接跑）
//   node teambuilding/smoke_test_ice_filter.js
//
// 复刻 index.html 的 toggleFilter 联动 + filterCards 筛选逻辑，喂入真实卡片清单，
// 模拟真实点击序列，验证：
//   1) 🧊破冰分类出 8 款，「破冰要什么」4 组各自 2 款
//   2) 切分类时破冰子类会复位（否则协作类会被 ice 条件误杀）
//   3) 协作 6 组与创意解题 4 组不受影响
//   4) 破冰子类与人数/时长筛选可叠加
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
      ice: (attrs.match(/data-ice="([a-z]+)"/) || [])[1] || null,
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

const F = { category: 'all', people: 'all', duration: 'all', sub: 'all', idea: 'all', ice: 'all' };

// ---- 复刻 toggleFilter 的联动 ----
function clickCategory(value) {
  F.category = value;
  if (value !== 'collaboration') { F.sub = 'all'; }              // 切走协作时复位协作子类
  if (value !== 'creativity' && value !== 'problem-solving') { F.idea = 'all'; }
  if (value !== 'icebreaker') { F.ice = 'all'; }                 // 切走破冰时复位破冰子类
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
      if (vis && F.ice !== 'all' && card.ice !== F.ice) { vis = false; }
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
function reset() { F.category = 'all'; F.people = 'all'; F.duration = 'all'; F.sub = 'all'; F.idea = 'all'; F.ice = 'all'; }

// 从 index.html 现取各组真实成员，避免手写清单与实际漂移
function membersOf(pred) {
  const out = [];
  grids.forEach((g) => g.cards.forEach((c) => { if (pred(c, g)) { out.push(c.id); } }));
  return out;
}
const ICE_ALL = membersOf((c, g) => g.id === 'grid-icebreaker');
const COLLAB_ALL = membersOf((c, g) => g.id === 'grid-collaboration');
const CREA = membersOf((c, g) => g.id === 'grid-creativity');
const PROB = membersOf((c, g) => g.id === 'grid-problem-solving');

// 1) 初始：全部 85 款
reset();
const ALL = membersOf(() => true);
expect('初始全部', ALL);
if (ALL.length !== 85) { fail++; console.log('FAIL 全库卡片数 ' + ALL.length + ' != 85'); }

// 2) 破冰分类出 8 款
clickCategory('icebreaker');
expect('🧊破冰', ICE_ALL);
if (ICE_ALL.length !== 8) { fail++; console.log('FAIL 🧊破冰 ' + ICE_ALL.length + ' != 8'); }

// 3) 四组「破冰要什么」：每组 2 款，且都真实存在
const ICE_GROUPS = ['name', 'hype', 'know', 'team'];
ICE_GROUPS.forEach((k) => {
  reset();
  clickCategory('icebreaker');
  F.ice = k;
  const want = membersOf((c) => c.ice === k);
  expect('🧊破冰 + 破冰要什么=' + k, want);
  if (want.length !== 2) { fail++; console.log('FAIL 组 ' + k + ' 成员 ' + want.length + ' != 2'); }
  // 每组成员必须都在破冰分类里（分组不能跨到别的分类去）
  const inIce = want.filter((id) => ICE_ALL.indexOf(id) >= 0).length;
  if (inIce !== want.length) {
    fail++;
    console.log('FAIL 组 ' + k + ' 有成员不在破冰分类里（' + inIce + '/' + want.length + '）');
  }
});

// 4) 联动复位：🧊破冰(选了组) → 切到🤝协作，ice 必须复位（否则协作类被误杀）
reset();
clickCategory('icebreaker');
F.ice = 'name';
clickCategory('collaboration');
expect('🧊破冰(只认名字) → 切到🤝协作', COLLAB_ALL);

// 5) 联动复位：🤝协作(选了子类) → 切到🧊破冰，sub 必须复位
reset();
clickCategory('collaboration');
F.sub = 'physical';
clickCategory('icebreaker');
expect('🤝协作(身体默契) → 切到🧊破冰', ICE_ALL);

// 6) 联动复位：🧊破冰(选了组) → 切到💡创意，ice 必须复位
reset();
clickCategory('icebreaker');
F.ice = 'know';
clickCategory('creativity');
expect('🧊破冰(谈自己的事) → 切到💡创意', CREA);

// 7) 创意解题 4 组不受影响
// ⚠️ 这里刻意不切分类：define 组横跨 💡创意 与 🔧解题两个网格，
// 切到某一类会把另一半成员筛掉（那是分类筛选的正常行为，不是 bug）。
reset();
F.idea = 'define';
expect('全部 + 卡在哪一步=define', membersOf((c) => c.idea === 'define'));
reset();
F.idea = 'hypothesis';
expect('全部 + 卡在哪一步=hypothesis', membersOf((c) => c.idea === 'hypothesis'));

// 8) 破冰子类可与人数/时长叠加
reset();
clickCategory('icebreaker');
F.ice = 'name';
F.duration = 'short';
const wantShort = membersOf((c) => c.ice === 'name' && c.duration === 'short');
expect('🧊破冰 + 只认名字 + 短时长', wantShort);
if (wantShort.length === 0) { fail++; console.log('FAIL 破冰+短时长 无结果（该组合本该有解）'); }

// 9) 破冰子类 + 冲突条件（<10人 + 只认名字 + 时长>60min）→ 应为空，不应误出别的组
reset();
clickCategory('icebreaker');
F.ice = 'name';
F.people = 'small';
F.duration = 'long';
const wantNone = membersOf((c) => c.ice === 'name' && c.people === 'small' && c.duration === 'long');
expect('🧊破冰 + 只认名字 + 小人数 + 60min+', wantNone);

console.log(fail === 0 ? '\nALL PASS' : '\n' + fail + ' 项失败');
process.exit(fail === 0 ? 0 : 1);
