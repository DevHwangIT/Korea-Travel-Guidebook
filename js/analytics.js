/**
 * Google Analytics 4 — events aimed at “what visitors do / what they want”.
 *
 * Demand (what they look for)
 *   click_section     home/hub: food, places, courses, shopping, fun, prep…
 *   click_food        a dish or convenience item
 *   click_restaurant  a recommended shop
 *   click_course      a day-course chip
 *   click_place       a sightseeing pin
 *   click_shopping    a souvenir card
 *   click_fun         a fun-activity card
 *   click_app         an app page or store button
 *   click_festival    a festival poster or VisitKorea index
 *   select_region     food/course/map region tab
 *   select_category   shopping tab or convenience brand
 *   select_topic      prep/tips booklet category
 *   select_language   language switch
 *   search            list search (GA4 recommended; param search_term)
 *   quiz_start / quiz_complete   food or course preference quiz
 *
 * Outcome (they want to act on it)
 *   click_external_map  open Naver/Kakao/Google Maps
 *   share_page          share or copy this page
 *   click_tool          travel-tools FAB (FX / weather / …)
 *   click_contact       email or LINE
 *   click_partner       partner card outbound (name or reserve)
 *   generate_lead       partner 「예약하기」 only — mark as a GA4 conversion
 *   view_promotion      partner card impression (CTR = lead / view per item_id)
 *
 * Partner marketing (per shop, even after more partners are added)
 *   item_id             partner slug (mooaa, …)
 *   partner_cta         reserve | name
 *   timezone, local_hour, hour_band, country_hint
 *   Country/city still come from GA4 geo (IP). Register custom dimensions:
 *   item_id, partner_cta, timezone, country_hint, local_hour, hour_band,
 *   browser_language, device_hint.
 *
 * Quality
 *   scroll_75   read most of a long page
 *   engage_60   stayed 60s
 *
 * Localhost is skipped unless window.GA4_DEBUG === true.
 */
(function () {
  var FALLBACK_ID = "G-38FDJLLF29";
  var SHARE_LABELS = {
    ko: "공유",
    en: "Share",
    ja: "共有",
    zh: "分享",
    "zh-Hant": "分享",
    vi: "Chia sẻ",
    th: "แชร์",
    ru: "Поделиться",
  };
  var HOME_SECTION = {
    "before-trip": "prep_tips",
    prep: "prep_info",
    transportation: "places",
    "food-life": "food",
    buy: "shopping_fun",
    festivals: "festivals",
    "travel-courses": "courses",
    apps: "apps",
  };

  if (window.__GUIDE_ANALYTICS_BOUND__) return;
  window.__GUIDE_ANALYTICS_BOUND__ = true;
  if (/(?:^|[?&])ga4_debug=1(?:&|$)/.test(String(location.search || ""))) {
    window.GA4_DEBUG = true;
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
    if (p.indexOf("/before-trip") >= 0 || p.indexOf("/travel-tips") >= 0) {
      return "prep_tips";
    }
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
    if (p.indexOf("/emergency") >= 0) return "emergency";
    if (p.indexOf("/privacy") >= 0) return "privacy";
    if (p.indexOf("/prep") >= 0) return "prep_info";
    return "other";
  }

  function pathKey(pathname) {
    return (
      String(pathname || "/")
        .toLowerCase()
        .replace(/\/index\.html$/i, "/")
        .replace(/\/+$/, "/") || "/"
    );
  }

  function pathSegs(pathname) {
    return pathKey(pathname).split("/").filter(Boolean);
  }

  function lastSlug(pathname) {
    var segs = pathSegs(pathname);
    return segs.length ? segs[segs.length - 1] : "";
  }

  function resolveUrl(href) {
    try {
      return new URL(href, location.href);
    } catch (e) {
      return null;
    }
  }

  var TZ_COUNTRY = {
    "Asia/Seoul": "KR",
    "Asia/Tokyo": "JP",
    "Asia/Osaka": "JP",
    "Asia/Shanghai": "CN",
    "Asia/Chongqing": "CN",
    "Asia/Harbin": "CN",
    "Asia/Urumqi": "CN",
    "Asia/Taipei": "TW",
    "Asia/Hong_Kong": "HK",
    "Asia/Macau": "MO",
    "Asia/Singapore": "SG",
    "Asia/Bangkok": "TH",
    "Asia/Ho_Chi_Minh": "VN",
    "Asia/Saigon": "VN",
    "Asia/Manila": "PH",
    "Asia/Jakarta": "ID",
    "Asia/Kuala_Lumpur": "MY",
    "Asia/Dubai": "AE",
    "Asia/Kolkata": "IN",
    "Asia/Calcutta": "IN",
    "Australia/Sydney": "AU",
    "Australia/Melbourne": "AU",
    "Australia/Brisbane": "AU",
    "Australia/Perth": "AU",
    "Pacific/Auckland": "NZ",
    "America/New_York": "US",
    "America/Chicago": "US",
    "America/Denver": "US",
    "America/Los_Angeles": "US",
    "America/Phoenix": "US",
    "America/Anchorage": "US",
    "Pacific/Honolulu": "US",
    "America/Toronto": "CA",
    "America/Vancouver": "CA",
    "America/Sao_Paulo": "BR",
    "America/Mexico_City": "MX",
    "Europe/London": "GB",
    "Europe/Paris": "FR",
    "Europe/Berlin": "DE",
    "Europe/Rome": "IT",
    "Europe/Madrid": "ES",
    "Europe/Amsterdam": "NL",
    "Europe/Moscow": "RU",
  };
  var DOW = ["sun", "mon", "tue", "wed", "thu", "fri", "sat"];

  function localeRegion() {
    try {
      if (typeof Intl !== "undefined" && Intl.Locale) {
        var loc = new Intl.Locale(navigator.language || navigator.userLanguage || "");
        if (typeof loc.maximize === "function") loc = loc.maximize();
        if (loc.region) return String(loc.region).toUpperCase();
      }
    } catch (e) {}
    var m = String(navigator.language || navigator.userLanguage || "").match(
      /[-_]([A-Za-z]{2})$/
    );
    return m ? m[1].toUpperCase() : "";
  }

  function hourBand(hour) {
    if (hour < 6) return "night";
    if (hour < 12) return "morning";
    if (hour < 18) return "afternoon";
    return "evening";
  }

  function deviceHint() {
    var w = window.innerWidth || 0;
    if (w && w <= 768) return "mobile";
    if (w && w <= 1080) return "tablet";
    if (window.matchMedia && window.matchMedia("(pointer: coarse)").matches && w <= 900) {
      return "mobile";
    }
    return "desktop";
  }

  function visitContext() {
    var now = new Date();
    var tz = "";
    try {
      tz = Intl.DateTimeFormat().resolvedOptions().timeZone || "";
    } catch (e) {}
    var hour = now.getHours();
    var qs = { utm_source: "", utm_medium: "", utm_campaign: "" };
    try {
      var search = new URLSearchParams(location.search || "");
      qs.utm_source = search.get("utm_source") || "";
      qs.utm_medium = search.get("utm_medium") || "";
      qs.utm_campaign = search.get("utm_campaign") || "";
    } catch (e2) {}
    var refHost = "";
    try {
      if (document.referrer) refHost = new URL(document.referrer).hostname;
    } catch (e3) {}
    var region = localeRegion();
    var tzCountry = TZ_COUNTRY[tz] || "";
    return {
      timezone: tz,
      tz_offset: -now.getTimezoneOffset(),
      local_hour: hour,
      local_dow: DOW[now.getDay()] || String(now.getDay()),
      hour_band: hourBand(hour),
      browser_language: String(navigator.language || navigator.userLanguage || "").slice(0, 20),
      country_hint: region || tzCountry || "",
      device_hint: deviceHint(),
      utm_source: qs.utm_source || "",
      utm_medium: qs.utm_medium || "",
      utm_campaign: qs.utm_campaign || "",
      referrer_host: String(refHost || "").slice(0, 80),
    };
  }

  function partnerSurface(el) {
    if (el && el.closest) {
      var rail = el.closest("[data-partner-surface], [data-partner-rail]");
      if (rail) {
        return rail.getAttribute("data-partner-surface") || "home_featured";
      }
    }
    return "home_featured";
  }

  function partnerPayload(el, extra) {
    extra = extra || {};
    var id =
      (el && el.getAttribute && el.getAttribute("data-partner-id")) || extra.id || "";
    var name =
      (el && el.getAttribute && el.getAttribute("data-partner-name")) || extra.name || id;
    var href =
      (el && (el.getAttribute("href") || el.href)) || extra.url || "";
    var slot =
      (el && el.getAttribute && el.getAttribute("data-partner-cta-slot")) || extra.slot || "";
    var host = "";
    try {
      if (href) host = new URL(href, location.href).hostname.replace(/^www\./, "");
    } catch (e) {}
    var ctx = visitContext();
    var surface = extra.surface || partnerSurface(el);
    var payload = {
      item_id: id,
      item_name: String(name || "").replace(/\s+/g, " ").trim().slice(0, 80),
      item_category: "partner_shop",
      item_list_id: surface,
      partner_cta: slot,
      link_url: String(href || "").slice(0, 200),
      link_domain: host,
      timezone: ctx.timezone,
      local_hour: ctx.local_hour,
      local_dow: ctx.local_dow,
      hour_band: ctx.hour_band,
      browser_language: ctx.browser_language,
      country_hint: ctx.country_hint,
      device_hint: ctx.device_hint,
      utm_source: ctx.utm_source,
      utm_medium: ctx.utm_medium,
      utm_campaign: ctx.utm_campaign,
      referrer_host: ctx.referrer_host,
    };
    return payload;
  }

  function promotionFields(payload, slot) {
    return {
      creative_slot: slot,
      promotion_id: payload.item_id,
      promotion_name: payload.item_name,
      items: [
        {
          item_id: payload.item_id,
          item_name: payload.item_name,
          item_category: "partner_shop",
          item_list_id: payload.item_list_id,
          item_list_name: "partner_shops",
        },
      ],
    };
  }

  function mergePayload(a, b) {
    var out = {};
    [a, b].forEach(function (src) {
      Object.keys(src || {}).forEach(function (key) {
        if (src[key] != null && src[key] !== "") out[key] = src[key];
      });
    });
    return out;
  }

  function trackPartnerView(detail) {
    var payload = partnerPayload(null, detail || {});
    track("view_promotion", mergePayload(payload, promotionFields(payload, "card")));
  }

  function trackPartnerClick(el) {
    var payload = partnerPayload(el, {});
    track("click_partner", payload);
    track(
      "select_promotion",
      mergePayload(payload, promotionFields(payload, payload.partner_cta || "cta"))
    );
    if (payload.partner_cta === "reserve") {
      track("generate_lead", {
        item_id: payload.item_id,
        item_name: payload.item_name,
        item_list_id: payload.item_list_id,
        currency: "KRW",
        lead_type: "partner_reserve",
        timezone: payload.timezone,
        country_hint: payload.country_hint,
        local_hour: payload.local_hour,
        local_dow: payload.local_dow,
        hour_band: payload.hour_band,
        device_hint: payload.device_hint,
        browser_language: payload.browser_language,
        link_domain: payload.link_domain,
      });
    }
  }

  function mapProvider(href) {
    var h = String(href || "").toLowerCase();
    if (/kakao\.com|kko\.to|map\.kakao/.test(h)) return "kakao";
    if (/naver\.com|naver\.me|map\.naver/.test(h)) return "naver";
    if (/google\.com\/maps|maps\.google|maps\.app\.goo\.gl|goo\.gl\/maps/.test(h)) {
      return "google";
    }
    return "other";
  }

  function isExternalMap(href) {
    var h = String(href || "").toLowerCase();
    if (!/^https?:/.test(h)) return false;
    return (
      /kakao\.com|kko\.to|map\.kakao/.test(h) ||
      /naver\.me|map\.naver\.com|naver\.com\/(maps|place)/.test(h) ||
      /google\.com\/maps|maps\.google|maps\.app\.goo\.gl|goo\.gl\/maps/.test(h)
    );
  }

  function isAppStore(href) {
    var h = String(href || "").toLowerCase();
    if (/play\.google\.com/.test(h)) return "android";
    if (/apps\.apple\.com|itunes\.apple\.com/.test(h)) return "ios";
    return "";
  }

  function textLabel(el) {
    if (!el) return "";
    var node =
      el.querySelector("h2, h3, .menu-item__title, .souvenir-card-body h3, [data-i18n]") ||
      el;
    return String(node.textContent || "")
      .replace(/\s+/g, " ")
      .trim()
      .slice(0, 80);
  }

  function classifyInternal(pathname) {
    var segs = pathSegs(pathname);
    var i = segs.indexOf("pages");
    var rest = i >= 0 ? segs.slice(i + 1) : segs;
    var a = rest[0] || "";
    var b = rest[1] || "";
    var c = rest[2] || "";
    var d = rest[3] || "";

    if (a === "food-life") {
      return { event: "click_section", item_id: "food", item_category: "food" };
    }
    if (a === "foods" && (b === "meals" || b === "desserts")) {
      if (d) {
        return {
          event: "click_restaurant",
          item_id: d,
          dish_id: c,
          item_category: b,
        };
      }
      if (c) {
        return { event: "click_food", item_id: c, item_category: b };
      }
      return { event: "click_section", item_id: b, item_category: "food" };
    }
    if (a === "convenience-store") {
      if (b) {
        return { event: "click_food", item_id: b, item_category: "convenience" };
      }
      return {
        event: "click_section",
        item_id: "convenience",
        item_category: "food",
      };
    }
    if (a === "travel-courses") {
      return { event: "click_section", item_id: "courses", item_category: "courses" };
    }
    if (a === "transportation" || a === "transport") {
      if (b === "places" && c) {
        return { event: "click_place", item_id: c, item_category: "places" };
      }
      return { event: "click_section", item_id: "places", item_category: "places" };
    }
    if (a === "buy") {
      return {
        event: "click_section",
        item_id: "shopping_fun",
        item_category: "shopping_fun",
      };
    }
    if (a === "souvenir") {
      if (b) {
        return { event: "click_shopping", item_id: b, item_category: "souvenir" };
      }
      return { event: "click_section", item_id: "shopping", item_category: "shopping" };
    }
    if (a === "fun") {
      if (b) {
        return { event: "click_fun", item_id: b, item_category: "fun" };
      }
      return { event: "click_section", item_id: "fun", item_category: "fun" };
    }
    if (a === "apps") {
      if (b) {
        return { event: "click_app", item_id: b, item_category: "apps" };
      }
      return { event: "click_section", item_id: "apps", item_category: "apps" };
    }
    if (a === "festivals") {
      return {
        event: "click_section",
        item_id: b || "festivals",
        item_category: "festivals",
      };
    }
    if (a === "before-trip" || a === "travel-tips") {
      return {
        event: "click_section",
        item_id: c || b || a,
        item_category: "prep_tips",
      };
    }
    if (a === "prep") {
      return {
        event: "click_section",
        item_id: b || "prep",
        item_category: "prep_info",
      };
    }
    if (a === "useful-korean") {
      return {
        event: "click_section",
        item_id: "useful_korean",
        item_category: "prep_info",
      };
    }
    if (a === "emergency") {
      return {
        event: "click_section",
        item_id: b || "emergency",
        item_category: "emergency",
      };
    }
    if (a === "airport-to-myeongdong") {
      return {
        event: "click_section",
        item_id: "airport_transfer",
        item_category: "prep_tips",
      };
    }
    if (a === "shopping") {
      if (b) {
        return { event: "click_shopping", item_id: b, item_category: "shopping" };
      }
      return {
        event: "click_section",
        item_id: "shopping_fun",
        item_category: "shopping_fun",
      };
    }
    return null;
  }

  function linkSource(a) {
    if (a.closest(".menu-grid")) return "home_menu";
    if (a.closest(".food-life-card")) return "food_hub";
    if (a.closest(".food-quiz-cta") || a.closest("[data-food-quiz]")) return "quiz";
    if (a.closest(".buy-choice-card")) return "buy_choice";
    if (a.closest(".souvenir-card")) return "souvenir";
    if (a.closest(".buy-fun-card")) return "fun";
    if (a.closest("article.card")) return "card";
    if (a.closest(".combo-card")) return "convenience";
    if (a.closest(".app-card") || a.closest(".store-btn")) return "apps";
    if (a.closest(".prep-card")) return "prep_hub";
    if (a.closest(".festivals-poster") || a.closest(".festivals-official")) {
      return "festival";
    }
    return "link";
  }

  function track(name, params) {
    var payload = {
      page_path: location.pathname + (location.search || ""),
      page_title: document.title || "",
      content_group: contentGroup(),
      language: currentLang(),
    };
    if (params) {
      Object.keys(params).forEach(function (key) {
        if (params[key] != null && params[key] !== "") payload[key] = params[key];
      });
    }
    if (window.GA4_DEBUG === true) {
      try {
        console.log("[guide-analytics]", name, payload);
      } catch (e) {}
    }
    try {
      recentEvents.push({ event: name, params: payload });
      if (recentEvents.length > 12) recentEvents.shift();
    } catch (e2) {}
    if (typeof window.gtag === "function") {
      window.gtag("event", name, payload);
    }
  }

  var recentEvents = [];

  window.GuideAnalytics = {
    event: track,
    contentGroup: contentGroup,
    partnerView: trackPartnerView,
    partnerClick: trackPartnerClick,
    recent: recentEvents,
  };

  var cfg = window.SITE_CONFIG || {};
  var id = String(
    window.GA4_MEASUREMENT_ID || cfg.GA4_MEASUREMENT_ID || FALLBACK_ID || ""
  )
    .trim()
    .toUpperCase();
  var host = String(location.hostname || "").toLowerCase();
  var isLocal =
    location.protocol === "file:" ||
    host === "localhost" ||
    host === "127.0.0.1" ||
    host === "::1";
  var sendTag = /^G-[A-Z0-9]+$/.test(id) && (!isLocal || window.GA4_DEBUG === true);

  if (sendTag && !window.__GUIDE_GA4_LOADED__) {
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

    gtag("js", new Date());
    gtag("config", id, {
      anonymize_ip: true,
      send_page_view: true,
      page_path: location.pathname + (location.search || ""),
      page_title: document.title || "",
      language: currentLang(),
      content_group: contentGroup(),
    });
    var tzProp = visitContext().timezone || "";
    gtag("set", "user_properties", tzProp
      ? { guide_lang: currentLang(), visitor_tz: tzProp }
      : { guide_lang: currentLang() });
  }

  var langReady = false;
  document.addEventListener("guide:langchange", function (ev) {
    var next = (ev.detail && ev.detail.lang) || currentLang();
    if (typeof window.gtag === "function") {
      window.gtag("set", "user_properties", { guide_lang: next });
    }
    if (!langReady) {
      langReady = true;
      return;
    }
    track("select_language", { language: next });
  });

  document.addEventListener("guide:placeclick", function (ev) {
    var d = (ev && ev.detail) || {};
    track("click_place", {
      item_id: d.slug || "",
      item_name: d.slug || "",
      item_category: d.kind || "place",
    });
  });

  document.addEventListener("guide:festivalclick", function (ev) {
    var d = (ev && ev.detail) || {};
    track("click_festival", {
      item_id: d.id || "",
      item_name: d.name || "",
      item_category: "festivals",
      source: "poster",
    });
  });

  /* Capture: prep map marks the parent active before bubble reaches document. */
  document.addEventListener(
    "click",
    function (ev) {
      var t = ev.target;
      if (!t || !t.closest) return;
      var topicBtn = t.closest(
        "[data-tip-go], [data-tip-cat], [data-prep-go], [data-prep-cat]"
      );
      if (!topicBtn) return;
      var isParent =
        topicBtn.hasAttribute("data-tip-cat") || topicBtn.hasAttribute("data-prep-cat");
      if (isParent && topicBtn.classList.contains("is-active")) return;
      var topic = "";
      var subtopic = "";
      var go =
        topicBtn.getAttribute("data-tip-go") ||
        topicBtn.getAttribute("data-prep-go") ||
        "";
      if (go) {
        var topicParts = go.toLowerCase().split("/");
        topic = topicParts[0] || "";
        subtopic = topicParts[1] || "";
      } else {
        topic =
          topicBtn.getAttribute("data-tip-cat") ||
          topicBtn.getAttribute("data-prep-cat") ||
          "";
      }
      track("select_topic", {
        topic: topic,
        subtopic: subtopic,
        context:
          topicBtn.hasAttribute("data-prep-cat") ||
          topicBtn.hasAttribute("data-prep-go")
            ? "prep"
            : "prep_tips",
      });
    },
    true
  );

  document.addEventListener("click", function (ev) {
    var t = ev.target;
    if (!t || !t.closest) return;

    var partnerCta = t.closest("[data-partner-cta]");
    if (partnerCta) {
      trackPartnerClick(partnerCta);
      return;
    }

    var regionBtn =
      t.closest("[data-region-tab]") ||
      t.closest("[data-courseRegion-tab]") ||
      t.closest("[data-places-region]");
    if (regionBtn) {
      var region =
        regionBtn.getAttribute("data-region-tab") ||
        regionBtn.getAttribute("data-courseRegion-tab") ||
        regionBtn.getAttribute("data-places-region") ||
        "";
      var context = regionBtn.hasAttribute("data-courseRegion-tab")
        ? "course"
        : regionBtn.hasAttribute("data-places-region")
          ? "places"
          : "food";
      track("select_region", { region: region, context: context });
      return;
    }

    var catBtn =
      t.closest("[data-buy-tab]") ||
      t.closest("[data-brand-tab]") ||
      t.closest("[data-section-tab]");
    if (catBtn) {
      var category =
        catBtn.getAttribute("data-buy-tab") ||
        catBtn.getAttribute("data-brand-tab") ||
        catBtn.getAttribute("data-section-tab") ||
        "";
      var catContext = catBtn.hasAttribute("data-buy-tab")
        ? "shopping"
        : catBtn.hasAttribute("data-section-tab")
          ? "convenience_section"
          : "convenience_brand";
      track("select_category", { category: category, context: catContext });
      return;
    }

    var lineBlock = t.closest(".contact-qr");
    if (lineBlock) {
      track("click_contact", { method: "line" });
      return;
    }

    var buyGoto = t.closest("[data-buy-goto]");
    if (buyGoto) {
      var dest = buyGoto.getAttribute("data-buy-goto") || "";
      track("click_section", {
        item_id: dest,
        item_category: dest === "fun" ? "fun" : "shopping",
        source: "buy_choice",
        item_name: textLabel(buyGoto),
      });
      return;
    }

    var courseChip = t.closest("[data-seoul-course]");
    if (courseChip) {
      var courseId = courseChip.getAttribute("data-seoul-course") || "";
      var curated = courseChip.closest("[data-region-curated], [data-seoul-curated]");
      track("click_course", {
        item_id: courseId,
        item_name: textLabel(courseChip) || courseId,
        region:
          (curated &&
            (curated.getAttribute("data-region-curated") ||
              curated.getAttribute("data-seoul-curated"))) ||
          "",
      });
      return;
    }

    var toolBtn = t.closest("[data-tu-tool], [data-tu-toggle]");
    if (toolBtn) {
      track("click_tool", {
        item_id: toolBtn.getAttribute("data-tu-tool") || "open",
      });
      return;
    }

    var shareBtn = t.closest("[data-share-page]");
    if (shareBtn) {
      ev.preventDefault();
      sharePage(shareBtn);
      return;
    }

    var a = t.closest("a[href]");
    if (!a) return;
    if (a.closest(".back-link") || a.classList.contains("site-brand")) return;

    var href = a.getAttribute("href") || "";
    if (!href || href === "#" || href.indexOf("javascript:") === 0) return;
    var url = resolveUrl(a.href);
    if (!url) return;

    if (/^tel:/i.test(href)) {
      track("click_phone", { item_id: href.replace(/^tel:/i, "") });
      return;
    }

    if (/^mailto:/i.test(href)) {
      track("click_contact", { method: "email" });
      return;
    }

    var store = isAppStore(url.href);
    if (store) {
      track("click_app", {
        item_id: lastSlug(location.pathname) || "store",
        item_category: "store",
        method: store,
        source: "store",
      });
      return;
    }

    var festEl = a.closest(".festivals-poster, .festivals-official__chip");
    if (festEl) {
      track("click_festival", {
        item_id:
          festEl.getAttribute("data-festival-id") ||
          url.hostname.replace(/^www\./, ""),
        item_name: textLabel(festEl),
        item_category: "festivals",
        source: festEl.classList.contains("festivals-poster")
          ? "poster"
          : "official_index",
      });
      return;
    }

    if (
      a.hasAttribute("data-shop-place-link") ||
      a.hasAttribute("data-shop-photos-link") ||
      a.hasAttribute("data-places-panel-address") ||
      isExternalMap(url.href)
    ) {
      if (
        isExternalMap(url.href) ||
        a.hasAttribute("data-shop-place-link") ||
        a.hasAttribute("data-shop-photos-link")
      ) {
        var shop = document.querySelector("[data-shop-detail][data-shop-slug]");
        track("click_external_map", {
          map_provider: mapProvider(url.href),
          item_id:
            (shop && shop.getAttribute("data-shop-slug")) || lastSlug(url.pathname),
          item_name: textLabel(document.querySelector("h1")) || "",
        });
        return;
      }
    }

    if (url.origin !== location.origin) return;

    var info = classifyInternal(url.pathname);
    if (!info) return;
    var source = linkSource(a);
    var label = textLabel(a) || info.item_id;
    var payload = {
      item_id: info.item_id,
      item_name: label,
      item_category: info.item_category || "",
      source: source,
    };
    if (info.dish_id) payload.dish_id = info.dish_id;
    if (source === "home_menu") {
      var segs = pathSegs(url.pathname);
      var idx = segs.indexOf("pages");
      var hub = segs[idx >= 0 ? idx + 1 : 0] || "";
      payload.item_id = HOME_SECTION[hub] || info.item_id;
      payload.item_category = payload.item_id;
      track("click_section", payload);
      return;
    }
    if (info.event === "click_restaurant") {
      var regionCard = a.closest("[data-region-group]");
      if (regionCard) payload.region = regionCard.getAttribute("data-region-group") || "";
    }
    track(info.event, payload);
  });

  document.addEventListener("change", function (ev) {
    var el = ev.target;
    if (!el || !el.getAttribute) return;
    if (el.hasAttribute("data-courseRegion-select")) {
      track("select_region", { region: el.value || "", context: "course" });
      return;
    }
    if (el.hasAttribute("data-seoul-course-select")) {
      var curated = el.closest("[data-region-curated], [data-seoul-curated]");
      track("click_course", {
        item_id: el.value || "",
        item_name: el.value || "",
        region:
          (curated &&
            (curated.getAttribute("data-region-curated") ||
              curated.getAttribute("data-seoul-curated"))) ||
          "",
        source: "select",
      });
    }
  });

  var scrolled75 = false;
  function onScroll() {
    var doc = document.documentElement;
    var body = document.body;
    var height = Math.max(
      body ? body.scrollHeight : 0,
      doc.scrollHeight,
      doc.offsetHeight
    );
    var view = window.innerHeight || doc.clientHeight || 0;
    if (height <= view + 24) return;
    var scrollTop = window.pageYOffset || doc.scrollTop || 0;
    var pct = Math.round(((scrollTop + view) / height) * 100);
    if (!scrolled75 && pct >= 75) {
      scrolled75 = true;
      track("scroll_75", { percent_scrolled: 75 });
    }
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  setTimeout(onScroll, 400);

  window.setTimeout(function () {
    if (document.visibilityState === "hidden") return;
    track("engage_60", { engagement_seconds: 60 });
  }, 60000);

  function shareLabel() {
    var lang = currentLang();
    return SHARE_LABELS[lang] || SHARE_LABELS.en;
  }

  function sharePage(btn) {
    var url = location.href;
    var title = document.title || "";
    function done(method) {
      track("share_page", { method: method, item_id: lastSlug(location.pathname) });
      if (btn && method === "copy_link") {
        var prev = btn.textContent;
        btn.textContent = currentLang() === "ko" ? "복사됨" : "Copied";
        window.setTimeout(function () {
          btn.textContent = prev;
        }, 1600);
      }
    }
    if (navigator.share) {
      navigator
        .share({ title: title, url: url })
        .then(function () {
          done("web_share");
        })
        .catch(function () {});
      return;
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard
        .writeText(url)
        .then(function () {
          done("copy_link");
        })
        .catch(function () {});
      return;
    }
    try {
      window.prompt(shareLabel(), url);
      done("prompt");
    } catch (e) {}
  }

  function injectShare() {
    var header = document.querySelector("header.site-header");
    if (!header || header.querySelector("[data-share-page]")) return;
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "site-share";
    btn.setAttribute("data-share-page", "");
    btn.textContent = shareLabel();
    header.appendChild(btn);
  }

  document.addEventListener("guide:langchange", function () {
    document.querySelectorAll("[data-share-page]").forEach(function (btn) {
      btn.textContent = shareLabel();
    });
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", injectShare);
  } else {
    injectShare();
  }
})();
