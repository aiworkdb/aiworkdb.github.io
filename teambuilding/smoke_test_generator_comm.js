/**
 * 生成器「拼游戏」模式 · 沟通 4 组子类 冒烟测试（2026-10-31）
 * 做法同 smoke_test_generator_online.js：
 *   抽出 toolbox/generator.html 内联 JS -> DOM stub -> 跑真实代码路径。
 *
 * 断言：
 *   1) COMM_GROUPS 的 4 组与 index.html 的 data-comm、comm.html 的表格三方同源
 *   2) 子类筛选行只在「拼游戏 + 目的=沟通表达」时出现；切走沟通自动复位为「不限」
 *   3) 选了子类后，推荐结果全部属于该组
 *   4) 4 人数桶 × 4 时长桶 × 5 子类 = 80 组全组合不抛错
 *   5) **沟通子类回退分支在当前数据下真的会触发**（与线上不同）：
 *      目的「沟通表达」的 categoryFilter 是 ['communication','trust']，
 *      而 4 组只覆盖 communication 那 8 款 —— 一旦某一组在 20+ 人下无解
 *      （🧩凑不齐 / ⚖️说不拢 两组成员最多只到 10-20 人），
 *      就会走回退。回退目标必须是「全部 8 款沟通」，
 *      **绝不能放宽到整个目的（会把 trust 的盲行一起放进来）**。本条是核心。
 *   6) 协作 6 组 / 创意解题 4 组 / 破冰 4 组 / 线上 4 组不受影响
 */
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const GEN = fs.readFileSync(path.join(__dirname, 'toolbox', 'generator.html'), 'utf8');
const IDX = fs.readFileSync(path.join(__dirname, 'index.html'), 'utf8');
const COMM = fs.readFileSync(path.join(__dirname, 'comm.html'), 'utf8');

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

// 1) 与 index.html 的 data-comm 同源
const idxComm = {};
for (const m of IDX.matchAll(/<a href="games\/communication\/([a-z0-9-]+)\.html"\s+class="card" data-comm="([a-z]+)"/g)) {
  idxComm[m[1]] = m[2];
}
ok(Object.keys(idxComm).length === 8, 'index.html 沟通卡片应为 8，实际 ' + Object.keys(idxComm).length);
ok(Object.keys(sandbox.COMM_SUB_OF).length === 8,
  '生成器子类成员应为 8，实际 ' + Object.keys(sandbox.COMM_SUB_OF).length);
const mismatch = Object.keys(idxComm).filter(id => sandbox.COMM_SUB_OF[id] !== idxComm[id]);
ok(mismatch.length === 0, '与 index.html data-comm 不一致：' + mismatch.slice(0, 5).join(', '));
ok(sandbox.COMM_GROUPS.length === 4, '分组应为 4，实际 ' + sandbox.COMM_GROUPS.length);

// 1b) 第三处同源：comm.html 的分组表格
const commKeys = [...COMM.matchAll(/<div class="group-card" id="g-([a-z]+)">/g)].map(x => x[1]);
ok(commKeys.length === 4, 'comm.html 应有 4 组，实际 ' + commKeys.length);
for (const grp of sandbox.COMM_GROUPS) {
  ok(grp.ids.length === grp.n, '分组 ' + grp.key + ' 声明 ' + grp.n + ' 款，实际 ' + grp.ids.length);
  ok(grp.ids.every(id => sandbox.gamesDB.some(x => x.id === id)),
    '分组 ' + grp.key + ' 含 gamesDB 里不存在的 id');
  ok(sandbox.gamesDB.some(x => x.id === grp.pick), '分组 ' + grp.key + ' 的首选不在 gamesDB');
  const i = COMM.indexOf('<div class="group-card" id="g-' + grp.key + '">');
  const idx = commKeys.indexOf(grp.key);
  const end = idx + 1 < commKeys.length
    ? COMM.indexOf('<div class="group-card" id="g-' + commKeys[idx + 1] + '">')
    : COMM.indexOf('<h2>💬 沟通不只是这 8 款</h2>');
  const seg = COMM.slice(i, end);
  const htmlIds = [...seg.matchAll(/<tr><td><a href="games\/communication\/([a-z0-9-]+)\.html">/g)].map(x => x[1]);
  ok(JSON.stringify(htmlIds.slice().sort()) === JSON.stringify(grp.ids.slice().sort()),
    '分组 ' + grp.key + ' 与 comm.html 表格不一致：'
    + JSON.stringify(grp.ids) + ' vs ' + JSON.stringify(htmlIds));
}
console.log('  ✅ 4 组子类与 index.html data-comm / comm.html 表格三方同源（8 款 / 4 组）');

// 2) 显隐与复位
sandbox.currentMode = 'game';
sandbox.userSelections.purpose = 'trust';
sandbox.refreshCommSub();
ok(byId['comm-sub-form-group'].style.display === 'none', '目的非沟通时子类行应隐藏');
sandbox.userSelections.purpose = 'communication';
sandbox.refreshCommSub();
ok(byId['comm-sub-form-group'].style.display === '', '目的=沟通时子类行应显示');
sandbox.userSelections.commSub = 'clash';
sandbox.refreshCommSub();
ok(sandbox.userSelections.commSub === 'clash', '沟通状态下子类不应被复位');
sandbox.userSelections.purpose = 'leadership';
sandbox.refreshCommSub();
ok(sandbox.userSelections.commSub === 'any', '切走沟通后子类应复位为 any');
sandbox.currentMode = 'flow';
sandbox.userSelections.purpose = 'communication';
sandbox.refreshCommSub();
ok(byId['comm-sub-form-group'].style.display === 'none', '整套流程模式下子类行应隐藏');
console.log('  ✅ 子类行显隐 / 切走复位通过');

// 3) 选子类后结果全部属于该组 + 80 组全组合不抛错
sandbox.currentMode = 'game';
const SUBS = ['express', 'relay', 'pool', 'clash', 'any'];
const PEOPLE = ['small', 'medium', 'large', 'xlarge'];
const DURS = ['short', 'medium', 'long', 'fullday'];
let subHits = 0;
let comboCount = 0;
let fbHits = 0;
for (const p of PEOPLE) {
  for (const d of DURS) {
    sandbox.userSelections.people = p;
    sandbox.userSelections.duration = d;
    sandbox.userSelections.purpose = 'communication';
    for (const s of SUBS) {
      sandbox.userSelections.commSub = s;
      const got = sandbox.recommendGames();
      comboCount++;
      if (sandbox.lastCommFallback) { fbHits++; continue; }
      if (s !== 'any') {
        const wrong = got.filter(x => sandbox.COMM_SUB_OF[x.id] !== s);
        ok(wrong.length === 0, '子类 ' + s + ' 混入了其它组：' + wrong.map(x => x.id).join(','));
        if (got.length) subHits++;
      }
    }
  }
}
ok(comboCount === 80, '组合数应为 4×4×5=80，实际 ' + comboCount);
console.log('  ✅ 80 组全组合不抛错；子类筛选命中 ' + subHits + ' 组组合，未混入其它组的游戏');

// 4) 子类回退分支在当前数据下真的会触发（与线上不同）
ok(fbHits > 0, '沟通子类回退应至少触发一次（实际 ' + fbHits + '）—— 若变为 0，说明本条事实断言已过时');
console.log('  ✅ 子类回退触发 ' + fbHits + ' 次（20+ 人下 🧩凑不齐 / ⚖️说不拢 无解）');

// 5) 回退目标必须是「全部 8 款沟通」，绝不能把 trust 分类放进来
sandbox.userSelections.people = 'xlarge';
sandbox.userSelections.duration = 'medium';
sandbox.userSelections.purpose = 'communication';
sandbox.userSelections.commSub = 'clash';
const fbGot = sandbox.recommendGames();
ok(sandbox.lastCommFallback === 'clash', '应记录回退来自 clash 组');
ok(fbGot.length > 0, '回退后仍应给出结果');
const badCat = fbGot.filter(x => x.category !== 'communication');
ok(badCat.length === 0,
  '回退结果混进了 trust 分类（放宽到了整个目的）：' + badCat.map(x => x.id).join(','));
const outsideAll = fbGot.filter(x => sandbox.COMM_ALL_IDS.indexOf(x.id) < 0);
ok(outsideAll.length === 0,
  '回退结果有游戏不在 COMM_ALL_IDS 里：' + outsideAll.map(x => x.id).join(','));
console.log('  ✅ 回退目标 = 全部 8 款沟通（未放宽到「沟通表达」目的里的 trust 分类）');

// 6) COMM_ALL_IDS 8 款必须全是 communication 分类
ok(sandbox.COMM_ALL_IDS.length === 8, 'COMM_ALL_IDS 应有 8 款，实际 ' + sandbox.COMM_ALL_IDS.length);
const allCats = new Set(sandbox.COMM_ALL_IDS.map(id => (sandbox.gamesDB.find(x => x.id === id) || {}).category));
ok(allCats.size === 1 && allCats.has('communication'),
  'COMM_ALL_IDS 应全部是 communication 类，实际 ' + [...allCats].join('/'));
const trustIds = sandbox.gamesDB.filter(x => x.category === 'trust').map(x => x.id);
ok(trustIds.every(id => sandbox.COMM_ALL_IDS.indexOf(id) < 0),
  'COMM_ALL_IDS 不应含 trust 分类的游戏（盲行等不在那 4 组里）');
ok(/COMM_SUB_OF\[game\.id\] === commKey/.test(GEN), '筛应用的是分组映射而不是硬编码');
ok(/lastCommFallback/.test(GEN), '应存在 lastCommFallback 回退标记');
ok(/commAll/.test(GEN), '回退目标应是 commAll（全部 8 款沟通）而非整个目的');
console.log('  ✅ 子类回退的目标集合 = 全部 8 款沟通（不放宽到 trust）');

// 7) 「不限」时应能看到 trust 分类（说明子类确实是"再收一层"，不是换口径）
sandbox.userSelections.commSub = 'any';
sandbox.userSelections.people = 'medium';
sandbox.userSelections.duration = 'long';
let sawTrust = false;
for (let i = 0; i < 40; i++) {          // 结果带随机洗牌，多跑几次
  if (sandbox.recommendGames().some(x => x.category === 'trust')) { sawTrust = true; break; }
}
console.log('  ' + (sawTrust ? '✅' : 'ℹ️ ') + ' 子类=不限时，40 次抽样'
  + (sawTrust ? '出现过 trust 分类' : '未出现 trust（属正常：洗牌随机）'));

// 8) 协作 6 组 / 创意解题 4 组 / 破冰 4 组 / 线上 4 组不受影响
ok(sandbox.COLLAB_GROUPS.length === 6, '协作子类仍应是 6 组，实际 ' + sandbox.COLLAB_GROUPS.length);
ok(sandbox.IDEA_GROUPS.length === 4, '创意解题子类仍应是 4 组，实际 ' + sandbox.IDEA_GROUPS.length);
ok(sandbox.ICE_GROUPS.length === 4, '破冰子类仍应是 4 组，实际 ' + sandbox.ICE_GROUPS.length);
ok(sandbox.ONLINE_GROUPS.length === 4, '线上子类仍应是 4 组，实际 ' + sandbox.ONLINE_GROUPS.length);

// 9) 按钮与入口齐全
ok(byId['comm-sub-group'] && byId['comm-sub-group'].querySelectorAll('.btn-option').length === 5,
  'commSub 按钮应为 5 个（4 组 + 不限），实际 '
  + (byId['comm-sub-group'] ? byId['comm-sub-group'].querySelectorAll('.btn-option').length : 'N/A'));
ok(/params\.get\('comm'\)/.test(GEN), '应支持 URL 参数 ?comm=');
ok(/refreshCommSub/.test(GEN), '应存在 refreshCommSub 显隐逻辑');
ok(/\.\.\/comm\.html/.test(GEN), '结果卡胶囊应指回 comm.html 挑款页');

console.log(fail === 0 ? '\nALL PASS' : '\n' + fail + ' 项失败');
process.exit(fail === 0 ? 0 : 1);
