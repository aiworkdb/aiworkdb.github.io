#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""移动端巡检：在 390px 宽的 iframe 里加载每个页面，检查横向溢出并截图。

headless Chrome 的窗口有最小宽度（约 500px），直接用 --window-size=390 量不准；
这里把页面塞进固定 390px 的 iframe，媒体查询按 iframe 宽度生效，测量才可信。

harness 文件固定放在仓库根的 __harness.html（只写不删，避免触发批量删除保护），
请把它加进 .gitignore。

用法：
    python3 tools/mobile_audit.py                 # 全站巡检
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

HARNESS = """<!DOCTYPE html><html><head><meta charset="utf-8">
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
  var de = d.documentElement;
  var res = {sw: de.scrollWidth, cw: de.clientWidth, bad: [], tries: tries};
  function scrollable(el){
    while(el && el !== de){
      var cs = getComputedStyle(el);
      if(cs.overflowX === 'auto' || cs.overflowX === 'scroll' || cs.overflowX === 'hidden') return true;
      el = el.parentElement;
    }
    return false;
  }
  d.querySelectorAll('body *').forEach(function(el){
    var r = el.getBoundingClientRect();
    if(r.width > 0 && r.right > de.clientWidth + 1 && !scrollable(el)){
      var cls = el.className && el.className.toString ? el.className.toString().slice(0,30) : '';
      res.bad.push(el.tagName + '.' + cls + ' right=' + Math.round(r.right));
    }
  });
  res.bad = res.bad.slice(0, 6);
  document.title = 'PROBE' + JSON.stringify(res) + 'PROBE';
}
f.addEventListener('load', function(){ setTimeout(probe, 200); });
setTimeout(probe, 400);
</script></body></html>""" % (W, H, PORT)


def ensure_harness():
    p = BASE / HARNESS_NAME
    if not p.exists() or p.read_text(encoding='utf-8') != HARNESS:
        p.write_text(HARNESS, encoding='utf-8')


def chrome(url, dump=True, shot=None, win=(W + 40, H + 40)):
    args = [CHROME, '--headless=new', '--no-sandbox', '--disable-gpu',
            '--single-process', '--hide-scrollbars', '--virtual-time-budget=4000',
            f'--window-size={win[0]},{win[1]}']
    if shot:
        args += [f'--screenshot={shot}', '--force-device-scale-factor=2']
    if dump:
        args += ['--dump-dom']
    args.append(url)
    return subprocess.run(args, capture_output=True, text=True, timeout=120).stdout


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
    a = ap.parse_args()
    ensure_harness()

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
    for rel in pages:
        r = probe(rel)
        if r is None:
            print(f'  ?? {rel} 探针未返回')
            continue
        if r['sw'] > r['cw'] + 1 or r['bad']:
            bad += 1
            print(f'  x {rel}  scrollWidth={r["sw"]} / 视口={r["cw"]}')
            for b in r['bad']:
                print('      ', b)
    print(f'\n巡检 {len(pages)} 页，横向溢出 {bad} 页')
    return 0 if bad == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
