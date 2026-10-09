#!/usr/bin/env python3
"""Build the modern Ozi Realty static site from content/content.json.

content.json is produced by tools/extract.py from the live www.ozirealty.com.au
pages; this script keeps every page's URL, section order, copy and images and
renders them with the shared design system in site/assets/site.css.
Usage: python3 tools/build.py   (writes into site/)
"""
import json, os, re, html, collections, datetime, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'site')
DATA = json.load(open(os.path.join(ROOT, 'content', 'content.json')))
META = json.load(open(os.path.join(ROOT, 'content', 'posts-meta.json'))) if os.path.exists(os.path.join(ROOT, 'content', 'posts-meta.json')) else {}
DOMAIN = 'https://www.ozirealty.com.au'
LOGO = 'https://static.wixstatic.com/media/160674_f4475077d64f463b9fc5aac5b1632930~mv2.png'
REISA = 'https://static.wixstatic.com/media/668220_867dfdc826514c96a7c9e9cb65c5b1bd~mv2.png'
ESI = 'https://static.wixstatic.com/media/160674_6fd16eb1a1d64d27bdb5f43d1d0695e8~mv2.jpg'
E = lambda s: html.escape(s or '', quote=True)

# Inline-SVG icons used across the UI
ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
PHONE = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/></svg>'
MENU = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg>'
CHEV = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9l6 6 6-6"/></svg>'
SOCIAL = {
 'TikTok': ('https://www.tiktok.com/@ozirealty.au?lang=en', '<svg viewBox="0 0 24 24"><path d="M16.6 5.8A4.3 4.3 0 0 1 15.5 3h-3.1v12.4a2.6 2.6 0 1 1-1.8-2.5V9.7a5.7 5.7 0 1 0 4.9 5.7V9a7.4 7.4 0 0 0 4.3 1.4V7.3a4.3 4.3 0 0 1-3.2-1.5z"/></svg>'),
 'Facebook': ('https://www.facebook.com/profile.php?id=61584417066380', '<svg viewBox="0 0 24 24"><path d="M14 8.5V6.6c0-.8.2-1.3 1.4-1.3H17V2.2c-.3 0-1.3-.2-2.5-.2-2.5 0-4.2 1.5-4.2 4.3v2.2H7.6v3.4h2.7V22H14V11.9h2.7l.4-3.4z"/></svg>'),
 'LinkedIn': ('https://www.linkedin.com/company/ozi-realty/about/', '<svg viewBox="0 0 24 24"><path d="M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5zM3 9h4v12H3zM9 9h3.8v1.7h.1c.5-1 1.8-2 3.8-2 4 0 4.8 2.6 4.8 6V21h-4v-5.6c0-1.3 0-3-1.9-3s-2.1 1.4-2.1 2.9V21H9z"/></svg>'),
}

def img(u, w=1400, h=None, fit='fill'):
    """Wix media transform URL (keeps original image, serves a sized copy)."""
    if not u or 'static.wixstatic.com/media/' not in u: return u or ''
    mid = u.split('/media/')[1].split('/')[0]
    ext = 'png' if mid.lower().endswith('.png') else 'jpg'
    if h: return f'https://static.wixstatic.com/media/{mid}/v1/fill/w_{w},h_{h},al_c,q_80,enc_auto/img.{ext}'
    return f'https://static.wixstatic.com/media/{mid}/v1/fit/w_{w},h_{w},q_82,enc_auto/img.{ext}'

def link(h):
    if not h: return '#'
    if h.startswith(DOMAIN):
        h = h[len(DOMAIN):] or '/'
        if h.startswith('/blog/page/'): return '/blog/'
        if '#' in h:
            p, a = h.split('#', 1)
            return (p.rstrip('/') + '/#' + a) if p else '#' + a
        return h.rstrip('/') + '/' if h != '/' else '/'
    return h

def ext(h): return h.startswith('http') and not h.startswith(DOMAIN)

# ---------------------------------------------------------------- nav / chrome
NAV = [
 ('Home', '/', None),
 ('Services', '/property-services/', [
    ('Manage My Property — from 2.99%', '/manage-property-adelaide/'),
    ('Sell My Property', '/sell-property-house-adelaide/'),
    ('Rent Out My Property', '/rent-out-my-property-adelaide/'),
    ('I Need A Buyer Agent', '/buyer-agent-adelaide/'),
    ('I Want to Invest', '/property-investment/'),
    ('Looking For Land', '/land-opportunities-sa-adelaide/'),
    ('I Need To Rent', '/rent-property-house-adelaide/'),
    ('Sell My Business', '/sell-my-business-australia/'),
    ('Properties List', '/properties/'),
    ('All services', '/property-services/')]),
 ('Strategy Services', '/property-strategy-services/', [
    ('Free Appraisal', '/free-property-appraisal-sa/'),
    ('Free Suburb Insight Report', '/free-suburb-insight-report/'),
    ('Property Rental Report', '/property-rental-report/'),
    ('Strategy Services', '/property-strategy-services/')]),
 ('Oversea Investment', '/oversees-investment/', None),
 ('About', '/about-adelaide-land-agent/', [
    ('About Us', '/about-adelaide-land-agent/'), ('Gift Party', '/realestate-gift-adelaide/'),
    ('FAQ', '/adelaide-property-faq/'), ('Blog', '/blog/')]),
 ('Free Meeting', '/book-online/', None),
 ('Contact Us', '/contact-adelaide-realestae-agency/', None),
]
QUICK = [('Home','/'),('Services','/property-services/'),('Strategy Services','/property-strategy-services/'),('Oversea Investment','/oversees-investment/'),('Free Appraisal','/free-property-appraisal-sa/'),('About','/about-adelaide-land-agent/'),('Contact Us','/contact-adelaide-realestae-agency/'),('Free Meeting','/book-online/'),('Gift Party','/realestate-gift-adelaide/'),('Blog','/blog/'),('FAQ','/adelaide-property-faq/'),('Properties','/properties/'),('Search','/search/')]

def header(path):
    li = []
    for name, href, sub in NAV:
        act = ' class="active"' if href == path else ''
        if sub:
            dd = ''.join(f'<a href="{h}">{E(n)}</a>' for n, h in sub)
            li.append(f'<li><a href="{href}"{act}>{E(name)} {CHEV}</a><div class="dd">{dd}</div></li>')
        else:
            li.append(f'<li><a href="{href}"{act}>{E(name)}</a></li>')
    drawer = ''
    for name, href, sub in NAV:
        if sub: drawer += f'<h6>{E(name)}</h6>' + ''.join(f'<a href="{h}">{E(n)}</a>' for n, h in sub)
        else: drawer += f'<a href="{href}">{E(name)}</a>'
    return f'''<div class="topbar"><div class="wrap"><span class="promo"><a href="/manage-property-adelaide/">Property Management From 2.99%</a> · <a href="/free-property-appraisal-sa/">Free Appraisal</a></span><span class="tb-right"><span>Licence Number: RLA 350 628</span><a href="tel:1800400333">1800 400 333</a></span></div></div>
<header class="nav"><div class="wrap">
<a class="logo" href="/" aria-label="Ozi Realty home"><img src="{img(LOGO,460)}" alt="ozi realty logo" width="195" height="30"></a>
<ul class="menu">{''.join(li)}</ul>
<div class="nav-cta"><a class="icon-btn" href="/search/" aria-label="Search this site"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg></a><a class="btn btn-primary" href="/free-property-appraisal-sa/">Free Appraisal</a><button class="burger" aria-label="Open menu" data-open>{MENU}</button></div>
</div></header>
<div class="drawer" id="drawer"><div class="scrim" data-close></div><div class="panel"><button class="close" aria-label="Close menu" data-close>&times;</button><div style="clear:both"></div>{drawer}<a class="btn btn-primary mt-m" style="width:100%" href="/free-property-appraisal-sa/">Free Appraisal</a></div></div>'''

def footer():
    soc = ''.join(f'<a href="{u}" target="_blank" rel="noopener" aria-label="{n}">{s}</a>' for n, (u, s) in SOCIAL.items())
    q = ''.join(f'<li><a href="{h}">{E(n)}</a></li>' for n, h in QUICK)
    mails = ''.join(f'<li><a href="mailto:{m}@ozirealty.com.au">{m}@ozirealty.com.au</a></li>' for m in ['support','rent','sell','buy','oversea'])
    return f'''<footer class="site"><div class="wrap"><div class="cols">
<div><a class="flogo" href="/"><img src="{img(LOGO,460)}" alt="ozi realty logo" width="170" height="26"></a>
<p>OziRealty blends real estate expertise with financial advising and finance broking, providing seamless property and investment solutions.</p>
<div class="social">{soc}</div>
<a class="reisa" href="https://reisa.com.au/" target="_blank" rel="noopener"><img src="{img(REISA,200)}" alt="reisa logo" width="52" height="40"></a></div>
<div><h6>Email / Call</h6><ul><li>Tel: <a href="tel:1800400333"><b>1800 400 333</b></a></li>{mails}</ul></div>
<div><h6>Address</h6><p>308, Prospect Rd,<br>Prospect SA 5082</p><p class="mt-s">Licence Number: RLA 350 628<br>ABN: 14682825449</p></div>
<div><h6>Quick Links</h6><ul>{q}</ul></div>
</div><div class="legal"><span>© 2024 OziRealty. All rights reserved.</span><span><a href="https://www.prospectbc.com.au/privacy-policy" target="_blank" rel="noopener">Privacy Policy</a></span></div></div></footer>
<div class="lightbox" id="lightbox" role="dialog" aria-label="Image viewer"><img alt=""></div>'''

def page(path, title, desc, body, og=''):
    canon = DOMAIN + (path if path != '/' else '')
    ogi = f'<meta property="og:image" content="{E(og)}">' if og else ''
    return f'''<!doctype html>
<html lang="en-AU"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(desc)}">
<link rel="canonical" href="{E(canon.rstrip('/') if path!='/' else DOMAIN)}">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}">{ogi}
<link rel="icon" href="{img('https://static.wixstatic.com/media/160674_f4475077d64f463b9fc5aac5b1632930~mv2.png',64)}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Jost:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css">
</head><body>
{header(path)}
<main>{body}</main>
{footer()}
<script src="/assets/site.js" defer></script>
</body></html>'''

# ---------------------------------------------------------------- forms
FORM_TO = {  # department mailbox each form is routed to
 'sell-property-house-adelaide':'sell','free-property-appraisal-sa':'sell','sell-my-business-australia':'sell',
 'rent-out-my-property-adelaide':'rent','rent-property-house-adelaide':'rent','manage-property-adelaide':'rent','property-rental-report':'rent',
 'buyer-agent-adelaide':'buy','land-opportunities-sa-adelaide':'buy','oversees-investment':'oversea','property-investment':'support',
}
SELECT_OPTS = {  # dropdown options as defined in the live site's Wix Forms
 'Select Your Plan': ['Income Protect', 'Income Optimise', 'Income & Risk Shield', 'Owner-Designed Plan'],
 'When are you considering selling?': ['1-3 months', '3-6 months', '6-12 months', 'Just browsing'],
 'Reason for report': ['Living here', 'Investing', 'Renting', 'Selling soon', 'Just Browsing'],
 'The property you’re looking at': ['House', 'Town House', 'Unit', 'Land', 'Commercial'],
 'Tell us what you’re looking for?': ['Buy a property', 'Sell a property', 'Rent a property', 'Investment property'],
}
fid = [0]
FORM_IDS = json.load(open(os.path.join(ROOT, 'content', 'form-ids.json'))) if os.path.exists(os.path.join(ROOT, 'content', 'form-ids.json')) else {}
SPECS = {}  # form key -> Wix Forms schema spec (input name == Wix field target)
def render_form(f, key, title=''):
    fid[0] += 1; n = fid[0]; out = []; spec = []
    for fl in f['fields']:
        lab = fl.get('label') or ''
        req = lab.endswith('*') or fl.get('req')
        clean = lab.rstrip(' *')
        name = re.sub(r'[^a-z0-9]+', '_', clean.lower()).strip('_')[:40] or f'f{len(out)}'
        r = ' required' if req else ''
        star = ' <span style="color:var(--red)">*</span>' if req else ''
        k = fl['k']
        if any(x['target'] == name for x in spec): name = f'{name}_{len(spec)}'
        if k in ('radio', 'checkbox') and fl.get('opts'):
            if not clean and k == 'checkbox' and len(fl['opts']) == 1:  # standalone checkbox (e.g. consent / opt-in)
                continue
            spec.append({'target': name, 'label': clean, 'kind': k, 'opts': [o for o in fl['opts'] if o], 'req': bool(req)})
            chips = ''.join(f'<label><input type="{k}" name="{name}" value="{E(o)}"{r if k=="radio" else ""}><span>{E(o)}</span></label>' for o in fl['opts'] if o)
            req_attr = ' data-required' if (req and k == 'checkbox') else ''
            out.append(f'<div class="fld full"><fieldset{req_attr}><legend>{E(clean)}{star}</legend><div class="chips">{chips}</div></fieldset></div>')
        elif k == 'select':
            opts = SELECT_OPTS.get(clean)
            spec.append({'target': name, 'label': clean, 'kind': 'select' if opts else 'text', 'opts': opts or [], 'req': False})
            if opts:
                o = ''.join(f'<option>{E(x)}</option>' for x in opts)
                out.append(f'<div class="fld full"><label for="f{n}_{name}">{E(clean)}</label><select id="f{n}_{name}" name="{name}"><option value="">Select…</option>{o}</select></div>')
            else:
                out.append(f'<div class="fld full"><label for="f{n}_{name}">{E(clean)}</label><input id="f{n}_{name}" name="{name}"></div>')
        elif k == 'textarea':
            spec.append({'target': name, 'label': clean, 'kind': 'textarea', 'req': bool(req)})
            out.append(f'<div class="fld full"><label for="f{n}_{name}">{E(clean)}{star}</label><textarea id="f{n}_{name}" name="{name}"{r}></textarea></div>')
        else:
            t = {'phone':'tel','tel':'tel','email':'email','date':'date','number':'number'}.get(k, 'text')
            if 'date' in clean.lower(): t = 'date'
            spec.append({'target': name, 'label': clean, 'kind': t, 'req': bool(req)})
            half = clean.lower() in ('first name','last name','email','phone','phone number','suburb','postcode','state')
            out.append(f'<div class="fld{"" if half else " full"}"><label for="f{n}_{name}">{E(clean)}{star}</label><input id="f{n}_{name}" name="{name}" type="{t}"{r} autocomplete="{ {"first name":"given-name","last name":"family-name","email":"email"}.get(clean.lower(), "tel" if t=="tel" else "on") }"></div>')
    to = FORM_TO.get(key.split('__')[0], 'support')
    SPECS[key] = {'name': (title or DATA.get(key, {}).get('title', key).split('|')[0]).strip(), 'fields': spec}
    consent = f['consent'] or 'By submitting this form, you acknowledge that you have read and understood our Privacy Policy, and consent to us collecting, using, and processing the personal information you provide in accordance with that policy.*'
    consent = E(consent).replace('Privacy Policy', '<a href="https://www.prospectbc.com.au/privacy-policy" target="_blank" rel="noopener">Privacy Policy</a>', 1)
    head = f'<h3>{E(title)}</h3>' if title else ''
    return f'''<form class="form-card" data-form="{E(key)}" data-form-id="{E(FORM_IDS.get(key, ''))}" data-to="{to}@ozirealty.com.au" novalidate>{head}
<div class="form-grid">{''.join(out)}</div>
<button class="btn btn-primary" type="submit">{E(f['submit'])} {ARROW}</button>
<p class="consent">{consent}</p><div class="form-ok" role="status">Thank you — your details have been sent. Our team will be in touch shortly.</div></form>'''

# ---------------------------------------------------------------- generic section renderer
H = ('h1','h2','h3','h4','h5','h6')
def text_items(items, skip_consent=True):
    """Render a run of non-structural items as prose with check-lists."""
    out = []; ul = []
    def flush():
        if ul: out.append('<ul class="checks' + (' cols' if len(ul) > 7 else '') + '">' + ''.join(ul) + '</ul>'); ul.clear()
    for it in items:
        t = it['t']
        if t == 'li': ul.append(f'<li>{E(it["text"])}</li>'); continue
        flush()
        if t in H:
            lvl = {'h1':'h2','h2':'h2','h3':'h3','h4':'h4','h5':'h5','h6':'h5'}[t]
            out.append(f'<{lvl}>{E(it["text"])}</{lvl}>')
        elif t == 'p':
            if skip_consent and it['text'].startswith('By submitting'): continue
            txt = E(it['text'])
            if '•' in txt:
                parts = [p.strip() for p in txt.split('•')]
                if parts[0]: out.append(f'<p>{parts[0]}</p>')
                out.append('<ul class="checks">' + ''.join(f'<li>{p}</li>' for p in parts[1:] if p) + '</ul>')
            else: out.append(f'<p>{txt}</p>')
        elif t == 'btn':
            out.append(button(it))
    flush()
    return '\n'.join(out)

def button(it, cls='btn-primary'):
    h = link(it.get('href'))
    if it['text'] in ('Privacy Policy',) or not it.get('href'): return ''
    tgt = ' target="_blank" rel="noopener"' if ext(h) else ''
    label = it['text']
    if label == 'First-person': label = 'Get My Free Appraisal'  # the live site's button carries only its icon's alt text
    if label == 'Next': label = 'Learn more'
    return f'<a class="btn {cls}" href="{E(h)}"{tgt}>{E(label)} {ARROW}</a>'

def btn_row(items, first='btn-primary'):
    bs = [button(b, first if i == 0 else 'btn-ghost') for i, b in enumerate(items) if b['t'] == 'btn']
    bs = [b for b in bs if b]
    return f'<div class="btn-row">{"".join(bs)}</div>' if bs else ''

def split_groups(items, level):
    groups = []; cur = None; pre = []
    for it in items:
        if it['t'] == level:
            cur = {'h': it['text'], 'items': []}; groups.append(cur)
        elif cur is None: pre.append(it)
        else: cur['items'].append(it)
    return pre, groups

def card_grid(groups, cols='g3', numbered=False):
    cards = []
    for i, g in enumerate(groups):
        im = next((x for x in g['items'] if x['t'] == 'img'), None)
        body = text_items([x for x in g['items'] if x['t'] not in ('img', 'btn')])
        b = btn_row(g['items'])
        ic = f'<div class="ic">{i+1:02d}</div>' if numbered else ''
        media = f'<div class="media" style="aspect-ratio:16/10;margin:-28px -28px 20px;border-radius:0;box-shadow:none"><img loading="lazy" src="{img(im["src"],800,500)}" alt="{E(im.get("alt") or g["h"])}"></div>' if im else ''
        cards.append(f'<div class="card rv">{media}{ic}<h4>{E(g["h"])}</h4>{body}{("<div class=card-cta>"+b+"</div>") if b else ""}</div>')
    return f'<div class="grid {cols}">{"".join(cards)}</div>'

def faq_block(items):
    intro = []; qs = []; cur = None
    for it in items:
        if it['t'] == 'q': cur = {'q': it['text'], 'a': []}; qs.append(cur)
        elif cur is None: intro.append(it)
        else: cur['a'].append(it)
    det = ''
    for q in qs:
        det += f'<details class="rv"><summary>{E(q["q"])}</summary><div class="ans prose">{text_items([a for a in q["a"] if a["t"] != "btn"])}</div></details>'
    return intro, f'<div class="faq">{det}</div>'

def is_logo(src): return src.lower().endswith('.png')

def render_section(items, key, idx, alt, anchor=None):
    """Pick a layout for one live-site section based on its content pattern."""
    cls = ' alt' if alt else ''
    ida = f' id="{anchor}"' if anchor else ''
    kinds = collections.Counter(i['t'] for i in items)
    imgs = [i for i in items if i['t'] == 'img']
    form = next((i for i in items if i['t'] == 'form'), None)
    if form:
        before = [i for i in items if i['t'] not in ('form', 'img') and not (i['t'] == 'btn' and i['text'] == 'Privacy Policy')]
        heads = [i for i in before if i['t'] in H]
        title = ''
        if len(before) == 1 and heads: title = heads[0]['text']; before = []
        im = imgs[0] if imgs else None
        left = text_items(before)
        if im: left += f'<div class="media contain mt-m"><img loading="lazy" src="{img(im["src"],900)}" alt="{E(im.get("alt"))}"></div>'
        if not left:
            return f'<section class="{cls.strip()}"{ida}><div class="wrap" style="max-width:860px">{render_form(form, key, title)}</div></section>'
        return f'<section class="dark"{ida}><div class="wrap split on-dark"><div class="prose rv">{left}</div><div class="rv">{render_form(form, key, title)}</div></div></section>'
    if kinds['q']:
        intro, acc = faq_block(items)
        ih = ''
        if intro:
            hh = [i for i in intro if i['t'] in H]
            ih = f'<div class="sec-head center"><span class="eyebrow">FAQ</span>{text_items(intro)}</div>'
        return f'<section class="{cls.strip()}"{ida}><div class="wrap">{ih}{acc}</div></section>'
    texts = [i for i in items if i['t'] in H + ('p', 'li')]
    # gallery / logos: mostly images
    if len(imgs) >= 3 and len(texts) <= 2 and not any(i['t'] == 'p' for i in items if len(i.get('text', '')) > 60):
        head = text_items([i for i in items if i['t'] in H + ('p',)])
        logos = all(is_logo(i['src']) for i in imgs)
        if logos and len(imgs) >= 6:
            grid = '<div class="logos">' + ''.join(f'<div><img loading="lazy" src="{img(i["src"],320)}" alt="{E(i.get("alt") or "partner logo")}"></div>' for i in imgs) + '</div>'
        else:
            c = ' contain' if logos else ''
            grid = f'<div class="gallery{c}">' + ''.join(f'<a href="{img(i["src"],1800)}" data-lb><img loading="lazy" src="{img(i["src"],900)}" alt="{E(i.get("alt") or "Ozi Realty image")}"></a>' for i in imgs) + '</div>'
        return f'<section class="{cls.strip()}"{ida}><div class="wrap"><div class="sec-head center">{head}</div>{grid}{btn_row(items)}</div></section>'
    # card grids: a top heading followed by >=3 sub-headed groups
    for lvl in ('h4', 'h3', 'h5'):
        pre, groups = split_groups([i for i in items], lvl)
        if len(groups) >= 3 and sum(1 for g in groups if g['items']) >= len(groups) - 1 or (lvl == 'h4' and len(groups) >= 4):
            if len(groups) < 3: continue
            pre_imgs = [i for i in pre if i['t'] == 'img']
            head = text_items([i for i in pre if i['t'] != 'img'])
            cols = 'g4' if len(groups) in (4, 8) or len(groups) > 6 else 'g3'
            has_list = any(x['t'] == 'li' for g in groups for x in g['items'])
            grid = card_grid(groups, cols, numbered=not has_list)
            side = ''
            if pre_imgs and not head:
                side = ''
            if pre_imgs:
                head = f'<div class="split"><div class="prose">{head}</div><div class="media contain"><img loading="lazy" src="{img(pre_imgs[0]["src"],900)}" alt=""></div></div>' if head else ''
            return f'<section class="{cls.strip()}"{ida}><div class="wrap"><div class="sec-head">{head}</div>{grid}</div></section>'
    # split text + one image
    body = text_items([i for i in items if i['t'] != 'img'])
    if imgs:
        im = imgs[0]
        rev = ' rev' if idx % 2 else ''
        cont = ' contain' if is_logo(im['src']) else ''
        extra = ''.join(f'<div class="media{cont} mt-m"><img loading="lazy" src="{img(i["src"],900)}" alt="{E(i.get("alt"))}"></div>' for i in imgs[1:3])
        return f'<section class="{cls.strip()}"{ida}><div class="wrap split{rev}"><div class="prose rv">{body}</div><div class="rv"><div class="media{cont}"><img loading="lazy" src="{img(im["src"],1100)}" alt="{E(im.get("alt") or "Ozi Realty")}"></div>{extra}</div></div></section>'
    return f'<section class="{cls.strip()}"{ida}><div class="wrap" style="max-width:880px"><div class="prose rv">{body}</div></div></section>'

def hero_from(items, path, title_fallback):
    """Turn a page's first section into a hero; returns (html, remaining_items)."""
    imgs = [i for i in items if i['t'] == 'img']
    heads = [i for i in items if i['t'] in H]
    if not heads: return page_hero(title_fallback, []), items
    h1 = heads[0]
    rest = items[items.index(h1) + 1:]
    lead = []; remaining = []
    # hero copy = following short headings/paragraphs/buttons until a list/form/sub-group starts
    for i, it in enumerate(rest):
        if it['t'] in ('p', 'h4', 'h5', 'h2', 'h1', 'btn') and len(lead) < 6 and not remaining:
            if it['t'] in ('h2', 'h1') and lead: remaining = rest[i:]; break
            lead.append(it)
        else:
            remaining = rest[i:]; break
    bg = imgs[0] if imgs and items.index(imgs[0]) < items.index(h1) + 3 + len(lead) else None
    if bg and bg in remaining: remaining.remove(bg)
    return page_hero(h1['text'], lead, bg['src'] if bg else None), [r for r in remaining if r is not bg]

def page_hero(title, lead, bg=None):
    sub = ''
    btns = [l for l in lead if l['t'] == 'btn']
    for l in lead:
        if l['t'] in ('h4', 'h5', 'h2', 'h1'): sub += f'<div class="sub">{E(l["text"])}</div>'
        elif l['t'] == 'p': sub += f'<p>{E(l["text"])}</p>'
    br = ''
    if btns:
        br = '<div class="btn-row">' + ''.join(button(b, 'btn-accent' if i == 0 else 'btn-ghost') for i, b in enumerate(btns)) + '</div>'
    if bg:
        return f'<section class="hero compact" style="padding:0"><div class="bg" style="background-image:url(\'{img(bg,2000)}\')"></div><div class="wrap"><span class="eyebrow">Ozi Realty Adelaide</span><h1>{E(title)}</h1>{sub}{br}</div></section>'
    return f'<section class="page-hero" style="padding:0"><div class="wrap on-dark"><span class="eyebrow">Ozi Realty Adelaide</span><h1 class="mt-s">{E(title)}</h1>{sub}{br}</div></section>'

def anchors_for(key):
    """Anchor ids the live site links to (#pmform, #freequote, ...) mapped to sections."""
    a = set()
    for s in DATA[key]['sections']:
        for it in s:
            h = it.get('href') or ''
            if '#' in h and h.split('#')[0].rstrip('/').endswith(key.replace('__', '/')): a.add(h.split('#')[1])
    return a

def generic_page(key, path):
    p = DATA[key]; secs = [list(s) for s in p['sections']]
    # pages whose content sits in one section: split it at form boundaries for clarity
    body = []; anchors = anchors_for(key)
    first = secs[0]
    hero, rest = hero_from(first, path, p['title'].split('|')[0].strip())
    body.append(hero)
    secs = ([rest] if rest else []) + secs[1:]
    # split mixed sections: [content..., form] -> content section + form section
    final = []
    for s in secs:
        if any(i['t'] == 'form' for i in s) and len([i for i in s if i['t'] in ('li',)]) > 6:
            k = max(j for j, i in enumerate(s) if i['t'] in H and j < next(j for j, x in enumerate(s) if x['t'] == 'form'))
            final.append(s[:k]); final.append(s[k:])
        else: final.append(s)
    for i, s in enumerate(final):
        if not s: continue
        anc = None
        if any(x['t'] == 'form' for x in s):
            anc = next((a for a in anchors if 'form' in a or 'quote' in a), None) or 'form'
        elif 'learnmore' in anchors and i == 0: anc = 'learnmore'
        body.append(render_section(s, key, i, i % 2 == 1, anc))
    return page(path, p['title'], p['desc'], '\n'.join(body), p.get('og'))

# ---------------------------------------------------------------- bespoke: home
def S(key, i): return DATA[key]['sections'][i]
def home():
    d = DATA['index']; s = d['sections']
    hero = f'''<section class="hero" style="padding:0"><div class="bg" style="background-image:url('{img(s[0][0]['src'],2200)}')"></div><div class="wrap">
<span class="eyebrow">Adelaide · South Australia</span><h1>{E(s[0][1]['text'])}</h1><p>{E(s[0][2]['text'])}</p>
<div class="btn-row"><a class="btn btn-accent" href="/free-property-appraisal-sa/">Get My Free Appraisal {ARROW}</a><a class="btn btn-ghost" href="/book-online/">Book a Free Consultation</a></div>
<div class="hero-badges"><span class="badge"><i></i>Property Management From 2.99%</span><span class="badge"><i></i>100 Days Risk-Free</span><span class="badge"><i></i>No Middle Man</span><span class="badge"><i></i>Licence RLA 350 628</span></div>
</div></section>'''
    # S1 property management + S2 journey tiles
    pm = s[1]
    tiles = [f'''<a class="tile feature" href="/manage-property-adelaide/"><img src="{img(pm[-1]['src'],900)}" alt="" style="object-fit:contain;padding:30px 30px 90px;opacity:.95"><div class="t"><div><span class="tag" style="margin-bottom:8px">From 2.99%</span><h3>{E(pm[0]['text'])}</h3><p style="color:#DCE4FF;font-size:.9rem">100 Days Risk-Free · No Middle Man</p></div><span class="arrow">{ARROW}</span></div></a>''']
    it = s[2]; k = 0
    while k < len(it):
        if it[k]['t'] == 'img' and k + 2 < len(it):
            im, label, b = it[k], it[k+1], it[k+2]
            tiles.append(f'<a class="tile rv" href="{link(b.get("href"))}"><img loading="lazy" src="{img(im["src"],700,520)}" alt="{E(label["text"])}"><div class="t"><h3>{E(label["text"])}</h3><span class="arrow">{ARROW}</span></div></a>')
            k += 3
        else: k += 1
    journey = f'<section><div class="wrap"><div class="sec-head"><span class="eyebrow">How can we help?</span><h2>Choose your property journey</h2><p>Select where you are today and we’ll take you straight to the right team.</p></div><div class="tiles">{"".join(tiles)}</div></div></section>'
    # S3 strategy offers
    offers = strategy_offers(s[3])
    strat = f'<section class="alt"><div class="wrap"><div class="sec-head"><span class="eyebrow">Free reports &amp; advice</span><h2>{E(s[3][0]["text"])}</h2></div>{offers}</div></section>'
    # S4 free book form
    fb = s[4]; frm = next(x for x in fb if x['t'] == 'form'); im = next(x for x in fb if x['t'] == 'img')
    book = f'''<section class="dark" id="free-book"><div class="wrap split on-dark"><div class="rv"><span class="eyebrow">{E(fb[0]['text'])}</span><h2 class="mt-s">{E(fb[1]['text'])}</h2><p class="lead mt-s">{E(fb[2]['text'])}</p><div class="media contain mt-m" style="max-width:360px"><img loading="lazy" src="{img(im['src'],720)}" alt="10 Truths About Finding The Right Home book"></div></div><div class="rv">{render_form(frm,'index','Get your free copy')}</div></div></section>'''
    # S5 why work with us
    pre, groups = split_groups(s[5][1:], 'h3')
    why = f'<section><div class="wrap"><div class="sec-head center"><span class="eyebrow">Our promise</span><h2>{E(s[5][0]["text"])}</h2></div>{card_grid(groups,"g3",False)}</div></section>'
    # S6 partners, S7 blog, S8 testimonials, S9 FAQ
    partners = render_section(s[6], 'index', 6, True)
    posts = sorted(post_list(), key=lambda x: x['date'], reverse=True)[:3]
    blog = f'<section><div class="wrap"><div class="sec-head" style="display:flex;justify-content:space-between;align-items:end;gap:20px;flex-wrap:wrap;max-width:none"><div><span class="eyebrow">Insights</span><h2 class="mt-s">{E(s[7][0]["text"])}</h2></div><a class="btn btn-ghost" href="/blog/">Read More {ARROW}</a></div><div class="posts">{"".join(post_card(p) for p in posts)}</div></div></section>'
    q = s[8]
    quotes = f'<section class="alt"><div class="wrap"><div class="sec-head center"><span class="eyebrow">Testimonials</span><h2>{E(q[0]["text"])}</h2></div><div class="quotes" style="max-width:640px;margin:0 auto"><div class="quote rv"><div class="stars">★★★★★</div><blockquote>“{E(q[1]["text"])}”</blockquote><cite>{E(q[2]["text"].strip(chr(8207)))}</cite></div></div></div></section>'
    intro, acc = faq_block(s[9][1:])
    faq = f'<section><div class="wrap"><div class="sec-head center"><span class="eyebrow">Questions</span><h2>{E(s[9][0]["text"])}</h2></div>{acc}</div></section>'
    cta = cta_band()
    return page('/', d['title'], d['desc'], hero + journey + strat + book + why + partners + blog + quotes + faq + cta, d.get('og'))

def cta_band():
    return f'<section style="padding-top:0"><div class="wrap"><div class="cta-band"><div><h2>Speak directly with Esi Dor</h2><p>Free property strategy consultation with the Principal of OziRealty (RLA 350 628). No pressure. Just clear, professional advice.</p></div><div class="btn-row" style="margin:0;position:relative;z-index:1"><a class="btn btn-accent" href="/book-online/">Book Your Free Consultation {ARROW}</a><a class="btn btn-ghost" href="tel:1800400333">{PHONE} 1800 400 333</a></div></div></div></section>'

def strategy_offers(items):
    """The four offer blocks (appraisal, consultation, suburb report, rental report)."""
    blocks = []; cur = None
    imgs = []
    for it in items[1:] if items[0]['t'] in H and items[0]['text'].startswith('Property Value') else items:
        if it['t'] == 'img': imgs.append(it); continue
        if it['t'] == 'h5' or (it['t'] == 'h3' and (cur is None or cur.get('h3'))):
            cur = {'tag': None, 'h3': None, 'li': [], 'btn': None}; blocks.append(cur)
        if cur is None: continue
        if it['t'] == 'h5': cur['tag'] = it['text']
        elif it['t'] == 'h3': cur['h3'] = it['text']
        elif it['t'] == 'li': cur['li'].append(it['text'])
        elif it['t'] == 'btn': cur['btn'] = it
    out = []
    for i, b in enumerate(blocks):
        im = imgs[i] if i < len(imgs) else None
        tag = f'<span class="tag{" red" if b["tag"]=="Limited Offer" else ""}">{E(b["tag"])}</span>' if b['tag'] else ''
        lis = ''.join(f'<li>{E(x)}</li>' for x in b['li'])
        out.append(f'<div class="offer rv{" rev" if i%2 else ""}"><div class="om">{f"<img loading=lazy src={chr(34)}{img(im[chr(115)+chr(114)+chr(99)],1000,760)}{chr(34)} alt={chr(34)}{E(b[chr(104)+chr(51)])}{chr(34)}>" if im else ""}</div><div class="ob">{tag}<h3>{E(b["h3"])}</h3><ul class="checks{" cols" if len(b["li"])>7 else ""} mt-s">{lis}</ul>{btn_row([b["btn"]]) if b["btn"] else ""}</div></div>')
    return ''.join(out)

# ---------------------------------------------------------------- bespoke: services / strategy / manage / about
def services():
    d = DATA['property-services']; s = d['sections']
    hero = page_hero('Our Services', [x for x in s[0][1:]])
    s1 = s[1]
    tiles = []
    pmi = next(x for x in s1 if x['t'] == 'img')
    tiles.append(f'<a class="tile feature" href="/manage-property-adelaide/"><img src="{img(pmi["src"],900)}" alt="" style="object-fit:contain;padding:30px 30px 90px"><div class="t"><div><span class="tag" style="margin-bottom:8px">From 2.99%</span><h3>Manage My Property</h3><p style="color:#DCE4FF;font-size:.9rem">Maximise your returns while we handle everything from tenants to maintenance.</p></div><span class="arrow">{ARROW}</span></div></a>')
    k = s1.index(pmi) + 1
    while k + 2 < len(s1) and s1[k]['t'] == 'img':
        im, label, b = s1[k], s1[k+1], s1[k+2]
        tiles.append(f'<a class="tile rv" href="{link(b.get("href"))}"><img loading="lazy" src="{img(im["src"],700,520)}" alt="{E(label["text"])}"><div class="t"><h3>{E(label["text"])}</h3><span class="arrow">{ARROW}</span></div></a>'); k += 3
    rest = s1[k:]
    journey = f'<section><div class="wrap"><div class="sec-head"><span class="eyebrow">Services</span><h2>{E(s1[0]["text"])}</h2><p>{E(s1[1]["text"])}</p></div><div class="tiles">{"".join(tiles)}</div></div></section>'
    strat = f'<section class="dark"><div class="wrap" style="max-width:900px"><div class="prose on-dark rv"><span class="eyebrow">Strategy</span>{text_items(rest)}</div></div></section>'
    return page('/property-services/', d['title'], d['desc'], hero + journey + strat + cta_band(), d.get('og'))

def strategy():
    d = DATA['property-strategy-services']; s = d['sections']
    a = s[0]; im = next(x for x in a if x['t'] == 'img')
    hero = f'<section class="hero compact" style="padding:0"><div class="bg" style="background-image:url(\'{img(im["src"],2000)}\')"></div><div class="wrap"><span class="eyebrow">Ozi Realty Adelaide</span><h1>{E(a[0]["text"])}</h1><div class="sub">{E(a[1]["text"])}</div></div></section>'
    intro = f'<section><div class="wrap" style="max-width:880px"><div class="prose rv">{text_items([x for x in a[2:] if x["t"]=="p"])}</div></div></section>'
    offers = f'<section class="alt"><div class="wrap">{strategy_offers(s[1])}</div></section>'
    return page('/property-strategy-services/', d['title'], d['desc'], hero + intro + offers + cta_band(), d.get('og'))

def manage():
    d = DATA['manage-property-adelaide']; s = d['sections']
    hero = f'''<section class="page-hero" style="padding:0"><div class="wrap on-dark split"><div><span class="eyebrow">Adelaide Property Management</span><h1 class="mt-s">{E(s[0][0]['text'])}</h1><div class="sub" style="font-size:1.6rem;color:var(--orange-lt)">{E(s[0][1]['text'])}</div>
<div class="hero-badges"><span class="badge"><i></i>100 Days Risk-Free</span><span class="badge"><i></i>No Middle Man</span><span class="badge"><i></i>Trust Account</span><span class="badge"><i></i>REISA standards</span></div>
<div class="btn-row"><a class="btn btn-accent" href="#pmform">See If I’m Paying Too Much {ARROW}</a><a class="btn btn-ghost" href="#plans">View Plans</a></div></div>
<div class="media contain"><img src="{img(s[2][1]['src'],900)}" alt="Property management"></div></div></section>'''
    s1 = s[1]; ix = next(i for i, x in enumerate(s1) if x['t'] == 'h1' and 'Plans' in x['text'])
    intro_items = s1[:ix]
    ip = [x for x in intro_items if x['t'] == 'p']
    promo = next((x for x in ip if x['text'].startswith('FOR ALL PACKAGES')), None)
    intro = f'<section><div class="wrap split"><div class="prose rv"><span class="eyebrow">Why OziRealty</span><h2 class="mt-s">{E(intro_items[0]["text"])}</h2>{text_items([x for x in ip if x is not promo])}</div><div class="rv"><div class="card" style="background:var(--navy);color:#fff;border:0"><span class="tag">For all packages</span><h3>Bring a friend. Enjoy 2 months of management fee-free</h3><p style="color:#C7D0DF" class="mt-s">{E(promo["text"]) if promo else ""}</p><div class="btn-row"><a class="btn btn-accent" href="#pmform">Get Started {ARROW}</a></div></div></div></div></section>'
    pre, groups = split_groups(s1[ix+1:], 'h4')
    plans = ''
    for i, g in enumerate(groups):
        lis = ''.join(f'<li>{E(x["text"])}</li>' for x in g['items'] if x['t'] == 'li')
        b = next((x for x in g['items'] if x['t'] == 'btn'), None)
        pop = ' pop' if i == 1 else ''
        badge = '<span class="tag" style="align-self:flex-start">Most popular</span>' if i == 1 else ''
        plans += f'<div class="plan rv{pop}">{badge}<h4>{E(g["h"])}</h4><ul class="checks">{lis}</ul><a class="btn {"btn-accent" if pop else "btn-primary"}" href="#pmform">{E(b["text"] if b else "Optimise Income")} {ARROW}</a></div>'
    plans_sec = f'<section class="alt" id="plans"><div class="wrap"><div class="sec-head center"><span class="eyebrow">Plans</span><h2>{E(s1[ix]["text"])}</h2></div><div class="plans">{plans}</div></div></section>'
    pre2, g2 = split_groups(s[2][2:], 'h4')
    diff = f'<section><div class="wrap"><div class="sec-head center"><span class="eyebrow">The difference</span><h2>{E(s[2][0]["text"])}</h2></div>{card_grid([dict(h=g["h"][0].upper()+g["h"][1:], items=g["items"]) for g in g2],"g4",True)}</div></section>'
    frm = render_section(s[3], 'manage-property-adelaide', 0, False, 'pmform')
    intro4, acc = faq_block(s[4][1:])
    faq = f'<section class="alt"><div class="wrap"><div class="sec-head center"><span class="eyebrow">Questions</span><h2>FAQ</h2></div>{acc}</div></section>'
    return page('/manage-property-adelaide/', d['title'], d['desc'], hero + intro + plans_sec + diff + frm + faq, d.get('og'))

def about():
    d = DATA['about-adelaide-land-agent']; s = d['sections']
    hero = page_hero('About Us', [{'t': 'p', 'text': s[4][0]['text']}])
    a = s[1]; im = a[0]
    vals = [x for x in a if x['t'] == 'li']
    ps = [x['text'] for x in a if x['t'] == 'p']
    vision = ps[3].replace(' Values', '').strip() if len(ps) > 3 else ''
    mv = f'''<section><div class="wrap split"><div class="media rv"><img src="{img(im['src'],1100,825)}" alt="Adelaide property"></div><div class="rv">
<div class="card"><div class="ic">01</div><h4>{E(ps[0])}</h4><p>{E(ps[1])}</p></div>
<div class="card mt-s"><div class="ic">02</div><h4>{E(ps[2])}</h4><p>{E(vision)}</p></div>
<div class="card mt-s"><div class="ic">03</div><h4>Values</h4><ul class="checks">{''.join(f"<li>{E(v['text'])}</li>" for v in vals)}</ul></div></div></div></section>'''
    story = f'<section class="alt"><div class="wrap" style="max-width:880px"><div class="prose rv center"><span class="eyebrow">Our story</span>{text_items(s[3])}</div></div></section>'
    board = s[2]
    team = f'<section><div class="wrap"><div class="sec-head center"><span class="eyebrow">Leadership</span><h2>{E(board[0]["text"])}</h2></div><div style="max-width:380px;margin:0 auto" class="card rv center"><div class="media" style="aspect-ratio:1;margin-bottom:20px"><img src="{img(board[1]["src"],700,700)}" alt="Esi Dor"></div><p>{E(board[2]["text"])}</p><h3 style="margin:6px 0">{E(board[3]["text"])}</h3><p>{E(board[4]["text"])}</p><div class="btn-row" style="justify-content:center"><a class="btn btn-primary" href="/book-online/">Book a meeting {ARROW}</a></div></div></div></section>'
    return page('/about-adelaide-land-agent/', d['title'], d['desc'], hero + mv + story + team + cta_band(), d.get('og'))

def contact():
    d = DATA['contact-adelaide-realestae-agency']; s = d['sections']
    a = s[0]; im = next(x for x in a if x['t'] == 'img')
    hero = page_hero('Contact Us', [])
    c1 = f'<section><div class="wrap split"><div class="prose rv"><span class="eyebrow">Free consultation</span>{text_items([x for x in a[1:] if x["t"]!="img"])}</div><div class="media rv contain"><img src="{img(im["src"],1000)}" alt="Free property strategy consultation"></div></div></section>'
    b = s[1]; ps = [x for x in b if x['t'] == 'p']
    depts = [('General Inquiries','support'),('Rentals','rent'),('Sellers','sell'),('Buyers','buy'),('Overseas investment','oversea')]
    cards = ''.join(f'<a class="card rv" href="mailto:{m}@ozirealty.com.au"><span class="eyebrow">{n}</span><h4 class="mt-s" style="word-break:break-all">{m}@ozirealty.com.au</h4></a>' for n, m in depts)
    c2 = f'''<section class="alt"><div class="wrap"><div class="sec-head"><span class="eyebrow">Get in touch</span><h2>{E(b[0]['text'])}</h2>{''.join(f"<p>{E(p['text'])}</p>" for p in ps[:2])}</div>
<div class="grid g3"><a class="card rv" href="tel:1800400333" style="background:var(--navy);color:#fff;border:0"><span class="eyebrow">Call</span><h3 class="mt-s">1800 400 333</h3></a><a class="card rv" href="https://maps.google.com/?q=308+Prospect+Rd,+Prospect+SA+5082" target="_blank" rel="noopener"><span class="eyebrow">Visit</span><h4 class="mt-s">308, Prospect Rd, Prospect SA 5082</h4></a>{cards}</div>
<div class="media mt-l" style="aspect-ratio:21/8"><iframe title="Ozi Realty office map" src="https://maps.google.com/maps?q=308%20Prospect%20Rd%2C%20Prospect%20SA%205082&z=15&output=embed" style="border:0;width:100%;height:100%" loading="lazy"></iframe></div></div></section>'''
    return page('/contact-adelaide-realestae-agency/', d['title'], d['desc'], hero + c1 + c2, d.get('og'))

def gift():
    d = DATA['realestate-gift-adelaide']; s = d['sections']
    hero = f'<section class="page-hero" style="padding:0"><div class="wrap on-dark center"><span class="eyebrow">Exclusive</span><h1 class="mt-s" style="margin-left:auto;margin-right:auto">{E(s[0][0]["text"])}</h1><p style="margin:16px auto 0">{E(s[1][1]["text"])}</p><div class="btn-row" style="justify-content:center"><a class="btn btn-accent" href="#form">Get on the List {ARROW}</a></div></div></section>'
    icons = [x for x in s[1] if x['t'] == 'img'][1:]
    why_p = [x['text'] for x in s[2] if x['t'] == 'p']
    why = f'<section><div class="wrap"><div class="sec-head center"><span class="eyebrow">Buy, Rent, Investment &amp; Sell</span><h2>{E(s[2][0]["text"])}</h2></div><div class="grid g4">' + ''.join(f'<div class="card rv"><div class="ic">{i+1:02d}</div><h4>{E(p.split(":")[0])}</h4><p>{E(p.split(":",1)[1].strip() if ":" in p else "")}</p></div>' for i, p in enumerate(why_p)) + '</div></div></section>'
    esi = s[3]
    team = f'<section class="alt"><div class="wrap split"><div class="prose rv"><span class="eyebrow">Who we are</span><h3 class="mt-s">{E(esi[0]["text"])}</h3></div><div class="agent rv" style="max-width:420px"><img src="{img(esi[1]["src"],200,200)}" alt="Esi Dor"><div><small style="color:var(--muted)">{E(esi[2]["text"])}</small><h4>{E(esi[3]["text"])}</h4><p>{E(esi[4]["text"])}</p></div></div></div></section>'
    g = s[4]
    gifts = [x['text'] for x in g if x['t'] in ('h3', 'h4')]
    book = s[5]
    giftsec = f'<section><div class="wrap"><div class="sec-head center"><span class="eyebrow">Bundle gift</span><h2>{E(g[1]["text"])}</h2></div><div class="grid g3">' + ''.join(f'<div class="card rv"><div class="ic">🎁</div><h4>{E(t)}</h4></div>' for t in gifts) + f'<div class="card rv" style="background:var(--navy);color:#fff;border:0"><span class="tag">Free book</span><h4>{E(book[0]["text"])}</h4><p>{E(book[1]["text"])}</p><h3 class="mt-s" style="color:var(--orange-lt)">{E(book[3]["text"])}</h3></div></div></div></section>'
    frm = next(x for x in s[6] if x['t'] == 'form')
    fsec = f'<section class="dark" id="form"><div class="wrap split on-dark"><div class="rv"><span class="eyebrow">Get on the list</span><h2 class="mt-s">{E(g[1]["text"])}</h2><div class="media contain mt-m" style="max-width:340px"><img loading="lazy" src="{img(book[2]["src"],700)}" alt="10 Truths About Finding the Right Home"></div></div><div class="rv">{render_form(frm,"realestate-gift-adelaide","Receive your bundle gift")}</div></div></section>'
    return page('/realestate-gift-adelaide/', d['title'], d['desc'], hero + why + team + giftsec + fsec, d.get('og'))

def oversea():
    d = DATA['oversees-investment']; s = d['sections']
    a = s[0]
    hero = f'''<section class="hero" style="padding:0"><div class="bg" style="background-image:url('{img(a[0]['src'],2200)}')"></div><div class="wrap"><span class="eyebrow">{E(a[3]['text'])}</span><h1>{E(a[1]['text'])}</h1><div class="sub">{E(a[2]['text'])}</div><div class="btn-row"><a class="btn btn-accent" href="#freequote">Free Quote {ARROW}</a><a class="btn btn-ghost" href="#learnmore">Learn More</a></div></div></section>'''
    b = s[1]
    s1 = f'<section id="learnmore"><div class="wrap split"><div class="prose rv"><span class="eyebrow">Dubai</span><h2 class="mt-s">{E(b[1]["text"])}</h2><p class="lead mt-s">{E(b[2]["text"])}</p></div><div class="media rv"><img loading="lazy" src="{img(b[0]["src"],1100,825)}" alt="Dubai skyline"></div></div></section>'
    s2 = render_section(s[2], 'oversees-investment', 2, True)
    s3 = render_section(s[3], 'oversees-investment', 3, False)
    q = s[4]; ps = [x['text'] for x in q if x['t'] == 'p']
    quotes = f'<section class="alt"><div class="wrap"><div class="sec-head center"><span class="eyebrow">Investor stories</span><h2>{E(q[0]["text"])}</h2></div><div class="quotes">' + ''.join(f'<div class="quote rv"><div class="stars">★★★★★</div><blockquote>{E(ps[i])}</blockquote><cite>{E(ps[i+1])}</cite></div>' for i in range(0, len(ps) - 1, 2)) + '</div></div></section>'
    pre, groups = split_groups(s[5][1:], 'h3')
    cb = f'<section class="dark"><div class="wrap"><div class="sec-head center on-dark"><span class="eyebrow">Why OziRealty</span><h2>{E(s[5][0]["text"])}</h2></div>{card_grid([dict(h=g["h"].strip(), items=g["items"]) for g in groups],"g3",True)}</div></section>'
    frm = render_section(s[6], 'oversees-investment', 0, False, 'freequote')
    return page('/oversees-investment/', d['title'], d['desc'], hero + s1 + s2 + s3 + quotes + cb + frm, d.get('og'))

def book_online(key='book-online', path='/book-online/'):
    d = DATA[key]; s = d['sections'][0]
    ps = [x for x in s if x['t'] == 'p']
    im = next((x for x in s if x['t'] == 'img'), None)
    hero = page_hero(s[0]['text'] if key == 'book-online' else 'Real Estate Consultation', [{'t': 'p', 'text': 'Expert property advice with Esi Dor, Principal of OziRealty (RLA 350 628)'}])
    body = text_items(ps) if key == 'book-online' else text_items([x for x in s if x['t'] == 'p'][:1] + [{'t':'h3','text':'Service Description'}] + [x for x in s if x['t']=='p'][1:2])
    card = f'''<div class="card rv" style="padding:0;overflow:hidden">{f'<img src="{img(im["src"],900,560)}" alt="Real estate consultation" style="width:100%">' if im else ''}<div style="padding:28px"><span class="tag">Available Online · 30 min</span><h3>Real Estate Consultation</h3><p class="mt-s">Expert property advice with Esi Dor, Principal of OziRealty (RLA 350 628)</p>
<div class="stats mt-m"><div class="stat"><b>30 min</b><span>Duration</span></div><div class="stat"><b>Free</b><span>No obligation</span></div></div>
<form class="mt-m" data-form="booking" data-form-id="{E(FORM_IDS.get('booking', ''))}" data-to="support@ozirealty.com.au" novalidate><div class="form-grid" style="margin-top:0"><div class="fld"><label for="b_name">Full name <span style="color:var(--red)">*</span></label><input id="b_name" name="first_name" required></div><div class="fld"><label for="b_phone">Phone <span style="color:var(--red)">*</span></label><input id="b_phone" name="phone" type="tel" required></div><div class="fld"><label for="b_email">Email <span style="color:var(--red)">*</span></label><input id="b_email" name="email" type="email" required></div><div class="fld"><label for="b_date">Preferred date</label><input id="b_date" name="preferred_date" type="date"></div><div class="fld full"><label for="b_msg">What would you like to discuss?</label><textarea id="b_msg" name="message"></textarea></div></div><button class="btn btn-primary" style="width:100%;margin-top:16px" type="submit">Request to Book {ARROW}</button><div class="form-ok" role="status">Thank you — your booking request has been sent. We’ll confirm a time shortly.</div></form></div></div>'''
    sec = f'<section><div class="wrap split"><div class="prose rv">{body}<div class="note mt-m">308 Prospect Road, Prospect SA, Australia · 1800 400 333 · admin@ozirealty.com.au</div></div>{card}</div></section>'
    return page(path, d['title'], d['desc'][:300], hero + sec, d.get('og'))

# ---------------------------------------------------------------- properties
def property_page(key):
    d = DATA[key]; s = d['sections'][0]; slug = key.split('__')[1]
    title = s[0]['text']; kind = s[1]['text']; status = s[2]['text']
    ps = [x['text'] for x in s if x['t'] == 'p']
    def after(label):
        i = ps.index(label) if label in ps else -1
        return ps[i + 1] if i >= 0 and i + 1 < len(ps) else ''
    bath, bed = after('Bathroom'), after('Bedroom')
    size = next((p for p in ps if 'm²' in p), '')
    floor = ps[ps.index('Size') + 1] if 'Size' in ps else ''
    price = after('Price')
    gi = next(i for i, x in enumerate(s) if x['t'] == 'h4' and 'Gallery' in x['text'])
    icons = {'a81bb2_6c6ba90f754444e0bf7a9002d9a70fc4~mv2.png','a81bb2_3c2a051e52c5468799450f1fde4cd48a~mv2.png','a81bb2_bc079639ab80490d8fb20e98de8015b4~mv2.png','a81bb2_ed05034e9084434081d639df4ec00c42~mv2.png','a81bb2_54ffd67c127a4e77a6b80c1cfb0efb26~mv2.png','a81bb2_2e9df689c7d3426eb227ca4a103120b2~mv2.png'}
    photos = [x['src'] for x in s if x['t'] == 'img' and x['src'].split('/')[-1] not in icons]
    main = photos[0] if photos else ''
    gallery = photos[1:]
    mi = next(i for i, x in enumerate(s) if x['t'] == 'h3' and 'Map' in x['text'])
    ai = next(i for i, x in enumerate(s) if x['t'] == 'h4' and 'Agent' in x['text'])
    desc = [x for x in s[mi+1:ai] if x['t'] == 'p']
    agent = [x['text'] for x in s[ai+1:] if x['t'] == 'p']
    st = 'sale' if status.lower() in ('for sale',) else ''
    stats = ''.join(f'<div class="stat"><b>{E(v)}</b><span>{l}</span></div>' for v, l in [(bed,'Bedrooms'),(bath,'Bathrooms'),(size,'Land size'),(floor,'Floors'),(price,'Price')] if v)
    hero = f'<section class="hero compact" style="padding:0"><div class="bg" style="background-image:url(\'{img(main,2000)}\')"></div><div class="wrap"><div class="crumbs"><a href="/">Home</a> / Properties</div><span class="status {st}">{E(status)}</span><h1 class="mt-s">{E(title)}</h1><div class="sub">{E(kind)}</div></div></section>'
    gal = '<div class="gallery mt-m">' + ''.join(f'<a href="{img(u,1800)}" data-lb><img loading="lazy" src="{img(u,800,600)}" alt="{E(title)} photo {i+1}"></a>' for i, u in enumerate(gallery)) + '</div>'
    m = s[mi]['text']
    loc = title if title != 'Pre-Market' else 'Greenacres SA'
    body = f'''<section><div class="wrap"><div class="stats">{stats}</div>
<div class="split mt-l" style="align-items:start"><div class="prose rv"><span class="eyebrow">About this {E(kind.lower())}</span>{text_items(desc)}</div>
<div class="rv"><div class="agent"><img src="{img(ESI,200,200)}" alt="Esi Dor"><div><small style="color:var(--muted)">Call the Agent</small><h4>{E(agent[0] if agent else 'Esi Dor')}</h4><p><a href="mailto:{E(agent[1] if len(agent)>1 else 'esi@ozirealty.com.au')}">{E(agent[1] if len(agent)>1 else '')}</a><br><a href="tel:{(agent[2] if len(agent)>2 else '').replace(' ','')}">{E(agent[2] if len(agent)>2 else '')}</a></p></div></div>
<div class="media mt-m" style="aspect-ratio:4/3"><iframe title="{E(m)}" src="https://maps.google.com/maps?q={E(loc.replace(' ','%20'))}%2C%20Adelaide%20SA&z=14&output=embed" style="border:0;width:100%;height:100%" loading="lazy"></iframe></div></div></div>
<h3 class="mt-l">House Gallery</h3>{gal}</div></section>'''
    mort = DATA[key]['sections'][1]
    mimg = [x for x in mort if x['t'] == 'img']
    mp = [x['text'] for x in mort if x['t'] == 'p']
    msec = f'''<section class="alt"><div class="wrap split"><div class="prose rv"><span class="eyebrow">Finance</span><h2 class="mt-s">{E(mort[0]['text'])}</h2><p>{E(mp[0])}</p><h4 class="mt-m">{E(mort[2]['text'])}</h4><p>{E(mp[1])}</p>{btn_row([x for x in mort if x['t']=='btn'])}</div><div class="media rv"><img loading="lazy" src="{img(mimg[-1]['src'],1000,750)}" alt="Home loan advice"></div></div></section>'''
    return page(f'/properties/{slug}/', d['title'], ' '.join(x['text'] for x in desc)[:160], hero + body + msec, img(main, 1200))

# ---------------------------------------------------------------- blog
CATS = [('Property Management','property-management'),("Buyer's Agent",'buyer-s-agent'),('Appraisals & Valuations','appraisals-valuations'),('Selling Your Home','selling-your-home'),('Property Investment','property-investment'),('Suburb Insights','suburb-insights')]
CATNAMES = {n for n, _ in CATS} | {'All Posts'}
_posts = None
def post_list():
    global _posts
    if _posts is not None: return _posts
    _posts = []
    for k, p in DATA.items():
        if not k.startswith('post__'): continue
        slug = k[6:]; m = META.get(slug, {})
        items = [i for s in p['sections'] for i in s]
        h1 = next((i['text'] for i in items if i['t'] == 'h1'), p['title'])
        btns = [i['text'] for i in items if i['t'] == 'btn' and i['text'] in CATNAMES]
        cat = m.get('category') or ''  # uncategorised on the live blog: listed under All Posts only
        excerpt = p['desc'] or next((i['text'] for i in items if i['t'] == 'p' and len(i['text']) > 60), '')
        _posts.append(dict(slug=slug, title=h1, cat=cat, date=m.get('date', ''), img=p.get('og') or next((i['src'] for i in items if i['t'] == 'img'), ''), excerpt=excerpt, read=m.get('read', '')))
    return _posts

def fmt_date(d):
    try: return datetime.date.fromisoformat(d[:10]).strftime('%-d %b %Y')
    except Exception: return ''

def post_card(p):
    cslug = dict(CATS).get(p['cat'], '')
    return f'<a class="post rv" href="/post/{p["slug"]}/" data-cat="{cslug}"><div class="pm"><img loading="lazy" src="{img(p["img"],720,405)}" alt="{E(p["title"])}"></div><div class="pb"><div class="meta"><b>{E(p["cat"] or "Ozi Realty")}</b><span>{fmt_date(p["date"])}</span></div><h3>{E(p["title"])}</h3><p>{E(p["excerpt"][:150])}{"…" if len(p["excerpt"])>150 else ""}</p><span class="link-arrow mt-s">Read article {ARROW}</span></div></a>'

def blog_index(cat=None):
    posts = sorted(post_list(), key=lambda x: x['date'], reverse=True)
    name = 'All Posts'; path = '/blog/'; key = 'blog'
    if cat:
        name = next(n for n, s in CATS if s == cat); path = f'/blog/categories/{cat}/'; key = f'blog__categories__{cat}'
        posts = [p for p in posts if dict(CATS).get(p['cat']) == cat]
    chips = f'<a href="/blog/" class="{"on" if not cat else ""}">All Posts</a>' + ''.join(f'<a href="/blog/categories/{s}/" class="{"on" if s == cat else ""}">{E(n)}</a>' for n, s in CATS)
    d = DATA.get(key, {'title': f'{name} | Ozi Realty', 'desc': ''})
    hero = page_hero(name if cat else 'Blog', [{'t': 'p', 'text': 'Expert advice on Adelaide and Australian real estate: market trends, tips for buying, selling and investing, and property management insights.'}])
    body = f'<section><div class="wrap"><nav class="chipnav" aria-label="Blog categories">{chips}</nav><div class="posts">{"".join(post_card(p) for p in posts)}</div></div></section>'
    return path, page(path, d['title'], d['desc'] or DATA['blog']['desc'], hero + body)

def post_page(p):
    d = DATA['post__' + p['slug']]
    items = [i for s in d['sections'] for i in s]
    # drop category nav at the top and trailing category tag
    while items and items[0]['t'] == 'btn' and items[0]['text'] in CATNAMES: items.pop(0)
    while items and items[-1]['t'] == 'btn' and items[-1]['text'] in CATNAMES: items.pop()
    h1i = next((i for i, x in enumerate(items) if x['t'] == 'h1'), -1)
    items = items[h1i + 1:]
    stop = next((i for i, x in enumerate(items) if x['t'] in H and x['text'] in ('Recent Posts', 'See All')), len(items))
    items = items[:stop]
    out = []; ul = []
    for it in items:
        if it['t'] == 'li': ul.append(f'<li>{E(it["text"])}</li>'); continue
        if ul: out.append('<ul>' + ''.join(ul) + '</ul>'); ul = []
        t = it['t']
        if t == 'img':
            if it['src'].split('/')[-1] in (p['img'] or ''): continue
            out.append(f'<img loading="lazy" src="{img(it["src"],1400)}" alt="{E(it.get("alt") or p["title"])}">')
        elif t in ('h1', 'h2'): out.append(f'<h2>{E(it["text"])}</h2>')
        elif t in ('h3', 'h4', 'h5', 'h6'): out.append(f'<h3>{E(it["text"])}</h3>')
        elif t == 'p': out.append(f'<p>{E(it["text"])}</p>')
        elif t == 'btn' and it.get('href') and it['text'] not in CATNAMES:
            out.append(f'<p><a href="{E(link(it["href"]))}">{E(it["text"])}</a></p>')
    if ul: out.append('<ul>' + ''.join(ul) + '</ul>')
    cslug = dict(CATS).get(p['cat'], '')
    hero = f'<section class="page-hero" style="padding:0"><div class="wrap on-dark" style="max-width:900px;padding-bottom:110px"><div class="crumbs"><a href="/blog/">Blog</a>{(' / <a href="/blog/categories/' + cslug + '/">' + E(p["cat"]) + '</a>') if cslug else ''}</div><h1 style="font-size:clamp(2rem,4.2vw,3.1rem);max-width:none">{E(p["title"])}</h1><p>{fmt_date(p["date"])}{(" · " + E(p["read"]) + " min read") if p.get("read") else ""} · Ozi Realty</p></div></section>'
    himg = f'<div class="wrap" style="max-width:980px"><div class="article-hero-img"><img src="{img(p["img"],1600)}" alt="{E(p["title"])}"></div></div>' if p['img'] else ''
    related = [q for q in sorted(post_list(), key=lambda x: x['date'], reverse=True) if (q['cat'] == p['cat'] or not p['cat']) and q['slug'] != p['slug']][:3]
    rel = f'<section class="alt"><div class="wrap"><div class="sec-head"><span class="eyebrow">Keep reading</span><h2 class="mt-s">{("More in " + E(p["cat"])) if p["cat"] else "Latest articles"}</h2></div><div class="posts">{"".join(post_card(q) for q in related)}</div></div></section>' if related else ''
    body = hero + himg + f'<section style="padding-top:48px"><div class="wrap"><article class="article">{"".join(out)}</article></div></section>' + rel + cta_band()
    return page(f'/post/{p["slug"]}/', d['title'], d['desc'], body, p['img'])

def notfound():
    body = page_hero('Page not found', [{'t':'p','text':'The page you are looking for has moved. Explore our services or get in touch with the team.'}, {'t':'btn','text':'Back to Home','href':DOMAIN}, {'t':'btn','text':'Contact Us','href':DOMAIN+'/contact-adelaide-realestae-agency'}])
    return page('/404/', 'Page not found | Ozi Realty', '', body)


# ---------------------------------------------------------------- properties list / search / booking calendar / redirects
def prop_summary(k):
    s = DATA[k]['sections'][0]
    ps = [x['text'] for x in s if x['t'] == 'p']
    after = lambda l: ps[ps.index(l) + 1] if l in ps and ps.index(l) + 1 < len(ps) else ''
    return dict(slug=k.split('__')[1], title=s[0]['text'], kind=s[1]['text'], status=s[2]['text'],
                bed=after('Bedroom'), bath=after('Bathroom'), size=next((p for p in ps if 'm²' in p), ''), price=after('Price'))

def properties_list():
    d = DATA['properties']; items = d['sections'][0]
    cards = []
    for i, it in enumerate(items):
        if it['t'] != 'img': continue
        h = items[i + 1]['text']; b = next(x for x in items[i:] if x['t'] == 'btn')
        slug = link(b['href']).strip('/').split('/')[-1]
        info = prop_summary('properties__' + slug)
        st = ' sale' if info['status'].lower() == 'for sale' else ''
        meta = ' · '.join(x for x in [info['bed'] and info['bed'] + ' bed', info['bath'] and info['bath'] + ' bath', info['size']] if x)
        cards.append(f'<a class="post rv" href="/properties/{slug}/"><div class="pm" style="position:relative"><img loading="lazy" src="{img(it["src"],800,450)}" alt="{E(h)}"><span class="status{st}" style="position:absolute;top:14px;left:14px">{E(info["status"])}</span></div><div class="pb"><div class="meta"><b>{E(info["kind"])}</b><span>{E(info["price"])}</span></div><h3>{E(h)}</h3><p>{E(meta)}</p><p class="mt-s">Agent: Esi Dor · esi@ozirealty.com.au</p><span class="link-arrow mt-s">Read More {ARROW}</span></div></a>')
    hero = page_hero('Properties List', [{'t': 'p', 'text': 'Homes listed, leased and sold by Ozi Realty across Adelaide.'}])
    body = f'<section><div class="wrap"><div class="posts">{"".join(cards)}</div></div></section>' + cta_band()
    return page('/properties/', d['title'], 'Properties listed, leased and sold by Ozi Realty in Adelaide.', hero + body)

def search_page():
    hero = page_hero('Search Results', [{'t': 'p', 'text': 'Search this site'}])
    body = """<section><div class="wrap" style="max-width:900px"><form class="searchbar" role="search" onsubmit="return false"><input id="q" type="search" placeholder="Search pages, services and articles…" aria-label="Site search" autocomplete="off"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg></form><p id="search-count" class="mt-m"></p><div id="search-results" class="search-results"></div></div></section>"""
    return page('/search/', 'Search Results | Ozi Realty', 'Search the Ozi Realty website.', hero + body)

def booking_calendar():
    d = DATA['booking-calendar__real-estate-consultation']; s = d['sections'][0]
    hero = page_hero(s[0]['text'], [{'t': 'p', 'text': s[1]['text']}])
    form = f'<form class="form-card" data-form="booking" data-form-id="{E(FORM_IDS.get("booking", ""))}" data-to="support@ozirealty.com.au" novalidate><h3>Request a time</h3><p>{E(s[2]["text"])}</p><div class="form-grid"><div class="fld"><label for="c_name">Full name <span style="color:var(--red)">*</span></label><input id="c_name" name="first_name" required autocomplete="name"></div><div class="fld"><label for="c_phone">Phone <span style="color:var(--red)">*</span></label><input id="c_phone" name="phone" type="tel" required></div><div class="fld"><label for="c_email">Email <span style="color:var(--red)">*</span></label><input id="c_email" name="email" type="email" required></div><div class="fld"><label for="c_date">Preferred date</label><input id="c_date" name="preferred_date" type="date"></div><div class="fld full"><label for="c_msg">What would you like to discuss?</label><textarea id="c_msg" name="message"></textarea></div></div><button class="btn btn-primary" type="submit">Request to Book {ARROW}</button><p class="consent">By submitting this form, you acknowledge that you have read and understood our <a href="https://www.prospectbc.com.au/privacy-policy" target="_blank" rel="noopener">Privacy Policy</a>, and consent to us collecting, using, and processing the personal information you provide in accordance with that policy.*</p><div class="form-ok" role="status"></div></form>'
    side = f'<div class="prose rv"><span class="eyebrow">Real Estate Consultation</span><h2 class="mt-s">Expert property advice with Esi Dor</h2><div class="stats mt-m"><div class="stat"><b>30 min</b><span>Duration</span></div><div class="stat"><b>Online</b><span>Available</span></div><div class="stat"><b>Free</b><span>No obligation</span></div></div><div class="agent mt-m"><img src="{img(ESI,200,200)}" alt="Esi Dor"><div><small style="color:var(--muted)">Principal · RLA 350 628</small><h4>Esi Dor</h4><p>308 Prospect Road, Prospect SA · 1800 400 333</p></div></div></div>'
    body = f'<section><div class="wrap split" style="align-items:start">{side}<div class="rv">{form}</div></div></section>'
    return page('/booking-calendar/real-estate-consultation/', d['title'], 'Schedule a real estate consultation with Esi Dor, Principal of OziRealty.', hero + body)

def redirect_page(to):
    return f'<!doctype html><html lang="en-AU"><head><meta charset="utf-8"><title>Redirecting…</title><link rel="canonical" href="{DOMAIN}{to.rstrip("/")}"><meta http-equiv="refresh" content="0; url={to}"><meta name="robots" content="noindex"></head><body><p><a href="{to}">Continue</a></p><script>location.replace({json.dumps(to)} + location.hash)</script></body></html>'

def search_index():
    idx = []
    for path, fp in walk_pages():
        h = open(fp).read()
        t = re.search(r'<title>(.*?)</title>', h, re.S); dsc = re.search(r'<meta name="description" content="(.*?)"', h)
        main = re.search(r'<main>(.*)</main>', h, re.S)
        txt = re.sub(r'<[^>]+>', ' ', main.group(1) if main else '')
        txt = html.unescape(re.sub(r'\s+', ' ', txt)).strip()
        idx.append({'u': path, 't': html.unescape(t.group(1)).split(' | ')[0] if t else path, 'd': html.unescape(dsc.group(1)) if dsc else '', 'x': txt[:1800]})
    json.dump(idx, open(os.path.join(OUT, 'assets', 'search-index.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
    return len(idx)

def walk_pages():
    for root, _, files in os.walk(OUT):
        for fn in files:
            if not fn.endswith('.html') or fn == '404.html': continue
            fp = os.path.join(root, fn)
            if 'http-equiv="refresh"' in open(fp).read(400): continue
            rel = os.path.relpath(fp, OUT)
            yield ('/' if rel == 'index.html' else '/' + rel), fp

# ---------------------------------------------------------------- write
# Wix headless hosting serves exact file names only (/about.html works, /about and /about/ 404),
# so every internal page link points at its .html file.
CLEAN = re.compile(r'((?:href|content)="|url=|location\.replace\(")(/[A-Za-z0-9_/-]*[A-Za-z0-9_-])/?(?=["#?])')
def clean_urls(html_):
    return CLEAN.sub(lambda m: m.group(1) + m.group(2) + ('' if m.group(2).startswith('/assets') else '.html'), html_)

def page_url(path):
    return '/' if path == '/' else '/' + path.strip('/') + '.html'

def write(path, content):
    content = clean_urls(content)
    fp = os.path.join(OUT, 'index.html') if path == '/' else os.path.join(OUT, path.strip('/') + '.html')
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    open(fp, 'w').write(content)

def main():
    for d in os.listdir(OUT):
        if d != 'assets': shutil.rmtree(os.path.join(OUT, d)) if os.path.isdir(os.path.join(OUT, d)) else os.remove(os.path.join(OUT, d))
    bespoke = {
        'index': ('/', home), 'property-services': ('/property-services/', services),
        'property-strategy-services': ('/property-strategy-services/', strategy),
        'manage-property-adelaide': ('/manage-property-adelaide/', manage),
        'about-adelaide-land-agent': ('/about-adelaide-land-agent/', about),
        'contact-adelaide-realestae-agency': ('/contact-adelaide-realestae-agency/', contact),
        'realestate-gift-adelaide': ('/realestate-gift-adelaide/', gift),
        'oversees-investment': ('/oversees-investment/', oversea),
        'book-online': ('/book-online/', book_online),
    }
    n = 0
    for k in DATA:
        if k.startswith(('post__', 'blog', 'properties')) or k in ('buy-property-adelaide', 'search', 'booking-calendar__real-estate-consultation'): continue
        if k in bespoke: path, fn = bespoke[k]; write(path, fn())
        elif k == 'service-page__real-estate-consultation': write('/service-page/real-estate-consultation/', book_online(k, '/service-page/real-estate-consultation/'))
        else: path = '/' + k.replace('__', '/') + '/'; write(path, generic_page(k, path))
        n += 1
    for k in DATA:
        if k.startswith('properties__'): write(f'/properties/{k.split("__")[1]}/', property_page(k)); n += 1
    path, html_ = blog_index(); write(path, html_); n += 1
    for _, c in CATS: path, html_ = blog_index(c); write(path, html_); n += 1
    for p in post_list(): write(f'/post/{p["slug"]}/', post_page(p)); n += 1
    open(os.path.join(OUT, '404.html'), 'w').write(clean_urls(notfound())); n += 1
    write('/properties/', properties_list()); write('/search/', search_page())
    write('/booking-calendar/real-estate-consultation/', booking_calendar()); n += 3
    # short URLs the live site redirects, plus paginated blog URLs
    for src, dst in [('/free-appraisal/', '/free-property-appraisal-sa/'), ('/manage-property/', '/manage-property-adelaide/'),
                     ('/about/', '/about-adelaide-land-agent/')] + [(f'/blog/page/{i}/', '/blog/') for i in range(2, 6)]:
        write(src, redirect_page(dst))
    print('search index:', search_index())
    SPECS['booking'] = {'name': 'Free Meeting: Real Estate Consultation', 'fields': [
        {'target': 'first_name', 'label': 'Full name', 'kind': 'text', 'req': True},
        {'target': 'phone', 'label': 'Phone', 'kind': 'tel', 'req': True},
        {'target': 'email', 'label': 'Email', 'kind': 'email', 'req': True},
        {'target': 'preferred_date', 'label': 'Preferred date', 'kind': 'date', 'req': False},
        {'target': 'message', 'label': 'What would you like to discuss?', 'kind': 'textarea', 'req': False}]}
    json.dump(SPECS, open(os.path.join(ROOT, 'content', 'forms-spec.json'), 'w'), indent=1, ensure_ascii=False)
    print('pages:', n, 'forms:', len(SPECS))

if __name__ == '__main__':
    main()
