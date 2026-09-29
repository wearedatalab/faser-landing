# -*- coding: utf-8 -*-
"""Genera las páginas en español a partir de las inglesas (fuente que edita la diseñadora)
y del diccionario i18n/es.json ({"texto en inglés": "texto en español"}).

    index.html      → es/index.html
    thank-you.html  → es/gracias.html

Uso:  python _build_es.py
Si cambias textos en inglés:  python _i18n_extract.py  → traduce los nuevos en i18n/es.json → python _build_es.py
El script avisa qué textos quedaron sin traducir.
"""
import json, os, re, sys
from bs4 import BeautifulSoup, Comment, Doctype
from _i18n_extract import ATTRS, META_OK, norm

SITE = 'https://wearedatalab.github.io/faser-landing/'
sys.stdout.reconfigure(encoding='utf-8')
tr = json.load(open('i18n/es.json', encoding='utf-8'))
missing = []

# (fuente inglesa, destino español, enlace EN desde /es/, enlace ES desde /es/, canónica)
PAGES = [
    ('index.html', 'es/index.html', '../', './', SITE + 'es/'),
    ('thank-you.html', 'es/gracias.html', '../thank-you.html', './gracias.html', SITE + 'es/gracias.html'),
]


def t(text):
    k = norm(text)
    if k in tr: return tr[k]
    missing.append(k); return text


def rel(u):
    # La página vive en /es/: los recursos suben un nivel. './…' apunta a la landing del mismo idioma y se deja igual.
    if not u or u.startswith(('#', 'http', 'mailto:', 'tel:', 'data:', '/', '../', './')): return u
    return '../' + u


def build(src, dst, en_href, es_href, canonical):
    soup = BeautifulSoup(open(src, encoding='utf-8').read(), 'html.parser')

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

    # 3) rutas relativas
    for tag in soup.find_all(True):
        for a in ('src', 'href', 'data-lb', 'action'):
            if tag.get(a) is not None and not (tag.name == 'a' and 'lang' in (tag.parent.get('class') or [])):
                tag[a] = rel(tag[a])
        for a in ('srcset', 'imagesrcset'):
            if tag.get(a):
                tag[a] = ', '.join(' '.join([rel(p.split()[0])] + p.split()[1:]) for p in tag[a].split(','))

    # 4) selector de idioma
    for nav in soup.select('nav.lang'):
        en, es = nav.find_all('a')[:2]
        en['href'] = en_href; es['href'] = es_href
        if en.has_attr('aria-current'): del en['aria-current']
        es['aria-current'] = 'true'

    # 5) cabecera: idioma, canónica, OG, datos estructurados
    soup.html['lang'] = 'es'
    soup.find('link', rel='canonical')['href'] = canonical
    og = soup.find('meta', property='og:url')
    if og: og['content'] = canonical
    ogt = soup.find('meta', property='og:type')
    if ogt: ogt.insert_after(soup.new_tag('meta', property='og:locale', content='es_CO'))
    ld = soup.find('script', type='application/ld+json')
    if ld:
        data = json.loads(ld.string); data['description'] = t(data['description']); data['url'] = canonical
        ld.string = json.dumps(data, ensure_ascii=False)

    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, 'w', encoding='utf-8', newline='\n').write(str(soup))


for page in PAGES:
    if os.path.exists(page[0]): build(*page)
miss = sorted(set(missing))
print(f'{", ".join(p[1] for p in PAGES)} generados · {len(tr)} traducciones · {len(miss)} textos sin traducir')
for m_ in miss: print('  FALTA:', m_)
