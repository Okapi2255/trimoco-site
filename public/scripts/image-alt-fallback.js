/**
 * Ensures <img> elements have accessible text:
 * - Missing `alt` → derived from main h1, then any h1, then document title.
 * - Missing `title` → same as non-empty `alt`, or the same fallback as `alt`.
 * Does not override existing non-empty attributes.
 * Skips subtrees marked with `data-skip-img-alt-fallback`.
 */
(function () {
  function deriveFallbackLabel() {
    var mainH1 = document.querySelector('main h1');
    if (mainH1 && mainH1.textContent) {
      var t = mainH1.textContent.replace(/\s+/g, ' ').trim();
      if (t) return t;
    }
    var anyH1 = document.querySelector('h1');
    if (anyH1 && anyH1.textContent) {
      var t2 = anyH1.textContent.replace(/\s+/g, ' ').trim();
      if (t2) return t2;
    }
    var docTitle = document.title || '';
    return docTitle.replace(/\s*\|\s*[^|]+\s*$/, '').trim() || docTitle.trim() || 'Page image';
  }

  function applyToImg(img, label) {
    if (img.closest('[data-skip-img-alt-fallback]')) return;

    var fallback = label + ' — image';

    if (!img.hasAttribute('alt')) {
      img.setAttribute('alt', fallback);
    }

    if (!img.hasAttribute('title')) {
      var alt = img.getAttribute('alt');
      if (alt && alt.trim()) {
        img.setAttribute('title', alt);
      } else {
        img.setAttribute('title', fallback);
      }
    }
  }

  function run() {
    var label = deriveFallbackLabel();
    document.querySelectorAll('img').forEach(function (img) {
      applyToImg(img, label);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run);
  } else {
    run();
  }
})();
