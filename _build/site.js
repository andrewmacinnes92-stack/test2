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

    // Step-by-step claim form (contact page). Sends by opening the visitor's email app.
    const form = document.getElementById('claim-form');
    if (form) {
      const EMAIL = 'nic@independentclaimsconsultants.co.uk';
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
        const body = rows().map(([k, v]) => `${k}: ${v}`).join('\n');
        window.location.href = `mailto:${EMAIL}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
        panels.forEach(p => p.classList.remove('current'));
        document.getElementById('sent').classList.add('current');
        form.querySelector('.wizard-progress').hidden = true;
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

      show(0, false);
    }
