/* Generic tab / select switcher for guidebook sections */
(function () {
  function activate(root, name, kind) {
    var buttons = root.querySelectorAll("[data-" + kind + "-tab]");
    var panels = root.querySelectorAll("[data-" + kind + "-panel]");
    var select = root.querySelector("[data-" + kind + "-select]");
    buttons.forEach(function (btn) {
      var on = btn.getAttribute("data-" + kind + "-tab") === name;
      btn.classList.toggle("is-active", on);
      btn.setAttribute("aria-selected", on ? "true" : "false");
    });
    panels.forEach(function (panel) {
      var on = panel.getAttribute("data-" + kind + "-panel") === name;
      panel.classList.toggle("is-active", on);
      panel.hidden = !on;
    });
    if (select && select.value !== name) {
      select.value = name;
    }
  }

  function bind(root, kind) {
    var buttons = root.querySelectorAll("[data-" + kind + "-tab]");
    var select = root.querySelector("[data-" + kind + "-select]");
    if (!buttons.length && !select) return;

    buttons.forEach(function (btn) {
      btn.addEventListener("click", function () {
        activate(root, btn.getAttribute("data-" + kind + "-tab"), kind);
      });
    });
    if (select) {
      select.addEventListener("change", function () {
        if (select.value) activate(root, select.value, kind);
      });
    }

    var first = select
      ? select.value || (select.options[0] && select.options[0].value)
      : buttons[0] && buttons[0].getAttribute("data-" + kind + "-tab");
    if (first) activate(root, first, kind);
  }

  function bindRoot(root, kinds) {
    kinds.forEach(function (kind) {
      bind(root, kind);
    });
    root.querySelectorAll("[data-tabs]").forEach(function (nested) {
      if (nested === root) return;
      var nestedKinds = (nested.getAttribute("data-tabs") || "")
        .split(",")
        .map(function (k) {
          return k.trim();
        })
        .filter(Boolean);
      nestedKinds.forEach(function (k) {
        bind(nested, k);
      });
    });
  }

  document.querySelectorAll("[data-tabs]").forEach(function (root) {
    if (root.parentElement && root.parentElement.closest("[data-tabs]")) return;
    var kinds = (root.getAttribute("data-tabs") || "")
      .split(",")
      .map(function (k) {
        return k.trim();
      })
      .filter(Boolean);
    if (!kinds.length) return;
    bindRoot(root, kinds);
  });

  // Food pages (legacy attributes)
  document.querySelectorAll("[data-city-tabs]").forEach(function (root) {
    bind(root, "city");
    root.querySelectorAll("[data-area-tabs]").forEach(function (areaRoot) {
      bind(areaRoot, "area");
    });
  });
})();
