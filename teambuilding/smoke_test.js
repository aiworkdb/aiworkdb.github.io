// T1 快速版生成器冒烟测试：抽出内联 JS，用 DOM stub 跑全组合
const fs = require('fs');
const path = require('path');

const file = path.join(__dirname, 'play', 'tools', 'plan-generator', 'index.html');
const html = fs.readFileSync(file, 'utf8');
const m = html.match(/<script>([\s\S]*?)<\/script>/);
if (!m) { console.error('未找到内联 script'); process.exit(1); }
const code = m[1];

// ---- DOM stub ----
let captured = '';
const el = {
  set innerHTML(v) { captured = v; },
  get innerHTML() { return captured; },
  scrollIntoView() {},
  classList: { contains: () => false, add() {}, remove() {} },
  getAttribute: () => '',
};
global.document = {
  getElementById: () => el,
  querySelectorAll: () => [],
};
global.alert = (msg) => { throw new Error('弹出 alert（应为已填满四维）: ' + msg); };
global.window = { print() {} };

const ctx = {};
const fn = new Function(code + '\nreturn { GAMES, PURPOSE_MAP, MAIN_GENERATOR, SELECTED, generatePlan, buildTimelineHtml, splitFooterHtml, purposeMapHtml, gameLinkHtml, scoreGame };');
Object.assign(ctx, fn());

const { GAMES, SELECTED, generatePlan, scoreGame } = ctx;
let pass = 0, fail = 0;
const problems = [];

// 静态断言
if (GAMES.length !== 22) { problems.push('精选库应为 22 款，实际 ' + GAMES.length); fail++; }
GAMES.forEach(g => {
  if (!g.doc) { problems.push('缺文档链接: ' + g.name); fail++; }
  if (!g.purpose || !g.forms.length || !g.peoples.length || !g.durations.length) {
    problems.push('维度不全: ' + g.name); fail++;
  }
});

const PURPOSES = ['破冰热场', '沟通表达', '团队协作', '信任建立', '领导力', '创新思维'];
const FORMS = ['室内', '户外', '线上'];
const PEOPLES = ['10人以下', '10-30人', '30人以上'];
const DURATIONS = ['30分钟内', '30-60分钟', '60分钟以上'];

let empty = 0;
const scoreDist = { 0: 0, 1: 0, 2: 0, 3: 0 };
for (const p of PURPOSES) for (const f of FORMS)
  for (const pe of PEOPLES) for (const d of DURATIONS) {
    SELECTED.purpose = p; SELECTED.form = f; SELECTED.people = pe; SELECTED.duration = d;
    captured = '';
    try {
      generatePlan();
    } catch (e) {
      problems.push(`[${p}/${f}/${pe}/${d}] 抛错: ${e.message}`); fail++; continue;
    }
    if (!captured) { problems.push(`[${p}/${f}/${pe}/${d}] 无输出`); fail++; continue; }
    // 每一组结果都必须给出主生成器入口（分工是硬要求）
    if (captured.indexOf('toolbox/generator.html') < 0) {
      problems.push(`[${p}/${f}/${pe}/${d}] 结果区缺少主生成器入口`); fail++; continue;
    }
    if (captured.indexOf('没有找到匹配的游戏') >= 0) { empty++; pass++; continue; }

    // 匹配度徽章必须存在，且按降序排列（分层打分的核心保证）
    const scores = (captured.match(/匹配 (\d)\/3/g) || []).map(s => parseInt(s.match(/(\d)/)[1], 10));
    if (!scores.length) { problems.push(`[${p}/${f}/${pe}/${d}] 无匹配度徽章`); fail++; continue; }
    for (let i = 1; i < scores.length; i++) {
      if (scores[i] > scores[i - 1]) {
        problems.push(`[${p}/${f}/${pe}/${d}] 匹配度未降序: ${scores.join(',')}`); fail++; break;
      }
    }
    // 首位必须是该目的下的最优解（不能漏掉更高分的游戏）
    const poolBest = Math.max(...GAMES.filter(g => g.purpose === p).map(g => scoreGame(g, f, pe, d)));
    if (scores[0] !== poolBest) {
      problems.push(`[${p}/${f}/${pe}/${d}] 首位 ${scores[0]} != 该目的最优 ${poolBest}`); fail++; continue;
    }
    scoreDist[scores[0]]++;
    // 推荐出的游戏必须都能链到主库文档
    if ((captured.match(/查看玩法/g) || []).length === 0) {
      problems.push(`[${p}/${f}/${pe}/${d}] 推荐游戏无文档链接`); fail++; continue;
    }
    pass++;
  }

// 分工提示与口径表
const sf = ctx.splitFooterHtml();
if (sf.indexOf('61') < 0) { problems.push('splitFooterHtml 未说明还有 61 款'); fail++; }
const pm = ctx.purposeMapHtml();
if (pm.indexOf('问题解决') < 0) { problems.push('purposeMapHtml 未提示主库另有两类'); fail++; }

console.log(`组合 ${pass + fail} 组：通过 ${pass}，失败 ${fail}`);
console.log(`空结果 ${empty} 组；首位匹配度分布 3/3:${scoreDist[3]} 2/3:${scoreDist[2]} 1/3:${scoreDist[1]} 0/3:${scoreDist[0]}`);
if (problems.length) {
  console.log('--- 问题 ---');
  problems.slice(0, 20).forEach(p => console.log('  ' + p));
  process.exit(1);
}
console.log('ALL PASS');
