# -*- coding: utf-8 -*-
"""Genera es/index.html a partir de index.html (inglés = fuente que edita la diseñadora)
y del diccionario i18n/es.json ({"texto en inglés": "texto en español"}).

Uso:  python _build_es.py
Si cambias textos en index.html:  python _i18n_extract.py  → traduce los nuevos en i18n/es.json → python _build_es.py
El script avisa qué textos quedaron sin traducir.
"""
import json, os, re, sys
from urllib.parse import quote, unquote
from bs4 import BeautifulSoup, Comment, Doctype
from _i18n_extract import ATTRS, META_OK, norm

SITE = 'https://wearedatalab.github.io/faser-landing/'
sys.stdout.reconfigure(encoding='utf-8')

src = open('index.html', encoding='utf-8').read()
tr = json.load(open('i18n/es.json', encoding='utf-8'))
missing = []

def t(text):
    k = norm(text)
    if k in tr: return tr[k]
    missing.append(k); return text

soup = BeautifulSoup(src, 'html.parser')

# 1) nodos de texto
for node in list(soup.find_all(string=True)):
    if isinstance(node, (Comment, Doctype)) or node.parent.name in ('script', 'style', 'symbol', 'svg', 'path'): continue
    raw = str(node)
    if not norm(raw) or not re.search(r'[A-Za-z]', raw): continue
    if node.parent.name == 'a' and node.parent.parent is not None and 'lang' in (node.parent.parent.get('class') or []): continue
    lead = raw[:len(raw) - len(raw.lstrip())]; trail = raw[len(raw.rstrip()):]
    node.replace_with(lead + t(raw) + trail)

# 2) atributos y mensajes prellenados de WhatsApp
for tag in soup.find_all(True):
    for a in ATTRS:
        v = tag.get(a)
        if not v or not re.search(r'[A-Za-z]', v): continue
        if a == 'content' and not (tag.get('name') in META_OK or tag.get('property') in META_OK): continue
        if tag.get('aria-label') == 'Language / Idioma' and a == 'aria-label': continue
        tag[a] = t(v)
    href = tag.get('href', '')
    m = re.search(r'([?&]text=)([^&"]+)', href)
    if m:
        es = t('URLTEXT:' + m.group(2))
        tag['href'] = href.replace(m.group(0), m.group(1) + (es[8:] if es.startswith('URLTEXT:') else m.group(2)))

# 3) rutas relativas: la página vive en /es/
def rel(u):
    if not u or u.startswith(('#', 'http', 'mailto:', 'tel:', 'data:', '/', '../')): return u
    return '../' + u
for tag in soup.find_all(True):
    for a in ('src', 'href', 'data-lb', 'action'):
        if tag.get(a) is not None and not (tag.name == 'a' and 'lang' in (tag.parent.get('class') or [])):
            tag[a] = rel(tag[a])
    for a in ('srcset', 'imagesrcset'):
        if tag.get(a):
            tag[a] = ', '.join(' '.join([rel(p.split()[0])] + p.split()[1:]) for p in tag[a].split(','))

# 4) selector de idioma: EN → ../ , ES → ./ (actual)
for nav in soup.select('nav.lang'):
    en, es = nav.find_all('a')[:2]
    en['href'] = '../'; es['href'] = './'
    del en['aria-current']; es['aria-current'] = 'true'

# 5) cabecera: idioma, canónica, OG
soup.html['lang'] = 'es'
soup.find('link', rel='canonical')['href'] = SITE + 'es/'
og = soup.find('meta', property='og:url');
if og: og['content'] = SITE + 'es/'
loc = soup.new_tag('meta', property='og:locale', content='es_CO'); soup.find('meta', property='og:type').insert_after(loc)
ld = soup.find('script', type='application/ld+json')
if ld:
    data = json.loads(ld.string); data['description'] = t(data['description']); data['url'] = SITE + 'es/'
    ld.string = json.dumps(data, ensure_ascii=False)

os.makedirs('es', exist_ok=True)
out = str(soup)
open('es/index.html', 'w', encoding='utf-8', newline='\n').write(out)
miss = sorted(set(missing))
print(f'es/index.html generado · {len(tr)} traducciones · {len(miss)} textos sin traducir')
for m_ in miss: print('  FALTA:', m_)
