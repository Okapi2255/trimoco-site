# Project gallery pages + clickable project photos. Run after build.py.
import re, os, json, html, glob
from PIL import Image
ROOT='/workspace/trimoco-site'; SRC=ROOT+'/_orig/mirror'; OUT=ROOT+'/public'; BASE='https://www.trimoco.com'
esc=lambda t: html.escape(t, quote=True)

orig=open(SRC+'/projects/index.html').read()
cards=re.findall(r'<article class="project-card"[^>]*aria-label="([^"]*)".*?<img src="/images/projects/(drive_[^"]*)" alt="([^"]*)".*?</article>',orig,re.S)
PH=[{'file':f,'title':html.unescape(t),'alt':html.unescape(a)} for t,f,a in cards]   # index = order on original /projects page
assert len(PH)==50

# Best-guess grouping by what is visible in the photos (same cabinets, stone, floors, windows, tile).
# Titles are taken from the original site's own card titles. Owner should confirm.
GROUPS=[
 ('kitchen-and-marble-bathroom-renovation','Kitchen and Marble Bathroom Renovation',[1,7,15,42,43,46,8,10,17,5,13,3,16]),
 ('modern-kitchen-and-dining-renovation','Modern Kitchen and Dining Renovation',[12,0,6]),
 ('kitchen-cabinetry-and-backsplash-installation','Kitchen Cabinetry and Backsplash Installation',[41,11,18,27]),
 ('green-kitchen-cabinetry-installation','Custom Kitchen Cabinetry Installation (Green Cabinets)',[31,33,23,26]),
 ('blue-kitchen-remodel-custom-cabinetry','Modern Kitchen Remodel with Custom Cabinetry (Blue Cabinets)',[49,45,48]),
 ('bathroom-renovation-walk-in-shower','Modern Bathroom Renovation with Walk-In Shower',[38,35,28,34,37]),
 ('master-bathroom-tile-renovation','Master Bathroom Tile Renovation',[9,20,21]),
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
    desc=f'{n} photo{"s" if n>1 else ""} of {title.lower()} by Trimoco LLC, a licensed general contractor serving Manhattan, Brooklyn, Queens, the Bronx and Long Island.'
    items=''.join(f'<figure class="m-0"><button type="button" class="pg-item" data-lb-index="{k}" aria-label="Enlarge photo {k+1} of {n}: {esc(PH[i]["alt"])}">{pic(PH[i]["file"],eager=k<3,alt=PH[i]["alt"])}</button><figcaption class="pg-cap">{esc(PH[i]["alt"])}</figcaption></figure>' for k,i in enumerate(ids))
    data=json.dumps([{'src':'/images/projects/'+PH[i]['file'],'alt':PH[i]['alt']} for i in ids])
    others=[g for g in GROUPS if g[0]!=sl and len(g[2])>1][:6]
    more=''.join(f'<a href="/projects/{o[0]}/" class="block no-underline group"><div class="relative rounded-xl overflow-hidden aspect-[4/3]">{cover(o)}<span class="proj-badge">{len(o[2])} photos</span></div><p class="mt-2 font-semibold text-text group-hover:text-accent">{esc(o[1])}</p></a>' for o in others)
    hero=(f'<section class="bg-dark-bg relative overflow-hidden py-[clamp(3.5rem,_7vw,_6rem)]" aria-label="Project header"><div class="container-site relative z-10">'
          f'<nav aria-label="Breadcrumb" class="flex items-center flex-wrap gap-x-2 gap-y-1 text-[0.8125rem] mb-6"><a href="/" class="text-text-on-dark-dim hover:text-accent-light no-underline">Home</a> {CHEV} <a href="/projects/" class="text-text-on-dark-dim hover:text-accent-light no-underline">Projects</a> {CHEV} <span aria-current="page" class="text-text-on-dark-muted">{esc(title)}</span></nav>'
          f'<span class="section-label section-label-dark">General Contractor</span><h1 class="text-[clamp(1.75rem,_4vw,_2.75rem)] font-bold text-text-on-dark leading-[1.15] mb-3">{esc(title)}</h1>'
          f'<p class="flex items-center gap-1.5 text-sm text-text-on-dark-muted mb-4">{PIN} Lynbrook, NY · {n} photo{"s" if n>1 else ""}</p>'
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
    gallery_ld={"@context":"https://schema.org","@type":"ImageGallery","name":title,"url":url,"description":desc,"author":{"@id":BASE+"/#business"},
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
    s=linkify(s)
    s=s.replace('<figure class="mb-8 overflow-hidden','<figure class="relative mb-8 overflow-hidden')
    s=s.replace('</head>',CSS[:7]+re.search(r'\.proj-link\{.*?(?=</style>)',CSS,re.S).group(0)+'</style></head>',1)
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
