/**
 * Lightweight SEO helpers for GitHub Pages + client-side i18n.
 * - Absolute canonical / Open Graph / Twitter URLs from SITE_CONFIG
 * - hreflang alternates via ?lang= (see js/i18n.js)
 * - Syncs meta description + og/twitter when language changes
 *
 * Page opts (on <html>):
 *   data-seo-path="pages/before-trip/"   — path under SITE_ORIGIN (preferred)
 *   data-i18n-desc="home.desc"           — i18n key for meta description
 *   data-seo-image="Images/menu/foo.png" — OG image path (relative to site root)
 */
(function () {
  var cfg = window.SITE_CONFIG || {};
  var ORIGIN = String(cfg.SITE_ORIGIN || "").replace(/\/$/, "");
  var SITE_NAME = cfg.SITE_NAME || "Korea Travel Guide";
  var DEFAULT_OG = cfg.DEFAULT_OG_IMAGE || "Images/cover/korea-cover.png";
  var LANGS = Array.isArray(cfg.LANGS) ? cfg.LANGS : ["ko", "en", "ja"];
  var X_DEFAULT = cfg.X_DEFAULT_LANG || "en";

  function ensureMeta(attr, key, content) {
    if (content == null || content === "") return null;
    var sel = 'meta[' + attr + '="' + key + '"]';
    var el = document.head.querySelector(sel);
    if (!el) {
      el = document.createElement("meta");
      el.setAttribute(attr, key);
      document.head.appendChild(el);
    }
    el.setAttribute("content", String(content));
    return el;
  }

  function ensureLink(rel, href, hreflang) {
    var sel =
      'link[rel="' +
      rel +
      '"]' +
      (hreflang ? '[hreflang="' + hreflang + '"]' : ":not([hreflang])");
    var el = document.head.querySelector(sel);
    if (!el) {
      el = document.createElement("link");
      el.setAttribute("rel", rel);
      if (hreflang) el.setAttribute("hreflang", hreflang);
      document.head.appendChild(el);
    }
    el.setAttribute("href", href);
    return el;
  }

  function absUrl(path) {
    if (!path) return ORIGIN + "/";
    if (/^https?:\/\//i.test(path)) return path;
    var clean = String(path)
      .replace(/^\.\//, "")
      .replace(/^\/+/, "")
      .replace(/index\.html$/i, "");
    if (clean && clean.charAt(clean.length - 1) !== "/") clean += "/";
    return ORIGIN + "/" + clean;
  }

  function pagePath() {
    var explicit = document.documentElement.getAttribute("data-seo-path");
    if (explicit != null && explicit !== "") {
      return String(explicit).replace(/^\/+/, "").replace(/index\.html$/i, "");
    }
    try {
      var path = window.location.pathname || "";
      var originPath = "";
      try {
        originPath = new URL(ORIGIN + "/").pathname.replace(/\/$/, "");
      } catch (e1) {
        originPath = "";
      }
      if (originPath && path.indexOf(originPath) === 0) {
        path = path.slice(originPath.length);
      }
      path = path.replace(/^\//, "").replace(/index\.html$/i, "");
      return path;
    } catch (e2) {
      return "";
    }
  }

  function ogImagePath() {
    var fromAttr = document.documentElement.getAttribute("data-seo-image");
    if (fromAttr) return fromAttr.replace(/^\//, "");
    var meta = document.head.querySelector('meta[property="og:image"]');
    var content = meta && meta.getAttribute("content");
    if (content && !/^https?:\/\//i.test(content)) {
      return content.replace(/^\//, "");
    }
    if (content && content.indexOf(ORIGIN) === 0) {
      return content.slice(ORIGIN.length).replace(/^\//, "");
    }
    return DEFAULT_OG;
  }

  function lookupDesc(lang) {
    var key = document.documentElement.getAttribute("data-i18n-desc") || "";
    if (!key) {
      var existing = document.querySelector('meta[name="description"]');
      return existing ? existing.getAttribute("content") || "" : "";
    }
    if (window.GuideI18n && typeof window.GuideI18n.lookupWithFallback === "function") {
      var via = window.GuideI18n.lookupWithFallback(key, lang);
      if (via != null && via !== "") return String(via);
    }
    var dict = null;
    if (window.__I18N_MESSAGES__ && window.__I18N_MESSAGES__[lang]) {
      dict = window.__I18N_MESSAGES__[lang];
    }
    if (!dict) return "";
    return key.split(".").reduce(function (acc, part) {
      if (acc && Object.prototype.hasOwnProperty.call(acc, part)) return acc[part];
      return undefined;
    }, dict);
  }

  function withLang(url, lang) {
    try {
      var u = new URL(url);
      u.searchParams.set("lang", lang);
      return u.toString();
    } catch (e) {
      var join = url.indexOf("?") >= 0 ? "&" : "?";
      return url + join + "lang=" + encodeURIComponent(lang);
    }
  }

  function refresh(lang) {
    if (!ORIGIN) return;
    lang = lang || (window.GuideI18n && window.GuideI18n.getLang
      ? window.GuideI18n.getLang()
      : document.documentElement.lang) || "ko";

    var path = pagePath();
    var canonical = absUrl(path);
    var title = document.title || SITE_NAME;
    var desc = lookupDesc(lang);
    if (!desc) {
      var metaDesc = document.querySelector('meta[name="description"]');
      desc = (metaDesc && metaDesc.getAttribute("content")) || "";
    }
    var imgRel = ogImagePath().replace(/^\/+/, "");
    var image = /^https?:\/\//i.test(imgRel)
      ? imgRel
      : ORIGIN + "/" + imgRel;

    ensureLink("canonical", canonical);

    LANGS.forEach(function (code) {
      ensureLink("alternate", withLang(canonical, code), code);
    });
    ensureLink("alternate", withLang(canonical, X_DEFAULT), "x-default");

    if (desc) ensureMeta("name", "description", desc);

    ensureMeta("property", "og:type", path ? "article" : "website");
    ensureMeta("property", "og:site_name", SITE_NAME);
    ensureMeta(
      "property",
      "og:locale",
      lang === "ja"
        ? "ja_JP"
        : lang === "en"
          ? "en_US"
          : lang === "zh"
            ? "zh_CN"
            : "ko_KR"
    );
    ensureMeta("property", "og:url", withLang(canonical, lang));
    ensureMeta("property", "og:title", title);
    if (desc) ensureMeta("property", "og:description", desc);
    ensureMeta("property", "og:image", image);

    ensureMeta("name", "twitter:card", "summary_large_image");
    ensureMeta("name", "twitter:title", title);
    if (desc) ensureMeta("name", "twitter:description", desc);
    ensureMeta("name", "twitter:image", image);
  }

  window.GuideSeo = { refresh: refresh, absUrl: absUrl, pagePath: pagePath };

  document.addEventListener("guide:langchange", function (e) {
    refresh(e.detail && e.detail.lang);
  });

  function boot() {
    refresh(
      window.GuideI18n && window.GuideI18n.getLang
        ? window.GuideI18n.getLang()
        : undefined
    );
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
