# Final pass: business base is Farmingdale, NY 11735 (town only; never publish a street address).
import re, glob, json, os
GEO={"@type":"GeoCoordinates","latitude":40.7326,"longitude":-73.4454}  # central Farmingdale village
TXT=[
 ('Trimoco LLC is a full-service general contractor based in Lynbrook, NY,','Trimoco LLC is a full-service general contractor based in Farmingdale, NY,'),
 ("We're based in Lynbrook and travel throughout the region.","We're based in Farmingdale and travel throughout the region."),
 ("We&#39;re based in Lynbrook and travel throughout the region.","We&#39;re based in Farmingdale and travel throughout the region."),
 ('Trimoco LLC is registered and operating out of Lynbrook, NY.','Trimoco LLC is based in Farmingdale, NY.'),
 ('Proudly Based in Lynbrook, NY','Proudly Based in Farmingdale, NY'),
 ('Map showing Trimoco LLC location in Lynbrook, NY','Map showing Farmingdale, NY, where Trimoco LLC is based'),
]
def fix_json(m):
    d=json.loads(m.group(1)); ch=False
    def walk(o):
        nonlocal ch
        if isinstance(o,dict):
            a=o.get('address')
            if isinstance(a,dict) and a.get('@type')=='PostalAddress' and (a.get('addressLocality')=='Lynbrook' or 'streetAddress' in a):
                o['address']={"@type":"PostalAddress","addressLocality":"Farmingdale","addressRegion":"NY","postalCode":"11735","addressCountry":a.get('addressCountry','US')}; ch=True
                if 'geo' in o: o['geo']=dict(GEO)
            if isinstance(o.get('areaServed'),list) and isinstance(o.get('@type'),list) and 'GeneralContractor' in o['@type']:
                names=[x.get('name') for x in o['areaServed'] if isinstance(x,dict)]
                for n in ['Farmingdale, NY','Lynbrook, NY']:
                    if n not in names: o['areaServed'].append({"@type":"Place","name":n}); ch=True
            for v in o.values(): walk(v)
        elif isinstance(o,list):
            for v in o: walk(v)
    walk(d)
    return '<script type="application/ld+json">'+json.dumps(d,ensure_ascii=False)+'</script>' if ch else m.group(0)
n=0
for f in glob.glob(OUT+'/**/*.html',recursive=True):
    s=open(f).read(); o=s
    s=re.sub(r'<script type="application/ld\+json">(.*?)</script>',fix_json,s,flags=re.S)
    for a,b in TXT: s=s.replace(a,b)
    s=re.sub(r'20 Concord Street\s+Lynbrook, NY 11563','Farmingdale, NY 11735',s)
    s=s.replace('Lynbrook, NY 11563','Farmingdale, NY 11735')
    s=re.sub(r'Our crew is based in Lynbrook, which puts us within a short drive of all (.*?) communities\.',r'Our crew is based in Farmingdale on Long Island, and we travel to jobs throughout \1.',s)
    if s!=o: open(f,'w').write(s); n+=1
print('farmingdale pass: files changed',n)
