/* Horizontal swipe galleries for the /design/ page. No external library.
   Mobile: CSS scroll-snap + touch swipe.
   Desktop: prev/next buttons and dots.
   Keyboard arrows when the gallery is focused.
   Click a slide to open a full-screen viewer. */
(function () {
  var galleries = [];

  function prefersDesktop() {
    return window.matchMedia("(min-width: 1024px)").matches;
  }

  function closestSlideIndex(track) {
    var slides = track.querySelectorAll("[data-gallery-slide]");
    if (!slides.length) return 0;
    var left = track.scrollLeft;
    var best = 0;
    var bestDist = Infinity;
    for (var i = 0; i < slides.length; i++) {
      var dist = Math.abs(slides[i].offsetLeft - left);
      if (dist < bestDist) {
        bestDist = dist;
        best = i;
      }
    }
    return best;
  }

  function goTo(g, index, behavior) {
    var n = g.slides.length;
    if (!n) return;
    var i = ((index % n) + n) % n;
    g.index = i;
    g.slides[i].scrollIntoView({ behavior: behavior || "smooth", block: "nearest", inline: "start" });
    sync(g);
  }

  function sync(g) {
    var i = g.index;
    var n = g.slides.length;
    g.dots.forEach(function (dot, di) {
      var on = di === i;
      dot.classList.toggle("is-active", on);
      dot.setAttribute("aria-current", on ? "true" : "false");
    });
    if (g.prev) g.prev.disabled = n <= 1;
    if (g.next) g.next.disabled = n <= 1;
    if (g.status) g.status.textContent = "Photo " + (i + 1) + " of " + n;
    if (g.root.getAttribute("data-fullscreen-open") === "true") {
      updateFullscreen(g);
    }
  }

  function updateFullscreen(g) {
    var img = g.slides[g.index] && g.slides[g.index].querySelector("img");
    if (!g.fsImg || !img) return;
    g.fsImg.src = img.currentSrc || img.src;
    g.fsImg.alt = img.alt || "";
    if (g.fsStatus) g.fsStatus.textContent = (g.index + 1) + " / " + g.slides.length;
    if (g.fsCaption) g.fsCaption.textContent = g.label;
  }

  function openFullscreen(g) {
    if (!g.fs) return;
    g.root.setAttribute("data-fullscreen-open", "true");
    updateFullscreen(g);
    if (typeof g.fs.showModal === "function") g.fs.showModal();
    else g.fs.setAttribute("open", "");
    document.documentElement.style.overflow = "hidden";
    if (g.fsClose) g.fsClose.focus();
  }

  function closeFullscreen(g) {
    if (!g.fs) return;
    g.root.setAttribute("data-fullscreen-open", "false");
    if (typeof g.fs.close === "function" && g.fs.open) g.fs.close();
    else g.fs.removeAttribute("open");
    document.documentElement.style.overflow = "";
  }

  function bind(root) {
    var track = root.querySelector("[data-gallery-track]");
    if (!track) return;
    var g = {
      root: root,
      track: track,
      slides: Array.prototype.slice.call(root.querySelectorAll("[data-gallery-slide]")),
      prev: root.querySelector("[data-gallery-prev]"),
      next: root.querySelector("[data-gallery-next]"),
      dots: Array.prototype.slice.call(root.querySelectorAll("[data-gallery-dot]")),
      status: root.querySelector("[data-gallery-status]"),
      fs: document.getElementById("design-gallery-fs"),
      fsImg: document.querySelector("#design-gallery-fs img"),
      fsStatus: document.querySelector("#design-gallery-fs [data-fs-status]"),
      fsCaption: document.querySelector("#design-gallery-fs [data-fs-caption]"),
      fsClose: document.querySelector("#design-gallery-fs [data-fs-close]"),
      label: root.getAttribute("data-project-label") || "Project photo",
      index: 0
    };
    galleries.push(g);

    var ticking = false;
    track.addEventListener("scroll", function () {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(function () {
        g.index = closestSlideIndex(track);
        sync(g);
        ticking = false;
      });
    }, { passive: true });

    if (g.prev) g.prev.addEventListener("click", function () { goTo(g, g.index - 1); });
    if (g.next) g.next.addEventListener("click", function () { goTo(g, g.index + 1); });
    g.dots.forEach(function (dot, di) {
      dot.addEventListener("click", function () { goTo(g, di); });
    });

    root.addEventListener("keydown", function (e) {
      if (e.key === "ArrowLeft") { e.preventDefault(); goTo(g, g.index - 1); }
      else if (e.key === "ArrowRight") { e.preventDefault(); goTo(g, g.index + 1); }
      else if (e.key === "Escape" && root.getAttribute("data-fullscreen-open") === "true") {
        e.preventDefault();
        closeFullscreen(g);
      }
    });

    g.slides.forEach(function (slide) {
      var btn = slide.querySelector("[data-gallery-open]") || slide;
      btn.addEventListener("click", function (e) {
        if (e.target.closest("[data-gallery-prev],[data-gallery-next],[data-gallery-dot]")) return;
        openFullscreen(g);
      });
    });

    sync(g);
  }

  document.querySelectorAll("[data-project-gallery]").forEach(bind);

  var fs = document.getElementById("design-gallery-fs");
  if (fs) {
    var active = function () {
      return galleries.filter(function (g) { return g.root.getAttribute("data-fullscreen-open") === "true"; })[0];
    };
    fs.querySelectorAll("[data-fs-close]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var g = active();
        if (g) closeFullscreen(g);
      });
    });
    fs.addEventListener("click", function (e) {
      if (e.target === fs) {
        var g = active();
        if (g) closeFullscreen(g);
      }
    });
    var prev = fs.querySelector("[data-fs-prev]");
    var next = fs.querySelector("[data-fs-next]");
    if (prev) prev.addEventListener("click", function () { var g = active(); if (g) goTo(g, g.index - 1); });
    if (next) next.addEventListener("click", function () { var g = active(); if (g) goTo(g, g.index + 1); });
    fs.addEventListener("keydown", function (e) {
      var g = active();
      if (!g) return;
      if (e.key === "ArrowLeft") { e.preventDefault(); goTo(g, g.index - 1); }
      else if (e.key === "ArrowRight") { e.preventDefault(); goTo(g, g.index + 1); }
    });
    fs.addEventListener("close", function () {
      galleries.forEach(function (g) {
        if (g.root.getAttribute("data-fullscreen-open") === "true") {
          g.root.setAttribute("data-fullscreen-open", "false");
        }
      });
      document.documentElement.style.overflow = "";
    });
  }
})();
