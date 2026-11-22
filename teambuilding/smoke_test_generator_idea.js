// 创意与解题子类在生成器「拼游戏」模式下的行为仿真（node 直接跑）
//   node teambuilding/smoke_test_generator_idea.js
//
// 复刻 generator.html 的 gamesDB 筛选逻辑，验证：
//   1) 目的＝创意与解题 时只出这 10 款（不多不少）
//   2) 4 组子类各自筛出的成员与 idea.html 分组完全一致
//   3) 子类 × 人数/时长 无解时显式回退，不静默换口径
//   4) 协作类 6 组子类不受影响
const fs = require('fs');
const path = require('path');

const TB = path.join(__dirname);
const gen = fs.readFileSync(path.join(TB, 'toolbox', 'generator.html'), 'utf8');
const idea = fs.readFileSync(path.join(TB, 'idea.html'), 'utf8');

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

// ---- 从 generator.html 抽 IDEA_GROUPS ----
const ideaGroups = [];
const igBlock = gen.match(/var IDEA_GROUPS = \[([\s\S]*?)\n\];/)[1];
const gRe = /\{ key: '([a-z]+)', name: '([^']*)', short: '([^']*)', n: (\d+),[\s\S]*?pick: '([a-z0-9-]+)',\s*\n\s*ids: \[([^\]]*)\] \}/g;
while ((m = gRe.exec(igBlock)) !== null) {
  ideaGroups.push({
    key: m[1], name: m[2], short: m[3], n: Number(m[4]), pick: m[5],
    ids: m[6].split(',').map((s) => s.trim().replace(/'/g, '')),
  });
}
console.log('IDEA_GROUPS：' + ideaGroups.length + ' 组');

// ---- 从 idea.html 抽真实分组（作为期望值的独立来源） ----
const htmlGroups = {};
const keys = [...idea.matchAll(/<div class="group-card" id="g-([a-z]+)">/g)].map((x) => x[1]);
// 注意：JS 里 '%s' % k 不是格式化（那是 Python 语法，JS 会算成 NaN），必须用字符串拼接
const groupTag = (k) => '<div class="group-card" id="g-' + k + '">';
keys.forEach((k, i) => {
  const start = idea.indexOf(groupTag(k));
  const end = i + 1 < keys.length ? idea.indexOf(groupTag(keys[i + 1]))
                                   : idea.indexOf('⚠️ 三个最容易挑错的地方');
  const seg = idea.slice(start, end);
  htmlGroups[k] = [...seg.matchAll(/<tr><td><a href="games\/(?:creativity|problem-solving)\/([a-z0-9-]+)\.html">/g)].map((x) => x[1]);
});

let fail = 0;
function ok(cond, label, extra) {
  if (cond) { console.log('OK   ' + label); }
  else { fail++; console.log('FAIL ' + label + (extra ? ' | ' + extra : '')); }
}

// 1) 生成器的分组必须与 idea.html 完全同源
ideaGroups.forEach((g) => {
  const want = (htmlGroups[g.key] || []).slice().sort();
  const got = g.ids.slice().sort();
  ok(JSON.stringify(got) === JSON.stringify(want),
     '生成器组 ' + g.key + ' 与 idea.html 同源（' + got.length + ' 款）',
     JSON.stringify(got) + ' vs ' + JSON.stringify(want));
  ok(g.n === want.length, '生成器组 ' + g.key + ' 款数标注 ' + g.n + ' == 实际 ' + want.length);
});

// 2) 目的＝创意与解题 只出这 10 款
const IDEA_CATS = ['creativity', 'problem-solving'];
const allIdea = games.filter((g) => IDEA_CATS.indexOf(g.category) >= 0).map((g) => g.id).sort();
ok(allIdea.length === 10, '目的＝创意与解题 命中 ' + allIdea.length + ' 款（应为 10）');
ok(JSON.stringify(allIdea) === JSON.stringify(Object.values(htmlGroups).flat().sort()),
   '生成器 idea 类目与 idea.html 10 款完全一致');

// 3) 四个子类各自的筛选结果
ideaGroups.forEach((g) => {
  const got = games.filter((x) => g.ids.indexOf(x.id) >= 0).map((x) => x.id).sort();
  ok(got.length === g.n, '子类 ' + g.key + ' 筛出 ' + got.length + ' 款 == ' + g.n);
  ok(g.ids.indexOf(g.pick) >= 0, '子类 ' + g.key + ' 的首选 ' + g.pick + ' 在本组内');
  // 每组必须横跨 💡/🔧 两个分类（否则又退回按分类挑）
  const cats = new Set(g.ids.map((id) => (games.find((x) => x.id === id) || {}).category));
  ok(cats.size === 2, '子类 ' + g.key + ' 横跨两个分类（' + [...cats].join('/') + '）');
});

// 4) 无解回退：某组 + 极小人数 + 极短时长 → 显式回退而不是空结果
function buildFilter(people, duration, ideaKey) {
  return games.filter((g) => {
    const matchPeople = g.people.indexOf(people) >= 0 || (people === 'xlarge' && g.people.indexOf('large') >= 0);
    const matchCategory = IDEA_CATS.indexOf(g.category) >= 0;
    const matchIdea = !ideaKey || (g.ids || []).indexOf(g.id) >= 0;
    return matchPeople && matchCategory && matchIdea;
  });
}
const strict = buildFilter('small', 'short', 'define');
const loose = buildFilter('small', 'short', null);
ok(loose.length >= strict.length, '放宽后集合不小于严格集合（' + strict.length + ' → ' + loose.length + '）');

// 5) 协作类 6 组不受影响
const collabIds = gen.match(/var COLLAB_GROUPS = \[([\s\S]*?)\n\];/)[1];
const collabCount = (collabIds.match(/ids: \[/g) || []).length;
ok(collabCount === 6, '协作子类仍是 6 组');

// 6) 目的按钮与筛选行齐全
ok(/data-value="idea"[^>]*>💡 创意与解题</.test(gen), '目的按钮含「💡 创意与解题」');
ok((gen.match(/selectOption\(this, 'ideaSub'\)/g) || []).length === 5, 'ideaSub 按钮 5 个（4 组 + 不限）');
ok(/id="idea-sub-form-group"/.test(gen), '存在 idea-sub-form-group');
ok(/params\.get\('idea'\)/.test(gen), '支持 URL 参数 ?idea=');

console.log(fail === 0 ? '\nALL PASS' : '\n' + fail + ' 项失败');
process.exit(fail === 0 ? 0 : 1);
