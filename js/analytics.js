/**
 * Google Analytics 4 (gtag).
 *
 * Set the measurement ID in ONE of:
 *   - window.SITE_CONFIG.GA4_MEASUREMENT_ID  (js/site-config.js)
 *   - window.GA4_MEASUREMENT_ID              (inline, before this file)
 *   - FALLBACK_ID below
 *
 * Localhost / file:// are skipped unless window.GA4_DEBUG === true.
 * After deploy, reports appear in GA4 (Realtime in minutes; daily reports next day).
 */
(function () {
  var FALLBACK_ID = "G-38FDJLLF29";

  if (window.__GUIDE_GA4_LOADED__) return;

  var cfg = window.SITE_CONFIG || {};
  var id = String(
    window.GA4_MEASUREMENT_ID || cfg.GA4_MEASUREMENT_ID || FALLBACK_ID || ""
  )
    .trim()
    .toUpperCase();
  if (!/^G-[A-Z0-9]+$/.test(id)) return;

  var host = String(location.hostname || "").toLowerCase();
  var isLocal =
    location.protocol === "file:" ||
    host === "localhost" ||
    host === "127.0.0.1" ||
    host === "::1";
  if (isLocal && window.GA4_DEBUG !== true) return;

  window.__GUIDE_GA4_LOADED__ = true;
  window.dataLayer = window.dataLayer || [];
  function gtag() {
    window.dataLayer.push(arguments);
  }
  window.gtag = gtag;

  if (!document.querySelector('script[src*="googletagmanager.com/gtag/js"]')) {
    var s = document.createElement("script");
    s.async = true;
    s.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(id);
    document.head.appendChild(s);
  }

  function currentLang() {
    try {
      if (window.GuideI18n && typeof window.GuideI18n.getLang === "function") {
        return window.GuideI18n.getLang() || "en";
      }
    } catch (e) {}
    return document.documentElement.lang || "en";
  }

  function contentGroup() {
    var p = String(location.pathname || "/").toLowerCase();
    if (p.indexOf("/pages/") < 0) return "home";
    if (p.indexOf("/before-trip") >= 0 || p.indexOf("/travel-tips") >= 0) return "prep_tips";
    if (p.indexOf("/travel-courses") >= 0) return "courses";
    if (
      p.indexOf("/food") >= 0 ||
      p.indexOf("/convenience-store") >= 0 ||
      p.indexOf("/food-life") >= 0
    ) {
      return "food";
    }
    if (p.indexOf("/buy") >= 0 || p.indexOf("/souvenir") >= 0 || p.indexOf("/fun") >= 0) {
      return "shopping_fun";
    }
    if (p.indexOf("/transport") >= 0) return "places";
    if (p.indexOf("/apps") >= 0) return "apps";
    if (p.indexOf("/festival") >= 0) return "festivals";
    if (p.indexOf("/privacy") >= 0) return "privacy";
    if (p.indexOf("/prep") >= 0) return "prep_info";
    return "other";
  }

  gtag("js", new Date());
  gtag("config", id, {
    anonymize_ip: true,
    send_page_view: true,
    page_path: location.pathname + (location.search || ""),
    page_title: document.title || "",
    language: currentLang(),
    content_group: contentGroup(),
  });
  gtag("set", "user_properties", { guide_lang: currentLang() });

  document.addEventListener("guide:langchange", function (ev) {
    var next = (ev.detail && ev.detail.lang) || currentLang();
    gtag("set", "user_properties", { guide_lang: next });
    gtag("event", "language_change", { language: next });
  });
})();
