# -*- coding: utf-8 -*-
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def patch(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"{label}: marker not found in {path}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print("ok", label)


def main() -> None:
    patch(
        ROOT / "js" / "list-pager.js",
        """    document.addEventListener("guide:filterchange", function () {
      state.page = 1;
      render();
    });""",
        """    var keepUrlPage = true;
    document.addEventListener("guide:filterchange", function () {
      if (keepUrlPage) {
        keepUrlPage = false;
      } else {
        state.page = 1;
      }
      render();
    });""",
        "list-pager filterchange",
    )

    tabs = ROOT / "js" / "region-tabs.js"
    t = tabs.read_text(encoding="utf-8")
    marker = """  function bindRoot(root, kinds) {
    if (root.hasAttribute("data-hash-tabs")) {
      bindHashRoot(root, kinds);
      return;
    }
    kinds.forEach(function (kind) {
      bind(root, kind);
    });
"""
    insert = r'''  function bindQueryRoot(root, kinds, paramKey) {
    var catKind = kinds[0];
    if (!catKind || !paramKey) return;
    var wanted = "";
    if (window.GuideUrlState) {
      wanted = String(window.GuideUrlState.get(paramKey) || "").toLowerCase();
    }
    var firstTab = root.querySelector("[data-" + catKind + "-tab]");
    var defaultName = firstTab
      ? firstTab.getAttribute("data-" + catKind + "-tab")
      : "";

    function syncFromUi(name) {
      if (!window.GuideUrlState) return;
      var values = {};
      var defaults = {};
      values[paramKey] = name;
      defaults[paramKey] = defaultName;
      window.GuideUrlState.patch(values, defaults);
    }

    kinds.forEach(function (kind) {
      bind(
        root,
        kind,
        kind === catKind
          ? function (name) {
              syncFromUi(name);
            }
          : null,
        kind === catKind ? wanted : ""
      );
    });
    nestedRoots(root).forEach(function (nested) {
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

  function bindRoot(root, kinds) {
    if (root.hasAttribute("data-hash-tabs")) {
      bindHashRoot(root, kinds);
      return;
    }
    var queryKey = root.getAttribute("data-query-tabs");
    if (queryKey) {
      bindQueryRoot(root, kinds, queryKey);
      return;
    }
    kinds.forEach(function (kind) {
      bind(root, kind);
    });
'''
    if marker not in t:
        raise SystemExit("region-tabs bindRoot marker not found")
    tabs.write_text(t.replace(marker, insert, 1), encoding="utf-8")
    print("ok region-tabs bindQueryRoot")

    brand = ROOT / "js" / "convenience-brand-filter.js"
    b = brand.read_text(encoding="utf-8")
    b = b.replace(
        "  function apply(root, filter, section) {",
        "  function apply(root, filter, section, opts) {\n    opts = opts || {};",
        1,
    )
    old_evt = """    document.dispatchEvent(
      new CustomEvent("guide:filterchange", {
        bubbles: true,
        detail: { filter: brandFilter, section: sectionFilter },
      })
    );
  }"""
    new_evt = """    if (!opts.skipUrl && window.GuideUrlState) {
      window.GuideUrlState.patch(
        { brand: brandFilter, section: sectionFilter },
        { brand: "common", section: "product" }
      );
    }
    if (!opts.silent) {
      document.dispatchEvent(
        new CustomEvent("guide:filterchange", {
          bubbles: true,
          detail: { filter: brandFilter, section: sectionFilter },
        })
      );
    }
  }"""
    if old_evt not in b:
        raise SystemExit("brand filter event marker not found")
    b = b.replace(old_evt, new_evt, 1)
    old_init = """    var initialBrand =
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
  }"""
    new_init = """    var fromBrand = window.GuideUrlState
      ? String(window.GuideUrlState.get("brand") || "").toLowerCase()
      : "";
    var fromSection = window.GuideUrlState
      ? String(window.GuideUrlState.get("section") || "").toLowerCase()
      : "";
    var initialBrand =
      fromBrand ||
      root.getAttribute("data-brand-active") ||
      (root.querySelector("[data-brand-tab].is-active") &&
        root
          .querySelector("[data-brand-tab].is-active")
          .getAttribute("data-brand-tab")) ||
      "common";
    var initialSection =
      fromSection ||
      root.getAttribute("data-section-active") ||
      (root.querySelector("[data-section-tab].is-active") &&
        root
          .querySelector("[data-section-tab].is-active")
          .getAttribute("data-section-tab")) ||
      "product";
    apply(root, initialBrand, initialSection, { silent: true, skipUrl: true });
  }"""
    if old_init not in b:
        raise SystemExit("brand filter init marker not found")
    b = b.replace(old_init, new_init, 1)
    brand.write_text(b, encoding="utf-8")
    print("ok convenience-brand-filter")

    hub = ROOT / "js" / "buy-hub.js"
    h = hub.read_text(encoding="utf-8")
    old_boot = """    setView(parseHashView(), {
      syncHash: true,
      replaceHash: true,
      animateChoice: true,
    });"""
    new_boot = """    var view = parseHashView();
    var tabQ = window.GuideUrlState
      ? String(window.GuideUrlState.get("tab") || "")
      : "";
    if (view === "choice" && tabQ) view = "shopping";
    setView(view, {
      syncHash: true,
      replaceHash: true,
      animateChoice: true,
    });"""
    if old_boot not in h:
        raise SystemExit("buy-hub boot marker not found")
    hub.write_text(h.replace(old_boot, new_boot, 1), encoding="utf-8")
    print("ok buy-hub")

    buy_html = ROOT / "pages" / "buy" / "index.html"
    html = buy_html.read_text(encoding="utf-8")
    html2 = html.replace(
        '<div class="city-tabs" data-tabs="buy">',
        '<div class="city-tabs" data-tabs="buy" data-query-tabs="tab">',
        1,
    )
    if html2 == html:
        raise SystemExit("buy index tabs marker not found")
    buy_html.write_text(html2, encoding="utf-8")
    print("ok buy/index.html")


if __name__ == "__main__":
    main()
