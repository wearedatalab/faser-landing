/* FASER GROUP — Landing (base: motion V04 de la diseñadora) */
(() => {
  const d = document, root = d.documentElement;
  const $ = (s, c = d) => c.querySelector(s);
  const $$ = (s, c = d) => [...c.querySelectorAll(s)];
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const WA = '5927433853';
  const ES = (root.lang || '').startsWith('es');
  const T = ES ? {
    name: 'Escribe tu nombre completo.', email: 'Escribe un correo válido.', phone: 'Escribe un teléfono o WhatsApp.',
    based: 'Elige dónde te encuentras.', interest: 'Elige qué te interesa.', message: 'Escribe un mensaje corto.',
    consent: 'Confirma que podemos usar tus datos para responderte.',
    hi: 'Hola FASER GROUP, soy', interestL: 'Me interesa', basedL: 'Ubicación', emailL: 'Correo', phoneL: 'Teléfono/WhatsApp', prefL: 'Prefiero que me contacten por',
    ok: 'Gracias por escribir a FASER GROUP. Nuestro equipo te responderá en un día hábil. Si WhatsApp no se abrió, ', okLink: 'envíalo por correo', subject: 'Consulta desde el sitio web — '
  } : {
    name: 'Please enter your full name.', email: 'Please enter a valid email.', phone: 'Please enter a phone or WhatsApp number.',
    based: 'Please choose where you are based.', interest: 'Please choose what you are interested in.', message: 'Please write a short message.',
    consent: 'Please confirm we may use your details to reply.',
    hi: "Hi FASER GROUP, I'm", interestL: 'Interested in', basedL: 'Based in', emailL: 'Email', phoneL: 'Phone/WhatsApp', prefL: 'Best way to reach me',
    ok: 'Thanks for writing to FASER GROUP. Our team will reply within one business day. If WhatsApp did not open, ', okLink: 'send it by email', subject: 'Website inquiry — '
  };
  root.classList.remove('no-js');

  /* Entrada del hero */
  requestAnimationFrame(() => d.body.classList.add('ready'));

  /* Header con sombra al hacer scroll + parallax suave del fondo del hero */
  const header = $('.header'), bg = $('.hero__background');
  const onScroll = () => {
    const y = scrollY;
    header.classList.toggle('scrolled', y > 8);
    if (bg && !reduce && y < innerHeight) bg.style.translate = `0 ${y * 0.075}px`;
  };
  let rnUpdate = null, ticking = false;
  addEventListener('scroll', () => { if (ticking) return; ticking = true; requestAnimationFrame(() => { rnUpdate && rnUpdate(); onScroll(); ticking = false; }); }, { passive: true }); onScroll();

  /* Desplegables del menú: hover en escritorio, clic/teclado en el chevron */
  const items = $$('.nav__item');
  const closeAll = (except) => items.forEach(it => { if (it !== except) { it.classList.remove('open'); $('.nav__toggle', it).setAttribute('aria-expanded', 'false'); } });
  items.forEach(it => {
    const btn = $('.nav__toggle', it);
    const set = (open) => { it.classList.toggle('open', open); btn.setAttribute('aria-expanded', String(open)); };
    btn.addEventListener('click', () => { const open = !it.classList.contains('open'); closeAll(it); set(open); if (open) $('.dropdown a', it).focus(); });
    it.addEventListener('mouseenter', () => { if (matchMedia('(hover:hover)').matches) { closeAll(it); set(true); } });
    it.addEventListener('mouseleave', () => { if (matchMedia('(hover:hover)').matches) set(false); });
    it.addEventListener('focusout', (e) => { if (!it.contains(e.relatedTarget)) set(false); });
    $$('.dropdown a', it).forEach(a => a.addEventListener('click', () => set(false)));
  });
  d.addEventListener('keydown', (e) => { if (e.key === 'Escape') { const open = items.find(i => i.classList.contains('open')); if (open) { closeAll(); $('.nav__toggle', open).focus(); } } });
  d.addEventListener('click', (e) => { if (!e.target.closest('.nav__item')) closeAll(); });

  /* Resaltar el enlace del menú según la sección visible */
  const spy = $$('[data-spy]');
  const sections = spy.map(a => d.getElementById(a.dataset.spy)).filter(Boolean);
  const extra = { why: 'what-we-do', contact: 'backing' };
  const setActive = (id) => spy.forEach(a => { const on = a.dataset.spy === id; a.classList.toggle('active', on); on ? a.setAttribute('aria-current', 'true') : a.removeAttribute('aria-current'); });
  const sio = new IntersectionObserver((es) => es.forEach(e => { if (e.isIntersecting) setActive(extra[e.target.id] || e.target.id); }), { rootMargin: '-45% 0px -50% 0px' });
  [...sections, d.getElementById('why'), d.getElementById('contact')].filter(Boolean).forEach(s => sio.observe(s));
  const heroObs = new IntersectionObserver((es) => { if (es[0].isIntersecting) setActive(null); }, { rootMargin: '-45% 0px -50% 0px' });
  heroObs.observe($('.hero'));

  /* Menú móvil (diálogo con foco atrapado) */
  const burger = $('.hamburger'), menu = $('#menu'), closeBtn = $('.menu__close');
  const setMenu = (open) => {
    burger.setAttribute('aria-expanded', String(open));
    d.body.style.overflow = open ? 'hidden' : '';
    if (open) { menu.hidden = false; requestAnimationFrame(() => menu.classList.add('open')); closeBtn.focus(); }
    else { menu.classList.remove('open'); setTimeout(() => { if (!menu.classList.contains('open')) menu.hidden = true; }, 350); burger.focus({ preventScroll: true }); }
  };
  burger.addEventListener('click', () => setMenu(true));
  closeBtn.addEventListener('click', () => setMenu(false));
  $$('a', menu).forEach(a => a.addEventListener('click', () => setMenu(false)));
  menu.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') setMenu(false);
    if (e.key === 'Tab') {
      const f = $$('button, a', menu), i = f.indexOf(d.activeElement);
      if (e.shiftKey && i <= 0) { e.preventDefault(); f[f.length - 1].focus(); }
      else if (!e.shiftKey && i === f.length - 1) { e.preventDefault(); f[0].focus(); }
    }
  });

  /* Revelado al hacer scroll + contadores */
  const fmt = (n) => { const s = Math.round(n).toLocaleString('en-US'); return ES ? s.replace(/,/g, '.') : s; };
  const count = (el) => {
    const to = +el.dataset.count, suf = el.dataset.suffix || '';
    if (reduce) { el.textContent = fmt(to) + suf; return; }
    const t0 = performance.now(), dur = 1500;
    const tick = (t) => { const p = Math.min(1, (t - t0) / dur); el.textContent = fmt(to * (1 - Math.pow(1 - p, 4))) + suf; if (p < 1) requestAnimationFrame(tick); };
    requestAnimationFrame(tick);
  };
  const rio = new IntersectionObserver((es) => es.forEach(e => {
    if (!e.isIntersecting) return;
    e.target.classList.add('in-view');
    $$('[data-count]', e.target).forEach(c => { if (!c.dataset.done) { c.dataset.done = 1; count(c); } });
    rio.unobserve(e.target);
  }), { threshold: .16 });
  $$('.scroll-reveal').forEach(el => rio.observe(el));

  /* Fondo de Our backing: se descarga al acercarse */
  const backing = $('.backing');
  if (backing) new IntersectionObserver((es, o) => { if (es[0].isIntersecting) { backing.classList.add('is-near'); o.disconnect(); } }, { rootMargin: '800px 0px' }).observe(backing);

  /* Galería de Duke Tower con visor */
  const lb = $('.lightbox'), items_lb = $$('[data-lb]');
  if (lb && items_lb.length) {
    const img = $('img', lb), cap = $('figcaption', lb); let k = 0, list = items_lb;
    // cada galería (Duke, Lotus, hotel) se recorre por separado
    const show = (n) => { k = (n + list.length) % list.length; img.src = list[k].dataset.lb; img.alt = $('img', list[k]).alt; cap.textContent = `${list[k].dataset.cap} · ${k + 1} / ${list.length}`; };
    items_lb.forEach((b) => b.addEventListener('click', () => { list = $$('[data-lb]', b.closest('.gallery-grid')); show(list.indexOf(b)); lb.showModal(); d.body.style.overflow = 'hidden'; }));
    // Deslizar con el dedo entre fotos
    let x0 = null, y0 = 0;
    lb.addEventListener('touchstart', (e) => { x0 = e.touches[0].clientX; y0 = e.touches[0].clientY; }, { passive: true });
    lb.addEventListener('touchend', (e) => {
      if (x0 === null) return;
      const dx = e.changedTouches[0].clientX - x0, dy = e.changedTouches[0].clientY - y0;
      if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy)) show(k + (dx < 0 ? 1 : -1));
      x0 = null;
    }, { passive: true });
    $('.lightbox__prev', lb).addEventListener('click', () => show(k - 1));
    $('.lightbox__next', lb).addEventListener('click', () => show(k + 1));
    $('.lightbox__close', lb).addEventListener('click', () => lb.close());
    lb.addEventListener('click', (e) => { if (e.target === lb || e.target.tagName === 'FIGURE') lb.close(); });
    lb.addEventListener('keydown', (e) => { if (e.key === 'ArrowLeft') show(k - 1); if (e.key === 'ArrowRight') show(k + 1); });
    lb.addEventListener('close', () => { d.body.style.overflow = ''; list[k].focus({ preventScroll: true }); });
  }

  /* Control de lectura: anillo de progreso + volver arriba (oculto sobre el hero y el footer) */
  const rn = $('.reading-nav'), circle = $('.reading-nav__progress'), topBtn = $('.reading-nav__top');
  if (rn && circle) {
    const c = 2 * Math.PI * 23; circle.style.strokeDasharray = c;
    const footer = $('.footer');
    const update = () => {
      const max = root.scrollHeight - innerHeight, p = max > 0 ? Math.min(1, Math.max(0, scrollY / max)) : 0;
      circle.style.strokeDashoffset = c * (1 - p);
      const nearFooter = footer.getBoundingClientRect().top < innerHeight - 40;
      rn.classList.toggle('is-hidden', scrollY < innerHeight * 0.6 || nearFooter);
    };
    rnUpdate = update; update(); addEventListener('resize', update, { passive: true });
    topBtn.addEventListener('click', () => { scrollTo({ top: 0, behavior: reduce ? 'auto' : 'smooth' }); $('.logo').focus({ preventScroll: true }); });
  }

  /* CTAs que preseleccionan el interés en el formulario */
  $$('[data-interest]').forEach(a => a.addEventListener('click', () => { const s = $('#interest'); if (s) s.value = a.dataset.interest; }));

  /* Formulario: validación + envío por WhatsApp (sitio estático, sin backend todavía) */
  const form = $('#contact-form');
  if (form) {
    const msgs = T;
    const valid = (f) => f.type === 'checkbox' ? f.checked : f.type === 'email' ? /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(f.value.trim()) : f.id === 'phone' ? f.value.replace(/\D/g, '').length >= 7 : f.value.trim().length > 1;
    const check = (f) => { const ok = valid(f); f.setAttribute('aria-invalid', String(!ok)); const er = $('#' + f.id + '-err'); if (er) er.textContent = ok ? '' : msgs[f.id]; return ok; };
    $$('[required]', form).forEach(f => f.addEventListener(f.tagName === 'SELECT' || f.type === 'checkbox' ? 'change' : 'blur', () => { if (f.getAttribute('aria-invalid')) check(f); }));
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      if ($('#website').value) return; // honeypot
      const bad = $$('[required]', form).filter(f => !check(f));
      if (bad.length) { bad[0].focus(); return; }
      const v = (id) => $('#' + id).value.trim();
      const pref = $('input[name="contact_pref"]:checked', form).value;
      const text = `${T.hi} ${v('name')}${v('company') ? ' (' + v('company') + ')' : ''}.\n${T.interestL}: ${v('interest')}\n${T.basedL}: ${v('based')}\n${T.emailL}: ${v('email')}\n${T.phoneL}: ${v('phone')}\n${T.prefL}: ${pref}\n\n${v('message')}`;
      const ok = $('.form__ok', form);
      $('p', ok).innerHTML = `${T.ok}<a href="mailto:info@fasergroup.com?subject=${encodeURIComponent(T.subject + v('interest'))}&body=${encodeURIComponent(text)}">${T.okLink}</a>.`;
      ok.hidden = false;
      window.open(`https://wa.me/${WA}?text=${encodeURIComponent(text)}`, '_blank', 'noopener');
      ok.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'nearest' });
    });
  }

  /* La barra fija de contacto se aparta mientras se escribe (con el teclado abierto taparía el campo) */
  const bar = $('.contact-bar');
  if (bar && form) {
    const typing = (el) => el && el.matches('input:not([type=radio]):not([type=checkbox]), select, textarea');
    form.addEventListener('focusin', (e) => { if (typing(e.target)) bar.classList.add('is-away'); });
    form.addEventListener('focusout', (e) => { if (!typing(e.relatedTarget)) bar.classList.remove('is-away'); });
  }

  $$('[data-year]').forEach(y => y.textContent = new Date().getFullYear());
})();
