# -*- coding: utf-8 -*-
"""Genera thank-you.html (inglés) reutilizando cabecera, menú y footer de index.html.
El español (es/gracias.html) lo genera _build_es.py con el mismo diccionario.

Uso:  python _build_thanks.py   (después: python _i18n_extract.py y python _build_es.py)
"""
import re, sys
from bs4 import BeautifulSoup
sys.stdout.reconfigure(encoding='utf-8')
SITE = 'https://wearedatalab.github.io/faser-landing/'

MAIN = '''<main id="main">
<section class="thanks" aria-labelledby="thanks-title">
  <div class="thanks__inner">
    <div class="thanks__copy">
      <div class="done-mark" aria-hidden="true"><svg viewBox="0 0 88 88"><circle class="dm-track" cx="44" cy="44" r="38"></circle><circle class="dm-ring" cx="44" cy="44" r="38"></circle><path class="dm-check" d="M29 45l10 10 21-22"></path></svg></div>
      <p class="kicker">MESSAGE SENT</p>
      <h1 id="thanks-title" data-thanks-name>THANK YOU.</h1>
      <p class="lead">Your message is already with the FASER GROUP team. We will reply within one business day, through the channel you chose.</p>
      <div class="duke-actions duke-actions--left">
        <a class="project-btn project-btn--dark" href="./#projects"><span>BACK TO THE PROJECTS</span><i aria-hidden="true"></i></a>
        <a class="duke-site" href="https://www.duketower.gy/" target="_blank" rel="noopener"><span>VISIT DUKETOWER.GY</span><b aria-hidden="true">›</b></a>
      </div>
    </div>
    <figure class="thanks__visual"><img src="img/duke-tower-600.webp" srcset="img/duke-tower-600.webp 600w, img/duke-tower.webp 900w" sizes="(max-width: 760px) 260px, 420px" alt="Rendering of Duke Tower, Kingston, Georgetown" width="600" height="874" fetchpriority="high"></figure>
  </div>
</section>

<section class="next" aria-labelledby="next-title">
  <div class="next__inner">
    <p class="what__eyebrow" id="next-title">WHAT HAPPENS NEXT</p>
    <ol class="next__steps">
      <li><span class="fact__line" aria-hidden="true"></span><b>01</b><h3>WE RECEIVE YOUR MESSAGE</h3><p>It is already in the FASER GROUP inbox, with the project or service you are interested in.</p></li>
      <li><span class="fact__line" aria-hidden="true"></span><b>02</b><h3>WE REPLY WITHIN ONE BUSINESS DAY</h3><p>By WhatsApp, phone call or e-mail, the way you chose in the form.</p></li>
      <li><span class="fact__line" aria-hidden="true"></span><b>03</b><h3>BUYING FROM OVERSEAS?</h3><p>We can walk you through each project by video call in your time zone and share every document digitally.</p></li>
    </ol>
    <div class="next__wa">
      <p>Need an answer sooner?</p>
      <a class="duke-talk" href="https://wa.me/5927433853?text=Hi%20FASER%20GROUP%2C%20I%20just%20sent%20you%20a%20message%20from%20your%20website." target="_blank" rel="noopener"><svg aria-hidden="true"><use href="#i-wa"/></svg><span>TALK TO OUR TEAM ON WHATSAPP</span></a>
    </div>
  </div>
</section>
</main>'''

soup = BeautifulSoup(open('index.html', encoding='utf-8').read(), 'html.parser')

# cabeza: título, descripción, sin indexar, canónica propia, sin precargas del hero ni datos estructurados
soup.title.string = 'Thank you | FASER GROUP'
soup.find('meta', attrs={'name': 'description'})['content'] = 'Your message was sent to FASER GROUP. Our team will reply within one business day.'
for tag in soup.find_all('link', rel='preload'): tag.decompose()
for tag in soup.find_all('link', rel='alternate'): tag.decompose()
for tag in soup.find_all('script', type='application/ld+json'): tag.decompose()
for tag in soup.find_all('meta', property=re.compile('^og:|^twitter:')): tag.decompose()
for tag in soup.find_all('meta', attrs={'name': 'twitter:card'}): tag.decompose()
soup.find('link', rel='canonical')['href'] = SITE + 'thank-you.html'
robots = soup.new_tag('meta', attrs={'name': 'robots', 'content': 'noindex, follow'}); soup.find('meta', attrs={'name': 'description'}).insert_after(robots)
soup.find('link', rel='canonical').insert_after(BeautifulSoup(
    f'<link rel="alternate" hreflang="en" href="{SITE}thank-you.html"><link rel="alternate" hreflang="es" href="{SITE}es/gracias.html">', 'html.parser'))

# cuerpo: se reemplaza el contenido; los enlaces internos vuelven a la landing
soup.find('main').replace_with(BeautifulSoup(MAIN, 'html.parser'))
for sel in ['.contact-bar', '.reading-nav', 'dialog.lightbox']:
    el = soup.select_one(sel)
    if el: el.decompose()
for a in soup.select('header a[href^="#"], #menu a[href^="#"], footer a[href^="#"]'):
    a['href'] = './' + a['href'] if a['href'] != '#top' else './'
for a in soup.select('.contact-btn'): a['href'] = './#contact'
for nav in soup.select('nav.lang'):
    en, es = nav.find_all('a')[:2]
    en['href'] = 'thank-you.html'; es['href'] = 'es/gracias.html'

open('thank-you.html', 'w', encoding='utf-8', newline='\n').write(str(soup))
print('thank-you.html generado')
