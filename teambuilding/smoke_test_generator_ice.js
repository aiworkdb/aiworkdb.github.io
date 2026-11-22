// 破冰子类在生成器「拼游戏」模式下的行为仿真（node 直接跑）
//   node teambuilding/smoke_test_generator_ice.js
//
// 复刻 generator.html 的 gamesDB 筛选逻辑，验证：
//   1) 破冰 4 组子类各自筛出的成员与 ice.html 分组完全一致
//   2) 回退落在「全部 8 款破冰」，而不是整个「破冰热场」目的（含沟通 8 款）
//   3) 子类 × 人数/时长 无解时显式回退，不静默换口径
//   4) 协作 6 组与创意解题 4 组不受影响
const fs = require('fs');
const path = require('path');

const TB = path.join(__dirname);
const gen = fs.readFileSync(path.join(TB, 'toolbox', 'generator.html'), 'utf8');
const ice = fs.readFileSync(path.join(TB, 'ice.html'), 'utf8');
const idx = fs.readFileSync(path.join(TB, 'index.html'), 'utf8');

// ---- 从 generator.html 抽 gamesDB ----
const dbBlock = gen.match(/var gamesDB = \[([\s\S]*?)\n\];/)[1];
const games = [];
const entryRe = /\{ id: '([a-z0-9-]+)',[\s\S]*?category: '([a-z-]+)',[\s\S]*?people: \[([^\]]*)\][\s\S]*?duration: (\d+)/g;
let m;
while ((m = entryRe.exec(dbBlock)) !== null) {
  games.push({
    id: m[1], category: m[2],
    people: m[3].split(',').map((s) => s.trim().replace(/'/g, '')),
    duration: Number(m[4]),
  });
}
console.log('gamesDB 条目：' + games.length);

// ---- 从 generator.html 抽 ICE_GROUPS ----
const iceGroups = [];
const igBlock = gen.match(/var ICE_GROUPS = \[([\s\S]*?)\n\];/)[1];
const gRe = /\{ key: '([a-z]+)', name: '([^']*)', short: '([^']*)', n: (\d+),[\s\S]*?pick: '([a-z0-9-]+)',\s*\n\s*ids: \[([^\]]*)\] \}/g;
while ((m = gRe.exec(igBlock)) !== null) {
  iceGroups.push({
    key: m[1], name: m[2], short: m[3], n: Number(m[4]), pick: m[5],
    ids: m[6].split(',').map((s) => s.trim().replace(/'/g, '')),
  });
}
console.log('ICE_GROUPS：' + iceGroups.length + ' 组');

// ---- 抽 ICE_ALL_IDS（回退目标）----
const allIdsBlock = gen.match(/var ICE_ALL_IDS = \[([^\]]*)\]/);
const iceAllIds = allIdsBlock
  ? allIdsBlock[1].split(',').map((s) => s.trim().replace(/'/g, ''))
  : [];
console.log('ICE_ALL_IDS：' + iceAllIds.length + ' 款');

// ---- 从 ice.html 抽真实分组（作为期望值的独立来源）----
const htmlGroups = {};
const keys = [...ice.matchAll(/<div class="group-card" id="g-([a-z]+)">/g)].map((x) => x[1]);
const groupTag = (k) => '<div class="group-card" id="g-' + k + '">';
keys.forEach((k, i) => {
  const start = ice.indexOf(groupTag(k));
  const end = i + 1 < keys.length ? ice.indexOf(groupTag(keys[i + 1]))
                                  : ice.indexOf('<h2>🧊 破冰不只是这 8 款</h2>');
  const seg = ice.slice(start, end);
  htmlGroups[k] = [...seg.matchAll(/<tr><td><a href="games\/icebreaker\/([a-z0-9-]+)\.html">/g)].map((x) => x[1]);
});

let fail = 0;
function ok(cond, label, extra) {
  if (cond) { console.log('OK   ' + label); }
  else { fail++; console.log('FAIL ' + label + (extra ? ' | ' + extra : '')); }
}

// 1) 生成器的分组必须与 ice.html 完全同源
iceGroups.forEach((g) => {
  const want = (htmlGroups[g.key] || []).slice().sort();
  const got = g.ids.slice().sort();
  ok(JSON.stringify(got) === JSON.stringify(want),
     '生成器组 ' + g.key + ' 与 ice.html 同源（' + got.length + ' 款）',
     JSON.stringify(got) + ' vs ' + JSON.stringify(want));
  ok(g.n === want.length, '生成器组 ' + g.key + ' 款数标注 ' + g.n + ' == 实际 ' + want.length);
});

// 2) 与 index.html 的 data-ice 也必须一致（第三处同源）
const idxIce = {};
[...idx.matchAll(/<a href="games\/icebreaker\/([a-z0-9-]+)\.html" class="card" data-ice="([a-z]+)"/g)]
  .forEach((x) => { idxIce[x[1]] = x[2]; });
const genIce = {};
iceGroups.forEach((g) => g.ids.forEach((id) => { genIce[id] = g.key; }));
// ⚠️ 必须按键排序后比：对象键的插入顺序取决于两边各自的排列顺序，
// 直接 JSON.stringify 比会误报（内容完全一致也会红）。
function sortedMap(o) {
  const out = {};
  Object.keys(o).sort().forEach((k) => { out[k] = o[k]; });
  return out;
}
ok(JSON.stringify(sortedMap(genIce)) === JSON.stringify(sortedMap(idxIce)),
   '生成器破冰子类与 index.html data-ice 完全一致',
   JSON.stringify(sortedMap(genIce)) + ' vs ' + JSON.stringify(sortedMap(idxIce)));
ok(Object.keys(idxIce).length === 8, 'index.html 带 data-ice 的破冰卡片 ' + Object.keys(idxIce).length + ' 款');

// 3) ICE_ALL_IDS 必须是全部 8 款破冰（回退目标），且不能混入沟通类
ok(iceAllIds.length === 8, 'ICE_ALL_IDS 有 ' + iceAllIds.length + ' 款（应为 8）');
const iceAllCats = new Set(iceAllIds.map((id) => (games.find((x) => x.id === id) || {}).category));
ok(iceAllCats.size === 1 && iceAllCats.has('icebreaker'),
   'ICE_ALL_IDS 全部是 icebreaker 类（实际 ' + [...iceAllCats].join('/') + '）');
const allIceCat = games.filter((g) => g.category === 'icebreaker').map((g) => g.id).sort();
ok(JSON.stringify(iceAllIds.slice().sort()) === JSON.stringify(allIceCat),
   'ICE_ALL_IDS == gamesDB 里全部破冰游戏');

// 4) 四个子类各自的筛选结果
iceGroups.forEach((g) => {
  const got = games.filter((x) => g.ids.indexOf(x.id) >= 0).map((x) => x.id).sort();
  ok(got.length === g.n, '子类 ' + g.key + ' 筛出 ' + got.length + ' 款 == ' + g.n);
  ok(g.ids.indexOf(g.pick) >= 0, '子类 ' + g.key + ' 的首选 ' + g.pick + ' 在本组内');
});

// 5) 无解回退：某组 + 极小人数 + 极长时长 → 显式回退到「全部 8 款破冰」
// ⚠️ 形参不要叫 g：它会遮蔽外层的 iceGroups 变量；且 games 的条目里没有 ids 字段，
//    「属于某一组」要从 iceGroups 里反查，不能直接读 gm.ids。
function buildFilter(people, iceKey) {
  const grp = iceKey && iceKey !== 'iceAll'
    ? iceGroups.filter((x) => x.key === iceKey)[0]
    : null;
  return games.filter((gm) => {
    const matchPeople = gm.people.indexOf(people) >= 0
      || (people === 'xlarge' && gm.people.indexOf('large') >= 0);
    const matchCategory = ['icebreaker', 'communication'].indexOf(gm.category) >= 0;
    const matchIce = !iceKey
      || (iceKey === 'iceAll'
        ? iceAllIds.indexOf(gm.id) >= 0
        : (grp && grp.ids.indexOf(gm.id) >= 0));
    return matchPeople && matchCategory && matchIce;
  });
}
const strict = buildFilter('small', 'team');
const loose = buildFilter('small', 'iceAll');
ok(strict.length === 0,
   '「带协作 + <10人」严格筛选确实无解（该组两款盲盒神话/美食挑战赛都是 4–8 人/组，'
   + '小于 10 人的场开不起来）');
ok(loose.length > 0, '回退后有结果（' + loose.length + ' 款）');
ok(loose.every((g) => g.category === 'icebreaker'),
   '回退结果全部落在破冰类（不含沟通 8 款）');
ok(loose.length <= 8, '回退结果不超过 8 款破冰（实际 ' + loose.length + '）');

// 6) 协作 6 组与创意解题 4 组不受影响
const collabCount = (gen.match(/var COLLAB_GROUPS = \[([\s\S]*?)\n\];/)[1].match(/ids: \[/g) || []).length;
ok(collabCount === 6, '协作子类仍是 6 组');
const ideaCount = (gen.match(/var IDEA_GROUPS = \[([\s\S]*?)\n\];/)[1].match(/ids: \[/g) || []).length;
ok(ideaCount === 4, '创意解题子类仍是 4 组');

// 7) 按钮与入口齐全
ok(/id="ice-sub-form-group"/.test(gen), '存在 ice-sub-form-group');
ok((gen.match(/selectOption\(this, 'iceSub'\)/g) || []).length === 5, 'iceSub 按钮 5 个（4 组 + 不限）');
ok(/params\.get\('ice'\)/.test(gen), '支持 URL 参数 ?ice=');
ok(/lastIceFallback/.test(gen), '存在 lastIceFallback 回退标记');
ok(/refreshIceSub/.test(gen), '存在 refreshIceSub 显隐逻辑');

console.log(fail === 0 ? '\nALL PASS' : '\n' + fail + ' 项失败');
process.exit(fail === 0 ? 0 : 1);
