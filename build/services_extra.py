# Painting / Plaster & Skim Coating / Drywall: surface them sitewide (nav, home grid, category grid, footer, schema)
# and upgrade the existing /services/carpenter/drywall-and-framing/ page instead of duplicating it.
# Rules: no invented jobs, reviews or credentials; only the NYC DCWP license already on the site.
import re, json, glob, html as _html
from content import SERVICES as _SV
RR='/services/general-contractor/residential-remodeling/'
NEW_NAV=[('/services/general-contractor/interior-painting/','Interior Painting'),
         ('/services/general-contractor/plaster-and-skim-coating/','Plaster & Skim Coating')]
FOOT=[('/services/general-contractor/interior-painting/','Painting'),
      ('/services/general-contractor/plaster-and-skim-coating/','Plaster & Skim Coating'),
      ('/services/carpenter/drywall-and-framing/','Drywall')]
SVMAP={x['slug']:x for x in _SV}
DW='/services/carpenter/drywall-and-framing/'

def _clone(block,href,label):
    b=block.replace(RR,href,1)
    b=re.sub(r'Residential Remodeling',_html.escape(label),b,count=1)
    return b.replace('<a href=','<a data-svc-extra href=',1)

def nav(s):
    if 'data-svc-extra' in s: return s
    pats=[r'<li data-astro-cid-[a-z0-9]+> <a href="'+re.escape(RR)+r'" class="block px-2 py-2.*?</a> </li>',
          r'<li class="m-0 p-0"> <a href="'+re.escape(RR)+r'".*?</a> </li>',
          r'<a href="'+re.escape(RR)+r'" class="flex items-center justify-between.*?</a>']
    for p in pats:
        s=re.sub(p,lambda m:m.group(0)+''.join(_clone(m.group(0),h,l) for h,l in NEW_NAV),s,flags=re.S)
    # footer services column
    s=re.sub(r'(<li> <a href="/services/plumber/" class="(text-\[0\.9rem\] text-text-footer[^"]*)">Plumber</a> </li>)',
             lambda m:m.group(1)+''.join(f'<li> <a href="{h}" class="{m.group(2)}">{_html.escape(l)}</a> </li>' for h,l in FOOT),s,count=1)
    return s

def category_cards(s):
    m=re.search(r'<a href="'+re.escape(RR)+r'" class="card group flex flex-col.*?</a>',s,re.S)
    if not m or 'data-svc-card' in s: return s
    blk=m.group(0); out=''
    for slug in ('interior-painting','plaster-and-skim-coating'):
        sv=SVMAP[slug]; b=blk.replace(RR,f'/services/general-contractor/{slug}/',1).replace('<a href=','<a data-svc-card href=',1)
        img=resolve_img(sv['img'])
        b=re.sub(r'<img src="[^"]*" alt="[^"]*" title="[^"]*"',f'<img src="{img}" alt="{esc(sv["img_alt"])}" title="{esc(sv["img_alt"])}"',b,count=1)
        b=re.sub(r'(<h3[^>]*>)[^<]*(</h3>)',lambda x:x.group(1)+esc(sv['name'])+x.group(2),b,count=1)
        b=re.sub(r'(<p class="text-\[0\.9rem\][^>]*>)[^<]*(</p>)',lambda x:x.group(1)+esc(sv['lead'])+x.group(2),b,count=1)
        lis=re.findall(r'(<li class="flex items-start gap-2[^>]*>\s*<svg.*?</svg>)\s*[^<]*?(</li>)',b,re.S)
        items=iter(sv['benefits'][:3])
        b=re.sub(r'(<li class="flex items-start gap-2[^>]*>\s*<svg.*?</svg>)\s*[^<]*?\s*(</li>)',lambda x:x.group(1)+' '+esc(next(items,''))+' '+x.group(2),b,flags=re.S)
        out+=b
    return s.replace(blk,blk+out,1)

OFFERS=[('Interior Painting','Interior painting of walls, ceilings, trim and doors for Manhattan apartments and homes across NYC, the Hamptons and Long Island.'),
        ('Plaster Repair and Skim Coating','Plaster crack repair, skim coating and veneer plaster for pre-war apartments, brownstones and older homes.'),
        ('Drywall Installation and Repair','Drywall hanging, taping, finishing and repair, plus wood and metal stud framing.')]
def schema(s):
    def upd(m):
        d=json.loads(m.group(1))
        cat=d.get('hasOfferCatalog')
        if isinstance(cat,dict) and isinstance(cat.get('itemListElement'),list):
            have={o.get('itemOffered',{}).get('name') for o in cat['itemListElement']}
            cat['itemListElement']+=[{"@type":"Offer","itemOffered":{"@type":"Service","name":n,"description":t}} for n,t in OFFERS if n not in have]
        return '<script type="application/ld+json">'+json.dumps(d,ensure_ascii=False)+'</script>'
    return re.sub(r'<script type="application/ld\+json">(.*?)</script>',upd,s,flags=re.S)

AREA_LINE=('<p class="text-[0.9375rem] text-text-secondary mt-6 mb-0">Walls and finishes: '
           '<a href="/services/general-contractor/interior-painting/" class="text-accent underline underline-offset-2">interior painting</a>, '
           '<a href="/services/general-contractor/plaster-and-skim-coating/" class="text-accent underline underline-offset-2">plaster repair and skim coating</a> and '
           '<a href="/services/carpenter/drywall-and-framing/" class="text-accent underline underline-offset-2">drywall installation and repair</a>.</p>')
def area(s):
    if 'id="area-guide-heading"' not in s or 'Walls and finishes:' in s: return s
    k=s.find('id="area-guide-heading"'); j=s.find('<p class="text-sm text-text-muted mt-6">',k)
    return s[:j]+AREA_LINE+' '+s[j:] if j>0 else s

# ---- drywall page upgrade
DW_TITLE='Drywall Installation & Repair in Manhattan, NY | Trimoco LLC'
DW_DESC='Drywall installation, framing, taping, finishing and repair for Manhattan apartments, Hamptons homes and NYC co-ops. Free estimates: (516) 787-1045.'
DW_NAME='Drywall Installation, Framing and Repair'
DW_LEAD='Trimoco LLC hangs, tapes, finishes and repairs drywall, and frames new walls, in Manhattan apartments and co-ops and in homes across the Hamptons, Brooklyn, Queens, the Bronx and Long Island.'
DW_GUIDE={
 'label':'Drywall in NYC and Long Island',
 'h2':'Drywall installation, taping, finishing and repair',
 'paras':[
  'We handle the whole drywall job: framing with wood or metal studs, hanging the board, then taping, applying joint compound and sanding to a finish that is ready for paint. In <a href="/areas/manhattan-ny/">Manhattan</a> co-ops and condos, we follow the building\'s work hours, protect hallways and elevators, and provide the certificate of insurance the building asks for. In pre-war apartments, we often tie new drywall into existing <a href="/services/general-contractor/plaster-and-skim-coating/">plaster walls</a>, so the joint between old and new disappears.',
  'Repairs are a big part of the work: holes, cracks, nail pops, openings left by plumbers and electricians, and walls or ceilings damaged by a leak. Once the patch is finished, we can <a href="/services/general-contractor/interior-painting/">paint</a> the wall so it matches the room. We do drywall in <a href="/areas/hamptons/">the Hamptons</a>, <a href="/areas/brooklyn-ny/">Brooklyn</a>, <a href="/areas/queens-ny/">Queens</a>, <a href="/areas/bronx-ny/">the Bronx</a> and across <a href="/areas/long-island-ny/">Long Island</a>, as well as Manhattan.',
 ],
 'list_title':'Drywall work we handle',
 'bullets':[
  'New walls and ceilings framed with wood or metal studs and hung with drywall',
  'Taping, joint compound and sanding to the finish level the room needs, up to a Level 5 skim for smooth, even walls',
  'Patches for holes, cracks, nail pops and openings left after plumbing and electrical work',
  'Water-damaged drywall cut out and replaced once the leak is fixed',
  'Moisture-resistant board in bathrooms and cement board behind shower tile',
  'Fire-rated and sound-reducing wall assemblies where the building or code calls for them',
 ],
}
DW_RELATED=['chelsea-manhattan-bathroom-renovation','soho-manhattan-bathroom-walk-in-shower','chelsea-manhattan-window-seat-radiator-cover','chelsea-manhattan-double-closet-doors']
DW_FAQS=[
 ('Do you do small drywall repairs?','Yes. We patch holes, cracks and nail pops, close up openings left by plumbers and electricians, and replace water-damaged sections. Small repairs are often paired with painting so the patch blends into the wall.'),
 ('What does drywall taping and finishing involve?','After the board is hung, the joints are covered with tape and several coats of joint compound, and each coat dries and is sanded before the next. This is what makes the seams and screws disappear, so taping and finishing usually takes a few days even in a small room.'),
 ('What is a Level 5 drywall finish?','It is the smoothest standard finish: after normal taping, a thin skim coat of compound goes over the entire wall. It is worth it for walls hit by strong side light or painted in a glossy finish, where small flaws would otherwise show.'),
 ('Do you install drywall in the Hamptons and on Long Island?','Yes. We hang, finish and repair drywall in the Hamptons, including East Hampton and Westhampton, and in homes across Long Island, as well as in Manhattan, Brooklyn, Queens and the Bronx.'),
]
def drywall(s):
    s=re.sub(r'<title>.*?</title>',f'<title>{esc(DW_TITLE)}</title>',s,flags=re.S)
    s=re.sub(r'(<meta (?:property="og:title"|name="twitter:title") content=")[^"]*',lambda m:m.group(1)+esc(DW_TITLE),s)
    s=re.sub(r'(<meta (?:name="description"|property="og:description"|name="twitter:description") content=")[^"]*',lambda m:m.group(1)+esc(DW_DESC),s)
    s=s.replace('<span class="capitalize">Drywall and Framing</span> in Manhattan, NY </h1>','<span class="capitalize">Drywall Installation &amp; Repair</span> in Manhattan, NY </h1>',1)
    s=re.sub(r'(<h1.*?</h1> <p class="text-\[1\.0625rem\] text-text-on-dark[^>]*>)\s*Trimoco LLC provides drywall and framing services for apartments and co-ops across Manhattan\.',lambda m:m.group(1)+' '+esc(DW_LEAD),s,count=1,flags=re.S)
    s=s.replace('<!-- FAQ for this service -->',guide_section(DW_GUIDE,DW_RELATED)+'<!-- FAQ for this service -->',1)
    s=add_faqs(s,DW_FAQS,'d')
    def upd(m):
        d=json.loads(m.group(1))
        if d.get('@type')=='Service': d['name']=DW_NAME; d['description']=DW_LEAD
        return '<script type="application/ld+json">'+json.dumps(d,ensure_ascii=False)+'</script>'
    return re.sub(r'<script type="application/ld\+json">(.*?)</script>',upd,s,flags=re.S)

for f in glob.glob(OUT+'/**/*.html',recursive=True):
    s=open(f).read(); o=s
    s=nav(s); s=schema(s); s=area(s)
    rel=f.replace(OUT,'')
    if rel=='/services/general-contractor/index.html': s=category_cards(s)
    if rel==DW+'index.html': s=drywall(s)
    if s!=o: open(f,'w').write(s)
print('services_extra: done')
