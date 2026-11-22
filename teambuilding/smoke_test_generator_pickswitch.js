/**
 * 生成器「🔀 换一整套切法」冒烟测试（2026-11-03）
 *
 * 被测对象：toolbox/generator.html 结果区顶部的 7 个跨类胶囊，点击后
 *   ① 切换 userSelections.purpose
 *   ② 顶部「🎯 主要目的」按钮选中态跟着变（上下两处不能打脸）
 *   ③ 上一套的子类条件清空（refresh* 会把不生效的 sub 置 any）
 *   ④ 重新出结果，且结果属于新目的
 *   ⑤ 胶囊选中态与实际目的一致
 *
 * 做法同 smoke_test_generator_lead.js：抽出内联 JS → DOM stub → 跑真实代码路径。
 * 新增：把 .pick-chip 也建进 stub（harness 原来只认 .btn-group 里的 .btn-option）。
 */
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const GEN = fs.readFileSync(path.join(__dirname, 'toolbox', 'generator.html'), 'utf8');
const PICK = fs.readFileSync(path.join(__dirname, 'pick.html'), 'utf8');

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

// 1) .btn-group 里的 .btn-option（原 harness）
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

// 2) 🔀 换一整套切法：7 个 .pick-chip → 各自挂到一个容器里
const bar = root.append(new El('div', { class: 'pick-switch', id: 'pick-switch-bar' }));
byId['pick-switch-bar'] = bar;
const chipBox = bar.append(new El('div', { class: 'pick-switch-chips' }));
const CHIP_RE = /<button class="pick-chip" data-purpose="([a-z]+)"[^>]*>([\s\S]*?)<\/button>/g;
let c;
const chips = [];
while ((c = CHIP_RE.exec(GEN)) !== null) {
  const el = chipBox.append(new El('button', { class: 'pick-chip', 'data-purpose': c[1] }, c[2]));
  chips.push(el);
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

// A. 与 pick.html 的七套切法同源
const PAGES = [
  ['collaboration', '动作', '动作 · 协作'],
  ['idea', '思考位置', '思考位置 · 创意解题'],
  ['communication', '通道', '通道 · 沟通'],
  ['icebreaker', '存量', '存量 · 破冰'],
  ['online', '成立条件', '成立条件 · 线上'],
  ['leadership', '权力层级', '权力层级 · 领导力'],
  ['trust', '托付内容', '托付内容 · 信任'],
];
ok(chips.length === 7, '胶囊应为 7 个（七套切法），实际 ' + chips.length);
ok(JSON.stringify(chips.map(x => x.getAttribute('data-purpose'))) === JSON.stringify(PAGES.map(p => p[0])),
  '胶囊顺序应与 pick.html 七套切法一致：' + chips.map(x => x.getAttribute('data-purpose')).join(','));

for (let i = 0; i < PAGES.length; i++) {
  const [purpose, dim, label] = PAGES[i];
  const t = chips[i] ? chips[i].text : '';
  ok(t.includes(dim), '第 ' + (i + 1) + ' 个胶囊应写出维度「' + dim + '」，实际「' + t + '」');
  ok(t.includes(label.split(' · ')[1]), '第 ' + (i + 1) + ' 个胶囊应写出所属分类，实际「' + t + '」');
  // 维度名必须在 pick.html 里也出现（同一套命名，不许另起一套）
  ok(PICK.includes('切「' + dim + '」'), 'pick.html 里找不到维度名「' + dim + '」—— 两边命名已漂移');
  // 目的值必须是生成器真实存在的 purpose 按钮值
  ok(new RegExp('data-value="' + purpose + '" onclick="selectOption\\(this, \'purpose\'\\)"').test(GEN),
    '胶囊 data-purpose="' + purpose + '" 在顶部目的按钮里找不到对应值');
}
ok(/href="\.\.\/pick\.html"/.test(GEN), '横条里应有 ../pick.html 总表入口');
console.log('  ✅ 7 个胶囊与 pick.html 七套切法 / 顶部目的按钮三方同源');

// B. 切换：目的变了、顶部按钮跟着亮、上一套子类清空
sandbox.currentMode = 'game';
sandbox.userSelections.people = 'medium';
sandbox.userSelections.duration = 'long';
sandbox.userSelections.purpose = 'collaboration';
sandbox.userSelections.collabSub = 'pipeline';
sandbox.refreshCollabSub();

// 用 stub 顶掉 generatePlan：本用例测的是「切换动作」，渲染路径另有 smoke test 覆盖
let planCalls = 0;
sandbox.__realGenerate = sandbox.generatePlan;
sandbox.generatePlan = function () { planCalls++; };

const pgBtns = byId['purpose-group'].querySelectorAll('.btn-option');
ok(pgBtns.length === 8, '顶部目的按钮应为 8 个，实际 ' + pgBtns.length);

sandbox.switchPickClass(chips[5]); // 👑 权力层级
ok(sandbox.userSelections.purpose === 'leadership',
  '点「权力层级」后 purpose 应为 leadership，实际 ' + sandbox.userSelections.purpose);
ok(sandbox.userSelections.collabSub === 'any',
  '换整套口径后协作子类应清空为 any，实际 ' + sandbox.userSelections.collabSub);
ok(planCalls === 1, '切换后应重算一次，实际 ' + planCalls + ' 次');

const activeP = pgBtns.filter(b => b.classList.contains('active')).map(b => b.getAttribute('data-value'));
ok(activeP.length === 1 && activeP[0] === 'leadership',
  '顶部目的按钮应只有 leadership 亮着，实际 ' + JSON.stringify(activeP));

const activeChips = chips.filter(x => x.classList.contains('active')).map(x => x.getAttribute('data-purpose'));
ok(activeChips.length === 1 && activeChips[0] === 'leadership',
  '胶囊应只有 leadership 亮着，实际 ' + JSON.stringify(activeChips));
console.log('  ✅ 切换后：purpose / 顶部按钮 / 胶囊 / 上一套子类 四处对齐');

// C. 七套逐个切一遍：不抛错、目的正确、结果都属于该目的允许的分类
sandbox.generatePlan = sandbox.__realGenerate;
const ALLOWED = {
  collaboration: ['collaboration', 'creativity', 'problem-solving'],
  idea: ['creativity', 'problem-solving'],
  communication: ['communication', 'trust'],
  icebreaker: ['icebreaker', 'communication'],
  online: ['online'],
  leadership: ['leadership', 'collaboration'],
  trust: ['trust', 'communication'],
};
for (let i = 0; i < chips.length; i++) {
  const purpose = chips[i].getAttribute('data-purpose');
  sandbox.switchPickClass(chips[i]);
  ok(sandbox.userSelections.purpose === purpose, '切到 ' + purpose + ' 失败');
  let got;
  try {
    got = sandbox.recommendGames();
  } catch (e) {
    ok(false, '切到 ' + purpose + ' 后 recommendGames 抛错：' + e.message);
    continue;
  }
  ok(Array.isArray(got) && got.length > 0, '切到 ' + purpose + ' 后应至少给出 1 款，实际 ' + (got && got.length));
  const bad = got.filter(x => ALLOWED[purpose].indexOf(x.category) < 0);
  ok(bad.length === 0, purpose + ' 的结果混进了不该出现的分类：' + bad.map(x => x.id).join(','));
}
console.log('  ✅ 七套逐个切换：目的正确、均有结果、分类不越界');

// D. 整套流程模式不该出现这条横条（整套流程看的是「处境」，不是七套切法）
sandbox.currentMode = 'flow';
sandbox.markPickSwitch();
ok(byId['pick-switch-bar'].style.display === 'none', '整套流程模式下横条应隐藏');
ok(/setCardVisible\('pick-switch-bar', !flowMode\)/.test(GEN),
  'generatePlan 里整套流程分支应按 flowMode 决定横条显隐');
sandbox.currentMode = 'game';
byId['pick-switch-bar'].style.display = '';   // 真实路径里由 generatePlan 的 setCardVisible 负责
sandbox.markPickSwitch();
ok(byId['pick-switch-bar'].style.display !== 'none', '拼游戏模式下横条应显示');

// E. generatePlan 里两处钩子必须在场（否则点「重新生成」后横条状态会漂）
ok(/setCardVisible\('pick-switch-bar', true\);\s*\n\s*maskPickSwitch|setCardVisible\('pick-switch-bar', true\);/.test(GEN),
  'generatePlan 的拼游戏分支应显式显示横条');
ok(/generateTips\(recommendedGames\);[\s\S]{0,200}markPickSwitch\(\);/.test(GEN),
  'generatePlan 出结果后应调用 markPickSwitch() 对齐胶囊选中态');
ok(/markPickSwitch\(\);[\s\S]{0,120}\}\s*$|markPickSwitch\(\);\n\}/.test(GEN) || /function markPickSwitch/.test(GEN),
  '应有 markPickSwitch 定义');

console.log(fail === 0 ? '\nALL PASS' : '\n' + fail + ' 项失败');
process.exit(fail === 0 ? 0 : 1);
