/**
 * Shop freeform body compat loader.
 * Synchronously pulls in content-body.js (same directory / ?v=).
 * Mount: <div id="shop-body" data-shop-slug="..."></div>
 */
(function () {
  if (window.GuideContentBody) return;
  var scr = document.currentScript;
  var src = (scr && scr.src) || "";
  var next = src.replace(/shop-body\.js/i, "content-body.js");
  if (!next || next === src) {
    next = src.replace(/[^/]*$/, "content-body.js");
  }
  /* Sync insert while parsing — keeps shop pages working without a second manual script tag. */
  document.write('<script src="' + next.replace(/"/g, "&quot;") + '"><\/script>');
})();
