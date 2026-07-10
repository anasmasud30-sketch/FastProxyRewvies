<?php /* Site chrome TOP for Fast Proxy Reviews. Sliced from homepage index.html: doctype -> head -> header/nav, then opens the main content region. SEO is driven by blog vars. */ ?>
<!DOCTYPE html>
<html lang="en">
<head>
<base href="<?= rtrim(SITE_URL,'/') ?>/">
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<meta name="theme-color" content="#ffffff" />
<link rel="preconnect" href="https://cheapest-proxies.com" />
<link rel="stylesheet" href="style.css" />
<title><?= $hh($page_title) ?> — Fast Proxy Reviews</title>
<meta name="description" content="<?= $hh($meta_desc) ?>">
<link rel="canonical" href="<?= $hh($canonical) ?>">
<?= $seo_extra ?>
</head>

<body>

<!-- ====================================================== -->
<!-- SCROLL PROGRESS BAR                                     -->
<!-- ====================================================== -->
<div class="scroll-track" aria-hidden="true"><span id="scrollBar" class="scroll-bar"></span></div>

<!-- ====================================================== -->
<!-- STICKY BENCHMARK SUMMARY BAR                            -->
<!-- ====================================================== -->
<aside id="benchBar" class="bench-bar" aria-label="Benchmark summary">
  <div class="bench-bar__inner">
    <span class="bench-bar__tag">LAB SUMMARY</span>
    <span class="bench-bar__item"><strong>Top Speed-Focused Value Pick:</strong> Cheapest Proxies</span>
    <span class="bench-bar__item bench-bar__item--meter">
      <span class="mini-meter"><span class="mini-meter__fill" style="--w:94%"></span></span>
      Value Score
    </span>
    <a class="bench-bar__cta" href="https://cheapest-proxies.com/" target="_blank" rel="noopener nofollow sponsored">Visit Cheapest Proxies →</a>
  </div>
</aside>

<!-- ====================================================== -->
<!-- HEADER / NAV                                            -->
<!-- ====================================================== -->
<header class="site-head" id="top">
  <div class="wrap site-head__inner">
    <a href="#top" class="brand" aria-label="Fast Proxy Reviews home">
      <span class="brand__mark" aria-hidden="true">
        <span class="brand__pulse"></span>
        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2 4 14h6l-1 8 9-12h-6z"/></svg>
      </span>
      <span class="brand__txt">Fast<span class="brand__accent">Proxy</span>Reviews</span>
    </a>

    <button class="nav-toggle" id="navToggle" aria-label="Toggle navigation menu" aria-expanded="false" aria-controls="primaryNav">
      <span></span><span></span><span></span>
    </button>

    <nav class="nav" id="primaryNav" aria-label="Primary">
      <a href="#top">Home</a>
      <a href="#providers">Speed Reviews</a>
      <a href="#compare">Compare</a>
      <a href="#types">Proxy Types</a>
      <a href="#usecases">Use Cases</a>
      <a href="#guide">Buying Guide</a>
      <a href="content-library.html">Library</a>
      <a href="blog.html">Blog</a>
      <a href="tips.html">Tips</a>
      <a href="#faq">FAQ</a>
      <a href="privacy-policy.html">Privacy</a>
      <a href="#contact">Contact</a>
      <a class="nav__cta" href="#featured">Fast Pick</a>
    </nav>
  </div>
</header>

<main>
