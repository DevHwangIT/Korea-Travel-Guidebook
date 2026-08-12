/**
 * AdSense unit filler + DEV placeholder (test client / local only).
 *
 * PROD:
 *   - Head snippet loads adsbygoogle.js (official AdSense code).
 *   - Meta google-adsense-account for site verification.
 *   - This file only configures <ins> slots and calls adsbygoogle.push
 *     (does NOT inject a second adsbygoogle.js — double-load breaks ads).
 *   - Display unit: data-ad-slot="4192792767" (Bottom Ad).
 *
 * DEV / Google sample:
 *   window.ADSENSE_CLIENT = "ca-pub-3940256099942544";
 *   Forces data-adtest="on" + sample web slot when needed.
 *
 * Notes:
 *   - AdSense needs http(s). file:// usually blocks ads.
 *   - Ad blockers hide creatives.
 *   - Placeholder UI only for TEST_CLIENT, file://, or localhost.
 */
(function () {
  var TEST_CLIENT = "ca-pub-3940256099942544";
  var SAMPLE_SLOT = "6351476141";
  var PROD_SLOT = "4192792767";
  var client = typeof window !== "undefined" ? window.ADSENSE_CLIENT : "";
  if (!client || typeof client !== "string" || !/^ca-pub-\d+$/.test(client.trim())) {
    return;
  }
  client = client.trim();

  var slots = document.querySelectorAll(".ad-slot__inner ins.adsbygoogle");
  if (!slots.length) {
    slots = document.querySelectorAll("ins.adsbygoogle");
  }
  if (!slots.length) return;

  var isTest = client === TEST_CLIENT;
  var showPlaceholder =
    window.ADSENSE_SHOW_PLACEHOLDER === true ||
    (window.ADSENSE_SHOW_PLACEHOLDER !== false &&
      (isTest ||
        location.protocol === "file:" ||
        /^(localhost|127\.0\.0\.1)$/i.test(location.hostname || "")));

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
      var prodSlot = (ins.getAttribute("data-ad-slot") || "").trim();
      if (!prodSlot) {
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
        "<span class=\"ad-slot__placeholder-meta\">" +
        client +
        " · slot " +
        (ins.getAttribute("data-ad-slot") || SAMPLE_SLOT) +
        "</span>";
      wrap.insertBefore(ph, ins);
    }
  });

  function markReady(filled) {
    slots.forEach(function (ins) {
      var parent = ins.closest(".ad-slot");
      if (!parent) return;
      parent.classList.add("ad-slot--ready");
      if (filled) parent.classList.add("ad-slot--filled");
    });
  }

  var pushed = false;
  function pushAds() {
    if (pushed) return;
    pushed = true;
    slots.forEach(function () {
      try {
        (window.adsbygoogle = window.adsbygoogle || []).push({});
      } catch (e) {
        /* ignore until AdSense markup is present */
      }
    });
    markReady(false);
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

  if (location.protocol === "file:") {
    markReady(false);
    return;
  }

  // Prefer official <head> snippet; only inject if missing (no double-load).
  var existing = document.querySelector(
    'script[src*="pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"]'
  );
  if (existing) {
    existing.addEventListener("load", pushAds);
    // Script may already be loaded by the time ads.js runs
    pushAds();
    return;
  }

  var script = document.createElement("script");
  script.async = true;
  script.src =
    "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=" +
    encodeURIComponent(client);
  script.crossOrigin = "anonymous";
  script.addEventListener("load", pushAds);
  script.addEventListener("error", function () {
    markReady(false);
  });
  document.head.appendChild(script);
})();
