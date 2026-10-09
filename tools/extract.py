import sys,os,json,re,bs4
from bs4 import Tag
raw=sys.argv[1]; out={}
def clean(t): return ' '.join(t.split()).replace('​','').strip()
def imgsrc(i):
    src=i.get('src') or ''
    m=re.search(r'static\.wixstatic\.com/media/([^/?]+)',src)
    return 'https://static.wixstatic.com/media/'+m.group(1) if m else None
def lbl(s,el):
    lb=el.get('aria-labelledby')
    if lb:
        e=s.find(id=lb.split()[0])
        if e: return clean(e.get_text(' '))
    if el.get('id'):
        e=s.find('label',attrs={'for':el['id']})
        if e: return clean(e.get_text(' '))
    return clean(el.get('aria-label') or el.get('placeholder') or el.get('name') or '')
def form(s,f):
    fields=[];submit=None;consent=''
    done=set()
    for el in f.find_all(['fieldset','input','textarea','button','p']):
        if any(id(p) in done for p in el.parents): continue
        if el.name=='fieldset':
            if not el.get('aria-labelledby') or el.find('input',type=lambda t:t not in('radio','checkbox')): continue
            done.add(id(el))
            q=lbl(s,el); opts=[]; typ='radio'
            for i in el.find_all('input'):
                if i.get('type') in('radio','checkbox'):
                    typ=i['type']; L=i.find_parent('label'); opts.append(clean(i.get('aria-label') or i.get('value') or (L.get_text(' ') if L else '')))
            if not q:
                # checkbox group w/o fieldset label: try name
                q=clean(el.get_text(' '))[:80]
            if opts: fields.append({'k':typ,'label':q,'opts':opts})
            elif q: 
                i=el.find('input'); fields.append({'k':(i.get('type') if i else 'text'),'label':q})
        elif el.name=='input':
            t=el.get('type','text')
            if t in('hidden','radio','checkbox','submit'): 
                if t=='checkbox': fields.append({'k':'checkbox','label':'','opts':[lbl(s,el)],'req':el.has_attr('required')})
                continue
            fields.append({'k':t,'label':lbl(s,el),'req':el.has_attr('required')})
        elif el.name=='textarea':
            fields.append({'k':'textarea','label':lbl(s,el),'req':el.has_attr('required')})
        elif el.name=='button':
            if el.get('role')=='combobox' or el.get('aria-haspopup'):
                fields.append({'k':'select','label':clean(el.get('aria-label') or el.get_text(' '))}); done.add(id(el))
            elif el.get('type')=='submit' or 'submit' in str(el.get('data-hook')):
                submit=clean(el.get_text(' '))
        elif el.name=='p':
            t=clean(el.get_text(' '))
            if t.startswith('By submitting'): consent=t
    # merge consecutive single checkboxes w/ same group: leave
    return {'t':'form','fields':fields,'submit':submit or 'Submit','consent':consent}
def walk(s,el,items,seen):
    for c in el.children:
        if not isinstance(c,Tag): continue
        n=c.name
        if n in('script','style','svg','noscript'): continue
        if n=='form': items.append(form(s,c)); continue
        if n=='img':
            u=imgsrc(c)
            if u and u not in seen: seen.add(u); items.append({'t':'img','src':u,'alt':c.get('alt','')})
            continue
        if n in('h1','h2','h3','h4','h5','h6','p','li') :
            # li containing headings/links -> recurse
            if n=='li' and c.find(['h1','h2','h3','h4','img','a','button']): walk(s,c,items,seen); continue
            t=clean(c.get_text(' '))
            a=c.find('a')
            if t: items.append({'t':n,'text':t, **({'href':a.get('href')} if a and a.get('href') and clean(a.get_text())==t else {})})
            continue
        if n=='button' and c.get('aria-expanded') is not None:
            t=clean(c.get_text(' '))
            if t: items.append({'t':'q','text':t})
            continue
        if n in('a','button'):
            t=clean(c.get_text(' '))
            if c.find(['h1','h2','h3','h4','h5','h6','p','img']): walk(s,c,items,seen)
            elif t and len(t)<70: items.append({'t':'btn','text':t,'href':c.get('href')})
            continue
        if n=='iframe':
            items.append({'t':'iframe','src':c.get('src') or c.get('data-src'),'title':c.get('title','')}); continue
        walk(s,c,items,seen)
for f in sorted(os.listdir(raw)):
    s=bs4.BeautifulSoup(open(os.path.join(raw,f)).read(),'lxml')
    title=clean(s.title.get_text()) if s.title else ''
    md=s.find('meta',attrs={'name':'description'})
    main=s.select_one('#PAGES_CONTAINER') or s.body
    secs=main.select('section.wixui-section') or [main]
    page=[]
    for sec in secs:
        items=[]; walk(s,sec,items,set())
        ded=[]
        for it in items:
            if ded and ded[-1]==it: continue
            if ded and it['t'].startswith('h') and ded[-1]['t']=='li' and ded[-1]['text']==it.get('text'): ded[-1]=it; continue
            ded.append(it)
        if ded: page.append(ded)
    og=s.find('meta',attrs={'property':'og:image'})
    out[f[:-5]]={'title':title,'desc':md.get('content') if md else '','og':og.get('content') if og else '','sections':page}
json.dump(out,open(sys.argv[2],'w'),indent=1,ensure_ascii=False)
print(len(out))
