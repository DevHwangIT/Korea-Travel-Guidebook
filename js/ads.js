/**
 * AdSense loader + DEV placeholder (test client / local only).
 *
 * PROD (wired now):
 *   window.ADSENSE_CLIENT = "ca-pub-7139367317436403";
 *   Meta google-adsense-account on pages (site verification).
 *   Script loads via this file — do NOT also put adsbygoogle.js in <head>
 *   (double-load breaks push). Display unit: data-ad-slot="4192792767" (Bottom Ad).
 *
 * DEV / Google sample:
 *   window.ADSENSE_CLIENT = "ca-pub-3940256099942544";
 *   Forces data-adtest="on" + sample web slot 6351476141 when needed.
 *
 * Notes:
 *   - AdSense needs http(s) (localhost / GitHub Pages). file:// usually blocks ads.
 *   - Ad blockers / privacy extensions hide creatives.
 *   - Google’s mobile AdMob unit IDs (ca-app-pub-…/6300978111) are NOT web AdSense slots.
 *   - Placeholder UI only for TEST_CLIENT, file://, or localhost — not for PROD on HTTPS.
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
      // Migrate mistaken AdMob banner unit id → web sample slot
      if (!slot || slot === "6300978111" || slot === "1234567890") {
        ins.setAttribute("data-ad-slot", SAMPLE_SLOT);
      }
    } else {
      var prodSlot = (ins.getAttribute("data-ad-slot") || "").trim();
      if (!prodSlot) {
        ins.setAttribute("data-ad-slot", PROD_SLOT);
      }
      // Real publisher: never force adtest
      ins.removeAttribute("data-adtest");
    }
    // Ensure AdSense can measure a visible box (never display:none)
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

  function pushAds() {
    slots.forEach(function (ins) {
      try {
        (window.adsbygoogle = window.adsbygoogle || []).push({});
      } catch (e) {
        /* ignore until AdSense markup is present */
      }
    });
    markReady(false);
    // If a creative fills, hide the placeholder for that slot
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

  // file:// cannot load remote AdSense — keep placeholder only
  if (location.protocol === "file:") {
    markReady(false);
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
