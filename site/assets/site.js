// Ozi Realty site behaviour: mobile drawer, reveal-on-scroll, gallery lightbox, enquiry forms.
(function () {
  var d = document, drawer = d.getElementById('drawer');
  d.addEventListener('click', function (e) {
    if (e.target.closest('[data-open]')) { drawer.classList.add('open'); d.body.style.overflow = 'hidden'; }
    if (e.target.closest('[data-close]') || (e.target.closest('#drawer a'))) { drawer.classList.remove('open'); d.body.style.overflow = ''; }
    var lb = e.target.closest('[data-lb]');
    if (lb) { e.preventDefault(); var box = d.getElementById('lightbox'); box.querySelector('img').src = lb.getAttribute('href'); box.classList.add('open'); }
    if (e.target.id === 'lightbox' || e.target.closest('#lightbox img')) d.getElementById('lightbox').classList.remove('open');
  });
  d.addEventListener('keydown', function (e) { if (e.key === 'Escape') { drawer.classList.remove('open'); d.body.style.overflow = ''; d.getElementById('lightbox').classList.remove('open'); } });

  var els = d.querySelectorAll('.rv');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) { es.forEach(function (x) { if (x.isIntersecting) { x.target.classList.add('in'); io.unobserve(x.target); } }); }, { rootMargin: '0px 0px -8% 0px' });
    els.forEach(function (el) { io.observe(el); });
  } else els.forEach(function (el) { el.classList.add('in'); });

  // Enquiry forms: validate, then submit to Wix Forms (headless visitor token).
  // If Wix can't be reached, fall back to the visitor's email app, addressed to
  // the matching Ozi Realty department.
  var CLIENT_ID = 'e800a350-9914-4f5f-867e-a9768e97267c', API = 'https://www.wixapis.com';
  var tokenP = null;
  function visitorToken() {
    if (!tokenP) tokenP = fetch(API + '/oauth2/token', { method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ clientId: CLIENT_ID, grantType: 'anonymous' }) })
      .then(function (r) { if (!r.ok) throw new Error('token ' + r.status); return r.json(); })
      .then(function (j) { return j.access_token; })
      .catch(function (e) { tokenP = null; throw e; });
    return tokenP;
  }
  function collect(f) {
    var values = {}, lines = [], seen = {};
    f.querySelectorAll('input,textarea,select').forEach(function (el) {
      if (!el.name || seen[el.name]) return;
      var lab = el.closest('fieldset') ? el.closest('fieldset').querySelector('legend') : f.querySelector('label[for="' + el.id + '"]');
      var name = lab ? lab.textContent.replace('*', '').trim() : el.name, v;
      if (el.type === 'checkbox') { seen[el.name] = 1; v = Array.prototype.map.call(f.querySelectorAll('input[name="' + el.name + '"]:checked'), function (x) { return x.value; }); if (v.length) { values[el.name] = v; lines.push(name + ': ' + v.join(', ')); } return; }
      if (el.type === 'radio') { seen[el.name] = 1; var c = f.querySelector('input[name="' + el.name + '"]:checked'); v = c ? c.value : ''; }
      else v = el.value.trim();
      if (v) { values[el.name] = v; lines.push(name + ': ' + v); }
    });
    return { values: values, lines: lines };
  }
  d.querySelectorAll('form[data-form]').forEach(function (f) {
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      var bad = null;
      f.querySelectorAll('[required]').forEach(function (el) {
        var ok = el.type === 'radio' ? !!f.querySelector('input[name="' + el.name + '"]:checked') : el.value.trim() !== '';
        if (el.type === 'email' && ok) ok = /.+@.+\..+/.test(el.value);
        var box = el.closest('.fld'); if (box) { box.style.outline = ok ? '' : '2px solid #DF3131'; box.style.borderRadius = '12px'; }
        if (!ok && !bad) bad = el;
      });
      f.querySelectorAll('fieldset[data-required]').forEach(function (fs) {
        var ok = !!fs.querySelector('input:checked'); var box = fs.closest('.fld');
        if (box) { box.style.outline = ok ? '' : '2px solid #DF3131'; box.style.borderRadius = '12px'; }
        if (!ok && !bad) bad = fs.querySelector('input');
      });
      if (bad) { bad.focus(); return; }
      var data = collect(f), btn = f.querySelector('button[type=submit]'), ok = f.querySelector('.form-ok');
      var formId = f.getAttribute('data-form-id');
      function done(msg) { if (ok) { ok.textContent = msg; ok.style.display = 'block'; } if (btn) { btn.disabled = false; btn.style.opacity = ''; } }
      function mailFallback() {
        var title = (f.querySelector('h3') || d.querySelector('h1') || {}).textContent || 'Website enquiry';
        location.href = 'mailto:' + f.getAttribute('data-to') + '?subject=' + encodeURIComponent('Website enquiry: ' + title.trim()) + '&body=' + encodeURIComponent(data.lines.join('\n') + '\n\nSent from ' + location.href);
        done('Your email app has opened with your enquiry to ' + f.getAttribute('data-to') + '. Press send and our team will be in touch. Prefer to talk? Call 1800 400 333.');
      }
      if (!formId) return mailFallback();
      if (btn) { btn.disabled = true; btn.style.opacity = '.7'; }
      visitorToken().then(function (tok) {
        return fetch(API + '/form-submission-service/v4/submissions', { method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Authorization': tok },
          body: JSON.stringify({ submission: { formId: formId, submissions: data.values } }) });
      }).then(function (r) {
        if (!r.ok) throw new Error('submit ' + r.status);
        f.querySelectorAll('.form-grid, button[type=submit]').forEach(function (x) { x.style.display = 'none'; });
        done('Thank you! Your details have been sent to the Ozi Realty team. We’ll be in touch shortly. Prefer to talk? Call 1800 400 333.');
      }).catch(function () { mailFallback(); });
    });
  });
})();
