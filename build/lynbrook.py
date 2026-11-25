# Final pass: business base is 20 Concord St, Lynbrook, NY 11563 (street may be shown publicly).
# Keep Farmingdale in areaServed and in Long Island town/service-area lists.
import re, glob, json, os

GEO = {"@type": "GeoCoordinates", "latitude": 40.66305, "longitude": -73.68527}
FARMINGDALE_GEO = {(40.7326, -73.4454), (40.66296, -73.68539)}
BUSINESS_LOCALITIES = {"Farmingdale"}
BUSINESS_POSTALS = {"11735"}

TXT = [
    ("based in Farmingdale, NY 11735", "based at 20 Concord St, Lynbrook, NY 11563"),
    ("Farmingdale, NY 11735", "20 Concord St, Lynbrook, NY 11563"),
    ("Farmingdale-based", "Lynbrook-based"),
    ("a Farmingdale, NY general contractor", "a Lynbrook, NY general contractor"),
    ("the Farmingdale, NY general contractor", "the Lynbrook, NY general contractor"),
    ("from Trimoco LLC in Farmingdale, NY", "from Trimoco LLC in Lynbrook, NY"),
    ("Proudly Based in Farmingdale, NY", "Proudly Based in Lynbrook, NY"),
    ("Based in Farmingdale —", "Based in Lynbrook —"),
    ("Based in Farmingdale, NY.", "Based in Lynbrook, NY."),
    ("based in Farmingdale, NY", "based in Lynbrook, NY"),
    ("based in Farmingdale, Long Island", "based in Lynbrook, Long Island"),
    ("based in Farmingdale and", "based in Lynbrook and"),
    ("based in Farmingdale on Long Island", "based in Lynbrook on Long Island"),
    ("based in Farmingdale, so", "based in Lynbrook, so"),
    ("our base in Farmingdale", "our base in Lynbrook"),
    ("serving Farmingdale, NY since 2021", "serving Lynbrook, NY since 2021"),
    ("based in Farmingdale", "based in Lynbrook"),
    (
        "https://maps.google.com/maps?q=Farmingdale,+NY+11735&amp;output=embed",
        "https://maps.google.com/maps?q=20+Concord+St,+Lynbrook,+NY+11563&amp;output=embed",
    ),
    (
        'title="Map showing Farmingdale, NY, where Trimoco LLC is based"',
        'title="Map showing Trimoco LLC location at 20 Concord St, Lynbrook, NY"',
    ),
]


def _is_business_address(a):
    if not isinstance(a, dict) or a.get("@type") != "PostalAddress":
        return False
    return a.get("addressLocality") in BUSINESS_LOCALITIES or a.get("postalCode") in BUSINESS_POSTALS


def _is_farmingdale_geo(g):
    if not isinstance(g, dict):
        return False
    try:
        lat = float(g.get("latitude"))
        lng = float(g.get("longitude"))
    except (TypeError, ValueError):
        return False
    return (lat, lng) in FARMINGDALE_GEO or (abs(lat - 40.7326) < 1e-6 and abs(lng + 73.4454) < 1e-6)


def fix_json(m):
    d = json.loads(m.group(1))
    ch = False

    def walk(o):
        nonlocal ch
        if isinstance(o, dict):
            a = o.get("address")
            if _is_business_address(a):
                country = a.get("addressCountry", "US")
                o["address"] = {
                    "@type": "PostalAddress",
                    "streetAddress": "20 Concord St",
                    "addressLocality": "Lynbrook",
                    "addressRegion": "NY",
                    "postalCode": "11563",
                    "addressCountry": country,
                }
                ch = True
                if "geo" in o:
                    o["geo"] = dict(GEO)
            elif _is_farmingdale_geo(o.get("geo")):
                o["geo"] = dict(GEO)
                ch = True
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    walk(d)
    return (
        '<script type="application/ld+json">' + json.dumps(d, ensure_ascii=False) + "</script>"
        if ch
        else m.group(0)
    )


def apply_text(s):
    for a, b in TXT:
        s = s.replace(a, b)
    return s


root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = globals().get("OUT", os.path.join(root, "public"))

n = 0
for f in glob.glob(out + "/**/*", recursive=True):
    if not (f.endswith(".html") or f.endswith(".txt") or f.endswith(".xml") or f.endswith(".json")):
        continue
    # skip binary-ish or reviews feed
    try:
        s = open(f, encoding="utf-8").read()
    except (UnicodeDecodeError, OSError):
        continue
    o = s
    if f.endswith(".html"):
        s = re.sub(r'<script type="application/ld\+json">(.*?)</script>', fix_json, s, flags=re.S)
    s = apply_text(s)
    if s != o:
        open(f, "w", encoding="utf-8").write(s)
        n += 1
print("lynbrook pass: files changed", n)
