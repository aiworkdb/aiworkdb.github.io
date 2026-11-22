/**
 * 生成器「拼游戏」模式 · 线上 4 组子类 冒烟测试（2026-10-28）
 * 做法同 smoke_test_generator_collab.js / smoke_test_generator_ice.js：
 *   抽出 toolbox/generator.html 内联 JS -> DOM stub -> 跑真实代码路径。
 *
 * 断言：
 *   1) ONLINE_GROUPS 的 4 组与 index.html 的 data-online、online.html 的表格三方同源
 *   2) 子类筛选行只在「拼游戏 + 目的=线上团建」时出现；切走线上自动复位为「不限」
 *   3) 选了子类后，推荐结果全部属于该组
 *   4) 4 人数桶 × 4 时长桶 × 5 子类 = 80 组全组合不抛错
 *   5) **线上子类无解时的真实路径**（重要，见下方注释）：
 *      线上 8 款在 4 个人数桶下**全部匹配**（5 人起都能玩），
 *      所以「子类 × 人数」永远筛不空任何一组 —— 子类回退分支在当前数据下
 *      不会由人数触发。它是**结构性安全网**（将来若新增一款只支持
 *      10-20 人的线上游戏，它才会生效）。
 *      真正会「装不下」的是**时长**：⏳异步接力 60 min 装不进「1 小时以内」
 *      的 50 min 预算 —— 这时走的是生成器通用的 overflow 路径
 *      （推荐最接近的一款 + 明说时长会超出）。本测试两条都验。
 *   6) 回退目标必须是「全部 8 款线上」而不是整个游戏库
 *   7) 协作 6 组 / 创意解题 4 组 / 破冰 4 组不受影响
 */
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const GEN = fs.readFileSync(path.join(__dirname, 'toolbox', 'generator.html'), 'utf8');
const IDX = fs.readFileSync(path.join(__dirname, 'index.html'), 'utf8');
const ONL = fs.readFileSync(path.join(__dirname, 'online.html'), 'utf8');

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

// 1) 与 index.html 的 data-online 同源
const idxOnline = {};
for (const m of IDX.matchAll(/<a href="games\/online\/([a-z0-9-]+)\.html"\s+class="card" data-online="([a-z]+)"/g)) {
  idxOnline[m[1]] = m[2];
}
ok(Object.keys(idxOnline).length === 8, 'index.html 线上卡片应为 8，实际 ' + Object.keys(idxOnline).length);
ok(Object.keys(sandbox.ONLINE_SUB_OF).length === 8,
  '生成器子类成员应为 8，实际 ' + Object.keys(sandbox.ONLINE_SUB_OF).length);
const mismatch = Object.keys(idxOnline).filter(id => sandbox.ONLINE_SUB_OF[id] !== idxOnline[id]);
ok(mismatch.length === 0, '与 index.html data-online 不一致：' + mismatch.slice(0, 5).join(', '));
ok(sandbox.ONLINE_GROUPS.length === 4, '分组应为 4，实际 ' + sandbox.ONLINE_GROUPS.length);

// 1b) 第三处同源：online.html 的分组表格
const onlKeys = [...ONL.matchAll(/<div class="group-card" id="g-([a-z]+)">/g)].map(x => x[1]);
ok(onlKeys.length === 4, 'online.html 应有 4 组，实际 ' + onlKeys.length);
for (const grp of sandbox.ONLINE_GROUPS) {
  ok(grp.ids.length === grp.n, '分组 ' + grp.key + ' 声明 ' + grp.n + ' 款，实际 ' + grp.ids.length);
  ok(grp.ids.every(id => sandbox.gamesDB.some(x => x.id === id)),
    '分组 ' + grp.key + ' 含 gamesDB 里不存在的 id');
  ok(sandbox.gamesDB.some(x => x.id === grp.pick), '分组 ' + grp.key + ' 的首选不在 gamesDB');
  const i = ONL.indexOf('<div class="group-card" id="g-' + grp.key + '">');
  const idx = onlKeys.indexOf(grp.key);
  const end = idx + 1 < onlKeys.length
    ? ONL.indexOf('<div class="group-card" id="g-' + onlKeys[idx + 1] + '">')
    : ONL.indexOf('<h2>💻 线上不只是这 8 款</h2>');
  const seg = ONL.slice(i, end);
  const htmlIds = [...seg.matchAll(/<tr><td><a href="games\/online\/([a-z0-9-]+)\.html">/g)].map(x => x[1]);
  ok(JSON.stringify(htmlIds.slice().sort()) === JSON.stringify(grp.ids.slice().sort()),
    '分组 ' + grp.key + ' 与 online.html 表格不一致：'
    + JSON.stringify(grp.ids) + ' vs ' + JSON.stringify(htmlIds));
}
console.log('  ✅ 4 组子类与 index.html data-online / online.html 表格三方同源（8 款 / 4 组）');

// 2) 显隐与复位
sandbox.currentMode = 'game';
sandbox.userSelections.purpose = 'trust';
sandbox.refreshOnlineSub();
ok(byId['online-sub-form-group'].style.display === 'none', '目的非线同时子类行应隐藏');
sandbox.userSelections.purpose = 'online';
sandbox.refreshOnlineSub();
ok(byId['online-sub-form-group'].style.display === '', '目的=线同时子类行应显示');
sandbox.userSelections.onlineSub = 'voice';
sandbox.refreshOnlineSub();
ok(sandbox.userSelections.onlineSub === 'voice', '线上状态下子类不应被复位');
sandbox.userSelections.purpose = 'leadership';
sandbox.refreshOnlineSub();
ok(sandbox.userSelections.onlineSub === 'any', '切走线上后子类应复位为 any');
sandbox.currentMode = 'flow';
sandbox.userSelections.purpose = 'online';
sandbox.refreshOnlineSub();
ok(byId['online-sub-form-group'].style.display === 'none', '整套流程模式下子类行应隐藏');
console.log('  ✅ 子类行显隐 / 切走复位通过');

// 3) 选子类后结果全部属于该组 + 全组合不抛错
sandbox.currentMode = 'game';
const SUBS = ['voice', 'screen', 'doc', 'async', 'any'];
const PEOPLE = ['small', 'medium', 'large', 'xlarge'];
const DURS = ['short', 'medium', 'long', 'fullday'];
let subHits = 0;
let comboCount = 0;
let fbHits = 0;
for (const p of PEOPLE) {
  for (const d of DURS) {
    sandbox.userSelections.people = p;
    sandbox.userSelections.duration = d;
    sandbox.userSelections.purpose = 'online';
    for (const s of SUBS) {
      sandbox.userSelections.onlineSub = s;
      const got = sandbox.recommendGames();
      comboCount++;
      if (sandbox.lastOnlineFallback) { fbHits++; continue; }
      if (s !== 'any') {
        const wrong = got.filter(x => sandbox.ONLINE_SUB_OF[x.id] !== s);
        ok(wrong.length === 0, '子类 ' + s + ' 混入了其它组：' + wrong.map(x => x.id).join(','));
        if (got.length) subHits++;
      }
    }
  }
}
ok(comboCount === 80, '组合数应为 4×4×5=80，实际 ' + comboCount);
console.log('  ✅ 80 组全组合不抛错；子类筛选命中 ' + subHits + ' 组组合，未混入其它组的游戏');

// 4) 人数维度筛不空任何一组 —— 这是一条「事实断言」，不是 bug
//    线上 8 款最小一款也要 5 人起，4 个人数桶全部覆盖，
//    所以「子类 × 人数」不可能为空。子类回退是结构性安全网，
//    由下面第 5 项单独验证其代码与目标集合。
let peopleAlwaysMatches = true;
for (const p of PEOPLE) {
  for (const s of SUBS.filter(x => x !== 'any')) {
    const grp = sandbox.ONLINE_GROUPS.filter(x => x.key === s)[0];
    const hit = grp.ids.filter(id => {
      const gm = sandbox.gamesDB.filter(x => x.id === id)[0];
      return gm.people.indexOf(p) >= 0 || (p === 'xlarge' && gm.people.indexOf('large') >= 0);
    });
    if (hit.length === 0) peopleAlwaysMatches = false;
  }
}
ok(peopleAlwaysMatches, '线上 8 款应覆盖 4 个人数桶（人数维度筛不空任何一组）');
ok(fbHits === 0, '人数维度不应触发子类回退（实际触发 ' + fbHits + ' 次）');
console.log('  ✅ 人数维度：8 款覆盖 4 个人数桶，子类回退不会由人数触发（安全网）');

// 5) 时长维度无解时的真实路径：⏳异步接力 60 min 装不进「1 小时以内」
//    → 走通用 overflow 路径：推荐最接近的一款 + 明说时长会超出
sandbox.userSelections.purpose = 'online';
sandbox.userSelections.people = 'medium';
sandbox.userSelections.duration = 'short';
sandbox.userSelections.onlineSub = 'async';
const gotAsync = sandbox.recommendGames();
ok(gotAsync.length > 0, '异步组 + 1 小时以内应仍给出结果（走 overflow 兜底）');
ok(gotAsync.every(x => x.category === 'online'), '结果必须全部落在线上类');
ok(sandbox.lastOverflow === true,
  '异步接力 60 min 装不进 1 小时以内，应标记时长会超出（lastOverflow）');
ok(gotAsync.some(x => x.id === 'async-relay'),
  'overflow 兜底应推荐该组唯一一款 async-relay');
console.log('  ✅ 时长维度：异步组 + 1 小时以内 → overflow 兜底 + 明说时长会超出');

// 6) 回退分支的代码与目标集合正确（即使当前数据触发不到，也必须是对的）
ok(sandbox.ONLINE_ALL_IDS.length === 8, 'ONLINE_ALL_IDS 应有 8 款，实际 ' + sandbox.ONLINE_ALL_IDS.length);
const allCats = new Set(sandbox.ONLINE_ALL_IDS.map(id => (sandbox.gamesDB.find(x => x.id === id) || {}).category));
ok(allCats.size === 1 && allCats.has('online'),
  'ONLINE_ALL_IDS 应全部是 online 类，实际 ' + [...allCats].join('/'));
ok(/ONLINE_SUB_OF\[game\.id\] === onlineKey/.test(GEN), '筛应用的是分组映射而不是硬编码');
ok(/lastOnlineFallback/.test(GEN), '应存在 lastOnlineFallback 回退标记');
ok(/onlineAll/.test(GEN), '回退目标应是 onlineAll（全部 8 款线上）而非整个游戏库');
console.log('  ✅ 子类回退的目标集合 = 全部 8 款线上（不放宽到整个游戏库）');

// 7) 异步组只有 1 款，且是全库唯一一款异步游戏
const asyncGrp = sandbox.ONLINE_GROUPS.filter(x => x.key === 'async')[0];
ok(asyncGrp && asyncGrp.ids.length === 1, '异步组应只有 1 款');
ok(asyncGrp && asyncGrp.ids[0] === 'async-relay', '异步组那唯一一款应是 async-relay');
ok(asyncGrp && asyncGrp.pick === 'async-relay', '异步组的首选应是 async-relay');

// 8) 协作 6 组 / 创意解题 4 组 / 破冰 4 组不受影响
ok(sandbox.COLLAB_GROUPS.length === 6, '协作子类仍应是 6 组，实际 ' + sandbox.COLLAB_GROUPS.length);
ok(sandbox.IDEA_GROUPS.length === 4, '创意解题子类仍应是 4 组，实际 ' + sandbox.IDEA_GROUPS.length);
ok(sandbox.ICE_GROUPS.length === 4, '破冰子类仍应是 4 组，实际 ' + sandbox.ICE_GROUPS.length);

// 9) 按钮与入口齐全
ok(byId['online-sub-group'] && byId['online-sub-group'].querySelectorAll('.btn-option').length === 5,
  'onlineSub 按钮应为 5 个（4 组 + 不限），实际 '
  + (byId['online-sub-group'] ? byId['online-sub-group'].querySelectorAll('.btn-option').length : 'N/A'));
ok(/params\.get\('online'\)/.test(GEN), '应支持 URL 参数 ?online=');
ok(/refreshOnlineSub/.test(GEN), '应存在 refreshOnlineSub 显隐逻辑');

console.log(fail === 0 ? '\nALL PASS' : '\n' + fail + ' 项失败');
process.exit(fail === 0 ? 0 : 1);
