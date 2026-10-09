#!/usr/bin/env python3
"""Pull publish date, category and read time for each blog post from the raw live HTML."""
import sys, os, re, json, collections
raw = sys.argv[1]; out = {}
CAT = {'property-management':'Property Management','buyer-s-agent':"Buyer's Agent",'appraisals-valuations':'Appraisals & Valuations','selling-your-home':'Selling Your Home','property-investment':'Property Investment','suburb-insights':'Suburb Insights'}
for f in os.listdir(raw):
    if not f.startswith('post__'): continue
    h = open(os.path.join(raw, f)).read()
    m = re.search(r'article:published_time" content="([^"]+)', h)
    cats = collections.Counter(re.findall(r'blog/categories/([a-z-]+)', h))
    top = [c for c, n in cats.items() if n > 1]
    r = re.search(r'"timeToRead":(\d+)', h) or re.search(r'(\d+) min read', h)
    out[f[6:-5]] = {'date': m.group(1) if m else '', 'category': CAT.get(top[0]) if top else None, 'read': r.group(1) if r else ''}
json.dump(out, open(sys.argv[2], 'w'), indent=1)
print(len(out), collections.Counter(v['category'] for v in out.values()))
