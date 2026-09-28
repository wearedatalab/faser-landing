# -*- coding: utf-8 -*-
"""Paquete para producción (fasergroup.com): copia solo lo publicable y cambia las URL absolutas
de la vista previa (GitHub Pages) por el dominio real. Resultado: dist/ y faser-landing-produccion.zip"""
import os, shutil, zipfile
PREVIEW = 'https://wearedatalab.github.io/faser-landing/'
PROD = os.environ.get('FASER_SITE', 'https://fasergroup.com/')
KEEP = ['index.html', 'es', 'css', 'js', 'img', 'robots.txt', 'sitemap.xml']
TEXT = ('.html', '.xml', '.txt', '.css', '.js')
if os.path.exists('dist'): shutil.rmtree('dist')
os.makedirs('dist')
for k in KEEP:
    (shutil.copytree if os.path.isdir(k) else shutil.copy2)(k, os.path.join('dist', k))
n = 0
for root, _, files in os.walk('dist'):
    for f in files:
        if f.endswith(TEXT):
            p = os.path.join(root, f); s = open(p, encoding='utf-8').read()
            if PREVIEW in s: open(p, 'w', encoding='utf-8', newline='\n').write(s.replace(PREVIEW, PROD)); n += 1
with zipfile.ZipFile('faser-landing-produccion.zip', 'w', zipfile.ZIP_DEFLATED) as z:
    for root, _, files in os.walk('dist'):
        for f in files:
            full = os.path.join(root, f); z.write(full, os.path.relpath(full, 'dist'))
print(f'dist/ listo · {n} archivos con URL de producción ({PROD}) · zip {os.path.getsize("faser-landing-produccion.zip") // 1024} KB')
