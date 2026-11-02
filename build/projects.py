# Project gallery pages + clickable project photos. Run after build.py.
import re, os, json, html, glob
from PIL import Image
ROOT='/workspace/trimoco-site'; SRC=ROOT+'/_orig/mirror'; OUT=ROOT+'/public'; BASE='https://www.trimoco.com'
esc=lambda t: html.escape(t, quote=True)

orig=open(SRC+'/projects/index.html').read()
cards=re.findall(r'<article class="project-card"[^>]*aria-label="([^"]*)".*?<img src="/images/projects/(drive_[^"]*)" alt="([^"]*)".*?</article>',orig,re.S)
PH=[{'file':f,'title':html.unescape(t),'alt':html.unescape(a)} for t,f,a in cards]   # index = order on original /projects page
assert len(PH)==50
assert PH[29]['file'].startswith('drive_17HzGk') and PH[36]['file'].startswith('drive_1tH6Sc')
PH[29]['alt']='Modern kitchen with white cabinets, marble waterfall island, and stainless steel refrigerator'  # original alt wrongly described a bathroom

# Best-guess grouping by what is visible in the photos (same cabinets, stone, floors, windows, tile).
# Titles are taken from the original site's own card titles. Owner should confirm.
GROUPS=[
 ('west-village-marble-kitchen-bathroom-renovation','West Village, Manhattan: Marble Kitchen and Bathroom Renovation',[1,7,15,42,43,46,8,10,17,5,13,3,16]),
 ('upper-west-side-west-end-avenue-kitchen-renovation','Upper West Side, Manhattan: White Kitchen Renovation on West End Avenue',[0,6,12]),
 ('kitchen-cabinetry-and-backsplash-installation','Kitchen Cabinetry and Backsplash Installation',[41,11,18,27]),
 ('green-kitchen-cabinetry-installation','Custom Kitchen Cabinetry Installation (Green Cabinets)',[31,33,23,26]),
 ('blue-kitchen-remodel-custom-cabinetry','Modern Kitchen Remodel with Custom Cabinetry (Blue Cabinets)',[49,45,48]),
 ('soho-manhattan-bathroom-walk-in-shower','SoHo, Manhattan: Bathroom Renovation with Walk-In Shower on Wooster Street',[38,35,28,34,37]),
 ('90th-street-manhattan-bathroom-tile-renovation','90th Street, Manhattan: Master Bathroom Tile Renovation',[9,20,21]),
 ('astoria-queens-bathroom-renovation','Astoria, Queens: Complete Bathroom Renovation',[36]),
 ('modern-kitchen-marble-waterfall-island','Modern Kitchen with Marble Waterfall Island',[29]),
 ('modern-apartment-interior-renovation','Modern Apartment Interior Renovation',[14,19,24]),
 ('custom-drywall-and-built-in-shelving','Custom Drywall and Built-In Shelving Installation',[32,25]),
 ('drywall-installation-and-framing','Drywall Installation and Framing',[2,4,40]),
]
used={i for _,_,ids in GROUPS for i in ids}
def slugify(t): return re.sub(r'[^a-z0-9]+','-',t.lower()).strip('-')
taken={g[0] for g in GROUPS}
for i,p in enumerate(PH):
    if i in used: continue
    sl=slugify(p['title'])
    if sl in taken: sl=sl+'-'+str(i)
    taken.add(sl); GROUPS.append((sl,p['title'],[i]))
FILE2PROJ={}
for sl,t,ids in GROUPS:
    for n,i in enumerate(ids): FILE2PROJ[PH[i]['file']]=(sl,t,n)

WV='west-village-marble-kitchen-bathroom-renovation'
UWS='upper-west-side-west-end-avenue-kitchen-renovation'
# owner-confirmed locations (Nov 2, 2026); street numbers intentionally not published
SOHO='soho-manhattan-bathroom-walk-in-shower'; E90='90th-street-manhattan-bathroom-tile-renovation'; AST='astoria-queens-bathroom-renovation'
LOC={WV:'West Village, Manhattan',UWS:'Upper West Side, Manhattan',SOHO:'SoHo, Manhattan',E90:'90th Street, Manhattan',AST:'Astoria, Queens'}
PLACE={WV:'West Village, Manhattan',UWS:'West End Avenue, Upper West Side, Manhattan',SOHO:'Wooster Street, SoHo, Manhattan',E90:'90th Street, Manhattan',AST:'Astoria, Queens'}
WHERE={WV:'in the West Village, Manhattan',UWS:'on West End Avenue, Upper West Side, Manhattan',SOHO:'on Wooster Street in SoHo, Manhattan',E90:'on 90th Street, Manhattan',AST:'in Astoria, Queens'}
DESC={WV:'walnut and white kitchen cabinetry, marble slab counters and a marble slab bathroom',UWS:'white cabinetry with glass-front upper doors, black countertops and pendant lights',SOHO:'large-format beige tile, a glass walk-in shower and a wall-hung sink',E90:'ribbed green-gray wall tile and a shower with built-in niches',AST:'white subway tile, a bathtub with shower and a wood vanity'}
LOCFILE={PH[i]['file']:LOC[g[0]] for g in GROUPS if g[0] in LOC for i in g[2]}
WV_FILES=set(LOCFILE)
for i,p in enumerate(PH):
    if p['file'] in LOCFILE: p['alt']=p['alt']+', '+LOCFILE[p['file']]
# thumbnails (640px wide) for gallery grids
os.makedirs(OUT+'/images/projects/thumbs',exist_ok=True)
DIM={}
for p in PH:
    src=OUT+'/images/projects/'+p['file']; dst=OUT+'/images/projects/thumbs/'+p['file']
    im=Image.open(src); DIM[p['file']]=im.size
    if not os.path.exists(dst):
        t=im.convert('RGB'); t.thumbnail((800,800*3)); t.save(dst,'WEBP',quality=64,method=6)
    DIM['t/'+p['file']]=Image.open(dst).size

shell=open(OUT+'/projects/index.html').read()
hero_a=shell.index('<section class="bg-dark-bg'); grid_a=shell.index('<section class="section-pad" aria-labelledby="projects-grid-label"')
grid_b=shell.index('</section>',grid_a)+len('</section>')
CHEV='<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true" class="text-text-on-dark-dim"><polyline points="9 18 15 12 9 6"></polyline></svg>'
PIN='<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>'
HDRFIX='@media(max-width:767px){section[aria-label="Projects page header"],section[aria-label="Project header"]{padding-top:6.5rem!important}}'
CSS='''<style>'''+HDRFIX+'''.pg-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:1rem}.pg-item{all:unset;box-sizing:border-box;display:block;cursor:zoom-in;border-radius:.75rem;overflow:hidden;background:#eee;position:relative}.pg-item img{width:100%;height:100%;aspect-ratio:3/4;object-fit:cover;display:block;transition:transform .3s}.pg-item:hover img{transform:scale(1.03)}.pg-item:focus-visible{outline:3px solid #c9a227;outline-offset:3px}.pg-cap{font-size:.8125rem;color:var(--color-text-secondary,#555);margin:.5rem .125rem 0;line-height:1.45}
#lb{border:0;padding:0;margin:0;width:100vw;height:100dvh;max-width:none;max-height:none;background:rgba(10,10,8,.94);color:#fff}#lb::backdrop{background:rgba(0,0,0,.6)}#lb .lb-stage{position:absolute;inset:3.5rem .5rem 4.5rem;display:flex;align-items:center;justify-content:center;touch-action:pan-y}#lb img{max-width:100%;max-height:100%;object-fit:contain;user-select:none;-webkit-user-drag:none}#lb button{position:absolute;background:rgba(255,255,255,.12);color:#fff;border:1px solid rgba(255,255,255,.25);border-radius:999px;width:3rem;height:3rem;font-size:1.5rem;line-height:1;cursor:pointer;display:flex;align-items:center;justify-content:center}#lb button:hover{background:rgba(255,255,255,.25)}#lb button:focus-visible{outline:3px solid #c9a227}#lb .lb-close{top:.5rem;right:.5rem}#lb .lb-prev{left:.5rem;top:50%;transform:translateY(-50%)}#lb .lb-next{right:.5rem;top:50%;transform:translateY(-50%)}#lb .lb-info{position:absolute;left:1rem;right:1rem;bottom:.75rem;text-align:center;font-size:.875rem;line-height:1.4}#lb .lb-count{position:absolute;top:1.1rem;left:1rem;font-size:.875rem;opacity:.85}@media(max-width:640px){#lb .lb-prev,#lb .lb-next{top:auto;bottom:3.6rem;transform:none}}
.proj-link{position:absolute;inset:0;z-index:5;border-radius:inherit}.proj-link:focus-visible{outline:3px solid #c9a227;outline-offset:-3px}.proj-badge{position:absolute;right:.75rem;top:.75rem;z-index:4;background:rgba(0,0,0,.6);color:#fff;font-size:.6875rem;font-weight:600;padding:.25rem .55rem;border-radius:999px;pointer-events:none}</style>'''

def pic(f,thumb=True,eager=False,alt=None):
    key=('t/' if thumb else '')+f; w,h=DIM[key]
    src='/images/projects/'+('thumbs/' if thumb else '')+f
    ss=f' srcset="/images/projects/thumbs/{f} {DIM["t/"+f][0]}w, /images/projects/{f} {DIM[f][0]}w" sizes="(max-width: 640px) 92vw, 380px"' if thumb else ''
    return f'<img src="{src}"{ss} alt="{esc(alt or "")}" width="{w}" height="{h}" loading="{"eager" if eager else "lazy"}" decoding="async">'

def cover(o):
    return pic(PH[o[2][0]]['file'],alt=PH[o[2][0]]['alt']).replace('<img ','<img class="w-full h-full object-cover" ')

def page(sl,title,ids):
    url=f'{BASE}/projects/{sl}/'; n=len(ids)
    desc=(f'{n} photo{"s" if n>1 else ""} of a renovation {WHERE[sl]} by Trimoco LLC: {DESC[sl]}.' if sl in LOC else None) or f'{n} photo{"s" if n>1 else ""} of {title.lower()} by Trimoco LLC, a licensed general contractor serving Manhattan, Brooklyn, Queens, the Bronx and Long Island.'
    items=''.join(f'<figure class="m-0"><button type="button" class="pg-item" data-lb-index="{k}" aria-label="Enlarge photo {k+1} of {n}: {esc(PH[i]["alt"])}">{pic(PH[i]["file"],eager=k<3,alt=PH[i]["alt"])}</button><figcaption class="pg-cap">{esc(PH[i]["alt"])}</figcaption></figure>' for k,i in enumerate(ids))
    data=json.dumps([{'src':'/images/projects/'+PH[i]['file'],'alt':PH[i]['alt']} for i in ids])
    others=[g for g in GROUPS if g[0]!=sl and len(g[2])>1][:6]
    more=''.join(f'<a href="/projects/{o[0]}/" class="block no-underline group"><div class="relative rounded-xl overflow-hidden aspect-[4/3]">{cover(o)}<span class="proj-badge">{len(o[2])} photos</span></div><p class="mt-2 font-semibold text-text group-hover:text-accent">{esc(o[1])}</p></a>' for o in others)
    hero=(f'<section class="bg-dark-bg relative overflow-hidden py-[clamp(3.5rem,_7vw,_6rem)]" aria-label="Project header"><div class="container-site relative z-10">'
          f'<nav aria-label="Breadcrumb" class="flex items-center flex-wrap gap-x-2 gap-y-1 text-[0.8125rem] mb-6"><a href="/" class="text-text-on-dark-dim hover:text-accent-light no-underline">Home</a> {CHEV} <a href="/projects/" class="text-text-on-dark-dim hover:text-accent-light no-underline">Projects</a> {CHEV} <span aria-current="page" class="text-text-on-dark-muted">{esc(title)}</span></nav>'
          f'<span class="section-label section-label-dark">General Contractor</span><h1 class="text-[clamp(1.75rem,_4vw,_2.75rem)] font-bold text-text-on-dark leading-[1.15] mb-3">{esc(title)}</h1>'
          f'<p class="flex items-center gap-1.5 text-sm text-text-on-dark-muted mb-4">{PIN} {LOC.get(sl,'Lynbrook, NY')} · {n} photo{"s" if n>1 else ""}</p>'
          f'<p class="text-[1.0625rem] text-text-on-dark leading-[1.65] max-w-[60ch] mb-6">Photos from this Trimoco LLC project. Tap any photo to enlarge it, then swipe or use the arrow keys to browse.</p>'
          f'<div class="flex gap-3 flex-wrap"><button type="button" data-open-quote-modal class="btn-primary py-3 px-6 text-sm">Get a Free Estimate</button><a href="tel:+15167871045" class="btn-ghost py-3 px-5 text-sm">(516) 787-1045</a></div></div></section>')
    gal=(f'<section class="section-pad" aria-label="Project photos"><div class="container-site"><div class="pg-grid">{items}</div>'
         f'<div class="mt-10 flex gap-3 flex-wrap items-center"><button type="button" data-open-quote-modal class="btn-primary">Get a Free Estimate</button><a href="/projects/" class="btn-ghost">All projects</a></div>'
         + (f'<h2 class="text-[clamp(1.5rem,3vw,2rem)] font-bold mt-16 mb-6">More projects</h2><div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">{more}</div>' if more else '')
         + f'</div></section><dialog id="lb" aria-label="Photo viewer"><span class="lb-count" aria-live="polite"></span><button type="button" class="lb-close" aria-label="Close photo viewer">&times;</button><div class="lb-stage"><img alt=""></div><button type="button" class="lb-prev" aria-label="Previous photo">&#8249;</button><button type="button" class="lb-next" aria-label="Next photo">&#8250;</button><p class="lb-info"></p></dialog><script type="application/json" id="lb-data">{data}</script>')
    s=shell[:hero_a]+hero+gal+shell[grid_b:]
    full=f'{esc(title)} | Project Photos | Trimoco LLC'
    s=re.sub(r'<title>[^<]*</title>',f'<title>{full}</title>',s,1)
    for prop in ['og:title','twitter:title']: s=re.sub(rf'<meta (property|name)="{prop}" content="[^"]*">',rf'<meta \1="{prop}" content="{full}">',s)
    for prop in ['description','og:description','twitter:description']: s=re.sub(rf'<meta (property|name)="{prop}" content="[^"]*">',rf'<meta \1="{prop}" content="{esc(desc)}">',s)
    s=re.sub(r'<link rel="canonical" href="[^"]*">',f'<link rel="canonical" href="{url}">',s)
    s=re.sub(r'<meta property="og:url" content="[^"]*">',f'<meta property="og:url" content="{url}">',s)
    og=BASE+'/images/projects/'+PH[ids[0]]['file']
    for prop in ['og:image','twitter:image']: s=re.sub(rf'<meta (property|name)="{prop}" content="[^"]*">',rf'<meta \1="{prop}" content="{og}">',s)
    def ld(m):
        d=json.loads(m.group(1))
        if d.get('@type')=='BreadcrumbList':
            d['itemListElement']=[{"@type":"ListItem","position":1,"name":"Home","item":BASE+"/"},{"@type":"ListItem","position":2,"name":"Projects","item":BASE+"/projects/"},{"@type":"ListItem","position":3,"name":title,"item":url}]
        return '<script type="application/ld+json">'+json.dumps(d,ensure_ascii=False)+'</script>'
    s=re.sub(r'<script type="application/ld\+json">(.*?)</script>',ld,s,flags=re.S)
    gallery_ld={"@context":"https://schema.org","@type":"ImageGallery","name":title,"url":url,"description":desc,"author":{"@id":BASE+"/#business"},**({"contentLocation":{"@type":"Place","name":PLACE.get(sl,""),"address":{"@type":"PostalAddress","addressLocality":("Queens" if sl==AST else "New York"),"addressRegion":"NY","addressCountry":"US"}}} if sl in LOC else {}),
                "image":[{"@type":"ImageObject","contentUrl":BASE+'/images/projects/'+PH[i]['file'],"caption":PH[i]['alt']} for i in ids]}
    s=s.replace('</head>',CSS+'<script type="application/ld+json">'+json.dumps(gallery_ld,ensure_ascii=False)+'</script><script src="/js/gallery.js" defer></script></head>',1)
    os.makedirs(f'{OUT}/projects/{sl}',exist_ok=True); open(f'{OUT}/projects/{sl}/index.html','w').write(s)

for g in GROUPS: page(*g)

# make every project photo elsewhere on the site link to its project page
def linkify(s):
    def rep(m):
        tag=m.group(0); f=m.group(1); sl,t,n=FILE2PROJ[f]; cnt=len(dict((g[0],g[2]) for g in GROUPS)[sl])
        a=f'<a href="/projects/{sl}/" class="proj-link" aria-label="View project photos: {esc(t)}"></a>'
        badge=f'<span class="proj-badge">{cnt} photos</span>' if cnt>1 else ''
        if 'srcset' not in tag and '<figure' not in m.string[max(0,m.start()-300):m.start()]:
            tag=tag.replace(f'src="/images/projects/{f}"',f'src="/images/projects/thumbs/{f}" srcset="/images/projects/thumbs/{f} {DIM["t/"+f][0]}w, /images/projects/{f} {DIM[f][0]}w" sizes="(max-width: 640px) 92vw, 400px"',1)
        return tag+a+badge
    return re.sub(r'<img [^>]*src="/images/projects/(drive_[^"/]*)"[^>]*>',rep,s)
for f in glob.glob(OUT+'/**/*.html',recursive=True):
    rel=f[len(OUT)+1:]
    if re.match(r'projects/[^/]+/index\.html',rel) or rel=='404.html': continue
    s=open(f).read()
    if '/images/projects/drive_' not in s or 'proj-link' in s: continue
    s=re.sub(r'(src="/images/projects/(?:thumbs/)?'+re.escape(PH[29]['file'])+r'"[^>]*?alt=")[^"]*"',lambda m:m.group(1)+PH[29]['alt']+'"',s)
    s=re.sub(r'(<img [^>]*src="/images/projects/'+re.escape(PH[29]['file'])+r'"[^>]*?) title="[^"]*"',r'\1',s)
    for f0 in WV_FILES:
        lab=LOCFILE[f0]
        s=re.sub(r'(src="/images/projects/(?:thumbs/)?'+re.escape(f0)+r'"[^>]*?alt=")([^"]*)"',lambda m: m.group(1)+(m.group(2) if lab in m.group(2) else m.group(2)+', '+lab)+'"',s)
        s=re.sub(r'(<img [^>]*src="/images/projects/'+re.escape(f0)+r'"[^>]*?) title="[^"]*"',r'\1',s)
    def cardloc(m):
        blk=m.group(0)
        hit=[f0 for f0 in LOCFILE if f0 in blk]
        return blk.replace('Lynbrook, NY',LOCFILE[hit[0]]) if hit else blk
    s=re.sub(r'<article\b.*?</article>',cardloc,s,flags=re.S)
    s=linkify(s)
    s=s.replace('<figure class="mb-8 overflow-hidden','<figure class="relative mb-8 overflow-hidden')
    s=s.replace('</head>',CSS[:7]+re.search(r'\.proj-link\{.*?(?=</style>)',CSS,re.S).group(0)+'</style></head>',1)
    open(f,'w').write(s)
# feature the West Village project on Manhattan + co-op/condo pages
FEAT={WV:dict(pick=[0,4,6,1],h2='Marble kitchen and bathroom in the West Village',hid='wv-heading',
   p='A kitchen and bathroom renovation by Trimoco LLC in the West Village, Manhattan: walnut and white kitchen cabinetry with marble slab counters, and a bathroom finished in marble slabs.'),
 SOHO:dict(pick=[0,1,2],h2='Walk-in shower bathroom on Wooster Street, SoHo',hid='soho-heading',p=''),
 E90:dict(pick=[0,1,2],h2='Tiled bathroom on 90th Street',hid='e90-heading',p=''),
 AST:dict(pick=[0],h2='Bathroom renovation in Astoria',hid='ast-heading',p=''),
 UWS:dict(pick=[0,1,2],h2='White kitchen on West End Avenue, Upper West Side',hid='uws-heading',
   p='A kitchen renovation by Trimoco LLC on West End Avenue in Manhattan\'s Upper West Side: white cabinetry with glass-front upper doors, black countertops and pendant lighting.')}
def featured(key=WV):
    g=[x for x in GROUPS if x[0]==key][0]; ids=g[2]; F=FEAT[key]
    pick=[ids[k] for k in F['pick']]
    tiles=''.join(f'<a href="/projects/{key}/" class="block relative rounded-xl overflow-hidden aspect-[3/4]" aria-label="View photo: {esc(PH[i]["alt"])}">{pic(PH[i]["file"],alt=PH[i]["alt"]).replace("<img ","<img class=\"w-full h-full object-cover\" ")}</a>' for i in pick)
    return (f'<!-- ─── FEATURED MANHATTAN PROJECT (owner-confirmed location) ─── --><section class="section-pad" aria-labelledby="{F["hid"]}"><div class="container-site">'
      f'<span class="section-label">Recent Manhattan Project</span><h2 id="{F["hid"]}" class="font-heading text-[clamp(1.75rem,_4vw,_2.5rem)] font-bold mb-3">{F["h2"]}</h2><span class="accent-bar"></span>'
      f'<p class="text-base text-text-secondary leading-[1.75] max-w-[65ch] mt-6 mb-8">{esc(F["p"])}</p>'
      f'<div class="grid grid-cols-2 lg:grid-cols-{len(pick)} gap-4 mb-8">{tiles}</div>'
      f'<div class="flex gap-3 flex-wrap"><a href="/projects/{key}/" class="btn-primary">See all {len(ids)} photos</a><button type="button" data-open-quote-modal class="btn-ghost">Get a Free Estimate</button></div></div></section> ')
def project_cards(keys,label,h2,intro):
    cards=''
    for key in keys:
        g=[x for x in GROUPS if x[0]==key][0]; i0=g[2][0]; n=len(g[2])
        img=pic(PH[i0]['file'],alt=PH[i0]['alt']).replace('<img ','<img class="w-full h-full object-cover" ')
        cards+=(f'<a href="/projects/{key}/" class="flex flex-col no-underline group"><div class="relative rounded-xl overflow-hidden aspect-[4/5]">{img}<span class="proj-badge">{n} photo{"s" if n>1 else ""}</span></div>'
                f'<p class="text-xs font-semibold uppercase tracking-[0.08em] text-accent mt-3 mb-1">{esc(LOC[key])}</p><h3 class="text-[1.0625rem] font-bold text-text m-0 group-hover:text-accent">{esc(g[1].split(": ",1)[-1])}</h3>'
                f'<p class="text-sm text-text-secondary mt-1 mb-0">{esc(DESC[key][0].upper()+DESC[key][1:])}.</p></a>')
    cols=min(len(keys),4)
    return (f'<!-- ─── REAL LOCAL PROJECTS (owner-confirmed locations) ─── --><section class="section-pad" aria-labelledby="local-projects-heading"><div class="container-site">'
            f'<span class="section-label">{esc(label)}</span><h2 id="local-projects-heading" class="font-heading text-[clamp(1.75rem,_4vw,_2.5rem)] font-bold mb-3">{esc(h2)}</h2><span class="accent-bar"></span>'
            f'<p class="text-base text-text-secondary leading-[1.75] max-w-[65ch] mt-6 mb-8">{esc(intro)}</p>'
            f'<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-{cols} gap-6 mb-8">{cards}</div>'
            f'<div class="flex gap-3 flex-wrap"><button type="button" data-open-quote-modal class="btn-primary">Get a Free Estimate</button><a href="/projects/" class="btn-ghost">All projects</a></div></div></section> ')
PLACEMENTS=[('areas/manhattan-ny/index.html', lambda: project_cards([WV,UWS,SOHO,E90],'Recent Manhattan Projects','Our recent work in Manhattan','Kitchens and bathrooms Trimoco LLC has renovated in Manhattan. Tap a project to see all of its photos.')),
            ('services/general-contractor/co-op-condo-renovation/index.html', lambda: featured(WV)),
            ('areas/queens-ny/index.html', lambda: project_cards([AST],'Recent Queens Project','Our recent work in Queens','A bathroom Trimoco LLC renovated in Astoria, Queens. Tap the photo to see the project page.'))]
for rel,fn in PLACEMENTS:
    f=OUT+'/'+rel; s=open(f).read()
    if 'owner-confirmed location' in s: continue
    anchor='<!-- ─── LOCAL GUIDE (added for SEO) ─── -->'
    fx=fn()
    if anchor in s: s=s.replace(anchor,fx+anchor,1)
    else:
        k=s.index('id="faq"'); k=s.rfind('<section',0,k); s=s[:k]+fx+s[k:]
    open(f,'w').write(s)

# fix projects breadcrumb trailing slash
p=OUT+'/projects/index.html'; s=open(p).read().replace('Years<br data-astro-cid-aid3sr62>Experience','Serving<br data-astro-cid-aid3sr62>Clients').replace('</head>','<style>'+HDRFIX+'</style></head>',1).replace('"item": "https://www.trimoco.com/projects"}','"item": "https://www.trimoco.com/projects/"}'); open(p,'w').write(s)

# sitemap
sm=open(OUT+'/sitemap.xml').read()
add=''.join(f'<url><loc>{BASE}/projects/{g[0]}/</loc><priority>{"0.6" if len(g[2])>1 else "0.4"}</priority></url>' for g in GROUPS)
sm=re.sub(r'<url><loc>[^<]*/projects/[^<]+/</loc>.*?</url>','',sm).replace('</urlset>',add+'</urlset>')
open(OUT+'/sitemap.xml','w').write(sm)
json.dump([{'slug':g[0],'title':g[1],'photos':[PH[i]['file'] for i in g[2]],'orig_titles':[PH[i]['title'] for i in g[2]]} for g in GROUPS],open(ROOT+'/build/project-groups.json','w'),indent=1)
print(len(GROUPS),'project pages;',sum(1 for g in GROUPS if len(g[2])>1),'multi-photo')

# ── keep <img> width/height in step with the real pixel aspect (after photo rotation fixes) ──
def _fix_dims(html_s):
    n=[0]
    def rep(m):
        tag=m.group(0); f=m.group(2)
        try: W,H=Image.open(OUT+'/images/projects/'+m.group(1)+f).size
        except Exception: return tag
        mw=re.search(r' width="(\d+)"',tag); mh=re.search(r' height="(\d+)"',tag)
        if not (mw and mh): return tag
        w,h=int(mw.group(1)),int(mh.group(1))
        if abs(w/h - W/H) < 0.02: return tag
        nh=round(w*H/W) if W<H else h; nw=w if W<H else round(h*W/H)
        n[0]+=1
        return tag.replace(mw.group(0),f' width="{nw}"',1).replace(mh.group(0),f' height="{nh}"',1)
    return re.sub(r'<img [^>]*?src="/images/projects/((?:thumbs/)?)([^"]+)"[^>]*>',rep,html_s), n[0]
_tot=0
for _f in glob.glob(OUT+'/**/*.html',recursive=True):
    _s=open(_f).read(); _s2,_n=_fix_dims(_s)
    if _n: open(_f,'w').write(_s2); _tot+=_n
print('img dimension attrs corrected:',_tot)
