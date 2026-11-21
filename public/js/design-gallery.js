/* Horizontal swipe galleries for the /designer/ page. No external library.
   Mobile: CSS scroll-snap + native touch swipe.
   Desktop: mouse click-and-drag, prev/next buttons, and dots.
   Trackpad: native overflow scroll with CSS scroll-snap.
   Keyboard arrows when the gallery or fullscreen viewer is focused.
   Click a slide (without a drag) to open a full-screen viewer;
   swipe or drag in the viewer to change photos. */
(function () {
  var galleries = [];
  var DRAG_THRESHOLD = 8;
  var FS_SWIPE_THRESHOLD = 50;

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
    var left = g.slides[i].offsetLeft;
    if (typeof g.track.scrollTo === "function") {
      g.track.scrollTo({ left: left, behavior: behavior || "smooth" });
    } else {
      g.slides[i].scrollIntoView({ behavior: behavior || "smooth", block: "nearest", inline: "start" });
    }
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

  function isMouseLike(e) {
    return e.pointerType === "mouse" || e.pointerType === "pen";
  }

  function bindTrackDrag(g) {
    var track = g.track;
    var startX = 0;
    var startLeft = 0;
    var pointerId = null;
    var armed = false;
    var dragging = false;

    track.addEventListener("dragstart", function (e) { e.preventDefault(); }, true);
    track.querySelectorAll("img").forEach(function (img) {
      img.setAttribute("draggable", "false");
    });

    track.addEventListener("pointerdown", function (e) {
      if (!isMouseLike(e) || e.button !== 0) return;
      if (e.target.closest("[data-gallery-prev],[data-gallery-next],[data-gallery-dot]")) return;
      armed = true;
      dragging = false;
      g.suppressClick = false;
      startX = e.clientX;
      startLeft = track.scrollLeft;
      pointerId = e.pointerId;
    });

    track.addEventListener("pointermove", function (e) {
      if (!armed || e.pointerId !== pointerId) return;
      var dx = e.clientX - startX;
      if (!dragging) {
        if (Math.abs(dx) < DRAG_THRESHOLD) return;
        dragging = true;
        g.suppressClick = true;
        track.classList.add("is-dragging");
        try { track.setPointerCapture(pointerId); } catch (err) {}
      }
      e.preventDefault();
      track.scrollLeft = startLeft - dx;
    }, { passive: false });

    function endDrag(e) {
      if (!armed || (e && pointerId != null && e.pointerId !== pointerId)) return;
      armed = false;
      if (dragging) {
        track.classList.remove("is-dragging");
        if (pointerId != null) {
          try { track.releasePointerCapture(pointerId); } catch (err) {}
        }
        goTo(g, closestSlideIndex(track), "smooth");
        setTimeout(function () { g.suppressClick = false; }, 0);
      }
      dragging = false;
      pointerId = null;
    }

    track.addEventListener("pointerup", endDrag);
    track.addEventListener("pointercancel", endDrag);
    track.addEventListener("lostpointercapture", function () {
      if (armed && dragging) {
        armed = false;
        track.classList.remove("is-dragging");
        goTo(g, closestSlideIndex(track), "smooth");
        setTimeout(function () { g.suppressClick = false; }, 0);
        dragging = false;
        pointerId = null;
      }
    });
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
      index: 0,
      suppressClick: false
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

    bindTrackDrag(g);

    g.slides.forEach(function (slide) {
      var btn = slide.querySelector("[data-gallery-open]") || slide;
      btn.addEventListener("click", function (e) {
        if (g.suppressClick) {
          e.preventDefault();
          e.stopPropagation();
          return;
        }
        if (e.target.closest("[data-gallery-prev],[data-gallery-next],[data-gallery-dot]")) return;
        openFullscreen(g);
      });
    });

    sync(g);
  }

  document.querySelectorAll("[data-project-gallery]").forEach(bind);

  function activeGallery() {
    return galleries.filter(function (g) { return g.root.getAttribute("data-fullscreen-open") === "true"; })[0];
  }

  function bindFsSwipe(fs) {
    var stage = fs.querySelector(".fs-stage");
    if (!stage) return;
    var startX = 0;
    var startY = 0;
    var pointerId = null;
    var armed = false;
    var dragging = false;

    stage.addEventListener("dragstart", function (e) { e.preventDefault(); }, true);
    var fsImg = stage.querySelector("img");
    if (fsImg) fsImg.setAttribute("draggable", "false");

    stage.addEventListener("pointerdown", function (e) {
      if (e.target.closest("[data-fs-prev],[data-fs-next],[data-fs-close]")) return;
      if (e.button && e.button !== 0) return;
      armed = true;
      dragging = false;
      pointerId = e.pointerId;
      startX = e.clientX;
      startY = e.clientY;
      try { stage.setPointerCapture(pointerId); } catch (err) {}
    });

    stage.addEventListener("pointermove", function (e) {
      if (!armed || e.pointerId !== pointerId) return;
      var dx = e.clientX - startX;
      if (!dragging && Math.abs(dx) >= DRAG_THRESHOLD) {
        dragging = true;
        stage.classList.add("is-dragging");
      }
    });

    function endSwipe(e) {
      if (!armed || (e && pointerId != null && e.pointerId !== pointerId)) return;
      armed = false;
      stage.classList.remove("is-dragging");
      var dx = e.clientX - startX;
      var dy = e.clientY - startY;
      var wasDrag = dragging;
      dragging = false;
      pointerId = null;
      if (!wasDrag) return;
      if (Math.abs(dx) < FS_SWIPE_THRESHOLD || Math.abs(dx) < Math.abs(dy)) return;
      var g = activeGallery();
      if (!g) return;
      if (dx < 0) goTo(g, g.index + 1);
      else goTo(g, g.index - 1);
    }

    stage.addEventListener("pointerup", endSwipe);
    stage.addEventListener("pointercancel", endSwipe);
  }

  var fs = document.getElementById("design-gallery-fs");
  if (fs) {
    bindFsSwipe(fs);
    fs.querySelectorAll("[data-fs-close]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var g = activeGallery();
        if (g) closeFullscreen(g);
      });
    });
    fs.addEventListener("click", function (e) {
      if (e.target === fs) {
        var g = activeGallery();
        if (g) closeFullscreen(g);
      }
    });
    var prev = fs.querySelector("[data-fs-prev]");
    var next = fs.querySelector("[data-fs-next]");
    if (prev) prev.addEventListener("click", function () { var g = activeGallery(); if (g) goTo(g, g.index - 1); });
    if (next) next.addEventListener("click", function () { var g = activeGallery(); if (g) goTo(g, g.index + 1); });
    fs.addEventListener("keydown", function (e) {
      var g = activeGallery();
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
