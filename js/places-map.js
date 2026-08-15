/**
 * Immersive Korea peninsula places map (Leaflet + Esri satellite).
 * Full-viewport "Earth-like" screen: markers from PLACES_COORDS, copy from i18n.
 * "자세히 보기" expands the panel in place (no navigation to place HTML).
 */
(function () {
  var KOREA_CENTER = [36.4, 127.8];
  var KOREA_ZOOM = 7;
  var FOCUS_ZOOM = 14;
  var KOREA_BOUNDS = L.latLngBounds([33.0, 124.5], [39.0, 132.0]);

  var REGION_VIEWS = {
    all: { center: KOREA_CENTER, zoom: KOREA_ZOOM },
    seoul: { center: [37.55, 126.99], zoom: 11 },
    gyeonggi: { center: [37.55, 127.2], zoom: 9 },
    incheon: { center: [37.45, 126.7], zoom: 10 },
    gangwon: { center: [37.85, 128.2], zoom: 8 },
    busan: { center: [35.15, 129.08], zoom: 11 },
    gyeongju: { center: [35.84, 129.22], zoom: 11 },
    jeolla: { center: [35.82, 127.15], zoom: 10 },
    jeju: { center: [33.38, 126.55], zoom: 9 },
    gyeongsang: { center: [35.5, 128.7], zoom: 8 },
  };

  var map = null;
  var markersBySlug = {};
  var placeMeta = {};
  var activeSlug = null;
  var activeRegion = "all";
  var drawerOpen = false;
  var detailOpen = false;
  var userLocMarker = null;
  var userAccCircle = null;
  var locateBusy = false;
  var locateToastTimer = null;
  var TYPE_FILTER_KEY = "korea-guide-places-type-filters";
  var DEFAULT_TYPES = {
    city: true,
    nature: true,
    heritage: true,
    airport: true,
    info: true,
    locker: true,
    port: true,
    "bus-terminal": true,
  };
  var activeTypes = Object.assign({}, DEFAULT_TYPES);
  // Metro overlay: off by default so the peninsula map stays uncluttered.
  var DEFAULT_METRO = {
    metro: false,
    metroLines: true,
    metroStations: true,
  };
  var activeMetro = Object.assign({}, DEFAULT_METRO);
  var METRO_LINE_IDS = [
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "arex",
    "gyeongui",
    "suin-bundang",
    "shinbundang",
    "sillim",
    "busan-1",
    "busan-2",
    "busan-3",
    "busan-4",
    "busan-gimhae",
    "daegu-1",
    "daegu-2",
    "daegu-3",
    "gwangju-1",
    "daejeon-1",
  ];
  var METRO_COLORS = {
    "1": "#0052A4",
    "2": "#00A84D",
    "3": "#EF7C1C",
    "4": "#00A5E3",
    "5": "#996CAC",
    "6": "#CD7C2F",
    "7": "#747F00",
    "8": "#E35D4D",
    "9": "#B7A45C",
    arex: "#0090D2",
    gyeongui: "#77C4A3",
    "suin-bundang": "#F5A200",
    shinbundang: "#D31145",
    sillim: "#6789CA",
    "busan-1": "#F06A00",
    "busan-2": "#3CB44A",
    "busan-3": "#BB8C00",
    "busan-4": "#2178C4",
    "busan-gimhae": "#8FC31F",
    "daegu-1": "#D93F0C",
    "daegu-2": "#00AA80",
    "daegu-3": "#FFB100",
    "gwangju-1": "#009088",
    "daejeon-1": "#007448",
  };
  var METRO_LINE_FILTER_KEY = "korea-guide-places-metro-line-filters";
  var activeMetroLines = {};
  METRO_LINE_IDS.forEach(function (id) {
    activeMetroLines[id] = true;
  });
  var metroLineGroups = {}; // lineId -> L.layerGroup (casing + stroke)
  var metroLineLayer = null;
  var metroStationLayer = null;
  var metroStationGeo = null;
  var metroLoadState = "idle"; // idle | loading | ready | error
  var metroCanvasRenderer = null;
  var metroZoomBound = false;
  var metroAutoFocused = false;
  var FILTER_OPEN_KEY = "korea-guide-places-filter-open";
  var FILTER_ACCORDION_KEY = "korea-guide-places-filter-accordion";
  var FILTER_GROUPS = {
    places: { types: ["city", "nature", "heritage"], metro: false },
    transit: {
      types: ["airport", "bus-terminal", "port"],
      metro: true,
    },
    convenience: { types: ["locker", "info"], metro: false },
  };
  var reduceMotion =
    window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function t(key, fallback) {
    try {
      if (window.GuideI18n && typeof window.GuideI18n.t === "function") {
        return window.GuideI18n.t(key, fallback || key);
      }
      if (window.GuideI18n && typeof window.GuideI18n.lookupWithFallback === "function") {
        var via = window.GuideI18n.lookupWithFallback(
          key,
          window.GuideI18n.getLang && window.GuideI18n.getLang()
        );
        if (via != null && via !== "") return String(via);
      }
    } catch (e) {}
    return fallback || key;
  }

  function placeField(slug, field) {
    return t("places." + slug + "." + field, "");
  }

  function placeHasBody(slug) {
    try {
      var lang =
        (window.GuideI18n && window.GuideI18n.getLang && window.GuideI18n.getLang()) ||
        "ko";
      if (window.GuideContentBody && typeof window.GuideContentBody.getBody === "function") {
        var blocks = window.GuideContentBody.getBody("places." + slug + ".body", lang);
        return !!(blocks && blocks.length);
      }
      var pack =
        (window.__I18N_MESSAGES__ && window.__I18N_MESSAGES__[lang]) ||
        (window.__I18N_MESSAGES__ && window.__I18N_MESSAGES__.ko) ||
        null;
      var body = pack && pack.places && pack.places[slug] && pack.places[slug].body;
      return Array.isArray(body) && body.length > 0;
    } catch (e) {
      return false;
    }
  }

  function el(sel) {
    return document.querySelector(sel);
  }

  function fly(latlng, zoom, duration) {
    if (!map) return;
    if (reduceMotion) {
      map.setView(latlng, zoom);
      return;
    }
    map.flyTo(latlng, zoom, {
      duration: duration != null ? duration : 1.35,
      easeLinearity: 0.2,
    });
  }

  function setMarkerActive(slug) {
    Object.keys(markersBySlug).forEach(function (s) {
      var m = markersBySlug[s];
      var iconEl = m.getElement && m.getElement();
      if (iconEl) {
        iconEl.classList.toggle("is-active", s === slug);
      }
    });
  }

  function applyRegionFilter(region) {
    activeRegion = region || "all";
    applyVisibilityFilters();

    document.querySelectorAll("[data-places-region]").forEach(function (btn) {
      var on = btn.getAttribute("data-places-region") === activeRegion;
      btn.classList.toggle("is-active", on);
      btn.setAttribute("aria-pressed", on ? "true" : "false");
    });
  }

  function healMetroSubFlags() {
    // Master ON always implies both overlays — never leave a blank "지하철" check.
    if (activeMetro.metro) {
      activeMetro.metroLines = true;
      activeMetro.metroStations = true;
    }
  }

  function healMetroLineFilters() {
    var anyOn = METRO_LINE_IDS.some(function (id) {
      return !!activeMetroLines[id];
    });
    if (!anyOn) {
      METRO_LINE_IDS.forEach(function (id) {
        activeMetroLines[id] = true;
      });
    }
  }

  function loadMetroLineFilters() {
    try {
      var raw = window.localStorage && localStorage.getItem(METRO_LINE_FILTER_KEY);
      if (!raw) return;
      var parsed = JSON.parse(raw);
      if (!parsed || typeof parsed !== "object") return;
      METRO_LINE_IDS.forEach(function (id) {
        if (typeof parsed[id] === "boolean") activeMetroLines[id] = parsed[id];
      });
      healMetroLineFilters();
    } catch (e) {}
  }

  function saveMetroLineFilters() {
    try {
      if (window.localStorage) {
        localStorage.setItem(METRO_LINE_FILTER_KEY, JSON.stringify(activeMetroLines));
      }
    } catch (e) {}
  }

  function stationMatchesLineFilter(props) {
    var lines = String((props && props.lines) || "")
      .split(",")
      .map(function (s) {
        return s.trim();
      })
      .filter(Boolean);
    if (!lines.length) return false;
    return lines.some(function (ln) {
      return !!activeMetroLines[ln];
    });
  }

  function isMetroLineEnabled(lineId) {
    return !!activeMetroLines[lineId];
  }

  function applyMetroLineIdVisibility() {
    if (!metroLineLayer) return;
    METRO_LINE_IDS.forEach(function (lineId) {
      var group = metroLineGroups[lineId];
      if (!group) return;
      var on = isMetroLineEnabled(lineId);
      if (on) {
        if (!metroLineLayer.hasLayer(group)) group.addTo(metroLineLayer);
      } else if (metroLineLayer.hasLayer(group)) {
        metroLineLayer.removeLayer(group);
      }
    });
  }

  function syncMetroLineFilterUi() {
    document.querySelectorAll("[data-places-metro-line]").forEach(function (input) {
      var id = input.getAttribute("data-places-metro-line");
      if (!id || !METRO_LINE_IDS.includes(id)) return;
      input.checked = !!activeMetroLines[id];
    });
  }

  function loadTypeFilters() {
    try {
      var raw = window.localStorage && localStorage.getItem(TYPE_FILTER_KEY);
      if (!raw) return;
      var parsed = JSON.parse(raw);
      if (!parsed || typeof parsed !== "object") return;
      Object.keys(DEFAULT_TYPES).forEach(function (k) {
        if (typeof parsed[k] === "boolean") activeTypes[k] = parsed[k];
      });
      Object.keys(DEFAULT_METRO).forEach(function (k) {
        if (typeof parsed[k] === "boolean") activeMetro[k] = parsed[k];
      });
      healMetroSubFlags();
      // Persist healed flags so poisoned LS (metro on, both children off) cannot stick.
      try {
        if (window.localStorage) {
          localStorage.setItem(
            TYPE_FILTER_KEY,
            JSON.stringify(Object.assign({}, activeTypes, activeMetro))
          );
        }
      } catch (eSave) {}
    } catch (e) {}
    loadMetroLineFilters();
  }

  function saveTypeFilters() {
    try {
      if (window.localStorage) {
        var payload = Object.assign({}, activeTypes, activeMetro);
        localStorage.setItem(TYPE_FILTER_KEY, JSON.stringify(payload));
      }
    } catch (e) {}
  }

  function syncTypeFilterUi() {
    document.querySelectorAll("[data-places-type-filter]").forEach(function (input) {
      var type = input.getAttribute("data-places-type-filter");
      if (!type) return;
      input.checked = !!activeTypes[type];
    });
    syncMetroFilterUi();
    syncGroupFilterUi();
  }

  function syncMetroFilterUi() {
    document.querySelectorAll("[data-places-metro-filter]").forEach(function (input) {
      var key = input.getAttribute("data-places-metro-filter");
      if (!key || !DEFAULT_METRO.hasOwnProperty(key)) return;
      input.checked = !!activeMetro[key];
    });
    document.querySelectorAll("[data-places-metro-sub]").forEach(function (el) {
      el.hidden = !activeMetro.metro;
    });
    syncMetroLineFilterUi();
  }

  function setAccordionOpen(groupEl, open, persist) {
    if (!groupEl) return;
    var id = groupEl.getAttribute("data-places-filter-accordion");
    var btn = groupEl.querySelector("[data-places-accordion-toggle]");
    var panel = btn && btn.getAttribute("aria-controls")
      ? document.getElementById(btn.getAttribute("aria-controls"))
      : groupEl.querySelector(".places-map-legend__list");
    groupEl.classList.toggle("is-open", !!open);
    if (btn) btn.setAttribute("aria-expanded", open ? "true" : "false");
    if (panel) panel.hidden = !open;
    if (persist !== false && id) {
      try {
        var raw = (window.localStorage && localStorage.getItem(FILTER_ACCORDION_KEY)) || "{}";
        var state = JSON.parse(raw);
        if (!state || typeof state !== "object") state = {};
        state[id] = !!open;
        if (window.localStorage) {
          localStorage.setItem(FILTER_ACCORDION_KEY, JSON.stringify(state));
        }
      } catch (e) {}
    }
  }

  function loadAccordionState() {
    var state = {};
    try {
      var raw = window.localStorage && localStorage.getItem(FILTER_ACCORDION_KEY);
      if (raw) state = JSON.parse(raw) || {};
    } catch (e) {
      state = {};
    }
    document.querySelectorAll("[data-places-filter-accordion]").forEach(function (groupEl) {
      var id = groupEl.getAttribute("data-places-filter-accordion");
      var open =
        state && typeof state[id] === "boolean"
          ? state[id]
          : id === "places";
      setAccordionOpen(groupEl, open, false);
    });
  }

  function bindAccordionUi() {
    document.querySelectorAll("[data-places-accordion-toggle]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var groupEl = btn.closest("[data-places-filter-accordion]");
        if (!groupEl) return;
        var open = !groupEl.classList.contains("is-open");
        setAccordionOpen(groupEl, open, true);
      });
    });
  }

  function groupFilterState(groupId) {
    var cfg = FILTER_GROUPS[groupId];
    if (!cfg) return { all: false, some: false };
    var on = 0;
    var total = cfg.types.length + (cfg.metro ? 1 : 0);
    cfg.types.forEach(function (t) {
      if (activeTypes[t]) on += 1;
    });
    if (cfg.metro && activeMetro.metro) on += 1;
    return { all: on === total && total > 0, some: on > 0 && on < total, on: on, total: total };
  }

  function syncGroupFilterUi() {
    document.querySelectorAll("[data-places-group-filter]").forEach(function (input) {
      var id = input.getAttribute("data-places-group-filter");
      var st = groupFilterState(id);
      input.checked = st.all;
      input.indeterminate = st.some;
    });
  }

  function setGroupFilters(groupId, on) {
    var cfg = FILTER_GROUPS[groupId];
    if (!cfg) return;
    cfg.types.forEach(function (t) {
      if (DEFAULT_TYPES.hasOwnProperty(t)) activeTypes[t] = !!on;
    });
    if (cfg.metro) {
      var turningMetroOn = !!on && !activeMetro.metro;
      activeMetro.metro = !!on;
      if (activeMetro.metro) {
        activeMetro.metroLines = true;
        activeMetro.metroStations = true;
        if (metroLoadState === "error") metroLoadState = "idle";
      }
      syncMetroFilterUi();
      applyMetroVisibility();
      if (turningMetroOn) focusMetroIfNeeded();
    }
    // Keep at least one place type visible overall
    var anyOn = Object.keys(activeTypes).some(function (k) {
      return activeTypes[k];
    });
    if (!anyOn && cfg.types.length) {
      activeTypes[cfg.types[0]] = true;
    }
    syncTypeFilterUi();
    syncGroupFilterUi();
    saveTypeFilters();
    applyVisibilityFilters();
  }

  function bindGroupFilterUi() {
    document.querySelectorAll("[data-places-group-filter]").forEach(function (input) {
      input.addEventListener("change", function () {
        var id = input.getAttribute("data-places-group-filter");
        setGroupFilters(id, !!input.checked);
      });
    });
  }

  function metroDataCandidates() {
    // Never use SITE_CONFIG.SITE_ORIGIN here — that is the production canonical host.
    // Local live-server / content-admin would cross-fetch prod, where stations.geojson
    // may 404 (file not deployed), and wrong bases 404 every line file.
    var out = [];
    var seen = {};
    function add(url) {
      if (!url) return;
      var u = String(url);
      if (!/\/$/.test(u)) u += "/";
      if (seen[u]) return;
      seen[u] = true;
      out.push(u);
    }
    try {
      var scripts = document.getElementsByTagName("script");
      for (var i = scripts.length - 1; i >= 0; i--) {
        var src = scripts[i].src || "";
        if (src.indexOf("places-map.js") === -1) continue;
        var fromScript = src.replace(/\/js\/[^/?#]*.*$/, "/data/metro/");
        // Only accept if /js/… was actually rewritten (else fetch would hit .js?v=…stations.geojson).
        if (fromScript !== src && /\/data\/metro\/$/i.test(fromScript)) add(fromScript);
        break;
      }
    } catch (e1) {}
    try {
      add(new URL("../../data/metro/", window.location.href).href);
    } catch (e2) {
      add("../../data/metro/");
    }
    try {
      if (window.location && /^https?:/i.test(window.location.origin || "")) {
        add(String(window.location.origin).replace(/\/$/, "") + "/data/metro/");
      }
    } catch (e3) {}
    return out;
  }

  function metroDataBase() {
    return metroDataCandidates()[0] || "../../data/metro/";
  }

  function probeMetroBase(base) {
    // Prefer a tracked line file so probe works even if stations.geojson is missing.
    var url = base + "line-2.geojson";
    return fetch(url, { cache: "no-store" })
      .then(function (res) {
        if (!res.ok) throw new Error(String(res.status));
        return res.json();
      })
      .then(function (geo) {
        if (!geo || !geo.features) throw new Error("bad-geo");
        return base;
      });
  }

  function resolveMetroBase() {
    var list = metroDataCandidates();
    var chain = Promise.reject(new Error("no-base"));
    list.forEach(function (base) {
      chain = chain.catch(function () {
        return probeMetroBase(base).catch(function (err) {
          try {
            console.warn("[places-map] metro base failed", base, err && err.message);
          } catch (eLog) {}
          throw err;
        });
      });
    });
    return chain.catch(function () {
      return list[0] || "../../data/metro/";
    });
  }

  function fetchMetroJson(url) {
    return fetch(url, { cache: "no-store" }).then(function (res) {
      if (!res.ok) {
        var err = new Error(String(res.status));
        err.status = res.status;
        err.url = url;
        throw err;
      }
      return res.json().then(function (geo) {
        if (!geo || typeof geo !== "object") {
          var bad = new Error("invalid-json");
          bad.url = url;
          throw bad;
        }
        return geo;
      });
    });
  }

  function setMetroHint(kind, detail) {
    var hint = el("[data-places-hint]");
    if (!hint) return;
    if (locateToastTimer) {
      clearTimeout(locateToastTimer);
      locateToastTimer = null;
    }
    hint.classList.remove(
      "is-metro-toast",
      "is-metro-loading",
      "is-metro-ready",
      "is-metro-error",
      "is-locate-toast",
      "is-locate-loading",
      "is-locate-error"
    );
    if (kind === "error") {
      hint.textContent =
        (detail && String(detail)) ||
        t(
          "transport.metroLoadError",
          "지하철 불러오기 실패 — 로컬 서버로 열거나 새로고침 후 다시 시도하세요."
        );
      hint.classList.add("is-metro-toast", "is-metro-error");
      hint.hidden = false;
      return;
    }
    if (kind === "loading") {
      hint.textContent = t("transport.metroLoading", "지하철 불러오는 중…");
      hint.classList.add("is-metro-toast", "is-metro-loading");
      hint.hidden = false;
      return;
    }
    if (kind === "ready") {
      var lines = detail && detail.lines != null ? detail.lines : null;
      var stations = detail && detail.stations != null ? detail.stations : null;
      var parts = [];
      if (lines != null) parts.push(lines + t("transport.metroCountLines", "개 노선"));
      if (stations != null) parts.push(stations + t("transport.metroCountStations", "개 역"));
      hint.textContent = parts.length
        ? t("transport.metroReadyCount", "지하철 표시 중 — ") + parts.join(" · ")
        : t(
            "transport.metroReady",
            "서울·수도권 지하철 노선·역이 표시됩니다."
          );
      hint.classList.add("is-metro-toast", "is-metro-ready");
      hint.hidden = false;
      return;
    }
    // Clear metro toast styling when returning to default help copy.
    if (kind === "clear") {
      hint.classList.remove(
        "is-metro-toast",
        "is-metro-loading",
        "is-metro-ready",
        "is-metro-error"
      );
    }
  }

  function focusMetroIfNeeded() {
    if (!map || !activeMetro.metro || metroAutoFocused) return;
    // Peninsula zoom makes the Seoul network a speck on Esri satellite —
    // jump to Seoul once so lines/stations are actually visible.
    if (map.getZoom() < 11) {
      metroAutoFocused = true;
      focusRegion("seoul");
    } else {
      metroAutoFocused = true;
    }
  }

  function ensureMetroStationPane() {
    if (!map || map.getPane("metroStations")) return;
    map.createPane("metroStations");
    // Above line canvas (overlay 400), below sightseeing DivIcon markers (600).
    map.getPane("metroStations").style.zIndex = 550;
    map.getPane("metroStations").style.pointerEvents = "auto";
  }

  function stationPrimaryColor(props) {
    var lines = String((props && props.lines) || "")
      .split(",")
      .map(function (s) {
        return s.trim();
      })
      .filter(Boolean);
    for (var i = 0; i < lines.length; i++) {
      if (activeMetroLines[lines[i]] && METRO_COLORS[lines[i]]) {
        return METRO_COLORS[lines[i]];
      }
    }
    var raw = lines[0] || "";
    return METRO_COLORS[raw] || "#1a1a1a";
  }

  function stationIsMajor(props) {
    props = props || {};
    if (props.major === true || props.source === "curated") return true;
    var lines = String(props.lines || "")
      .split(",")
      .map(function (s) {
        return s.trim();
      })
      .filter(Boolean);
    return lines.length > 1;
  }

  function metroStationSvg(glyphPx) {
    var g = glyphPx != null ? glyphPx : 11;
    // Compact subway/train glyph — line color via currentColor on the badge.
    return (
      '<svg class="places-metro-station__glyph" viewBox="0 0 24 24" width="' +
      g +
      '" height="' +
      g +
      '" focusable="false" aria-hidden="true">' +
      '<path fill="currentColor" d="M12 2C7.6 2 4 4.1 4 8.5V16c0 1.7 1.3 3 3 3l-1 1.2V21h2.2l1.5-1.8h5.6L16.8 21H19v-.8L18 19c1.7 0 3-1.3 3-3V8.5C21 4.1 16.4 2 12 2zm-3.2 14.2c-.7 0-1.3-.6-1.3-1.3s.6-1.3 1.3-1.3 1.3.6 1.3 1.3-.6 1.3-1.3 1.3zm6.4 0c-.7 0-1.3-.6-1.3-1.3s.6-1.3 1.3-1.3 1.3.6 1.3 1.3-.6 1.3-1.3 1.3zM7.2 11.2V7.8h9.6v3.4H7.2z"/>' +
      "</svg>"
    );
  }

  function stationDivIcon(props, zoom) {
    var color = stationPrimaryColor(props);
    var major = stationIsMajor(props);
    var z = zoom != null ? zoom : (map && map.getZoom()) || 11;
    // Non-transfer stations were tiny circleMarkers (r≈3–5); bump toward hub size
    // while keeping majors slightly larger for hierarchy.
    var size =
      z >= 13 ? (major ? 22 : 18) : z >= 11 ? (major ? 20 : 16) : major ? 17 : 14;
    var glyph = major ? (z >= 13 ? 13 : 12) : z >= 13 ? 11 : 10;
    var pad = 2;
    var box = size + pad;
    return L.divIcon({
      className: "places-metro-station" + (major ? " is-major" : ""),
      html:
        '<span class="places-metro-station__badge" style="width:' +
        size +
        "px;height:" +
        size +
        "px;border-color:" +
        color +
        ";color:" +
        color +
        '">' +
        metroStationSvg(glyph) +
        "</span>",
      iconSize: [box, box],
      iconAnchor: [box / 2, box / 2],
    });
  }

  function stationHasName(props) {
    props = props || {};
    return !!(
      String(props.name || "").trim() ||
      String(props.name_en || "").trim() ||
      String(props.name_ja || "").trim() ||
      String(props.name_zh || "").trim() ||
      String(props.name_han || "").trim() ||
      String(props.name_vi || "").trim() ||
      String(props.name_th || "").trim() ||
      String(props.name_ru || "").trim()
    );
  }

  function stationNameLooksKorean(s) {
    return /[\uac00-\ud7a3]/.test(String(s || ""));
  }

  function stationPickField(props, key) {
    var v = String((props && props[key]) || "").trim();
    if (!v || stationNameLooksKorean(v)) return "";
    return v;
  }

  function stationPickLatin(props) {
    return stationPickField(props, "name_en");
  }

  function stationPickCjk(props, preferSimplified) {
    props = props || {};
    var zh = stationPickField(props, "name_zh");
    var han = stationPickField(props, "name_han");
    if (preferSimplified) return zh || han || "";
    return han || zh || "";
  }

  function stationVisibleAtZoom(props, zoom, index) {
    // Only real named stations are kept in metroStationGeo; never show
    // anonymous line-sample dots as if they were stations.
    if (!stationHasName(props)) return false;
    // Seoul city zoom and closer: show every named station.
    if (zoom >= 11) return true;
    if (stationIsMajor(props)) return true;
    if (zoom >= 9) return index % 2 === 0;
    // Peninsula / far zoom: lines + transfer/tourist majors only.
    return false;
  }

  function simplifyCoords(coords, minDistDeg) {
    if (!coords || coords.length < 3) return coords;
    var out = [coords[0]];
    var last = coords[0];
    var minD = minDistDeg != null ? minDistDeg : 0.0012;
    for (var i = 1; i < coords.length - 1; i++) {
      var c = coords[i];
      var dx = c[0] - last[0];
      var dy = c[1] - last[1];
      if (dx * dx + dy * dy >= minD * minD) {
        out.push(c);
        last = c;
      }
    }
    out.push(coords[coords.length - 1]);
    return out.length >= 2 ? out : coords;
  }

  function simplifyGeo(geo, minDistDeg) {
    if (!geo || !geo.features) return geo;
    return {
      type: "FeatureCollection",
      features: geo.features
        .map(function (f) {
          if (!f || !f.geometry) return null;
          var g = f.geometry;
          if (g.type === "LineString") {
            return {
              type: "Feature",
              properties: f.properties || {},
              geometry: {
                type: "LineString",
                coordinates: simplifyCoords(g.coordinates, minDistDeg),
              },
            };
          }
          if (g.type === "MultiLineString") {
            return {
              type: "Feature",
              properties: f.properties || {},
              geometry: {
                type: "MultiLineString",
                coordinates: g.coordinates.map(function (line) {
                  return simplifyCoords(line, minDistDeg);
                }),
              },
            };
          }
          return f;
        })
        .filter(Boolean),
    };
  }

  function stationLabel(props) {
    props = props || {};
    var ko = String(props.name || "").trim();
    var en = stationPickLatin(props);
    var lang =
      (window.GuideI18n && window.GuideI18n.getLang && window.GuideI18n.getLang()) ||
      "ko";
    if (lang === "ko") return ko || en || "";
    if (lang === "ja") {
      return stationPickField(props, "name_ja") || en || ko || "";
    }
    if (lang === "zh-Hant") {
      return stationPickCjk(props, false) || en || ko || "";
    }
    if (lang === "zh") {
      return stationPickCjk(props, true) || en || ko || "";
    }
    if (lang === "vi") {
      return stationPickField(props, "name_vi") || en || ko || "";
    }
    if (lang === "th") {
      return stationPickField(props, "name_th") || en || ko || "";
    }
    if (lang === "ru") {
      return stationPickField(props, "name_ru") || en || ko || "";
    }
    // en (and any unknown lang)
    return en || ko || "";
  }

  function refreshMetroStationLabels() {
    if (!metroStationGeo || !metroStationLayer) return;
    rebuildMetroStationLayer();
  }

  function metroLineWeightForZoom(zoom) {
    // Readable on Esri World Imagery at Seoul zoom, without heavy strokes.
    if (zoom >= 13) return 6.5;
    if (zoom >= 11) return 5.5;
    if (zoom >= 9) return 4.5;
    return 3.5;
  }

  function metroLineCasingWeight(zoom) {
    return metroLineWeightForZoom(zoom) + 2.5;
  }

  function applyMetroLineZoomStyle() {
    if (!metroLineLayer || !map) return;
    var z = map.getZoom();
    var w = metroLineWeightForZoom(z);
    var cw = metroLineCasingWeight(z);
    metroLineLayer.eachLayer(function (layer) {
      var role = layer && layer.options && layer.options.metroRole;
      var style =
        role === "casing"
          ? { weight: cw, opacity: 0.92, color: "#ffffff" }
          : { weight: w, opacity: 1 };
      if (layer.setStyle) {
        layer.setStyle(style);
      } else if (layer.eachLayer) {
        layer.eachLayer(function (sub) {
          if (!sub.setStyle) return;
          var subRole = sub.options && sub.options.metroRole;
          sub.setStyle(
            subRole === "casing"
              ? { weight: cw, opacity: 0.92, color: "#ffffff" }
              : { weight: w, opacity: 1 }
          );
        });
      }
    });
  }

  function namedStationGeo(geo) {
    if (!geo || !geo.features) return geo;
    return {
      type: "FeatureCollection",
      properties: geo.properties || {},
      features: geo.features.filter(function (f) {
        return stationHasName((f && f.properties) || {});
      }),
    };
  }

  function bindStationTooltip(marker, label) {
    if (!label) return;
    marker.bindTooltip(label, {
      direction: "top",
      offset: [0, -8],
      opacity: 0.96,
      className: "places-metro-tooltip",
    });
    marker.on("click", function (ev) {
      if (ev && ev.originalEvent) {
        L.DomEvent.stopPropagation(ev.originalEvent);
      }
      marker.openTooltip();
    });
  }

  function buildStationMarkers(geo) {
    ensureMetroStationPane();
    var zoom = (map && map.getZoom()) || 11;
    // All named stations use metro DivIcons (line-color accent + subway glyph)
    // so non-transfer stops stay readable on satellite — not plain dots.
    return L.geoJSON(geo, {
      filter: function (feature) {
        return stationHasName((feature && feature.properties) || {});
      },
      pointToLayer: function (feature, latlng) {
        var props = feature.properties || {};
        var label = stationLabel(props);
        var marker = L.marker(latlng, {
          pane: "metroStations",
          icon: stationDivIcon(props, zoom),
          keyboard: false,
          interactive: true,
          riseOnHover: true,
          title: label || "",
        });

        marker.feature = feature;
        bindStationTooltip(marker, label);
        return marker;
      },
    });
  }

  function filterStationsForZoom(geo, zoom) {
    if (!geo || !geo.features) return geo;
    return {
      type: "FeatureCollection",
      features: geo.features.filter(function (f, i) {
        var props = f.properties || {};
        if (!stationMatchesLineFilter(props)) return false;
        return stationVisibleAtZoom(props, zoom, i);
      }),
    };
  }

  function rebuildMetroStationLayer() {
    if (!metroStationLayer || !metroStationGeo) return false;
    var zoom = (map && map.getZoom()) || 11;
    metroStationLayer.clearLayers();
    var filtered = filterStationsForZoom(metroStationGeo, zoom);
    if (!filtered.features.length) return false;
    buildStationMarkers(filtered).addTo(metroStationLayer);
    return true;
  }

  function stationLayerHasMarkers() {
    return !!(
      metroStationLayer &&
      metroStationLayer.getLayers().some(function (layer) {
        return layer.getLayers ? layer.getLayers().length > 0 : true;
      })
    );
  }

  function bindMetroZoomHandlers() {
    if (!map || metroZoomBound) return;
    metroZoomBound = true;
    map.on("zoomend", function () {
      if (!activeMetro.metro) return;
      applyMetroLineZoomStyle();
      if (activeMetro.metroStations && metroStationGeo) {
        rebuildMetroStationLayer();
      }
    });
  }

  function countStationMarkers() {
    var n = 0;
    if (!metroStationLayer) return 0;
    metroStationLayer.eachLayer(function (layer) {
      if (layer.getLayers) n += layer.getLayers().length;
      else n += 1;
    });
    return n;
  }

  function countMetroLineOverlays() {
    var n = 0;
    METRO_LINE_IDS.forEach(function (id) {
      if (!isMetroLineEnabled(id)) return;
      if (metroLineGroups[id]) n += 1;
    });
    return n;
  }

  function embeddedLineGeo(lineId) {
    try {
      var pack = window.METRO_LINE_DATA;
      if (pack && pack[lineId]) return pack[lineId];
    } catch (e) {}
    return null;
  }

  function embeddedStationGeo() {
    try {
      if (window.METRO_STATION_DATA && window.METRO_STATION_DATA.features) {
        return window.METRO_STATION_DATA;
      }
    } catch (e) {}
    return null;
  }

  function fetchLineGeo(base, lineId) {
    var url = base + "line-" + lineId + ".geojson";
    return fetchMetroJson(url).catch(function (err) {
      try {
        console.warn(
          "[places-map] line fetch failed",
          (err && err.url) || url,
          (err && err.status) || (err && err.message) || err
        );
      } catch (eLog) {}
      var emb = embeddedLineGeo(lineId);
      if (emb) return emb;
      throw err || new Error("line-" + lineId);
    });
  }

  function loadMetroStations(base) {
    var url = base + "stations.geojson";
    return fetchMetroJson(url)
      .catch(function (err) {
        try {
          console.warn(
            "[places-map] stations fetch failed",
            (err && err.url) || url,
            (err && err.status) || (err && err.message) || err
          );
        } catch (eLog) {}
        var emb = embeddedStationGeo();
        if (emb) return emb;
        throw err || new Error("stations");
      })
      .then(function (geo) {
        if (!geo || !geo.features || !geo.features.length) return false;
        // Drop derived line-sample points (empty name) — only real stations.
        metroStationGeo = namedStationGeo(geo);
        if (!metroStationGeo.features.length) return false;
        if (!metroStationLayer) metroStationLayer = L.layerGroup();
        rebuildMetroStationLayer();
        return stationLayerHasMarkers();
      })
      .catch(function () {
        return false;
      });
  }

  function ensureMetroLayers() {
    if (!map || typeof L === "undefined") return Promise.resolve(false);
    if (metroLoadState === "ready") {
      // Lines may have loaded while stations 404'd earlier — retry once if empty.
      if (activeMetro.metroStations && !stationLayerHasMarkers() && !metroStationGeo) {
        return resolveMetroBase()
          .then(function (base) {
            return loadMetroStations(base);
          })
          .then(function () {
            return true;
          });
      }
      return Promise.resolve(true);
    }
    if (metroLoadState === "loading") {
      return new Promise(function (resolve) {
        var tries = 0;
        var timer = setInterval(function () {
          tries += 1;
          if (metroLoadState === "ready") {
            clearInterval(timer);
            resolve(true);
          } else if (metroLoadState === "error") {
            clearInterval(timer);
            resolve(false);
          } else if (tries > 300) {
            // Still loading after ~30s — do not treat as hard failure (avoids false error toast).
            clearInterval(timer);
            resolve(false);
          }
        }, 100);
      });
    }

    metroLoadState = "loading";
    setMetroHint("loading");
    ensureMetroStationPane();
    bindMetroZoomHandlers();
    if (!metroCanvasRenderer) {
      metroCanvasRenderer = L.canvas({ padding: 0.5 });
    }
    if (!metroLineLayer) {
      metroLineLayer = L.layerGroup();
    } else {
      metroLineLayer.clearLayers();
    }
    metroLineGroups = {};
    if (!metroStationLayer) {
      metroStationLayer = L.layerGroup();
    } else {
      metroStationLayer.clearLayers();
    }

    return resolveMetroBase()
      .then(function (base) {
        try {
          console.info("[places-map] metro data base", base);
        } catch (eInfo) {}
        var z0 = map.getZoom();
        // Mild simplify — keep shape readable on satellite.
        var lineSimplify = z0 < 10 ? 0.0016 : 0.0009;
        var lineJobs = METRO_LINE_IDS.map(function (lineId) {
          return fetchLineGeo(base, lineId)
            .then(function (geo) {
              var simplified = simplifyGeo(geo, lineSimplify);
              var color = METRO_COLORS[lineId] || "#888";
              var group = L.layerGroup();
              group.options = group.options || {};
              group.options.metroLineId = lineId;
              // White casing understroke so colored lines pop on Esri imagery.
              L.geoJSON(simplified, {
                renderer: metroCanvasRenderer,
                metroRole: "casing",
                metroLineId: lineId,
                style: {
                  color: "#ffffff",
                  weight: metroLineCasingWeight(z0),
                  opacity: 0.95,
                  lineCap: "round",
                  lineJoin: "round",
                },
                interactive: false,
              }).addTo(group);
              L.geoJSON(simplified, {
                renderer: metroCanvasRenderer,
                metroRole: "stroke",
                metroLineId: lineId,
                style: {
                  color: color,
                  weight: metroLineWeightForZoom(z0),
                  opacity: 1,
                  lineCap: "round",
                  lineJoin: "round",
                },
                interactive: false,
              }).addTo(group);
              metroLineGroups[lineId] = group;
              if (isMetroLineEnabled(lineId)) group.addTo(metroLineLayer);
              return true;
            })
            .catch(function () {
              return null;
            });
        });

        return Promise.all(lineJobs.concat([loadMetroStations(base)]));
      })
      .then(function () {
        var hasLines = metroLineLayer && metroLineLayer.getLayers().length > 0;
        var hasStations = !!metroStationGeo || stationLayerHasMarkers();
        if (!hasLines && !hasStations) {
          metroLoadState = "error";
          var isFile =
            typeof window !== "undefined" &&
            window.location &&
            String(window.location.protocol).indexOf("file") === 0;
          setMetroHint(
            "error",
            isFile
              ? t(
                  "transport.metroFileProtocolError",
                  "지하철 불러오기 실패 — HTML을 직접 열면(file://) 데이터가 막힙니다. 폴더에서 로컬 서버를 켜 주세요."
                )
              : null
          );
          return false;
        }
        metroLoadState = "ready";
        applyMetroLineZoomStyle();
        return true;
      })
      .catch(function (err) {
        try {
          console.warn("[places-map] metro load error", err && err.message);
        } catch (eLog) {}
        metroLoadState = "error";
        setMetroHint("error");
        return false;
      });
  }

  function isFilterPanelOpen() {
    var legend = el("[data-places-legend]");
    return !!(legend && !legend.classList.contains("is-collapsed"));
  }

  function setFilterPanelOpen(open, persist) {
    var legend = el("[data-places-legend]");
    var toggle = el("[data-places-filter-toggle]");
    if (!legend) return;
    legend.classList.toggle("is-collapsed", !open);
    if (toggle) {
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    }
    if (persist !== false) {
      try {
        if (window.localStorage) {
          localStorage.setItem(FILTER_OPEN_KEY, open ? "1" : "0");
        }
      } catch (e) {}
    }
  }

  function initFilterPanel() {
    var legend = el("[data-places-legend]");
    var toggle = el("[data-places-filter-toggle]");
    if (!legend || !toggle) return;

    var open = false;
    try {
      var raw = window.localStorage && localStorage.getItem(FILTER_OPEN_KEY);
      if (raw === "1") open = true;
      else if (raw === "0") open = false;
      else open = false; // collapsed by default (esp. mobile map coverage)
    } catch (e) {
      open = false;
    }
    setFilterPanelOpen(open, false);

    toggle.addEventListener("click", function () {
      setFilterPanelOpen(!isFilterPanelOpen(), true);
    });
  }

  function applyMetroVisibility() {
    if (!map) return;
    var show = !!activeMetro.metro;

    if (!show) {
      if (metroLineLayer && map.hasLayer(metroLineLayer)) map.removeLayer(metroLineLayer);
      if (metroStationLayer && map.hasLayer(metroStationLayer)) {
        map.removeLayer(metroStationLayer);
      }
      metroAutoFocused = false;
      setMetroHint("clear");
      return;
    }

    // Never leave master ON with both children OFF (blank map + lying toast).
    if (!activeMetro.metroLines && !activeMetro.metroStations) {
      activeMetro.metroLines = true;
      activeMetro.metroStations = true;
      syncMetroFilterUi();
      saveTypeFilters();
    }

    ensureMetroLayers().then(function (ok) {
      if (!activeMetro.metro) return;
      if (!ok) {
        // Only surface error when load truly failed (not a visibility/zoom race).
        if (metroLoadState === "error") setMetroHint("error");
        return;
      }
      // Re-read flags after async load (user may have toggled during fetch).
      var linesOn = !!activeMetro.metro && !!activeMetro.metroLines;
      var stationsOn = !!activeMetro.metro && !!activeMetro.metroStations;

      if (linesOn) {
        applyMetroLineIdVisibility();
        if (!map.hasLayer(metroLineLayer)) metroLineLayer.addTo(map);
        try {
          metroLineLayer.bringToFront();
        } catch (e1) {}
      } else if (metroLineLayer && map.hasLayer(metroLineLayer)) {
        map.removeLayer(metroLineLayer);
      }
      if (stationsOn) {
        // Zoom into Seoul first so station filter at peninsula zoom is not empty.
        focusMetroIfNeeded();
        if (!stationLayerHasMarkers() && metroStationGeo) {
          rebuildMetroStationLayer();
        }
        if (!map.hasLayer(metroStationLayer)) metroStationLayer.addTo(map);
        try {
          metroStationLayer.bringToFront();
        } catch (e2) {}
      } else if (metroStationLayer && map.hasLayer(metroStationLayer)) {
        map.removeLayer(metroStationLayer);
      }

      var lineCount = linesOn ? countMetroLineOverlays() : 0;
      var stationCount = stationsOn ? countStationMarkers() : 0;
      var hasData =
        (metroLineLayer && metroLineLayer.getLayers().length > 0) ||
        !!metroStationGeo;
      if (lineCount + stationCount > 0) {
        setMetroHint("ready", { lines: lineCount, stations: stationCount });
      } else if (hasData) {
        // Data loaded; markers may appear after zoom/focus settles.
        setMetroHint("ready", { lines: lineCount, stations: stationCount });
        focusMetroIfNeeded();
      } else {
        setMetroHint("error");
      }

      try {
        map.invalidateSize(false);
      } catch (e3) {}
    });
  }

  function applyVisibilityFilters() {
    Object.keys(markersBySlug).forEach(function (slug) {
      var meta = placeMeta[slug] || {};
      var typeOk = !!activeTypes[normalizeType(meta.type)];
      var regionOk = activeRegion === "all" || meta.region === activeRegion;
      var m = markersBySlug[slug];
      var iconEl = m.getElement && m.getElement();

      if (!typeOk) {
        if (iconEl) {
          iconEl.classList.add("is-type-hidden");
          iconEl.classList.remove("is-dimmed");
        }
        if (m.setOpacity) m.setOpacity(0);
        if (m._icon) m._icon.style.display = "none";
        if (m._shadow) m._shadow.style.display = "none";
        return;
      }

      if (m._icon) m._icon.style.display = "";
      if (m._shadow) m._shadow.style.display = "";
      if (iconEl) {
        iconEl.classList.remove("is-type-hidden");
        iconEl.classList.toggle("is-dimmed", !regionOk);
      }
      if (m.setOpacity) m.setOpacity(regionOk ? 1 : 0.35);
    });

    document.querySelectorAll("[data-places-drawer-item]").forEach(function (item) {
      var r = item.getAttribute("data-region") || "";
      var type = normalizeType(item.getAttribute("data-type"));
      var regionOk = activeRegion === "all" || r === activeRegion;
      var typeOk = !!activeTypes[type];
      item.hidden = !(regionOk && typeOk);
    });

    if (activeSlug) {
      var am = placeMeta[activeSlug] || {};
      if (!activeTypes[normalizeType(am.type)]) setPanel(null);
    }

    applyMetroVisibility();
  }

  function clearDetailEmbed() {
    var iframe = el("[data-places-panel-embed]");
    if (iframe) iframe.setAttribute("src", "about:blank");
    var wrap = el("[data-places-panel-map-wrap]");
    if (wrap) wrap.hidden = true;
  }

  function clearDetailBodyMount() {
    var mount = el("[data-places-panel-body-mount]");
    if (!mount) return;
    mount.innerHTML = "";
    mount.setAttribute("data-body-path", "");
    mount.hidden = true;
  }

  function fillDetailContent(slug) {
    var addressWrap = el("[data-places-panel-address-wrap]");
    var addressLink = el("[data-places-panel-address]");
    var howBlock = el("[data-places-panel-how-block]");
    var howFull = el("[data-places-panel-how-full]");
    var mapWrap = el("[data-places-panel-map-wrap]");
    var iframe = el("[data-places-panel-embed]");
    var mount = el("[data-places-panel-body-mount]");

    var address = placeField(slug, "address");
    var mapsUrl = placeField(slug, "mapsUrl");
    var embedUrl = placeField(slug, "mapsEmbedUrl");
    var howText = placeField(slug, "how");
    var hasBody = placeHasBody(slug);

    if (addressWrap && addressLink) {
      if (address) {
        addressWrap.hidden = false;
        addressLink.textContent = address;
        if (mapsUrl) {
          addressLink.href = mapsUrl;
          addressLink.removeAttribute("aria-disabled");
        } else {
          addressLink.href = "#";
          addressLink.setAttribute("aria-disabled", "true");
        }
      } else {
        addressWrap.hidden = true;
        addressLink.textContent = "";
        addressLink.href = "#";
      }
    }

    if (howBlock && howFull) {
      if (howText) {
        howBlock.hidden = false;
        howFull.textContent = howText;
      } else {
        howBlock.hidden = true;
        howFull.textContent = "";
      }
    }

    // Rich intro blocks from i18n (may overlap desc/how; still useful when expanded).
    if (mount) {
      if (hasBody) {
        mount.setAttribute("data-body-path", "places." + slug + ".body");
        mount.hidden = false;
        if (window.GuideContentBody && typeof window.GuideContentBody.render === "function") {
          window.GuideContentBody.render(
            (window.GuideI18n && window.GuideI18n.getLang && window.GuideI18n.getLang()) || "ko"
          );
        }
      } else {
        clearDetailBodyMount();
      }
    }

    if (mapWrap && iframe) {
      if (embedUrl) {
        mapWrap.hidden = false;
        if (iframe.getAttribute("src") !== embedUrl) {
          iframe.setAttribute("src", embedUrl);
        }
      } else {
        clearDetailEmbed();
      }
    }
  }

  function setDetailMode(open) {
    detailOpen = !!open && !!activeSlug;
    var panel = el("[data-places-panel]");
    var detail = el("[data-places-panel-detail]");
    var howSummary = el("[data-places-panel-how]");
    var expandBtn = el("[data-places-panel-expand]");
    var collapseBtn = el("[data-places-panel-collapse]");

    if (panel) panel.classList.toggle("is-detail", detailOpen);
    if (detail) detail.hidden = !detailOpen;
    if (howSummary) {
      // Summary how line stays in compact mode only
      var howText = activeSlug ? placeField(activeSlug, "how") : "";
      howSummary.hidden = detailOpen || !howText;
    }
    if (expandBtn) expandBtn.hidden = detailOpen || !activeSlug;
    if (collapseBtn) collapseBtn.hidden = !detailOpen;

    if (detailOpen && activeSlug) {
      fillDetailContent(activeSlug);
    } else {
      clearDetailEmbed();
      clearDetailBodyMount();
    }

    if (map) {
      setTimeout(function () {
        try {
          map.invalidateSize();
        } catch (e) {}
      }, 280);
    }
  }

  function syncHash(slug) {
    try {
      if (!window.history || !window.history.replaceState) return;
      var url = new URL(window.location.href);
      if (slug) {
        url.hash = "place=" + encodeURIComponent(slug);
      } else {
        url.hash = "";
      }
      window.history.replaceState(null, "", url.pathname + url.search + url.hash);
    } catch (e) {}
  }

  function setPanel(slug, opts) {
    opts = opts || {};
    var panel = el("[data-places-panel]");
    var empty = el("[data-places-panel-empty]");
    var body = el("[data-places-panel-body]");
    var hint = el("[data-places-hint]");
    if (!panel || !body) return;

    var prevSlug = activeSlug;
    activeSlug = slug || null;
    panel.classList.toggle("is-open", !!slug);
    panel.setAttribute("aria-hidden", slug ? "false" : "true");
    if (empty) empty.hidden = !!slug;
    body.hidden = !slug;
    if (hint) hint.hidden = !!slug;

    setMarkerActive(slug);

    document.querySelectorAll("[data-places-drawer-item]").forEach(function (item) {
      item.classList.toggle(
        "is-active",
        item.getAttribute("data-slug") === slug
      );
    });

    if (!slug) {
      setDetailMode(false);
      syncHash(null);
      var infoBadgeClear = el("[data-places-panel-info]");
      var lockerBadgeClear = el("[data-places-panel-locker]");
      var portBadgeClear = el("[data-places-panel-port]");
      var busBadgeClear = el("[data-places-panel-bus-terminal]");
      var panelBodyClear = el("[data-places-panel-body]");
      var coverWrapClear = el("[data-places-panel-cover-wrap]");
      var coverImgClear = el("[data-places-panel-cover]");
      if (infoBadgeClear) infoBadgeClear.hidden = true;
      if (lockerBadgeClear) lockerBadgeClear.hidden = true;
      if (portBadgeClear) portBadgeClear.hidden = true;
      if (busBadgeClear) busBadgeClear.hidden = true;
      if (panelBodyClear) {
        panelBodyClear.classList.remove(
          "is-info-place",
          "is-locker-place",
          "is-port-place",
          "is-bus-terminal-place"
        );
      }
      if (coverWrapClear) coverWrapClear.hidden = true;
      if (coverImgClear) {
        coverImgClear.removeAttribute("src");
        coverImgClear.alt = "";
      }
      return;
    }

    var title = el("[data-places-panel-title]");
    var region = el("[data-places-panel-region]");
    var desc = el("[data-places-panel-desc]");
    var how = el("[data-places-panel-how]");
    var expandBtn = el("[data-places-panel-expand]");

    var meta = placeMeta[slug] || {};
    var kind = normalizeType(meta.type);
    var isInfo = kind === "info";
    var isLocker = kind === "locker";
    var isPort = kind === "port";
    var isBusTerminal = kind === "bus-terminal";
    var infoBadge = el("[data-places-panel-info]");
    var lockerBadge = el("[data-places-panel-locker]");
    var portBadge = el("[data-places-panel-port]");
    var busBadge = el("[data-places-panel-bus-terminal]");
    var panelBody = el("[data-places-panel-body]");
    if (panelBody) {
      panelBody.classList.toggle("is-info-place", isInfo);
      panelBody.classList.toggle("is-locker-place", isLocker);
      panelBody.classList.toggle("is-port-place", isPort);
      panelBody.classList.toggle("is-bus-terminal-place", isBusTerminal);
    }
    if (infoBadge) infoBadge.hidden = !isInfo;
    if (lockerBadge) lockerBadge.hidden = !isLocker;
    if (portBadge) portBadge.hidden = !isPort;
    if (busBadge) busBadge.hidden = !isBusTerminal;

    setPanelCover(slug, meta);

    if (title) title.textContent = placeField(slug, "name") || slug;
    if (region) region.textContent = placeField(slug, "regionLabel") || "";
    if (desc) desc.textContent = placeField(slug, "desc") || "";
    if (how) {
      var howText = placeField(slug, "how");
      how.textContent = howText
        ? t("transport.howLabel", "가는 방법") + ": " + howText
        : "";
      how.hidden = !howText;
    }
    if (expandBtn) {
      expandBtn.textContent = t("transport.mapOpenDetail", "자세히 보기");
      expandBtn.hidden = false;
    }

    // Keep detail open when refreshing same place (e.g. language change)
    var keepDetail = opts.keepDetail || (detailOpen && prevSlug === slug);
    setDetailMode(!!keepDetail);
    if (opts.syncHash !== false) syncHash(slug);
  }

  function focusPlace(slug, opts) {
    var marker = markersBySlug[slug];
    if (!marker || !map) return;
    opts = opts || {};
    var meta = placeMeta[slug];
    if (meta && meta.region && activeRegion !== "all" && activeRegion !== meta.region) {
      applyRegionFilter(meta.region);
    }
    setPanel(slug, {
      keepDetail: !!opts.detail,
      syncHash: opts.syncHash,
    });
    if (opts.detail) setDetailMode(true);
    var latlng = marker.getLatLng();
    var zoom = opts.zoom != null ? opts.zoom : FOCUS_ZOOM;
    fly(latlng, zoom, opts.duration != null ? opts.duration : 1.55);
  }

  function focusRegion(region) {
    var key = region || "all";
    applyRegionFilter(key);
    setPanel(null);
    var view = REGION_VIEWS[key] || REGION_VIEWS.all;
    fly(view.center, view.zoom, 1.2);
  }

  function resetView() {
    applyRegionFilter("all");
    setPanel(null);
    fly(KOREA_CENTER, KOREA_ZOOM, 1.1);
  }

  function clearLocateToastClasses(hint) {
    if (!hint) return;
    hint.classList.remove(
      "is-locate-toast",
      "is-locate-loading",
      "is-locate-error"
    );
  }

  function restoreHintAfterLocate() {
    var hint = el("[data-places-hint]");
    if (!hint) return;
    clearLocateToastClasses(hint);
    if (activeMetro.metro) {
      if (metroLoadState === "loading") {
        setMetroHint("loading");
        return;
      }
      if (metroLoadState === "error") {
        setMetroHint("error");
        return;
      }
      if (metroLoadState === "ready") {
        setMetroHint("ready");
        return;
      }
    }
    hint.classList.remove(
      "is-metro-toast",
      "is-metro-loading",
      "is-metro-ready",
      "is-metro-error"
    );
    hint.textContent = t(
      "transport.mapHelp",
      "핀을 눌러 명소를 확대·살펴보세요. 지역 칩으로 카메라가 이동합니다."
    );
    hint.hidden = false;
  }

  function showLocateToast(kind, message) {
    var hint = el("[data-places-hint]");
    if (!hint) return;
    if (locateToastTimer) {
      clearTimeout(locateToastTimer);
      locateToastTimer = null;
    }
    hint.classList.remove(
      "is-metro-toast",
      "is-metro-loading",
      "is-metro-ready",
      "is-metro-error"
    );
    clearLocateToastClasses(hint);
    if (!kind) {
      restoreHintAfterLocate();
      return;
    }
    hint.textContent = message || "";
    hint.classList.add("is-locate-toast");
    if (kind === "loading") hint.classList.add("is-locate-loading");
    if (kind === "error") hint.classList.add("is-locate-error");
    hint.hidden = false;
    if (kind === "error" || kind === "done") {
      locateToastTimer = setTimeout(function () {
        locateToastTimer = null;
        restoreHintAfterLocate();
      }, kind === "error" ? 4200 : 1600);
    }
  }

  function clearUserLocation() {
    if (!map) return;
    if (userLocMarker) {
      try {
        map.removeLayer(userLocMarker);
      } catch (e) {}
      userLocMarker = null;
    }
    if (userAccCircle) {
      try {
        map.removeLayer(userAccCircle);
      } catch (e) {}
      userAccCircle = null;
    }
  }

  function userLocationIcon() {
    return L.divIcon({
      className: "places-map-user-loc",
      html:
        '<span class="places-map-user-loc__wrap" aria-hidden="true">' +
        '<span class="places-map-user-loc__pulse"></span>' +
        '<span class="places-map-user-loc__dot"></span>' +
        "</span>",
      iconSize: [22, 22],
      iconAnchor: [11, 11],
    });
  }

  function showUserLocation(lat, lng, accuracy) {
    if (!map) return;
    clearUserLocation();
    var latlng = L.latLng(lat, lng);
    userLocMarker = L.marker(latlng, {
      icon: userLocationIcon(),
      interactive: false,
      keyboard: false,
      zIndexOffset: 1200,
    }).addTo(map);

    var acc = typeof accuracy === "number" && isFinite(accuracy) ? accuracy : 0;
    if (acc > 0) {
      userAccCircle = L.circle(latlng, {
        radius: Math.max(acc, 12),
        color: "#2b7fff",
        weight: 1.5,
        opacity: 0.5,
        fillColor: "#2b7fff",
        fillOpacity: 0.12,
        interactive: false,
      }).addTo(map);
      try {
        map.fitBounds(userAccCircle.getBounds().pad(0.4), {
          maxZoom: 16,
          animate: !reduceMotion,
          duration: reduceMotion ? 0 : 0.9,
        });
      } catch (e) {
        fly(latlng, 15, 0.9);
      }
    } else {
      fly(latlng, 15, 0.9);
    }
  }

  function setLocateBusy(busy) {
    locateBusy = !!busy;
    var btn = el("[data-places-locate]");
    if (btn) {
      btn.classList.toggle("is-busy", locateBusy);
      btn.setAttribute("aria-busy", locateBusy ? "true" : "false");
    }
  }

  function locateUser() {
    if (!map || locateBusy) return;

    if (!navigator.geolocation) {
      showLocateToast(
        "error",
        t(
          "transport.locateUnsupported",
          "이 기기는 위치 기능을 지원하지 않습니다."
        )
      );
      return;
    }

    if (typeof window.isSecureContext === "boolean" && !window.isSecureContext) {
      showLocateToast(
        "error",
        t(
          "transport.locateInsecure",
          "위치는 HTTPS 또는 localhost에서만 사용할 수 있습니다."
        )
      );
      return;
    }

    setLocateBusy(true);
    showLocateToast(
      "loading",
      t("transport.locateLocating", "위치 찾는 중…")
    );

    navigator.geolocation.getCurrentPosition(
      function (pos) {
        setLocateBusy(false);
        if (!pos || !pos.coords) {
          showLocateToast(
            "error",
            t("transport.locateUnavailable", "현재 위치를 확인할 수 없습니다.")
          );
          return;
        }
        showUserLocation(
          pos.coords.latitude,
          pos.coords.longitude,
          pos.coords.accuracy
        );
        if (locateToastTimer) {
          clearTimeout(locateToastTimer);
          locateToastTimer = null;
        }
        restoreHintAfterLocate();
      },
      function (err) {
        setLocateBusy(false);
        var code = err && err.code;
        var msg;
        if (code === 1) {
          msg = t(
            "transport.locateDenied",
            "위치 권한이 거부되었습니다. 브라우저 설정에서 허용해 주세요."
          );
        } else if (code === 3) {
          msg = t(
            "transport.locateTimeout",
            "위치 확인 시간이 초과되었습니다. 다시 시도해 주세요."
          );
        } else {
          msg = t(
            "transport.locateUnavailable",
            "현재 위치를 확인할 수 없습니다."
          );
        }
        showLocateToast("error", msg);
      },
      {
        enableHighAccuracy: true,
        timeout: 15000,
        maximumAge: 30000,
      }
    );
  }

  function setDrawer(open) {
    drawerOpen = !!open;
    var drawer = el("[data-places-drawer]");
    var toggle = el("[data-places-list-toggle]");
    if (drawer) {
      drawer.hidden = !drawerOpen;
      drawer.setAttribute("aria-hidden", drawerOpen ? "false" : "true");
      drawer.classList.toggle("is-open", drawerOpen);
    }
    if (toggle) {
      toggle.setAttribute("aria-expanded", drawerOpen ? "true" : "false");
      toggle.classList.toggle("is-active", drawerOpen);
    }
    document.body.classList.toggle("places-map-drawer-open", drawerOpen);
  }

  var PLACE_TYPES = {
    city: true,
    nature: true,
    heritage: true,
    airport: true,
    info: true,
    locker: true,
    port: true,
    "bus-terminal": true,
  };

  function normalizeType(type) {
    var key = (type || "").toLowerCase();
    return PLACE_TYPES[key] ? key : "city";
  }

  function assetUrl(rel) {
    if (!rel) return "";
    if (/^https?:\/\//i.test(rel) || rel.charAt(0) === "/") return rel;
    try {
      return new URL("../../" + rel.replace(/^\.\.\//, ""), window.location.href).href;
    } catch (e) {
      return "../../" + rel;
    }
  }

  function placeImageCandidates(slug, meta) {
    meta = meta || {};
    var kind = normalizeType(meta.type);
    var list = [];
    var fromI18n = placeField(slug, "image");
    if (fromI18n) list.push(fromI18n);
    if (meta.image) list.push(meta.image);
    list.push("Images/places/" + slug + ".jpg");
    list.push("Images/places/" + slug + ".png");
    list.push("Images/places/" + slug + ".webp");
    list.push("Images/places/_types/" + kind + ".jpg");
    list.push("Images/places/_types/" + kind + ".png");
    // de-dupe
    var seen = {};
    return list.filter(function (p) {
      if (!p || seen[p]) return false;
      seen[p] = true;
      return true;
    });
  }

  function bindImageFallback(img, candidates, startIdx) {
    var i = startIdx || 0;
    function tryNext() {
      if (i >= candidates.length) {
        img.onerror = null;
        img.removeAttribute("src");
        var wrap = img.closest("[data-places-panel-cover-wrap], .places-map-drawer__thumb-wrap");
        if (wrap) wrap.hidden = true;
        return;
      }
      var url = assetUrl(candidates[i]);
      i += 1;
      img.onerror = tryNext;
      img.src = url;
    }
    tryNext();
  }

  function setPanelCover(slug, meta) {
    var wrap = el("[data-places-panel-cover-wrap]");
    var img = el("[data-places-panel-cover]");
    if (!wrap || !img) return;
    var candidates = placeImageCandidates(slug, meta);
    if (!candidates.length) {
      wrap.hidden = true;
      img.removeAttribute("src");
      return;
    }
    wrap.hidden = false;
    img.alt = placeField(slug, "name") || slug;
    bindImageFallback(img, candidates, 0);
  }

  /** SVG glyph snippets — solid silhouettes readable at ~16px on satellite. */
  var MARKER_GLYPHS = {
    airport:
      '<svg viewBox="0 0 24 24" width="16" height="16" focusable="false" aria-hidden="true">' +
      '<path fill="currentColor" d="M21 16v-2l-8-5V3.5a1.5 1.5 0 0 0-3 0V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"/>' +
      "</svg>",
    // Skyline: three stepped buildings + ground line
    city:
      '<svg viewBox="0 0 24 24" width="16" height="16" focusable="false" aria-hidden="true">' +
      '<path fill="currentColor" d="M3 21h18v-1.5H3V21zm2-3h3.5V9H5v9zm5 0h4V5h-4v13zm5.5 0H19v-7h-3.5v7z"/>' +
      "</svg>",
    // Twin mountain peaks
    nature:
      '<svg viewBox="0 0 24 24" width="16" height="16" focusable="false" aria-hidden="true">' +
      '<path fill="currentColor" d="M2 19L8.5 7.5 11.8 13l2.7-4.8L22 19H2z"/>' +
      "</svg>",
    // Pagoda: roof tiers + base pillar
    heritage:
      '<svg viewBox="0 0 24 24" width="16" height="16" focusable="false" aria-hidden="true">' +
      '<path fill="currentColor" d="M12 2.2L4 7.2v1.6h16V7.2L12 2.2zM5.5 10.2v1.5h13V10.2h-13zm2 3v1.5h9V13.2h-9zm2 3v1.4h5V16.2h-5zm1.2 2.8v2.5h-1.4V22h5.4v-1.5h-1.4v-2.5h-2.6z"/>' +
      "</svg>",
    // Luggage / suitcase with handle
    locker:
      '<svg viewBox="0 0 24 24" width="15" height="15" focusable="false" aria-hidden="true">' +
      '<path fill="currentColor" d="M9 7V4.8c0-1 .8-1.8 1.8-1.8h2.4c1 0 1.8.8 1.8 1.8V7H18c1.1 0 2 .9 2 2v10c0 1.1-.9 2-2 2H6c-1.1 0-2-.9-2-2V9c0-1.1.9-2 2-2h3zm2-2.2h2v2.2h-2V4.8zM6 9v10h12V9H6zm3 2h2v6H9v-6zm6 0h2v6h-2v-6z"/>' +
      "</svg>",
    // Ferry / ship hull
    port:
      '<svg viewBox="0 0 24 24" width="16" height="16" focusable="false" aria-hidden="true">' +
      '<path fill="currentColor" d="M20 21c-1.39 0-2.78-.47-4-1.32-2.44 1.71-5.56 1.71-8 0C6.78 20.53 5.39 21 4 21H2v2h2c1.38 0 2.74-.35 4-.99 2.52 1.29 5.48 1.29 8 0 1.26.65 2.62.99 4 .99h2v-2h-2zM3.95 19H4c1.6 0 3.02-.88 4-2 .98 1.12 2.4 2 4 2s3.02-.88 4-2c.98 1.12 2.4 2 4 2h.05l1.9-6.68c.08-.26.06-.54-.06-.78s-.32-.42-.57-.5L20 10.5V6c0-1.1-.9-2-2-2h-3V1H9v3H6c-1.1 0-2 .9-2 2v4.5l-.31.11c-.25.08-.45.26-.57.5s-.14.52-.06.78L3.95 19zM6 6h12v3.97L12 8 6 9.97V6z"/>' +
      "</svg>",
    // Bus / coach front
    "bus-terminal":
      '<svg viewBox="0 0 24 24" width="16" height="16" focusable="false" aria-hidden="true">' +
      '<path fill="currentColor" d="M4 16c0 .88.39 1.67 1 2.22V20a1 1 0 0 0 1 1h1a1 1 0 0 0 1-1v-1h8v1a1 1 0 0 0 1 1h1a1 1 0 0 0 1-1v-1.78c.61-.55 1-1.34 1-2.22V6c0-3.5-3.58-4-8-4s-8 .5-8 4v10zm3.5 1.5a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3zm9 0a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3zM18 6.88c0 .07-.05.13-.1.18-.4.35-2.07.94-5.9.94s-5.5-.59-5.9-.94A.25.25 0 0 1 6 6.88V6c0-.34.66-.94 2.19-1.32C9.54 4.34 10.94 4.2 12 4.2s2.46.14 3.81.48C17.34 5.06 18 5.66 18 6v.88zM6.5 11h4V8.5h-4V11zm7 0h4V8.5h-4V11z"/>' +
      "</svg>",
  };

  var BADGE_MARKER_KINDS = {
    city: true,
    nature: true,
    heritage: true,
    airport: true,
    locker: true,
    port: true,
    "bus-terminal": true,
  };

  function markerIcon(type, active) {
    var kind = normalizeType(type);
    var pulse = '<span class="places-map-marker__pulse" aria-hidden="true"></span>';
    var glyphClass =
      kind === "airport"
        ? "plane"
        : kind === "bus-terminal"
          ? "bus-terminal"
          : kind === "city" ||
              kind === "nature" ||
              kind === "heritage" ||
              kind === "locker" ||
              kind === "port"
            ? kind
            : null;
    var inner;
    if (glyphClass && MARKER_GLYPHS[kind]) {
      inner =
        '<span class="places-map-marker__' +
        glyphClass +
        '" data-places-marker-glyph="' +
        kind +
        '" aria-hidden="true">' +
        MARKER_GLYPHS[kind] +
        "</span>" +
        pulse;
    } else if (kind === "info") {
      inner = '<span class="places-map-marker__info" aria-hidden="true">i</span>';
    } else {
      inner =
        '<span class="places-map-marker__pin" aria-hidden="true"></span>' + pulse;
    }
    var isBadge = !!BADGE_MARKER_KINDS[kind];
    var size = kind === "info" ? [22, 22] : isBadge ? [34, 34] : [28, 36];
    var anchor = kind === "info" ? [11, 11] : isBadge ? [17, 17] : [14, 34];
    var popup = kind === "info" ? [0, -10] : isBadge ? [0, -15] : [0, -30];
    // Always DivIcon for place markers (never L.icon / image pins).
    return L.divIcon({
      className:
        "places-map-marker places-map-marker--" +
        kind +
        (active ? " is-active" : ""),
      html:
        '<span class="places-map-marker__wrap" data-places-marker-kind="' +
        kind +
        '">' +
        inner +
        "</span>",
      iconSize: size,
      iconAnchor: anchor,
      popupAnchor: popup,
    });
  }

  /** Create a sightseeing / transit place marker (DivIcon badges for typed places). */
  function createMarker(item, label) {
    var kind = normalizeType(item && item.type);
    var icon = markerIcon(kind, false);
    // Proof: badge kinds must be Leaflet DivIcon, not image Icon.
    if (
      BADGE_MARKER_KINDS[kind] &&
      !(icon && icon.options && /places-map-marker--/.test(icon.options.className || ""))
    ) {
      console.warn("[places-map] expected DivIcon badge for type:", kind);
    }
    return L.marker([item.lat, item.lng], {
      icon: icon,
      title: label,
      keyboard: true,
      riseOnHover: true,
    });
  }

  function buildDrawerList() {
    var list = el("[data-places-drawer-list]");
    if (!list) return;
    list.innerHTML = "";
    var coords = window.PLACES_COORDS || [];
    coords.forEach(function (item) {
      if (!item || !item.slug) return;
      var li = document.createElement("li");
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "places-map-drawer__item";
      btn.setAttribute("data-places-drawer-item", "");
      btn.setAttribute("data-slug", item.slug);
      btn.setAttribute("data-region", item.region || "");
      btn.setAttribute("data-type", normalizeType(item.type));

      var thumbWrap = document.createElement("span");
      thumbWrap.className = "places-map-drawer__thumb-wrap";
      var thumb = document.createElement("img");
      thumb.className = "places-map-drawer__thumb";
      thumb.alt = "";
      thumb.loading = "lazy";
      thumb.decoding = "async";
      thumbWrap.appendChild(thumb);
      bindImageFallback(thumb, placeImageCandidates(item.slug, item), 0);

      var swatch = document.createElement("span");
      swatch.className =
        "places-map-drawer__swatch places-map-drawer__swatch--" +
        normalizeType(item.type);
      swatch.setAttribute("aria-hidden", "true");
      var name = document.createElement("span");
      name.className = "places-map-drawer__name";
      name.textContent = placeField(item.slug, "name") || item.slug;
      var region = document.createElement("span");
      region.className = "places-map-drawer__region";
      region.textContent = placeField(item.slug, "regionLabel") || item.region || "";
      btn.appendChild(thumbWrap);
      btn.appendChild(swatch);
      btn.appendChild(name);
      btn.appendChild(region);
      btn.addEventListener("click", function () {
        setDrawer(false);
        focusPlace(item.slug);
      });
      li.appendChild(btn);
      list.appendChild(li);
    });
  }

  function refreshDrawerLabels() {
    document.querySelectorAll("[data-places-drawer-item]").forEach(function (btn) {
      var slug = btn.getAttribute("data-slug");
      if (!slug) return;
      var name = btn.querySelector(".places-map-drawer__name");
      var region = btn.querySelector(".places-map-drawer__region");
      if (name) name.textContent = placeField(slug, "name") || slug;
      if (region) region.textContent = placeField(slug, "regionLabel") || "";
    });
  }

  function parseHashSlug() {
    try {
      var hash = (window.location.hash || "").replace(/^#/, "");
      if (!hash) return null;
      if (hash.indexOf("place=") === 0) {
        return decodeURIComponent(hash.slice(6)) || null;
      }
      // bare slug e.g. #myeongdong
      if (/^[a-z0-9-]+$/i.test(hash) && markersBySlug[hash]) return hash;
    } catch (e) {}
    return null;
  }

  function initMap() {
    var host = el("#places-korea-map");
    if (!host || typeof L === "undefined") return;
    if (map) return;

    map = L.map(host, {
      center: KOREA_CENTER,
      zoom: KOREA_ZOOM,
      minZoom: 6,
      maxZoom: 18,
      maxBounds: KOREA_BOUNDS.pad(0.15),
      maxBoundsViscosity: 0.75,
      zoomControl: false,
      attributionControl: false,
      scrollWheelZoom: true,
    });

    L.control
      .zoom({
        position: "topright",
      })
      .addTo(map);

    L.tileLayer(
      "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
      {
        attribution:
          "Tiles &copy; Esri &mdash; Source: Esri, Maxar, Earthstar Geographics",
        maxZoom: 18,
      }
    ).addTo(map);

    L.tileLayer(
      "https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}",
      {
        opacity: 0.85,
        maxZoom: 18,
        attribution: "",
      }
    ).addTo(map);

    var coords = window.PLACES_COORDS || [];
    coords.forEach(function (item) {
      if (!item || !item.slug || item.lat == null || item.lng == null) return;
      var slug = item.slug;
      placeMeta[slug] = {
        region: item.region || "",
        type: normalizeType(item.type),
        lat: item.lat,
        lng: item.lng,
        image: item.image || "",
      };
      var label = placeField(slug, "name") || slug;
      var marker = createMarker(item, label);
      marker.addTo(map);
      marker.bindTooltip(label, {
        permanent: false,
        direction: "auto",
        sticky: true,
        opacity: 0.96,
        className: "places-metro-tooltip",
      });
      marker.on("click", function () {
        focusPlace(slug);
      });
      markersBySlug[slug] = marker;
    });

    setTimeout(function () {
      try {
        map.invalidateSize();
      } catch (e) {}
    }, 80);

    window.addEventListener("resize", function () {
      if (map) map.invalidateSize();
    });
  }

  function bindUi() {
    var reset = el("[data-places-map-reset]");
    if (reset) {
      reset.addEventListener("click", function () {
        resetView();
      });
    }

    var locateBtn = el("[data-places-locate]");
    if (locateBtn) {
      locateBtn.addEventListener("click", function () {
        locateUser();
      });
    }

    var close = el("[data-places-panel-close]");
    if (close) {
      close.addEventListener("click", function () {
        setPanel(null);
      });
    }

    var expandBtn = el("[data-places-panel-expand]");
    if (expandBtn) {
      expandBtn.addEventListener("click", function () {
        if (!activeSlug) return;
        setDetailMode(true);
      });
    }

    var collapseBtn = el("[data-places-panel-collapse]");
    if (collapseBtn) {
      collapseBtn.addEventListener("click", function () {
        setDetailMode(false);
      });
    }

    document.querySelectorAll("[data-places-region]").forEach(function (btn) {
      btn.setAttribute("aria-pressed", btn.classList.contains("is-active") ? "true" : "false");
      btn.addEventListener("click", function () {
        focusRegion(btn.getAttribute("data-places-region") || "all");
      });
    });

    document.querySelectorAll("[data-places-type-filter]").forEach(function (input) {
      input.addEventListener("change", function () {
        var type = input.getAttribute("data-places-type-filter");
        if (!type || !DEFAULT_TYPES.hasOwnProperty(type)) return;
        activeTypes[type] = !!input.checked;
        // Keep at least one type visible
        var anyOn = Object.keys(activeTypes).some(function (k) {
          return activeTypes[k];
        });
        if (!anyOn) {
          activeTypes[type] = true;
          input.checked = true;
        }
        saveTypeFilters();
        syncGroupFilterUi();
        applyVisibilityFilters();
      });
    });

    document.querySelectorAll("[data-places-metro-filter]").forEach(function (input) {
      input.addEventListener("change", function () {
        var key = input.getAttribute("data-places-metro-filter");
        if (!key || !DEFAULT_METRO.hasOwnProperty(key)) return;
        var turningMetroOn = key === "metro" && !!input.checked && !activeMetro.metro;
        activeMetro[key] = !!input.checked;
        if (key === "metro" && activeMetro.metro) {
          // Master on: always enable BOTH overlays and force a fresh draw.
          activeMetro.metroLines = true;
          activeMetro.metroStations = true;
          if (metroLoadState === "error") metroLoadState = "idle";
        }
        if (key === "metroLines" || key === "metroStations") {
          if (activeMetro.metro && !activeMetro.metroLines && !activeMetro.metroStations) {
            activeMetro[key] = true;
            input.checked = true;
          }
        }
        syncMetroFilterUi();
        syncGroupFilterUi();
        saveTypeFilters();
        applyMetroVisibility();
        if (turningMetroOn) focusMetroIfNeeded();
      });
    });

    document.querySelectorAll("[data-places-metro-line]").forEach(function (input) {
      input.addEventListener("change", function () {
        var id = input.getAttribute("data-places-metro-line");
        if (!id || !METRO_LINE_IDS.includes(id)) return;
        activeMetroLines[id] = !!input.checked;
        var anyOn = METRO_LINE_IDS.some(function (lid) {
          return !!activeMetroLines[lid];
        });
        if (!anyOn) {
          activeMetroLines[id] = true;
          input.checked = true;
        }
        saveMetroLineFilters();
        syncMetroLineFilterUi();
        if (!activeMetro.metro) return;
        applyMetroLineIdVisibility();
        if (activeMetro.metroStations && metroStationGeo) {
          rebuildMetroStationLayer();
        }
        if (metroLoadState === "ready") {
          var lineCount = activeMetro.metroLines ? countMetroLineOverlays() : 0;
          var stationCount = activeMetro.metroStations ? countStationMarkers() : 0;
          setMetroHint("ready", { lines: lineCount, stations: stationCount });
        }
      });
    });

    var typeAll = el("[data-places-type-all]");
    if (typeAll) {
      typeAll.addEventListener("click", function () {
        Object.keys(DEFAULT_TYPES).forEach(function (k) {
          activeTypes[k] = true;
        });
        syncTypeFilterUi();
        saveTypeFilters();
        applyVisibilityFilters();
      });
    }

    var listToggle = el("[data-places-list-toggle]");
    if (listToggle) {
      listToggle.addEventListener("click", function () {
        setDrawer(!drawerOpen);
      });
    }

    var drawerClose = el("[data-places-drawer-close]");
    if (drawerClose) {
      drawerClose.addEventListener("click", function () {
        setDrawer(false);
      });
    }

    document.addEventListener("keydown", function (ev) {
      if (ev.key === "Escape") {
        if (isFilterPanelOpen()) {
          setFilterPanelOpen(false, true);
          return;
        }
        if (drawerOpen) {
          setDrawer(false);
          return;
        }
        if (detailOpen) {
          setDetailMode(false);
          return;
        }
        if (activeSlug) setPanel(null);
      }
    });

    document.addEventListener("guide:langchange", function () {
      if (activeSlug) setPanel(activeSlug, { keepDetail: detailOpen, syncHash: false });
      refreshDrawerLabels();
      Object.keys(markersBySlug).forEach(function (slug) {
        var m = markersBySlug[slug];
        if (!m) return;
        var label = placeField(slug, "name") || slug;
        if (m.options) m.options.title = label;
        if (m.setTooltipContent) {
          m.setTooltipContent(label);
        } else {
          var tip = m.getTooltip && m.getTooltip();
          if (tip) tip.setContent(label);
        }
      });
      refreshMetroStationLabels();
    });

    window.addEventListener("hashchange", function () {
      var slug = parseHashSlug();
      if (slug && markersBySlug[slug]) {
        focusPlace(slug, { syncHash: false });
      } else if (!slug && activeSlug) {
        setPanel(null);
      }
    });
  }

  function boot() {
    loadTypeFilters();
    loadAccordionState();
    bindAccordionUi();
    bindGroupFilterUi();
    initFilterPanel();
    initMap();
    buildDrawerList();
    bindUi();
    syncTypeFilterUi();
    applyRegionFilter("all");
    setPanel(null);
    setDrawer(false);

    var hashSlug = parseHashSlug();
    if (hashSlug && markersBySlug[hashSlug]) {
      focusPlace(hashSlug, { syncHash: false });
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }

  window.PlacesMap = {
    focus: focusPlace,
    reset: resetView,
    region: focusRegion,
    expandDetail: function () {
      if (activeSlug) setDetailMode(true);
    },
    collapseDetail: function () {
      setDetailMode(false);
    },
  };
})();
