#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""移动端巡检：在 390px 宽的 iframe 里加载每个页面，检查横向溢出并截图。

headless Chrome 的窗口有最小宽度（约 500px），直接用 --window-size=390 量不准；
这里把页面塞进固定 390px 的 iframe，媒体查询按 iframe 宽度生效，测量才可信。

⚠️ 判据不能再退回 documentElement.scrollWidth：
   body 带 overflow-x:hidden（lib.css 的「永不横向滚动」铁律），
   所以 de.scrollWidth 恒等于 clientWidth，用它判溢出永远是 0。
   同理，把 overflowX:hidden 当作「可滚动祖先」来豁免，等于给全站开免检通道
   （2026-11-03 发现：旧版两条叠加，166 页恒报 0 溢出，属于假绿）。
   现行判据是逐个元素比对视口宽度，且只认 auto/scroll 为可滑容器；
   另外单独报「hidden 容器里真子元素被裁」，装饰伪元素（.h-hero::after）不误报。

harness 文件固定放在仓库根的 __harness.html（只写不删，避免触发批量删除保护），
请把它加进 .gitignore。

用法：
    python3 tools/mobile_audit.py                 # 全站巡检（390px）
    python3 tools/mobile_audit.py --w 320         # 窄屏（iPhone SE / 老安卓）
    python3 tools/mobile_audit.py --only guide    # 只巡检路径含 guide 的页
    python3 tools/mobile_audit.py --shot index.html guide.html
"""
import argparse
import json
import pathlib
import re
import subprocess
import sys
import urllib.parse

BASE = pathlib.Path(__file__).resolve().parent.parent
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
PORT = 8902
W, H = 390, 844
HARNESS_NAME = '__harness.html'

HARNESS_TMPL = """<!DOCTYPE html><html><head><meta charset="utf-8">
<style>html,body{margin:0;padding:0;background:#111}
iframe{width:%dpx;height:%dpx;border:0;display:block}</style></head>
<body><iframe id="f"></iframe>
<script>
var q = new URLSearchParams(location.search);
var f = document.getElementById('f');
var tries = 0;
f.src = 'http://127.0.0.1:%d/' + (q.get('u') || 'index.html');
function probe(){
  tries++;
  var d;
  try { d = f.contentDocument; } catch(e) { d = null; }
  // iframe 可能还没就绪 —— 轮询，别赌 load 事件的时机
  if (!d || !d.documentElement || !d.body) {
    if (tries < 60) return setTimeout(probe, 100);
    document.title = 'PROBE{"err":"no-doc","tries":' + tries + '}PROBE';
    return;
  }
  var de = d.documentElement, body = d.body;
  var vw = de.clientWidth;
  // 注意：body 是 overflow-x:hidden，de.scrollWidth 恒等于 clientWidth，
  // 拿它判溢出永远是 0 —— 必须按视口宽度逐元素比对。
  var res = {sw: de.scrollWidth, cw: vw, bodySW: body.scrollWidth,
             bad: [], clip: [], tries: tries};
  function nm(el){
    var c = el.className;
    var s = (c && c.toString) ? c.toString().trim().split(' ').slice(0,2).join('.') : '';
    return el.tagName + (s ? '.' + s : '');
  }
  // 只有 auto/scroll 才算「滑得到」。hidden 是把内容裁掉，用户根本滑不到，
  // 早先把它也算作可滚动祖先，等于给全站开了免检通道。
  function realScroller(el, stop){
    var p = el.parentElement;
    while (p && p !== stop){
      var cs = getComputedStyle(p);
      if (cs.overflowX === 'auto' || cs.overflowX === 'scroll') return p;
      p = p.parentElement;
    }
    return null;
  }
  d.querySelectorAll('body *').forEach(function(el){
    var r = el.getBoundingClientRect();
    if(r.width > 0 && r.height > 0 && (r.right > vw + 1 || r.left < -1)
       && !realScroller(el, body)){
      res.bad.push(nm(el) + ' L=' + Math.round(r.left) + ' R=' + Math.round(r.right));
    }
    var cs2 = getComputedStyle(el);
    if(cs2.overflowX === 'hidden' && el.clientWidth > 0
       && el.scrollWidth - el.clientWidth > 1){
      var box = el.getBoundingClientRect(), hit = null, kids = el.querySelectorAll('*');
      for(var k = 0; k < kids.length; k++){
        var kr = kids[k].getBoundingClientRect();
        if(kr.width <= 0 || kr.height <= 0) continue;
        if(realScroller(kids[k], el)) continue;   // 中间有可滑容器，不算被裁
        if(kr.right > box.right + 1 || kr.left < box.left - 1){ hit = nm(kids[k]); break; }
      }
      // 没命中真元素 = 装饰光斑（.h-hero::after 这类故意超出再裁掉），不算内容丢失
      if(hit) res.clip.push(nm(el) + ' cw=' + el.clientWidth + ' sw=' + el.scrollWidth + ' <- ' + hit);
    }
  });
  res.bad = res.bad.slice(0, 6);
  res.clip = res.clip.slice(0, 6);
  document.title = 'PROBE' + JSON.stringify(res) + 'PROBE';
}
f.addEventListener('load', function(){ setTimeout(probe, 200); });
setTimeout(probe, 400);
</script></body></html>"""


def harness_html(w, h):
    """按目标宽度生成 harness。窄屏（320）和宽屏（414）各跑一轮才算真的「手机端好用」。"""
    return HARNESS_TMPL % (w, h, PORT)


def ensure_harness(html):
    p = BASE / HARNESS_NAME
    if not p.exists() or p.read_text(encoding='utf-8') != html:
        p.write_text(html, encoding='utf-8')


CHROME_TIMEOUT = 45      # 单页上限。virtual-time-budget 只有 4s，超 45s 基本就是卡死
CHROME_RETRY = 1         # 失败重试次数（偶发卡死占多数，重试一次通常就过）


def chrome(url, dump=True, shot=None, win=(W + 40, H + 40)):
    """跑一次 headless Chrome。

    必须自己兜住 TimeoutExpired —— 早先版本没有 try，只要一个页面卡住
    （曾遇到 games/online/online-bingo.html 挂满 120s），整轮巡检直接抛异常中断，
    后面几十页根本没被检查，而 `| tail` 还会把退出码吞掉，看起来像「跑完了」。
    """
    args = [CHROME, '--headless=new', '--no-sandbox', '--disable-gpu',
            '--disable-dev-shm-usage', '--single-process', '--hide-scrollbars',
            '--virtual-time-budget=4000',
            f'--window-size={win[0]},{win[1]}']
    if shot:
        args += [f'--screenshot={shot}', '--force-device-scale-factor=2']
    if dump:
        args += ['--dump-dom']
    args.append(url)
    for attempt in range(CHROME_RETRY + 1):
        try:
            return subprocess.run(args, capture_output=True, text=True,
                                  timeout=CHROME_TIMEOUT).stdout
        except subprocess.TimeoutExpired:
            if attempt >= CHROME_RETRY:
                return ''      # 交给上层记「探针未返回」，不中断整轮
    return ''


def harness_url(rel):
    return (f'http://127.0.0.1:{PORT}/{HARNESS_NAME}?u='
            + urllib.parse.quote(rel))


def probe(rel):
    m = re.search(r'<title>PROBE(.*?)PROBE</title>', chrome(harness_url(rel)), re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--shot', nargs='*', default=[])
    ap.add_argument('--only', nargs='*', default=[])
    ap.add_argument('--w', type=int, default=W,
                    help='目标视口宽度，默认 390；建议同时跑 320 与 414')
    a = ap.parse_args()
    ensure_harness(harness_html(a.w, H))

    if a.shot:
        outdir = BASE / '.audit'
        if not outdir.exists():
            outdir.mkdir()
        for rel in a.shot:
            name = rel.replace('/', '_').replace('.html', '') + '.png'
            chrome(harness_url(rel), dump=False, shot=str(outdir / name))
            print(f'shot -> {outdir / name}')
        return 0

    pages = ['index.html', 'guide.html']
    pages += [str(p.relative_to(BASE)) for p in sorted(BASE.glob('games/**/*.html'))]
    pages += [str(p.relative_to(BASE)) for p in sorted(BASE.glob('flows/**/*.html'))]
    pages += [str(p.relative_to(BASE)) for p in sorted(BASE.glob('toolbox/*.html'))]
    # play/ 下的在线工具与在线游戏本来就是手机端场景，一并纳入巡检
    pages += [str(p.relative_to(BASE)) for p in sorted(BASE.glob('play/**/*.html'))]
    if a.only:
        pages = [p for p in pages if any(o in p for o in a.only)]

    bad = 0
    failed = []
    for rel in pages:
        r = probe(rel)
        if r is None:
            failed.append(rel)
            print(f'  ?? {rel} 探针未返回')
            continue
        # 只看 bad/clip：sw 与 cw 因 body{overflow-x:hidden} 恒等，不能作为判据
        if r['bad'] or r.get('clip'):
            bad += 1
            print(f'  x {rel}  视口={r["cw"]} bodyScrollWidth={r.get("bodySW")}')
            for b in r['bad']:
                print('      越界:', b)
            for c in r.get('clip', []):
                print('      被裁:', c)
    print(f'\n巡检 {len(pages)} 页，横向溢出 {bad} 页，探针未返回 {len(failed)} 页')
    if failed:
        print('  未返回页面（需单独复核）：')
        for f in failed:
            print('   -', f)
    return 0 if bad == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
