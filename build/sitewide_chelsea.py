# Site-wide Chelsea area-page links. exec'd from build.py after sitewide_hamptons.py.
# Idempotent: skips a pattern if the Chelsea href is already present in that list.
import re, glob, os

CH = '/areas/chelsea-manhattan/'
LABEL = 'Chelsea, Manhattan'

def _after_first(s, needle, insert, already):
    if already in s and s.find(already) < s.find(needle)+len(needle)+len(insert)+80:
        # rough; callers pass a tighter already-check
        pass
    if needle not in s:
        return s
    # only insert after first occurrence if insert snippet not already immediately after this needle anywhere
    out=[]; pos=0
    for m in re.finditer(re.escape(needle), s):
        # if chelsea already appears shortly after this manhattan item, skip
        window=s[m.end():m.end()+450]
        if CH in window and LABEL in window:
            continue
        out.append(s[pos:m.end()]+insert); pos=m.end()
    out.append(s[pos:]); return ''.join(out)

def add_links(s):
    if CH in s and s.count('href="'+CH+'"')>=3:
        # still run each pattern; idempotent
        pass

    # Footer
    foot_m = '<li> <a href="/areas/manhattan-ny/" class="text-[0.9rem] text-text-footer no-underline transition-colors duration-150 hover:text-accent-light">Manhattan, NY</a> </li>'
    foot_c = '<li> <a href="'+CH+'" class="text-[0.9rem] text-text-footer no-underline transition-colors duration-150 hover:text-accent-light">'+LABEL+'</a> </li>'
    s=_after_first(s, foot_m, foot_c, foot_c)

    # Desktop header dropdown
    desk_m = ('<a href="/areas/manhattan-ny/" class="flex items-center gap-2.5 px-4 py-2 text-[0.9375rem] font-medium text-text-secondary rounded-md no-underline transition-colors duration-150 hover:text-accent hover:bg-accent-light capitalize" data-astro-cid-3ef6ksr2> '
              '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="shrink-0 text-text-muted" aria-hidden="true" data-astro-cid-3ef6ksr2> '
              '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" data-astro-cid-3ef6ksr2></path> '
              '<circle cx="12" cy="10" r="3" data-astro-cid-3ef6ksr2></circle> </svg> Manhattan, NY </a>')
    desk_c = desk_m.replace('/areas/manhattan-ny/', CH).replace('Manhattan, NY', LABEL)
    s=_after_first(s, desk_m, desk_c, desk_c)

    # Mobile menu (py-2.5 + trailing chevron)
    mob_m = ('<a href="/areas/manhattan-ny/" class="flex items-center gap-2.5 px-4 py-2.5 text-[0.9375rem] font-medium text-text-secondary rounded-md no-underline transition-colors duration-150 hover:bg-accent-light hover:text-accent capitalize" data-astro-cid-3ef6ksr2> '
             '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="shrink-0 text-text-muted" aria-hidden="true" data-astro-cid-3ef6ksr2> '
             '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" data-astro-cid-3ef6ksr2></path> '
             '<circle cx="12" cy="10" r="3" data-astro-cid-3ef6ksr2></circle> </svg> '
             '<span class="flex-1" data-astro-cid-3ef6ksr2>Manhattan, NY</span> '
             '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="shrink-0 opacity-40" aria-hidden="true" data-astro-cid-3ef6ksr2> '
             '<line x1="5" y1="12" x2="19" y2="12" data-astro-cid-3ef6ksr2></line>'
             '<polyline points="12 5 19 12 12 19" data-astro-cid-3ef6ksr2></polyline> </svg> </a>')
    mob_c = mob_m.replace('/areas/manhattan-ny/', CH).replace('Manhattan, NY', LABEL)
    s=_after_first(s, mob_m, mob_c, mob_c)

    # Compact "Serving A · B · C" header line
    tiny_m = '<a href="/areas/manhattan-ny/" class="text-[0.8125rem] text-text-secondary no-underline hover:text-accent transition-colors duration-150 capitalize" data-astro-cid-3ef6ksr2>Manhattan, NY</a>'
    tiny_c = (' <span class="text-text-muted select-none" aria-hidden="true" data-astro-cid-3ef6ksr2>·</span> '
              '<a href="'+CH+'" class="text-[0.8125rem] text-text-secondary no-underline hover:text-accent transition-colors duration-150 capitalize" data-astro-cid-3ef6ksr2>'+LABEL+'</a>')
    s=_after_first(s, tiny_m, tiny_c, 'href="'+CH+'" class="text-[0.8125rem] text-text-secondary')

    # Service subpage lists (li + pin)
    sm_m = ('<a href="/areas/manhattan-ny/" class="flex items-center gap-2 text-sm font-medium text-text-secondary py-[0.375rem] transition-colors duration-150 no-underline hover:text-accent"> '
            '<svg class="text-text-muted shrink-0" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"> '
            '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path> <circle cx="12" cy="10" r="3"></circle> </svg> '
            '<span class="min-w-0 capitalize">Manhattan, NY</span> </a>')
    sm_c = sm_m.replace('/areas/manhattan-ny/', CH).replace('Manhattan, NY', LABEL)
    # these sit in <li> ... </li>
    s=s.replace(sm_m+' </li>', sm_m+' </li><li> '+sm_c+' </li>')

    # Category index simple text links
    cat_m = '<a href="/areas/manhattan-ny/" class="text-sm text-text-secondary no-underline hover:text-accent transition-colors duration-150 capitalize">Manhattan, NY</a>'
    cat_c = '<a href="'+CH+'" class="text-sm text-text-secondary no-underline hover:text-accent transition-colors duration-150 capitalize">'+LABEL+'</a>'
    s=_after_first(s, cat_m, cat_c, cat_c)

    # Other-service-area pills on area pages (manhattan page omits itself, so insert before Brooklyn)
    pill_b = ('<li> <a href="/areas/brooklyn-ny/" class="inline-flex items-center gap-1.5 py-[0.35rem] px-3 text-[0.8125rem] font-medium text-text-secondary bg-surface border border-border rounded-full no-underline hover:border-accent hover:text-accent transition-colors duration-150 capitalize"> '
              '<svg class="text-text-muted shrink-0" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"> '
              '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path> <circle cx="12" cy="10" r="3"></circle> </svg> Brooklyn, NY </a> </li>')
    pill_c = pill_b.replace('/areas/brooklyn-ny/', CH).replace('Brooklyn, NY', LABEL)
    if 'href="'+CH+'" class="inline-flex items-center gap-1.5 py-[0.35rem] px-3' not in s and pill_b in s:
        s=s.replace(pill_b, pill_c+pill_b, 1)

    return s

def publish_chelsea_page(s):
    s=s.replace('<meta name="robots" content="noindex, nofollow">','',1)
    s=s.replace('<span class="section-label section-label-dark">Draft — not published</span>',
                '<span class="section-label section-label-dark">Service Area</span>',1)
    return s

# Owner correction (Nov 25, 2026): this job is a custom radiator cover only — not a window seat.
# Rewrite any leftover old slug so a later rebuild cannot restore it.
OLD_RAD_SLUG='chelsea-manhattan-window-seat-radiator-cover'
NEW_RAD_SLUG='chelsea-manhattan-radiator-cover'

n=0
for f in glob.glob(OUT+'/**/*.html',recursive=True):
    s=open(f).read(); o=s
    s=s.replace('/projects/'+OLD_RAD_SLUG,'/projects/'+NEW_RAD_SLUG)
    rel=os.path.relpath(f,OUT)
    if rel=='areas/chelsea-manhattan/index.html':
        s=publish_chelsea_page(s)
    s=add_links(s)
    if rel=='areas/manhattan-ny/index.html':
        s=s.replace('<li class="badge">Chelsea</li>',
                    '<li class="badge"><a href="'+CH+'" class="no-underline hover:text-accent">Chelsea</a></li>',1)
    if rel=='index.html' and 'href="'+CH+'" class="btn-ghost">Chelsea' not in s:
        # Ghost button next to the Manhattan spotlight CTA, matching the Hamptons East Hampton button
        s, nsub = re.subn(
            r'(<a href="/areas/manhattan-ny/" class="btn-primary inline-flex items-center gap-2">\s*Manhattan, NY Services\s*<svg[^>]*>.*?</svg>\s*</a>)',
            r'<div class="flex flex-wrap gap-3">\1<a href="'+CH+'" class="btn-ghost">Chelsea</a></div>',
            s, count=1, flags=re.S)
        if not nsub:
            pass  # leave unchanged if the CTA markup moved
    # Five Chelsea project pages: link the hero location line (other neighborhoods have no area page to link)
    if rel.startswith('projects/chelsea-manhattan-') and rel.endswith('/index.html'):
        old='</svg> Chelsea, Manhattan · '
        new='</svg> <a href="'+CH+'" class="text-text-on-dark-muted hover:text-accent-light no-underline">Chelsea, Manhattan</a> · '
        if old in s and 'href="'+CH+'" class="text-text-on-dark-muted' not in s:
            s=s.replace(old, new, 1)
    if s!=o:
        open(f,'w').write(s); n+=1
print('chelsea sitewide pass: files changed', n)
