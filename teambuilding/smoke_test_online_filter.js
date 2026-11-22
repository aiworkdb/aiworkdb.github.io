// 线上二级筛选的 DOM 仿真（不依赖浏览器，node 直接跑）
//   node teambuilding/smoke_test_online_filter.js
//
// 复刻 index.html 的 toggleFilter 联动 + filterCards 筛选逻辑，喂入真实卡片清单，
// 模拟真实点击序列，验证：
//   1) 💻线上分类出 8 款，「线上怎么玩」4 组各自成员数正确
//   2) 切分类时线上子类会复位（否则别的分类会被 online 条件误杀）
//   3) 协作 6 组 / 创意解题 4 组 / 破冰 4 组不受影响
//   4) 线上子类与人数/时长筛选可叠加
//   5) 异步组只有 1 款，且该组是全库唯一一款异步游戏
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
      online: (attrs.match(/data-online="([a-z]+)"/) || [])[1] || null,
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

const F = { category: 'all', people: 'all', duration: 'all', sub: 'all', idea: 'all', ice: 'all', online: 'all' };

// ---- 复刻 toggleFilter 的联动 ----
function clickCategory(value) {
  F.category = value;
  if (value !== 'collaboration') { F.sub = 'all'; }
  if (value !== 'creativity' && value !== 'problem-solving') { F.idea = 'all'; }
  if (value !== 'icebreaker') { F.ice = 'all'; }
  if (value !== 'online') { F.online = 'all'; }   // 切走线上时复位线上子类
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
      if (vis && F.online !== 'all' && card.online !== F.online) { vis = false; }
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
function reset() { F.category = 'all'; F.people = 'all'; F.duration = 'all'; F.sub = 'all'; F.idea = 'all'; F.ice = 'all'; F.online = 'all'; }

function membersOf(pred) {
  const out = [];
  grids.forEach((g) => g.cards.forEach((c) => { if (pred(c, g)) { out.push(c.id); } }));
  return out;
}
const ONLINE_ALL = membersOf((c, g) => g.id === 'grid-online');
const COLLAB_ALL = membersOf((c, g) => g.id === 'grid-collaboration');
const ICE_ALL = membersOf((c, g) => g.id === 'grid-icebreaker');
const CREA = membersOf((c, g) => g.id === 'grid-creativity');
const PROB = membersOf((c, g) => g.id === 'grid-problem-solving');

// 1) 初始：全部 85 款
reset();
const ALL = membersOf(() => true);
expect('初始全部', ALL);
if (ALL.length !== 85) { fail++; console.log('FAIL 全库卡片数 ' + ALL.length + ' != 85'); }

// 2) 线上分类出 8 款
clickCategory('online');
expect('💻线上', ONLINE_ALL);
if (ONLINE_ALL.length !== 8) { fail++; console.log('FAIL 💻线上 ' + ONLINE_ALL.length + ' != 8'); }

// 3) 四组「线上怎么玩」：成员数正确，且都真实存在于线上分类里
const ONLINE_GROUPS = { voice: 2, screen: 3, doc: 2, async: 1 };
Object.keys(ONLINE_GROUPS).forEach((k) => {
  reset();
  clickCategory('online');
  F.online = k;
  const want = membersOf((c) => c.online === k);
  expect('💻线上 + 线上怎么玩=' + k, want);
  if (want.length !== ONLINE_GROUPS[k]) {
    fail++;
    console.log('FAIL 组 ' + k + ' 成员 ' + want.length + ' != ' + ONLINE_GROUPS[k]);
  }
  const inOnline = want.filter((id) => ONLINE_ALL.indexOf(id) >= 0).length;
  if (inOnline !== want.length) {
    fail++;
    console.log('FAIL 组 ' + k + ' 有成员不在线上分类里（' + inOnline + '/' + want.length + '）');
  }
});

// 4) 四组合计必须正好覆盖 8 款（不重不漏）
reset();
clickCategory('online');
const covered = Object.keys(ONLINE_GROUPS).reduce((acc, k) => {
  F.online = k;
  return acc.concat(membersOf((c) => c.online === k));
}, []).sort();
const coveredUniq = Array.from(new Set(covered)).sort();
if (JSON.stringify(coveredUniq) !== JSON.stringify(ONLINE_ALL.slice().sort())) {
  fail++;
  console.log('FAIL 四组合计与线上 8 款不一致：' + JSON.stringify(coveredUniq));
} else {
  console.log('OK   四组合计覆盖线上 8 款（不重不漏）');
}

// 5) 异步组只有 1 款，且必须是 async-relay（全库唯一一款异步游戏）
reset();
clickCategory('online');
F.online = 'async';
expect('💻线上 + 不用同时在线', ['async-relay']);

// 6) 联动复位：💻线上(选了组) → 切到🤝协作，online 必须复位
reset();
clickCategory('online');
F.online = 'voice';
clickCategory('collaboration');
expect('💻线上(不用专用工具) → 切到🤝协作', COLLAB_ALL);

// 7) 联动复位：💻线上(选了组) → 切到🧊破冰，online 必须复位
reset();
clickCategory('online');
F.online = 'doc';
clickCategory('icebreaker');
expect('💻线上(要一份文档承载) → 切到🧊破冰', ICE_ALL);

// 8) 联动复位：🤝协作(选了子类) → 切到💻线上，sub 必须复位
reset();
clickCategory('collaboration');
F.sub = 'physical';
clickCategory('online');
expect('🤝协作(身体默契) → 切到💻线上', ONLINE_ALL);

// 9) 协作 6 组 / 破冰 4 组 / 创意解题 4 组不受线上子类影响
reset();
F.sub = 'pipeline';
expect('全部 + 协作子类=pipeline', membersOf((c) => c.sub === 'pipeline'));
reset();
F.ice = 'hype';
expect('全部 + 破冰要什么=hype', membersOf((c) => c.ice === 'hype'));
reset();
F.idea = 'define';
expect('全部 + 卡在哪一步=define', membersOf((c) => c.idea === 'define'));

// 10) 线上子类可与人数/时长叠加
reset();
clickCategory('online');
F.online = 'screen';
F.duration = 'medium';
const wantMed = membersOf((c) => c.online === 'screen' && c.duration === 'medium');
expect('💻线上 + 要一块共享屏 + 30-60min', wantMed);
if (wantMed.length === 0) { fail++; console.log('FAIL 线上+共享屏+中时长 无结果（该组合本该有解）'); }

// 11) 线上子类 + 冲突条件（小人数 + 异步组 + 60min+）→ 应为空，不应误出别的组
reset();
clickCategory('online');
F.online = 'async';
F.people = 'small';
F.duration = 'long';
const wantNone = membersOf((c) => c.online === 'async' && c.people === 'small' && c.duration === 'long');
expect('💻线上 + 不用同时在线 + 小人数 + 60min+', wantNone);

// 12) 线上子类 + 冲突条件（<10人 + 要一块共享屏）→ 只剩画图猜词（medium? 应为空或唯一）
reset();
clickCategory('online');
F.online = 'screen';
F.people = 'small';
const wantSmall = membersOf((c) => c.online === 'screen' && c.people === 'small');
expect('💻线上 + 要一块共享屏 + <10人', wantSmall);

console.log(fail === 0 ? '\nALL PASS' : '\n' + fail + ' 项失败');
process.exit(fail === 0 ? 0 : 1);
