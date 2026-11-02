# Generates /areas/hamptons/, /areas/east-hampton/, /areas/westhampton/ from the original area-page template.
# exec'd from build.py with its globals (common, write, faq_html, esc, SRC, OUT, BASE, pages, PAGE_META).
import importlib, sys
sys.path.insert(0, ROOT+'/build')
import hamptons_content; importlib.reload(hamptons_content)
from hamptons_content import PAGES, SVC, GALLERIES
TPL=open(SRC+'/areas/east-hamptons-ny/index.html').read()
ARROW='<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>'
PINS='<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-accent shrink-0" aria-hidden="true"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>'
GROUPS={g['slug']:g for g in json.load(open(ROOT+'/build/project-groups.json'))}

def sub1(s,old,new):
    assert old in s, ('missing',old[:80]); return s.replace(old,new,1)

def sections(c,key):
    # services grid
    cards=''.join(f'<a href="{SVC[k][0]}" class="card px-5 py-5 flex flex-col gap-2 no-underline group"><h3 class="font-heading text-[1.0625rem] font-semibold text-text m-0 group-hover:text-accent">{esc(SVC[k][1])}</h3><p class="text-sm text-text-secondary m-0 leading-[1.6]">{esc(t)}</p><span class="text-[0.8125rem] font-semibold text-accent inline-flex items-center gap-1 mt-auto">Learn more {ARROW}</span></a>' for k,t in c['svcs'])
    svc=(f'<!-- ─── HAMPTONS SERVICES (added for SEO) ─── --><section class="section-pad bg-surface" aria-labelledby="hs-heading"><div class="container-site"><div class="max-w-[720px] mb-10 reveal"><span class="section-label">What we do in {esc(c["short"])}</span>'
         f'<h2 id="hs-heading" class="font-heading text-[clamp(1.75rem,_4vw,_2.5rem)] font-bold mb-3">Remodeling services for {esc(c["short"])} homes</h2><span class="accent-bar"></span><p class="text-base text-text-secondary leading-[1.75] mt-6">{esc(c["svc_intro"])}</p></div>'
         f'<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 reveal-stagger">{cards}</div></div></section> ')
    steps=''.join(f'<li class="flex gap-4"><span class="shrink-0 w-8 h-8 rounded-full bg-accent text-accent-fg flex items-center justify-center text-sm font-bold">{i+1}</span><div><h3 class="text-[1.0625rem] font-bold m-0 mb-1">{esc(t)}</h3><p class="text-[0.9375rem] text-text-secondary leading-[1.7] m-0">{esc(d)}</p></div></li>' for i,(t,d) in enumerate(c['plan']))
    towns=''.join((f'<a href="{u}" class="card px-5 py-4 flex flex-col gap-1 no-underline group">' if u.startswith('/') else '<div class="card px-5 py-4 flex flex-col gap-1">')+f'<span class="flex items-center gap-2">{PINS}<span class="font-heading text-[0.9375rem] font-semibold text-text group-hover:text-accent">{esc(n)}</span></span><span class="text-[0.8125rem] text-text-secondary">{esc(d)}</span>'+('</a>' if u.startswith('/') else '</div>') for n,u,d in c['towns'])
    plan=(f'<section class="section-pad" aria-labelledby="hp-heading"><div class="container-site grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-16 items-start"><div class="reveal"><span class="section-label">Planning</span><h2 id="hp-heading" class="font-heading text-[clamp(1.75rem,_4vw,_2.5rem)] font-bold mb-3">{esc(c["plan_title"])}</h2><span class="accent-bar"></span>'
          f'<ol class="list-none m-0 p-0 mt-8 flex flex-col gap-6" role="list">{steps}</ol></div>'
          f'<div class="reveal" id="towns"><span class="section-label">Where we work</span><h2 class="font-heading text-[clamp(1.5rem,_3.5vw,_2rem)] font-bold mb-3">{esc(c["towns_title"])}</h2><span class="accent-bar"></span><div class="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-8">{towns}</div>'
          f'<div class="flex flex-col sm:flex-row gap-3 mt-8"><button type="button" data-open-quote-modal class="btn-primary justify-center">Get a Free Estimate</button><a href="tel:+15167871045" class="btn-ghost justify-center">Call (516) 787-1045</a></div></div></div></section> ')
    gal=''
    for slug,label,loc in GALLERIES:
        g=GROUPS.get(slug)
        if not g: continue
        f=g['photos'][0]; n=len(g['photos'])
        gal+=(f'<a href="/projects/{slug}/" class="flex flex-col no-underline group"><div class="relative rounded-xl overflow-hidden aspect-[4/5]"><img src="/images/projects/thumbs/{f}" alt="{esc(label)}{", "+esc(loc) if loc else ""}" width="800" height="1000" loading="lazy" decoding="async" class="w-full h-full object-cover">'
              f'<span class="proj-badge">{n} photo{"s" if n>1 else ""}</span></div><h3 class="text-[0.9375rem] font-bold text-text mt-3 mb-0 group-hover:text-accent">{esc(label)}</h3>'
              +(f'<p class="text-xs text-text-muted m-0 mt-0.5">{esc(loc)}</p>' if loc else '')+'</a>')
    work=(f'<section class="section-pad bg-bg-warm" aria-labelledby="hw-heading"><div class="container-site"><div class="max-w-[720px] mb-10 reveal"><span class="section-label">Our work</span><h2 id="hw-heading" class="font-heading text-[clamp(1.75rem,_4vw,_2.5rem)] font-bold mb-3">See the quality of our finished work</h2><span class="accent-bar"></span>'
          f'<p class="text-base text-text-secondary leading-[1.75] mt-6">These are real Trimoco projects, labeled with where they were done. Browse the galleries to see the kitchens, baths, tile and millwork we build, then call us about your {esc(c["short"])} home.</p></div>'
          f'<div class="grid grid-cols-2 lg:grid-cols-3 gap-6 reveal-stagger">{gal}</div><div class="mt-8"><a href="/projects/" class="btn-ghost">All projects</a></div></div></section> ')
    extra=''
    if key=='hamptons':
        extra=('<section class="py-10 border-t border-border bg-bg" aria-label="Hamptons pages"><div class="container-site flex flex-col md:flex-row gap-4">'
               '<a href="/areas/east-hampton/" class="card flex-1 px-6 py-5 no-underline group"><span class="section-label">Town guide</span><span class="block font-heading text-xl font-bold text-text group-hover:text-accent">East Hampton contractor</span><span class="block text-sm text-text-secondary mt-1">East Hampton Village, Amagansett, Springs, Wainscott and Montauk</span></a>'
               '<a href="/areas/westhampton/" class="card flex-1 px-6 py-5 no-underline group"><span class="section-label">Town guide</span><span class="block font-heading text-xl font-bold text-text group-hover:text-accent">Westhampton &amp; Westhampton Beach contractor</span><span class="block text-sm text-text-secondary mt-1">Westhampton Beach, Westhampton, Quogue, Remsenburg and Hampton Bays</span></a></div></section> ')
    else:
        other='/areas/westhampton/' if key=='east-hampton' else '/areas/east-hampton/'
        on='Westhampton &amp; Westhampton Beach' if key=='east-hampton' else 'East Hampton'
        extra=(f'<section class="py-10 border-t border-border bg-bg" aria-label="More Hamptons pages"><div class="container-site flex flex-wrap items-center gap-3"><span class="text-[0.9375rem] font-semibold text-text-secondary">More in the Hamptons:</span>'
               f'<a href="/areas/hamptons/" class="badge no-underline hover:text-accent">All Hamptons towns</a><a href="{other}" class="badge no-underline hover:text-accent">{on}</a><a href="/areas/manhattan-ny/" class="badge no-underline hover:text-accent">Manhattan</a><a href="/areas/long-island-ny/" class="badge no-underline hover:text-accent">Long Island</a></div></section> ')
    return svc+plan+work+extra

def build_page(key,c):
    s=TPL; url=f'{BASE}/{c["path"]}/'
    s=s.replace('aria-label="East Hamptons, NY service page header"',f'aria-label="{esc(c["name"])} service page header"')
    s=s.replace("url('/images/service-areas/east-hamptons-ny.webp')",f"url('{c['hero_img']}')")
    crumb_mid='' if key=='hamptons' else ' <a href="/areas/hamptons/" class="text-text-on-dark-dim hover:text-text-on-dark-muted transition-colors duration-150 shrink-0">The Hamptons</a> <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true" class="text-text-on-dark-dim"><polyline points="9 18 15 12 9 6"></polyline></svg>'
    s=sub1(s,'<span aria-current="page" class="text-text-on-dark-muted capitalize min-w-0 truncate">East Hamptons, NY</span>',crumb_mid+f'<span aria-current="page" class="text-text-on-dark-muted capitalize min-w-0 truncate">{esc(c["crumb"])}</span>')
    s=re.sub(r'(<h1 class="font-heading[^>]*>).*?(</h1>)',lambda m:m.group(1)+' '+c['h1']+' '+m.group(2),s,count=1,flags=re.S)
    s=re.sub(r'(style="animation-delay: 270ms">).*?(</p>)',lambda m:m.group(1)+' '+esc(c['lead'])+' '+m.group(2),s,count=1,flags=re.S)
    s=re.sub(r'(<p class="font-heading text-\[2rem\][^>]*>)East Hamptons, NY(</p>)',lambda m:m.group(1)+esc(c['short'] if key!='westhampton' else 'Westhampton')+m.group(2),s,count=1)
    s=s.replace(' NY Service Area ',' Suffolk County, NY ' if key!='hamptons' else ' East End of Long Island ',1)
    s=s.replace('No extra travel fees for this area','Free on-site estimates')
    chip='<span class="py-[0.3rem] px-3 bg-surface-footer border border-border-on-dark rounded-full text-[0.8125rem] text-text-on-dark-muted"> {} </span>'
    s=re.sub(r'(Communities we serve\s*</p> <div class="flex flex-wrap gap-2">).*?(</div>)',lambda m:m.group(1)+' '+''.join(chip.format(esc(x)) for x in c['chips'])+' '+m.group(2),s,count=1,flags=re.S)
    # narrative
    s=re.sub(r'<img src="/images/service-areas/east-hamptons-ny-secondary\.webp" alt="[^"]*" title="[^"]*"',f'<img src="{c["side_img"]}" alt="{esc(c["side_alt"])}"',s,count=1)
    s=re.sub(r'(<p class="font-heading text-\[1\.0625rem\] font-bold text-text-on-dark[^>]*>)East Hamptons, NY(</p>)',lambda m:m.group(1)+esc(c['crumb'])+m.group(2),s,count=1)
    s=sub1(s,'<span class="section-label">Trimoco LLC in East Hamptons, NY</span>',f'<span class="section-label">{esc(c["label"])}</span>')
    s=re.sub(r'(<h2 id="area-about-heading"[^>]*>).*?(</h2>)',lambda m:m.group(1)+' '+esc(c['h2'])+' '+m.group(2),s,count=1,flags=re.S)
    s=re.sub(r'(<span class="accent-bar"></span> <div class="mt-6 flex flex-col gap-4 mb-8">).*?(</div> <!-- Quick proof points -->)',lambda m:m.group(1)+' '+''.join(f'<p class="text-base text-text-secondary leading-[1.75]">{esc(p)}</p>' for p in c['paras'])+' '+m.group(2),s,count=1,flags=re.S)
    m=re.search(r'At a glance</p> <ul class="list-none m-0 p-0 flex flex-col gap-2.5" role="list">(.*?)</ul>',s,re.S)
    lis=re.findall(r'(<li class="flex items-start gap-3 text-\[0\.9375rem\] text-text-secondary">\s*<svg.*?</svg>)\s*(.*?)\s*</li>',m.group(1),re.S)
    newlis=''.join(f'{lis[0][0]} {esc(t)} </li>' for t in c['glance'])
    s=s[:m.start(1)]+' '+newlis+' '+s[m.end(1):]
    s=s.replace('Schedule a Free Inspection in East Hamptons, NY',f'Get a Free Estimate in {esc(c["short"])}')
    # services section intro
    s=s.replace('<span class="section-label">Our Services in East Hamptons, NY</span>',f'<span class="section-label">All services</span>')
    s=re.sub(r'(<h2 id="area-services-heading"[^>]*>).*?(</h2>)',lambda m:m.group(1)+f' Every Trimoco service, available in <span class="capitalize">{esc(c["short"])}</span> '+m.group(2),s,count=1,flags=re.S)
    s=re.sub(r'(<h2 id="area-services-heading".*?</h2> <p class="[^"]*">).*?(</p>)',lambda m:m.group(1)+' General contracting, carpentry, electrical and plumbing, coordinated by one team. '+m.group(2),s,count=1,flags=re.S)
    s=sub1(s,'<!-- ─── SERVICES ──',sections(c,key)+'<!-- ─── SERVICES ──')
    # CTA band
    s=re.sub(r'(<p class="text-\[0\.6875rem\] font-semibold tracking-\[0\.12em\] uppercase text-accent-on-dark mb-3 max-w-none">)\s*Serving East Hamptons, NY\s*(</p>)',lambda m:m.group(1)+' Serving '+esc(c['short'] if key!='hamptons' else 'the Hamptons')+' '+m.group(2),s,count=1)
    s=re.sub(r'Our crew knows East Hamptons, NY\. .*?anything\.',esc(c['cta']),s,count=1,flags=re.S)
    s=s.replace('Schedule a Free Inspection','Get a Free Estimate')
    # FAQ
    fs=s.find('id="faq"'); a0=s.find('<div class="md:col-start-2 border-t border-border reveal" style="transition-delay: 100ms;">',fs)
    inner=a0+len('<div class="md:col-start-2 border-t border-border reveal" style="transition-delay: 100ms;">')
    a1=s.find('<!-- Still have questions -->',a0)
    s=s[:inner]+' '+faq_html(c['faqs'],'h')+' </div> '+s[a1:]
    s=re.sub(r'(<h2 id="faq-heading"[^>]*>).*?(</h2>)',lambda m:m.group(1)+f'{esc(c["short"]).capitalize() if key=="hamptons" else esc(c["short"])} renovation FAQ'+m.group(2),s,count=1,flags=re.S)
    s=s.replace('Common questions from East Hamptons, NY homeowners about our services, process, and coverage.',f'Common questions from {esc(c["short"])} homeowners about scheduling, permits and working with us from the city.')
    # JSON-LD
    def upd(m):
        d=json.loads(m.group(1)); t=d.get('@type')
        if t=='FAQPage': d['mainEntity']=[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in c['faqs']]
        elif t=='Service':
            d['name']=f'General contractor in {c["name"]}'; d['serviceType']='Home renovation and remodeling'; d['url']=url
            d['description']=c['lead']
            d['areaServed']=[{"@type":"Place","name":x+', NY'} for x in c['chips'] if x!='Dune Road']
        elif t=='BreadcrumbList':
            items=[{"@type":"ListItem","position":1,"name":"Home","item":BASE+'/'}]
            if key!='hamptons': items.append({"@type":"ListItem","position":2,"name":"The Hamptons","item":BASE+'/areas/hamptons/'})
            items.append({"@type":"ListItem","position":len(items)+1,"name":c['crumb'],"item":url}); d['itemListElement']=items
        return '<script type="application/ld+json">'+json.dumps(d,ensure_ascii=False)+'</script>'
    s=re.sub(r'<script type="application/ld\+json">(.*?)</script>',upd,s,flags=re.S)
    s=re.sub(r'<title>.*?</title>',f'<title>{esc(c["title"])}</title>',s,flags=re.S)
    s=re.sub(r'(<meta (?:property="og:title"|name="twitter:title") content=")[^"]*',lambda m:m.group(1)+esc(c['title']),s)
    s=re.sub(r'<meta name="description" content="[^"]*"',f'<meta name="description" content="{esc(c["desc"])}"',s)
    PAGE_META[c['path']]=(c['title'],c['desc'])
    s=common(s,c['path'])
    left=[w for w in ['East Hamptons','West Hamptons','panhandle','5 years'] if w in re.sub(r'<script.*?</script>','',s[s.index('<main'):s.index('</main>')],flags=re.S)]
    if left: print('WARN leftover',key,left)
    write(c['path'],s); pages.append(c['path'])

for key,c in PAGES.items(): build_page(key,c)
