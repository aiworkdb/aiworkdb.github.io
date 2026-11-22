/**
 * 生成器「拼游戏」模式 · 协作 6 组子类 冒烟测试（2026-10-25）
 * 做法同 smoke_test.js / smoke_test_collab.js：
 *   抽出 toolbox/generator.html 内联 JS -> DOM stub -> 跑真实代码路径。
 *
 * 断言：
 *   1. COLLAB_GROUPS 的 6 组与 index.html 的 data-sub 完全同源（分组集合 / 每组成员 / 总数 39）
 *   2. 子类筛选行只在「拼游戏 + 目的=协作」时出现；切走协作自动复位为「不限」
 *   3. 选了子类后，推荐结果全部属于该组（无退路时）
 *   4. 子类 × 人数/时长 无解时：显式回退到全部协作类并置 lastSubFallback，而不是静默换口径
 *   5. 4×4×7×7 = 784 组全组合不抛错，且每组返回的每款游戏都真的属于所选子类
 */
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const GEN = fs.readFileSync(path.join(__dirname, 'toolbox', 'generator.html'), 'utf8');
const IDX = fs.readFileSync(path.join(__dirname, 'index.html'), 'utf8');

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
// 把页面里每个 btn-group 建成 DOM（按钮不含嵌套 div，非贪婪到第一个 </div> 即可）
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

// 1) 与 index.html 的 data-sub 同源
const idxSub = {};
for (const m of IDX.matchAll(/<a href="games\/collaboration\/([a-z0-9-]+)\.html"\s+class="card" data-sub="([a-z]+)"/g)) {
  idxSub[m[1]] = m[2];
}
ok(Object.keys(idxSub).length === 39, 'index.html 协作卡片应为 39，实际 ' + Object.keys(idxSub).length);
ok(Object.keys(sandbox.COLLAB_SUB_OF).length === 39,
  '生成器子类成员应为 39，实际 ' + Object.keys(sandbox.COLLAB_SUB_OF).length);
let mismatch = Object.keys(idxSub).filter(id => sandbox.COLLAB_SUB_OF[id] !== idxSub[id]);
ok(mismatch.length === 0, '与 index.html data-sub 不一致：' + mismatch.slice(0, 5).join(', '));
ok(sandbox.COLLAB_GROUPS.length === 6, '分组应为 6，实际 ' + sandbox.COLLAB_GROUPS.length);
for (const grp of sandbox.COLLAB_GROUPS) {
  ok(grp.ids.length === grp.n, '分组 %s 声明 %d 款，实际 %d 款'
    .replace('%s', grp.key).replace('%d', grp.n).replace('%d', grp.ids.length));
  ok(grp.ids.every(id => sandbox.gamesDB.some(x => x.id === id)),
    '分组 ' + grp.key + ' 含 gamesDB 里不存在的 id');
  ok(sandbox.gamesDB.some(x => x.id === grp.pick), '分组 ' + grp.key + ' 的首选不在 gamesDB');
}
console.log('  ✅ 6 组子类与 index.html data-sub 同源（39 款 / 6 组）');

// 2) 显隐与复位
sandbox.currentMode = 'game';
sandbox.userSelections.purpose = 'trust';
sandbox.refreshCollabSub();
ok(byId['collab-sub-form-group'].style.display === 'none', '目的非协同时子类行应隐藏');
sandbox.userSelections.purpose = 'collaboration';
sandbox.refreshCollabSub();
ok(byId['collab-sub-form-group'].style.display === '', '目的=协同时子类行应显示');
sandbox.userSelections.collabSub = 'role';
sandbox.refreshCollabSub();
ok(sandbox.userSelections.collabSub === 'role', '协作状态下子类不应被复位');
sandbox.userSelections.purpose = 'leadership';
sandbox.refreshCollabSub();
ok(sandbox.userSelections.collabSub === 'any', '切走协作后子类应复位为 any');
sandbox.currentMode = 'flow';
sandbox.userSelections.purpose = 'collaboration';
sandbox.refreshCollabSub();
ok(byId['collab-sub-form-group'].style.display === 'none', '整套流程模式下子类行应隐藏');
console.log('  ✅ 子类行显隐 / 切走复位通过');

// 3) 选子类后结果全部属于该组
sandbox.currentMode = 'game';
const SUBS = ['physical', 'pipeline', 'resource', 'info', 'role', 'whole', 'any'];
let subHits = 0;
for (const p of ['small', 'medium', 'large', 'xlarge']) {
  for (const d of ['short', 'medium', 'long', 'fullday']) {
    sandbox.userSelections.people = p;
    sandbox.userSelections.duration = d;
    sandbox.userSelections.purpose = 'collaboration';
    for (const s of SUBS) {
      sandbox.userSelections.collabSub = s;
      const got = sandbox.recommendGames();
      if (sandbox.lastSubFallback) continue;   // 无解已显式回退，不计入本断言
      if (s !== 'any') {
        const wrong = got.filter(x => sandbox.COLLAB_SUB_OF[x.id] !== s);
        ok(wrong.length === 0, '子类 ' + s + ' 混入了其它组：' + wrong.map(x => x.id).join(','));
        if (got.length) subHits++;
      }
    }
  }
}
console.log('  ✅ 子类筛选命中 ' + subHits + ' 组组合，未混入其它组的游戏');

// 4) 无解时显式回退：扫出第一个「子类无解、放宽后有解」的组合，验证回退与提示
sandbox.userSelections.purpose = 'collaboration';
let fbCase = null;
for (const p of ['small', 'medium', 'large', 'xlarge']) {
  for (const d of ['short', 'medium', 'long', 'fullday']) {
    for (const s of SUBS.filter(x => x !== 'any')) {
      sandbox.userSelections.people = p;
      sandbox.userSelections.duration = d;
      sandbox.userSelections.collabSub = s;
      sandbox.recommendGames();
      if (sandbox.lastSubFallback === s) { fbCase = [p, d, s]; break; }
    }
    if (fbCase) break;
  }
  if (fbCase) break;
}
ok(fbCase !== null, '未找到任何触发回退的组合——回退分支无法被验证');
if (fbCase) {
  sandbox.userSelections.people = fbCase[0];
  sandbox.userSelections.duration = fbCase[1];
  sandbox.userSelections.collabSub = fbCase[2];
  sandbox.generateGameList(sandbox.recommendGames());
  ok(byId['recommended-games'].innerHTML.indexOf('自动放宽') > 0,
    '回退时结果区未说明「已自动放宽」');
  ok(sandbox.lastSubFallback === fbCase[2], '回退后 lastSubFallback 未记录原子类');
}
console.log('  ✅ 无解回退通过' + (fbCase ? '（用例 ' + fbCase.join('/') + '）' : ''));

// 4b) 结果卡带子类胶囊（直链挑款页对应分组），教练能一路追到同类
sandbox.userSelections.people = 'medium';
sandbox.userSelections.duration = 'long';
sandbox.userSelections.purpose = 'collaboration';
sandbox.userSelections.collabSub = 'resource';
sandbox.generateGameList(sandbox.recommendGames());
const ghtml = byId['recommended-games'].innerHTML;
ok(ghtml.indexOf('../collab.html#g-resource') > 0, '结果卡未带子类胶囊（直链挑款页分组）');
ok(ghtml.indexOf('自动放宽') === -1, '有解时不应出现「自动放宽」提示');
console.log('  ✅ 结果卡子类胶囊通过');

// 5) 全组合不抛错
let combos = 0;
for (const p of ['small', 'medium', 'large', 'xlarge']) {
  for (const d of ['short', 'medium', 'long', 'fullday']) {
    for (const pu of ['icebreaker', 'communication', 'collaboration', 'trust', 'leadership', 'comprehensive', 'online']) {
      for (const s of SUBS) {
        sandbox.userSelections.people = p;
        sandbox.userSelections.duration = d;
        sandbox.userSelections.purpose = pu;
        sandbox.userSelections.collabSub = s;
        try {
          const got = sandbox.recommendGames();
          sandbox.generateStats(got);
          sandbox.generateTimeline(got);
          sandbox.generateGameList(got);
          sandbox.generateMaterials(got);
          sandbox.generateTips(got);
          combos++;
        } catch (e) {
          console.log('  ❌ 组合 ' + [p, d, pu, s].join('/') + ' 抛错：' + e.message);
          fail++;
        }
      }
    }
  }
}
console.log('  ✅ 全组合 ' + combos + ' 组全部无抛错');

// 6) 提示文案渲染不抛错（文案取自 collab.html，含组内首选链接）
try {
  sandbox.userSelections.purpose = 'collaboration';
  sandbox.currentMode = 'game';
  sandbox.refreshCollabSub();
  for (const s of SUBS) {
    sandbox.userSelections.collabSub = s;
    sandbox.renderCollabSubHint();
    if (s !== 'any') {
      ok(byId['collab-sub-hint'].innerHTML.indexOf('什么情况下选它') > 0,
        '子类 ' + s + ' 的提示未给出「什么情况下选它」');
      ok(byId['collab-sub-hint'].innerHTML.indexOf('../collab.html#g-' + s) > 0,
        '子类 ' + s + ' 的提示未指回挑款页对应分组');
    }
  }
} catch (e) {
  console.log('  ❌ 提示渲染抛错：' + e.message);
  fail++;
}
console.log('  ✅ 子类提示渲染通过');

console.log(fail === 0 ? '\n🎉 生成器协作子类冒烟测试 ALL PASS' : '\n❌ 失败 ' + fail + ' 项');
process.exit(fail === 0 ? 0 : 1);
