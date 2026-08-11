/**
 * Live search + chip/select filters for admin list pages.
 */
(function () {
  function boot() {
    document.querySelectorAll("[data-list-filters]").forEach(initFilters);
  }

  function initFilters(root) {
    if (root._listFilterReady) return;
    root._listFilterReady = true;

    var input = root.querySelector("[data-list-search]");
    var empty = root.querySelector("[data-list-empty]");
    var chips = root.querySelector("[data-filter-chips]");
    var select = root.querySelector("[data-filter-select]");
    var scope =
      root.closest(".content") ||
      root.parentElement ||
      document;
    var items = Array.prototype.slice.call(scope.querySelectorAll("[data-filter-item]"));
    var activeGroup = "";

    function apply() {
      var q = ((input && input.value) || "").trim().toLowerCase();
      var visible = 0;
      items.forEach(function (el) {
        var hay = (el.getAttribute("data-filter-text") || el.textContent || "")
          .toLowerCase();
        var group = el.getAttribute("data-filter-group") || "";
        var matchQ = !q || hay.indexOf(q) !== -1;
        var matchG = !activeGroup || group === activeGroup;
        var show = matchQ && matchG;
        el.hidden = !show;
        if (show) visible += 1;
      });
      if (empty) empty.hidden = visible !== 0 || items.length === 0;
    }

    if (input) {
      input.addEventListener("input", apply);
    }

    if (select) {
      select.addEventListener("change", function () {
        activeGroup = select.value || "";
        apply();
      });
    }

    if (chips) {
      chips.addEventListener("click", function (e) {
        var btn = e.target.closest("[data-filter-chip]");
        if (!btn || !chips.contains(btn)) return;
        if (btn.tagName === "A") return; // navigation chips (meals/desserts)
        e.preventDefault();
        var group = btn.getAttribute("data-filter-chip") || "";
        if (group === activeGroup) group = "";
        activeGroup = group;
        Array.prototype.forEach.call(
          chips.querySelectorAll("[data-filter-chip]"),
          function (b) {
            if (b.tagName === "A") return;
            b.classList.toggle(
              "is-active",
              (b.getAttribute("data-filter-chip") || "") === activeGroup
            );
          }
        );
        var allBtn = chips.querySelector('[data-filter-chip=""]');
        if (allBtn && allBtn.tagName !== "A") {
          allBtn.classList.toggle("is-active", !activeGroup);
        }
        apply();
      });
    }

    apply();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
