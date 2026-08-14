/**
 * Sitewide floating travel utilities (currency / weather / timezone / units).
 * Loaded dynamically from i18n.js — not a menu category.
 * Collapsed FAB → tool picker → single tool panel. Soft guidebook UI.
 */
(function () {
  var ROOT_ID = "guide-travel-utils";
  var STORAGE_KEY = "korea-guide-travel-utils";
  var FX_CACHE_KEY = "korea-guide-fx-cache";
  var FX_CACHE_MS = 30 * 60 * 1000; // 30 min
  var WEATHER_CACHE_KEY = "korea-guide-weather-cache";
  var WEATHER_CACHE_MS = 15 * 60 * 1000; // 15 min

  var CURRENCIES = [
    "USD",
    "EUR",
    "JPY",
    "CNY",
    "GBP",
    "AUD",
    "CAD",
    "SGD",
    "HKD",
    "THB",
    "TWD",
    "VND",
    "PHP",
    "MYR",
    "IDR",
  ];

  var REGIONS = [
    { id: "seoul", lat: 37.5665, lon: 126.978 },
    { id: "busan", lat: 35.1796, lon: 129.0756 },
    { id: "jeju", lat: 33.4996, lon: 126.5312 },
    { id: "incheon", lat: 37.4563, lon: 126.7052 },
    { id: "daegu", lat: 35.8714, lon: 128.6014 },
    { id: "gwangju", lat: 35.1595, lon: 126.8526 },
    { id: "daejeon", lat: 36.3504, lon: 127.3845 },
    { id: "gangneung", lat: 37.7519, lon: 128.8761 },
    { id: "gyeongju", lat: 35.8562, lon: 129.2247 },
  ];

  /* Traveler-focused IANA zones. id "device" = browser local TZ. */
  var TIMEZONES = [
    { id: "device", tz: null },
    { id: "seoul", tz: "Asia/Seoul" },
    { id: "tokyo", tz: "Asia/Tokyo" },
    { id: "osaka", tz: "Asia/Tokyo" },
    { id: "shanghai", tz: "Asia/Shanghai" },
    { id: "taipei", tz: "Asia/Taipei" },
    { id: "hongkong", tz: "Asia/Hong_Kong" },
    { id: "singapore", tz: "Asia/Singapore" },
    { id: "bangkok", tz: "Asia/Bangkok" },
    { id: "hochiminh", tz: "Asia/Ho_Chi_Minh" },
    { id: "manila", tz: "Asia/Manila" },
    { id: "kualalumpur", tz: "Asia/Kuala_Lumpur" },
    { id: "jakarta", tz: "Asia/Jakarta" },
    { id: "delhi", tz: "Asia/Kolkata" },
    { id: "dubai", tz: "Asia/Dubai" },
    { id: "london", tz: "Europe/London" },
    { id: "paris", tz: "Europe/Paris" },
    { id: "berlin", tz: "Europe/Berlin" },
    { id: "rome", tz: "Europe/Rome" },
    { id: "madrid", tz: "Europe/Madrid" },
    { id: "newyork", tz: "America/New_York" },
    { id: "losangeles", tz: "America/Los_Angeles" },
    { id: "chicago", tz: "America/Chicago" },
    { id: "toronto", tz: "America/Toronto" },
    { id: "vancouver", tz: "America/Vancouver" },
    { id: "saopaulo", tz: "America/Sao_Paulo" },
    { id: "sydney", tz: "Australia/Sydney" },
    { id: "auckland", tz: "Pacific/Auckland" },
    { id: "honolulu", tz: "Pacific/Honolulu" },
  ];

  var WMO = {
    0: "clear",
    1: "mainlyClear",
    2: "partlyCloudy",
    3: "overcast",
    45: "fog",
    48: "fog",
    51: "drizzle",
    53: "drizzle",
    55: "drizzle",
    61: "rain",
    63: "rain",
    65: "rain",
    71: "snow",
    73: "snow",
    75: "snow",
    80: "showers",
    81: "showers",
    82: "showers",
    95: "thunder",
    96: "thunder",
    99: "thunder",
  };

  var state = {
    open: false,
    view: "menu", // menu | currency | weather | timezone | units
    lastTool: "currency",
    fxFrom: "USD",
    fxAmount: "100",
    weatherRegion: "seoul",
    tzZone: "device",
    clockTimer: null,
  };

  function scriptDir() {
    var scripts = document.getElementsByTagName("script");
    for (var i = scripts.length - 1; i >= 0; i--) {
      var src = scripts[i].src || "";
      if (src.indexOf("travel-utils.js") !== -1) {
        return src.replace(/\/[^/]*$/, "/");
      }
    }
    return "./js/";
  }

  function cssHref() {
    return (
      scriptDir().replace(/\/js\/?$/, "/css/") +
      "travel-utils.css?v=" +
      encodeURIComponent(window.SITE_ASSET_VERSION || "")
    );
  }

  function ensureCss() {
    if (document.querySelector('link[data-guide-travel-utils-css="1"]')) return;
    var link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = cssHref();
    link.setAttribute("data-guide-travel-utils-css", "1");
    (document.head || document.documentElement).appendChild(link);
  }

  function loadState() {
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return;
      var saved = JSON.parse(raw);
      if (typeof saved.open === "boolean") state.open = saved.open;
      if (saved.lastTool) state.lastTool = saved.lastTool;
      if (saved.fxFrom) state.fxFrom = saved.fxFrom;
      if (saved.fxAmount != null) state.fxAmount = String(saved.fxAmount);
      if (saved.weatherRegion) state.weatherRegion = saved.weatherRegion;
      if (saved.tzZone && findTimezone(saved.tzZone)) {
        state.tzZone = saved.tzZone;
      }
      if (saved.view === "menu" || saved.view === state.lastTool) {
        state.view = saved.view || "menu";
      }
    } catch (e) {
      /* ignore */
    }
  }

  function saveState() {
    try {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({
          open: state.open,
          view: state.view,
          lastTool: state.lastTool,
          fxFrom: state.fxFrom,
          fxAmount: state.fxAmount,
          weatherRegion: state.weatherRegion,
          tzZone: state.tzZone,
        })
      );
    } catch (e) {
      /* ignore */
    }
  }

  function t(key, fallback) {
    try {
      if (window.GuideI18n && typeof window.GuideI18n.lookupWithFallback === "function") {
        var via = window.GuideI18n.lookupWithFallback(
          key,
          window.GuideI18n.getLang && window.GuideI18n.getLang()
        );
        if (via != null && via !== "") return String(via);
      }
    } catch (e0) {
      /* ignore */
    }
    var dict = null;
    try {
      var lang = window.GuideI18n && window.GuideI18n.getLang();
      if (lang && window.__I18N_MESSAGES__ && window.__I18N_MESSAGES__[lang]) {
        dict = window.__I18N_MESSAGES__[lang];
      }
    } catch (e) {
      /* ignore */
    }
    if (!dict) return fallback;
    var parts = key.split(".");
    var cur = dict;
    for (var i = 0; i < parts.length; i++) {
      if (!cur || !Object.prototype.hasOwnProperty.call(cur, parts[i])) {
        return fallback;
      }
      cur = cur[parts[i]];
    }
    return cur == null || cur === "" ? fallback : String(cur);
  }

  function applyI18n(root) {
    root.querySelectorAll("[data-i18n]").forEach(function (el) {
      var key = el.getAttribute("data-i18n");
      el.textContent = t(key, el.textContent);
    });
    root.querySelectorAll("[data-i18n-attr]").forEach(function (el) {
      var specs = el.getAttribute("data-i18n-attr").split(",");
      specs.forEach(function (spec) {
        var parts = spec.split(":");
        if (parts.length < 2) return;
        var attr = parts[0].trim();
        var key = parts.slice(1).join(":").trim();
        el.setAttribute(attr, t(key, el.getAttribute(attr) || ""));
      });
    });
  }

  function formatNumber(n, digits) {
    if (!isFinite(n)) return "—";
    var d = digits == null ? 2 : digits;
    try {
      return new Intl.NumberFormat(undefined, {
        maximumFractionDigits: d,
        minimumFractionDigits: 0,
      }).format(n);
    } catch (e) {
      return String(Math.round(n * Math.pow(10, d)) / Math.pow(10, d));
    }
  }

  function readCache(key, maxAge) {
    try {
      var raw = localStorage.getItem(key);
      if (!raw) return null;
      var obj = JSON.parse(raw);
      if (!obj || !obj.at || Date.now() - obj.at > maxAge) return null;
      return obj.data;
    } catch (e) {
      return null;
    }
  }

  function writeCache(key, data) {
    try {
      localStorage.setItem(key, JSON.stringify({ at: Date.now(), data: data }));
    } catch (e) {
      /* ignore */
    }
  }

  /* —— FX (no API key): fawazahmed0 currency-api via jsDelivr —— */
  function fetchFxRates() {
    var cached = readCache(FX_CACHE_KEY, FX_CACHE_MS);
    if (cached && cached.krw) return Promise.resolve(cached);

    var url =
      "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/krw.json";
    return fetch(url)
      .then(function (res) {
        if (!res.ok) throw new Error("HTTP " + res.status);
        return res.json();
      })
      .then(function (json) {
        var krw = (json && json.krw) || {};
        var data = { krw: krw, date: json.date || "" };
        writeCache(FX_CACHE_KEY, data);
        return data;
      });
  }

  function convertFx(amount, fromCode, rates) {
    var code = String(fromCode || "").toLowerCase();
    if (code === "krw") return amount;
    var perKrw = rates.krw && rates.krw[code];
    if (!perKrw || !isFinite(perKrw) || perKrw === 0) return NaN;
    // rates.krw.usd = how many USD per 1 KRW → KRW = amount / rate
    return amount / perKrw;
  }

  function convertFromKrw(amountKrw, toCode, rates) {
    var code = String(toCode || "").toLowerCase();
    if (code === "krw") return amountKrw;
    var perKrw = rates.krw && rates.krw[code];
    if (!perKrw || !isFinite(perKrw)) return NaN;
    return amountKrw * perKrw;
  }

  /* —— Weather: Open-Meteo —— */
  function fetchWeather(region) {
    var cacheAll = readCache(WEATHER_CACHE_KEY, WEATHER_CACHE_MS) || {};
    if (cacheAll[region.id]) return Promise.resolve(cacheAll[region.id]);

    var url =
      "https://api.open-meteo.com/v1/forecast?latitude=" +
      encodeURIComponent(region.lat) +
      "&longitude=" +
      encodeURIComponent(region.lon) +
      "&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m" +
      "&timezone=Asia%2FSeoul&wind_speed_unit=kmh";

    return fetch(url)
      .then(function (res) {
        if (!res.ok) throw new Error("HTTP " + res.status);
        return res.json();
      })
      .then(function (json) {
        var cur = json.current || {};
        var data = {
          temp: cur.temperature_2m,
          humidity: cur.relative_humidity_2m,
          code: cur.weather_code,
          wind: cur.wind_speed_10m,
          time: cur.time || "",
        };
        cacheAll[region.id] = data;
        writeCache(WEATHER_CACHE_KEY, cacheAll);
        return data;
      });
  }

  function weatherLabel(code) {
    var key = WMO[code] || "unknown";
    return t("travelUtils.weatherCodes." + key, key);
  }

  function regionLabel(id) {
    return t("travelUtils.regions." + id, id);
  }

  function findTimezone(id) {
    for (var i = 0; i < TIMEZONES.length; i++) {
      if (TIMEZONES[i].id === id) return TIMEZONES[i];
    }
    return null;
  }

  function cityLabel(id) {
    if (id === "device") {
      return t("travelUtils.tzDevice", "Device local time");
    }
    return t("travelUtils.cities." + id, id);
  }

  function resolveTzId(entry) {
    if (!entry) return localTzName();
    if (entry.id === "device" || !entry.tz) return localTzName();
    return entry.tz;
  }

  /* —— Timezone —— */
  function formatInTz(date, timeZone) {
    try {
      return new Intl.DateTimeFormat(undefined, {
        timeZone: timeZone,
        weekday: "short",
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
        hour12: false,
      }).format(date);
    } catch (e) {
      return date.toISOString();
    }
  }

  function tzOffsetMinutes(date, timeZone) {
    try {
      var parts = new Intl.DateTimeFormat("en-US", {
        timeZone: timeZone,
        timeZoneName: "shortOffset",
        hour: "2-digit",
      }).formatToParts(date);
      var name = "";
      for (var i = 0; i < parts.length; i++) {
        if (parts[i].type === "timeZoneName") name = parts[i].value;
      }
      // GMT+9 / UTC+09:00 / GMT+5:30
      var m = name.match(/([+-])(\d{1,2})(?::?(\d{2}))?/);
      if (!m) {
        // Fallback via locale string
        var a = new Date(date.toLocaleString("en-US", { timeZone: "UTC" }));
        var b = new Date(date.toLocaleString("en-US", { timeZone: timeZone }));
        return Math.round((b - a) / 60000);
      }
      var sign = m[1] === "-" ? -1 : 1;
      var hh = parseInt(m[2], 10);
      var mm = m[3] ? parseInt(m[3], 10) : 0;
      return sign * (hh * 60 + mm);
    } catch (e) {
      return null;
    }
  }

  function localTzName() {
    try {
      return Intl.DateTimeFormat().resolvedOptions().timeZone || "Local";
    } catch (e) {
      return "Local";
    }
  }

  function formatDiffHours(diffMin) {
    if (diffMin == null || !isFinite(diffMin)) return "—";
    if (diffMin === 0) return t("travelUtils.tzSame", "Same as Korea");
    var abs = Math.abs(diffMin);
    var h = Math.floor(abs / 60);
    var m = abs % 60;
    var ahead = diffMin > 0;
    var mm = m < 10 ? "0" + m : String(m);
    var core = h + (m ? ":" + mm : "") + "h";
    if (ahead) {
      return t(
        "travelUtils.tzAhead",
        "Selected city is {n} ahead of Korea"
      ).replace("{n}", core);
    }
    return t(
      "travelUtils.tzBehind",
      "Selected city is {n} behind Korea"
    ).replace("{n}", core);
  }

  /* —— DOM —— */
  function tools() {
    return [
      { id: "currency", icon: "₩", labelKey: "travelUtils.currency", fb: "Currency" },
      { id: "weather", icon: "☁", labelKey: "travelUtils.weather", fb: "Weather" },
      { id: "timezone", icon: "◷", labelKey: "travelUtils.timezone", fb: "Time difference" },
      { id: "units", icon: "⇄", labelKey: "travelUtils.units", fb: "Units" },
    ];
  }

  function buildRoot() {
    if (document.getElementById(ROOT_ID)) {
      return document.getElementById(ROOT_ID);
    }

    var root = document.createElement("div");
    root.id = ROOT_ID;
    root.className = "travel-utils";
    root.setAttribute("data-open", "0");
    root.innerHTML =
      '<button type="button" class="travel-utils__fab" data-tu-toggle ' +
      'data-i18n-attr="aria-label:travelUtils.open" aria-label="Travel tools" aria-expanded="false">' +
      '<span class="travel-utils__fab-icon" aria-hidden="true">' +
      '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">' +
      '<circle cx="12" cy="12" r="8.5"/>' +
      '<path d="M12 7.5v4.2l2.8 2.8"/>' +
      "</svg></span>" +
      "</button>" +
      '<div class="travel-utils__panel" data-tu-panel hidden>' +
      '  <div class="travel-utils__chrome">' +
      '    <button type="button" class="travel-utils__back" data-tu-back hidden ' +
      'data-i18n-attr="aria-label:travelUtils.back" aria-label="Back">←</button>' +
      '    <h2 class="travel-utils__title" data-tu-title data-i18n="travelUtils.title">Travel tools</h2>' +
      '    <button type="button" class="travel-utils__close" data-tu-close ' +
      'data-i18n-attr="aria-label:travelUtils.close" aria-label="Close">×</button>' +
      "  </div>" +
      '  <div class="travel-utils__body" data-tu-body></div>' +
      '  <p class="travel-utils__ref" data-i18n="travelUtils.reference">For reference only</p>' +
      "</div>";

    document.body.appendChild(root);

    root.addEventListener("click", function (e) {
      if (e.target.closest("[data-tu-toggle]")) {
        e.preventDefault();
        toggleOpen();
        return;
      }
      if (e.target.closest("[data-tu-close]")) {
        e.preventDefault();
        setOpen(false);
        return;
      }
      if (e.target.closest("[data-tu-back]")) {
        e.preventDefault();
        state.view = "menu";
        saveState();
        renderBody();
        return;
      }
      var pick = e.target.closest("[data-tu-tool]");
      if (pick) {
        e.preventDefault();
        openTool(pick.getAttribute("data-tu-tool"));
      }
    });

    document.addEventListener("keydown", function (e) {
      if (e.key !== "Escape") return;
      if (!state.open) return;
      // Don't steal Escape from welcome modal
      if (document.body.classList.contains("welcome-popup-lock")) return;
      e.preventDefault();
      if (state.view !== "menu") {
        state.view = "menu";
        saveState();
        renderBody();
      } else {
        setOpen(false);
      }
    });

    return root;
  }

  function setOpen(open) {
    state.open = !!open;
    if (!state.open) {
      state.view = "menu";
      stopClock();
    }
    saveState();
    syncUi();
  }

  function toggleOpen() {
    setOpen(!state.open);
  }

  function openTool(id) {
    state.view = id;
    state.lastTool = id;
    saveState();
    renderBody();
  }

  function syncUi() {
    var root = document.getElementById(ROOT_ID);
    if (!root) return;
    root.setAttribute("data-open", state.open ? "1" : "0");
    var fab = root.querySelector("[data-tu-toggle]");
    var panel = root.querySelector("[data-tu-panel]");
    if (fab) fab.setAttribute("aria-expanded", state.open ? "true" : "false");
    if (panel) panel.hidden = !state.open;
    if (state.open) renderBody();
    else stopClock();
  }

  function setTitle(key, fb) {
    var root = document.getElementById(ROOT_ID);
    if (!root) return;
    var title = root.querySelector("[data-tu-title]");
    var back = root.querySelector("[data-tu-back]");
    if (title) {
      title.setAttribute("data-i18n", key);
      title.textContent = t(key, fb);
    }
    if (back) back.hidden = state.view === "menu";
  }

  function renderBody() {
    var root = document.getElementById(ROOT_ID);
    if (!root || !state.open) return;
    var body = root.querySelector("[data-tu-body]");
    if (!body) return;

    stopClock();

    if (state.view === "menu") {
      setTitle("travelUtils.title", "Travel tools");
      body.innerHTML =
        '<ul class="travel-utils__menu">' +
        tools()
          .map(function (tool) {
            return (
              '<li><button type="button" class="travel-utils__menu-btn" data-tu-tool="' +
              tool.id +
              '">' +
              '<span class="travel-utils__menu-icon" aria-hidden="true">' +
              tool.icon +
              "</span>" +
              '<span data-i18n="' +
              tool.labelKey +
              '">' +
              tool.fb +
              "</span>" +
              "</button></li>"
            );
          })
          .join("") +
        "</ul>";
      applyI18n(root);
      return;
    }

    if (state.view === "currency") {
      setTitle("travelUtils.currency", "Currency");
      renderCurrency(body);
    } else if (state.view === "weather") {
      setTitle("travelUtils.weather", "Weather");
      renderWeather(body);
    } else if (state.view === "timezone") {
      setTitle("travelUtils.timezone", "Time difference");
      renderTimezone(body);
    } else if (state.view === "units") {
      setTitle("travelUtils.units", "Units");
      renderUnits(body);
    }
    applyI18n(root);
  }

  function renderCurrency(body) {
    var opts = CURRENCIES.map(function (c) {
      return (
        '<option value="' +
        c +
        '"' +
        (c === state.fxFrom ? " selected" : "") +
        ">" +
        c +
        "</option>"
      );
    }).join("");

    body.innerHTML =
      '<div class="travel-utils__form" data-tu-fx>' +
      '  <label class="travel-utils__label"><span data-i18n="travelUtils.amount">Amount</span>' +
      '    <input type="number" inputmode="decimal" min="0" step="any" class="travel-utils__input" data-tu-fx-amount value="' +
      String(state.fxAmount).replace(/"/g, "") +
      '">' +
      "  </label>" +
      '  <label class="travel-utils__label"><span data-i18n="travelUtils.fromCurrency">From</span>' +
      '    <select class="travel-utils__select" data-tu-fx-from>' +
      opts +
      "</select>" +
      "  </label>" +
      '  <div class="travel-utils__result" data-tu-fx-out aria-live="polite">' +
      '    <p class="travel-utils__muted" data-i18n="travelUtils.loading">Loading…</p>' +
      "  </div>" +
      "</div>";

    var amountEl = body.querySelector("[data-tu-fx-amount]");
    var fromEl = body.querySelector("[data-tu-fx-from]");

    function run() {
      state.fxAmount = amountEl.value;
      state.fxFrom = fromEl.value;
      saveState();
      updateFxOut(body);
    }

    amountEl.addEventListener("input", run);
    fromEl.addEventListener("change", run);
    updateFxOut(body);
  }

  function updateFxOut(body) {
    var out = body.querySelector("[data-tu-fx-out]");
    if (!out) return;
    var amount = parseFloat(String(state.fxAmount).replace(/,/g, ""), 10);
    if (!isFinite(amount) || amount < 0) {
      out.innerHTML =
        '<p class="travel-utils__error" data-i18n="travelUtils.invalidAmount">Enter a valid amount</p>';
      applyI18n(out);
      return;
    }

    out.innerHTML =
      '<p class="travel-utils__muted" data-i18n="travelUtils.loading">Loading…</p>';
    applyI18n(out);

    fetchFxRates()
      .then(function (rates) {
        var toKrw = convertFx(amount, state.fxFrom, rates);
        var back = convertFromKrw(10000, state.fxFrom, rates);
        var html =
          '<p class="travel-utils__fx-main"><strong>' +
          formatNumber(amount, 2) +
          " " +
          state.fxFrom +
          "</strong> ≈ <strong>" +
          formatNumber(toKrw, 0) +
          " KRW</strong></p>" +
          '<p class="travel-utils__fx-sub">10,000 KRW ≈ ' +
          formatNumber(back, state.fxFrom === "JPY" || state.fxFrom === "VND" ? 0 : 2) +
          " " +
          state.fxFrom +
          "</p>";
        if (rates.date) {
          html +=
            '<p class="travel-utils__meta">' +
            t("travelUtils.rateDate", "Rate date") +
            ": " +
            rates.date +
            "</p>";
        }
        out.innerHTML = html;
      })
      .catch(function () {
        out.innerHTML =
          '<p class="travel-utils__error" data-i18n="travelUtils.fxError">Could not load exchange rates. Check your connection.</p>';
        applyI18n(out);
      });
  }

  function renderWeather(body) {
    var opts = REGIONS.map(function (r) {
      return (
        '<option value="' +
        r.id +
        '"' +
        (r.id === state.weatherRegion ? " selected" : "") +
        ">" +
        regionLabel(r.id) +
        "</option>"
      );
    }).join("");

    body.innerHTML =
      '<div class="travel-utils__form" data-tu-wx>' +
      '  <label class="travel-utils__label"><span data-i18n="travelUtils.region">Region</span>' +
      '    <select class="travel-utils__select" data-tu-wx-region>' +
      opts +
      "</select>" +
      "  </label>" +
      '  <div class="travel-utils__result" data-tu-wx-out aria-live="polite">' +
      '    <p class="travel-utils__muted" data-i18n="travelUtils.loading">Loading…</p>' +
      "  </div>" +
      "</div>";

    var sel = body.querySelector("[data-tu-wx-region]");
    sel.addEventListener("change", function () {
      state.weatherRegion = sel.value;
      saveState();
      updateWeatherOut(body);
    });
    updateWeatherOut(body);
  }

  function updateWeatherOut(body) {
    var out = body.querySelector("[data-tu-wx-out]");
    if (!out) return;
    var region = null;
    for (var i = 0; i < REGIONS.length; i++) {
      if (REGIONS[i].id === state.weatherRegion) {
        region = REGIONS[i];
        break;
      }
    }
    if (!region) region = REGIONS[0];

    out.innerHTML =
      '<p class="travel-utils__muted" data-i18n="travelUtils.loading">Loading…</p>';
    applyI18n(out);

    fetchWeather(region)
      .then(function (data) {
        var tempC = data.temp;
        var tempF = tempC * 1.8 + 32;
        out.innerHTML =
          '<p class="travel-utils__wx-main"><strong>' +
          regionLabel(region.id) +
          "</strong></p>" +
          '<p class="travel-utils__wx-temp">' +
          formatNumber(tempC, 1) +
          "°C / " +
          formatNumber(tempF, 1) +
          "°F</p>" +
          "<p>" +
          weatherLabel(data.code) +
          "</p>" +
          '<p class="travel-utils__meta">' +
          t("travelUtils.humidity", "Humidity") +
          ": " +
          formatNumber(data.humidity, 0) +
          "% · " +
          t("travelUtils.wind", "Wind") +
          ": " +
          formatNumber(data.wind, 0) +
          " km/h</p>";
      })
      .catch(function () {
        out.innerHTML =
          '<p class="travel-utils__error" data-i18n="travelUtils.weatherError">Could not load weather. Check your connection.</p>';
        applyI18n(out);
      });
  }

  function stopClock() {
    if (state.clockTimer) {
      clearInterval(state.clockTimer);
      state.clockTimer = null;
    }
  }

  function renderTimezone(body) {
    if (!findTimezone(state.tzZone)) state.tzZone = "device";

    var opts = TIMEZONES.map(function (z) {
      var label = cityLabel(z.id);
      if (z.id === "device") {
        label += " (" + localTzName() + ")";
      }
      return (
        '<option value="' +
        z.id +
        '"' +
        (z.id === state.tzZone ? " selected" : "") +
        ">" +
        label +
        "</option>"
      );
    }).join("");

    body.innerHTML =
      '<div class="travel-utils__form" data-tu-tz>' +
      '  <label class="travel-utils__label"><span data-i18n="travelUtils.tzPickCity">Compare with</span>' +
      '    <select class="travel-utils__select" data-tu-tz-city>' +
      opts +
      "</select>" +
      "  </label>" +
      '  <div class="travel-utils__tz-row">' +
      '    <p class="travel-utils__label" data-i18n="travelUtils.koreaTime">Korea (Seoul)</p>' +
      '    <p class="travel-utils__tz-time" data-tu-tz-kr>—</p>' +
      "  </div>" +
      '  <div class="travel-utils__tz-row">' +
      '    <p class="travel-utils__label"><span data-tu-tz-city-label></span> <span class="travel-utils__meta" data-tu-tz-name></span></p>' +
      '    <p class="travel-utils__tz-time" data-tu-tz-local>—</p>' +
      "  </div>" +
      '  <p class="travel-utils__tz-diff" data-tu-tz-diff aria-live="polite"></p>' +
      "</div>";

    var sel = body.querySelector("[data-tu-tz-city]");
    sel.addEventListener("change", function () {
      state.tzZone = sel.value;
      saveState();
      tick();
    });

    function tick() {
      var entry = findTimezone(state.tzZone) || TIMEZONES[0];
      var iana = resolveTzId(entry);
      var now = new Date();
      var kr = body.querySelector("[data-tu-tz-kr]");
      var loc = body.querySelector("[data-tu-tz-local]");
      var diff = body.querySelector("[data-tu-tz-diff]");
      var labelEl = body.querySelector("[data-tu-tz-city-label]");
      var nameEl = body.querySelector("[data-tu-tz-name]");

      if (labelEl) labelEl.textContent = cityLabel(entry.id);
      if (nameEl) nameEl.textContent = "(" + iana + ")";
      if (kr) kr.textContent = formatInTz(now, "Asia/Seoul");
      if (loc) loc.textContent = formatInTz(now, iana);
      if (diff) {
        var krOff = tzOffsetMinutes(now, "Asia/Seoul");
        var locOff = tzOffsetMinutes(now, iana);
        var delta = locOff != null && krOff != null ? locOff - krOff : null;
        diff.textContent = formatDiffHours(delta);
      }
    }

    tick();
    state.clockTimer = setInterval(tick, 1000);
  }

  function renderUnits(body) {
    body.innerHTML =
      '<div class="travel-utils__form" data-tu-units>' +
      '  <fieldset class="travel-utils__fieldset">' +
      '    <legend data-i18n="travelUtils.temp">Temperature</legend>' +
      '    <div class="travel-utils__row2">' +
      '      <label class="travel-utils__label">°C' +
      '        <input type="number" step="any" class="travel-utils__input" data-tu-c value="20">' +
      "      </label>" +
      '      <label class="travel-utils__label">°F' +
      '        <input type="number" step="any" class="travel-utils__input" data-tu-f value="68">' +
      "      </label>" +
      "    </div>" +
      "  </fieldset>" +
      '  <fieldset class="travel-utils__fieldset">' +
      '    <legend data-i18n="travelUtils.distance">Distance</legend>' +
      '    <div class="travel-utils__row2">' +
      '      <label class="travel-utils__label">km' +
      '        <input type="number" min="0" step="any" class="travel-utils__input" data-tu-km value="10">' +
      "      </label>" +
      '      <label class="travel-utils__label">mile' +
      '        <input type="number" min="0" step="any" class="travel-utils__input" data-tu-mi value="6.21">' +
      "      </label>" +
      "    </div>" +
      "  </fieldset>" +
      "</div>";

    var cEl = body.querySelector("[data-tu-c]");
    var fEl = body.querySelector("[data-tu-f]");
    var kmEl = body.querySelector("[data-tu-km]");
    var miEl = body.querySelector("[data-tu-mi]");
    var lock = false;

    function setPair(a, b, fn) {
      if (lock) return;
      lock = true;
      var v = parseFloat(a.value, 10);
      if (isFinite(v)) b.value = String(Math.round(fn(v) * 100) / 100);
      lock = false;
    }

    cEl.addEventListener("input", function () {
      setPair(cEl, fEl, function (c) {
        return c * 1.8 + 32;
      });
    });
    fEl.addEventListener("input", function () {
      setPair(fEl, cEl, function (f) {
        return (f - 32) / 1.8;
      });
    });
    kmEl.addEventListener("input", function () {
      setPair(kmEl, miEl, function (km) {
        return km / 1.609344;
      });
    });
    miEl.addEventListener("input", function () {
      setPair(miEl, kmEl, function (mi) {
        return mi * 1.609344;
      });
    });
  }

  function boot() {
    ensureCss();
    loadState();
    // Always start collapsed so content stays clear; remember last tool only.
    state.open = false;
    state.view = "menu";
    buildRoot();
    applyI18n(document.getElementById(ROOT_ID));
    syncUi();
  }

  document.addEventListener("guide:langchange", function () {
    var root = document.getElementById(ROOT_ID);
    if (!root) return;
    applyI18n(root);
    if (state.open) renderBody();
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
