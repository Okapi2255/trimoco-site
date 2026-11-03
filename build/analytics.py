# ---- Google Analytics 4 (owner approved Nov 2, 2026). Runs last: inject once into <head> of every HTML file.
GA_ID='G-E33S347W19'
GA_SNIPPET=('<script async src="https://www.googletagmanager.com/gtag/js?id='+GA_ID+'"></script>'
            '<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}'
            "gtag('js',new Date());gtag('config','"+GA_ID+"');</script>")
_n=0
for _f in glob.glob(OUT+'/**/*.html',recursive=True):
    _s=open(_f).read()
    if 'googletagmanager.com/gtag/js' in _s: continue
    _m=re.search(r'<head[^>]*>',_s)
    if _m: _s=_s[:_m.end()]+GA_SNIPPET+_s[_m.end():]
    elif '<meta charset="utf-8">' in _s: _s=_s.replace('<meta charset="utf-8">','<meta charset="utf-8">'+GA_SNIPPET,1)
    elif _s.lower().startswith('<!doctype html>'): _s=_s[:15]+GA_SNIPPET+_s[15:]
    else: continue
    open(_f,'w').write(_s); _n+=1
print('analytics: injected into',_n,'files')
