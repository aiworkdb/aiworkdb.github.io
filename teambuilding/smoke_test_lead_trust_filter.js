// 👑领导力 / 🔐信任 二级筛选的 DOM 仿真（不依赖浏览器，node 直接跑）
//   node teambuilding/smoke_test_lead_trust_filter.js
//
// 复刻 index.html 的 toggleFilter 联动 + filterCards 筛选逻辑，喂入真实卡片清单，
// 模拟真实点击序列，验证：
//   1) 👑领导力出 6 款、🔐信任出 6 款；两类的 3 组各自成员数正确
//   2) 切分类时对应的子类会复位（否则别的分类会被 lead / trust 条件误杀）
//   3) 协作 6 组 / 创意解题 4 组 / 破冰 4 组 / 线上 4 组 / 沟通 4 组不受影响
//   4) 子类与人数筛选可叠加；🔑授权 组在「<10 人」下无解（两款都要求 8 人以上且分组）
//   5) 两类的 3 组都不重不漏地覆盖本类 6 款
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
      lead: (attrs.match(/data-lead="([a-z]+)"/) || [])[1] || null,
      trust: (attrs.match(/data-trust="([a-z]+)"/) || [])[1] || null,
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

const F = {
  category: 'all', people: 'all', duration: 'all',
  sub: 'all', idea: 'all', ice: 'all', online: 'all', comm: 'all',
  lead: 'all', trust: 'all',
};

// ---- 复刻 toggleFilter 的联动（切走即复位）----
function clickCategory(value) {
  F.category = value;
  if (value !== 'collaboration') { F.sub = 'all'; }
  if (value !== 'creativity' && value !== 'problem-solving') { F.idea = 'all'; }
  if (value !== 'icebreaker') { F.ice = 'all'; }
  if (value !== 'online') { F.online = 'all'; }
  if (value !== 'communication') { F.comm = 'all'; }
  if (value !== 'leadership') { F.lead = 'all'; }
  if (value !== 'trust') { F.trust = 'all'; }
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
      if (vis && F.lead !== 'all' && card.lead !== F.lead) { vis = false; }
      if (vis && F.trust !== 'all' && card.trust !== F.trust) { vis = false; }
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
  Object.keys(F).forEach((k) => { F[k] = 'all'; });
}
function membersOf(pred) {
  const out = [];
  grids.forEach((g) => g.cards.forEach((c) => { if (pred(c, g)) { out.push(c.id); } }));
  return out;
}
const LEAD_ALL = membersOf((c, g) => g.id === 'grid-leadership');
const TRUST_ALL = membersOf((c, g) => g.id === 'grid-trust');
const COLLAB_ALL = membersOf((c, g) => g.id === 'grid-collaboration');
const COMM_ALL = membersOf((c, g) => g.id === 'grid-communication');
const ONLINE_ALL = membersOf((c, g) => g.id === 'grid-online');

// 期望分组（与 lead.html / trust.html 的表格一致，改组时这里会先炸）
const LEAD_MEMBERS = {
  decide: ['red-black-game', 'vice-city-empire'],
  delegate: ['stellar-conqueror', 'heavenly-quest'],
  informal: ['silent-leader', 'tangram'],
};
const TRUST_MEMBERS = {
  body: ['trust-fall', 'blind-walk'],
  truth: ['spy-family-trust', 'chef-undercover'],
  outcome: ['baxian-crossing-sea', 'three-monkeys-defuse'],
};

// 1) 初始全部 85 款
reset();
const ALL = membersOf(() => true);
expect('初始全部', ALL);
if (ALL.length !== 85) { fail++; console.log('FAIL 全库卡片数 ' + ALL.length + ' != 85'); }

// 2) 两类各 6 款
clickCategory('leadership');
expect('👑领导力', LEAD_ALL);
if (LEAD_ALL.length !== 6) { fail++; console.log('FAIL 👑领导力 ' + LEAD_ALL.length + ' != 6'); }
reset();
clickCategory('trust');
expect('🔐信任', TRUST_ALL);
if (TRUST_ALL.length !== 6) { fail++; console.log('FAIL 🔐信任 ' + TRUST_ALL.length + ' != 6'); }

// 3) 三组各自成员数正确、不越出本分类、与挑款页一致
function checkGroups(label, attr, catAll, MEMBERS) {
  Object.keys(MEMBERS).forEach((k) => {
    const want = membersOf((c) => c[attr] === k);
    if (JSON.stringify(want.slice().sort()) !== JSON.stringify(MEMBERS[k].slice().sort())) {
      fail++;
      console.log('FAIL ' + label + ' 组 ' + k + ' 成员不符：' + JSON.stringify(want));
    }
    if (want.length !== MEMBERS[k].length) {
      fail++;
      console.log('FAIL ' + label + ' 组 ' + k + ' 成员数 ' + want.length);
    }
    const inside = want.filter((id) => catAll.indexOf(id) >= 0).length;
    if (inside !== want.length) {
      fail++;
      console.log('FAIL ' + label + ' 组 ' + k + ' 有成员不在本分类里（' + inside + '/' + want.length + '）');
    }
    reset();
    clickCategory(attr === 'lead' ? 'leadership' : 'trust');
    F[attr] = k;
    expect(label + ' + ' + k, want);
  });
  console.log('OK   ' + label + ' 三组成员与挑款页一致');
}
checkGroups('👑领导力', 'lead', LEAD_ALL, LEAD_MEMBERS);
checkGroups('🔐信任', 'trust', TRUST_ALL, TRUST_MEMBERS);

// 4) 三组合计不重不漏地覆盖本类 6 款
function checkCover(label, attr, catAll, MEMBERS) {
  reset();
  clickCategory(attr === 'lead' ? 'leadership' : 'trust');
  const covered = Object.keys(MEMBERS).reduce((acc, k) => acc.concat(membersOf((c) => c[attr] === k)), []);
  const uniq = Array.from(new Set(covered)).sort();
  if (JSON.stringify(uniq) !== JSON.stringify(catAll.slice().sort())) {
    fail++;
    console.log('FAIL ' + label + ' 三组合计与本类 6 款不一致：' + JSON.stringify(uniq));
  } else {
    console.log('OK   ' + label + ' 三组合计覆盖 6 款（不重不漏）');
  }
}
checkCover('👑领导力', 'lead', LEAD_ALL, LEAD_MEMBERS);
checkCover('🔐信任', 'trust', TRUST_ALL, TRUST_MEMBERS);

// 5) 联动复位：选了子类后切到别的分类，必须复位
reset();
clickCategory('leadership');
F.lead = 'delegate';
clickCategory('collaboration');
expect('👑领导力(授权) → 切到🤝协作', COLLAB_ALL);

reset();
clickCategory('trust');
F.trust = 'truth';
clickCategory('communication');
expect('🔐信任(真话) → 切到💬沟通', COMM_ALL);

reset();
clickCategory('leadership');
F.lead = 'informal';
clickCategory('trust');
expect('👑领导力(不带权) → 切到🔐信任', TRUST_ALL);

// 6) 反向：别的分类选了子类再切回来，也要复位
reset();
clickCategory('collaboration');
F.sub = 'physical';
clickCategory('leadership');
expect('🤝协作(身体默契) → 切到👑领导力', LEAD_ALL);

reset();
clickCategory('online');
F.online = 'async';
clickCategory('trust');
expect('💻线上(异步) → 切到🔐信任', TRUST_ALL);

// 7) 其它 5 套子类不受影响
reset();
F.sub = 'pipeline';
expect('全部 + 协作子类=pipeline', membersOf((c) => c.sub === 'pipeline'));
reset();
F.comm = 'relay';
expect('全部 + 沟通坏在哪一环=relay', membersOf((c) => c.comm === 'relay'));
reset();
F.ice = 'know';
expect('全部 + 破冰要什么=know', membersOf((c) => c.ice === 'know'));
reset();
F.idea = 'define';
expect('全部 + 卡在哪一步=define', membersOf((c) => c.idea === 'define'));
reset();
F.online = 'screen';
expect('全部 + 线上怎么玩=screen', membersOf((c) => c.online === 'screen'));

// 8) 子类 × 人数 叠加
reset();
clickCategory('leadership');
F.lead = 'informal';
F.people = 'large';
const leadLarge = membersOf((c) => c.lead === 'informal' && c.people === 'large');
expect('👑领导力 + 不带权 + 20+人', leadLarge);
if (leadLarge.length !== 1 || leadLarge[0] !== 'tangram') {
  fail++;
  console.log('FAIL 👑不带权 + 20+人 应只剩七巧板：' + JSON.stringify(leadLarge));
}

reset();
clickCategory('leadership');
F.lead = 'delegate';
F.people = 'small';
const delegateSmall = membersOf((c) => c.lead === 'delegate' && c.people === 'small');
expect('👑领导力 + 授权 + <10人（应为 0 款）', delegateSmall);
if (delegateSmall.length !== 0) { fail++; console.log('FAIL 该组合本该为空（两款都要 8 人以上分组）'); }

reset();
clickCategory('trust');
F.trust = 'body';
F.people = 'small';
const bodySmall = membersOf((c) => c.trust === 'body' && c.people === 'small');
expect('🔐信任 + 托付身体 + <10人', bodySmall);
if (bodySmall.length !== 1 || bodySmall[0] !== 'blind-walk') {
  fail++;
  console.log('FAIL 🔐托付身体 + <10人 应只剩盲行：' + JSON.stringify(bodySmall));
}

reset();
clickCategory('trust');
F.trust = 'outcome';
F.people = 'small';
const outcomeSmall = membersOf((c) => c.trust === 'outcome' && c.people === 'small');
expect('🔐信任 + 托付结果 + <10人（应为 0 款）', outcomeSmall);
if (outcomeSmall.length !== 0) { fail++; console.log('FAIL 该组合本该为空（八仙/三猿都要 8 人以上）'); }

// 9) 子类 × 时长 叠加（领导力是最贵的一类：只有沉默领袖 30-40 min）
reset();
clickCategory('leadership');
F.lead = 'informal';
F.duration = 'medium';
expect('👑领导力 + 不带权 + 30-60min', membersOf((c) => c.lead === 'informal' && c.duration === 'medium'));

console.log(fail === 0 ? '\nALL PASS' : '\n' + fail + ' 项失败');
process.exit(fail === 0 ? 0 : 1);
