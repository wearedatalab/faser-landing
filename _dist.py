# -*- coding: utf-8 -*-
"""Paquete de producción para Hostinger (o cualquier hosting con PHP).

    python _dist.py
    FASER_FOLDER=landing FASER_BASE=https://fasergroup.com/landing/ LEADS_TO="a@x.com,b@y.com" python _dist.py

Genera dist/<carpeta>/ y faser-landing-<carpeta>.zip. El zip trae la carpeta completa: se sube a public_html
y se descomprime ahí (queda en https://dominio/<carpeta>/). Para un subdominio basta apuntar su carpeta raíz a esa.
"""
import os, re, shutil, sys, zipfile, datetime
sys.stdout.reconfigure(encoding="utf-8")

PREVIEW = 'https://wearedatalab.github.io/faser-landing/'
FOLDER = os.environ.get('FASER_FOLDER', 'landing')
BASE = os.environ.get('FASER_BASE', f'https://fasergroup.com/{FOLDER}/')
LEADS_TO = [e.strip() for e in os.environ.get('LEADS_TO', 'juan.garcia@wearedatalab.co').split(',') if e.strip()]
FROM_EMAIL = os.environ.get('FROM_EMAIL', 'no-reply@fasergroup.com')
VERSION = datetime.datetime.now().strftime('%Y%m%d%H%M')

KEEP = ['index.html', 'es', 'css', 'js', 'img', 'sitemap.xml', 'send.php', 'config.example.php', '.htaccess']
out = os.path.join('dist', FOLDER)
if os.path.exists('dist'): shutil.rmtree('dist')
os.makedirs(out)
for k in KEEP:
    (shutil.copytree if os.path.isdir(k) else shutil.copy2)(k, os.path.join(out, k))
os.makedirs(os.path.join(out, '_data'))
shutil.copy2('_data/.htaccess', os.path.join(out, '_data', '.htaccess'))
shutil.copy2('_data/index.html', os.path.join(out, '_data', 'index.html'))

# config.php real (no va al repositorio)
cfg = open('config.example.php', encoding='utf-8').read()
cfg = cfg.replace("'to' => ['__LEADS_TO__'],", "'to' => [" + ', '.join(f"'{e}'" for e in LEADS_TO) + "],")
cfg = cfg.replace('__FROM_EMAIL__', FROM_EMAIL)
open(os.path.join(out, 'config.php'), 'w', encoding='utf-8', newline='\n').write(cfg)

# URL del dominio real + versión en CSS/JS (evita que el navegador muestre archivos viejos)
n = 0
for root, _, files in os.walk(out):
    for f in files:
        if not f.endswith(('.html', '.xml')): continue
        p = os.path.join(root, f); s = open(p, encoding='utf-8').read(); s0 = s
        s = s.replace(PREVIEW, BASE)
        s = re.sub(r'((?:href|src)="(?:\.\./)?(?:css/styles\.css|js/main\.js))"', r'\1?v=' + VERSION + '"', s)
        if s != s0: open(p, 'w', encoding='utf-8', newline='\n').write(s); n += 1

zname = f'faser-landing-{FOLDER}.zip'
with zipfile.ZipFile(zname, 'w', zipfile.ZIP_DEFLATED) as z:
    for root, _, files in os.walk('dist'):
        for f in files:
            full = os.path.join(root, f); z.write(full, os.path.relpath(full, 'dist'))
print(f'{out}/ · {n} archivos ajustados a {BASE} · leads → {", ".join(LEADS_TO)} · {zname} {os.path.getsize(zname) // 1024} KB')
