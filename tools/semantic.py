#!/usr/bin/env python3
import re, pathlib

MAP = {
    'bg-white': 'bg-surface',
    'bg-slate-50': 'bg-bg',
    'bg-slate-100': 'bg-surface-2',
    'bg-slate-200': 'bg-surface-2',
    'text-slate-800': 'text-text',
    'text-slate-700': 'text-text',
    'text-slate-600': 'text-muted',
    'text-slate-500': 'text-faint',
    'text-slate-400': 'text-faint',
    'text-blue-600': 'text-primary',
    'bg-blue-600': 'bg-primary',
    'bg-blue-700': 'bg-primary',
    'text-red-600': 'text-danger',
    'text-red-500': 'text-danger',
    'border-red-300': 'border-danger',
    'bg-red-50': 'bg-danger/10',
}
keys = sorted(MAP, key=len, reverse=True)

for p in pathlib.Path('app').rglob('*.vue'):
    src = orig = p.read_text(encoding='utf-8')
    for k in keys:
        # 精确匹配，排除 /透明度 和 -后缀
        src = re.sub(rf'(?<![\w:-]){re.escape(k)}(?!/[\d])(?![\w-])', MAP[k], src)
    # 裸 border → border-border（仅独立单词）
    src = re.sub(r'(?<=["\s])border(?=["\s])', 'border-border', src)
    if src != orig:
        p.write_text(src, encoding='utf-8')
        print('updated', p)