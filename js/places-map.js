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
  var reduceMotion =
    window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function t(key, fallback) {
    try {
      var lang =
        (window.GuideI18n && window.GuideI18n.getLang && window.GuideI18n.getLang()) ||
        "ko";
      var pack =
        (window.__I18N_MESSAGES__ && window.__I18N_MESSAGES__[lang]) || null;
      if (pack) {
        var cur = pack;
        var parts = key.split(".");
        for (var i = 0; i < parts.length; i++) {
          if (!cur || typeof cur !== "object" || !(parts[i] in cur)) {
            cur = undefined;
            break;
          }
          cur = cur[parts[i]];
        }
        if (typeof cur === "string" && cur) return cur;
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
    Object.keys(markersBySlug).forEach(function (slug) {
      var meta = placeMeta[slug] || {};
      var match = activeRegion === "all" || meta.region === activeRegion;
      var m = markersBySlug[slug];
      var iconEl = m.getElement && m.getElement();
      if (iconEl) {
        iconEl.classList.toggle("is-dimmed", !match);
      }
      if (m.setOpacity) {
        m.setOpacity(match ? 1 : 0.35);
      }
    });

    document.querySelectorAll("[data-places-region]").forEach(function (btn) {
      var on = btn.getAttribute("data-places-region") === activeRegion;
      btn.classList.toggle("is-active", on);
      btn.setAttribute("aria-pressed", on ? "true" : "false");
    });

    document.querySelectorAll("[data-places-drawer-item]").forEach(function (item) {
      var r = item.getAttribute("data-region") || "";
      var match = activeRegion === "all" || r === activeRegion;
      item.hidden = !match;
    });
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
      var panelBodyClear = el("[data-places-panel-body]");
      if (infoBadgeClear) infoBadgeClear.hidden = true;
      if (panelBodyClear) panelBodyClear.classList.remove("is-info-place");
      return;
    }

    var title = el("[data-places-panel-title]");
    var region = el("[data-places-panel-region]");
    var desc = el("[data-places-panel-desc]");
    var how = el("[data-places-panel-how]");
    var expandBtn = el("[data-places-panel-expand]");

    var meta = placeMeta[slug] || {};
    var isInfo = normalizeType(meta.type) === "info";
    var infoBadge = el("[data-places-panel-info]");
    var panelBody = el("[data-places-panel-body]");
    if (panelBody) panelBody.classList.toggle("is-info-place", isInfo);
    if (infoBadge) infoBadge.hidden = !isInfo;

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
  };

  function normalizeType(type) {
    var key = (type || "").toLowerCase();
    return PLACE_TYPES[key] ? key : "city";
  }

  function markerIcon(type, active) {
    var kind = normalizeType(type);
    var inner;
    if (kind === "airport") {
      inner =
        '<span class="places-map-marker__plane" aria-hidden="true">' +
        '<svg viewBox="0 0 24 24" width="16" height="16" focusable="false">' +
        '<path fill="currentColor" d="M21 16v-2l-8-5V3.5a1.5 1.5 0 0 0-3 0V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"/>' +
        "</svg></span>" +
        '<span class="places-map-marker__pulse" aria-hidden="true"></span>';
    } else if (kind === "info") {
      inner =
        '<span class="places-map-marker__info" aria-hidden="true">i</span>';
    } else {
      inner =
        '<span class="places-map-marker__pin" aria-hidden="true"></span>' +
        '<span class="places-map-marker__pulse" aria-hidden="true"></span>';
    }
    var size = kind === "info" ? [22, 22] : kind === "airport" ? [32, 32] : [28, 36];
    var anchor =
      kind === "info" ? [11, 11] : kind === "airport" ? [16, 16] : [14, 34];
    var popup =
      kind === "info" ? [0, -10] : kind === "airport" ? [0, -14] : [0, -30];
    return L.divIcon({
      className:
        "places-map-marker places-map-marker--" +
        kind +
        (active ? " is-active" : ""),
      html: inner,
      iconSize: size,
      iconAnchor: anchor,
      popupAnchor: popup,
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
      };
      var marker = L.marker([item.lat, item.lng], {
        icon: markerIcon(item.type, false),
        title: placeField(slug, "name") || slug,
        keyboard: true,
        riseOnHover: true,
      });
      marker.addTo(map);
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
        if (m && m.options) {
          m.options.title = placeField(slug, "name") || slug;
        }
      });
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
    initMap();
    buildDrawerList();
    bindUi();
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
