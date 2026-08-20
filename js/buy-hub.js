/**
 * Shopping & Fun hub: choice → shopping | fun views with hash deep links.
 */
(function () {
  var VIEWS = { choice: true, shopping: true, fun: true };
  var root = null;
  var current = "choice";
  var reduceMotion =
    window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function t(key, fallback) {
    try {
      if (window.GuideI18n && typeof window.GuideI18n.t === "function") {
        return window.GuideI18n.t(key, fallback || key);
      }
      if (window.GuideI18n && typeof window.GuideI18n.lookupWithFallback === "function") {
        var via = window.GuideI18n.lookupWithFallback(
          key,
          window.GuideI18n.getLang && window.GuideI18n.getLang()
        );
        if (via != null && via !== "") return String(via);
      }
    } catch (e) {}
    return fallback || key;
  }

  function parseHashView() {
    try {
      var hash = (window.location.hash || "").replace(/^#/, "").toLowerCase();
      if (hash === "shopping" || hash === "shop") return "shopping";
      if (hash === "fun" || hash === "play") return "fun";
    } catch (e) {}
    return "choice";
  }

  function syncHash(view, replace) {
    try {
      if (!window.history) return;
      var url = new URL(window.location.href);
      if (view === "choice") {
        url.hash = "";
      } else {
        url.hash = view;
      }
      var next = url.pathname + url.search + url.hash;
      if (replace && window.history.replaceState) {
        window.history.replaceState(null, "", next);
      } else if (window.history.pushState) {
        window.history.pushState(null, "", next);
      } else {
        window.location.hash = view === "choice" ? "" : view;
      }
    } catch (e) {}
  }

  function replayChoiceCards() {
    if (!root) return;
    var cards = root.querySelectorAll(".buy-choice-card");
    cards.forEach(function (card) {
      card.classList.remove("is-entered", "is-animating");
      void card.offsetWidth;
      if (reduceMotion) {
        card.classList.add("is-entered");
        return;
      }
      card.classList.add("is-animating");
      var done = false;
      function finish() {
        if (done) return;
        done = true;
        card.classList.remove("is-animating");
        card.classList.add("is-entered");
      }
      card.addEventListener(
        "animationend",
        function (ev) {
          if (ev.target === card) finish();
        },
        { once: true }
      );
      window.setTimeout(finish, 900);
    });
  }

  function applyCopy(view) {
    var title = root.querySelector("[data-buy-title]");
    var intro = root.querySelector("[data-buy-intro]");
    var backMain = root.querySelector("[data-buy-back-main]");
    var backChoice = root.querySelector("[data-buy-back-choice]");

    if (view === "shopping") {
      if (title) title.textContent = t("buyHub.shoppingTitle", "쇼핑&기념품");
      if (intro) intro.textContent = t("buyHub.shoppingIntro", "카테고리별로 살 거리를 모아 두었습니다.");
    } else if (view === "fun") {
      if (title) title.textContent = t("buyHub.funTitle", "놀거리");
      if (intro) intro.textContent = t("buyHub.funIntro", "외국인이 즐기기 쉬운 한국식 놀거리입니다.");
    } else {
      if (title) title.textContent = t("buyHub.title", "쇼핑 및 놀거리");
      if (intro) intro.textContent = t("buyHub.intro", "살 것과 함께, 외국인이 많이 즐기는 한국식 놀거리도 모았습니다.");
    }

    if (backMain) backMain.hidden = view !== "choice";
    if (backChoice) backChoice.hidden = view === "choice";
  }

  function setView(view, opts) {
    opts = opts || {};
    if (!VIEWS[view]) view = "choice";
    if (!root) return;

    var prev = current;
    current = view;
    root.setAttribute("data-buy-active", view);

    root.querySelectorAll("[data-buy-view]").forEach(function (section) {
      var name = section.getAttribute("data-buy-view");
      var on = name === view;
      section.hidden = !on;
      section.classList.toggle("is-active", on);
    });

    applyCopy(view);

    if (opts.syncHash !== false && (opts.forceHash || prev !== view)) {
      syncHash(view, !!opts.replaceHash);
    }

    if (view === "choice" && (opts.animateChoice || prev !== "choice")) {
      replayChoiceCards();
    }
  }

  function boot() {
    root = document.querySelector("[data-buy-hub]");
    if (!root) return;

    root.querySelectorAll("[data-buy-goto]").forEach(function (el) {
      el.addEventListener("click", function (ev) {
        var target = el.getAttribute("data-buy-goto");
        if (!VIEWS[target] || target === "choice") return;
        ev.preventDefault();
        setView(target, { syncHash: true });
      });
    });

    var backChoice = root.querySelector("[data-buy-back-choice]");
    if (backChoice) {
      backChoice.addEventListener("click", function () {
        setView("choice", { syncHash: true, animateChoice: true });
      });
    }

    window.addEventListener("hashchange", function () {
      setView(parseHashView(), { syncHash: false, animateChoice: true });
    });

    document.addEventListener("guide:langchange", function () {
      applyCopy(current);
    });

    setView(parseHashView(), {
      syncHash: true,
      replaceHash: true,
      animateChoice: true,
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
