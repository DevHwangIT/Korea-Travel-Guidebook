/**
 * AdSense: site verification on every page + display units on content pages.
 *
 * - Meta google-adsense-account + adsbygoogle.js (once).
 * - Display slot only on hubs / articles / lists — not shop-detail or privacy.
 * - Does not double-load adsbygoogle.js.
 * Localhost / file:// / test client: placeholder only (no live ads).
 */
(function () {
  var PROD_CLIENT = "ca-pub-7139367317436403";
  var TEST_CLIENT = "ca-pub-3940256099942544";
  var SAMPLE_SLOT = "6351476141";
  var PROD_SLOT = "4192792767";

  if (window.__GUIDE_ADS_BOUND__) return;
  window.__GUIDE_ADS_BOUND__ = true;

  var client = "";
  if (typeof window.ADSENSE_CLIENT === "string" && /^ca-pub-\d+$/.test(window.ADSENSE_CLIENT.trim())) {
    client = window.ADSENSE_CLIENT.trim();
  } else {
    client = PROD_CLIENT;
    window.ADSENSE_CLIENT = client;
  }

  var isTest = client === TEST_CLIENT;
  var host = String(location.hostname || "").toLowerCase();
  var isLocal =
    location.protocol === "file:" ||
    host === "localhost" ||
    host === "127.0.0.1" ||
    host === "::1";
  var showPlaceholder =
    window.ADSENSE_SHOW_PLACEHOLDER === true ||
    (window.ADSENSE_SHOW_PLACEHOLDER !== false && (isTest || isLocal));

  function ensureMeta() {
    if (document.querySelector('meta[name="google-adsense-account"]')) return;
    var meta = document.createElement("meta");
    meta.setAttribute("name", "google-adsense-account");
    meta.setAttribute("content", client);
    document.head.appendChild(meta);
  }

  function isPrivacyPage() {
    return String(location.pathname || "").toLowerCase().indexOf("/privacy") >= 0;
  }

  function isShopDetail() {
    return !!document.querySelector("[data-shop-detail]");
  }

  function isContentPage() {
    if (isPrivacyPage() || isShopDetail()) return false;
    if (document.body && document.body.classList.contains("home-page")) return true;
    if (
      document.querySelector(
        ".hub-page, .article-page, .tip-article, .guide-article, .food-hub, [data-food-quiz], [data-buy-hub], [data-prep-map], [data-festivals-slider], [data-content-body], [data-list-pager], section.intro"
      )
    ) {
      return true;
    }
    var p = String(location.pathname || "").toLowerCase();
    return (
      /\/pages\/(food-life|foods|before-trip|travel-tips|travel-courses|prep|buy|festivals|apps|useful-korean|emergency|transportation|convenience-store|fun)(\/|$)/.test(
        p
      ) && !isShopDetail()
    );
  }

  function adLabel() {
    try {
      if (window.GuideI18n && typeof window.GuideI18n.t === "function") {
        return window.GuideI18n.t("common.adLabel", "Advertisement");
      }
    } catch (e) {}
    return "Advertisement";
  }

  function injectDisplaySlot() {
    if (document.querySelector("ins.adsbygoogle")) return;
    if (!isContentPage()) return;
    var aside = document.createElement("aside");
    aside.className = "ad-slot ad-slot--banner ad-slot--below-footer";
    aside.setAttribute("aria-label", adLabel());
    aside.innerHTML =
      '<span class="ad-slot__label">' +
      adLabel() +
      "</span>" +
      '<div class="ad-slot__inner" data-ad-slot>' +
      '<ins class="adsbygoogle" style="display:block;min-height:90px;width:100%"' +
      ' data-ad-client="' +
      client +
      '" data-ad-slot="' +
      PROD_SLOT +
      '" data-ad-format="auto" data-full-width-responsive="true"></ins>' +
      "</div>";
    var footer = document.querySelector("footer.site-footer, .site-footer");
    if (footer && footer.parentNode) {
      footer.parentNode.insertBefore(aside, footer.nextSibling);
      return;
    }
    document.body.appendChild(aside);
  }

  function collectSlots() {
    var slots = document.querySelectorAll(".ad-slot__inner ins.adsbygoogle");
    if (!slots.length) slots = document.querySelectorAll("ins.adsbygoogle");
    return slots;
  }

  function prepareSlots(slots) {
    slots.forEach(function (ins) {
      if (!ins.getAttribute("data-ad-client")) {
        ins.setAttribute("data-ad-client", client);
      }
      if (isTest) {
        ins.setAttribute("data-adtest", "on");
        var slot = (ins.getAttribute("data-ad-slot") || "").trim();
        if (!slot || slot === "6300978111" || slot === "1234567890") {
          ins.setAttribute("data-ad-slot", SAMPLE_SLOT);
        }
      } else {
        if (!(ins.getAttribute("data-ad-slot") || "").trim()) {
          ins.setAttribute("data-ad-slot", PROD_SLOT);
        }
        ins.removeAttribute("data-adtest");
      }
      var style = ins.getAttribute("style") || "";
      if (!/display\s*:/i.test(style)) {
        ins.setAttribute("style", "display:block;min-height:90px;width:100%;" + style);
      } else if (/display\s*:\s*none/i.test(style)) {
        ins.setAttribute(
          "style",
          style.replace(/display\s*:\s*none/gi, "display:block") + ";min-height:90px;width:100%;"
        );
      }

      var wrap = ins.closest(".ad-slot__inner") || ins.parentElement;
      if (wrap && showPlaceholder && !wrap.querySelector(".ad-slot__placeholder")) {
        var ph = document.createElement("div");
        ph.className = "ad-slot__placeholder";
        ph.setAttribute("aria-hidden", "true");
        ph.innerHTML =
          "<strong>Ad slot</strong>" +
          "<span>Test tags loaded · creatives need HTTPS + no ad blocker</span>" +
          '<span class="ad-slot__placeholder-meta">' +
          client +
          " · slot " +
          (ins.getAttribute("data-ad-slot") || SAMPLE_SLOT) +
          "</span>";
        wrap.insertBefore(ph, ins);
      }
    });
  }

  function markReady(slots, filled) {
    slots.forEach(function (ins) {
      var parent = ins.closest(".ad-slot");
      if (!parent) return;
      parent.classList.add("ad-slot--ready");
      if (filled) parent.classList.add("ad-slot--filled");
    });
  }

  var pushed = false;
  function pushAds(slots) {
    if (pushed || !slots.length) return;
    if (location.protocol === "file:") {
      markReady(slots, false);
      return;
    }
    if (isLocal && !isTest && window.GA4_DEBUG !== true && window.ADSENSE_FORCE !== true) {
      markReady(slots, false);
      return;
    }
    pushed = true;
    slots.forEach(function () {
      try {
        (window.adsbygoogle = window.adsbygoogle || []).push({});
      } catch (e) {}
    });
    markReady(slots, false);
    window.setTimeout(function () {
      slots.forEach(function (ins) {
        var h = ins.offsetHeight || 0;
        var status = (ins.getAttribute("data-ad-status") || "").toLowerCase();
        var filled = h > 40 || status === "filled";
        if (filled) {
          var wrap = ins.closest(".ad-slot__inner");
          var ph = wrap && wrap.querySelector(".ad-slot__placeholder");
          if (ph) ph.hidden = true;
          var parent = ins.closest(".ad-slot");
          if (parent) parent.classList.add("ad-slot--filled");
        }
      });
    }, 2500);
  }

  function loadScript(onReady) {
    var existing = document.querySelector(
      'script[src*="pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"]'
    );
    if (existing) {
      if (existing.getAttribute("data-guide-ads-loaded") === "1") {
        onReady();
        return;
      }
      existing.addEventListener("load", onReady);
      onReady();
      return;
    }
    var script = document.createElement("script");
    script.async = true;
    script.crossOrigin = "anonymous";
    script.src =
      "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=" +
      encodeURIComponent(client);
    script.addEventListener("load", function () {
      script.setAttribute("data-guide-ads-loaded", "1");
      onReady();
    });
    script.addEventListener("error", function () {
      markReady(collectSlots(), false);
    });
    document.head.appendChild(script);
  }

  function boot() {
    ensureMeta();
    if (isPrivacyPage() || isShopDetail()) return;
    injectDisplaySlot();
    var slots = collectSlots();
    if (!slots.length) return;
    prepareSlots(slots);
    loadScript(function () {
      pushAds(slots);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
