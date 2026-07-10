from __future__ import annotations

"""
Fast Proxy Reviews - programmatic SEO library generator.

Adapted from the cheapestproxydeals.com engine, re-pointed at this site's
"Medic Care" (TemplateMo 566) light theme and a SPEED / fastest-proxy content
model. Emits ~20,000 long-form speed-review pages under /seo/, paginated
content-library hub pages, a sitemap index, and a manifest. Every page links
../style.css and reuses the site's real classes, so it inherits the theme for
free. See tools/README-seo.md.

Run:  py tools/generate_seo_content.py       (interpreter is `py` on this box)
Env:  SEO_TARGET (default 20000), SEO_OUT (seo dir), SEO_SITEROOT (root outputs)
"""

import json
import os
import re
from collections import defaultdict
from dataclasses import dataclass, asdict
from datetime import date, timedelta
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE_OUT = Path(os.environ.get("SEO_SITEROOT", str(ROOT)))
OUT_DIR = Path(os.environ.get("SEO_OUT", str(SITE_OUT / "seo")))
SITE = "https://fastproxyreviews.com"
DEAL_URL = "https://cheapest-proxies.com/"
DEAL_NAME = "Cheapest Proxies"
DEAL_REL = "noopener nofollow sponsored"
TODAY = date(2026, 7, 7)

TARGET = int(os.environ.get("SEO_TARGET", "20000"))
CARDS_PER_HUB = int(os.environ.get("SEO_CARDS_PER_HUB", "48"))
SITEMAP_CHUNK = 10000


@dataclass(frozen=True)
class PageSpec:
    idx: int
    title: str
    slug: str
    category: str
    focus: str
    ptype: str
    use_case: str
    geo: str
    platform: str
    speed: str
    audience: str
    mode: str
    angle: str
    intent: str
    modified: str
    description: str
    keywords: tuple[str, ...]


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"&", " and ", text)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def pick(items: list[str], idx: int, offset: int = 0) -> str:
    return items[(idx + offset) % len(items)]


def e(value: object) -> str:
    return escape(str(value), quote=True)


def meta_description(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= 158:
        return text
    cut = text[:155].rsplit(" ", 1)[0]
    return f"{cut}..."


# ---------------------------------------------------------------------------
# Vocabularies. APPEND-ONLY: never insert/reorder existing entries, or earlier
# page slugs will shift. Add new coverage at the end of each list.
# ---------------------------------------------------------------------------

PROXY_TYPES = [
    "residential",
    "ISP",
    "IPv4",
    "mobile",
    "datacenter",
    "rotating residential",
    "static residential",
    "4G mobile",
    "dedicated",
    "shared",
]

# Per-type SPEED facts used to vary copy so pages never read identically.
TYPE_FACTS: dict[str, dict[str, str]] = {
    "residential": {"what": "IP addresses assigned by ISPs to real homes", "speed": "moderate and variable", "latency": "higher, tied to the underlying home connection", "best": "sensitive targets where trust matters more than raw speed"},
    "ISP": {"what": "datacenter-hosted IPs registered under real internet providers", "speed": "fast and stable", "latency": "low", "best": "speed with residential-grade trust"},
    "IPv4": {"what": "classic dedicated or shared IPv4 addresses", "speed": "reliable and consistent", "latency": "low to moderate", "best": "tools that need fixed, broadly compatible addresses"},
    "mobile": {"what": "IPs from 3G/4G/5G mobile carriers shared by real devices", "speed": "variable", "latency": "higher and less predictable", "best": "high-trust tasks where speed is secondary"},
    "datacenter": {"what": "high-bandwidth IPs hosted in data centers", "speed": "the fastest", "latency": "the lowest", "best": "high-volume work on less protected targets"},
    "rotating residential": {"what": "residential IPs that change automatically per request or timer", "speed": "moderate with rotation overhead", "latency": "varies per IP", "best": "large-scale data collection that spreads load"},
    "static residential": {"what": "residential IPs that stay fixed for long sessions", "speed": "moderate but consistent", "latency": "steady", "best": "account work that needs a stable, trusted identity"},
    "4G mobile": {"what": "IPs from 4G cellular networks shared by many real users", "speed": "variable", "latency": "higher", "best": "social workflows that reward mobile-grade trust"},
    "dedicated": {"what": "private proxies reserved for a single user", "speed": "fast and predictable", "latency": "low", "best": "consistent, exclusive performance"},
    "shared": {"what": "proxies used by more than one customer at a time", "speed": "variable under load", "latency": "depends on how busy the pool is", "best": "lighter tasks where speed needs are modest"},
}

USE_CASES = [
    "web scraping",
    "SEO rank tracking",
    "social media management",
    "ad verification",
    "price monitoring",
    "market research",
    "brand protection",
    "e-commerce research",
    "business automation",
    "account management",
    "sneaker copping",
    "data collection",
    "affiliate marketing",
    "lead generation",
    "travel fare aggregation",
    "ticket availability monitoring",
    "review monitoring",
    "SERP data collection",
    "competitor analysis",
    "stock and inventory monitoring",
    "app store research",
    "social listening",
    "coupon and deal validation",
    "localized QA testing",
    "survey panel diversification",
    "streaming catalog research",
    "real estate listing research",
    "job board aggregation",
    "crypto exchange monitoring",
    "news aggregation",
    "marketplace seller research",
    "web automation testing",
    "content localization checks",
    "email verification workflows",
    "digital marketing research",
]

PLATFORMS = [
    "Instagram", "TikTok", "Facebook", "Twitter", "YouTube", "Amazon", "eBay",
    "Walmart", "Shopify", "Google", "Bing", "LinkedIn", "Pinterest", "Reddit",
    "Craigslist", "Etsy", "AliExpress", "Best Buy", "Target", "Scrapy",
    "Selenium", "Puppeteer", "Playwright", "Octoparse", "Multilogin", "GoLogin",
    "Dolphin Anty", "AdsPower", "Nike SNKRS", "Ticketmaster", "Booking.com",
    "Expedia", "Zillow", "Indeed", "Google Maps",
]

GEOS = [
    "United States", "United Kingdom", "Canada", "Australia", "Germany", "France",
    "Spain", "Italy", "Netherlands", "Brazil", "Mexico", "India", "Japan",
    "Singapore", "United Arab Emirates", "South Africa", "Poland", "Sweden",
    "Turkey", "Indonesia", "Ireland", "Belgium", "Switzerland", "Austria",
    "Portugal", "Denmark", "Norway", "Finland", "Czechia", "Romania", "Greece",
    "Hungary", "New Zealand", "South Korea", "Thailand", "Vietnam", "Philippines",
    "Malaysia", "Saudi Arabia", "Israel", "Argentina", "Colombia", "Chile",
    "Peru", "Ukraine", "Bulgaria", "Croatia", "Slovakia", "Lithuania", "Latvia",
    "Estonia", "Egypt", "Nigeria", "Kenya", "Morocco", "Hong Kong", "Taiwan",
    "Pakistan", "Bangladesh",
]

CITIES = [
    "New York", "Los Angeles", "Chicago", "Houston", "London", "Manchester",
    "Toronto", "Vancouver", "Sydney", "Melbourne", "Berlin", "Munich", "Paris",
    "Madrid", "Barcelona", "Rome", "Milan", "Amsterdam", "Sao Paulo",
    "Mexico City", "Mumbai", "Delhi", "Tokyo", "Osaka", "Singapore", "Dubai",
    "Johannesburg", "Warsaw", "Stockholm", "Istanbul", "Jakarta", "Dublin",
    "Brussels", "Zurich", "Vienna", "Lisbon", "Copenhagen", "Oslo", "Helsinki",
    "Prague", "Bucharest", "Athens", "Budapest", "Auckland", "Seoul", "Bangkok",
]

PROVIDERS = [
    DEAL_NAME, "Bright Data", "Oxylabs", "Smartproxy", "SOAX", "IPRoyal",
    "NetNut", "Rayobyte", "Webshare", "Proxy-Seller", "Storm Proxies",
]

PROVIDER_PAIRS = [f"{DEAL_NAME} vs {p}" for p in PROVIDERS[1:]] + [
    "Bright Data vs Oxylabs", "Smartproxy vs IPRoyal", "SOAX vs NetNut",
    "Webshare vs Rayobyte", "IPRoyal vs Webshare", "Oxylabs vs Smartproxy",
    "Bright Data vs Smartproxy", "Proxy-Seller vs IPRoyal", "Storm Proxies vs Webshare",
    "NetNut vs Bright Data",
]
TYPE_PAIRS = [
    "residential vs datacenter proxies", "ISP vs residential proxies",
    "mobile vs residential proxies", "datacenter vs ISP proxies",
    "rotating vs static proxies", "shared vs dedicated proxies",
    "IPv4 vs residential proxies", "4G mobile vs residential proxies",
]
COMPARE_DIMENSIONS = PROVIDER_PAIRS + TYPE_PAIRS

SPEED_TOPICS = [
    "speed explained", "latency benchmarks", "throughput and concurrency",
    "how to speed test", "residential vs datacenter speed", "reducing latency",
    "success rate vs speed", "peak-hour performance", "rotation and speed",
    "uptime and reliability", "server location and latency", "fast setup checklist",
]

SPEED_MODS = ["Fastest", "Fast", "Low-Latency", "High-Speed", "Quick", "Rapid"]

AUDIENCES = [
    "solo founders", "growth marketers", "data teams", "SEO agencies",
    "e-commerce sellers", "affiliate marketers", "developers", "social media managers",
    "market researchers", "startups on a budget", "freelancers", "automation engineers",
]
MODES = ["rotating", "sticky-session", "pay-as-you-go", "subscription", "prepaid", "on-demand"]
ANGLES = ["the lowest latency", "the highest throughput", "consistent speed under load",
          "fast, stable connections", "strong success rates at speed", "value-focused speed"]
INTENTS = ["find the fastest option", "compare speed and value", "cut latency",
           "match a fast proxy to the task", "benchmark before buying", "start small and scale"]

# Emoji per cluster for the blog-card thumbnails (matches the site's card style).
CATEGORY_ICON = {
    "Speed Reviews": "\U0001F3C1",        # chequered flag
    "Speed Comparisons": "⚖️",   # balance scale
    "Platform Speed": "\U0001F4F1",        # mobile phone
    "Latency Guides": "\U0001F4CA",        # bar chart
    "Country Speed": "\U0001F30D",         # globe
    "City Speed": "\U0001F4CD",            # round pin
}


# ---------------------------------------------------------------------------
# Spec builder
# ---------------------------------------------------------------------------

def build_specs() -> list[PageSpec]:
    specs: list[PageSpec] = []
    used: set[str] = set()
    used_titles: set[str] = set()
    done: set[tuple] = set()

    def add(title: str, category: str, ptype: str, use_case: str, geo: str,
            platform: str, focus: str, keywords: tuple[str, ...]) -> None:
        if len(specs) >= TARGET:
            return
        base_title = title
        suffix = 2
        while title in used_titles:
            title = f"{base_title} for {pick(AUDIENCES, suffix, len(base_title))}"
            suffix += 1
        used_titles.add(title)
        idx = len(specs) + 1
        base_slug = slugify(title)
        slug = base_slug
        s2 = 2
        while slug in used:
            slug = f"{base_slug}-{s2}"
            s2 += 1
        used.add(slug)
        speed = pick(SPEED_MODS, idx, 0)
        audience = pick(AUDIENCES, idx, len(use_case))
        mode = pick(MODES, idx, len(geo))
        angle = pick(ANGLES, idx, len(platform))
        intent = pick(INTENTS, idx, len(category))
        modified = (TODAY - timedelta(days=idx % 24)).isoformat()
        desc = meta_description(
            f"{title}. Benchmark-style reviews of proxy speed, latency, throughput and value "
            f"for {use_case} in 2026 - compare the fastest proxy providers, with {DEAL_NAME} as our featured value pick."
        )
        specs.append(PageSpec(
            idx=idx, title=title, slug=slug, category=category, focus=focus,
            ptype=ptype, use_case=use_case, geo=geo, platform=platform, speed=speed,
            audience=audience, mode=mode, angle=angle, intent=intent,
            modified=modified, description=desc, keywords=keywords,
        ))

    def kw(*parts: str) -> tuple[str, ...]:
        base = ["fast proxy reviews", "fastest proxies", "proxy speed comparison", "fast proxies"]
        return tuple(list(dict.fromkeys([p.lower() for p in parts if p] + base)))[:9]

    # ---- Phase 1: Speed Reviews - Fastest {type} proxies for {use-case} in {geo} (cap 7000)
    cap = min(TARGET, 7000)
    for ptype in PROXY_TYPES:
        for use_case in USE_CASES:
            for geo in GEOS:
                if len(specs) >= cap:
                    break
                key = ("rev", ptype, use_case, geo)
                if key in done:
                    continue
                done.add(key)
                focus = f"fastest {ptype} proxies for {use_case} in {geo}"
                title = f"Fastest {ptype.title()} Proxies for {use_case.title()} in {geo} (2026 Speed Review)"
                add(title, "Speed Reviews", ptype, use_case, geo, ptype, focus,
                    kw(f"fastest {ptype} proxies", f"fast {ptype} proxies for {use_case}",
                       f"{ptype} proxies {geo}", f"low latency proxies for {use_case}"))
            if len(specs) >= cap:
                break
        if len(specs) >= cap:
            break

    # ---- Phase 2: Speed Comparisons - {A} vs {B} speed for {use-case} (cap +5500)
    cap = min(TARGET, len(specs) + 5500)
    for dim in COMPARE_DIMENSIONS:
        for use_case in USE_CASES:
            for geo in GEOS:
                if len(specs) >= cap:
                    break
                key = ("cmp", dim, use_case, geo)
                if key in done:
                    continue
                done.add(key)
                ptype = pick(PROXY_TYPES, len(specs), len(use_case))
                focus = f"{dim} speed for {use_case} in {geo}"
                title = f"{dim.title()} for {use_case.title()} in {geo}: Speed & Value Comparison (2026)"
                add(title, "Speed Comparisons", ptype, use_case, geo, dim, focus,
                    kw(f"{dim} speed", f"{dim} comparison", f"fastest proxies for {use_case}",
                       f"proxy speed comparison {geo}"))
            if len(specs) >= cap:
                break
        if len(specs) >= cap:
            break

    # ---- Phase 3: Platform Speed - Fastest {type} proxies for {platform} in {geo} (cap +3000)
    cap = min(TARGET, len(specs) + 3000)
    for platform in PLATFORMS:
        for ptype in PROXY_TYPES:
            for geo in GEOS:
                if len(specs) >= cap:
                    break
                key = ("plat", platform, ptype, geo)
                if key in done:
                    continue
                done.add(key)
                use_case = f"{platform} operations"
                focus = f"fastest {ptype} proxies for {platform} in {geo}"
                title = f"Fastest {ptype.title()} Proxies for {platform} in {geo} (2026 Speed Guide)"
                add(title, "Platform Speed", ptype, use_case, geo, platform, focus,
                    kw(f"fastest proxies for {platform}", f"fast {platform} proxies",
                       f"{ptype} proxies for {platform}", f"low latency proxies {geo}"))
            if len(specs) >= cap:
                break
        if len(specs) >= cap:
            break

    # ---- Phase 4: Latency Guides - {type} proxy {topic} (cap +2000)
    cap = min(TARGET, len(specs) + 2000)
    for ptype in PROXY_TYPES:
        for topic in SPEED_TOPICS:
            for geo in GEOS:
                if len(specs) >= cap:
                    break
                key = ("lat", ptype, topic, geo)
                if key in done:
                    continue
                done.add(key)
                use_case = "proxy speed research"
                focus = f"{ptype} proxy {topic} in {geo}"
                title = f"{ptype.title()} Proxy {topic.title()} in {geo} (2026 Speed Guide)"
                add(title, "Latency Guides", ptype, use_case, geo, ptype, focus,
                    kw(f"{ptype} proxy speed", f"{ptype} proxy latency", f"proxy speed {geo}",
                       "how fast are proxies"))
            if len(specs) >= cap:
                break
        if len(specs) >= cap:
            break

    # ---- Phase 5: Country Speed - Fastest {type} proxies in {geo} (cap +1500)
    cap = min(TARGET, len(specs) + 1500)
    for geo in GEOS:
        for ptype in PROXY_TYPES:
            if len(specs) >= cap:
                break
            key = ("country", geo, ptype)
            if key in done:
                continue
            done.add(key)
            use_case = "country-targeted proxy speed"
            focus = f"fastest {ptype} proxies in {geo}"
            title = f"Fastest {ptype.title()} Proxies in {geo}: Speed-Ranked Picks (2026)"
            add(title, "Country Speed", ptype, use_case, geo, geo, focus,
                kw(f"fastest proxies in {geo}", f"fast {ptype} proxies {geo}",
                   f"low latency proxies {geo}", f"best proxies {geo}"))
        if len(specs) >= cap:
            break
    if len(specs) < cap:
        for geo in GEOS:
            for use_case in USE_CASES:
                if len(specs) >= cap:
                    break
                key = ("countryuc", geo, use_case)
                if key in done:
                    continue
                done.add(key)
                ptype = pick(PROXY_TYPES, len(specs), len(geo))
                focus = f"fastest proxies in {geo} for {use_case}"
                title = f"Fastest Proxies in {geo} for {use_case.title()} (2026 Speed Guide)"
                add(title, "Country Speed", ptype, use_case, geo, geo, focus,
                    kw(f"fast proxies {geo}", f"fastest proxies {geo}", f"{use_case} proxies {geo}"))
            if len(specs) >= cap:
                break

    # ---- Phase 6: City Speed - Fastest {type} proxies in {city} (cap +1000)
    cap = min(TARGET, len(specs) + 1000)
    for city in CITIES:
        for ptype in PROXY_TYPES:
            if len(specs) >= cap:
                break
            key = ("city", city, ptype)
            if key in done:
                continue
            done.add(key)
            use_case = "city-targeted proxy speed"
            focus = f"fastest {ptype} proxies in {city}"
            title = f"Fastest {ptype.title()} Proxies in {city} (2026 Local Speed Guide)"
            add(title, "City Speed", ptype, use_case, city, city, focus,
                kw(f"fastest proxies in {city}", f"fast {ptype} proxies {city}", f"proxies {city}"))
        if len(specs) >= cap:
            break
    if len(specs) < cap:
        for city in CITIES:
            for use_case in USE_CASES:
                if len(specs) >= cap:
                    break
                key = ("cityuc", city, use_case)
                if key in done:
                    continue
                done.add(key)
                ptype = pick(PROXY_TYPES, len(specs), len(city))
                focus = f"fastest proxies in {city} for {use_case}"
                title = f"Fast Proxies in {city} for {use_case.title()} (2026)"
                add(title, "City Speed", ptype, use_case, city, city, focus,
                    kw(f"fast proxies {city}", f"proxies {city}", f"{use_case} proxies"))
            if len(specs) >= cap:
                break

    # ---- Final top-up: keep filling Speed Reviews across the full grid until TARGET.
    if len(specs) < TARGET:
        for ptype in PROXY_TYPES:
            for use_case in USE_CASES:
                for geo in GEOS:
                    if len(specs) >= TARGET:
                        break
                    key = ("rev", ptype, use_case, geo)
                    if key in done:
                        continue
                    done.add(key)
                    focus = f"fastest {ptype} proxies for {use_case} in {geo}"
                    title = f"Fastest {ptype.title()} Proxies for {use_case.title()} in {geo} (2026 Speed Review)"
                    add(title, "Speed Reviews", ptype, use_case, geo, ptype, focus,
                        kw(f"fastest {ptype} proxies", f"fast {ptype} proxies for {use_case}",
                           f"{ptype} proxies {geo}"))
                if len(specs) >= TARGET:
                    break
            if len(specs) >= TARGET:
                break

    return specs


# ---------------------------------------------------------------------------
# Chrome - reproduces the Fast Proxy Reviews (Medic Care) sub-page markup, with
# a relative prefix so /seo/ pages resolve ../ correctly.
# ---------------------------------------------------------------------------

BRAND_MARK = (
    '<span class="brand__mark" aria-hidden="true"><span class="brand__pulse"></span>'
    '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" '
    'stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2 4 14h6l-1 8 9-12h-6z"/></svg></span>'
)
BRAND_MARK_FOOT = (
    '<span class="brand__mark" aria-hidden="true">'
    '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" '
    'stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2 4 14h6l-1 8 9-12h-6z"/></svg></span>'
)


def header(prefix: str, active: str = "library") -> str:
    def nav(name: str, href: str, key: str) -> str:
        cur = ' aria-current="true"' if active == key else ""
        return f'<a href="{href}"{cur}>{name}</a>'

    return f"""<div class="scroll-track" aria-hidden="true"><span id="scrollBar" class="scroll-bar"></span></div>

<header class="site-head">
  <div class="wrap site-head__inner">
    <a href="{prefix}index.html" class="brand" aria-label="Fast Proxy Reviews home">
      {BRAND_MARK}
      <span class="brand__txt">Fast<span class="brand__accent">Proxy</span>Reviews</span>
    </a>
    <button class="nav-toggle" id="navToggle" aria-label="Toggle navigation menu" aria-expanded="false" aria-controls="primaryNav"><span></span><span></span><span></span></button>
    <nav class="nav" id="primaryNav" aria-label="Primary">
      {nav("Home", f"{prefix}index.html", "home")}
      {nav("Speed Reviews", f"{prefix}index.html#providers", "providers")}
      {nav("Compare", f"{prefix}index.html#compare", "compare")}
      {nav("Proxy Types", f"{prefix}index.html#types", "types")}
      {nav("Library", f"{prefix}content-library.html", "library")}
      {nav("Blog", "/blog/", "blog")}
      {nav("Tips", f"{prefix}tips.html", "tips")}
      {nav("FAQ", f"{prefix}index.html#faq", "faq")}
      {nav("Privacy", f"{prefix}privacy-policy.html", "privacy")}
      <a class="nav__cta" href="{DEAL_URL}" target="_blank" rel="{DEAL_REL}">Fast Pick</a>
    </nav>
  </div>
</header>
"""


def footer(prefix: str) -> str:
    return f"""<footer class="site-foot">
  <div class="wrap site-foot__grid">
    <div class="site-foot__brand">
      <span class="brand brand--foot">{BRAND_MARK_FOOT}<span class="brand__txt">Fast<span class="brand__accent">Proxy</span>Reviews</span></span>
      <p>Independent proxy speed reviews, performance benchmarks and provider comparisons for fast, reliable and affordable proxies in 2026.</p>
      <a class="btn btn--primary btn--sm" href="{DEAL_URL}" target="_blank" rel="{DEAL_REL}">View Fast Proxy Pick</a>
    </div>
    <nav class="site-foot__col" aria-label="Explore"><h3>Explore</h3>
      <a href="{prefix}index.html#providers">Speed Reviews</a><a href="{prefix}index.html#compare">Compare Providers</a><a href="{prefix}index.html#types">Proxy Types</a><a href="{prefix}index.html#usecases">Use Cases</a><a href="{prefix}index.html#guide">Buying Guide</a></nav>
    <nav class="site-foot__col" aria-label="Pages"><h3>Pages</h3>
      <a href="{prefix}content-library.html">Speed Library</a><a href="/blog/">Blog</a><a href="{prefix}tips.html">Proxy Speed Tips</a><a href="{prefix}about.html">About &amp; Methodology</a><a href="{prefix}privacy-policy.html">Privacy Policy</a></nav>
    <div class="site-foot__col"><h3>Contact</h3>
      <a href="mailto:info@fastproxyreviews.com">info@fastproxyreviews.com</a>
      <p class="site-foot__small">Email only &mdash; no phone, no chat.</p></div>
  </div>
  <div class="site-foot__bar"><div class="wrap site-foot__bar-inner">
    <p>&copy; 2026 Fast Proxy Reviews. Independent reviews &amp; comparisons.</p>
    <p class="site-foot__disc">Qualitative, editorial ratings only. We don't claim exact speed, uptime, latency, bandwidth or locations. Some links may be affiliate links. Always test the exact plan before relying on it for critical workloads.</p>
  </div></div>
</footer>

<button id="toTop" class="to-top" aria-label="Back to top">&uarr;</button>
<script src="{prefix}script.js" defer></script>
<script src="/blog-nav.js" defer></script>
"""


# ---------------------------------------------------------------------------
# Content builders (speed voice)
# ---------------------------------------------------------------------------

def _vars(spec: PageSpec) -> dict:
    metric = pick(["latency", "throughput", "success rate", "p90 response time",
                   "requests completed per minute", "time to first byte", "connection stability",
                   "block ratio", "consistency across runs"], spec.idx)
    tuner = pick(["tuning concurrency to the pool", "reusing keep-alive connections",
                  "choosing exit locations close to the target", "capping retries so slow requests don't snowball",
                  "caching DNS for your targets", "rotating only on failure instead of every request",
                  "trimming request payloads and accepting compression", "respecting rate limits to avoid blocks"],
                 spec.idx, 2)
    trap = pick(["oversubscribed shared pools that crawl under load", "far-away exit nodes that add latency to every request",
                 "aggressive rotation that adds handshake overhead", "cheap pools that get blocked and force slow retries",
                 "throttled 'unlimited' plans", "peak-hour congestion on busy networks",
                 "thin regional coverage that routes you the long way round", "marketing speeds measured on an empty network"],
                spec.idx, 3)
    opener = pick(["In practice", "On real workloads", "Across repeated runs", "When speed matters most",
                   "Under real concurrency", "From a performance standpoint", "In day-to-day use", "At scale"],
                  spec.idx, 5)
    return {"metric": metric, "tuner": tuner, "trap": trap, "opener": opener}


def _tf(ptype: str, key: str) -> str:
    return TYPE_FACTS.get(ptype, TYPE_FACTS["residential"]).get(key, "")


def guide_sections(spec: PageSpec) -> list[tuple[str, str, str]]:
    title = e(spec.title)
    ptype = e(spec.ptype)
    use_case = e(spec.use_case)
    geo = e(spec.geo)
    audience = e(spec.audience)
    speed = e(spec.speed.lower())
    v = _vars(spec)
    metric, tuner, trap, opener = v["metric"], v["tuner"], v["trap"], v["opener"]
    what, spd, lat, best = _tf(spec.ptype, "what"), _tf(spec.ptype, "speed"), _tf(spec.ptype, "latency"), _tf(spec.ptype, "best")
    rows = lambda pairs: "<ul>" + "".join(f"<li><strong>{e(a)}:</strong> {e(b)}</li>" for a, b in pairs) + "</ul>"

    return [
        ("intent", f"What buyers want from {e(spec.focus)}",
         f"""
        <p>{title} is written for one very specific searcher: someone who wants the {speed} way to run {ptype} proxies for {use_case} without guessing. The intent is practical and performance-driven &mdash; people here want to compare real proxy speed, understand what causes latency, and pick an option they can defend with their own numbers.</p>
        <p>For {audience}, the honest goal is <strong>effective speed, not a marketing headline</strong>. A network that looks fast on an empty demo can crawl under your real concurrency, so this benchmark-style review keeps the focus on latency, throughput and success rate &mdash; and points back to our featured value pick, <a href="{DEAL_URL}" target="_blank" rel="{DEAL_REL}">{DEAL_NAME}</a>, for buyers who want fast, affordable access.</p>
        {rows([("Primary keyword", spec.focus), ("Buyer goal", spec.intent), ("Best metric to judge", metric)])}
        """),
        ("what-it-is", f"What {ptype} proxies are and how fast they feel for {use_case}",
         f"""
        <p>{ptype.title()} proxies are {what}. For {use_case}, the proxy type is the single biggest lever on speed: it decides how much latency each request carries and how consistently your traffic gets through. {ptype.title()} proxies are typically <strong>{spd}</strong>, with latency that is {lat}, and they are usually {best}.</p>
        <p>Choosing the right type first is how you avoid paying for capability you will not use &mdash; or picking a bargain type that keeps getting blocked and turns &quot;fast&quot; into a stream of slow retries.</p>
        {rows([("What it is", what), ("Typical speed", spd), ("Latency profile", lat), ("Best for", best)])}
        """),
        ("speed-factors", f"What actually makes {ptype} proxies fast (or slow)",
         f"""
        <p>Raw provider marketing rarely explains real-world speed. For {use_case} in {geo}, {ptype} proxy performance comes down to a handful of factors you can actually measure and control.</p>
        {rows([("Network capacity", "well-provisioned pools resist slow-downs under load"),
               ("Routing distance", "the closer the exit node to the target, the lower the latency"),
               ("Pool sharing", "lightly-shared or dedicated IPs are more predictable than busy shared pools"),
               ("Success rate", "blocks force retries, and retries are the hidden tax on speed"),
               ("Concurrency", "the right number of parallel connections keeps throughput high without contention")])}
        <p>{opener}, the fastest setup for {use_case} is the one that scores best on {metric} across many requests &mdash; not the one with the flashiest advertised number.</p>
        """),
        ("latency", "Latency, throughput and success rate explained",
         f"""
        <p>&quot;Fast&quot; means three different things, and a good {ptype} proxy delivers all three. Judge any plan for {use_case} on this trio rather than a single figure.</p>
        <table><thead><tr><th>Metric</th><th>What it measures</th><th>Why it matters for {use_case}</th></tr></thead><tbody>
        <tr><td>Latency</td><td>response time per request</td><td>decides how snappy each call feels</td></tr>
        <tr><td>Throughput</td><td>data moved per second under load</td><td>drives how fast large jobs finish</td></tr>
        <tr><td>Success rate</td><td>share of requests that complete cleanly</td><td>low success quietly destroys effective speed</td></tr></tbody></table>
        <p>Measure all three across many requests, not a single best-case ping. Consistency matters as much as the peak.</p>
        """),
        ("by-type", f"Speed by proxy type: where {ptype} fits",
         f"""
        <p>Each proxy type has a characteristic speed profile. Understanding it helps you shortlist fast options for {use_case} quickly, and shows where {ptype} proxies sit against the alternatives.</p>
        {rows([("Datacenter", "usually the lowest latency and highest raw throughput on tolerant targets"),
               ("ISP", "fast and stable, with residential-grade trust &mdash; a favourite for speed"),
               ("Residential", "more variable latency, chosen when trust beats raw speed"),
               ("Mobile", "higher, less predictable latency, valued for trust and rotation"),
               (f"{spec.ptype.title()}", f"{spd}, best for {best}")])}
        <p>For {geo}, also weigh coverage: a fast type with thin coverage in the region can still route you the long way round.</p>
        """),
        ("how-to-test", f"How to speed-test {ptype} proxies for {use_case}",
         f"""
        <p>The only reliable way to know a proxy is fast for {use_case} is to benchmark it on your real targets. Generic speed pages mislead; your sites and your concurrency are what count.</p>
        {rows([("Measure latency", "response time across many requests, not one ping"),
               ("Measure throughput", f"data per second at the concurrency {use_case} really uses"),
               ("Measure success rate", "clean completions vs blocks, timeouts and CAPTCHAs"),
               ("Watch the slow tail", "p90 latency often matters more than the average"),
               ("Test at peak", "performance shifts by time of day, so test your busy window")])}
        <p>{opener}, run the test from a small paid trial before you scale, and only commit once {metric} stays steady across several runs.</p>
        """),
        ("providers", f"Fast, value-focused providers to compare for {use_case}",
         f"""
        <p>For {audience} chasing {speed} {ptype} proxies, a short shortlist beats endless tabs. We feature <a href="{DEAL_URL}" target="_blank" rel="{DEAL_REL}">{DEAL_NAME}</a> as the value pick because it covers residential, ISP, IPv4, mobile and datacenter categories in one place at budget-friendly pricing. Larger teams often also weigh Bright Data, Oxylabs and NetNut for scale, while Smartproxy, SOAX, IPRoyal, Webshare and Rayobyte are common picks for a balance of speed and value.</p>
        <p>Whatever the shortlist, confirm the exact package, {ptype} proxy availability and coverage for {geo} before you commit &mdash; and benchmark each on the same targets.</p>
        {rows([("Featured value pick", f"{DEAL_NAME} - fast, budget-friendly, multi-category"),
               ("Enterprise scale", "Bright Data, Oxylabs, NetNut"),
               ("Balanced options", "Smartproxy, SOAX, IPRoyal, Webshare, Rayobyte")])}
        """),
        ("use-case-fit", f"Matching proxy speed to {use_case}",
         f"""
        <p>The fastest plan only counts if it fits {use_case}. Break the job into steps and match each to the right setting so speed is not wasted on the wrong part of the workflow.</p>
        {rows([("Discovery work", "favour volume, rotation and throughput to finish large jobs fast"),
               ("Account or session work", f"favour {spec.mode} sessions and stable, low-latency IPs"),
               ("Retries", "cap depth so failed requests do not quietly drag the whole run down")])}
        <p>{opener}, a {ptype} plan sized to real usage in {geo} outperforms a bigger plan bought &quot;just in case.&quot;</p>
        """),
        ("geo", f"{geo}: latency and coverage notes",
         f"""
        <p>Speed and availability for {ptype} proxies vary by location, so a plan that is fast in one market can lag in {geo}. Distance to the exit node is one of the biggest latency factors, so verified in-region coverage is a speed feature, not just a targeting one.</p>
        {rows([("Verify", "the country, city and network of the IPs you actually receive"),
               ("Test", f"a small sample targeted to {geo} at peak and off-peak"),
               ("Compare", "reproducible latency in-region, not just a headline number")])}
        <p>Thin regional coverage is the most common reason a &quot;fast&quot; plan feels slow for {geo}.</p>
        """),
        ("reliability", "Why reliability is part of speed",
         f"""
        <p>A fast proxy that drops connections is slow once you count the retries. For {use_case}, uptime and stability belong in the same conversation as latency &mdash; a slightly slower network that stays up often beats a faster one that stalls under load.</p>
        <p>{opener}, treat {metric} and success rate together: the effective speed of a run is throughput multiplied by how often requests actually succeed.</p>
        <div class="callout"><span class="callout__title">&#9889; Key point</span><p>The fastest proxy for {use_case} is the one that completes your workload with the highest success rate &mdash; not the one with the best-case ping on a landing page.</p></div>
        """),
        ("value", "Fast vs cheap: getting speed at the right price",
         f"""
        <p>Raw speed is easy to advertise and expensive to sustain. Value &mdash; the blend of speed, reliability, proxy-type coverage and price &mdash; is what decides whether a provider works for {use_case} month after month.</p>
        <p>{opener}, weigh {metric} against cost per successful result. That is exactly how we rank providers, and why an affordable, flexible option such as <a href="{DEAL_URL}" target="_blank" rel="{DEAL_REL}">{DEAL_NAME}</a> can be the smart buy for {audience} who want fast proxies without enterprise pricing.</p>
        {rows([("Judge on", "effective speed at a price you can live with"),
               ("Watch", "premium plans you pay for but never fully use"),
               ("Featured pick", f"{DEAL_NAME} - value-focused speed across proxy types")])}
        """),
        ("traps", f"Speed traps to avoid with {ptype} proxies",
         f"""
        <p>A big advertised number hides problems as often as it signals real speed. For {use_case} in {geo}, watch for {trap}, which quietly turn a &quot;fast&quot; plan into a slow one once you count failed requests.</p>
        <p>The safeguard is simple: benchmark on your real targets, read the fine print on rate limits and coverage, and run a short pilot before committing.</p>
        {rows([("Biggest trap here", trap), ("Check", "peak-hour behaviour, success rate and in-region routing"),
               ("Protect yourself", "pilot first, measure, then scale")])}
        """),
        ("setup", f"Quick setup for fast {ptype} proxies",
         f"""
        <p>Start small. Configure one endpoint, target {geo}, authenticate, and run an IP lookup and a latency check to confirm you are getting what you paid for. Only after a clean manual test should you connect automation for {use_case}.</p>
        {rows([("Step 1", "verify the endpoint, IP location and first-request latency"),
               ("Step 2", "run one manual test against your real target"),
               ("Step 3", f"connect a small automated batch and watch {metric}")])}
        <p>Speed up further by {tuner}. Our <a href="{DEAL_URL}" target="_blank" rel="{DEAL_REL}">featured value pick</a> and <a href="../tips.html">proxy speed tips</a> cover this in more depth.</p>
        """),
        ("featured", f"Why {DEAL_NAME} is our featured value pick",
         f"""
        <p>Across our comparisons, <a href="{DEAL_URL}" target="_blank" rel="{DEAL_REL}">{DEAL_NAME}</a> stands out as a strong value-focused option for {use_case}. It bundles residential, ISP, IPv4, mobile and datacenter categories in one place at budget-friendly pricing, which suits {audience} who want fast, affordable proxy access without committing to enterprise plans first.</p>
        <p>As with any provider, we present it as a value option rather than a guarantee of specific speed &mdash; confirm the exact package and coverage for {geo}, and benchmark it on your own targets.</p>
        {rows([("Why featured", "value-focused speed across multiple proxy types"),
               ("Good fit for", f"{audience} comparing fast {ptype} proxies"),
               ("Before ordering", "check the package, proxy type and usage rules")])}
        """),
        ("recommendation", f"Final take on {e(spec.focus)}",
         f"""
        <p>The strongest plan for {use_case} is a measured one: pick the right proxy type, benchmark latency, throughput and success rate on your real targets in {geo}, and run a small pilot before scaling. That path gives {audience} the {speed} option that actually performs.</p>
        <p>If you are still choosing, start with our <a href="../index.html#providers">speed reviews</a> and <a href="../index.html#compare">comparison table</a>, then test the top candidates &mdash; including <a href="{DEAL_URL}" target="_blank" rel="{DEAL_REL}">{DEAL_NAME}</a> &mdash; on your own workload.</p>
        """),
    ]


def comparison_sections(spec: PageSpec) -> list[tuple[str, str, str]]:
    dim = e(spec.platform)
    use_case = e(spec.use_case)
    geo = e(spec.geo)
    audience = e(spec.audience)
    speed = e(spec.speed.lower())
    v = _vars(spec)
    metric, tuner, trap, opener = v["metric"], v["tuner"], v["trap"], v["opener"]
    parts = [p.strip() for p in spec.platform.replace(" vs ", "|").split("|")]
    a = e(parts[0]) if parts else dim
    b = e(parts[1]) if len(parts) > 1 else dim
    rows = lambda pairs: "<ul>" + "".join(f"<li><strong>{e(x)}:</strong> {e(y)}</li>" for x, y in pairs) + "</ul>"

    return [
        ("short-answer", f"{dim} for {use_case}: the short answer",
         f"""
        <p>This page compares <strong>{dim}</strong> specifically for {use_case} in {geo}, with speed and value front and centre. Both options can do the job, but the wrong pick quietly raises your latency and your cost per successful result. The aim is a decision you can defend with your own benchmark numbers.</p>
        <p>For {audience}, the practical question is which option delivers {spec.angle} for {use_case}. {opener}, the answer turns on latency, throughput, success rate and coverage in {geo}.</p>
        {rows([("Comparison", spec.platform), ("Applied to", f"{spec.use_case} in {spec.geo}"), ("Decide on", metric)])}
        """),
        ("what-differs", f"What actually differs between {a} and {b} on speed",
         f"""
        <p>Marketing blurs the line between {a} and {b}. For {use_case}, the real differences show up in latency, network capacity, coverage and how each holds up under load in {geo}. Name the one variable that matters most to your workflow and the rest gets easier.</p>
        <table><thead><tr><th>Factor</th><th>{a}</th><th>{b}</th></tr></thead><tbody>
        <tr><td>Best fit</td><td>value and steady speed</td><td>scale or precision at speed</td></tr>
        <tr><td>Latency feel</td><td>depends on plan and routing</td><td>depends on plan and routing</td></tr>
        <tr><td>Main risk</td><td>{trap}</td><td>{trap}</td></tr></tbody></table>
        """),
        ("speed", f"Speed comparison for {use_case}",
         f"""
        <p>Compare {a} and {b} on <strong>effective speed</strong> &mdash; latency, throughput and success rate together &mdash; not a single advertised figure. An option that looks faster per request can finish slower once retries and blocks are counted. Model the full path from request to completed task in {geo}.</p>
        <p>Run a small paid test on each, record latency and completions per minute under your real concurrency, and project to full volume with a retry buffer. The true winner usually only becomes clear after this step.</p>
        {rows([("Compare on", "latency, throughput and success rate"), ("Hidden cost", "retries and wasted bandwidth"), ("Guardrail", "test at peak and off-peak in-region")])}
        """),
        ("latency-throughput", "Latency and throughput: which wins under load",
         f"""
        <p>The lower-latency option is not automatically the better pick. For {use_case}, weigh single-request latency against sustained throughput under concurrency. A choice that is a touch slower per request but far steadier under load can finish the job first.</p>
        <p>{opener}, judge the pair by {metric} on your own targets. That is the number that decides which of {a} or {b} keeps your run fast across a full session.</p>
        """),
        ("when-a", f"When {a} is the faster choice",
         f"""
        <p>{a} tends to win for {use_case} when the workflow values stability, predictable routing and simpler operations in {geo}. Choose it when your logs show that dropped connections hurt more than peak throughput, and keep {tuner} so the advantage is not wasted.</p>
        {rows([("Strong for", f"{spec.use_case} that needs consistency"), ("Watch", trap), ("Speed up by", tuner)])}
        """),
        ("when-b", f"When {b} is the faster choice",
         f"""
        <p>{b} tends to win for {use_case} when scale, coverage or precision is the bottleneck. Prove the gain with a small test before committing, because a premium only pays off if {metric} actually improves on your targets.</p>
        {rows([("Strong for", f"{spec.use_case} that needs scale or precision"), ("Prove it with", "a small paid pilot"), ("Confirm on", metric)])}
        """),
        ("by-use-case", f"Matching the pick to {use_case}",
         f"""
        <p>The comparison only means something once tied to {use_case}. Split the job into steps &mdash; discovery, authenticated actions, retries &mdash; and decide per step. A choice that is perfect for one step can drag on another.</p>
        {rows([("Discovery steps", "favour throughput and rotation"), ("Session steps", "favour low latency and sticky IPs"), ("Retries", "cap depth and watch the slow tail")])}
        """),
        ("geo", f"Coverage and latency in {geo}",
         f"""
        <p>Coverage and routing vary by country, so a verdict that holds in one market can flip in {geo}. Verify real IP location and test during peak and off-peak windows before deciding {dim}. If one option has thin {geo} coverage, that alone can settle it regardless of headline speed.</p>
        {rows([("Verify", "country, city and network"), ("Test window", f"peak and off-peak in {spec.geo}"), ("Deciding factor", "reproducible in-region latency")])}
        """),
        ("featured", "A value-focused alternative to benchmark",
         f"""
        <p>Whichever way {dim} leans for you, it is worth benchmarking against our featured value pick, <a href="{DEAL_URL}" target="_blank" rel="{DEAL_REL}">{DEAL_NAME}</a>. It covers multiple proxy categories at budget-friendly pricing, which makes it a useful speed-and-value yardstick for {audience} comparing {use_case}.</p>
        <p>Confirm the exact package and {geo} coverage before ordering, and compare it on the same latency-and-success-rate basis you use for {a} and {b}.</p>
        """),
        ("verdict", f"Verdict: {dim} for {use_case}",
         f"""
        <p>There is no universal winner &mdash; only the option with the lowest effective latency and highest success rate for <em>your</em> workload. Decide the session model first, benchmark both on {metric} in {geo}, and let a short pilot break the tie.</p>
        <div class="callout"><span class="callout__title">&#9989; Next step</span><p>Pilot both options on {use_case}, compare {metric}, and also test <a href="{DEAL_URL}" target="_blank" rel="{DEAL_REL}">{DEAL_NAME}</a> before you commit.</p></div>
        """),
    ]


def faq_items(spec: PageSpec) -> list[tuple[str, str]]:
    ptype = spec.ptype
    use_case = spec.use_case
    geo = spec.geo
    speed = spec.speed.lower()
    return [
        (f"What are the fastest {ptype} proxies for {use_case}?",
         f"The fastest {ptype} proxies for {use_case} are the ones with the lowest latency and highest success rate on your real targets - not the biggest advertised number. Match the proxy type to the task, benchmark latency and throughput across many requests, and check coverage in {geo}. We feature {DEAL_NAME} as our value pick because it bundles multiple proxy types at fast, budget-friendly rates."),
        (f"How fast are {ptype} proxies in {geo}?",
         f"{ptype.title()} proxies are usually {_tf(ptype, 'speed')}, with latency that is {_tf(ptype, 'latency')}. Real speed depends on network capacity, routing distance to {geo}, pool sharing and how many requests succeed. Measure latency, throughput and success rate together rather than trusting a single ping."),
        (f"Are cheap {ptype} proxies fast enough for {use_case}?",
         f"They can be, when the provider keeps a well-provisioned pool and you match the right type to {use_case}. Price alone does not guarantee speed, so benchmark latency and success rate on a small trial before scaling, and weigh effective speed against cost rather than choosing on the headline number."),
        (f"How do I get the {speed} proxy setup for {use_case}?",
         f"Pick the right proxy type first, benchmark providers on latency, throughput and success rate, verify {geo} coverage, and test on a small paid trial. Our speed reviews and comparison table make this quick, and {DEAL_NAME} is a practical value-focused starting point."),
    ]


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def sections_for(spec: PageSpec) -> list[tuple[str, str, str]]:
    if spec.category == "Speed Comparisons":
        return comparison_sections(spec)
    return guide_sections(spec)


def build_related_map(specs: list[PageSpec]) -> dict[str, list[PageSpec]]:
    n = len(specs)
    by_cat: dict[str, list[PageSpec]] = defaultdict(list)
    by_geo: dict[str, list[PageSpec]] = defaultdict(list)
    for s in specs:
        by_cat[s.category].append(s)
        by_geo[s.geo].append(s)
    cat_pos = {s.slug: i for lst in by_cat.values() for i, s in enumerate(lst)}
    geo_pos = {s.slug: i for lst in by_geo.values() for i, s in enumerate(lst)}

    related_map: dict[str, list[PageSpec]] = {}
    for s in specs:
        seen = {s.slug}
        rel: list[PageSpec] = []

        def push(x: PageSpec | None) -> None:
            if x is not None and x.slug not in seen:
                seen.add(x.slug)
                rel.append(x)

        push(specs[(s.idx - 2) % n])
        push(specs[s.idx % n])
        cl = by_cat[s.category]
        ci = cat_pos[s.slug]
        for j in (ci + 1, ci - 1, ci + 2, ci - 2, ci + 3):
            if 0 <= j < len(cl):
                push(cl[j])
        gl = by_geo[s.geo]
        gi = geo_pos[s.slug]
        for j in (gi + 1, gi - 1):
            if 0 <= j < len(gl):
                push(gl[j])
        related_map[s.slug] = rel[:6]
    return related_map


def blog_card(spec: PageSpec, prefix: str) -> str:
    ico = CATEGORY_ICON.get(spec.category, "⚡")
    return f"""
      <article class="blog-card">
        <a href="{prefix}{e(spec.slug)}.html" class="blog-card__thumb" aria-label="Read: {e(spec.title)}">
          <span class="blog-card__thumb-grid" aria-hidden="true"></span>
          <span class="blog-card__cat">{e(spec.category)}</span>
          <span class="blog-card__thumb-ico" aria-hidden="true">{ico}</span>
        </a>
        <div class="blog-card__body">
          <h3 class="blog-card__title"><a href="{prefix}{e(spec.slug)}.html">{e(spec.title)}</a></h3>
          <p class="blog-card__excerpt">{e(spec.description)}</p>
          <div class="blog-card__meta"><span>{e(spec.geo)}</span><a class="blog-card__more" href="{prefix}{e(spec.slug)}.html">Read &rarr;</a></div>
        </div>
      </article>"""


def render_article(spec: PageSpec, related: list[PageSpec]) -> str:
    canonical = f"{SITE}/seo/{spec.slug}.html"
    sections = sections_for(spec)
    n_sections = len(sections)
    read_min = max(9, round(n_sections * 0.9))
    toc = "\n".join(f'          <li><a href="#{sid}">{h2}</a></li>' for sid, h2, _ in sections)
    body = "\n".join(f'      <h2 id="{sid}">{h2}</h2>\n{html}' for sid, h2, html in sections)

    faqs = faq_items(spec)
    faq_html = "\n".join(
        f'        <details class="acc-item"><summary><span>{e(q)}</span><span class="acc-item__sign" aria-hidden="true"></span></summary><div class="acc-item__body"><p>{e(ans)}</p></div></details>'
        for q, ans in faqs
    )
    related_cards = "\n".join(blog_card(item, "") for item in related)

    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Article",
                "headline": spec.title,
                "description": spec.description,
                "datePublished": spec.modified,
                "dateModified": TODAY.isoformat(),
                "author": {"@type": "Organization", "name": "Fast Proxy Reviews"},
                "publisher": {"@type": "Organization", "name": "Fast Proxy Reviews", "url": f"{SITE}/"},
                "mainEntityOfPage": canonical,
                "inLanguage": "en",
                "articleSection": spec.category,
                "keywords": ", ".join(spec.keywords),
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
                    {"@type": "ListItem", "position": 2, "name": "Speed Library", "item": f"{SITE}/content-library.html"},
                    {"@type": "ListItem", "position": 3, "name": spec.title, "item": canonical},
                ],
            },
            {
                "@type": "FAQPage",
                "mainEntity": [
                    {"@type": "Question", "name": q,
                     "acceptedAnswer": {"@type": "Answer", "text": ans}}
                    for q, ans in faqs
                ],
            },
        ],
    }
    keywords = ", ".join(spec.keywords)
    prev_slug = related[0].slug if related else spec.slug
    next_slug = related[1].slug if len(related) > 1 else (related[0].slug if related else spec.slug)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<meta name="theme-color" content="#ffffff" />
<title>{e(spec.title)} | Fast Proxy Reviews</title>
<meta name="description" content="{e(spec.description)}" />
<meta name="keywords" content="{e(keywords)}" />
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1" />
<link rel="canonical" href="{canonical}" />
<meta property="og:type" content="article" />
<meta property="og:site_name" content="Fast Proxy Reviews" />
<meta property="og:title" content="{e(spec.title)}" />
<meta property="og:description" content="{e(spec.description)}" />
<meta property="og:url" content="{canonical}" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{e(spec.title)}" />
<meta name="twitter:description" content="{e(spec.description)}" />
<link rel="stylesheet" href="../style.css" />
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=True, separators=(",", ":"))}</script>
</head>
<body>
{header("../")}
<main>
<article>
<section class="page-hero">
  <div class="wrap page-hero__inner">
    <nav class="breadcrumb" aria-label="Breadcrumb"><a href="../index.html">Home</a><span>/</span><a href="../content-library.html">Speed Library</a><span>/</span>{e(spec.category)}</nav>
    <span class="eyebrow">{e(spec.category)} &middot; Updated {e(spec.modified)}</span>
    <h1>{e(spec.title)}</h1>
    <p class="page-hero__lead">{e(spec.description)}</p>
    <div class="post-meta">
      <span class="post-meta__cat">{e(spec.category)}</span>
      <span class="post-meta__chip">&#128197; Updated {e(spec.modified)}</span>
      <span class="post-meta__chip">&#9201; {read_min} min read</span>
      <span class="post-meta__chip">&#128300; Fast Proxy Reviews Lab</span>
    </div>
  </div>
</section>

<section class="guide">
  <div class="wrap">
    <div class="prose">
      <nav class="toc" aria-label="On this page">
        <p class="toc__title">In this article</p>
        <ol>
{toc}
        </ol>
      </nav>
{body}

      <div class="post-cta">
        <h2>Compare fast, affordable proxies before you buy</h2>
        <p>See our speed reviews and comparison table, then benchmark latency and success rate on your own targets before committing.</p>
        <a class="btn btn--primary btn--lg" href="{DEAL_URL}" target="_blank" rel="{DEAL_REL}">Visit {DEAL_NAME}</a>
      </div>

      <div class="author-box">
        <span class="author-box__avatar" aria-hidden="true"><svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2 4 14h6l-1 8 9-12h-6z"/></svg></span>
        <div>
          <div class="author-box__name">Fast Proxy Reviews Lab</div>
          <div class="author-box__role">Independent Proxy Speed &amp; Value Testing</div>
          <p>We benchmark and compare proxy providers on speed, reliability and value so you can buy on evidence, not marketing. We don't claim exact speed, uptime or latency &mdash; always test the exact plan before relying on it for critical workloads.</p>
        </div>
      </div>

      <section aria-label="Frequently asked questions">
        <div class="section-head" style="margin-bottom:1.4rem">
          <span class="eyebrow">Questions</span>
          <h2>Frequently asked questions</h2>
        </div>
        <div class="accordion">
{faq_html}
        </div>
      </section>

      <div class="related">
        <h2 class="related__title">Keep comparing proxy speed</h2>
        <div class="blog-grid">
{related_cards}
        </div>
      </div>

      <p class="post-meta" style="margin-top:2rem">
        <a class="blog-card__more" href="{prev_slug}.html">&larr; Previous review</a> &nbsp;&middot;&nbsp;
        <a class="blog-card__more" href="../content-library.html">Back to library</a> &nbsp;&middot;&nbsp;
        <a class="blog-card__more" href="{next_slug}.html">Next review &rarr;</a>
      </p>
    </div>
  </div>
</section>
</article>
</main>
{footer("../")}
</body>
</html>
"""


def hub_filename(category: str, page: int) -> str:
    base = f"content-library-{slugify(category)}"
    return f"{base}.html" if page == 1 else f"{base}-{page}.html"


def page_head(title: str, description: str, canonical: str,
              robots: str = "index, follow, max-image-preview:large, max-snippet:-1", extra: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<meta name="theme-color" content="#ffffff" />
<title>{e(title)}</title>
<meta name="description" content="{e(description)}" />
<meta name="robots" content="{robots}" />
<link rel="canonical" href="{canonical}" />
<meta property="og:type" content="website" />
<meta property="og:site_name" content="Fast Proxy Reviews" />
<meta property="og:title" content="{e(title)}" />
<meta property="og:description" content="{e(description)}" />
<meta property="og:url" content="{canonical}" />
<meta name="twitter:card" content="summary_large_image" />
<link rel="stylesheet" href="style.css" />
{extra}
</head>"""


def render_category_hubs(grouped: dict[str, list[PageSpec]]) -> dict[str, str]:
    pages: dict[str, str] = {}
    for category, items in grouped.items():
        total_pages = max(1, (len(items) + CARDS_PER_HUB - 1) // CARDS_PER_HUB)
        for page in range(1, total_pages + 1):
            start = (page - 1) * CARDS_PER_HUB
            chunk = items[start:start + CARDS_PER_HUB]
            cards = "\n".join(blog_card(s, "seo/") for s in chunk)
            fname = hub_filename(category, page)
            canonical = f"{SITE}/{fname}"
            pager = []
            if page > 1:
                pager.append(f'<a class="btn btn--ghost btn--sm" href="{hub_filename(category, page - 1)}">&larr; Newer</a>')
            else:
                pager.append("<span></span>")
            if page < total_pages:
                pager.append(f'<a class="btn btn--ghost btn--sm" href="{hub_filename(category, page + 1)}">Older &rarr;</a>')
            else:
                pager.append("<span></span>")
            title = f"{category} - Fast Proxy Reviews Speed Library" + (f" (Page {page})" if page > 1 else "")
            desc = meta_description(
                f"Browse {len(items):,} {category.lower()} guides in the Fast Proxy Reviews speed library - "
                f"benchmark-style proxy speed reviews, comparisons and value picks."
            )
            head = page_head(title, desc, canonical)
            pages[fname] = f"""{head}
<body>
{header("", "library")}
<main>
<section class="page-hero">
  <div class="wrap page-hero__inner">
    <nav class="breadcrumb" aria-label="Breadcrumb"><a href="index.html">Home</a><span>/</span><a href="content-library.html">Speed Library</a><span>/</span>{e(category)}</nav>
    <span class="eyebrow">{len(items):,} guides &middot; Page {page} of {total_pages}</span>
    <h1>{e(category)}</h1>
    <p class="page-hero__lead">Benchmark-style proxy speed guides in the {e(category.lower())} cluster &mdash; latency, throughput, comparisons and value-focused picks that all point to our featured pick, {DEAL_NAME}.</p>
  </div>
</section>
<section class="providers">
  <div class="wrap">
    <div class="blog-grid">
{cards}
    </div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-top:2.4rem;gap:1rem">
      {pager[0]}
      {pager[1]}
    </div>
  </div>
</section>
</main>
{footer("")}
</body>
</html>
"""
    return pages


def render_hub(specs: list[PageSpec], grouped: dict[str, list[PageSpec]]) -> str:
    total = len(specs)
    cluster_cards = "\n".join(
        f"""
      <article class="blog-card">
        <a href="{hub_filename(category, 1)}" class="blog-card__thumb" aria-label="Browse {e(category)}">
          <span class="blog-card__thumb-grid" aria-hidden="true"></span>
          <span class="blog-card__cat">{len(items):,} guides</span>
          <span class="blog-card__thumb-ico" aria-hidden="true">{CATEGORY_ICON.get(category, "⚡")}</span>
        </a>
        <div class="blog-card__body">
          <h3 class="blog-card__title"><a href="{hub_filename(category, 1)}">{e(category)}</a></h3>
          <p class="blog-card__excerpt">Benchmark-style proxy speed guides focused on {e(category.lower())}, with latency, throughput, comparisons and internal links into related reviews.</p>
          <div class="blog-card__meta"><span>{len(items):,} guides</span><a class="blog-card__more" href="{hub_filename(category, 1)}">Browse &rarr;</a></div>
        </div>
      </article>"""
        for category, items in grouped.items()
    )
    item_list = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "Fast Proxy Reviews Speed Library",
        "numberOfItems": len(grouped),
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": category, "url": f"{SITE}/{hub_filename(category, 1)}"}
            for i, category in enumerate(grouped)
        ],
    }
    extra = f'<script type="application/ld+json">{json.dumps(item_list, ensure_ascii=True, separators=(",", ":"))}</script>'
    head = page_head(
        f"Proxy Speed Library - {total:,} Fast Proxy Reviews &amp; Comparisons (2026)",
        f"Browse {total:,} in-depth proxy speed guides covering the fastest proxies by type, use case, platform, "
        f"country and city - with benchmark-style comparisons and value-focused picks.",
        f"{SITE}/content-library.html",
        extra=extra,
    )
    return f"""{head}
<body>
{header("", "library")}
<main>
<section class="page-hero">
  <div class="wrap page-hero__inner">
    <nav class="breadcrumb" aria-label="Breadcrumb"><a href="index.html">Home</a><span>/</span>Speed Library</nav>
    <span class="eyebrow">{total:,} speed guides &middot; Updated {TODAY.isoformat()}</span>
    <h1>Proxy Speed Library</h1>
    <p class="page-hero__lead">A deep resource hub of {total:,} proxy speed reviews &mdash; each built around a unique search, with latency and throughput guidance, comparisons, FAQs, related links and value-focused recommendations.</p>
  </div>
</section>

<section class="overview">
  <div class="wrap">
    <ul class="stat-strip" aria-label="Library at a glance">
      <li><span class="stat-num">{total:,}</span><span class="stat-lab">Speed guides</span></li>
      <li><span class="stat-num">{len(grouped)}</span><span class="stat-lab">Topic clusters</span></li>
      <li><span class="stat-num">{len(GEOS)}</span><span class="stat-lab">Countries covered</span></li>
      <li><span class="stat-num">{len(PROXY_TYPES)}</span><span class="stat-lab">Proxy types</span></li>
    </ul>

    <div class="section-head section-head--center" style="margin-top:3rem">
      <span class="eyebrow">Browse by cluster</span>
      <h2>Explore the proxy speed clusters</h2>
      <p class="section-sub">Each cluster is a paginated hub of benchmark-style proxy speed guides that link into related comparisons and latency resources.</p>
    </div>
    <div class="blog-grid">
{cluster_cards}
    </div>
  </div>
</section>

<section class="cta-strip" aria-label="Featured pick call to action">
  <div class="wrap cta-strip__inner">
    <div>
      <h2 class="cta-strip__title">Comparing fast, affordable proxies?</h2>
      <p class="cta-strip__sub">Start with our featured value pick, then benchmark it against the field on your own targets.</p>
    </div>
    <div class="cta-strip__actions">
      <a class="btn btn--primary btn--lg" href="{DEAL_URL}" target="_blank" rel="{DEAL_REL}">Visit {DEAL_NAME}</a>
      <a class="btn btn--ghost btn--lg" href="index.html#compare">Compare Providers</a>
    </div>
  </div>
</section>
</main>
{footer("")}
</body>
</html>
"""


STATIC_URLS = [
    ("", "weekly", "1.0"),
    ("index.html", "weekly", "1.0"),
    ("content-library.html", "weekly", "0.9"),
    ("blog.html", "weekly", "0.8"),
    ("tips.html", "monthly", "0.7"),
    ("about.html", "yearly", "0.5"),
    ("privacy-policy.html", "yearly", "0.3"),
    ("blog-fastest-proxy-providers-2026.html", "monthly", "0.6"),
    ("blog-how-to-test-proxy-speed.html", "monthly", "0.6"),
    ("blog-residential-vs-datacenter-speed.html", "monthly", "0.6"),
    ("blog-cheap-fast-proxies-value.html", "monthly", "0.6"),
]


def render_sitemaps(specs: list[PageSpec], hub_files: list[str]) -> dict[str, str]:
    lastmod = TODAY.isoformat()
    urls: list[str] = []
    for path, changefreq, priority in STATIC_URLS:
        loc = f"{SITE}/{path}" if path else f"{SITE}/"
        urls.append(f"  <url><loc>{loc}</loc><lastmod>{lastmod}</lastmod><changefreq>{changefreq}</changefreq><priority>{priority}</priority></url>")
    for hub in hub_files:
        urls.append(f"  <url><loc>{SITE}/{hub}</loc><lastmod>{lastmod}</lastmod><changefreq>weekly</changefreq><priority>0.6</priority></url>")
    for spec in specs:
        urls.append(f"  <url><loc>{SITE}/seo/{spec.slug}.html</loc><lastmod>{spec.modified}</lastmod><changefreq>monthly</changefreq><priority>0.6</priority></url>")

    files: dict[str, str] = {}
    chunks = [urls[i:i + SITEMAP_CHUNK] for i in range(0, len(urls), SITEMAP_CHUNK)] or [[]]
    chunk_names = []
    for i, chunk in enumerate(chunks, start=1):
        name = f"sitemap-{i}.xml"
        chunk_names.append(name)
        files[name] = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "\n".join(chunk) + "\n</urlset>\n"
        )
    index = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(f"  <sitemap><loc>{SITE}/{n}</loc><lastmod>{lastmod}</lastmod></sitemap>" for n in chunk_names)
        + "\n</sitemapindex>\n"
    )
    files["sitemap.xml"] = index
    return files


def write_json_manifest(specs: list[PageSpec]) -> None:
    manifest = [asdict(spec) for spec in specs]
    (SITE_OUT / "seo-library-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def write_robots() -> None:
    txt = (
        "User-agent: *\n"
        "Allow: /\n\n"
        f"Sitemap: {SITE}/sitemap.xml\n"
    )
    (SITE_OUT / "robots.txt").write_text(txt, encoding="utf-8", newline="\n")


def group_by_category(specs: list[PageSpec]) -> dict[str, list[PageSpec]]:
    grouped: dict[str, list[PageSpec]] = {}
    for spec in specs:
        grouped.setdefault(spec.category, []).append(spec)
    return grouped


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    SITE_OUT.mkdir(parents=True, exist_ok=True)

    for old_page in OUT_DIR.glob("*.html"):
        old_page.unlink()
    for old_hub in SITE_OUT.glob("content-library*.html"):
        old_hub.unlink()
    for old_map in SITE_OUT.glob("sitemap-*.xml"):
        old_map.unlink()

    specs = build_specs()
    assert len({s.slug for s in specs}) == len(specs), "duplicate slug detected"
    related_map = build_related_map(specs)

    for spec in specs:
        (OUT_DIR / f"{spec.slug}.html").write_text(
            render_article(spec, related_map[spec.slug]), encoding="utf-8", newline="\n"
        )

    grouped = group_by_category(specs)
    hub_pages = render_category_hubs(grouped)
    for fname, html in hub_pages.items():
        (SITE_OUT / fname).write_text(html, encoding="utf-8", newline="\n")

    (SITE_OUT / "content-library.html").write_text(render_hub(specs, grouped), encoding="utf-8", newline="\n")

    sitemaps = render_sitemaps(specs, list(hub_pages.keys()))
    for fname, xml in sitemaps.items():
        (SITE_OUT / fname).write_text(xml, encoding="utf-8", newline="\n")

    write_json_manifest(specs)
    write_robots()

    print(f"Generated {len(specs):,} SEO pages in {OUT_DIR}")
    print(f"Generated {len(hub_pages)} category hub pages across {len(grouped)} clusters")
    print("Clusters: " + ", ".join(f"{c}={len(v):,}" for c, v in grouped.items()))
    print(f"Wrote content-library.html, {len([k for k in sitemaps if k != 'sitemap.xml'])} sitemap chunk(s) + sitemap.xml index, robots.txt, and seo-library-manifest.json")


if __name__ == "__main__":
    main()
