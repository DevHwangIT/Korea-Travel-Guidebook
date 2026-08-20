/**
 * Shared pagination + name search for food / convenience card grids.
 *
 * Mark a grid: <div class="card-grid" data-list-pager>
 * Optional: data-page-size="8" (default 8)
 * Optional: data-item="article.card" | "a.combo-card" (auto-detected)
 *
 * Injects pager + search below the grid. Filters by visible title text
 * (current i18n language), then paginates the filtered set.
 */
(function () {
  var DEFAULT_PAGE_SIZE = 8;

  function t(key, fallback) {
    if (window.GuideI18n && typeof GuideI18n.t === "function") {
      return GuideI18n.t(key, fallback);
    }
    return fallback;
  }

  function detectItems(grid) {
    var custom = grid.getAttribute("data-item");
    if (custom) {
      return Array.prototype.slice.call(grid.querySelectorAll(custom));
    }
    var cards = grid.querySelectorAll(":scope > article.card, :scope > a.combo-card");
    if (cards.length) return Array.prototype.slice.call(cards);
    return Array.prototype.slice.call(grid.children).filter(function (el) {
      return el.nodeType === 1;
    });
  }

  function itemTitle(el) {
    var title =
      el.querySelector("h2 [data-i18n], h3[data-i18n], h2, h3") ||
      el.querySelector("[data-i18n]");
    var text = title ? title.textContent : el.textContent;
    return String(text || "")
      .replace(/\s+/g, " ")
      .trim()
      .toLowerCase();
  }

  function pageWindow(current, total, maxButtons) {
    if (total <= maxButtons) {
      var all = [];
      for (var i = 1; i <= total; i++) all.push(i);
      return all;
    }
    var half = Math.floor(maxButtons / 2);
    var start = Math.max(1, current - half);
    var end = Math.min(total, start + maxButtons - 1);
    start = Math.max(1, end - maxButtons + 1);
    var pages = [];
    for (var p = start; p <= end; p++) pages.push(p);
    return pages;
  }

  function createControls(grid) {
    var wrap = document.createElement("div");
    wrap.className = "list-pager-controls";
    wrap.setAttribute("data-list-pager-controls", "");

    var empty = document.createElement("p");
    empty.className = "list-empty";
    empty.setAttribute("data-list-empty", "");
    empty.setAttribute("data-i18n", "common.listNoResults");
    empty.textContent = t("common.listNoResults", "No results.");
    empty.hidden = true;

    var nav = document.createElement("nav");
    nav.className = "list-pager";
    nav.setAttribute("data-list-pager-nav", "");
    nav.setAttribute("aria-label", t("common.listPagerLabel", "Page"));

    var prev = document.createElement("button");
    prev.type = "button";
    prev.className = "list-pager__btn";
    prev.setAttribute("data-pager-prev", "");
    prev.setAttribute("data-i18n", "common.listPrev");
    prev.textContent = t("common.listPrev", "Previous");

    var pages = document.createElement("div");
    pages.className = "list-pager__pages";
    pages.setAttribute("data-pager-pages", "");

    var next = document.createElement("button");
    next.type = "button";
    next.className = "list-pager__btn";
    next.setAttribute("data-pager-next", "");
    next.setAttribute("data-i18n", "common.listNext");
    next.textContent = t("common.listNext", "Next");

    nav.appendChild(prev);
    nav.appendChild(pages);
    nav.appendChild(next);

    var search = document.createElement("div");
    search.className = "list-search";
    search.setAttribute("data-list-search", "");

    var label = document.createElement("label");
    label.className = "list-search__label";

    var labelText = document.createElement("span");
    labelText.className = "list-search__text";
    labelText.setAttribute("data-i18n", "common.listSearch");
    labelText.textContent = t("common.listSearch", "Search");

    var input = document.createElement("input");
    input.type = "search";
    input.className = "list-search__input";
    input.setAttribute("data-pager-query", "");
    input.setAttribute("data-i18n-attr", "placeholder:common.listSearchPlaceholder");
    input.setAttribute(
      "placeholder",
      t("common.listSearchPlaceholder", "Search by name")
    );
    input.setAttribute("autocomplete", "off");
    input.setAttribute("enterkeyhint", "search");

    label.appendChild(labelText);
    label.appendChild(input);
    search.appendChild(label);

    wrap.appendChild(nav);
    wrap.appendChild(search);
    wrap.appendChild(empty);
    grid.insertAdjacentElement("afterend", wrap);

    if (window.GuideI18n && typeof GuideI18n.apply === "function") {
      GuideI18n.apply(wrap);
    }

    return {
      wrap: wrap,
      nav: nav,
      prev: prev,
      next: next,
      pages: pages,
      input: input,
      empty: empty,
    };
  }

  function bind(grid) {
    if (grid.getAttribute("data-list-pager-bound") === "1") return;
    grid.setAttribute("data-list-pager-bound", "1");

    var pageSize = parseInt(grid.getAttribute("data-page-size") || "", 10);
    if (!pageSize || pageSize < 1) pageSize = DEFAULT_PAGE_SIZE;

    var items = detectItems(grid);
    if (!items.length) return;

    var ui = createControls(grid);
    var state = { page: 1, query: "" };

    function filtered() {
      var q = state.query;
      return items.filter(function (el) {
        if (el.getAttribute("data-filter-hide") === "1") return false;
        if (!q) return true;
        return itemTitle(el).indexOf(q) !== -1;
      });
    }

    function render() {
      var match = filtered();
      var totalPages = Math.max(1, Math.ceil(match.length / pageSize));
      if (state.page > totalPages) state.page = totalPages;
      if (state.page < 1) state.page = 1;

      var start = (state.page - 1) * pageSize;
      var end = start + pageSize;

      items.forEach(function (el) {
        el.hidden = true;
        el.setAttribute("aria-hidden", "true");
      });

      match.forEach(function (el, idx) {
        var onPage = idx >= start && idx < end;
        el.hidden = !onPage;
        el.setAttribute("aria-hidden", onPage ? "false" : "true");
      });

      var noResults = match.length === 0;
      ui.empty.hidden = !noResults;
      grid.hidden = noResults;

      // Nested section grids (e.g. convenience products + combos): hide empty blocks.
      grid.querySelectorAll(".combo-grid, .card-grid").forEach(function (nested) {
        var nestedItems = Array.prototype.slice.call(nested.children).filter(function (el) {
          return el.nodeType === 1 && items.indexOf(el) !== -1;
        });
        if (!nestedItems.length) return;
        var anyVisible = nestedItems.some(function (el) {
          return !el.hidden;
        });
        nested.hidden = !anyVisible;
        var prev = nested.previousElementSibling;
        while (prev && (prev.classList.contains("tabs-help") || prev.tagName === "P")) {
          prev.hidden = !anyVisible;
          prev = prev.previousElementSibling;
        }
        if (prev && prev.classList.contains("section-heading")) {
          prev.hidden = !anyVisible;
        }
      });

      var showPager = !noResults && match.length > pageSize;
      ui.nav.hidden = !showPager;
      ui.prev.disabled = state.page <= 1;
      ui.next.disabled = state.page >= totalPages;

      ui.pages.innerHTML = "";
      if (showPager) {
        var maxButtons = window.matchMedia("(max-width: 640px)").matches ? 3 : 5;
        pageWindow(state.page, totalPages, maxButtons).forEach(function (num) {
          var btn = document.createElement("button");
          btn.type = "button";
          btn.className =
            "list-pager__page" + (num === state.page ? " is-active" : "");
          btn.textContent = String(num);
          btn.setAttribute("aria-label", t("common.listPage", "Page") + " " + num);
          if (num === state.page) btn.setAttribute("aria-current", "page");
          btn.addEventListener("click", function () {
            state.page = num;
            render();
            grid.scrollIntoView({ behavior: "smooth", block: "start" });
          });
          ui.pages.appendChild(btn);
        });
      }
    }

    ui.prev.addEventListener("click", function () {
      if (state.page <= 1) return;
      state.page -= 1;
      render();
      grid.scrollIntoView({ behavior: "smooth", block: "start" });
    });

    ui.next.addEventListener("click", function () {
      state.page += 1;
      render();
      grid.scrollIntoView({ behavior: "smooth", block: "start" });
    });

    var debounce;
    ui.input.addEventListener("input", function () {
      var value = String(ui.input.value || "")
        .replace(/\s+/g, " ")
        .trim()
        .toLowerCase();
      window.clearTimeout(debounce);
      debounce = window.setTimeout(function () {
        state.query = value;
        state.page = 1;
        render();
      }, 120);
    });

    document.addEventListener("guide:langchange", function () {
      render();
    });

    document.addEventListener("guide:filterchange", function () {
      state.page = 1;
      render();
    });

    render();
  }

  function init() {
    document.querySelectorAll("[data-list-pager]").forEach(bind);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
