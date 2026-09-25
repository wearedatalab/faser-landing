# -*- coding: utf-8 -*-
"""Extrae los textos traducibles de index.html (inglés = fuente) → i18n/strings-en.json"""
import json, os, re
from bs4 import BeautifulSoup, NavigableString, Comment
ATTRS = ['alt', 'aria-label', 'placeholder', 'title', 'data-cap', 'data-interest', 'content']
META_OK = {'description', 'og:title', 'og:description', 'og:site_name'}

def norm(t): return re.sub(r'\s+', ' ', t).strip()

def strings(html):
    soup = BeautifulSoup(html, 'html.parser'); out = []
    for node in soup.find_all(string=True):
        if isinstance(node, Comment) or node.parent.name in ('script', 'style', 'symbol', 'svg', 'path'): continue
        t = norm(str(node))
        if t and re.search(r'[A-Za-z]', t): out.append(t)
    for tag in soup.find_all(True):
        for a in ATTRS:
            v = tag.get(a)
            if not v or not re.search(r'[A-Za-z]', v): continue
            if a == 'content' and not (tag.get('name') in META_OK or tag.get('property') in META_OK): continue
            out.append(norm(v))
        href = tag.get('href', '')
        m = re.search(r'[?&]text=([^&"]+)', href)
        if m: out.append('URLTEXT:' + m.group(1))
    seen = []; [seen.append(x) for x in out if x not in seen]
    return seen

if __name__ == '__main__':
    os.makedirs('i18n', exist_ok=True)
    s = strings(open('index.html', encoding='utf-8').read())
    json.dump(s, open('i18n/strings-en.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(len(s), 'textos')
