// 沟通二级筛选的 DOM 仿真（不依赖浏览器，node 直接跑）
//   node teambuilding/smoke_test_comm_filter.js
//
// 复刻 index.html 的 toggleFilter 联动 + filterCards 筛选逻辑，喂入真实卡片清单，
// 模拟真实点击序列，验证：
//   1) 💬沟通分类出 8 款，「沟通坏在哪一环」4 组各自成员数正确
//   2) 切分类时沟通子类会复位（否则别的分类会被 comm 条件误杀）
//   3) 协作 6 组 / 创意解题 4 组 / 破冰 4 组 / 线上 4 组不受影响
//   4) 沟通子类与人数/时长筛选可叠加
//   5) ⚖️说不拢 那组的两款都不支持 20+ 人（与挑款页「建议 6 人以上」不冲突：
//      它的上限就是 12 人），叠加 20+ 人时应为空且不误出别的组
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
      comm: (attrs.match(/data-comm="([a-z]+)"/) || [])[1] || null,
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

const F = { category: 'all', people: 'all', duration: 'all', sub: 'all', idea: 'all', ice: 'all', online: 'all', comm: 'all' };

// ---- 复刻 toggleFilter 的联动 ----
function clickCategory(value) {
  F.category = value;
  if (value !== 'collaboration') { F.sub = 'all'; }
  if (value !== 'creativity' && value !== 'problem-solving') { F.idea = 'all'; }
  if (value !== 'icebreaker') { F.ice = 'all'; }
  if (value !== 'online') { F.online = 'all'; }
  if (value !== 'communication') { F.comm = 'all'; }   // 切走沟通时复位沟通子类
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
      if (vis && F.comm !== 'all' && card.comm !== F.comm) { vis = false; }
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
function reset() {
  F.category = 'all'; F.people = 'all'; F.duration = 'all';
  F.sub = 'all'; F.idea = 'all'; F.ice = 'all'; F.online = 'all'; F.comm = 'all';
}
function membersOf(pred) {
  const out = [];
  grids.forEach((g) => g.cards.forEach((c) => { if (pred(c, g)) { out.push(c.id); } }));
  return out;
}
const COMM_ALL = membersOf((c, g) => g.id === 'grid-communication');
const COLLAB_ALL = membersOf((c, g) => g.id === 'grid-collaboration');
const ICE_ALL = membersOf((c, g) => g.id === 'grid-icebreaker');
const ONLINE_ALL = membersOf((c, g) => g.id === 'grid-online');

// 1) 初始：全部 85 款
reset();
const ALL = membersOf(() => true);
expect('初始全部', ALL);
if (ALL.length !== 85) { fail++; console.log('FAIL 全库卡片数 ' + ALL.length + ' != 85'); }

// 2) 沟通分类出 8 款
clickCategory('communication');
expect('💬沟通', COMM_ALL);
if (COMM_ALL.length !== 8) { fail++; console.log('FAIL 💬沟通 ' + COMM_ALL.length + ' != 8'); }

// 3) 四组「沟通坏在哪一环」：成员数正确，且都真实存在于沟通分类里
const COMM_GROUPS = { express: 2, relay: 2, pool: 2, clash: 2 };
Object.keys(COMM_GROUPS).forEach((k) => {
  reset();
  clickCategory('communication');
  F.comm = k;
  const want = membersOf((c) => c.comm === k);
  expect('💬沟通 + 坏在哪一环=' + k, want);
  if (want.length !== COMM_GROUPS[k]) {
    fail++;
    console.log('FAIL 组 ' + k + ' 成员 ' + want.length + ' != ' + COMM_GROUPS[k]);
  }
  const inComm = want.filter((id) => COMM_ALL.indexOf(id) >= 0).length;
  if (inComm !== want.length) {
    fail++;
    console.log('FAIL 组 ' + k + ' 有成员不在沟通分类里（' + inComm + '/' + want.length + '）');
  }
});

// 4) 四组合计必须正好覆盖 8 款（不重不漏）
reset();
clickCategory('communication');
const covered = Object.keys(COMM_GROUPS).reduce((acc, k) => {
  F.comm = k;
  return acc.concat(membersOf((c) => c.comm === k));
}, []).sort();
const coveredUniq = Array.from(new Set(covered)).sort();
if (JSON.stringify(coveredUniq) !== JSON.stringify(COMM_ALL.slice().sort())) {
  fail++;
  console.log('FAIL 四组合计与沟通 8 款不一致：' + JSON.stringify(coveredUniq));
} else {
  console.log('OK   四组合计覆盖沟通 8 款（不重不漏）');
}

// 5) 每组具体成员（与 comm.html 的分组一致，改组时这里会先炸）
const EXPECT_MEMBERS = {
  express: ['blind-polygon', 'draw-guess'],
  relay: ['telephone-game', 'rumor-factory'],
  pool: ['drawing-relay', 'animal-detective'],
  clash: ['courtroom-debate', 'time-agents'],
};
Object.keys(EXPECT_MEMBERS).forEach((k) => {
  const got = membersOf((c) => c.comm === k).sort();
  if (JSON.stringify(got) !== JSON.stringify(EXPECT_MEMBERS[k].slice().sort())) {
    fail++;
    console.log('FAIL 组 ' + k + ' 成员不符：' + JSON.stringify(got));
  }
});
console.log('OK   四组成员与挑款页一致');

// 6) 联动复位：💬沟通(选了组) → 切到🤝协作，comm 必须复位
reset();
clickCategory('communication');
F.comm = 'express';
clickCategory('collaboration');
expect('💬沟通(说不清) → 切到🤝协作', COLLAB_ALL);

// 7) 联动复位：💬沟通(选了组) → 切到🧊破冰，comm 必须复位
reset();
clickCategory('communication');
F.comm = 'clash';
clickCategory('icebreaker');
expect('💬沟通(说不拢) → 切到🧊破冰', ICE_ALL);

// 8) 联动复位：💬沟通(选了组) → 切到💻线上，comm 必须复位
reset();
clickCategory('communication');
F.comm = 'pool';
clickCategory('online');
expect('💬沟通(凑不齐) → 切到💻线上', ONLINE_ALL);

// 9) 反向：🤝协作(选了子类) → 切到💬沟通，sub 必须复位
reset();
clickCategory('collaboration');
F.sub = 'physical';
clickCategory('communication');
expect('🤝协作(身体默契) → 切到💬沟通', COMM_ALL);

// 10) 协作 6 组 / 破冰 4 组 / 创意解题 4 组 / 线上 4 组不受沟通子类影响
reset();
F.sub = 'pipeline';
expect('全部 + 协作子类=pipeline', membersOf((c) => c.sub === 'pipeline'));
reset();
F.ice = 'hype';
expect('全部 + 破冰要什么=hype', membersOf((c) => c.ice === 'hype'));
reset();
F.idea = 'define';
expect('全部 + 卡在哪一步=define', membersOf((c) => c.idea === 'define'));
reset();
F.online = 'screen';
expect('全部 + 线上怎么玩=screen', membersOf((c) => c.online === 'screen'));

// 11) 沟通子类可与人数/时长叠加
reset();
clickCategory('communication');
F.comm = 'relay';
F.duration = 'short';
const wantShort = membersOf((c) => c.comm === 'relay' && c.duration === 'short');
expect('💬沟通 + 传不准 + <30min', wantShort);
if (wantShort.length === 0) { fail++; console.log('FAIL 沟通+传不准+短时长 无结果（该组合本该有解）'); }

reset();
clickCategory('communication');
F.comm = 'clash';
F.people = 'small';
expect('💬沟通 + 说不拢 + <10人', membersOf((c) => c.comm === 'clash' && c.people === 'small'));

// 12) 沟通子类 + 冲突条件（20+人 + 说不拢）→ 应为空，且不应误出别的组
reset();
clickCategory('communication');
F.comm = 'clash';
F.people = 'large';
const wantNone = membersOf((c) => c.comm === 'clash' && c.people === 'large');
expect('💬沟通 + 说不拢 + 20+人（应为 0 款）', wantNone);
if (wantNone.length !== 0) { fail++; console.log('FAIL 该组合本该为空'); }

console.log(fail === 0 ? '\nALL PASS' : '\n' + fail + ' 项失败');
process.exit(fail === 0 ? 0 : 1);
