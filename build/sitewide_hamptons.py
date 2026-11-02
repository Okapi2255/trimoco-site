# Site-wide Hamptons prominence pass. exec'd at the very end of build.py (after projects.py).
import re, glob, os, shutil
for old in ['east-hamptons-ny','west-hamptons-ny']:
    d=OUT+'/areas/'+old
    if os.path.isdir(d): shutil.rmtree(d)
SEP_RE=re.compile(r'(<span[^>]*>·</span> )$')
def add_hub_before_east(s):
    out=[]; pos=0
    for m in re.finditer(r'<a href="/areas/east-hampton/"[^>]*>.*?</a>',s,re.S):
        a=m.group(0)
        if 'data-hub' in s[max(0,m.start()-1500):m.start()] and '/areas/hamptons/' in s[max(0,m.start()-1500):m.start()]: continue
        if '/areas/hamptons/' in s[max(0,m.start()-300):m.start()]: continue  # hub link already right before this one
        hub=a.replace('href="/areas/east-hampton/"','href="/areas/hamptons/" data-hub',1).replace('East Hampton, NY','The Hamptons',1)
        hub=hub.replace('Amagansett, Springs, Montauk +2','Southampton, Sag Harbor, Montauk +6',1)
        sep=SEP_RE.search(s[max(0,m.start()-200):m.start()])
        out.append(s[pos:m.start()]+hub+(' '+sep.group(1) if sep else '')); pos=m.start()
    out.append(s[pos:]); return ''.join(out)
LI_FOOT=re.compile(r'(<li[^>]*>\s*)(<a href="/areas/long-island-ny/" class="text-\[0\.9rem\][^"]*"[^>]*>)\s*Long Island, NY\s*(</a>\s*</li>)')
def footer(s):
    m=LI_FOOT.search(s)
    if not m or 'href="/areas/hamptons/" class="text-[0.9rem]' in s: return s
    li=lambda u,n: m.group(1)+m.group(2).replace('/areas/long-island-ny/',u)+n+m.group(3)
    return s[:m.end()]+' '+li('/areas/hamptons/','The Hamptons')+' '+li('/areas/east-hampton/','East Hampton, NY')+' '+li('/areas/westhampton/','Westhampton &amp; Westhampton Beach')+s[m.end():]
HOME_BLOCK=('<!-- Hamptons spotlight (second focus) --> <div class="grid md:grid-cols-2 gap-10 bg-surface-raised border border-border rounded-xl p-8 md:p-12 mb-10 shadow-md reveal"> <div> <div class="flex flex-col gap-2 mb-4"> '
 '<span class="inline-flex self-start px-3 py-1 bg-secondary-light text-secondary text-[0.6875rem] font-semibold tracking-[0.1em] uppercase rounded-full">Second Homes &amp; Estates</span> <h3 class="text-[clamp(1.5rem,3vw,2rem)] font-bold text-text leading-[1.1]">The Hamptons</h3> </div> '
 '<p class="text-text-secondary leading-[1.65] mb-6">Kitchen, bath, tile, millwork, flooring and painting for second homes from Westhampton Beach to Montauk, scheduled for the off-season and managed with photo updates while you are in the city.</p> '
 '<div class="flex flex-wrap gap-2 mb-8">'+''.join(f'<span class="inline-flex px-3 py-1 bg-surface border border-border rounded-full text-[0.8125rem] text-text-secondary">{t}</span>' for t in ['East Hampton','Westhampton Beach','Southampton','Bridgehampton','Sag Harbor','Montauk'])+'</div> '
 '<div class="flex flex-wrap gap-3"><a href="/areas/hamptons/" class="btn-primary inline-flex items-center gap-2">Hamptons Services</a><a href="/areas/east-hampton/" class="btn-ghost">East Hampton</a><a href="/areas/westhampton/" class="btn-ghost">Westhampton</a></div> </div> '
 '<div class="hidden md:flex items-stretch" aria-hidden="true"> <div class="relative flex-1 min-h-[280px] overflow-hidden rounded-xl bg-dark-bg"> <img src="/images/service-areas/west-hamptons-ny.webp" alt="" width="640" height="420" loading="lazy" decoding="async" class="absolute inset-0 h-full w-full object-cover opacity-80"> '
 '<div class="absolute inset-0 bg-[linear-gradient(to_top,oklch(from_var(--color-overlay)_l_c_h/0.76),transparent_70%)]"></div> <div class="absolute inset-x-0 bottom-0 p-7 text-text-on-dark"> <p class="text-xs font-semibold tracking-[0.12em] uppercase text-accent-on-dark mb-2 max-w-none">East End</p> <p class="font-heading text-2xl font-bold leading-tight max-w-[14ch]">East Hampton to Westhampton Beach.</p> </div> </div> </div> </div> ')
LI_BLOCK=('<!-- ─── HAMPTONS LINKS ─── --> <section class="section-pad" aria-labelledby="li-hamptons-heading"> <div class="container-site"> <div class="max-w-[720px] mb-8 reveal"> <span class="section-label">Heading east</span> <h2 id="li-hamptons-heading" class="font-heading text-[clamp(1.75rem,_4vw,_2.5rem)] font-bold mb-3">Renovating a house in the Hamptons?</h2> <span class="accent-bar"></span> '
 '<p class="text-base text-text-secondary leading-[1.75] mt-6">We also take on kitchen, bathroom and interior projects on the East End, scheduled around the season for second homes. See our Hamptons pages for how we plan that work.</p> </div> '
 '<div class="grid grid-cols-1 md:grid-cols-3 gap-4"> <a href="/areas/hamptons/" class="card px-6 py-5 no-underline group"><span class="block font-heading text-lg font-bold text-text group-hover:text-accent">The Hamptons</span><span class="block text-sm text-text-secondary mt-1">Second-home renovations from Westhampton to Montauk</span></a> '
 '<a href="/areas/east-hampton/" class="card px-6 py-5 no-underline group"><span class="block font-heading text-lg font-bold text-text group-hover:text-accent">East Hampton</span><span class="block text-sm text-text-secondary mt-1">East Hampton Village, Amagansett, Springs, Montauk</span></a> '
 '<a href="/areas/westhampton/" class="card px-6 py-5 no-underline group"><span class="block font-heading text-lg font-bold text-text group-hover:text-accent">Westhampton &amp; Westhampton Beach</span><span class="block text-sm text-text-secondary mt-1">Plus Quogue, Remsenburg and Hampton Bays</span></a> </div> </div> </section> ')
n=0
for f in glob.glob(OUT+'/**/*.html',recursive=True):
    s=open(f).read(); o=s
    s=s.replace('Long Island, NY, East Hamptons, NY, West Hamptons, NY.','Long Island, NY, and the Hamptons, including East Hampton, Westhampton, Westhampton Beach and Southampton.')
    s=s.replace('/areas/east-hamptons-ny/','/areas/east-hampton/').replace('/areas/west-hamptons-ny/','/areas/westhampton/')
    s=s.replace('/areas/east-hamptons-ny"','/areas/east-hampton/"').replace('/areas/west-hamptons-ny"','/areas/westhampton/"')
    s=s.replace('East Hamptons, NY','East Hampton, NY').replace('West Hamptons, NY','Westhampton, NY')
    s=s.replace('East Hampton, Southampton, Bridgehampton +1','Amagansett, Springs, Montauk +2').replace('Westhampton, Westhampton Beach, Quogue +1','Westhampton Beach, Quogue, Remsenburg +2')
    if '/areas/hamptons/" data-hub' not in s: s=add_hub_before_east(s)
    s=footer(s)
    rel=os.path.relpath(f,OUT)
    if rel=='index.html' and 'Hamptons spotlight' not in s:
        s=s.replace('<!-- Other areas grid -->',HOME_BLOCK+'<!-- Other areas grid -->',1)
        s=s.replace('Based in Farmingdale — serving Manhattan, Brooklyn, Queens, the Bronx and Long Island.','Based in Farmingdale — serving Manhattan first, plus the Hamptons, Brooklyn, Queens, the Bronx and Long Island.')
    if rel=='areas/long-island-ny/index.html' and 'li-hamptons-heading' not in s:
        s=s.replace('<!-- ─── LOCAL GUIDE (added for SEO) ─── -->',LI_BLOCK+'<!-- ─── LOCAL GUIDE (added for SEO) ─── -->',1)
    if rel=='404.html' and '/areas/hamptons/" class="btn-ghost"' not in s:
        s=s.replace('<a href="/areas/manhattan-ny/" class="btn-ghost">Manhattan</a>','<a href="/areas/manhattan-ny/" class="btn-ghost">Manhattan</a><a href="/areas/hamptons/" class="btn-ghost">The Hamptons</a>',1)
    if s!=o: open(f,'w').write(s); n+=1
print('hamptons sitewide pass: files changed',n)
