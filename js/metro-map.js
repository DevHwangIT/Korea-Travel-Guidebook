/**
 * Seoul metro interactive map (Leaflet) + line highlight.
 * Uses local GeoJSON from data/metro/line-*.geojson (OpenStreetMap via Overpass).
 * Official detailed diagram: Seoul Metro Cyber Station (linked separately).
 */
(function () {
  var COLORS = {
    "1": "#0052A4",
    "2": "#00A84D",
    "3": "#EF7C1C",
    "4": "#00A5E3",
    "5": "#996CAC",
    "6": "#CD7C2F",
    "7": "#747F00",
    "9": "#B7A45C",
    arex: "#0090D2",
  };

  var map = null;
  var layers = {};
  var activeLine = "all";
  var mapReady = false;

  function dataBase() {
    var scripts = document.getElementsByTagName("script");
    for (var i = scripts.length - 1; i >= 0; i--) {
      var src = scripts[i].src || "";
      if (src.indexOf("metro-map.js") !== -1) {
        return src.replace(/\/js\/[^/]*$/, "/data/metro/");
      }
    }
    return "../../data/metro/";
  }

  function setLineDetail(lineId) {
    document.querySelectorAll("[data-metro-detail]").forEach(function (el) {
      var on = el.getAttribute("data-metro-detail") === lineId;
      el.hidden = !on;
    });
  }

  function highlight(lineId) {
    activeLine = lineId || "all";
    Object.keys(layers).forEach(function (id) {
      var layer = layers[id];
      if (!layer) return;
      var selected = activeLine === "all" || activeLine === id;
      layer.setStyle({
        color: COLORS[id] || "#333",
        weight: selected ? (activeLine === "all" ? 3 : 5) : 2,
        opacity: selected ? 1 : 0.12,
      });
      if (selected && activeLine !== "all") {
        try {
          map.fitBounds(layer.getBounds(), { padding: [30, 30], maxZoom: 12 });
        } catch (e) {}
      }
    });

    document.querySelectorAll("[data-metro-line]").forEach(function (btn) {
      btn.classList.toggle("is-active", btn.getAttribute("data-metro-line") === activeLine);
    });
    var metroSelect = document.querySelector("[data-metro-select]");
    if (metroSelect && metroSelect.value !== activeLine) {
      metroSelect.value = activeLine;
    }

    if (activeLine !== "all") setLineDetail(activeLine);
    else {
      document.querySelectorAll("[data-metro-detail]").forEach(function (el) {
        el.hidden = true;
      });
      document.querySelectorAll('[data-metro-detail="all"]').forEach(function (el) {
        el.hidden = false;
      });
    }
  }

  function loadLine(lineId) {
    function addGeo(geo) {
      if (!geo || !geo.features || !geo.features.length) return null;
      var layer = L.geoJSON(geo, {
        style: {
          color: COLORS[lineId],
          weight: 3,
          opacity: 0.95,
        },
      });
      layer.addTo(map);
      layers[lineId] = layer;
      return layer;
    }

    if (window.METRO_LINE_DATA && window.METRO_LINE_DATA[lineId]) {
      return Promise.resolve(addGeo(window.METRO_LINE_DATA[lineId]));
    }

    var url = dataBase() + "line-" + lineId + ".geojson";
    return fetch(url)
      .then(function (res) {
        if (!res.ok) throw new Error(String(res.status));
        return res.json();
      })
      .then(addGeo)
      .catch(function () {
        return null;
      });
  }

  function initMap() {
    var el = document.getElementById("metro-leaflet");
    if (!el || typeof L === "undefined") return;

    map = L.map(el, {
      center: [37.55, 126.98],
      zoom: 11,
      scrollWheelZoom: false,
    });

    L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; CARTO',
      maxZoom: 18,
    }).addTo(map);

    var ids = ["1", "2", "3", "4", "5", "6", "7", "9", "arex"];
    Promise.all(ids.map(loadLine)).then(function () {
      mapReady = true;
      var group = L.featureGroup(Object.keys(layers).map(function (k) { return layers[k]; }));
      try {
        map.fitBounds(group.getBounds(), { padding: [20, 20] });
      } catch (e) {}
      highlight("all");
      setTimeout(function () {
        map.invalidateSize();
      }, 200);
    });

    document.querySelectorAll("[data-metro-line]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        highlight(btn.getAttribute("data-metro-line"));
      });
    });
    var metroSelect = document.querySelector("[data-metro-select]");
    if (metroSelect) {
      metroSelect.addEventListener("change", function () {
        if (metroSelect.value) highlight(metroSelect.value);
      });
    }
  }

  // When switching to subway tab, invalidate map size (hidden panels break Leaflet sizing)
  document.addEventListener("click", function (e) {
    var tab = e.target.closest("[data-topic-tab]");
    if (!tab) return;
    if (tab.getAttribute("data-topic-tab") === "subway" && map) {
      setTimeout(function () {
        map.invalidateSize();
        if (activeLine && activeLine !== "all" && layers[activeLine]) {
          try {
            map.fitBounds(layers[activeLine].getBounds(), { padding: [30, 30], maxZoom: 12 });
          } catch (err) {}
        }
      }, 80);
    }
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initMap);
  } else {
    initMap();
  }
})();
