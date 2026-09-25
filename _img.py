# -*- coding: utf-8 -*-
"""Optimiza los assets del boceto de la diseñadora (_originales/diseno-v04/images) → img/."""
import os
from PIL import Image
O = os.path.join('_originales', 'diseno-v04', 'images'); D = 'img'

def web(src, dst, w, q=80, keep_alpha=False):
    im = Image.open(os.path.join(O, src))
    if keep_alpha:
        im = im.convert('RGBA')
    else:
        im = im.convert('RGBA'); bg = Image.new('RGBA', im.size, (255, 255, 255, 255)); bg.alpha_composite(im); im = bg.convert('RGB')
    if im.width > w: im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    im.save(os.path.join(D, dst + '.webp'), 'WEBP', quality=q, method=6)
    print(f'{dst}.webp {im.size} {os.path.getsize(os.path.join(D, dst + ".webp")) // 1024} KB')

# hero: ver _hero_gy.py (la foto background-guyana.jpg del boceto es JFK, Nueva York)
web('duke-main.png', 'duke-main', 1640, 80)
web('duke-tower.png', 'duke-tower', 900, 82)
for n in ['duke-balcony', 'duke-pool', 'duke-exterior', 'duke-family']:
    web(n + '.png', n, 1200, 80)
web('computer.png', 'laptop-duke', 1400, 84, keep_alpha=True)
# logo: recorte de márgenes y ancho útil 2x
lg = Image.open(os.path.join(O, 'faser-group.png')).convert('RGBA'); lg = lg.crop(lg.getbbox())
lg = lg.resize((640, round(lg.height * 640 / lg.width)), Image.LANCZOS); lg.save(os.path.join(D, 'faser-group.png'), optimize=True)
print('faser-group.png', lg.size, os.path.getsize(os.path.join(D, 'faser-group.png')) // 1024, 'KB')
# íconos de servicios (línea negra sobre transparente) a 2x del tamaño de uso
for i in range(1, 5):
    ic = Image.open(os.path.join(O, f'service-{i}.png')).convert('RGBA'); ic = ic.crop(ic.getbbox()); ic.thumbnail((160, 160), Image.LANCZOS)
    ic.save(os.path.join(D, f'service-{i}.png'), optimize=True); print(f'service-{i}.png', ic.size, os.path.getsize(os.path.join(D, f'service-{i}.png')) // 1024, 'KB')
# favicon: símbolo FS (parte roja del logo)
px = lg.load(); xr = max(x for x in range(lg.width) for y in range(lg.height) if px[x, y][3] > 0 and px[x, y][0] > 150 and px[x, y][1] < 90)
mk = lg.crop((0, 0, xr + 2, lg.height)); mk = mk.crop(mk.getbbox())
sq = Image.new('RGBA', (max(mk.size),) * 2, (0, 0, 0, 0)); sq.paste(mk, ((sq.width - mk.width) // 2, (sq.height - mk.height) // 2))
sq.resize((180, 180), Image.LANCZOS).save(os.path.join(D, 'apple-touch-icon.png')); sq.resize((64, 64), Image.LANCZOS).save(os.path.join(D, 'favicon.png'))
# imagen para compartir (OG)
og = Image.open(os.path.join(O, 'duke-main.png')).convert('RGB'); og = og.resize((1200, round(og.height * 1200 / og.width))); t = (og.height - 630) // 2
og.crop((0, t, 1200, t + 630)).save(os.path.join(D, 'og-faser.jpg'), quality=82); print('og ok')

# Variantes para móvil (srcset / image-set)
VARIANTS = {'duke-main': [800, 1200], 'duke-tower': [600], 'laptop-duke': [800],
            'duke-balcony': [600], 'duke-pool': [600], 'duke-exterior': [600], 'duke-family': [600]}
SRC = {'duke-main': 'duke-main.png', 'duke-tower': 'duke-tower.png', 'laptop-duke': 'computer.png',
       'duke-balcony': 'duke-balcony.png', 'duke-pool': 'duke-pool.png', 'duke-exterior': 'duke-exterior.png', 'duke-family': 'duke-family.png'}
for n, ws in VARIANTS.items():
    for w in ws:
        web(SRC[n], f'{n}-{w}', w, 76, keep_alpha=(n == 'laptop-duke'))
