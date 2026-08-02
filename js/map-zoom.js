/**
 * Simple pan/zoom for schematic subway map images.
 */
(function () {
  function bind(root) {
    var viewport = root.querySelector(".map-zoom-viewport");
    var img = root.querySelector(".map-zoom-img");
    if (!viewport || !img) return;

    var scale = 1;
    var min = 1;
    var max = 4;
    var x = 0;
    var y = 0;
    var dragging = false;
    var startX = 0;
    var startY = 0;
    var origX = 0;
    var origY = 0;

    function apply() {
      img.style.transform = "translate(" + x + "px," + y + "px) scale(" + scale + ")";
    }

    function zoom(factor, cx, cy) {
      var prev = scale;
      scale = Math.min(max, Math.max(min, scale * factor));
      if (cx != null && cy != null) {
        var rect = viewport.getBoundingClientRect();
        var px = cx - rect.left - rect.width / 2;
        var py = cy - rect.top - rect.height / 2;
        x = px - ((px - x) * scale) / prev;
        y = py - ((py - y) * scale) / prev;
      }
      if (scale === 1) {
        x = 0;
        y = 0;
      }
      apply();
    }

    root.querySelectorAll("[data-map-zoom]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var action = btn.getAttribute("data-map-zoom");
        if (action === "in") zoom(1.25);
        else if (action === "out") zoom(1 / 1.25);
        else if (action === "reset") {
          scale = 1;
          x = 0;
          y = 0;
          apply();
        }
      });
    });

    viewport.addEventListener(
      "wheel",
      function (e) {
        e.preventDefault();
        zoom(e.deltaY < 0 ? 1.1 : 1 / 1.1, e.clientX, e.clientY);
      },
      { passive: false }
    );

    viewport.addEventListener("pointerdown", function (e) {
      if (scale <= 1) return;
      dragging = true;
      startX = e.clientX;
      startY = e.clientY;
      origX = x;
      origY = y;
      viewport.setPointerCapture(e.pointerId);
    });
    viewport.addEventListener("pointermove", function (e) {
      if (!dragging) return;
      x = origX + (e.clientX - startX);
      y = origY + (e.clientY - startY);
      apply();
    });
    viewport.addEventListener("pointerup", function () {
      dragging = false;
    });
  }

  function init() {
    document.querySelectorAll("[data-map-zoom-root]").forEach(bind);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
