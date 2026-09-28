# -*- coding: utf-8 -*-
"""Imágenes enviadas por el cliente el 2026-09-26 (chat "Landing Faser Group") → img/.
Hero nuevo (Guyana Web.png), Lotus Gardens (principal + 5 de galería) y hotel (principal + collage de 4 recortado)."""
import os
import numpy as np
from PIL import Image
O = '_originales/cliente-2026-09-26'; D = 'img'

def save(im, name, w, q=80):
    im = im.convert('RGB')
    if im.width > w: im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    im.save(f'{D}/{name}.webp', 'WEBP', quality=q, method=6)
    print(f'{name}.webp {im.size} {os.path.getsize(f"{D}/{name}.webp") // 1024} KB')

def bbox_nonwhite(im, box):
    # filas/columnas con más de la mitad de píxeles no blancos (ignora las líneas guía finas del collage)
    a = np.asarray(im.crop(box).convert('L')) < 235
    rows = np.where(a.mean(axis=1) > .5)[0]; cols = np.where(a.mean(axis=0) > .5)[0]
    return (box[0] + cols.min(), box[1] + rows.min(), box[0] + cols.max() + 1, box[1] + rows.max() + 1)

# Hero: el cielo queda para el texto (pedido del cliente)
hero = Image.open(f'{O}/Guyana Web.png').convert('RGB')
save(hero, 'hero-guyana', 2560, 76)
save(hero, 'hero-guyana-1600', 1600, 76)
save(hero.crop((1880, 0, 3620, 3072)), 'hero-guyana-m', 1100, 74)   # vertical: puente y río

# Lotus Gardens
save(Image.open(f'{O}/IMG-20260926-WA0002.jpg'), 'lotus-main', 1400, 74)
save(Image.open(f'{O}/IMG-20260926-WA0002.jpg'), 'lotus-main-800', 800, 76)
LOTUS = {'lotus-dining': 'IMG-20260926-WA0004.jpg', 'lotus-pool': 'IMG-20260926-WA0003.jpg', 'lotus-aerial-lotus': 'IMG-20260926-WA0014.jpg',
         'lotus-living': 'IMG-20260926-WA0005.jpg', 'lotus-aerial': 'IMG-20260926-WA0006.jpg'}
for n, f in LOTUS.items():
    im = Image.open(f'{O}/{f}'); save(im, n, 1400, 72); save(im, n + '-600', 600, 72)

# Hotel
save(Image.open(f'{O}/IMG-20260926-WA0009.jpg'), 'hotel-main', 1640, 82)
save(Image.open(f'{O}/IMG-20260926-WA0009.jpg'), 'hotel-main-800', 800, 76)
col = Image.open(f'{O}/IMG-20260926-WA0010.jpg').convert('RGB')
HOTEL = {'hotel-bim': (0, 0, 495, 751), 'hotel-facade-dusk': (505, 0, 1540, 372), 'hotel-facade': (505, 380, 1036, 751), 'hotel-lobby': (1044, 380, 1540, 751)}
for n, box in HOTEL.items():
    im = col.crop(bbox_nonwhite(col, box)); save(im, n, 1200, 84); save(im, n + '-600', 600, 78)
