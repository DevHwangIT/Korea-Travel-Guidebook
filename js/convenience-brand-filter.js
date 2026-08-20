/**
 * Convenience-store brand + section filter:
 * Brand tabs: 공통 | CU | GS | seven | …
 * Under 공통: secondary tabs 인기제품 | 꿀조합 (data-section).
 * Cards: data-brand="common|cu|gs|seven|emart24", data-section="product|combo".
 * Brand tabs show only that brand (공통 ≠ exclusives). Section tabs apply only when brand=common.
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
    var f = (filter || "common").toLowerCase();
    return b === f;
  }

  function apply(root, filter, section) {
    var brandFilter =
      filter != null
        ? filter
        : root.getAttribute("data-brand-active") || "common";
    brandFilter = String(brandFilter || "common").toLowerCase();

    var sectionFilter =
      section != null
        ? section
        : root.getAttribute("data-section-active") || "product";
    sectionFilter = String(sectionFilter || "product").toLowerCase();

    var list = items(root);
    var visible = 0;
    list.forEach(function (el) {
      var brand = (el.getAttribute("data-brand") || "common").toLowerCase();
      var sec = (el.getAttribute("data-section") || "product").toLowerCase();
      var brandOn = matches(brand, brandFilter);
      // Section split only applies under 공통; brand exclusives show as one list.
      var sectionOn = brandFilter !== "common" || sec === sectionFilter;
      var on = brandOn && sectionOn;
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
      var on = btn.getAttribute("data-brand-tab") === brandFilter;
      btn.classList.toggle("is-active", on);
      btn.setAttribute("aria-selected", on ? "true" : "false");
    });
    root.setAttribute("data-brand-active", brandFilter);

    var sectionUi = root.querySelector("[data-section-filter]");
    if (sectionUi) {
      sectionUi.hidden = brandFilter !== "common";
    }
    root.querySelectorAll("[data-section-tab]").forEach(function (btn) {
      var on = btn.getAttribute("data-section-tab") === sectionFilter;
      btn.classList.toggle("is-active", on);
      btn.setAttribute("aria-selected", on ? "true" : "false");
    });
    root.setAttribute("data-section-active", sectionFilter);

    document.dispatchEvent(
      new CustomEvent("guide:filterchange", {
        bubbles: true,
        detail: { filter: brandFilter, section: sectionFilter },
      })
    );
  }

  function bind(root) {
    if (root.getAttribute("data-brand-bound") === "1") return;
    root.setAttribute("data-brand-bound", "1");

    root.querySelectorAll("[data-brand-tab]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        apply(
          root,
          btn.getAttribute("data-brand-tab") || "common",
          root.getAttribute("data-section-active") || "product"
        );
      });
    });

    root.querySelectorAll("[data-section-tab]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        apply(
          root,
          root.getAttribute("data-brand-active") || "common",
          btn.getAttribute("data-section-tab") || "product"
        );
      });
    });

    var initialBrand =
      root.getAttribute("data-brand-active") ||
      (root.querySelector("[data-brand-tab].is-active") &&
        root
          .querySelector("[data-brand-tab].is-active")
          .getAttribute("data-brand-tab")) ||
      "common";
    var initialSection =
      root.getAttribute("data-section-active") ||
      (root.querySelector("[data-section-tab].is-active") &&
        root
          .querySelector("[data-section-tab].is-active")
          .getAttribute("data-section-tab")) ||
      "product";
    apply(root, initialBrand, initialSection);
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
        apply(
          root,
          root.getAttribute("data-brand-active") || "common",
          root.getAttribute("data-section-active") || "product"
        );
      });
  });
})();
