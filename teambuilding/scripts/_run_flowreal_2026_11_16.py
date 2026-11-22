# -*- coding: utf-8 -*-
"""把 site_check_flow_real 当模块真调一次（该文件没有 __main__，直接跑永远 exit 0）。"""
import sys
import os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

TB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TB)
import site_check_flow_real as M  # noqa: E402

errs = []
M.check_flow_real(errs, TB)
print('-' * 70)
print('异常 %d 项' % len(errs))
for e in errs:
    print('❌', e)
