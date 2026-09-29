/**
 * Home featured partner shops — sticky rail on desktop, in-flow card on mobile.
 * Data: partners/catalog.js + partners/{slug}/info.json
 */
(function () {
  if (window.__GUIDE_PARTNER_RAIL__) return;
  window.__GUIDE_PARTNER_RAIL__ = true;

  var ROTATE_DEFAULT = 8000;
  var LANG_ALIAS = {
    "zh-Hans": "zh",
    "zh-CN": "zh",
    "zh-SG": "zh",
    "zh-TW": "zh-Hant",
    "zh-HK": "zh-Hant",
    "zh-MO": "zh-Hant",
  };
  var SCRIPT_SRC = (document.currentScript && document.currentScript.src) || "";
  var rail = null;
  var shops = [];
  var index = 0;
  var timer = null;
  var touchX = null;
  var activeLang = "";
  var followY = 0;
  var followRaf = 0;
  var refreshTimer = 0;
  var bound = false;

  function normalizeShopLang(code) {
    if (!code) return "";
    code = String(code);
    if (LANG_ALIAS[code]) code = LANG_ALIAS[code];
    if (code === "zh-Hans") code = "zh";
    return code;
  }

  function lang() {
    var code = normalizeShopLang(activeLang);
    if (!code) {
      try {
        if (window.GuideI18n && typeof window.GuideI18n.getLang === "function") {
          code = normalizeShopLang(window.GuideI18n.getLang() || "");
        }
      } catch (e) {}
    }
    if (!code) {
      try {
        var q = new URLSearchParams(location.search || "").get("lang");
        if (q) code = normalizeShopLang(q);
      } catch (e2) {}
    }
    if (!code) code = normalizeShopLang(document.documentElement.lang || "ko");
    return code || "ko";
  }

  function t(key, fallback) {
    try {
      if (window.GuideI18n && typeof window.GuideI18n.lookupWithFallback === "function") {
        var val = window.GuideI18n.lookupWithFallback(key, lang());
        if (val != null && val !== "") return String(val);
      }
    } catch (e) {}
    try {
      if (window.GuideI18n && typeof window.GuideI18n.t === "function") {
        return window.GuideI18n.t(key, fallback);
      }
    } catch (e2) {}
    return fallback;
  }

  function i18nRow(pack, code) {
    if (!pack || !code) return null;
    if (pack[code]) return pack[code];
    var aliased = LANG_ALIAS[code];
    if (aliased && pack[aliased]) return pack[aliased];
    var lower = String(code).toLowerCase();
    var keys = Object.keys(pack);
    for (var i = 0; i < keys.length; i++) {
      if (keys[i].toLowerCase() === lower) return pack[keys[i]];
    }
    return null;
  }

  function loc(shop, key) {
    var pack = (shop && shop.i18n) || {};
    var code = lang();
    var row = i18nRow(pack, code);
    if (!row && code && code.indexOf("-") > 0 && code !== "zh-Hant") {
      row = i18nRow(pack, code.split("-")[0]);
    }
    row = row || pack.en || pack.ko || {};
    if (row[key]) return row[key];
    if (pack.en && pack.en[key]) return pack.en[key];
    if (pack.ko && pack.ko[key]) return pack.ko[key];
    return "";
  }

  function siteRoot() {
    var src = SCRIPT_SRC;
    if (!src) {
      var s = document.querySelector('script[src*="partner-shops.js"]');
      src = (s && s.src) || "";
    }
    if (src) {
      return src.replace(/\/js\/partner-shops\.js(\?.*)?$/i, "/");
    }
    try {
      return new URL("./", document.baseURI || location.href).href;
    } catch (e) {
      return "./";
    }
  }

  function assetVersion() {
    if (window.SITE_ASSET_VERSION) return String(window.SITE_ASSET_VERSION);
    var src = SCRIPT_SRC || "";
    var m = src.match(/[?&]v=([^&]+)/);
    if (m) return decodeURIComponent(m[1]);
    try {
      var i18n = document.querySelector('script[src*="i18n.js"]');
      var fromI18n = i18n && i18n.src && i18n.src.match(/[?&]v=([^&]+)/);
      if (fromI18n) return decodeURIComponent(fromI18n[1]);
    } catch (e) {}
    return "";
  }

  function withVersion(url) {
    var v = assetVersion();
    if (!v) return url;
    return url + (url.indexOf("?") >= 0 ? "&" : "?") + "v=" + encodeURIComponent(v);
  }

  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function shopImage(shop) {
    var file = shop.image || "cover.jpg";
    var folder = shop._folder || "partners/" + shop.id + "/";
    return withVersion(siteRoot() + folder + file);
  }

  function stopTimer() {
    if (timer) {
      window.clearInterval(timer);
      timer = null;
    }
  }

  function startTimer() {
    stopTimer();
    if (shops.length < 2) return;
    if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      return;
    }
    var cat = window.GUIDE_PARTNER_CATALOG || {};
    var ms = Number(cat.rotateMs) || ROTATE_DEFAULT;
    if (ms < 3000) ms = 3000;
    timer = window.setInterval(function () {
      show(index + 1);
    }, ms);
  }

  function show(next) {
    if (!shops.length) return;
    index = ((next % shops.length) + shops.length) % shops.length;
    var shop = shops[index];
    renderCard(shop);
    renderDots();
    trackImpression(shop);
  }

  function renderDots() {
    if (!rail) return;
    var wrap = rail.querySelector("[data-partner-dots]");
    if (!wrap) return;
    var n = shops.length || 1;
    var html = "";
    var i;
    for (i = 0; i < n; i++) {
      var on = i === index;
      html +=
        '<button type="button" class="home-featured__dot' +
        (on ? " is-on" : "") +
        '" data-partner-dot="' +
        i +
        '"' +
        (on ? ' aria-current="true"' : "") +
        (n < 2 ? " disabled" : "") +
        ' aria-label="' +
        escapeHtml(String(i + 1)) +
        '"></button>';
    }
    wrap.innerHTML = html;
    wrap.setAttribute("aria-label", t("home.partnerDots", "제휴 가게"));
  }

  function trackImpression(shop) {
    if (!shop) return;
    try {
      if (window.GuideAnalytics && typeof window.GuideAnalytics.partnerView === "function") {
        var surface = (rail && rail.getAttribute("data-partner-surface")) || "home_featured";
        window.GuideAnalytics.partnerView({
          id: shop.id,
          name: shop.name || loc(shop, "name") || shop.id,
          url: shop.url || "",
          surface: surface,
        });
      }
    } catch (e) {}
  }

  function ico(kind) {
    var svg =
      {
        en:
          '<path fill="none" stroke="currentColor" stroke-width="1.8" d="M4 18.5V8.5c0-1 .8-1.8 1.8-1.8h8.4c1 0 1.8.8 1.8 1.8v6.2c0 1-.8 1.8-1.8 1.8H8.2L4 18.5z"/><path fill="none" stroke="currentColor" stroke-width="1.8" d="M14.5 11.6h3.7c.9 0 1.6.7 1.6 1.6v4.2L18 16.2h-3"/>',
        meal:
          '<path fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" d="M8 4v7m0 0c0 2-1.4 3-2.8 3M8 11c0 2 1.4 3 2.8 3M8 11v9M16.5 4v16M15 5c1.2 2 1.5 3.5 1.5 5M18 5c-1.2 2-1.5 3.5-1.5 5"/>',
        hours:
          '<circle cx="12" cy="12" r="8" fill="none" stroke="currentColor" stroke-width="1.8"/><path fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" d="M12 8v4.5L15 14"/>',
        book:
          '<rect x="4" y="6" width="16" height="14" rx="2" fill="none" stroke="currentColor" stroke-width="1.8"/><path fill="none" stroke="currentColor" stroke-width="1.8" d="M8 4v4M16 4v4M4 11h16"/>',
        sns:
          '<rect x="6" y="6" width="12" height="12" rx="3.2" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="12" cy="12" r="3" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="16.2" cy="7.8" r="0.9" fill="currentColor"/>',
      }[kind] || "";
    return (
      '<span class="home-featured__ico" aria-hidden="true"><svg viewBox="0 0 24 24" width="16" height="16">' +
      svg +
      "</svg></span>"
    );
  }

  function factRow(kind, labelKey, fallbackLabel, value, href) {
    if (!value) return "";
    var valHtml = href
      ? '<a class="home-featured__fact-a" href="' +
        escapeHtml(href) +
        '" target="_blank" rel="noopener noreferrer">' +
        escapeHtml(value) +
        "</a>"
      : escapeHtml(value);
    return (
      '<li class="home-featured__fact">' +
      ico(kind) +
      '<div><span class="home-featured__fact-k" data-i18n="' +
      labelKey +
      '">' +
      escapeHtml(t(labelKey, fallbackLabel)) +
      '</span><span class="home-featured__fact-v">' +
      valHtml +
      "</span></div></li>"
    );
  }

  function instagramHandle(shop) {
    var raw = (shop && (shop.instagramHandle || shop.instagram)) || loc(shop, "instagram") || "";
    raw = String(raw).trim();
    if (!raw) {
      var href = (shop && shop.instagramUrl) || "";
      if (/instagram\.com/i.test(href)) raw = href;
    }
    if (!raw) return "";
    if (/^https?:\/\//i.test(raw)) {
      try {
        var path = new URL(raw).pathname.replace(/\/+$/, "");
        var parts = path.split("/").filter(Boolean);
        raw = parts[parts.length - 1] || "";
      } catch (e) {
        raw = raw.replace(/^https?:\/\/(www\.)?instagram\.com\//i, "").replace(/\/.*$/, "");
      }
    }
    raw = String(raw).replace(/^@/, "").replace(/\/+$/, "");
    return raw ? "@" + raw : "";
  }

  function instagramHref(shop) {
    var raw = (shop && (shop.instagramUrl || shop.instagram)) || loc(shop, "instagram") || "";
    raw = String(raw).trim();
    if (!raw) return "";
    if (/^https?:\/\//i.test(raw)) return raw;
    raw = raw.replace(/^@/, "").replace(/^(www\.)?instagram\.com\//i, "");
    return "https://www.instagram.com/" + raw.replace(/\/+$/, "") + "/";
  }

  function genreKey(shop) {
    var code = String((shop && shop.genre) || "restaurant").toLowerCase();
    if (code === "cafe" || code === "café") return "home.partnerGenreCafe";
    if (code === "shop" || code === "store") return "home.partnerGenreShop";
    return "home.partnerGenreRestaurant";
  }

  function genreLabel(shop) {
    var fromLoc = loc(shop, "genreLabel");
    if (fromLoc) return fromLoc;
    var fallbacks = {
      "home.partnerGenreRestaurant": "음식점",
      "home.partnerGenreCafe": "카페",
      "home.partnerGenreShop": "상점",
    };
    var key = genreKey(shop);
    return t(key, fallbacks[key] || "음식점");
  }

  function renderCard(shop) {
    if (!rail) return;
    var card = rail.querySelector("[data-partner-card]");
    if (!card) return;
    var name = shop.name || loc(shop, "name") || shop.id;
    var tagline = loc(shop, "tagline");
    var area = loc(shop, "area");
    var about = loc(shop, "about") || loc(shop, "summary");
    if (!about) {
      about = [loc(shop, "concept"), loc(shop, "signature"), loc(shop, "exhibition")]
        .filter(Boolean)
        .join(" ");
    }
    var booking = loc(shop, "booking");
    var lunch = loc(shop, "lunch") || shop.lunch;
    var dinner = loc(shop, "dinner") || shop.dinner;
    var hours = loc(shop, "hours") || shop.hours;
    var englishLabel = loc(shop, "englishLabel");
    var url = shop.url || "#";
    var img = shopImage(shop);

    var facts = "";
    if (shop.english === true || englishLabel) {
      facts += factRow(
        "en",
        "home.partnerLang",
        "Language",
        englishLabel || t("home.partnerEnglish", "English Available")
      );
    }
    if (lunch) facts += factRow("meal", "home.partnerLunch", "Lunch", lunch);
    if (dinner) facts += factRow("meal", "home.partnerDinner", "Dinner", dinner);
    if (hours) facts += factRow("hours", "home.partnerHours", "Hours", hours);
    var ig = instagramHref(shop);
    if (ig) {
      facts += factRow("sns", "home.partnerSns", "SNS", instagramHandle(shop), ig);
    }
    if (booking && (!url || url === "#")) {
      facts += factRow("book", "home.partnerBooking", "Booking", booking);
    }

    card.innerHTML =
      '<div class="home-featured__photo">' +
      '<img src="' +
      escapeHtml(img) +
      '" alt="' +
      escapeHtml(name) +
      '" width="640" height="400" decoding="async">' +
      (area
        ? '<span class="home-featured__badge" data-partner-area>' + escapeHtml(area) + "</span>"
        : "") +
      "</div>" +
      '<div class="home-featured__body">' +
      '<a class="home-featured__name" data-partner-cta data-partner-cta-slot="name" data-partner-id="' +
      escapeHtml(shop.id) +
      '" data-partner-name="' +
      escapeHtml(name) +
      '" href="' +
      escapeHtml(url) +
      '" target="_blank" rel="noopener noreferrer">' +
      escapeHtml(name) +
      '<span aria-hidden="true"> ›</span></a>' +
      (tagline ? '<p class="home-featured__tagline">' + escapeHtml(tagline) + "</p>" : "") +
      (about ? '<p class="home-featured__about">' + escapeHtml(about) + "</p>" : "") +
      (facts ? '<ul class="home-featured__meta">' + facts + "</ul>" : "") +
      '<a class="home-featured__cta" data-partner-cta data-partner-cta-slot="reserve" data-partner-id="' +
      escapeHtml(shop.id) +
      '" data-partner-name="' +
      escapeHtml(name) +
      '" href="' +
      escapeHtml(url) +
      '" target="_blank" rel="noopener noreferrer">' +
      '<span data-i18n="home.partnerViewDetails">' +
      escapeHtml(t("home.partnerViewDetails", "예약하기")) +
      "</span>" +
      ' <span aria-hidden="true">›</span></a>' +
      "</div>";
    var imgEl = card.querySelector("img");
    if (imgEl) {
      imgEl.addEventListener("load", kickFollow);
    }
    var genreEl = rail.querySelector("[data-partner-genre]");
    if (genreEl) genreEl.textContent = genreLabel(shop);
    kickFollow();
  }

  function desktopFollow() {
    return window.matchMedia && window.matchMedia("(min-width: 1080px)").matches;
  }

  function followStep() {
    followRaf = 0;
    if (!rail) return;
    var reduced =
      window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (!desktopFollow()) {
      followY = 0;
      rail.style.transform = "";
      rail.classList.remove("home-featured--sticky");
      return;
    }
    if (reduced) {
      followY = 0;
      rail.style.transform = "";
      rail.classList.add("home-featured--sticky");
      return;
    }
    rail.classList.remove("home-featured--sticky");
    var parent = rail.closest(".home-layout") || rail.parentElement;
    if (!parent) return;
    var parentRect = parent.getBoundingClientRect();
    var railH = rail.offsetHeight;
    var gap = 88;
    var max = Math.max(0, parent.offsetHeight - railH);
    var target = Math.min(max, Math.max(0, gap - parentRect.top));
    followY += (target - followY) * 0.18;
    if (Math.abs(target - followY) < 0.4) followY = target;
    rail.style.transform = "translate3d(0," + followY.toFixed(2) + "px,0)";
    if (Math.abs(target - followY) >= 0.4) {
      followRaf = window.requestAnimationFrame(followStep);
    }
  }

  function kickFollow() {
    if (!followRaf) followRaf = window.requestAnimationFrame(followStep);
  }

  function bindFollow() {
    window.addEventListener("scroll", kickFollow, { passive: true });
    window.addEventListener("resize", function () {
      if (!desktopFollow()) {
        followY = 0;
        if (rail) rail.style.transform = "";
      }
      kickFollow();
    });
    kickFollow();
  }

  function bind(el) {
    rail = el;
    var nextBtn = el.querySelector("[data-partner-next]");
    if (nextBtn) {
      nextBtn.addEventListener("click", function () {
        if (shops.length < 2) return;
        show(index + 1);
        startTimer();
      });
    }
    el.addEventListener("click", function (ev) {
      var dot = ev.target && ev.target.closest && ev.target.closest("[data-partner-dot]");
      if (!dot || shops.length < 2) return;
      var i = Number(dot.getAttribute("data-partner-dot"));
      if (isNaN(i)) return;
      show(i);
      startTimer();
    });
    el.addEventListener("mouseenter", stopTimer);
    el.addEventListener("mouseleave", startTimer);
    el.addEventListener("focusin", stopTimer);
    el.addEventListener("focusout", function () {
      if (!el.contains(document.activeElement)) startTimer();
    });
    el.addEventListener(
      "touchstart",
      function (ev) {
        if (ev.changedTouches && ev.changedTouches[0]) {
          touchX = ev.changedTouches[0].clientX;
        }
      },
      { passive: true }
    );
    el.addEventListener(
      "touchend",
      function (ev) {
        if (touchX == null || !ev.changedTouches || !ev.changedTouches[0]) return;
        var dx = ev.changedTouches[0].clientX - touchX;
        touchX = null;
        if (Math.abs(dx) < 48) return;
        show(index + (dx < 0 ? 1 : -1));
        startTimer();
      },
      { passive: true }
    );
    bindFollow();
  }

  function loadScript(src) {
    return new Promise(function (resolve, reject) {
      if (window.GUIDE_PARTNER_CATALOG && window.GUIDE_PARTNER_CATALOG.shops) {
        resolve();
        return;
      }
      var s = document.createElement("script");
      s.src = withVersion(src);
      s.onload = function () {
        resolve();
      };
      s.onerror = function () {
        reject(new Error("catalog"));
      };
      document.head.appendChild(s);
    });
  }

  function decorateShop(id, data) {
    var copy = {};
    var key;
    for (key in data) {
      if (Object.prototype.hasOwnProperty.call(data, key)) copy[key] = data[key];
    }
    copy.id = copy.id || id;
    copy._folder = "partners/" + id + "/";
    return copy;
  }

  function loadShop(id) {
    var folder = "partners/" + id + "/";
    var cat = window.GUIDE_PARTNER_CATALOG || {};
    if (cat.records && cat.records[id]) {
      return Promise.resolve(decorateShop(id, cat.records[id]));
    }
    var href = siteRoot() + folder + "info.json";
    return fetch(withVersion(href), { cache: "no-store" })
      .then(function (res) {
        if (!res.ok) throw new Error("info " + id);
        return res.json();
      })
      .then(function (data) {
        return decorateShop(id, data);
      });
  }

  function syncNextButton() {
    if (!rail) return;
    var nextBtn = rail.querySelector("[data-partner-next]");
    if (!nextBtn) return;
    var many = shops.length > 1;
    nextBtn.hidden = !many;
    nextBtn.disabled = !many;
  }

  function loadAll() {
    if (!rail) return;
    var ready = Promise.resolve();
    if (!(window.GUIDE_PARTNER_CATALOG && window.GUIDE_PARTNER_CATALOG.shops)) {
      ready = loadScript(siteRoot() + "partners/catalog.js");
    }
    ready
      .then(function () {
        var cat = window.GUIDE_PARTNER_CATALOG || {};
        var ids = cat.shops || [];
        if (!ids.length) return [];
        return Promise.all(ids.map(loadShop));
      })
      .then(function (list) {
        shops = (list || []).filter(Boolean);
        syncNextButton();
        if (!shops.length) return;
        show(index);
        startTimer();
        kickFollow();
      })
      .catch(function () {
        /* keep static HTML fallback */
      });
  }

  function boot() {
    var el = document.querySelector("[data-partner-rail]");
    if (!el) return;
    if (!bound) {
      bind(el);
      bound = true;
    }
    loadAll();
  }

  function refreshCard() {
    if (!rail || !shops.length) return;
    renderCard(shops[index]);
    renderDots();
    kickFollow();
  }

  function scheduleRefresh() {
    refreshCard();
    if (refreshTimer) window.clearTimeout(refreshTimer);
    refreshTimer = window.setTimeout(function () {
      refreshTimer = 0;
      refreshCard();
    }, 50);
  }

  function onLangChange(ev) {
    var next = "";
    if (ev && ev.detail && ev.detail.lang) next = ev.detail.lang;
    if (next) activeLang = normalizeShopLang(next);
    if (!shops.length) loadAll();
    else scheduleRefresh();
  }

  document.addEventListener("guide:langchange", onLangChange);
  document.addEventListener(
    "click",
    function (e) {
      var btn = e.target && e.target.closest && e.target.closest("[data-set-lang]");
      if (!btn) return;
      var code = btn.getAttribute("data-set-lang") || "";
      if (code) activeLang = normalizeShopLang(code);
      if (!shops.length) loadAll();
      else scheduleRefresh();
    },
    true
  );

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
