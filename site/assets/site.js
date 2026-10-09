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

  // Enquiry forms: validate, then hand the enquiry to the visitor's email app,
  // addressed to the right Ozi Realty department.
  d.querySelectorAll('form[data-form]').forEach(function (f) {
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      var bad = null;
      f.querySelectorAll('[required]').forEach(function (el) {
        var ok = el.type === 'radio' ? !!f.querySelector('input[name="' + el.name + '"]:checked') : el.value.trim() !== '';
        if (el.type === 'email' && ok) ok = /.+@.+\..+/.test(el.value);
        var box = el.closest('.fld'); if (box) box.style.outline = ok ? '' : '2px solid #DF3131';
        if (box) box.style.borderRadius = '12px';
        if (!ok && !bad) bad = el;
      });
      if (bad) { bad.focus(); return; }
      var lines = [], seen = {};
      f.querySelectorAll('input,textarea,select').forEach(function (el) {
        if (seen[el.name] || !el.name) return;
        var lab = el.closest('fieldset') ? el.closest('fieldset').querySelector('legend') : f.querySelector('label[for="' + el.id + '"]');
        var name = lab ? lab.textContent.replace('*', '').trim() : el.name;
        var v;
        if (el.type === 'radio' || el.type === 'checkbox') { seen[el.name] = 1; v = Array.prototype.map.call(f.querySelectorAll('input[name="' + el.name + '"]:checked'), function (x) { return x.value; }).join(', '); }
        else v = el.value.trim();
        if (v) lines.push(name + ': ' + v);
      });
      var title = (f.querySelector('h3') || d.querySelector('h1') || {}).textContent || 'Website enquiry';
      var subject = 'Website enquiry: ' + title.trim();
      var body = lines.join('\n') + '\n\nSent from ' + location.href;
      location.href = 'mailto:' + f.getAttribute('data-to') + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
      var ok = f.querySelector('.form-ok');
      if (ok) { ok.textContent = 'Thank you! Your email app has opened with your enquiry to ' + f.getAttribute('data-to') + ' — press send and our team will be in touch. Prefer to talk? Call 1800 400 333.'; ok.style.display = 'block'; }
    });
  });
})();
