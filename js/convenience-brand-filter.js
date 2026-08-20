/**
 * Convenience-store brand filter: 공통 | CU | GS | …
 * Cards use data-brand="common|cu|gs|seven|emart24".
 * Brand tab shows common + that brand's exclusives.
 */
(function () {
  function t(key, fallback) {
    if (window.GuideI18n && typeof GuideI18n.t === "function") {
      return GuideI18n.t(key, fallback);
    }
    return fallback;
  }

  function items(root) {
    var sel = root.getAttribute("data-brand-item") || "a.combo-card";
    return Array.prototype.slice.call(root.querySelectorAll(sel));
  }

  function ensureEmpty(root) {
    var empty = root.querySelector("[data-brand-empty]");
    if (empty) return empty;
    empty = document.createElement("p");
    empty.className = "brand-filter-empty";
    empty.setAttribute("data-brand-empty", "");
    empty.setAttribute("data-i18n", "convenience.brandFilterEmpty");
    empty.textContent = t(
      "convenience.brandFilterEmpty",
      "이 브랜드에 해당하는 항목이 없습니다."
    );
    empty.hidden = true;
    var brandUi = root.querySelector(".brand-filter");
    if (brandUi && brandUi.parentNode) {
      brandUi.parentNode.insertBefore(empty, brandUi.nextSibling);
    } else {
      root.insertBefore(empty, root.firstChild);
    }
    return empty;
  }

  function matches(brand, filter) {
    var b = (brand || "common").toLowerCase();
    if (filter === "common") return b === "common";
    return b === "common" || b === filter;
  }

  function apply(root, filter) {
    var list = items(root);
    var visible = 0;
    list.forEach(function (el) {
      var brand = (el.getAttribute("data-brand") || "common").toLowerCase();
      var on = matches(brand, filter);
      // data-filter-hide integrates with js/list-pager.js
      if (on) {
        el.removeAttribute("data-filter-hide");
        visible += 1;
      } else {
        el.setAttribute("data-filter-hide", "1");
      }
    });
    var empty = ensureEmpty(root);
    empty.hidden = visible !== 0;
    if (!empty.hidden) {
      empty.textContent = t(
        "convenience.brandFilterEmpty",
        "이 브랜드에 해당하는 항목이 없습니다."
      );
    }
    root.querySelectorAll("[data-brand-tab]").forEach(function (btn) {
      var on = btn.getAttribute("data-brand-tab") === filter;
      btn.classList.toggle("is-active", on);
      btn.setAttribute("aria-selected", on ? "true" : "false");
    });
    root.setAttribute("data-brand-active", filter);

    document.dispatchEvent(
      new CustomEvent("guide:filterchange", {
        bubbles: true,
        detail: { filter: filter },
      })
    );
  }

  function bind(root) {
    if (root.getAttribute("data-brand-bound") === "1") return;
    root.setAttribute("data-brand-bound", "1");
    root.querySelectorAll("[data-brand-tab]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        apply(root, btn.getAttribute("data-brand-tab") || "common");
      });
    });
    var initial =
      root.getAttribute("data-brand-active") ||
      (root.querySelector("[data-brand-tab].is-active") &&
        root
          .querySelector("[data-brand-tab].is-active")
          .getAttribute("data-brand-tab")) ||
      "common";
    apply(root, initial);
  }

  function init() {
    document.querySelectorAll("[data-convenience-brand-filter]").forEach(bind);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  document.addEventListener("guide:langchange", function () {
    document
      .querySelectorAll("[data-convenience-brand-filter]")
      .forEach(function (root) {
        apply(root, root.getAttribute("data-brand-active") || "common");
      });
  });
})();
