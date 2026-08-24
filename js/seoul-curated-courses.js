/**
 * Region curated day-course list for travel-courses hub.
 * Same chrome for every region: intro → course chips → detail (map + timetable).
 * Data: window.CURATED_COURSES_BY_REGION[regionId]
 * Seoul copy: travelCourses.seoulCurated.* — other regions: travelCourses.curated.*
 */
(function () {
  var ROOT_SEL = "[data-region-curated], [data-seoul-curated]";
  var liveMaps = [];
  var REGION_I18N = {
    seoul: "travelCourses.regionSeoul",
    gyeonggi: "travelCourses.regionGyeonggi",
    incheon: "travelCourses.regionIncheon",
    gyeongju: "travelCourses.regionGyeongju",
    busan: "travelCourses.regionBusan",
    jeju: "travelCourses.regionJeju",
  };

  var SLUG_COORDS = {
    "ssamziegil": [37.5741, 126.9847],
    "ikseon-dong": [37.5744, 126.9898],
    "n-seoul-tower": [37.5512, 126.9882],
    "namsan-park": [37.5545, 126.9838],
    "yongsan-station": [37.5299, 126.9648],
    "apgujeong-rodeo": [37.5275, 127.0406],
    "seoullo-7017": [37.5567, 126.9738],
    "euljiro": [37.566, 126.991],
    "seongsu-cafe": [37.5445, 127.0557],
    "seongsu-popup": [37.5448, 127.0518],
    "seongsu-dong": [37.5445, 127.0557],
    "ttukseom-hangang": [37.5305, 127.0668],
    "konkuk-food-street": [37.5407, 127.0692],
    "konkuk-university": [37.5404, 127.0796],
    "yeonnam-cafe": [37.5623, 126.9254],
    "yeonnam-dong": [37.5623, 126.9254],
    "hongdae-street": [37.5563, 126.9236],
    "hongdae-shops": [37.5555, 126.9218],
    "mangwon-hangang": [37.5556, 126.893],
    "byeolmadang-library": [37.5116, 127.0595],
    "garosu-gil": [37.521, 127.0229],
    "boteunsa": [37.5145, 127.0574],
    "seokchon-lake": [37.511, 127.103],
    "lotte-world": [37.5111, 127.098],
    "naksan-park": [37.5808, 127.0076],
    "ihwa-mural-village": [37.579, 127.0078],
    "daehangno": [37.5826, 127.002],
    "marronnier-park": [37.5804, 127.0027],
    "ddp": [37.5668, 127.0094],
    "the-hyundai-seoul": [37.5258, 126.9286],
    "yeouido": [37.5219, 126.9245],
    "seochon": [37.5788, 126.9688],
    "seochon-cafe": [37.5794, 126.9696],
    "gwathwamun": [37.5716, 126.9769],
    "hannam-dong": [37.5345, 127.0028],
    "itaewon-street": [37.5345, 126.9946],
    "gyeongnidan-gil": [37.5412, 126.9868],
    "haebangchon": [37.542, 126.9865],
    "yongridan-gil": [37.53, 126.9678],
    "bosingak": [37.57, 126.9833],
    "songridan-gil": [37.5055, 127.1065],
    "jamsil-skyline": [37.5126, 127.1025],
    "sebit-seom": [37.5125, 126.996],
    "hangang-yeouido": [37.5285, 126.934],
    "hangang-yeouido-cafe": [37.5285, 126.934],
    "hangang-banpo": [37.5105, 126.996],
    "hangang-banpo-fountain": [37.5142, 126.9968],
    "national-museum-korea": [37.5239, 126.9803],
    "cheongdam-fashion": [37.5245, 127.047],
    "cheonggyecheon": [37.5692, 126.9975],
    "cheonggyecheon-plaza": [37.5695, 126.9788],
    "gwangjang-market": [37.57, 126.9996],
    "insadong": [37.5717, 126.9858],
    "ichon-hangang": [37.5178, 126.9756],
    "dosan-park": [37.5226, 127.0356],
    "bukjeong-village": [37.5926, 127.0038],
    "seongbuk-dong": [37.5922, 126.9984],
    "hansung-univ": [37.5884, 127.0062],
  };

  var SLUG_ALIAS = {
    "hongdae-street": "hongdae",
    "hongdae-shops": "hongdae",
    "hangang-banpo-fountain": "hangang-banpo",
    "itaewon-street": "itaewon",
    "ddp": "dongdaemun",
    "byeolmadang-library": "coex",
    "n-seoul-tower": "namsan",
    "cheongdam-fashion": "cheongdam",
    "jamsil-skyline": "lotte-tower",
    "seongsu-cafe": "seongsu-dong",
    "seongsu-popup": "seongsu-dong",
    "yeonnam-cafe": "hongdae",
  };

  function t(key, fallback) {
    try {
      if (window.GuideI18n && typeof window.GuideI18n.t === "function") {
        return window.GuideI18n.t(key, fallback || key);
      }
    } catch (e) {
      /* ignore */
    }
    return fallback || key;
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function escapeAttr(s) {
    return escapeHtml(s).replace(/'/g, "&#39;");
  }

  function regionId(root) {
    if (!root) return "seoul";
    return (
      root.getAttribute("data-region-curated") ||
      (root.hasAttribute("data-seoul-curated") ? "seoul" : "seoul")
    );
  }

  function regionLabel(id) {
    return t(REGION_I18N[id] || "travelCourses.regionSeoul", id);
  }

  function fillRegion(str, name) {
    return String(str || "").replace(/\{region\}/g, name);
  }

  function coursesFor(region) {
    var byRegion = window.CURATED_COURSES_BY_REGION || {};
    if (Array.isArray(byRegion[region])) return byRegion[region];
    if (region === "seoul" && Array.isArray(window.SEOUL_CURATED_COURSES)) {
      return window.SEOUL_CURATED_COURSES;
    }
    return [];
  }

  function courseCopyBase(region, id) {
    if (region === "seoul") {
      return "travelCourses.seoulCurated.courses." + id;
    }
    return "travelCourses.curated." + region + ".courses." + id;
  }

  function courseCopy(region, id) {
    var base = courseCopyBase(region, id);
    return {
      title: t(base + ".title", id),
      summary: t(base + ".summary", ""),
      route: t(base + ".route", ""),
      tips: t(base + ".tips", ""),
    };
  }

  function stopCopy(region, id, index) {
    var base = courseCopyBase(region, id) + ".stops." + index;
    return {
      name: t(base + ".name", ""),
      desc: t(base + ".desc", ""),
    };
  }

  function chromeCopy(region) {
    var name = regionLabel(region);
    if (region === "seoul") {
      return {
        pickLabel: t("travelCourses.seoulCurated.pickLabel", "서울 추천 코스"),
        intro: t(
          "travelCourses.seoulCurated.intro",
          "서울을 하루 만에 알차게 도는 대표 코스입니다."
        ),
        guideEyebrow: t("travelCourses.seoulCurated.guideEyebrow", "서울 코스 안내"),
      };
    }
    return {
      pickLabel: fillRegion(
        t("travelCourses.curated.pickLabel", "{region} 추천 코스"),
        name
      ),
      intro: fillRegion(
        t(
          "travelCourses.curated.intro",
          "이 지역의 대표 코스 설명서입니다. 코스가 추가되면 타이틀을 고르고 소개·동선·시간표를 확인할 수 있습니다."
        ),
        name
      ),
      guideEyebrow: fillRegion(
        t("travelCourses.curated.guideEyebrow", "{region} 코스 안내"),
        name
      ),
    };
  }

  function imgSrc(path) {
    if (!path) return "../../Images/places/_types/city.jpg";
    if (path.indexOf("../../") === 0 || path.indexOf("../") === 0) return path;
    return "../../" + String(path).replace(/^\.\//, "");
  }

  function imageSlug(path) {
    return String(path || "")
      .split("/")
      .pop()
      .replace(/\.(jpg|jpeg|png|webp)$/i, "");
  }

  function placeIndex() {
    var index = {};
    (window.PLACES_COORDS || []).forEach(function (p) {
      index[p.slug] = p;
    });
    return index;
  }

  function lookupCoord(slug, index) {
    if (SLUG_COORDS[slug]) {
      return { lat: SLUG_COORDS[slug][0], lng: SLUG_COORDS[slug][1] };
    }
    if (index[slug]) return index[slug];
    var alias = SLUG_ALIAS[slug];
    if (alias && index[alias]) return index[alias];
    return null;
  }

  function diffHours(start, end) {
    if (!start || !end || start.indexOf(":") === -1 || end.indexOf(":") === -1) {
      return "";
    }
    var a = start.split(":").map(Number);
    var b = end.split(":").map(Number);
    var mins = b[0] * 60 + b[1] - (a[0] * 60 + a[1]);
    if (mins <= 0) return "";
    var hours = Math.round((mins / 60) * 10) / 10;
    return String(hours) + "h";
  }

  function courseMeta(course) {
    var stops = (course && course.stops) || [];
    var first = stops[0] && stops[0].time;
    var last = stops[stops.length - 1] && stops[stops.length - 1].time;
    return {
      totalTime: diffHours(first, last) || "-",
      stopCount: String(stops.length || 0),
      firstTime: first || "-",
      lastTime: last || "-",
    };
  }

  function icon(name) {
    if (name === "time") {
      return '<svg viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="7"></circle><path d="M10 6.5v4l2.8 1.7"></path></svg>';
    }
    if (name === "stops") {
      return '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M4.5 14.5c0-2.2 1.8-4 4-4h3c2.2 0 4 1.8 4 4"></path><circle cx="10" cy="6.8" r="2.4"></circle></svg>';
    }
    if (name === "start") {
      return '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M5.5 4.8v10.4L15 10z"></path></svg>';
    }
    return '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M5 10.6l3.2 3.2L15 6.8"></path></svg>';
  }

  function splitRoute(route) {
    return String(route || "")
      .split(/\s*→\s*|\s*->\s*|\s*➜\s*/)
      .map(function (part) {
        return part.trim();
      })
      .filter(Boolean);
  }

  function renderAside(copy, routeLabel, tipsLabel) {
    if (!copy.route && !copy.tips) return "";
    var routeHtml = "";
    if (copy.route) {
      var parts = splitRoute(copy.route);
      var hop =
        '<li class="course-guide-route__hop" aria-hidden="true">' +
        '<svg viewBox="0 0 20 20"><circle cx="10.2" cy="3.7" r="1.7"></circle><path d="M7.2 17.5l1.8-5.1-2.1-2.5 3.4-2.1 2.4 1.5 2.5 6.4"></path><path d="M8.4 8.7l3.8 2.1"></path></svg>' +
        "</li>";
      var flow = parts
        .map(function (name, idx) {
          var extra = "";
          if (idx === 0) extra = " is-start";
          if (idx === parts.length - 1) extra += " is-end";
          return (
            '<li class="course-guide-route__stop' +
            extra +
            '">' +
            '<span class="course-guide-route__num">' +
            (idx + 1) +
            "</span>" +
            '<span class="course-guide-route__name">' +
            escapeHtml(name) +
            "</span></li>" +
            (idx < parts.length - 1 ? hop : "")
          );
        })
        .join("");
      routeHtml =
        '<div class="course-guide-route">' +
        '<p class="course-guide-route__kicker">' +
        '<span class="course-guide-route__icon" aria-hidden="true">' +
        '<svg viewBox="0 0 20 20"><path d="M4 10h12"></path><path d="M12.5 6.5L16 10l-3.5 3.5"></path></svg>' +
        "</span>" +
        escapeHtml(routeLabel) +
        "</p>" +
        '<ol class="course-guide-route__flow">' +
        (flow ||
          '<li class="course-guide-route__stop"><span class="course-guide-route__name">' +
            escapeHtml(copy.route) +
            "</span></li>") +
        "</ol></div>";
    }
    var tipsHtml = "";
    if (copy.tips) {
      tipsHtml =
        '<div class="course-guide-tips">' +
        '<span class="course-guide-tips__icon" aria-hidden="true">' +
        '<svg viewBox="0 0 20 20"><path d="M10 3.2a5 5 0 0 0-2.8 9.1c.5.4.8 1 .8 1.6v.4h4v-.4c0-.6.3-1.2.8-1.6A5 5 0 0 0 10 3.2z"></path><path d="M8.2 15.8h3.6M8.6 17.4h2.8"></path></svg>' +
        "</span>" +
        '<div class="course-guide-tips__body">' +
        '<p class="course-guide-tips__kicker">' +
        escapeHtml(tipsLabel) +
        "</p>" +
        '<p class="course-guide-tips__text">' +
        escapeHtml(copy.tips) +
        "</p></div></div>";
    }
    return (
      '<div class="course-guide-aside">' + routeHtml + tipsHtml + "</div>"
    );
  }

  function renderMetaCards(course) {
    var meta = courseMeta(course);
    var labels = {
      total: t("travelCourses.seoulCurated.meta.totalTime", "총 소요"),
      stops: t("travelCourses.seoulCurated.meta.stops", "방문 포인트"),
      start: t("travelCourses.seoulCurated.meta.start", "시작 시간"),
      finish: t("travelCourses.seoulCurated.meta.finish", "마무리"),
    };
    return (
      '<div class="course-guide-meta">' +
      '<div class="course-guide-meta__item"><span class="course-guide-meta__icon">' +
      icon("time") +
      '</span><div class="course-guide-meta__text"><span class="course-guide-meta__label">' +
      escapeHtml(labels.total) +
      '</span><strong class="course-guide-meta__value">' +
      escapeHtml(meta.totalTime) +
      "</strong></div></div>" +
      '<div class="course-guide-meta__item"><span class="course-guide-meta__icon">' +
      icon("stops") +
      '</span><div class="course-guide-meta__text"><span class="course-guide-meta__label">' +
      escapeHtml(labels.stops) +
      '</span><strong class="course-guide-meta__value">' +
      escapeHtml(meta.stopCount) +
      "</strong></div></div>" +
      '<div class="course-guide-meta__item"><span class="course-guide-meta__icon">' +
      icon("start") +
      '</span><div class="course-guide-meta__text"><span class="course-guide-meta__label">' +
      escapeHtml(labels.start) +
      '</span><strong class="course-guide-meta__value">' +
      escapeHtml(meta.firstTime) +
      "</strong></div></div>" +
      '<div class="course-guide-meta__item"><span class="course-guide-meta__icon">' +
      icon("finish") +
      '</span><div class="course-guide-meta__text"><span class="course-guide-meta__label">' +
      escapeHtml(labels.finish) +
      '</span><strong class="course-guide-meta__value">' +
      escapeHtml(meta.lastTime) +
      "</strong></div></div>" +
      "</div>"
    );
  }

  function routePoints(course, region) {
    var index = placeIndex();
    var points = [];
    (course.stops || []).forEach(function (stop, idx) {
      var sc = stopCopy(region, course.id, idx);
      var hit = lookupCoord(stop.place || imageSlug(stop.image), index);
      if (hit && typeof hit.lat === "number" && typeof hit.lng === "number") {
        points.push({
          lat: hit.lat,
          lng: hit.lng,
          time: stop.time || "",
          name: sc.name || "",
        });
      }
    });
    return points;
  }

  var SAME_BUILDING = 0.00018;

  function sameBuilding(a, b) {
    return (
      Math.abs(a.lat - b.lat) < SAME_BUILDING &&
      Math.abs(a.lng - b.lng) < SAME_BUILDING
    );
  }

  function destroyMaps(root) {
    var maps = [];
    if (root) {
      maps = root.__courseMaps || [];
      root.__courseMaps = [];
    } else {
      maps = liveMaps.slice();
      liveMaps = [];
      document.querySelectorAll(ROOT_SEL).forEach(function (el) {
        maps = maps.concat(el.__courseMaps || []);
        el.__courseMaps = [];
      });
    }
    maps.forEach(function (map) {
      try {
        map.remove();
      } catch (e) {
        /* ignore */
      }
    });
  }

  function mountRouteMap(host) {
    if (typeof window.L === "undefined") return;
    var canvas = host.querySelector("[data-course-map]");
    if (!canvas) return;
    var raw = canvas.getAttribute("data-points") || "[]";
    var points = [];
    try {
      points = JSON.parse(raw);
    } catch (e) {
      return;
    }
    if (points.length < 2) return;

    var map = window.L.map(canvas, {
      scrollWheelZoom: false,
      zoomControl: true,
      attributionControl: true,
    });
    canvas.__leafletMap = map;
    window.L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 18,
      attribution: "&copy; OpenStreetMap",
    }).addTo(map);

    var latlngs = points.map(function (p) {
      return [p.lat, p.lng];
    });
    window.L.polyline(latlngs, {
      color: "#ffffff",
      weight: 8,
      opacity: 0.7,
      lineJoin: "round",
      lineCap: "round",
    }).addTo(map);
    var routeLine = window.L.polyline(latlngs, {
      color: "#1f5fe0",
      weight: 5,
      opacity: 0.95,
      lineJoin: "round",
      lineCap: "round",
    }).addTo(map);

    var pinLayer = window.L.layerGroup().addTo(map);

    function renderPins() {
      pinLayer.clearLayers();
      var items = points.map(function (p, idx) {
        return {
          lat: p.lat,
          lng: p.lng,
          num: idx + 1,
          name: p.name,
          time: p.time,
        };
      });
      var used = {};
      items.forEach(function (p, i) {
        if (used[i]) return;
        var group = [i];
        used[i] = true;
        items.forEach(function (q, j) {
          if (used[j]) return;
          if (sameBuilding(p, q)) {
            group.push(j);
            used[j] = true;
          }
        });
        group.forEach(function (gi, k) {
          var item = items[gi];
          var dx = 0;
          var dy = 0;
          if (group.length > 1) {
            var angle = (Math.PI * 2 * k) / group.length - Math.PI / 2;
            dx = Math.cos(angle) * 10;
            dy = Math.sin(angle) * 10;
          }
          var marker = window.L.marker([item.lat, item.lng], {
            zIndexOffset: item.num * 40,
            icon: window.L.divIcon({
              className: "course-guide-map-pin" + (item.num % 2 ? "" : " is-alt"),
              html: "<span>" + item.num + "</span>",
              iconSize: [28, 28],
              iconAnchor: [14 - dx, 14 - dy],
            }),
          });
          marker.bindPopup(
            "<strong>" +
              escapeHtml(item.name) +
              "</strong>" +
              (item.time ? "<br>" + escapeHtml(item.time) : "")
          );
          pinLayer.addLayer(marker);
        });
      });
      if (pinLayer.bringToFront) pinLayer.bringToFront();
    }

    map.fitBounds(window.L.latLngBounds(latlngs), { padding: [36, 36], maxZoom: 15 });
    renderPins();
    var owner =
      host.closest("[data-region-curated], [data-seoul-curated]") || null;
    if (owner) {
      owner.__courseMaps = owner.__courseMaps || [];
      owner.__courseMaps.push(map);
    } else {
      liveMaps.push(map);
    }
    setTimeout(function () {
      try {
        map.invalidateSize();
        if (routeLine.bringToFront) routeLine.bringToFront();
        renderPins();
      } catch (e) {
        /* ignore */
      }
    }, 80);
  }

  function renderRouteMap(course, region) {
    var points = routePoints(course, region);
    var label = t("travelCourses.seoulCurated.fullRouteLabel", "지도상 이동 경로");
    if (points.length < 2) return "";
    var legend = points
      .map(function (p, idx) {
        return (
          '<li class="course-guide-map__legend-item">' +
          '<span class="course-guide-map__legend-num">' +
          (idx + 1) +
          "</span>" +
          '<span class="course-guide-map__legend-copy">' +
          (p.time
            ? '<em>' + escapeHtml(p.time) + "</em>"
            : "") +
          escapeHtml(p.name) +
          "</span></li>"
        );
      })
      .join("");
    return (
      '<section class="course-guide-map">' +
      '<h4 class="course-guide-map__title">' +
      '<span class="course-guide-section-icon" aria-hidden="true"><svg viewBox="0 0 20 20"><path d="M10 17s5-4.4 5-8.2A5 5 0 0 0 5 8.8C5 12.6 10 17 10 17z"></path><circle cx="10" cy="8.6" r="1.7"></circle></svg></span>' +
      escapeHtml(label) +
      "</h4>" +
      '<div class="course-guide-map__layout">' +
      '<div class="course-guide-map__canvas" data-course-map data-points="' +
      escapeAttr(JSON.stringify(points)) +
      '"></div>' +
      '<ol class="course-guide-map__legend">' +
      legend +
      "</ol></div></section>"
    );
  }

  function renderStop(stop, sc, idx) {
    var n = idx + 1;
    var odd = idx % 2 === 0;
    var hasImg = !!(stop.image && String(stop.image).trim());
    var media = hasImg
      ? '<figure class="course-guide-stop__media">' +
        '<img class="course-guide-thumb" src="' +
        escapeAttr(imgSrc(stop.image)) +
        '" alt="" loading="lazy" decoding="async" onerror="this.onerror=null;this.src=\'../../Images/places/_types/city.jpg\'">' +
        "</figure>"
      : "";
    var copy =
      '<div class="course-guide-stop__copy">' +
      (stop.time
        ? '<span class="course-guide-stop__time">' +
          escapeHtml(stop.time) +
          "</span>"
        : "") +
      '<h4 class="course-guide-stop__name">' +
      escapeHtml(sc.name) +
      "</h4>" +
      (sc.desc
        ? '<p class="course-guide-stop__desc">' + escapeHtml(sc.desc) + "</p>"
        : "") +
      "</div>";
    return (
      '<li class="course-guide-stop ' +
      (odd ? "is-odd" : "is-even") +
      (idx === 0 ? " is-first" : "") +
      '">' +
      '<div class="course-guide-stop__stack">' +
      media +
      copy +
      "</div>" +
      '<div class="course-guide-stop__rail" aria-hidden="true">' +
      '<span class="course-guide-stop__dot">' +
      n +
      "</span></div></li>"
    );
  }

  function renderDetail(host, course, region) {
    if (!course) return;
    var root = host.closest(ROOT_SEL);
    destroyMaps(root);
    var copy = courseCopy(region, course.id);
    var chrome = chromeCopy(region);
    var tipsLabel = t("travelCourses.seoulCurated.tipsLabel", "팁");
    var routeLabel = t(
      "travelCourses.seoulCurated.routeLabel",
      "한눈에 보는 루트"
    );
    var scheduleLabel = t(
      "travelCourses.seoulCurated.scheduleLabel",
      "하루 일정"
    );
    var items = (course.stops || [])
      .map(function (stop, idx) {
        return renderStop(stop, stopCopy(region, course.id, idx), idx);
      })
      .join("");

    host.innerHTML =
      '<article class="course-guide-detail" data-seoul-detail>' +
      '<header class="course-guide-hero">' +
      '<img class="course-guide-hero__img" src="' +
      escapeAttr(imgSrc(course.cover)) +
      '" alt="" loading="lazy" decoding="async" onerror="this.onerror=null;this.src=\'../../Images/places/_types/city.jpg\'">' +
      '<div class="course-guide-hero__shade" aria-hidden="true"></div>' +
      '<div class="course-guide-hero__text">' +
      '<p class="course-guide-detail__eyebrow">' +
      escapeHtml(chrome.guideEyebrow) +
      "</p>" +
      '<h3 class="course-guide-detail__title">' +
      escapeHtml(copy.title) +
      "</h3>" +
      "</div></header>" +
      '<div class="course-guide-detail__body">' +
      (copy.summary
        ? '<p class="course-guide-detail__summary">' +
          escapeHtml(copy.summary) +
          "</p>"
        : "") +
      renderMetaCards(course) +
      renderAside(copy, routeLabel, tipsLabel) +
      '<section class="course-guide-schedule">' +
      '<h4 class="course-guide-schedule__title">' +
      '<span class="course-guide-section-icon" aria-hidden="true"><svg viewBox="0 0 20 20"><path d="M4 3.5h12v13H4z"></path><path d="M7 2.5v2M13 2.5v2M4 7.5h12"></path></svg></span>' +
      escapeHtml(scheduleLabel) +
      "</h4>" +
      '<ol class="course-guide-timeline">' +
      items +
      "</ol></section>" +
      renderRouteMap(course, region) +
      "</div></article>";

    mountRouteMap(host);
  }

  function renderEmpty(root, region) {
    destroyMaps(root);
    var chrome = chromeCopy(region);
    var name = regionLabel(region);
    var coming = fillRegion(
      t(
        "travelCourses.regionComingSoon",
        "{region} 추천 코스는 추후 추가될 예정입니다."
      ),
      name
    );
    var schedule = t(
      "travelCourses.scheduleComingSoon",
      "당일·1박2일 등 일정별 코스는 추후 추가될 예정입니다."
    );
    root.innerHTML =
      '<div class="course-guide">' +
      '<p class="course-guide__intro">' +
      escapeHtml(chrome.intro) +
      "</p>" +
      '<div class="travel-course-empty" role="status">' +
      '<p class="travel-course-empty__lead">' +
      escapeHtml(coming) +
      "</p>" +
      '<p class="travel-course-empty__note">' +
      escapeHtml(schedule) +
      "</p>" +
      "</div></div>";
  }

  function render(root) {
    var region = regionId(root);
    var list = coursesFor(region);
    if (!list.length) {
      renderEmpty(root, region);
      return;
    }

    var chrome = chromeCopy(region);
    var pickLabel = chrome.pickLabel;
    var intro = chrome.intro;
    var activeId =
      root.getAttribute("data-active-course") || (list[0] && list[0].id) || "";

    var options = list
      .map(function (c) {
        var title = courseCopy(region, c.id).title;
        return (
          '<option value="' +
          escapeAttr(c.id) +
          '"' +
          (c.id === activeId ? " selected" : "") +
          ">" +
          escapeHtml(title) +
          "</option>"
        );
      })
      .join("");

    var chips = list
      .map(function (c, idx) {
        var title = courseCopy(region, c.id).title;
        return (
          '<button type="button" class="course-guide-chip' +
          (c.id === activeId ? " is-active" : "") +
          '" data-seoul-course="' +
          escapeAttr(c.id) +
          '" aria-pressed="' +
          (c.id === activeId ? "true" : "false") +
          '"><span class="course-guide-chip__num">' +
          (idx + 1) +
          '</span><span class="course-guide-chip__label">' +
          escapeHtml(title) +
          "</span></button>"
        );
      })
      .join("");

    destroyMaps(root);
    root.innerHTML =
      '<div class="course-guide">' +
      '<p class="course-guide__intro">' +
      escapeHtml(intro) +
      "</p>" +
      '<label class="cat-select-wrap course-guide-select-wrap">' +
      '<span class="cat-select-label">' +
      escapeHtml(pickLabel) +
      "</span>" +
      '<select class="cat-select" data-seoul-course-select aria-label="' +
      escapeAttr(pickLabel) +
      '">' +
      options +
      "</select></label>" +
      '<div class="course-guide-chips" role="listbox" aria-label="' +
      escapeAttr(pickLabel) +
      '">' +
      chips +
      "</div>" +
      '<div class="course-guide-detail-host" data-seoul-detail-host></div></div>';

    var detailHost = root.querySelector("[data-seoul-detail-host]");
    var active =
      list.filter(function (c) {
        return c.id === activeId;
      })[0] || list[0];
    renderDetail(detailHost, active, region);

    var select = root.querySelector("[data-seoul-course-select]");
    if (select) {
      select.addEventListener("change", function () {
        root.setAttribute("data-active-course", select.value);
        render(root);
        root.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    }
    root.querySelectorAll("[data-seoul-course]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        root.setAttribute(
          "data-active-course",
          btn.getAttribute("data-seoul-course")
        );
        render(root);
      });
    });
  }

  function refreshAll() {
    document.querySelectorAll(ROOT_SEL).forEach(function (root) {
      render(root);
    });
  }

  function init() {
    refreshAll();
    document.addEventListener("guide:langchange", refreshAll);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
