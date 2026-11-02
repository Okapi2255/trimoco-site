import re, json, os, glob, html, shutil
from content import AREAS, SERVICES, LICENSE
ROOT='/workspace/trimoco-site'; SRC=ROOT+'/_orig/mirror'; OUT=ROOT+'/public'
BASE='https://www.trimoco.com'
GMAPS='https://www.google.com/maps/place/?q=place_id:ChIJ__8beJpkwokRkhfKdrDJYuM'
css1=open(SRC+'/_astro/Footer.Bc5uZAL2.css').read(); css2=open(SRC+'/_astro/index@_@astro.Cng6o1fU.css').read()
fonts=open(OUT+'/fonts/fonts.css').read().replace('\n','')
esc=html.escape

def resolve_img(p):
    if p.endswith('-placeholder'):
        pre=p.replace('-placeholder','')
        return '/'+os.path.relpath(glob.glob(OUT+pre+'*')[0],OUT)
    return p

def trim_desc(d,limit=158):
    d=html.unescape(d).strip()
    if len(d)<=limit: return d
    parts=re.split(r'(?<=[.!?])\s+',d); out=''
    for p in parts:
        if len(out)+len(p)+1>limit: break
        out=(out+' '+p).strip()
    return out or d[:limit].rsplit(' ',1)[0]

PAGE_META={
 '': ('Manhattan General Contractor & Renovations | Trimoco LLC',
      'Kitchen, bathroom and gut renovations in Manhattan, the Hamptons, Brooklyn, Queens, the Bronx and Long Island. NYC licensed. Free estimates: (516) 787-1045.'),
 'areas/manhattan-ny': ('Manhattan Contractor: Co-op & Condo Renovations | Trimoco LLC','Manhattan co-op, condo and brownstone renovations: kitchens, bathrooms, gut renovations. Alteration agreements and COIs handled. (516) 787-1045.'),
 'areas/brooklyn-ny': (None,'Brooklyn brownstone, row house and co-op renovations: kitchens, bathrooms, plaster, trim and flooring. Free estimates: (516) 787-1045.'),
 'areas/queens-ny': (None,'Kitchen, bathroom and whole-home renovations for Queens houses, co-ops and condos. Free estimates from Trimoco LLC: (516) 787-1045.'),
 'areas/bronx-ny': (None,'Kitchen, bathroom, plaster and flooring renovations for Bronx co-ops, condos and homes. Free estimates from Trimoco LLC: (516) 787-1045.'),
 'areas/long-island-ny': ('General Contractor in Long Island & Nassau County | Trimoco LLC','Farmingdale-based general contractor for Nassau County and Long Island: kitchens, bathrooms, gut renovations, roofing. Free estimates: (516) 787-1045.'),
 'about': (None,'Trimoco LLC is a Farmingdale, NY general contractor serving Manhattan, Brooklyn, Queens, the Bronx and Long Island since 2021. Call (516) 787-1045.'),
 'projects': ('Renovation Projects in NYC & Long Island | Trimoco LLC',None),
}
NOINDEX={'thank-you','marketing-form','discount','review','blog'}

FORM_PATCH_OLD='await fetch(o,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({placeId:s,answers:m,botTrap:k})})'
FORM_PATCH_NEW='k||await window.trimocoSubmit(m,"Quote form")'
CHAT_RE=re.compile(r"await fetch\(chatWidgetSubmitUrl, \{.*?\}\),\s*\}\);",re.S)

def fix_reviews(s):
    # Owner confirmed (Nov 2, 2026) the 3 Google reviews and 5.0 rating are real: keep them exactly as on the original.
    # No Review/AggregateRating schema (Google ignores self-serving LocalBusiness review stars).
    s=s.replace('What Nassau County homeowners <em class="italic text-accent">say.</em>','What our clients <em class="italic text-accent">say.</em>')
    s=s.replace('<span class="text-sm text-text-secondary">3 Google reviews</span>','<a href="'+GMAPS+'" target="_blank" rel="noopener" class="text-sm text-text-secondary underline underline-offset-2 hover:text-accent">3 Google reviews</a>')
    s=s.replace(' aria-label="Top-rated by local clients — jump to client reviews"','')
    return s

def fix_hours(s):
    # Owner: Mon-Sat 8:00 AM - 6:00 PM, Sunday closed (matches Google Business Profile)
    H='8:00 AM - 6:00 PM'
    # footer dl: Mon – Fri row -> Mon – Sat, drop Saturday row
    s=re.sub(r'(<dt class="text-text-on-dark-muted">)Mon – Fri(</dt> <dd class="text-text-footer m-0">)9:00 AM - 5:00 PM(</dd> </div>) <div class="flex justify-between gap-4 text-\[0\.8125rem\]"> <dt class="text-text-on-dark-muted">Saturday</dt> <dd class="text-text-footer m-0">9:00 AM - 2:00 PM</dd> </div>',r'\1Mon – Sat\g<2>'+H+r'\3',s)
    # contact page dl
    s=re.sub(r'(<dt class="text-text-secondary">)Monday – Friday(</dt> <dd class="text-text font-medium m-0">)9:00 AM - 5:00 PM(</dd> </div>) <div class="flex justify-between text-sm"> <dt class="text-text-secondary">Saturday</dt> <dd class="text-text font-medium m-0">9:00 AM - 2:00 PM</dd> </div>',r'\1Monday – Saturday\g<2>'+H+r'\3',s)
    s=s.replace('Mon–Fri 9:00 AM - 5:00 PM · Sat 9:00 AM - 2:00 PM','Mon–Sat '+H)
    s=s.replace('Monday through Friday, 9 AM to 5 PM, and Saturdays from 9 AM to 2 PM','Monday through Saturday, 8 AM to 6 PM')
    # per-day lists
    s=s.replace('9:00 AM - 5:00 PM',H).replace('9:00 AM - 2:00 PM',H)
    s=s.replace('"openingHoursSpecification":[{"@type":"OpeningHoursSpecification","dayOfWeek":["Monday","Tuesday","Wednesday","Thursday","Friday"],"opens":"09:00","closes":"17:00"},{"@type":"OpeningHoursSpecification","dayOfWeek":"Saturday","opens":"09:00","closes":"14:00"}]',
                '"openingHoursSpecification":[{"@type":"OpeningHoursSpecification","dayOfWeek":["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],"opens":"08:00","closes":"18:00"}]')
    return s

def faq_html(faqs,prefix):
    out=''
    for n,(q,a) in enumerate(faqs):
        fid=f'faq-{prefix}{n}'
        out+=(f'<div class="faq-item"> <button class="faq-trigger" aria-expanded="false" aria-controls="{fid}"> <span>{esc(q)}</span> '
              '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="faq-icon" aria-hidden="true"><polyline points="6 9 12 15 18 9"></polyline></svg> '
              f'</button> <div class="faq-content" id="{fid}" role="region" aria-labelledby="{fid}"> <p>{esc(a)}</p> </div> </div>')
    return out

def add_faqs(s,faqs,prefix):
    # visible
    k=s.find('id="faq"')
    if k<0: return s
    anchor='<div class="md:col-start-2 border-t border-border reveal" style="transition-delay: 100ms;">'
    a=s.find(anchor,k)
    if a<0: return s
    a+=len(anchor); s=s[:a]+' '+faq_html(faqs,prefix)+s[a:]
    # JSON-LD
    def upd(m):
        d=json.loads(m.group(1))
        if d.get('@type')=='FAQPage':
            d['mainEntity']=[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faqs]+d['mainEntity']
        return '<script type="application/ld+json">'+json.dumps(d,ensure_ascii=False)+'</script>'
    return re.sub(r'<script type="application/ld\+json">(.*?)</script>',upd,s,flags=re.S)

CHECK='<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="text-accent shrink-0 mt-[3px]" aria-hidden="true"><polyline points="20 6 9 17 4 12"></polyline></svg>'
def area_section(a):
    paras=''.join(f'<p class="text-base text-text-secondary leading-[1.75]">{esc(p)}</p>' for p in a['paras'])
    bullets=''.join(f'<li class="flex items-start gap-3 text-[0.9375rem] text-text-secondary">{CHECK} {esc(b)}</li>' for b in a['bullets'])
    hoods=''.join(f'<li class="badge">{esc(h)}</li>' for h in a['hoods'])
    return f'''<!-- ─── LOCAL GUIDE (added for SEO) ─── --> <section class="section-pad bg-surface" aria-labelledby="area-guide-heading"> <div class="container-site"> <div class="max-w-[820px] reveal"> <span class="section-label">{esc(a['label'])}</span> <h2 id="area-guide-heading" class="font-heading text-[clamp(1.75rem,_4vw,_2.5rem)] font-bold mb-3">{esc(a['h2'])}</h2> <span class="accent-bar"></span> <div class="mt-6 flex flex-col gap-4 mb-8">{paras}</div> <div class="flex flex-col gap-3 mb-8 p-5 bg-surface-raised border border-border rounded-xl"> <h3 class="text-[1.0625rem] font-bold m-0">{esc(a['list_title'])}</h3> <ul class="list-none m-0 p-0 flex flex-col gap-2.5" role="list">{bullets}</ul> </div> <h3 class="text-[1.0625rem] font-bold mb-3">{esc(a['hoods_title'])}</h3> <ul class="list-none m-0 p-0 flex flex-wrap gap-2" role="list">{hoods}</ul> <p class="text-sm text-text-muted mt-6">{LICENSE}.</p> </div> </div> </section> '''

def guide_section(g,related=()):
    # g: dict(label,h2,paras[html, trusted, ours],list_title,bullets); related: project slugs (real, owner-confirmed)
    # class before href on purpose: keeps sitewide_hamptons from inserting a hub link before our East Hampton link
    paras=''.join(f'<p class="text-base text-text-secondary leading-[1.75]">{p}</p>' for p in g['paras']).replace('<a href=','<a class="text-accent font-medium underline underline-offset-2" href=')
    bullets=''.join(f'<li class="flex items-start gap-3 text-[0.9375rem] text-text-secondary">{CHECK} {esc(b)}</li>' for b in g['bullets'])
    rel=''
    if related:
        G={x['slug']:x for x in json.load(open(ROOT+'/build/project-groups.json'))}
        cards=''
        for sl in related:
            if sl not in G: continue
            x=G[sl]; loc,_,ttl=x['title'].partition(': ')
            cards+=(f'<a href="/projects/{sl}/" class="card group flex flex-col no-underline overflow-hidden"><div class="relative aspect-[4/3] overflow-hidden"><img src="/images/projects/{x["photos"][0]}" alt="{esc(ttl or loc)}, {esc(loc)}" width="400" height="300" loading="lazy" decoding="async" class="h-full w-full object-cover transition-transform duration-500 group-hover:scale-[1.04]"></div>'
                    f'<div class="px-4 py-3 flex flex-col gap-1"><span class="text-xs text-text-muted">{esc(loc)}</span><span class="text-[0.9375rem] font-semibold text-text leading-snug group-hover:text-accent">{esc(ttl or loc)}</span></div></a>')
        rel=(f'<h3 class="text-[1.0625rem] font-bold mb-2">Recent projects</h3><p class="text-sm text-text-muted mb-4">Photos from our project gallery. <a href="/projects/" class="text-accent underline underline-offset-2">See all projects</a></p>'
             f'<div class="grid grid-cols-2 lg:grid-cols-4 gap-4">{cards}</div>')
    return (f'<!-- ─── SERVICE GUIDE (added for SEO) ─── --> <section class="section-pad bg-surface" aria-labelledby="svc-guide-heading"> <div class="container-site"> <div class="max-w-[820px] reveal"> <span class="section-label">{esc(g["label"])}</span> '
            f'<h2 id="svc-guide-heading" class="font-heading text-[clamp(1.75rem,_4vw,_2.5rem)] font-bold mb-3">{esc(g["h2"])}</h2> <span class="accent-bar"></span> <div class="mt-6 flex flex-col gap-4 mb-8">{paras}</div> '
            f'<div class="flex flex-col gap-3 mb-10 p-5 bg-surface-raised border border-border rounded-xl"> <h3 class="text-[1.0625rem] font-bold m-0">{esc(g["list_title"])}</h3> <ul class="list-none m-0 p-0 flex flex-col gap-2.5" role="list">{bullets}</ul> </div> </div> {rel} '
            f'<p class="text-sm text-text-muted mt-6">{LICENSE}. Based in Farmingdale, NY.</p> </div> </section> ')

EXTRA_LINKS=[('/services/general-contractor/co-op-condo-renovation/','Co-op & Condo Renovation'),('/services/general-contractor/flooring-installation/','Flooring Installation'),('/services/general-contractor/tile-installation/','Tile Installation'),('/services/general-contractor/interior-painting/','Interior Painting'),('/services/general-contractor/plaster-and-skim-coating/','Plaster & Skim Coating'),('/services/carpenter/drywall-and-framing/','Drywall Installation & Repair'),('/services/general-contractor/roofing/','Roofing')]

def common(s,path):
    url=BASE+'/'+(path+'/' if path else '')
    # CSS inline + fonts
    s=re.sub(r'<link rel="preconnect" href="https://fonts\.g[^>]*>\s*','',s)
    s=re.sub(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com[^>]*>','<link rel="preload" href="/fonts/dmsans.woff2" as="font" type="font/woff2" crossorigin><link rel="preload" href="/fonts/playfair.woff2" as="font" type="font/woff2" crossorigin><style>'+fonts+'</style>',s)
    s=s.replace('<link rel="stylesheet" href="/_astro/Footer.Bc5uZAL2.css">','<style>'+css1+'</style>')
    s=s.replace('<link rel="stylesheet" href="/_astro/index@_@astro.Cng6o1fU.css">','<style>'+css2+'</style>')
    s=re.sub(r'@import\s*"https://fonts\.googleapis\.com[^"]*";?','',s)
    s=s.replace('<link rel="icon" type="image/svg+xml" href="/favicon.svg">','<link rel="icon" type="image/png" sizes="48x48" href="/favicon-48.png">')
    # logo -> webp
    s=s.replace('src="/images/logo.png"','src="/images/logo.webp"')
    s=s.replace('<img src="/images/logo.webp" alt=""','<img src="/images/logo.webp" alt="Trimoco LLC"')
    # canonical / og
    s=re.sub(r'<link rel="canonical" href="[^"]*">',f'<link rel="canonical" href="{url}">',s)
    s=re.sub(r'<meta property="og:url" content="[^"]*">',f'<meta property="og:url" content="{url}">',s)
    s=s.replace('content="/images/og-home.webp"',f'content="{BASE}/images/og-home.jpg"')
    # facts
    s=s.replace('11653','11563')
    s=s.replace('"latitude":40.654823,"longitude":-73.671799','"latitude":40.66296,"longitude":-73.68539')
    s=s.replace('across the panhandle','across NYC and Long Island')
    s=s.replace('20+ Years Building Trust','Serving NYC &amp; Long Island Since 2021')
    s=s.replace('>24/7 Emergency Service<','>Clean Job Sites<')
    s=s.replace('Emergency response available 24/7','Free on-site estimates')
    s=s.replace('Get a clear roof assessment before you commit.','Get a clear assessment before you commit.')
    s=re.sub(r'(<p class="[^"]*">Since 2021</p> <p class="[^"]*">)Years(\s*<br>\s*)?Experience',r'\1Serving\2Clients',s)
    # internal links: trailing slash
    s=re.sub(r'href="(/(?:services|areas|about|contact|projects|privacy|terms|review|blog|discount)[^"#?]*?)(?<!/)"',r'href="\1/"',s)
    # map embed without third-party API key
    s=re.sub(r'<iframe src="https://www\.google\.com/maps/embed/v1/place\?[^"]*"','<iframe src="https://maps.google.com/maps?q=Farmingdale,+NY+11735&amp;output=embed"',s)
    # forms
    s=s.replace('data-submit-url="https://api.stonesystems.io/public-forms/submit"','data-submit-url="local"')
    s=s.replace(FORM_PATCH_OLD,FORM_PATCH_NEW)
    s=CHAT_RE.sub('await window.trimocoSubmit({name,phone,message},"Chat widget");',s)
    s=s.replace('const chatWidgetSubmitUrl = "https://api.stonesystems.io/customers/websites/chat-widget";','')
    s=s.replace('</head>','<script src="/js/forms.js" defer></script></head>',1)
    # reviews
    s=fix_reviews(s)
    s=fix_hours(s)
    # footer: license + extra service links
    extra=' · '.join(f'<a href="{u}" class="hover:text-accent">{n}</a>' for u,n in EXTRA_LINKS)
    s=s.replace('&copy; 2026 Trimoco LLC. All rights reserved.',f'&copy; 2026 Trimoco LLC. All rights reserved. {LICENSE}.</p><p class="text-xs mt-2">More services: {extra}',1)
    # JSON-LD business: credential, url
    def upd(m):
        d=json.loads(m.group(1))
        if isinstance(d.get('@type'),list) and 'GeneralContractor' in d['@type']:
            d['url']=BASE+'/'
            d['image']=BASE+'/images/og-home.jpg'; d['logo']=BASE+'/images/logo.png'
            d['hasCredential']={"@type":"EducationalOccupationalCredential","credentialCategory":"license","name":"NYC Home Improvement Contractor License","identifier":"2114773-DCA","recognizedBy":{"@type":"GovernmentOrganization","name":"NYC Department of Consumer and Worker Protection"}}
            names=[a['name'] for a in d.get('areaServed',[])]
            d['areaServed']=[a for a in d['areaServed'] if a['name'] not in ('East Hamptons, NY','West Hamptons, NY')]+[{"@type":"Place","name":n} for n in ['The Hamptons, NY','East Hampton, NY','Westhampton, NY','Westhampton Beach, NY','Southampton, NY'] if n not in names]
            if 'Nassau County, NY' not in names: d['areaServed'].append({"@type":"AdministrativeArea","name":"Nassau County, NY"})
            d['description']=d['description'].replace('Manhattan, Brooklyn, Queens, Long Island','Manhattan, Brooklyn, Queens, the Bronx, Long Island')
            # TODO(owner): add "sameAs": [Google Business Profile URL, Facebook, Instagram, Houzz, Yelp]
        elif isinstance(d.get('areaServed'),list) and any(a.get('name')=='East Hamptons, NY' for a in d['areaServed']):
            d['areaServed']=[a for a in d['areaServed'] if a['name'] not in ('East Hamptons, NY','West Hamptons, NY')]+[{"@type":"Place","name":n} for n in ['The Hamptons, NY','East Hampton, NY','Westhampton, NY','Westhampton Beach, NY','Southampton, NY']]
        return '<script type="application/ld+json">'+json.dumps(d,ensure_ascii=False)+'</script>'
    s=re.sub(r'<script type="application/ld\+json">(.*?)</script>',upd,s,flags=re.S)
    s=re.sub(r'("item":"https://www\.trimoco\.com/[^"]*?)(?<!/)"',r'\1/"',s)
    # meta
    t,d=PAGE_META.get(path,(None,None))
    if t: s=re.sub(r'<title>.*?</title>',f'<title>{esc(t)}</title>',s,flags=re.S); s=re.sub(r'(<meta (?:property="og:title"|name="twitter:title") content=")[^"]*',lambda m:m.group(1)+esc(t),s)
    cur=re.search(r'<meta name="description" content="([^"]*)"',s)
    if cur:
        nd=d or trim_desc(cur.group(1))
        s=re.sub(r'(<meta (?:name="description"|property="og:description"|name="twitter:description") content=")[^"]*',lambda m:m.group(1)+esc(nd),s)
    if path.split('/')[0] in NOINDEX and path:
        s=s.replace('<meta charset="UTF-8">','<meta charset="UTF-8"><meta name="robots" content="noindex, follow">',1)
    return s

def write(path,s):
    fn=OUT+('/'+path if path else '')+'/index.html'
    os.makedirs(os.path.dirname(fn),exist_ok=True); open(fn,'w').write(s)

pages=[]
for f in glob.glob(SRC+'/**/index.html',recursive=True):
    path=os.path.relpath(os.path.dirname(f),SRC); path='' if path=='.' else path
    s=open(f).read()
    if path=='':
        s=s.replace('Serving <span class="capitalize">Long Island</span>','Serving <span class="capitalize">NYC &amp; Long Island</span>')
        s=s.replace('Services Across\nLong Island','Services Across\nNYC &amp; Long Island')
        s=s.replace('Based in Lynbrook — serving every corner of Long Island.','Based in Farmingdale — serving Manhattan, Brooklyn, Queens, the Bronx and Long Island.')
    slug=path.split('/')[-1]
    if path in ('areas/east-hamptons-ny','areas/west-hamptons-ny'): continue  # replaced by /areas/east-hampton/ and /areas/westhampton/ (301)
    if path.startswith('areas/') and slug in AREAS:
        a=AREAS[slug]
        s=s.replace('<!-- ─── SERVICES ──',area_section(a)+'<!-- ─── SERVICES ──',1)
        s=add_faqs(s,a['faqs'],'a')
    s=common(s,path); write(path,s)
    if path.split('/')[0] not in NOINDEX: pages.append(path)

# ---- Hamptons pages
exec(open(ROOT+'/build/hamptons.py').read(),globals())

# ---- new service pages, cloned from kitchen-renovation
tpl=open(SRC+'/services/general-contractor/kitchen-renovation/index.html').read()
k_h1='<span class="capitalize">Kitchen Renovation</span> in Manhattan, NY'
k_lead=re.search(r'(<p class="text-\[1\.0625rem\] text-text-on-dark[^>]*>)(.*?)(</p>)',tpl,re.S)
k_body=re.search(r'(<div class="mt-6 mb-10 reveal"[^>]*> <p[^>]*>)(.*?)(</p>)',tpl,re.S)
k_benefits=re.findall(r'<svg[^>]*>.*?</svg>\s*([^<]{20,}?)\s*</li>',tpl,re.S)
k_benefits=list(dict.fromkeys(b.strip() for b in k_benefits))[:6]
for sv in SERVICES:
    s=tpl
    name=sv['name']; img=resolve_img(sv['img'])
    s=s.replace(k_lead.group(0),k_lead.group(1)+' '+esc(sv['lead'])+' '+k_lead.group(3))
    s=s.replace(k_body.group(0),k_body.group(1)+esc(sv['body'])+k_body.group(3))
    for old,new in zip(k_benefits,sv['benefits']): s=s.replace(old,esc(new))
    loc='Long Island &amp; NYC' if sv['slug']=='roofing' else 'Manhattan, NY'
    s=s.replace(k_h1,f'<span class="capitalize">{esc(name)}</span> in {loc}')
    s=s.replace('Expert <span class="capitalize">Kitchen Renovation</span> in Manhattan, NY',f'Expert <span class="capitalize">{esc(name)}</span> in {loc}')
    s=s.replace('<span aria-current="page" class="text-text-on-dark-muted capitalize min-w-0 truncate">Kitchen Renovation</span>',f'<span aria-current="page" class="text-text-on-dark-muted capitalize min-w-0 truncate">{esc(name)}</span>')
    s=s.replace('aria-label="Kitchen Renovation service hero"',f'aria-label="{esc(name)} service hero"')
    s=s.replace('/images/services/kitchen-renovation.webp',img)
    s=re.sub(r'(<img src="'+re.escape(img)+r'" alt=")[^"]*(" title=")[^"]*',lambda m:m.group(1)+esc(sv['img_alt'])+m.group(2)+esc(sv['img_alt']),s)
    # FAQ: replace whole visible list + JSON-LD
    fs=s.find('id="faq"'); a0=s.find('<div class="md:col-start-2 border-t border-border reveal" style="transition-delay: 100ms;">',fs)
    a1=s.find('<!-- Still have questions -->',a0)
    inner_start=a0+len('<div class="md:col-start-2 border-t border-border reveal" style="transition-delay: 100ms;">')
    # end of faq list = last '</div> </div> </div> </section>' before still-have-questions; rebuild simply
    sec_end=s.find('</section>',a0)
    s=s[:inner_start]+' '+faq_html(sv['faqs'],'')+' </div> </div> '+s[sec_end:]
    s=s.replace('>Kitchen Renovation FAQ<',f'>{esc(name)} FAQ<').replace('Common questions about kitchen renovation in Manhattan, NY.',f'Common questions about {esc(name.lower())}.')
    # JSON-LD
    url=f'{BASE}/services/general-contractor/{sv["slug"]}/'
    def upd(m):
        d=json.loads(m.group(1)); t=d.get('@type')
        if t=='FAQPage': d['mainEntity']=[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in sv['faqs']]
        elif t=='Service': d['name']=name; d['description']=sv['lead']; d['url']=url
        elif t=='BreadcrumbList': d['itemListElement'][-1].update({"name":name,"item":url})
        return '<script type="application/ld+json">'+json.dumps(d,ensure_ascii=False)+'</script>'
    s=re.sub(r'<script type="application/ld\+json">(.*?)</script>',upd,s,flags=re.S)
    s=re.sub(r'<title>.*?</title>',f'<title>{esc(sv["title"])}</title>',s,flags=re.S)
    s=re.sub(r'(<meta (?:property="og:title"|name="twitter:title") content=")[^"]*',lambda m:m.group(1)+esc(sv['title']),s)
    s=re.sub(r'<meta name="description" content="[^"]*"',f'<meta name="description" content="{esc(sv["desc"])}"',s)
    if sv.get('guide'): s=s.replace('<!-- FAQ for this service -->',guide_section(sv['guide'],sv.get('related',()))+'<!-- FAQ for this service -->',1)
    path=f'services/general-contractor/{sv["slug"]}'
    PAGE_META[path]=(None,sv['desc'])
    s=common(s,path)
    leftover=[w for w in ['Kitchen Renovation FAQ','wet-over-dry rule prevents'] if w in s]
    if leftover: print('WARN leftover',sv['slug'],leftover)
    write(path,s); pages.append(path)

# retired slug (301 -> interior-painting in render.yaml): remove stale build output so the redirect applies
shutil.rmtree(OUT+'/services/general-contractor/painting-and-plaster',ignore_errors=True)

# add new pages to "More General Contractor Services" lists & category page via simple link injection
for f in glob.glob(OUT+'/services/general-contractor/**/index.html',recursive=True):
    s=open(f).read()
    marker='More General Contractor Services\n</p> <ul class="list-none m-0 p-0 flex flex-col gap-[0.25rem]" role="list">'
    if marker in s and 'data-added-links' not in s:
        li=''.join(f'<li data-added-links> <a href="{u}" class="flex items-center gap-2 text-sm font-medium text-text-secondary py-[0.375rem] transition-colors duration-150 no-underline hover:text-accent"> <span class="min-w-0">{n}</span> </a> </li>' for u,n in EXTRA_LINKS if u not in f.replace(OUT,''))
        s=s.replace(marker,marker+li); open(f,'w').write(s)

# robots, sitemap, forms.js, 404, render config
open(OUT+'/robots.txt','w').write(f"# robots.txt for Trimoco LLC\nUser-agent: *\nAllow: /\nDisallow: /thank-you/\n\nSitemap: {BASE}/sitemap.xml\n")
prio={'':'1.0','areas/manhattan-ny':'0.9','areas/hamptons':'0.85','areas/east-hampton':'0.85','areas/westhampton':'0.85','services/general-contractor/co-op-condo-renovation':'0.9'}
urls=''.join(f'<url><loc>{BASE}/{p+"/" if p else ""}</loc><priority>{prio.get(p,"0.8" if p.startswith(("areas","services")) else "0.5")}</priority></url>' for p in sorted(pages))
open(OUT+'/sitemap.xml','w').write('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+urls+'</urlset>')
for old in ['sitemap-index.xml','sitemap-0.xml']:
    open(OUT+'/'+old,'w').write('<?xml version="1.0" encoding="UTF-8"?><sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><sitemap><loc>'+BASE+'/sitemap.xml</loc></sitemap></sitemapindex>') if old=='sitemap-index.xml' else None
os.makedirs(OUT+'/js',exist_ok=True)
shutil.copy(ROOT+'/build/forms.js',OUT+'/js/forms.js')
[os.remove(f) for f in glob.glob(OUT+'/_astro/*.css')]
os.makedirs(OUT+'/services',exist_ok=True)
open(OUT+'/services/index.html','w').write('<!doctype html><meta charset="utf-8"><title>Services | Trimoco LLC</title><meta name="robots" content="noindex"><link rel="canonical" href="'+BASE+'/services/general-contractor/"><meta http-equiv="refresh" content="0;url=/services/general-contractor/"><a href="/services/general-contractor/">Our services</a>')
print(len(pages),'indexable pages')

# ---- 404 page (Render serves /404.html for missing paths) ----
def make_404():
    h=open(os.path.join(OUT,'index.html')).read()
    a=h.index('<main id="main-content">')+len('<main id="main-content">'); b=h.index('</main>')
    body=('<section class="section-pad bg-bg-warm"><div class="container-site max-w-[720px] text-center py-16">'
          '<span class="section-label">Error 404</span><h1 class="font-heading text-[clamp(2rem,5vw,3rem)] font-bold mb-4">Page not found</h1>'
          '<p class="text-base text-text-secondary mb-8">The page you are looking for has moved or no longer exists. Try one of these instead.</p>'
          '<div class="flex gap-3 flex-wrap justify-center mb-8"><a href="/" class="btn-primary">Home</a>'
          '<a href="/services/general-contractor/" class="btn-ghost">Services</a><a href="/areas/manhattan-ny/" class="btn-ghost">Manhattan</a>'
          '<a href="/projects/" class="btn-ghost">Projects</a><a href="/contact/" class="btn-ghost">Contact</a></div>'
          '<p class="text-base">Or call <a href="tel:+15167871045" class="text-accent font-semibold">(516) 787-1045</a></p></div></section>')
    h=h[:a]+body+h[b:]
    h=re.sub(r'<title>[^<]*</title>','<title>Page Not Found | Trimoco LLC</title>',h,count=1)
    h=re.sub(r'<link rel="canonical" href="[^"]*">','',h)
    h=re.sub(r'<script type="application/ld\+json">.*?</script>','',h,flags=re.S)
    h=h.replace('<head>','<head><meta name="robots" content="noindex">',1) if 'name="robots"' not in h else re.sub(r'<meta name="robots" content="[^"]*">','<meta name="robots" content="noindex">',h)
    open(os.path.join(OUT,'404.html'),'w').write(h)
make_404()

# ---- project gallery pages ----
shutil.copy(ROOT+'/build/gallery.js',OUT+'/js/gallery.js')
exec(open(ROOT+'/build/projects.py').read(),{})

# ---- Hamptons prominence (links, footer, home spotlight)
exec(open(ROOT+'/build/sitewide_hamptons.py').read(),globals())
exec(open(ROOT+'/build/farmingdale.py').read(),globals())
# ---- painting / plaster / drywall: nav, grid, footer, schema, drywall page upgrade
exec(open(ROOT+'/build/services_extra.py').read(),globals())
# ---- optional copy tweaks (owner approval pending; separate commit)
exec(open(ROOT+'/build/copy_tweaks.py').read(),globals())
