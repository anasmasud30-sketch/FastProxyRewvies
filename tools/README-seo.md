# Fast Proxy Reviews — programmatic SEO library

`tools/generate_seo_content.py` builds a ~20,000-page programmatic SEO library
around this site's **speed / fastest-proxy** angle, in the Medic Care (TemplateMo
566) light theme. Every page links `../style.css` and reuses the site's real
classes, so it inherits the theme for free — no per-page CSS.

## Regenerate

```
py tools/generate_seo_content.py
```

(Interpreter is `py` on this Windows box, not `python`.) Fast — the full 20k run
is well under a minute of file I/O. Env overrides for dry-runs:
`SEO_TARGET` (default 20000), `SEO_OUT` (seo dir), `SEO_SITEROOT` (root outputs).

The generator is **idempotent**: at the start of each run it deletes `seo/*.html`,
`content-library*.html`, and `sitemap-*.xml`, then rewrites everything. **Never
hand-edit generated files** — edit the generator and re-run.

## What it emits (at the site root)

- `seo/*.html` — 20,000 long-form pages (all `index,follow`)
- `content-library-{cluster}-{n}.html` — 419 paginated cluster hubs (48 cards each)
- `content-library.html` — the library index (hub of hubs)
- `sitemap.xml` — a **sitemap index** → `sitemap-1..3.xml` (≤10k URLs each; 20,430 total)
- `robots.txt` — points at the sitemap index
- `seo-library-manifest.json` — the full spec list

## Clusters (6, all index,follow)

| Cluster | Pattern | Count |
|---|---|---|
| Speed Reviews | Fastest {type} proxies for {use-case} in {country} | 7,000 |
| Speed Comparisons | {A} vs {B} speed for {use-case} in {country} | 5,500 |
| Platform Speed | Fastest {type} proxies for {platform} in {country} | 3,000 |
| Latency Guides | {type} proxy {speed-topic} in {country} | 2,000 |
| Country Speed | Fastest {type} proxies in {country} | 1,500 |
| City Speed | Fastest {type} proxies in {city} | 1,000 |

Each page: unique title/meta/keywords, ~15 speed-focused sections (comparison
pages use a distinct 10-section template), comparison tables, an FAQ, a 6-item
related-link mesh, breadcrumb, and **Article + BreadcrumbList + FAQPage** JSON-LD.
All funnel to the featured value pick **Cheapest Proxies**
(`https://cheapest-proxies.com/`, `rel="noopener nofollow sponsored"`).

## Vocab rule (append-only)

To add coverage, **append** to the ends of `PROXY_TYPES`, `USE_CASES`,
`PLATFORMS`, `GEOS`, `CITIES`, etc. — never insert/reorder (the phased builder
keeps earlier slugs stable). `main()` asserts global slug uniqueness.

## Site integration

A **Library** link was added to the header nav (`index.html`, `blog/_top.php`) and
a **Speed Library** link to the footer "Pages" column on every static page +
`blog/_bottom.php`; the homepage has a Speed Library promo section. Generated
pages carry the same nav/footer via the generator's `header()`/`footer()`.

## Deploy (cPanel)

`/seo/` is ~20k files — **confirm the host's inode limit** allows ~21k extra
files. Upload `seo/`, `content-library*.html`, `sitemap*.xml`, `robots.txt`,
`seo-library-manifest.json` (and the updated `style.css` + static pages) to the
web root.
