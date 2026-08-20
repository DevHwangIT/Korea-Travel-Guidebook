/**
 * Region filter tabs on meal/dessert dish pages.
 * Tabs: 전체 | 수도권 | 강원권 | 충청권 | 전라권 | 경상권 | 제주권
 * Cards use data-region-group="sudo|gangwon|chungcheong|jeolla|gyeongsang|jeju".
 */
(function () {
  var GROUPS = [
    "all",
    "sudo",
    "gangwon",
    "chungcheong",
    "jeolla",
    "gyeongsang",
    "jeju",
  ];

  function t(key, fallback) {
    if (window.GuideI18n && typeof GuideI18n.t === "function") {
      return GuideI18n.t(key, fallback);
    }
    return fallback;
  }

  /** Scope that contains both tabs and .card-grid (tabs may be a sibling wrapper). */
  function scopeOf(root) {
    if (root.querySelector(".card-grid")) return root;
    var parent = root.parentElement;
    if (parent && parent.querySelector(".card-grid")) return parent;
    return root;
  }

  function findGrid(root) {
    var scope = scopeOf(root);
    return scope.querySelector(".card-grid");
  }

  function cards(root) {
    var grid = findGrid(root);
    if (!grid) return [];
    return Array.prototype.slice.call(
      grid.querySelectorAll(":scope > article.card[data-region-group]")
    );
  }

  function ensureEmpty(root) {
    var scope = scopeOf(root);
    var empty = scope.querySelector("[data-region-empty]");
    if (empty) return empty;
    empty = document.createElement("p");
    empty.className = "region-filter-empty";
    empty.setAttribute("data-region-empty", "");
    empty.setAttribute("data-i18n", "common.regionFilterEmpty");
    empty.textContent = t(
      "common.regionFilterEmpty",
      "이 권역에 등록된 가게가 없습니다."
    );
    empty.hidden = true;
    var grid = findGrid(root);
    if (grid && grid.parentNode) {
      grid.parentNode.insertBefore(empty, grid.nextSibling);
    } else {
      scope.appendChild(empty);
    }
    return empty;
  }

  function apply(root, group) {
    var list = cards(root);
    var visible = 0;
    list.forEach(function (card) {
      var g = card.getAttribute("data-region-group") || "";
      var on = group === "all" || g === group;
      card.hidden = !on;
      if (on) visible += 1;
    });
    var empty = ensureEmpty(root);
    var hasCards = list.length > 0;
    empty.hidden = !(hasCards && visible === 0);
    if (!empty.hidden) {
      empty.textContent = t(
        "common.regionFilterEmpty",
        "이 권역에 등록된 가게가 없습니다."
      );
    }
    root.querySelectorAll("[data-region-tab]").forEach(function (btn) {
      var on = btn.getAttribute("data-region-tab") === group;
      btn.classList.toggle("is-active", on);
      btn.setAttribute("aria-selected", on ? "true" : "false");
    });
    root.setAttribute("data-region-active", group);
  }

  function bind(root) {
    if (root.getAttribute("data-region-bound") === "1") return;
    root.setAttribute("data-region-bound", "1");
    root.querySelectorAll("[data-region-tab]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        apply(root, btn.getAttribute("data-region-tab") || "all");
      });
    });
    var initial =
      root.getAttribute("data-region-active") ||
      (root.querySelector("[data-region-tab].is-active") &&
        root
          .querySelector("[data-region-tab].is-active")
          .getAttribute("data-region-tab")) ||
      "all";
    if (GROUPS.indexOf(initial) < 0) initial = "all";
    apply(root, initial);
  }

  function init() {
    document.querySelectorAll("[data-dish-region-filter]").forEach(bind);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  document.addEventListener("guide:langchange", function () {
    document.querySelectorAll("[data-dish-region-filter]").forEach(function (root) {
      var g = root.getAttribute("data-region-active") || "all";
      apply(root, g);
    });
  });
})();
