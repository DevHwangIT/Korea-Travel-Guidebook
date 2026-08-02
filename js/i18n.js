/**
 * Language switcher — loads local i18n messages and applies to [data-i18n] nodes.
 */
(function () {
  var SUPPORTED = ["ko", "en", "ja"];
  var STORAGE_KEY = "korea-guide-lang";
  var cache = {};

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

  function getLang() {
    var saved = localStorage.getItem(STORAGE_KEY);
    if (SUPPORTED.indexOf(saved) !== -1) return saved;
    var nav = (navigator.language || "ko").toLowerCase();
    if (nav.indexOf("ja") === 0) return "ja";
    if (nav.indexOf("en") === 0) return "en";
    return "ko";
  }

  function lookup(obj, path) {
    return path.split(".").reduce(function (acc, key) {
      if (acc && Object.prototype.hasOwnProperty.call(acc, key)) return acc[key];
      return undefined;
    }, obj);
  }

  function apply(dict, lang) {
    document.querySelectorAll("[data-i18n]").forEach(function (el) {
      var key = el.getAttribute("data-i18n");
      var val = lookup(dict, key);
      if (val == null || val === "") {
        if (el.closest(".tip") && key.indexOf(".tip") !== -1) {
          el.closest(".tip").hidden = true;
        }
        return;
      }
      if (el.closest(".tip")) el.closest(".tip").hidden = false;
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

    document.documentElement.lang = lang === "ja" ? "ja" : lang === "en" ? "en" : "ko";

    document.querySelectorAll("[data-set-lang]").forEach(function (btn) {
      var on = btn.getAttribute("data-set-lang") === lang;
      btn.classList.toggle("is-active", on);
      btn.setAttribute("aria-pressed", on ? "true" : "false");
    });
  }

  function load(lang) {
    function done(dict) {
      apply(dict, lang);
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
    localStorage.setItem(STORAGE_KEY, lang);
    load(lang).then(function () {
      document.dispatchEvent(new CustomEvent("guide:langchange", { detail: { lang: lang } }));
    });
  }

  window.GuideI18n = {
    setLang: setLang,
    getLang: getLang,
    load: load,
  };

  document.addEventListener("click", function (e) {
    var btn = e.target.closest("[data-set-lang]");
    if (!btn) return;
    e.preventDefault();
    setLang(btn.getAttribute("data-set-lang"));
  });

  function init() {
    load(getLang());
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
