/**
 * Travel tips — booklet topic index (parents always visible; children under active).
 * Hash deep links: #category[/sub]. Empty hash → first category + first sub.
 */
(function () {
  var root = document.querySelector("[data-tip-map]");
  if (!root) return;

  var nodes = Array.prototype.slice.call(root.querySelectorAll("[data-tip-cat]"));
  var topics = Array.prototype.slice.call(root.querySelectorAll("[data-tip-topic]"));
  var childLists = Array.prototype.slice.call(root.querySelectorAll("[data-tip-children]"));
  var childBtns = Array.prototype.slice.call(root.querySelectorAll("[data-tip-go]"));
  var regions = Array.prototype.slice.call(root.querySelectorAll("[data-tip-region]"));
  var pagePane = root.querySelector("[data-tip-page]");
  var reduceMotionMq = window.matchMedia("(prefers-reduced-motion: reduce)");
  var narrowMq = window.matchMedia("(max-width: 820px)");
  var lastTurnKey = "";

  function reduceMotion() {
    return reduceMotionMq.matches;
  }

  function pulsePageTurn(cat, sub) {
    if (!pagePane || reduceMotion()) return;
    var key = (cat || "") + "/" + (sub || "");
    if (!key || key === "/" || key === lastTurnKey) return;
    lastTurnKey = key;
    pagePane.classList.remove("is-turning");
    // Force reflow so the page-turn animation can restart.
    void pagePane.offsetWidth;
    pagePane.classList.add("is-turning");
  }

  function parseHash() {
    var raw = (window.location.hash || "").replace(/^#/, "").trim();
    if (!raw) return null;
    var parts = raw.split("/").filter(Boolean);
    if (!parts.length) return null;
    return {
      cat: decodeURIComponent(parts[0]).toLowerCase(),
      sub: parts[1] ? decodeURIComponent(parts[1]).toLowerCase() : "",
    };
  }

  function writeHash(cat, sub) {
    if (!cat) {
      if (!window.location.hash) return;
      if (history.replaceState) {
        history.replaceState(null, "", window.location.pathname + window.location.search);
      } else {
        window.location.hash = "";
      }
      return;
    }
    var next = "#" + encodeURIComponent(cat);
    if (sub) next += "/" + encodeURIComponent(sub);
    if (window.location.hash === next) return;
    if (history.replaceState) {
      var url = new URL(window.location.href);
      url.hash = next.slice(1);
      history.replaceState(null, "", url.pathname + url.search + url.hash);
    } else {
      window.location.hash = next;
    }
  }

  function firstCategoryId() {
    var first = nodes[0];
    return first ? first.getAttribute("data-tip-cat") : "";
  }

  function firstSubId(region) {
    var first = region.querySelector("[data-tip-sub]");
    return first ? first.getAttribute("data-tip-sub") : "";
  }

  function setSubOpen(region, subId) {
    var subs = region.querySelectorAll("[data-tip-sub]");
    subs.forEach(function (sub) {
      var on = !!subId && sub.getAttribute("data-tip-sub") === subId;
      sub.classList.toggle("is-open", on);
      sub.hidden = !on;
    });
  }

  function syncChildNav(cat, subId) {
    topics.forEach(function (topic) {
      var on = !!cat && topic.getAttribute("data-tip-topic") === cat;
      topic.classList.toggle("is-active", on);
    });

    childLists.forEach(function (list) {
      var on = !!cat && list.getAttribute("data-tip-children") === cat;
      list.hidden = !on;
      list.setAttribute("aria-hidden", on ? "false" : "true");
    });

    childBtns.forEach(function (btn) {
      var go = (btn.getAttribute("data-tip-go") || "").toLowerCase();
      var parts = go.split("/");
      var btnCat = parts[0] || "";
      var btnSub = parts[1] || "";
      var on = !!cat && !!subId && btnCat === cat && btnSub === subId;
      btn.classList.toggle("is-active", on);
      btn.setAttribute("aria-current", on ? "page" : "false");
    });
  }

  function scrollActiveNodeIntoView(node) {
    if (!node || !narrowMq.matches) return;
    if (typeof node.scrollIntoView !== "function") return;
    node.scrollIntoView({
      behavior: reduceMotion() ? "auto" : "smooth",
      inline: "center",
      block: "nearest",
    });
  }

  function setCategory(cat, sub, opts) {
    opts = opts || {};
    var found = false;
    var activeNode = null;

    nodes.forEach(function (node) {
      var on = !!cat && node.getAttribute("data-tip-cat") === cat;
      node.classList.toggle("is-active", on);
      node.setAttribute("aria-expanded", on ? "true" : "false");
      if (on) {
        found = true;
        activeNode = node;
      }
    });

    var activeSub = "";

    regions.forEach(function (region) {
      var on = !!cat && region.getAttribute("data-tip-region") === cat;
      region.classList.toggle("is-open", on);
      region.hidden = !on;
      if (on) {
        var subId = sub || firstSubId(region);
        if (subId && !region.querySelector('[data-tip-sub="' + subId + '"]')) {
          subId = firstSubId(region);
        }
        activeSub = subId;
        setSubOpen(region, subId);
        if (!opts.skipHash) writeHash(cat, subId);
        if (!opts.skipScroll) {
          requestAnimationFrame(function () {
            scrollActiveNodeIntoView(activeNode);
            if (narrowMq.matches && pagePane && typeof pagePane.scrollIntoView === "function") {
              pagePane.scrollIntoView({
                behavior: reduceMotion() ? "auto" : "smooth",
                block: "nearest",
              });
            }
          });
        }
      } else {
        setSubOpen(region, "");
      }
    });

    syncChildNav(found ? cat : "", activeSub);
    if (found && !opts.skipTurn) pulsePageTurn(cat, activeSub);

    if (!found && !opts.skipHash) writeHash("", "");
  }

  nodes.forEach(function (node) {
    node.addEventListener("click", function () {
      var cat = node.getAttribute("data-tip-cat");
      // Active parent stays open — no collapse / no reset of current tip.
      if (node.classList.contains("is-active")) return;
      setCategory(cat, "");
    });
  });

  root.addEventListener("click", function (e) {
    var btn = e.target.closest("[data-tip-go]");
    if (!btn || !root.contains(btn)) return;
    var go = (btn.getAttribute("data-tip-go") || "").toLowerCase();
    var parts = go.split("/");
    var cat = parts[0] || "";
    var sub = parts[1] || "";
    if (!cat || !sub) return;
    setCategory(cat, sub, { skipScroll: narrowMq.matches ? false : true });
  });

  function applyFromHash() {
    var state = parseHash();
    if (!state || !state.cat) {
      var fallbackCat = firstCategoryId();
      var region = fallbackCat
        ? root.querySelector('[data-tip-region="' + fallbackCat + '"]')
        : null;
      setCategory(fallbackCat, region ? firstSubId(region) : "", {
        skipHash: true,
        skipScroll: true,
        skipTurn: true,
      });
      return;
    }
    var region = root.querySelector('[data-tip-region="' + state.cat + '"]');
    if (!region) {
      var fallback = firstCategoryId();
      var fbRegion = fallback
        ? root.querySelector('[data-tip-region="' + fallback + '"]')
        : null;
      setCategory(fallback, fbRegion ? firstSubId(fbRegion) : "", {
        skipHash: true,
        skipScroll: true,
        skipTurn: true,
      });
      return;
    }
    var sub = state.sub;
    if (sub && !region.querySelector('[data-tip-sub="' + sub + '"]')) {
      sub = firstSubId(region);
    }
    setCategory(state.cat, sub || firstSubId(region), {
      skipHash: true,
      skipScroll: true,
      skipTurn: true,
    });
  }

  applyFromHash();
  window.addEventListener("hashchange", applyFromHash);
})();
