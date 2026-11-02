# trimoco.com — static site

Static rebuild of trimoco.com (Trimoco LLC, Lynbrook NY). Served by Render as a free static site from `public/`.

- `public/` — the deployed site (no build step).
- `build/build.py` + `build/content.py` — regenerate `public/` from the original-site mirror (`_orig/mirror`, kept off-repo).
- `build/forms.js` — quote form + chat widget send to info@trimoco.com via FormSubmit (first submission triggers a one-time activation email).
- `render.yaml` — Render config: security headers, caching, redirects.
- `README-TODO.md` — items only the owner can supply.
