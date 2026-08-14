/**
 * Language switcher — loads local i18n messages and applies to [data-i18n] nodes.
 *
 * Languages are data-driven (GUIDE_LANGS): ko / en / ja / zh (中文).
 * To add another locale later:
 *   1. Add { code, label } to GUIDE_LANGS below
 *   2. Create i18n/{code}.json and add code to i18n/build-bundle.py LANGS
 *   3. Re-run build-bundle — .lang-switch is rendered from GUIDE_LANGS site-wide
 *
 * SEO: ?lang=ko|en|ja|zh is read on load and kept in sync when the user switches
 * language (for hreflang / shareable locale links). Primary storage remains localStorage.
 *
 * First-visit language (no saved preference / no ?lang=):
 *   Match navigator.languages against GUIDE_LANGS (ko/en/ja/zh).
 *   If no match → en (international default), except Korean language/region (ko* / *-KR) → ko.
 *   Saved korea-guide-lang always wins; never override an existing user choice on later loads.
 */
(function () {
  /** @type {{ code: string, label: string }[]} */
  var GUIDE_LANGS = [
    { code: "ko", label: "KR" },
    { code: "en", label: "EN" },
    { code: "ja", label: "JP" },
    { code: "zh", label: "中文" },
  ];

  var SUPPORTED = GUIDE_LANGS.map(function (l) {
    return l.code;
  });
  /** Distinct from welcome popup key (korea-guide-welcome-hide-date). */
  var STORAGE_KEY = "korea-guide-lang";
  var cache = {};
  var welcomeScriptQueued = false;

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

  function langFromQuery() {
    try {
      var q = new URLSearchParams(window.location.search).get("lang");
      if (q) q = String(q).toLowerCase().split("-")[0];
      if (SUPPORTED.indexOf(q) !== -1) return q;
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
    if (!tag) return null;
    var base = tag.split("-")[0];
    for (var i = 0; i < SUPPORTED.length; i++) {
      var code = SUPPORTED[i];
      if (tag === code || tag.indexOf(code + "-") === 0 || base === code) {
        return code;
      }
    }
    return null;
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
    if (SUPPORTED.indexOf(saved) !== -1) return saved;
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

  function lookup(obj, path) {
    return path.split(".").reduce(function (acc, key) {
      if (acc && Object.prototype.hasOwnProperty.call(acc, key)) return acc[key];
      return undefined;
    }, obj);
  }

  /** Rebuild every .lang-switch from GUIDE_LANGS so pages need not hardcode buttons. */
  function renderLangSwitchers(lang) {
    document.querySelectorAll("nav.lang-switch, .lang-switch").forEach(function (nav) {
      if (nav.getAttribute("data-lang-static") === "1") return;
      var html = GUIDE_LANGS.map(function (l) {
        var on = l.code === lang;
        return (
          '<button type="button" data-set-lang="' +
          l.code +
          '"' +
          (on ? ' class="is-active" aria-pressed="true"' : ' aria-pressed="false"') +
          ">" +
          l.label +
          "</button>"
        );
      }).join("");
      nav.innerHTML = html;
      if (!nav.getAttribute("aria-label")) {
        nav.setAttribute("aria-label", "Language");
      }
    });
  }

  function apply(dict, lang) {
    renderLangSwitchers(lang);

    document.querySelectorAll("[data-i18n]").forEach(function (el) {
      var key = el.getAttribute("data-i18n");
      var val = lookup(dict, key);
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

    document.querySelectorAll("[data-i18n-attr]").forEach(function (el) {
      var specs = el.getAttribute("data-i18n-attr").split(",");
      specs.forEach(function (spec) {
        var parts = spec.split(":");
        if (parts.length < 2) return;
        var attr = parts[0].trim();
        var key = parts.slice(1).join(":").trim();
        var val = lookup(dict, key);
        if (val != null) el.setAttribute(attr, String(val));
      });
    });

    var titleKey = document.documentElement.getAttribute("data-i18n-title") || "";
    var pageTitle = titleKey ? lookup(dict, titleKey) : null;
    if (pageTitle) {
      document.title =
        String(pageTitle).indexOf("Korea Travel Guide") !== -1
          ? String(pageTitle)
          : String(pageTitle) + " | Korea Travel Guide";
    }

    document.documentElement.lang = lang;

    document.querySelectorAll("[data-set-lang]").forEach(function (btn) {
      var on = btn.getAttribute("data-set-lang") === lang;
      btn.classList.toggle("is-active", on);
      btn.setAttribute("aria-pressed", on ? "true" : "false");
    });
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

    var url = i18nDir() + lang + ".json";
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
        var banner = document.querySelector("[data-i18n-fallback]");
        if (banner) banner.hidden = false;
      });
  }

  function setLang(lang) {
    if (SUPPORTED.indexOf(lang) === -1) return;
    persistLang(lang);
    syncLangQuery(lang);
    load(lang, { silent: true }).then(function () {
      notifyLang(lang);
    });
  }

  window.GuideI18n = {
    setLang: setLang,
    getLang: getLang,
    load: load,
    detectBrowserLang: detectBrowserLang,
    languages: GUIDE_LANGS.slice(),
    supported: SUPPORTED.slice(),
  };

  document.addEventListener("click", function (e) {
    var btn = e.target.closest("[data-set-lang]");
    if (!btn) return;
    e.preventDefault();
    setLang(btn.getAttribute("data-set-lang"));
  });

  function init() {
    var lang = getLang();
    // Persist discoverable ?lang= for SEO / share links (no-op on file://)
    syncLangQuery(lang);
    renderLangSwitchers(lang);
    load(lang).then(function () {
      ensureWelcomePopupScript();
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
