/* ==========================================================================
   FAST PROXY REVIEWS — front-end interactions (vanilla JS, no dependencies)
   Features:
   1. Scroll progress bar
   2. Sticky benchmark summary bar (appears after hero)
   3. Back-to-top button
   4. Mobile navigation toggle
   5. Animated speedometer "perf index" counter
   6. Single-open FAQ accordion behaviour
   7. Active nav link highlighting via IntersectionObserver
   ========================================================================== */
(function () {
  "use strict";

  var prefersReduced =
    window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- cached elements ---------- */
  var scrollBar = document.getElementById("scrollBar");
  var benchBar = document.getElementById("benchBar");
  var toTop = document.getElementById("toTop");
  var navToggle = document.getElementById("navToggle");
  var nav = document.getElementById("primaryNav");
  var hero = document.querySelector(".hero");

  /* ---------- 1 + 2 + 3: scroll-driven UI (throttled with rAF) ---------- */
  var ticking = false;

  function onScroll() {
    var scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    var docHeight =
      document.documentElement.scrollHeight - window.innerHeight;
    var pct = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;

    if (scrollBar) scrollBar.style.width = pct + "%";

    // Reveal sticky bench bar + back-to-top once the user passes the hero.
    var trigger = hero ? hero.offsetHeight * 0.75 : 600;
    var passed = scrollTop > trigger;

    if (benchBar) benchBar.classList.toggle("is-visible", passed);
    if (toTop) toTop.classList.toggle("is-visible", passed);

    ticking = false;
  }

  function requestScroll() {
    if (!ticking) {
      window.requestAnimationFrame(onScroll);
      ticking = true;
    }
  }

  window.addEventListener("scroll", requestScroll, { passive: true });
  window.addEventListener("resize", requestScroll);
  onScroll(); // initialise

  /* ---------- back-to-top click ---------- */
  if (toTop) {
    toTop.addEventListener("click", function () {
      window.scrollTo({
        top: 0,
        behavior: prefersReduced ? "auto" : "smooth"
      });
    });
  }

  /* ---------- 4: mobile nav toggle ---------- */
  if (navToggle && nav) {
    navToggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      navToggle.setAttribute("aria-expanded", open ? "true" : "false");
    });

    // Close the menu after tapping a link (mobile).
    nav.addEventListener("click", function (e) {
      if (e.target.tagName === "A" && nav.classList.contains("is-open")) {
        nav.classList.remove("is-open");
        navToggle.setAttribute("aria-expanded", "false");
      }
    });
  }

  /* ---------- 5: animated speedometer perf index ---------- */
  var speedoNum = document.getElementById("speedoNum");
  if (speedoNum) {
    var target = 94; // matches the gauge fill / value score
    if (prefersReduced) {
      speedoNum.textContent = target;
    } else {
      var current = 0;
      var stepStart = null;
      var duration = 1900;

      var animateCount = function (ts) {
        if (stepStart === null) stepStart = ts;
        var progress = Math.min((ts - stepStart) / duration, 1);
        // easeOutCubic
        var eased = 1 - Math.pow(1 - progress, 3);
        current = Math.round(eased * target);
        speedoNum.textContent = current;
        if (progress < 1) window.requestAnimationFrame(animateCount);
      };

      // Kick off when the gauge scrolls into view.
      if ("IntersectionObserver" in window) {
        var gaugeObs = new IntersectionObserver(
          function (entries, obs) {
            entries.forEach(function (entry) {
              if (entry.isIntersecting) {
                window.requestAnimationFrame(animateCount);
                obs.disconnect();
              }
            });
          },
          { threshold: 0.4 }
        );
        gaugeObs.observe(speedoNum);
      } else {
        window.requestAnimationFrame(animateCount);
      }
    }
  }

  /* ---------- 6: single-open FAQ accordion ---------- */
  var accItems = Array.prototype.slice.call(
    document.querySelectorAll("#accordion .acc-item")
  );
  accItems.forEach(function (item) {
    item.addEventListener("toggle", function () {
      if (item.open) {
        accItems.forEach(function (other) {
          if (other !== item) other.open = false;
        });
      }
    });
  });

  /* ---------- 7: active nav link highlighting ---------- */
  var sections = Array.prototype.slice.call(
    document.querySelectorAll("main section[id], #top")
  );
  var navLinks = Array.prototype.slice.call(
    document.querySelectorAll('.nav > a[href^="#"]')
  );

  if ("IntersectionObserver" in window && navLinks.length) {
    var linkMap = {};
    navLinks.forEach(function (a) {
      linkMap[a.getAttribute("href").slice(1)] = a;
    });

    var sectionObs = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            navLinks.forEach(function (a) {
              a.removeAttribute("aria-current");
            });
            var active = linkMap[entry.target.id];
            if (active) active.setAttribute("aria-current", "true");
          }
        });
      },
      { rootMargin: "-45% 0px -50% 0px" }
    );

    sections.forEach(function (sec) {
      if (sec.id) sectionObs.observe(sec);
    });
  }
})();
