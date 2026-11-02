# Optional copy tweaks, staged for owner approval. Drop this commit (or set a flag to False) to leave them out.
ABOUT_HERO_FARMINGDALE=True     # About hero: "serving Lynbrook, NY since 2021" -> "serving Farmingdale, NY since 2021"
PROJECTS_H1_MANHATTAN=True      # /projects/ H1: "... Across Long Island" -> "... Across Manhattan & Long Island"
def _edit(rel,fn):
    p=OUT+rel; s=open(p).read(); n=fn(s)
    if n==s: print('copy_tweaks: no change in',rel)
    else: open(p,'w').write(n)
if ABOUT_HERO_FARMINGDALE:
    _edit('/about/index.html',lambda s:s.replace('</span> serving Lynbrook, NY since 2021 </h1>','</span> serving Farmingdale, NY since 2021 </h1>',1))
if PROJECTS_H1_MANHATTAN:
    _edit('/projects/index.html',lambda s:s.replace('Projects Across<br class="hidden sm:block" data-astro-cid-aid3sr62> Long Island </h1>','Projects Across<br class="hidden sm:block" data-astro-cid-aid3sr62> Manhattan &amp; Long Island </h1>',1))
print('copy_tweaks: done')
