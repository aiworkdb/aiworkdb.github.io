/**
 * 生成器「拼游戏」模式 · 👑领导力 3 组 + 🔐信任 3 组 冒烟测试（2026-11-01）
 * 做法同 smoke_test_generator_comm.js：
 *   抽出 toolbox/generator.html 内联 JS -> DOM stub -> 跑真实代码路径。
 *
 * 断言：
 *   1) LEAD_GROUPS / TRUST_GROUPS 与 index.html 的 data-lead / data-trust、
 *      lead.html / trust.html 的分组表格三方同源
 *   2) 子类筛选行只在「拼游戏 + 对应目的」时出现；切走自动复位为「不限」
 *   3) 选了子类后，推荐结果全部属于该组
 *   4) 4 人数桶 × 4 时长桶 × 4 子类 × 2 类 = 128 组全组合不抛错
 *   5) **两类的回退分支在当前数据下都真的会触发**（与线上那轮不同）：
 *      目的「👑领导力」的 categoryFilter 是 ['leadership','collaboration']，
 *      目的「🔐信任建立」的是 ['trust','communication']，
 *      而 3 组只覆盖本类那 6 款 —— 一旦某一组在某个人数桶下无解就会走回退。
 *      回退目标必须落在本类 6 款上，**绝不能放宽到整个目的**（会把 39 款协作
 *      / 8 款沟通一起放进来）。本条是核心。
 *   6) 协作 6 / 创意解题 4 / 破冰 4 / 线上 4 / 沟通 4 组不受影响
 */
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const GEN = fs.readFileSync(path.join(__dirname, 'toolbox', 'generator.html'), 'utf8');
const IDX = fs.readFileSync(path.join(__dirname, 'index.html'), 'utf8');
const LEAD = fs.readFileSync(path.join(__dirname, 'lead.html'), 'utf8');
const TRUST = fs.readFileSync(path.join(__dirname, 'trust.html'), 'utf8');

// ---------- 极简 DOM ----------
class El {
  constructor(tag, attrs, text) {
    this.tag = tag;
    this.attrs = attrs || {};
    this.text = text || '';
    this.children = [];
    this.parent = null;
    this.style = {};
    this.innerHTML = '';
    this._classes = (this.attrs.class || '').split(/\s+/).filter(Boolean);
    const self = this;
    this.classList = {
      add: (c) => { if (!self._classes.includes(c)) self._classes.push(c); },
      remove: (c) => { self._classes = self._classes.filter(x => x !== c); },
      contains: (c) => self._classes.includes(c),
    };
  }
  get id() { return this.attrs.id || ''; }
  getAttribute(k) { return k in this.attrs ? this.attrs[k] : null; }
  append(c) { c.parent = this; this.children.push(c); return c; }
  get parentElement() { return this.parent; }
  _all(out) { for (const c of this.children) { out.push(c); c._all(out); } return out; }
  querySelectorAll(sel) {
    const m = /^\.([a-z-]+)$/.exec(sel);
    if (!m) throw new Error('不支持的选择器: ' + sel);
    return this._all([]).filter(e => e._classes.includes(m[1]));
  }
  querySelector(sel) { return this.querySelectorAll(sel)[0] || null; }
  scrollIntoView() {}
}

const root = new El('body', {});
const byId = {};
const grpRe = /<div class="btn-group" id="([a-z-]+)">([\s\S]*?)<\/div>/g;
let g;
while ((g = grpRe.exec(GEN)) !== null) {
  const box = root.append(new El('div', { class: 'btn-group', id: g[1] }));
  byId[g[1]] = box;
  const btnRe = /<button class="btn-option[^"]*"([^>]*)>([\s\S]*?)<\/button>/g;
  let b;
  while ((b = btnRe.exec(g[2])) !== null) {
    const dv = /data-value="([^"]+)"/.exec(b[1]);
    box.append(new El('button', { class: 'btn-option', 'data-value': dv ? dv[1] : '' }, b[2]));
  }
}

const document_ = {
  getElementById: (id) => {
    if (!byId[id]) byId[id] = root.append(new El('div', { id }));
    return byId[id];
  },
  querySelectorAll: (sel) => root.querySelectorAll(sel),
  querySelector: () => null,
};

const sandbox = { document: document_, window: { addEventListener: () => {} }, console, alert: () => {} };
vm.createContext(sandbox);
vm.runInContext(/<script>([\s\S]*)<\/script>/.exec(GEN)[1], sandbox);

// ---------- 断言 ----------
let fail = 0;
const ok = (cond, msg) => { if (!cond) { console.log('  ❌ ' + msg); fail++; } };

function idxMap(attr) {
  const out = {};
  const re = new RegExp('<a href="games/(?:leadership|trust)/([a-z0-9-]+)\\.html"\\s+class="card" data-'
    + attr + '="([a-z]+)"', 'g');
  for (const m of IDX.matchAll(re)) { out[m[1]] = m[2]; }
  return out;
}

function checkSource(label, attr, CAP, SUB_OF, GROUPS, ALL_IDS, PAGE, TAIL, cat) {
  const idx = idxMap(attr);
  ok(Object.keys(idx).length === 6, label + '：index.html 卡片应为 6，实际 ' + Object.keys(idx).length);
  ok(Object.keys(SUB_OF).length === 6, label + '：生成器子类成员应为 6，实际 ' + Object.keys(SUB_OF).length);
  const mismatch = Object.keys(idx).filter(id => SUB_OF[id] !== idx[id]);
  ok(mismatch.length === 0, label + '：与 index.html data-' + attr + ' 不一致：' + mismatch.join(', '));
  ok(GROUPS.length === 3, label + '：分组应为 3，实际 ' + GROUPS.length);

  const keys = [...PAGE.matchAll(/<div class="group-card" id="g-([a-z]+)">/g)].map(x => x[1]);
  ok(keys.length === 3, label + '：挑款页应有 3 组，实际 ' + keys.length);
  for (const grp of GROUPS) {
    ok(grp.ids.length === grp.n, label + ' 组 ' + grp.key + ' 声明 ' + grp.n + ' 款，实际 ' + grp.ids.length);
    ok(grp.ids.every(id => sandbox.gamesDB.some(x => x.id === id)),
      label + ' 组 ' + grp.key + ' 含 gamesDB 里不存在的 id');
    ok(sandbox.gamesDB.some(x => x.id === grp.pick), label + ' 组 ' + grp.key + ' 的首选不在 gamesDB');
    const i = PAGE.indexOf('<div class="group-card" id="g-' + grp.key + '">');
    const k = keys.indexOf(grp.key);
    const end = k + 1 < keys.length
      ? PAGE.indexOf('<div class="group-card" id="g-' + keys[k + 1] + '">')
      : PAGE.indexOf(TAIL);
    const seg = PAGE.slice(i, end);
    const htmlIds = [...seg.matchAll(/<tr><td><a href="games\/[a-z-]+\/([a-z0-9-]+)\.html">/g)].map(x => x[1]);
    ok(JSON.stringify(htmlIds.slice().sort()) === JSON.stringify(grp.ids.slice().sort()),
      label + ' 组 ' + grp.key + ' 与挑款页表格不一致：'
      + JSON.stringify(grp.ids) + ' vs ' + JSON.stringify(htmlIds));
  }
  ok(ALL_IDS.length === 6, label + '：ALL_IDS 应有 6 款，实际 ' + ALL_IDS.length);
  const cats = new Set(ALL_IDS.map(id => (sandbox.gamesDB.find(x => x.id === id) || {}).category));
  ok(cats.size === 1 && cats.has(cat), label + '：ALL_IDS 应全部是 ' + cat + ' 类，实际 ' + [...cats].join('/'));
  console.log('  ✅ ' + label + ' 3 组子类与 index.html / 挑款页三方同源（6 款 / 3 组）');
}

checkSource('👑领导力', 'lead', 'LEAD', sandbox.LEAD_SUB_OF, sandbox.LEAD_GROUPS,
  sandbox.LEAD_ALL_IDS, LEAD, '<h2>👑 领导力不只是这 6 款</h2>', 'leadership');
checkSource('🔐信任', 'trust', 'TRUST', sandbox.TRUST_SUB_OF, sandbox.TRUST_GROUPS,
  sandbox.TRUST_ALL_IDS, TRUST, '<h2>🔐 信任不只是这 6 款</h2>', 'trust');

// 2) 显隐与复位
sandbox.currentMode = 'game';
sandbox.userSelections.purpose = 'collaboration';
sandbox.refreshLeadSub();
sandbox.refreshTrustSub();
ok(byId['lead-sub-form-group'].style.display === 'none', '目的非领导力时领导力子类行应隐藏');
ok(byId['trust-sub-form-group'].style.display === 'none', '目的非信任时信任子类行应隐藏');
sandbox.userSelections.purpose = 'leadership';
sandbox.refreshLeadSub();
ok(byId['lead-sub-form-group'].style.display === '', '目的=领导力时子类行应显示');
sandbox.userSelections.leadSub = 'delegate';
sandbox.refreshLeadSub();
ok(sandbox.userSelections.leadSub === 'delegate', '领导力状态下子类不应被复位');
sandbox.userSelections.purpose = 'trust';
sandbox.refreshLeadSub();
ok(sandbox.userSelections.leadSub === 'any', '切走领导力后子类应复位为 any');
sandbox.userSelections.purpose = 'trust';
sandbox.refreshTrustSub();
ok(byId['trust-sub-form-group'].style.display === '', '目的=信任时子类行应显示');
sandbox.userSelections.trustSub = 'truth';
sandbox.refreshTrustSub();
ok(sandbox.userSelections.trustSub === 'truth', '信任状态下子类不应被复位');
sandbox.userSelections.purpose = 'communication';
sandbox.refreshTrustSub();
ok(sandbox.userSelections.trustSub === 'any', '切走信任后子类应复位为 any');
sandbox.currentMode = 'flow';
sandbox.userSelections.purpose = 'leadership';
sandbox.refreshLeadSub();
ok(byId['lead-sub-form-group'].style.display === 'none', '整套流程模式下子类行应隐藏');
console.log('  ✅ 两组子类行显隐 / 切走复位通过');

// 3) 全组合 + 回退
sandbox.currentMode = 'game';
const PEOPLE = ['small', 'medium', 'large', 'xlarge'];
const DURS = ['short', 'medium', 'long', 'fullday'];

function runCombos(label, purpose, SUBS, SUB_OF, ALL_IDS, subKey, fbVar) {
  let combos = 0;
  let fbHits = 0;
  let hits = 0;
  for (const p of PEOPLE) {
    for (const d of DURS) {
      sandbox.userSelections.people = p;
      sandbox.userSelections.duration = d;
      sandbox.userSelections.purpose = purpose;
      for (const s of SUBS) {
        sandbox.userSelections[subKey] = s;
        const got = sandbox.recommendGames();
        combos++;
        if (sandbox[fbVar]) { fbHits++; continue; }
        if (s !== 'any') {
          const wrong = got.filter(x => SUB_OF[x.id] !== s);
          ok(wrong.length === 0, label + ' 子类 ' + s + ' 混入了其它组：' + wrong.map(x => x.id).join(','));
          const outside = got.filter(x => ALL_IDS.indexOf(x.id) < 0);
          ok(outside.length === 0, label + ' 子类 ' + s + ' 出了本类以外的游戏：' + outside.map(x => x.id).join(','));
          if (got.length) hits++;
        }
      }
    }
  }
  ok(combos === 64, label + ' 组合数应为 4×4×4=64，实际 ' + combos);
  ok(fbHits > 0, label + ' 回退应至少触发一次（实际 ' + fbHits + '）—— 若变为 0，说明本条事实断言已过时');
  console.log('  ✅ ' + label + ' 64 组全组合不抛错；子类命中 ' + hits + ' 组；回退触发 ' + fbHits + ' 次');
  return fbHits;
}

// ⚠️ 状态位名字是小写开头的 leadSub / trustSub，回退标记才是 lastLeadFallback / lastTrustFallback
//    （曾把两者写成同一个首字母大写的变量，结果子类根本没生效、回退 0 次也照样"通过"）
const leadFb = runCombos('👑领导力', 'leadership', ['decide', 'delegate', 'informal', 'any'],
  sandbox.LEAD_SUB_OF, sandbox.LEAD_ALL_IDS, 'leadSub', 'lastLeadFallback');
const trustFb = runCombos('🔐信任', 'trust', ['body', 'truth', 'outcome', 'any'],
  sandbox.TRUST_SUB_OF, sandbox.TRUST_ALL_IDS, 'trustSub', 'lastTrustFallback');

// 4) 回退目标：绝不能放宽到整个目的
sandbox.userSelections.people = 'small';
sandbox.userSelections.duration = 'medium';
sandbox.userSelections.purpose = 'leadership';
sandbox.userSelections.leadSub = 'delegate';
const leadGot = sandbox.recommendGames();
ok(sandbox.lastLeadFallback === 'delegate', '应记录回退来自 delegate 组');
ok(leadGot.length > 0, '领导力回退后仍应给出结果');
ok(leadGot.filter(x => x.category !== 'leadership').length === 0,
  '领导力回退结果混进了协作分类（放宽到了整个目的）：'
  + leadGot.filter(x => x.category !== 'leadership').map(x => x.id).join(','));
ok(leadGot.filter(x => sandbox.LEAD_ALL_IDS.indexOf(x.id) < 0).length === 0,
  '领导力回退结果有游戏不在 LEAD_ALL_IDS 里');
const collabIds = sandbox.gamesDB.filter(x => x.category === 'collaboration').map(x => x.id);
ok(collabIds.every(id => sandbox.LEAD_ALL_IDS.indexOf(id) < 0),
  'LEAD_ALL_IDS 不应含协作分类的游戏（39 款并不在那 3 组里）');

sandbox.userSelections.people = 'small';
sandbox.userSelections.duration = 'medium';
sandbox.userSelections.purpose = 'trust';
sandbox.userSelections.trustSub = 'outcome';
const trustGot = sandbox.recommendGames();
ok(sandbox.lastTrustFallback === 'outcome', '应记录回退来自 outcome 组');
ok(trustGot.length > 0, '信任回退后仍应给出结果');
ok(trustGot.filter(x => x.category !== 'trust').length === 0,
  '信任回退结果混进了沟通分类（放宽到了整个目的）：'
  + trustGot.filter(x => x.category !== 'trust').map(x => x.id).join(','));
ok(trustGot.filter(x => sandbox.TRUST_ALL_IDS.indexOf(x.id) < 0).length === 0,
  '信任回退结果有游戏不在 TRUST_ALL_IDS 里');
const commIds = sandbox.gamesDB.filter(x => x.category === 'communication').map(x => x.id);
ok(commIds.every(id => sandbox.TRUST_ALL_IDS.indexOf(id) < 0),
  'TRUST_ALL_IDS 不应含沟通分类的游戏（8 款并不在那 3 组里）');
console.log('  ✅ 两组回退目标 = 本类 6 款（未放宽到「领导力 / 信任建立」目的里的其它分类）');

// 5) 人数桶的一个事实：xlarge 会连带命中 large（matchPeople 里 `people === 'xlarge'
//    && game.people.includes('large')`），所以 🔐托付身体 + 30+人 不是空，而是只剩信任背摔
sandbox.userSelections.people = 'xlarge';
sandbox.userSelections.duration = 'medium';
sandbox.userSelections.purpose = 'trust';
sandbox.userSelections.trustSub = 'body';
const bigGot = sandbox.recommendGames();
ok(Array.isArray(bigGot), '应返回数组而不是抛错');
ok(!sandbox.lastTrustFallback, '🔐托付身体 + 30+人 不必回退（信任背摔支持 large，xlarge 会连带命中）');
ok(bigGot.length === 1 && bigGot[0].id === 'trust-fall',
  '🔐托付身体 + 30+人 应只剩信任背摔（盲行只到 10-20 人），实际 '
  + bigGot.map(x => x.id).join(','));
ok(bigGot.every(x => sandbox.TRUST_SUB_OF[x.id] === 'body'), '结果仍应全部属于所选组');
console.log('  ✅ xlarge 连带命中 large 的行为符合预期（30+人下 🫱托付身体 只剩信任背摔）');

// 6) 其余 5 套子类不受影响
ok(sandbox.COLLAB_GROUPS.length === 6, '协作子类仍应是 6 组，实际 ' + sandbox.COLLAB_GROUPS.length);
ok(sandbox.IDEA_GROUPS.length === 4, '创意解题子类仍应是 4 组，实际 ' + sandbox.IDEA_GROUPS.length);
ok(sandbox.ICE_GROUPS.length === 4, '破冰子类仍应是 4 组，实际 ' + sandbox.ICE_GROUPS.length);
ok(sandbox.ONLINE_GROUPS.length === 4, '线上子类仍应是 4 组，实际 ' + sandbox.ONLINE_GROUPS.length);
ok(sandbox.COMM_GROUPS.length === 4, '沟通子类仍应是 4 组，实际 ' + sandbox.COMM_GROUPS.length);

// 7) 按钮与入口
ok(byId['lead-sub-group'].querySelectorAll('.btn-option').length === 4,
  'leadSub 按钮应为 4 个（3 组 + 不限），实际 '
  + byId['lead-sub-group'].querySelectorAll('.btn-option').length);
ok(byId['trust-sub-group'].querySelectorAll('.btn-option').length === 4,
  'trustSub 按钮应为 4 个（3 组 + 不限），实际 '
  + byId['trust-sub-group'].querySelectorAll('.btn-option').length);
ok(/params\.get\('lead'\)/.test(GEN), '应支持 URL 参数 ?lead=');
ok(/params\.get\('trust'\)/.test(GEN), '应支持 URL 参数 ?trust=');
ok(/LEAD_SUB_OF\[game\.id\] === leadKey/.test(GEN), '领导力筛选应用的是分组映射');
ok(/TRUST_SUB_OF\[game\.id\] === trustKey/.test(GEN), '信任筛选应用的是分组映射');
ok(/\.\.\/lead\.html/.test(GEN), '结果卡胶囊应指回 lead.html 挑款页');
ok(/\.\.\/trust\.html/.test(GEN), '结果卡胶囊应指回 trust.html 挑款页');

console.log(fail === 0 ? '\nALL PASS' : '\n' + fail + ' 项失败');
process.exit(fail === 0 ? 0 : 1);
