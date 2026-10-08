    // Mobile menu
    const header = document.querySelector('.site-header');
    const toggle = document.querySelector('.menu-toggle');
    const nav = document.getElementById('main-nav');
    const setMenu = (open) => {
      nav.classList.toggle('open', open);
      toggle.setAttribute('aria-expanded', open);
      toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    };
    toggle.addEventListener('click', () => setMenu(!nav.classList.contains('open')));
    nav.querySelectorAll('a').forEach(link => link.addEventListener('click', () => setMenu(false)));

    // Header border once the page is scrolled
    const onScroll = () => header.classList.toggle('scrolled', window.scrollY > 8);
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();

    // Footer year
    document.getElementById('year').textContent = new Date().getFullYear();

    // Print buttons on the advice page
    document.querySelectorAll('[data-print]').forEach(btn => btn.addEventListener('click', () => window.print()));

    // Step-by-step claim form (contact page). Sends through FormSubmit; falls back to the visitor's email app.
    const form = document.getElementById('claim-form');
    if (form) {
      const EMAIL = form.dataset.email;
      const panels = [...form.querySelectorAll('.panel')];
      const progress = [...form.querySelectorAll('.wizard-progress li')];

      const show = (n, focus = true) => {
        panels.forEach((p, k) => p.classList.toggle('current', k === n));
        progress.forEach((li, k) => {
          li.classList.toggle('active', k === n);
          li.classList.toggle('done', k < n);
        });
        if (n === 2) fillSummary();
        if (!focus) return;
        const heading = panels[n].querySelector('h2');
        if (heading) heading.focus({ preventScroll: true });
        const top = form.getBoundingClientRect().top;
        if (top < 0) window.scrollTo({ top: window.scrollY + top - 100, behavior: 'smooth' });
      };

      const validate = (panel) => {
        let firstBad = null;
        panel.querySelectorAll('.field').forEach(field => {
          const inputs = [...field.querySelectorAll('input, select, textarea')];
          const ok = inputs.every(input => input.checkValidity());
          field.classList.toggle('invalid', !ok);
          if (!ok && !firstBad) firstBad = inputs[0];
        });
        if (firstBad) firstBad.focus();
        return !firstBad;
      };

      const value = (name) => {
        const el = form.elements[name];
        if (!el) return '';
        return (el.value || '').trim();
      };

      const rows = () => [
        ['I am a', value('who')],
        ['Claim for', value('claim')],
        ['Date of incident', value('date')],
        ['Property postcode', value('postcode')],
        ['Loss adjuster appointed?', value('adjuster')],
        ['What happened', value('details')],
        ['Name', value('name')],
        ['Phone', value('phone')],
        ['Email', value('email')],
        ['Best time to call', value('time')],
      ].filter(([, v]) => v);

      const fillSummary = () => {
        const dl = document.getElementById('summary');
        dl.innerHTML = '';
        rows().forEach(([k, v]) => {
          const row = document.createElement('div');
          const dt = document.createElement('dt');
          const dd = document.createElement('dd');
          dt.textContent = k;
          dd.textContent = v.length > 80 ? v.slice(0, 80) + '…' : v;
          row.append(dt, dd);
          dl.append(row);
        });
      };

      form.querySelectorAll('[data-next]').forEach(btn => btn.addEventListener('click', () => {
        const n = panels.findIndex(p => p.classList.contains('current'));
        if (validate(panels[n])) show(n + 1);
      }));
      form.querySelectorAll('[data-back]').forEach(btn => btn.addEventListener('click', () => {
        const n = panels.findIndex(p => p.classList.contains('current'));
        show(n - 1);
      }));
      form.addEventListener('input', (e) => {
        const field = e.target.closest('.field');
        if (field) field.classList.remove('invalid');
      });

      form.addEventListener('submit', (e) => {
        e.preventDefault();
        for (let n = 0; n < 2; n++) {
          if (!validate(panels[n])) { show(n); return; }
        }
        const subject = `Claim enquiry: ${value('claim')} (${value('who')})`;
        const done = () => {
          panels.forEach(p => p.classList.remove('current'));
          const sent = document.getElementById('sent');
          sent.classList.add('current');
          form.querySelector('.wizard-progress').hidden = true;
          sent.querySelector('h2').focus({ preventScroll: true });
        };
        if (value('_honey')) { done(); return; }
        const btn = form.querySelector('[data-send]');
        const label = btn.innerHTML;
        btn.disabled = true;
        btn.textContent = 'Sending…';
        const data = Object.fromEntries(rows());
        Object.assign(data, { _subject: subject, _cc: form.dataset.cc, _replyto: value('email'), _template: 'table', _captcha: 'false' });
        fetch(form.action.replace('formsubmit.co/', 'formsubmit.co/ajax/'), {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
          body: JSON.stringify(data),
        })
          .then(r => r.json().then(j => { if (!r.ok || String(j.success) !== 'true') throw new Error(j.message || 'Send failed'); }))
          .then(done)
          .catch(() => {
            btn.disabled = false;
            btn.innerHTML = label;
            document.getElementById('send-error').hidden = false;
            const body = rows().map(([k, v]) => `${k}: ${v}`).join('\n');
            window.location.href = `mailto:${EMAIL}?cc=${encodeURIComponent(form.dataset.cc)}&subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
          });
      });

      // Pre-fill answers passed from the homepage quick-start form
      const params = new URLSearchParams(window.location.search);
      const who = params.get('who');
      if (who) {
        const radio = [...form.querySelectorAll('input[name="who"]')].find(r => r.value === who);
        if (radio) radio.checked = true;
      }
      const claim = params.get('claim');
      if (claim && [...form.elements.claim.options].some(o => o.value === claim)) form.elements.claim.value = claim;

      if (params.get('sent')) {
        panels.forEach(p => p.classList.remove('current'));
        document.getElementById('sent').classList.add('current');
        form.querySelector('.wizard-progress').hidden = true;
      } else {
        show(0, false);
      }
    }

    // Gentle fade-in as sections scroll into view
    const motionOK = !window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if ('IntersectionObserver' in window) {
      const targets = document.querySelectorAll(
        'main .section-head, main .card, main a.tile, main .step, main .checklist li, main .faq, main .compare-table, ' +
        'main .trust li, main .mini, main .cta, main .quote, main .stats li, main .glossary div, main .creds li, main .side-card'
      );
      const io = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (!entry.isIntersecting) return;
          const el = entry.target;
          el.classList.add('in');
          io.unobserve(el);
          // Hand control back to the element's own hover effects once it has appeared
          const done = () => { el.classList.remove('reveal', 'in'); el.style.transitionDelay = ''; };
          el.addEventListener('transitionend', done, { once: true });
          setTimeout(done, 1600);
        });
      }, { rootMargin: '0px 0px -8% 0px' });
      targets.forEach(el => {
        const siblings = [...el.parentElement.children].filter(c => c.matches(el.tagName));
        const i = Math.min(siblings.indexOf(el), 5);
        el.style.transitionDelay = (i > 0 ? i * 80 : 0) + 'ms';
        el.classList.add('reveal');
        io.observe(el);
      });

      // Count-up numbers in the stats band
      const counters = document.querySelectorAll('[data-count]');
      const countIO = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (!entry.isIntersecting) return;
          const el = entry.target;
          countIO.unobserve(el);
          const end = +el.dataset.count;
          if (!motionOK) { el.textContent = end; return; }
          const start = performance.now();
          const tick = (now) => {
            const t = Math.min((now - start) / 1400, 1);
            el.textContent = Math.round(end * (1 - Math.pow(1 - t, 3)));
            if (t < 1) requestAnimationFrame(tick);
          };
          requestAnimationFrame(tick);
        });
      }, { threshold: 0.6 });
      counters.forEach(el => countIO.observe(el));
    }

    // Homepage background video: only on larger screens, and not for reduced motion or data saver
    const heroVideo = document.querySelector('.hero-bg[data-src]');
    if (heroVideo) {
      const big = window.matchMedia('(min-width: 769px)').matches;
      const saveData = navigator.connection && navigator.connection.saveData;
      if (big && motionOK && !saveData) {
        [['webm', 'video/webm'], ['mp4', 'video/mp4']].forEach(([ext, type]) => {
          const source = document.createElement('source');
          source.src = `${heroVideo.dataset.src}.${ext}`;
          source.type = type;
          heroVideo.append(source);
        });
        heroVideo.load();
        heroVideo.play().catch(() => {});
      }
    }

    // Claims drop-down menu
    document.querySelectorAll('.has-sub').forEach(item => {
      const btn = item.querySelector('.sub-toggle');
      const set = (open) => { item.classList.toggle('open', open); btn.setAttribute('aria-expanded', open); };
      btn.addEventListener('click', (e) => { e.stopPropagation(); set(!item.classList.contains('open')); });
      document.addEventListener('click', (e) => { if (!item.contains(e.target)) set(false); });
      item.addEventListener('keydown', (e) => { if (e.key === 'Escape') { set(false); btn.focus(); } });
    });
