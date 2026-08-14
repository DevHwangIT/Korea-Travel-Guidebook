/**
 * Language switcher — loads local i18n messages and applies to [data-i18n] nodes.
 *
 * Languages are data-driven (GUIDE_LANGS). Labels use each language’s own script.
 * Fallback chain for missing keys: selected → en → ko
 *   (zh-Hant also tries zh before en).
 *
 * To add another locale later:
 *   1. Add { code, label } to GUIDE_LANGS below
 *   2. Create i18n/{code}.json and add code to i18n/build-bundle.py LANGS
 *   3. Re-run build-bundle — .lang-switch is rendered from GUIDE_LANGS site-wide
 *
 * SEO: ?lang= is read on load and kept in sync when the user switches
 * language (for hreflang / shareable locale links). Primary storage remains localStorage.
 *
 * First-visit language (no saved preference / no ?lang=):
 *   Match navigator.languages against GUIDE_LANGS (incl. zh-Hant / vi / th / ru).
 *   If no match → en (international default), except Korean language/region (ko* / *-KR) → ko.
 *   Saved korea-guide-lang always wins; never override an existing user choice on later loads.
 */
(function () {
  /** @type {{ code: string, label: string }[]} */
  var GUIDE_LANGS = [
    { code: "ko", label: "한국어" },
    { code: "en", label: "English" },
    { code: "ja", label: "日本語" },
    { code: "zh", label: "简体中文" },
    { code: "zh-Hant", label: "繁體中文" },
    { code: "vi", label: "Tiếng Việt" },
    { code: "th", label: "ภาษาไทย" },
    { code: "ru", label: "Русский" },
  ];

  var SUPPORTED = GUIDE_LANGS.map(function (l) {
    return l.code;
  });
  /** Distinct from welcome popup key (korea-guide-welcome-hide-date). */
  var STORAGE_KEY = "korea-guide-lang";
  var cache = {};
  var welcomeScriptQueued = false;
  var travelUtilsScriptQueued = false;

  var LANG_ALIASES = {
    "zh-hans": "zh",
    "zh-cn": "zh",
    "zh-sg": "zh",
    "zh-hant": "zh-Hant",
    "zh-tw": "zh-Hant",
    "zh-hk": "zh-Hant",
    "zh-mo": "zh-Hant",
  };

  function scriptDir() {
    var scripts = document.getElementsByTagName("script");
    for (var i = scripts.length - 1; i >= 0; i--) {
      var src = scripts[i].src || "";
      if (src.indexOf("i18n.js") !== -1) {
        return src.replace(/\/[^/]*$/, "/");
      }
    }
    return "./js/";
  }

  function i18nDir() {
    return scriptDir().replace(/\/js\/?$/, "/i18n/");
  }

  function normalizeLangCode(raw) {
    if (!raw) return null;
    var q = String(raw).trim();
    if (!q) return null;
    if (SUPPORTED.indexOf(q) !== -1) return q;
    var lower = q.toLowerCase();
    if (LANG_ALIASES[lower]) return LANG_ALIASES[lower];
    if (SUPPORTED.indexOf(lower) !== -1) return lower;
    // Prefer full tag match for zh-Hant before stripping
    for (var i = 0; i < SUPPORTED.length; i++) {
      var code = SUPPORTED[i];
      if (lower === code.toLowerCase()) return code;
    }
    var base = lower.split("-")[0];
    if (base === "zh") {
      if (/zh-(tw|hk|mo|hant)/.test(lower)) return "zh-Hant";
      return "zh";
    }
    if (SUPPORTED.indexOf(base) !== -1) return base;
    return null;
  }

  function langFromQuery() {
    try {
      var q = new URLSearchParams(window.location.search).get("lang");
      return normalizeLangCode(q);
    } catch (e) {
      /* ignore */
    }
    return null;
  }

  function syncLangQuery(lang) {
    try {
      var url = new URL(window.location.href);
      if (url.searchParams.get("lang") === lang) return;
      url.searchParams.set("lang", lang);
      history.replaceState(null, "", url.pathname + url.search + url.hash);
    } catch (e) {
      /* ignore (file:// etc.) */
    }
  }

  function browserLocaleCandidates() {
    var list = [];
    try {
      if (navigator.languages && navigator.languages.length) {
        for (var i = 0; i < navigator.languages.length; i++) {
          var item = String(navigator.languages[i] || "").toLowerCase();
          if (item) list.push(item);
        }
      }
    } catch (e) {
      /* ignore */
    }
    var primary = String(
      navigator.language || navigator.userLanguage || ""
    ).toLowerCase();
    if (primary) list.push(primary);
    return list;
  }

  function matchSupportedLocale(tag) {
    return normalizeLangCode(tag);
  }

  /**
   * Pick GUIDE_LANGS from browser locale.
   * Unsupported → en; Korean language or Korea region → ko (documented default policy).
   */
  function detectBrowserLang() {
    var candidates = browserLocaleCandidates();
    var i;
    for (i = 0; i < candidates.length; i++) {
      var hit = matchSupportedLocale(candidates[i]);
      if (hit) return hit;
    }
    for (i = 0; i < candidates.length; i++) {
      var tag = candidates[i];
      if (tag === "ko" || tag.indexOf("ko-") === 0 || /-kr$/.test(tag)) {
        return "ko";
      }
    }
    return "en";
  }

  function persistLang(lang) {
    try {
      localStorage.setItem(STORAGE_KEY, lang);
    } catch (e) {
      /* ignore */
    }
  }

  function getLang() {
    var fromQuery = langFromQuery();
    if (fromQuery) {
      persistLang(fromQuery);
      return fromQuery;
    }
    var saved = null;
    try {
      saved = localStorage.getItem(STORAGE_KEY);
    } catch (e2) {
      saved = null;
    }
    var normalizedSaved = normalizeLangCode(saved);
    if (normalizedSaved) return normalizedSaved;
    var detected = detectBrowserLang();
    persistLang(detected);
    return detected;
  }

  /** Sitewide welcome modal — loaded once after i18n so every page gets it. */
  function ensureWelcomePopupScript() {
    if (welcomeScriptQueued) return;
    if (document.querySelector('script[data-guide-welcome="1"]')) {
      welcomeScriptQueued = true;
      return;
    }
    welcomeScriptQueued = true;
    var s = document.createElement("script");
    s.src =
      scriptDir() +
      "welcome-popup.js?v=" +
      encodeURIComponent(window.SITE_ASSET_VERSION || "");
    s.async = true;
    s.setAttribute("data-guide-welcome", "1");
    (document.body || document.documentElement).appendChild(s);
  }

  /** Sitewide floating travel utils (FX / weather / TZ / units) — same inject path. */
  function ensureTravelUtilsScript() {
    if (travelUtilsScriptQueued) return;
    if (document.querySelector('script[data-guide-travel-utils="1"]')) {
      travelUtilsScriptQueued = true;
      return;
    }
    travelUtilsScriptQueued = true;
    var s = document.createElement("script");
    s.src =
      scriptDir() +
      "travel-utils.js?v=" +
      encodeURIComponent(window.SITE_ASSET_VERSION || "");
    s.async = true;
    s.setAttribute("data-guide-travel-utils", "1");
    (document.body || document.documentElement).appendChild(s);
  }

  function lookup(obj, path) {
    return path.split(".").reduce(function (acc, key) {
      if (acc && Object.prototype.hasOwnProperty.call(acc, key)) return acc[key];
      return undefined;
    }, obj);
  }

  /** Fallback chain: selected → (zh for zh-Hant) → en → ko */
  function fallbackLangs(lang) {
    var chain = [lang];
    if (lang === "zh-Hant") chain.push("zh");
    if (lang !== "en") chain.push("en");
    if (lang !== "ko") chain.push("ko");
    var out = [];
    var seen = {};
    for (var i = 0; i < chain.length; i++) {
      var c = chain[i];
      if (!c || seen[c]) continue;
      seen[c] = true;
      out.push(c);
    }
    return out;
  }

  function dictFor(lang) {
    if (cache[lang]) return cache[lang];
    if (window.__I18N_MESSAGES__ && window.__I18N_MESSAGES__[lang]) {
      cache[lang] = window.__I18N_MESSAGES__[lang];
      return cache[lang];
    }
    return null;
  }

  function lookupWithFallback(path, lang) {
    var chain = fallbackLangs(lang);
    for (var i = 0; i < chain.length; i++) {
      var dict = dictFor(chain[i]);
      if (!dict) continue;
      var val = lookup(dict, path);
      if (val != null && val !== "") return val;
    }
    return undefined;
  }

  function labelFor(code) {
    for (var i = 0; i < GUIDE_LANGS.length; i++) {
      if (GUIDE_LANGS[i].code === code) return GUIDE_LANGS[i].label;
    }
    return code;
  }

  function closeLangMenus(exceptNav) {
    document.querySelectorAll("nav.lang-switch, .lang-switch").forEach(function (nav) {
      if (exceptNav && nav === exceptNav) return;
      nav.classList.remove("is-open");
      var toggle = nav.querySelector(".lang-switch__toggle");
      var menu = nav.querySelector(".lang-switch__menu");
      if (toggle) toggle.setAttribute("aria-expanded", "false");
      if (menu) menu.hidden = true;
    });
  }

  /** Rebuild every .lang-switch from GUIDE_LANGS so pages need not hardcode buttons. */
  function renderLangSwitchers(lang) {
    document.querySelectorAll("nav.lang-switch, .lang-switch").forEach(function (nav) {
      if (nav.getAttribute("data-lang-static") === "1") return;
      var prefix =
        lookupWithFallback("common.langMenu", lang) || "Language";
      var currentLabel = labelFor(lang);
      /** Closed toggle: "Language : English", "언어 : 한국어", "言語 : 日本語", … */
      var toggleText = prefix + " : " + currentLabel;
      var options = GUIDE_LANGS.map(function (l) {
        var on = l.code === lang;
        return (
          '<button type="button" role="option" data-set-lang="' +
          l.code +
          '"' +
          (on ? ' class="is-active" aria-selected="true"' : ' aria-selected="false"') +
          ">" +
          l.label +
          "</button>"
        );
      }).join("");
      nav.innerHTML =
        '<button type="button" class="lang-switch__toggle" aria-expanded="false" aria-haspopup="listbox" aria-label="' +
        toggleText +
        '">' +
        '<span class="lang-switch__current">' +
        toggleText +
        "</span>" +
        '<span class="lang-switch__caret" aria-hidden="true">▾</span>' +
        "</button>" +
        '<div class="lang-switch__menu" role="listbox" hidden>' +
        '<p class="lang-switch__heading">' +
        prefix +
        "</p>" +
        options +
        "</div>";
      if (!nav.getAttribute("aria-label")) {
        nav.setAttribute("aria-label", prefix);
      }
    });
  }

  function applyInRoot(root, lang) {
    if (!root || !root.querySelectorAll) return;
    root.querySelectorAll("[data-i18n]").forEach(function (el) {
      var key = el.getAttribute("data-i18n");
      var val = lookupWithFallback(key, lang);
      if (val == null || val === "") {
        if (el.closest(".tip") && key.indexOf(".tip") !== -1) {
          el.closest(".tip").hidden = true;
        }
        return;
      }
      if (el.closest(".tip")) {
        if (!el.closest(".tip").hasAttribute("data-shop-body-hides-tip")) {
          el.closest(".tip").hidden = false;
        }
      }
      if (el.hasAttribute("data-i18n-html")) {
        el.innerHTML = String(val);
      } else {
        el.textContent = String(val);
      }
    });

    root.querySelectorAll("[data-i18n-attr]").forEach(function (el) {
      var specs = el.getAttribute("data-i18n-attr").split(",");
      specs.forEach(function (spec) {
        var parts = spec.split(":");
        if (parts.length < 2) return;
        var attr = parts[0].trim();
        var key = parts.slice(1).join(":").trim();
        var val = lookupWithFallback(key, lang);
        if (val != null) el.setAttribute(attr, String(val));
      });
    });
  }

  function apply(dict, lang) {
    // Keep active dict in cache for fallback lookups across langs
    cache[lang] = dict;
    renderLangSwitchers(lang);
    applyInRoot(document, lang);

    var titleKey = document.documentElement.getAttribute("data-i18n-title") || "";
    var pageTitle = titleKey ? lookupWithFallback(titleKey, lang) : null;
    if (pageTitle) {
      document.title =
        String(pageTitle).indexOf("Korea Travel Guide") !== -1
          ? String(pageTitle)
          : String(pageTitle) + " | Korea Travel Guide";
    }

    document.documentElement.lang = lang === "zh" ? "zh-Hans" : lang;

    document.querySelectorAll("[data-set-lang]").forEach(function (btn) {
      var on = btn.getAttribute("data-set-lang") === lang;
      btn.classList.toggle("is-active", on);
      btn.setAttribute("aria-selected", on ? "true" : "false");
    });
  }

  /** Re-apply current language to document or a late-injected subtree. */
  function reapply(root) {
    var lang = getLang();
    var dict = dictFor(lang) || dictFor("en") || dictFor("ko") || {};
    cache[lang] = dict;
    if (!root || root === document || root === document.documentElement) {
      apply(dict, lang);
      return;
    }
    applyInRoot(root, lang);
  }

  function t(path, fallback) {
    var val = lookupWithFallback(path, getLang());
    if (val != null && val !== "") return String(val);
    return fallback != null ? fallback : path;
  }

  function notifyLang(lang) {
    document.dispatchEvent(
      new CustomEvent("guide:langchange", { detail: { lang: lang } })
    );
  }

  function load(lang, opts) {
    var silent = opts && opts.silent;
    function done(dict) {
      apply(dict, lang);
      if (!silent) notifyLang(lang);
      return dict;
    }

    if (cache[lang]) return Promise.resolve(done(cache[lang]));

    if (window.__I18N_MESSAGES__ && window.__I18N_MESSAGES__[lang]) {
      cache[lang] = window.__I18N_MESSAGES__[lang];
      return Promise.resolve(done(cache[lang]));
    }

    var url = i18nDir() + encodeURIComponent(lang) + ".json";
    return fetch(url)
      .then(function (res) {
        if (!res.ok) throw new Error("HTTP " + res.status);
        return res.json();
      })
      .then(function (dict) {
        cache[lang] = dict;
        return done(dict);
      })
      .catch(function (err) {
        console.warn("[i18n] Failed to load", url, err);
        // Soft-fail: still apply via fallback chain if en/ko already cached/bundled
        var fallback = dictFor("en") || dictFor("ko");
        if (fallback) {
          cache[lang] = fallback;
          return done(fallback);
        }
        var banner = document.querySelector("[data-i18n-fallback]");
        if (banner) banner.hidden = false;
      });
  }

  function setLang(lang) {
    var normalized = normalizeLangCode(lang);
    if (!normalized || SUPPORTED.indexOf(normalized) === -1) return;
    persistLang(normalized);
    syncLangQuery(normalized);
    closeLangMenus();
    load(normalized, { silent: true }).then(function () {
      notifyLang(normalized);
    });
  }

  window.GuideI18n = {
    setLang: setLang,
    getLang: getLang,
    load: load,
    apply: reapply,
    reapply: reapply,
    t: t,
    detectBrowserLang: detectBrowserLang,
    languages: GUIDE_LANGS.slice(),
    supported: SUPPORTED.slice(),
    fallbackLangs: fallbackLangs,
    lookupWithFallback: lookupWithFallback,
  };

  document.addEventListener("click", function (e) {
    var toggle = e.target.closest(".lang-switch__toggle");
    if (toggle) {
      e.preventDefault();
      var nav = toggle.closest(".lang-switch");
      if (!nav) return;
      var open = !nav.classList.contains("is-open");
      closeLangMenus();
      if (open) {
        nav.classList.add("is-open");
        toggle.setAttribute("aria-expanded", "true");
        var menu = nav.querySelector(".lang-switch__menu");
        if (menu) menu.hidden = false;
      }
      return;
    }

    var btn = e.target.closest("[data-set-lang]");
    if (btn) {
      e.preventDefault();
      setLang(btn.getAttribute("data-set-lang"));
      return;
    }

    if (!e.target.closest(".lang-switch")) {
      closeLangMenus();
    }
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeLangMenus();
  });

  function init() {
    var lang = getLang();
    // Persist discoverable ?lang= for SEO / share links (no-op on file://)
    syncLangQuery(lang);
    // Prime all bundled dicts for fallback lookups
    if (window.__I18N_MESSAGES__) {
      Object.keys(window.__I18N_MESSAGES__).forEach(function (code) {
        cache[code] = window.__I18N_MESSAGES__[code];
      });
    }
    renderLangSwitchers(lang);
    load(lang).then(function () {
      ensureWelcomePopupScript();
      ensureTravelUtilsScript();
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
