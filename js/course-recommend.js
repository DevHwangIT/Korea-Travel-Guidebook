/**
 * Travel-courses hub: “스무고개” style itinerary quiz.
 * Places from window.PLACES_COORDS; meals from window.FOOD_RECOMMEND_CATALOG.
 * Saved courses: browser localStorage only (key koreaGuide.savedCourses).
 * Never sent to any server — stored on this device/browser only.
 */
(function () {
  var ROOT_SEL = "[data-course-quiz]";
  var SAVED_KEY = "koreaGuide.savedCourses";
  var SAVED_MAX = 12;
  var EXCLUDE_TYPES = {
    airport: 1,
    locker: 1,
    info: 1,
    "bus-terminal": 1,
    port: 1,
  };
  var NATURE_TYPES = { nature: 1, mountain: 1, beach: 1, lake: 1 };
  var CITY_TYPES = { city: 1, market: 1 };
  var reduceMotion =
    window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  var QUESTIONS = [
    {
      id: "party",
      options: [
        { id: "solo", image: "Images/places/quiz-party-solo.jpg" },
        { id: "couple", image: "Images/places/quiz-party-couple.jpg" },
        { id: "friends", image: "Images/places/quiz-party-friends.jpg" },
        { id: "family", image: "Images/places/quiz-party-family.jpg" },
      ],
    },
    {
      id: "region",
      options: [
        { id: "seoul", image: "Images/places/heritage/gyeongbok.jpg" },
        { id: "incheon", image: "Images/places/city/songdo.jpg" },
        { id: "gyeonggi", image: "Images/places/heritage/suwon.jpg" },
        { id: "gangwon", image: "Images/places/mountain/seoraksan.jpg" },
        { id: "chungcheong", image: "Images/places/heritage/gotsanseot.jpg" },
        { id: "jeolla", image: "Images/places/heritage/jeonju.jpg" },
        { id: "gyeongsang", image: "Images/places/heritage/bulguksa.jpg" },
        { id: "busan", image: "Images/places/beach/haeundae.jpg" },
        { id: "jeju", image: "Images/places/nature/seongsan.jpg" },
      ],
    },
    {
      id: "vibe",
      options: [
        { id: "nature", image: "Images/places/nature/naksan-park.jpg" },
        { id: "heritage", image: "Images/places/heritage/bukchon.jpg" },
        { id: "city", image: "Images/places/_courses/hongdae-street.jpg" },
      ],
    },
    {
      id: "mobility",
      options: [
        { id: "transit", image: "Images/places/bus-terminal/bus-terminal-seoul-express.jpg" },
        { id: "rent", image: "Images/places/nature/gapyeong.jpg" },
        { id: "mix", image: "Images/places/_courses/seoullo-7017.jpg" },
      ],
    },
    {
      id: "budget",
      options: [
        { id: "thrifty", image: "Images/places/market/gwangjang-market.jpg" },
        { id: "mid", image: "Images/places/food-baekban.jpg" },
        { id: "splurge", image: "Images/places/food-galbijjim.jpg" },
      ],
    },
    {
      id: "pace",
      options: [
        { id: "relax", image: "Images/places/_courses/dosan-park.jpg" },
        { id: "balanced", image: "Images/places/_courses/ikseon-dong.jpg" },
        { id: "active", image: "Images/places/city/namsan.jpg" },
      ],
    },
  ];

  var root = null;
  var dialog = null;
  var answers = {};
  var historyStack = [];
  var activeQuestionIds = [];
  var stepIndex = 0;
  var lastFocus = null;
  var lastCourse = null;
  var viewingSavedId = null;
  var pendingChoice = null;

  function t(key, fallback) {
    try {
      if (window.GuideI18n && typeof window.GuideI18n.t === "function") {
        return window.GuideI18n.t(key, fallback || key);
      }
      if (
        window.GuideI18n &&
        typeof window.GuideI18n.lookupWithFallback === "function"
      ) {
        var via = window.GuideI18n.lookupWithFallback(
          key,
          window.GuideI18n.getLang && window.GuideI18n.getLang()
        );
        if (via != null && via !== "") return String(via);
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

  function optionThumbSrc(opt) {
    if (opt && opt.image) {
      return "../../" + String(opt.image).replace(/^\.\//, "");
    }
    return "../../Images/places/_types/city.jpg";
  }

  function optionThumbFallback() {
    return "../../Images/places/_types/city.jpg";
  }

  function questionById(id) {
    for (var i = 0; i < QUESTIONS.length; i++) {
      if (QUESTIONS[i].id === id) return QUESTIONS[i];
    }
    return null;
  }

  function visibleQuestions() {
    return QUESTIONS.slice();
  }

  function placesList() {
    var list = window.PLACES_COORDS;
    return Array.isArray(list) ? list : [];
  }

  function foodCatalog() {
    var list = window.FOOD_RECOMMEND_CATALOG;
    return Array.isArray(list) ? list : [];
  }

  function dayCount(duration) {
    if (duration === "1n2d") return 2;
    if (duration === "2n3d") return 3;
    if (duration === "3n4d") return 4;
    return 1;
  }

  function stopsPerDay(pace) {
    if (pace === "relax") return 2;
    if (pace === "active") return 3;
    return 2;
  }

  function placeName(slug) {
    var key = "places." + slug + ".name";
    var name = t(key, "");
    if (name && name !== key) return name;
    return slug;
  }

  function placeHref(slug) {
    return "../transportation/places/" + slug + "/index.html";
  }

  function foodName(item) {
    if (!item) return "";
    if (item.titleKey) {
      var fromTitle = t(item.titleKey, "");
      if (fromTitle && fromTitle !== item.titleKey) return fromTitle;
    }
    var dishTitle = t("dishes." + item.id + ".title", "");
    if (dishTitle && dishTitle !== "dishes." + item.id + ".title") {
      return dishTitle;
    }
    return item.id;
  }

  function foodHref(item) {
    if (!item || !item.href) return "../food-life/index.html";
    return item.href;
  }

  function placeRecord(slug) {
    var list = placesList();
    for (var i = 0; i < list.length; i++) {
      if (list[i].slug === slug) return list[i];
    }
    return null;
  }

  function placeImage(slug, type) {
    var rec = placeRecord(slug);
    if (rec && rec.image) {
      return "../../" + String(rec.image).replace(/^\.\//, "");
    }
    if (type) return "../../Images/places/_types/" + type + ".jpg";
    return "../../Images/places/_types/city.jpg";
  }

  function foodImage(href) {
    if (!href) return "../../Images/places/food-baekban.jpg";
    if (href.indexOf("index.html") >= 0) {
      return href.replace(/index\.html$/, "media/cover.jpg");
    }
    return href.replace(/\/?$/, "/media/cover.jpg");
  }

  function placeDesc(slug) {
    var key = "places." + slug + ".desc";
    var val = t(key, "");
    return val && val !== key ? val : "";
  }

  function placeHow(slug) {
    var key = "places." + slug + ".how";
    var val = t(key, "");
    return val && val !== key ? val : "";
  }

  function placeFallbackDesc(slug, type) {
    var name = placeName(slug);
    var region = answerLabel("region", answers.region) || "";
    var typ = typeLabel(type) || type || "";
    return t(
      "travelCourses.quiz.placeFallbackDesc",
      "{name} — {region}의 대표 {type}입니다."
    )
      .replace("{name}", name)
      .replace("{region}", region)
      .replace("{type}", typ);
  }

  function placeHowFallback(slug) {
    var name = placeName(slug);
    return t(
      "travelCourses.quiz.howFallback",
      "카카오맵·네이버지도에서 '{name}'을(를) 검색해 대중교통·도보 경로를 확인하세요."
    ).replace("{name}", name);
  }

  function mealFallbackDesc(name) {
    return t(
      "travelCourses.quiz.mealFallbackDesc",
      "{name} — 현지에서 인기 있는 메뉴예요. 가이드 페이지에서 맛집 정보를 확인해 보세요."
    ).replace("{name}", name);
  }

  function placeActivity(type) {
    var key = "travelCourses.quiz.activity." + (type || "default");
    var val = t(key, "");
    if (val && val !== key) return val;
    return t(
      "travelCourses.quiz.activity.default",
      "대표 스팟을 둘러보며 사진을 남기고, 주변 산책·쇼핑도 함께 즐겨보세요."
    );
  }

  function foodDesc(id) {
    var desc = t("dishes." + id + ".desc", "");
    if (desc && desc !== "dishes." + id + ".desc") return desc;
    var about = t("dishes." + id + ".about", "");
    if (about && about !== "dishes." + id + ".about") return about;
    return "";
  }

  function foodActivity(mealKind) {
    var fallbacks = {
      lunch:
        "근처 맛집·식당가에서 천천히 식사하며 다음 일정을 준비해 보세요.",
      snack:
        "카페·디저트·길거리 간식으로 잠깐 쉬며 에너지를 보충해 보세요.",
      dinner: "하루를 마무리하며 현지인이 자주 찾는 메뉴를 맛보세요.",
    };
    return t(
      "travelCourses.quiz.mealActivity." + mealKind,
      fallbacks[mealKind] || fallbacks.lunch
    );
  }

  function haversineKm(a, b) {
    if (!a || !b || a.lat == null || b.lat == null) return 3;
    var R = 6371;
    var dLat = ((b.lat - a.lat) * Math.PI) / 180;
    var dLng = ((b.lng - a.lng) * Math.PI) / 180;
    var x =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos((a.lat * Math.PI) / 180) *
        Math.cos((b.lat * Math.PI) / 180) *
        Math.sin(dLng / 2) *
        Math.sin(dLng / 2);
    return R * 2 * Math.atan2(Math.sqrt(x), Math.sqrt(1 - x));
  }

  function travelMinutes(km, mobility) {
    if (km < 0.35) return 10;
    if (km < 0.8) return mobility === "rent" ? 12 : 15;
    var speed = mobility === "rent" ? 28 : mobility === "mix" ? 22 : 18;
    var mins = Math.round((km / speed) * 60 + 12);
    return Math.max(12, Math.min(90, mins));
  }

  function mealTravelMinutes(mobility) {
    if (mobility === "rent") return 12;
    if (mobility === "mix") return 18;
    return 20;
  }

  function postMealBufferMin() {
    return 10;
  }

  function dayEndLimitMin() {
    return 22 * 60 + 30;
  }

  function minToTime(totalMin) {
    var m = ((totalMin % 1440) + 1440) % 1440;
    var h = Math.floor(m / 60);
    var mm = m % 60;
    return (
      (h < 10 ? "0" : "") +
      h +
      ":" +
      (mm < 10 ? "0" : "") +
      mm
    );
  }

  function timeRange(startMin, durationMin) {
    return minToTime(startMin) + " – " + minToTime(startMin + durationMin);
  }

  function durationLabel(mins) {
    return t("travelCourses.quiz.durationStay", "약 {minutes}분").replace(
      "{minutes}",
      String(mins)
    );
  }

  function enrichPlace(place) {
    var desc = placeDesc(place.slug) || placeFallbackDesc(place.slug, place.type);
    var how = placeHow(place.slug) || placeHowFallback(place.slug);
    return {
      slug: place.slug,
      type: place.type,
      lat: place.lat,
      lng: place.lng,
      name: placeName(place.slug),
      href: placeHref(place.slug),
      image: placeImage(place.slug, place.type),
      imageFallback: placeImage("", place.type),
      desc: desc,
      how: how,
      activity: placeActivity(place.type),
    };
  }

  function enrichMeal(item, mealKind) {
    var name = foodName(item);
    var desc = foodDesc(item.id) || mealFallbackDesc(name);
    return {
      id: item.id,
      name: name,
      href: foodHref(item),
      image: foodImage(foodHref(item)),
      imageFallback: "../../Images/places/food-baekban.jpg",
      desc: desc,
      activity: foodActivity(mealKind),
      meal: mealKind,
    };
  }

  function orderPlacesByProximity(places) {
    if (places.length <= 1) return places.slice();
    var remaining = places.slice();
    var ordered = [remaining.shift()];
    while (remaining.length) {
      var last = ordered[ordered.length - 1];
      var bestIdx = 0;
      var bestDist = Infinity;
      for (var i = 0; i < remaining.length; i++) {
        var d = haversineKm(last, remaining[i]);
        if (d < bestDist) {
          bestDist = d;
          bestIdx = i;
        }
      }
      ordered.push(remaining.splice(bestIdx, 1)[0]);
    }
    return ordered;
  }

  function splitPlacesAcrossDays(places, days, perDay) {
    var ordered =
      places.length > 1 ? orderPlacesByProximity(places.slice()) : places.slice();
    var chunks = [];
    var idx = 0;
    for (var d = 0; d < days; d++) {
      var take = Math.min(perDay, ordered.length - idx);
      if (take < 1 && ordered.length) {
        idx = 0;
        take = Math.min(perDay, ordered.length);
      }
      if (take > 0) {
        chunks.push(ordered.slice(idx, idx + take));
        idx += take;
      } else {
        chunks.push([]);
      }
    }
    return chunks;
  }

  function mobilityModeKey(mobility) {
    if (mobility === "rent") return "modeRent";
    if (mobility === "mix") return "modeMix";
    return "modeTransit";
  }

  function formatMove(item) {
    var mode = t(
      "travelCourses.quiz." + (item.modeKey || mobilityModeKey(answers.mobility)),
      "이동"
    );
    var tmpl = t(
      "travelCourses.quiz.moveDetail",
      "↓ 약 {minutes}분 · {mode} ({from} → {to})"
    );
    return tmpl
      .replace("{minutes}", String(item.minutes || 20))
      .replace("{mode}", mode)
      .replace("{from}", item.fromName || "")
      .replace("{to}", item.toName || "");
  }

  function buildDayTimeline(placeRecords, lunch, snack, dinner, pace, mobility) {
    var stayPlace = { relax: 150, balanced: 100, active: 75 }[pace] || 100;
    var startMin = { relax: 600, balanced: 570, active: 540 }[pace] || 570;
    var lunchAnchor = { relax: 750, balanced: 720, active: 705 };
    var snackAnchor = { relax: 930, balanced: 900, active: 885 };
    var dinnerAnchor = { relax: 1110, balanced: 1095, active: 1080 };
    var endLimit = dayEndLimitMin();
    var cursor = startMin;
    var timeline = [];
    var prevPlace = null;
    var lastStopName = "";
    var modeKey = mobilityModeKey(mobility);

    function pushMove(fromName, toName, toPlace, fixedMinutes) {
      var mins;
      if (fixedMinutes != null) {
        mins = fixedMinutes;
      } else if (prevPlace && toPlace && toPlace.lat != null) {
        mins = travelMinutes(haversineKm(prevPlace, toPlace), mobility);
      } else {
        mins = mobility === "rent" ? 15 : 22;
      }
      timeline.push({
        kind: "move",
        minutes: mins,
        fromName: fromName || lastStopName || "",
        toName: toName,
        modeKey: modeKey,
      });
      cursor += mins;
    }

    function fitStay(requested, slot) {
      var stay = requested;
      var snackBudget = snack ? mealTravelMinutes(mobility) + 40 : 0;
      var dinnerBudget = dinner ? mealTravelMinutes(mobility) + 75 : 0;
      var eveningBudget = placeRecords[2]
        ? travelMinutes(4, mobility) + Math.round(stayPlace * 0.85)
        : 0;
      var tail = 0;
      if (slot === "morning") {
        tail = dinnerBudget + snackBudget + eveningBudget;
      } else if (slot === "afternoon") {
        tail = snackBudget + eveningBudget + dinnerBudget;
      } else if (slot === "evening") {
        tail = dinnerBudget;
      }
      if (cursor + stay + tail > endLimit) {
        stay = Math.max(45, endLimit - cursor - tail);
      }
      return stay;
    }

    function pushPlace(rec, slot, stayOverride) {
      var ep = enrichPlace(rec);
      var requested =
        stayOverride != null
          ? stayOverride
          : slot === "evening"
            ? Math.round(stayPlace * 0.85)
            : stayPlace;
      var stay = fitStay(requested, slot);
      if (prevPlace) {
        pushMove(lastStopName || placeName(prevPlace.slug), ep.name, rec);
      }
      timeline.push({
        kind: "place",
        time: minToTime(cursor),
        timeRange: timeRange(cursor, stay),
        durationMin: stay,
        slot: slot,
        slug: ep.slug,
        type: ep.type,
        href: ep.href,
        name: ep.name,
        image: ep.image,
        imageFallback: ep.imageFallback,
        desc: ep.desc,
        how: ep.how,
        activity: ep.activity,
      });
      cursor += stay;
      prevPlace = rec;
      lastStopName = ep.name;
    }

    function pushMeal(meal, anchorMin, durationMin) {
      if (!meal) return;
      var travel =
        meal.meal === "snack"
          ? Math.max(10, Math.round(mealTravelMinutes(mobility) * 0.75))
          : mealTravelMinutes(mobility);
      pushMove(
        lastStopName || (prevPlace ? placeName(prevPlace.slug) : ""),
        meal.name,
        null,
        travel
      );
      cursor = Math.max(cursor, anchorMin);
      timeline.push({
        kind: "meal",
        time: minToTime(cursor),
        timeRange: timeRange(cursor, durationMin),
        durationMin: durationMin,
        meal: meal.meal,
        id: meal.id,
        name: meal.name,
        href: meal.href,
        image: meal.image,
        imageFallback: meal.imageFallback,
        desc: meal.desc,
        activity: meal.activity,
      });
      cursor += durationMin + postMealBufferMin();
      lastStopName = meal.name;
    }

    if (placeRecords[0]) {
      pushPlace(placeRecords[0], "morning");
    }
    if (lunch) {
      pushMeal(lunch, lunchAnchor[pace] || 720, 60);
    }
    if (placeRecords[1]) {
      pushPlace(placeRecords[1], "afternoon");
    }
    if (snack) {
      var snackDur = snack.meal === "snack" ? 40 : 45;
      if (cursor + mealTravelMinutes(mobility) + snackDur + 90 <= endLimit) {
        pushMeal(snack, snackAnchor[pace] || 900, snackDur);
      }
    }
    var eveningOk =
      !placeRecords[2] ||
      cursor +
        travelMinutes(
          prevPlace && placeRecords[2]
            ? haversineKm(prevPlace, placeRecords[2])
            : 3,
          mobility
        ) +
        Math.round(stayPlace * 0.85) +
        (dinner ? mealTravelMinutes(mobility) + 75 : 0) <=
        endLimit;
    if (placeRecords[2] && eveningOk) {
      pushPlace(placeRecords[2], "evening", Math.round(stayPlace * 0.85));
    }
    if (dinner) {
      var dinnerStart = Math.max(cursor, dinnerAnchor[pace] || 1110);
      if (dinnerStart + 75 <= endLimit + 15) {
        pushMeal(dinner, dinnerAnchor[pace] || 1110, 75);
      }
    }

    return timeline;
  }

  function buildCourse() {
    var days = dayCount(answers.duration || "day");
    var pace = answers.pace || "balanced";
    var mobility = answers.mobility || "transit";
    var perDay = stopsPerDay(pace);
    var needPlaces = Math.max(days * perDay, days);
    var places = pickTopPlaces(needPlaces);
    var dayChunks = splitPlacesAcrossDays(places, days, perDay);
    var meals = pickFoods(days * 2, "meal");
    var snacks = pickFoods(days, "snack");

    var courseDays = [];
    var mi = 0;
    var si = 0;
    for (var d = 0; d < days; d++) {
      var chunk = dayChunks[d] || [];
      var lunchItem = meals[mi % Math.max(meals.length, 1)] || null;
      mi++;
      var dinnerItem = meals[mi % Math.max(meals.length, 1)] || null;
      mi++;
      var snackItem = snacks[si % Math.max(snacks.length, 1)] || null;
      si++;
      var lunch = lunchItem ? enrichMeal(lunchItem, "lunch") : null;
      var snack = snackItem ? enrichMeal(snackItem, "snack") : null;
      var dinner = dinnerItem ? enrichMeal(dinnerItem, "dinner") : null;

      courseDays.push({
        day: d + 1,
        timeline: buildDayTimeline(
          chunk,
          lunch,
          snack,
          dinner,
          pace,
          mobility
        ),
      });
    }

    return {
      id: "c_" + Date.now().toString(36),
      createdAt: Date.now(),
      answers: Object.assign({}, answers),
      days: courseDays,
      reason: t(
        "travelCourses.quiz.defaultReason",
        "답변과 이동 거리를 반영해, 시간대별로 현실적인 코스를 구성했어요."
      ),
    };
  }

  function scorePlace(place) {
    var s = 1;
    var type = place.type || "";
    var vibe = answers.vibe;
    var mobility = answers.mobility;
    var pace = answers.pace;
    var region = answers.region;

    if (vibe === "nature") {
      if (NATURE_TYPES[type]) s += 8;
      else if (type === "heritage") s += 1;
      else if (CITY_TYPES[type]) s -= 1;
    } else if (vibe === "heritage") {
      if (type === "heritage") s += 9;
      else if (NATURE_TYPES[type]) s += 2;
      else if (CITY_TYPES[type]) s += 1;
    } else if (vibe === "city") {
      if (type === "city") s += 8;
      else if (type === "market") s += 5;
      else if (type === "heritage") s += 2;
      else if (NATURE_TYPES[type]) s += 1;
    }

    if (mobility === "transit") {
      if (CITY_TYPES[type] || type === "heritage") s += 3;
      if (type === "mountain") s -= 2;
      if (region === "jeju" && NATURE_TYPES[type]) s -= 1;
    } else if (mobility === "rent") {
      if (NATURE_TYPES[type] || type === "mountain") s += 4;
      if (region === "jeju") s += 2;
      if (type === "city") s += 1;
    } else {
      s += 1;
    }

    if (pace === "relax") {
      if (NATURE_TYPES[type] || type === "heritage") s += 2;
      if (type === "city") s += 1;
    } else if (pace === "active") {
      if (type === "mountain" || type === "city" || type === "beach") s += 2;
    }

    if (
      answers.party === "family" &&
      (type === "nature" || type === "beach" || type === "lake")
    ) {
      s += 2;
    }
    if (answers.party === "friends" && type === "city") s += 2;
    if (
      answers.party === "couple" &&
      (type === "heritage" || NATURE_TYPES[type])
    ) {
      s += 1;
    }
    if (answers.party === "solo" && (CITY_TYPES[type] || type === "heritage")) {
      s += 1;
    }

    return s;
  }

  function foodTagScores() {
    var tags = {};
    var budget = answers.budget;
    var party = answers.party;
    var pace = answers.pace;

    if (budget === "thrifty") {
      tags.quickbite = 4;
      tags.portable = 3;
      tags.mild = 2;
      tags.noodles = 2;
      tags.combo = 2;
    } else if (budget === "splurge") {
      tags.meat = 4;
      tags.grill = 3;
      tags.hearty = 3;
      tags.soup = 1;
    } else {
      tags.balanced = 2;
      tags.hearty = 2;
      tags.mild = 1;
    }

    if (party === "friends" || party === "family") {
      tags.hearty = (tags.hearty || 0) + 3;
      tags.grill = (tags.grill || 0) + 2;
      tags.meat = (tags.meat || 0) + 2;
    } else if (party === "solo") {
      tags.portable = (tags.portable || 0) + 2;
      tags.quickbite = (tags.quickbite || 0) + 2;
      tags.light = (tags.light || 0) + 1;
    } else {
      tags.balanced = (tags.balanced || 0) + 1;
    }

    if (pace === "relax") {
      tags.soup = (tags.soup || 0) + 1;
      tags.warm = (tags.warm || 0) + 1;
    } else if (pace === "active") {
      tags.quickbite = (tags.quickbite || 0) + 1;
      tags.noodles = (tags.noodles || 0) + 1;
    }

    return tags;
  }

  function scoreFood(item, tagScores, preferKind) {
    var s = 0;
    if (preferKind && item.kind === preferKind) s += 5;
    else if (item.kind === "meal") s += 2;
    else if (item.kind === "dessert") s += 2;
    else if (item.kind === "quick") s += 1;
    var tags = item.tags || [];
    for (var i = 0; i < tags.length; i++) {
      s += tagScores[tags[i]] || 0;
    }
    return s;
  }

  function regionSet(id) {
    if (id === "gyeongsang" || id === "gyeongju") {
      return { gyeongsang: 1, gyeongju: 1 };
    }
    var set = {};
    if (id) set[id] = 1;
    return set;
  }

  function placeInRegion(place, region) {
    return !!(place && regionSet(region)[place.region]);
  }

  function pickTopPlaces(n) {
    var region = answers.region;
    var scored = [];
    var list = placesList();
    for (var i = 0; i < list.length; i++) {
      var p = list[i];
      if (!p || !p.slug) continue;
      if (EXCLUDE_TYPES[p.type]) continue;
      if (!placeInRegion(p, region)) continue;
      scored.push({ place: p, score: scorePlace(p) });
    }
    scored.sort(function (a, b) {
      if (b.score !== a.score) return b.score - a.score;
      return a.place.slug < b.place.slug ? -1 : 1;
    });

    var picked = [];
    var used = {};
    for (var j = 0; j < scored.length && picked.length < n; j++) {
      var slug = scored[j].place.slug;
      if (used[slug]) continue;
      used[slug] = 1;
      picked.push(scored[j].place);
    }
    return picked;
  }

  function pickFoods(count, role) {
    var tagScores = foodTagScores();
    var preferKind = role === "snack" ? "dessert" : "meal";
    var items = foodCatalog().filter(function (it) {
      if (!it) return false;
      if (role === "snack") {
        return it.kind === "dessert" || it.kind === "quick";
      }
      return it.kind === "meal" || it.kind === "quick";
    });
    if (!items.length) {
      items = foodCatalog().filter(function (it) {
        return it && it.kind !== "dessert";
      });
    }
    if (!items.length) items = foodCatalog();

    var ranked = items
      .map(function (it) {
        var bonus = 0;
        if (role === "snack") {
          if (it.kind === "dessert") bonus += 4;
          if (it.kind === "quick") bonus += 2;
        }
        return {
          item: it,
          score: scoreFood(it, tagScores, preferKind) + bonus,
        };
      })
      .sort(function (a, b) {
        if (b.score !== a.score) return b.score - a.score;
        return a.item.id < b.item.id ? -1 : 1;
      });

    var out = [];
    var used = {};
    for (var i = 0; i < ranked.length && out.length < count; i++) {
      var id = ranked[i].item.id;
      if (used[id]) continue;
      used[id] = 1;
      out.push(ranked[i].item);
    }
    return out;
  }

  function foodById(id) {
    if (!id) return null;
    var list = foodCatalog();
    for (var i = 0; i < list.length; i++) {
      if (list[i] && list[i].id === id) return list[i];
    }
    return null;
  }

  function localizeTimelineItem(item, mobility) {
    if (!item) return item;
    if (item.kind === "move") {
      return {
        kind: "move",
        minutes: item.minutes,
        fromName: item.fromName || "",
        toName: item.toName || "",
        modeKey:
          item.modeKey ||
          (item.tipKey === "moveRent"
            ? "modeRent"
            : item.tipKey === "moveMix"
              ? "modeMix"
              : mobilityModeKey(mobility)),
      };
    }
    if (item.kind === "place" && item.slug) {
      var rec = placeRecord(item.slug) || {
        slug: item.slug,
        type: item.type,
        lat: item.lat,
        lng: item.lng,
      };
      var ep = enrichPlace(rec);
      return Object.assign({}, item, {
        name: ep.name,
        href: ep.href,
        image: ep.image || item.image,
        imageFallback: ep.imageFallback,
        desc: ep.desc,
        how: ep.how,
        activity: ep.activity,
        type: ep.type || item.type,
      });
    }
    if (item.kind === "meal" && item.id) {
      var catalogItem = foodById(item.id);
      var mealKind = item.meal || "lunch";
      if (catalogItem) {
        var em = enrichMeal(catalogItem, mealKind);
        return Object.assign({}, item, {
          name: em.name,
          href: em.href,
          image: em.image || item.image,
          imageFallback: em.imageFallback,
          desc: em.desc,
          activity: em.activity,
        });
      }
      return Object.assign({}, item, {
        name: foodName({ id: item.id, titleKey: "dishes." + item.id + ".title" }) || item.name,
        desc: foodDesc(item.id) || item.desc,
        activity: foodActivity(mealKind),
      });
    }
    return item;
  }

  function localizeCourse(course) {
    if (!course || !course.days) return course;
    var mobility = (course.answers && course.answers.mobility) || answers.mobility;
    var days = course.days.map(function (day) {
      var timeline = (day.timeline || []).map(function (item) {
        return localizeTimelineItem(item, mobility);
      });
      // Refresh move from/to names from neighboring stops
      for (var i = 0; i < timeline.length; i++) {
        if (timeline[i].kind !== "move") continue;
        var prev = null;
        var next = null;
        for (var p = i - 1; p >= 0; p--) {
          if (timeline[p].kind === "place" || timeline[p].kind === "meal") {
            prev = timeline[p];
            break;
          }
        }
        for (var n = i + 1; n < timeline.length; n++) {
          if (timeline[n].kind === "place" || timeline[n].kind === "meal") {
            next = timeline[n];
            break;
          }
        }
        if (prev && prev.name) timeline[i].fromName = prev.name;
        if (next && next.name) timeline[i].toName = next.name;
      }
      return Object.assign({}, day, { timeline: timeline });
    });
    return Object.assign({}, course, {
      days: days,
      reason: t(
        "travelCourses.quiz.defaultReason",
        "답변과 이동 거리를 반영해, 시간대별로 현실적인 코스를 구성했어요."
      ),
    });
  }

  function loadSaved() {
    try {
      var raw = window.localStorage && localStorage.getItem(SAVED_KEY);
      if (!raw) return [];
      var list = JSON.parse(raw);
      return Array.isArray(list) ? list : [];
    } catch (e) {
      return [];
    }
  }

  function writeSaved(list) {
    try {
      if (!window.localStorage) return false;
      localStorage.setItem(SAVED_KEY, JSON.stringify(list.slice(0, SAVED_MAX)));
      return true;
    } catch (e) {
      return false;
    }
  }

  function saveCourse(course) {
    if (!course || !course.days || !course.days.length) return false;
    var list = loadSaved();
    var payload = {
      id: course.id || "c_" + Date.now().toString(36),
      createdAt: course.createdAt || Date.now(),
      answers: course.answers || {},
      days: course.days,
      reason: course.reason || "",
    };
    list = list.filter(function (x) {
      return x && x.id !== payload.id;
    });
    list.unshift(payload);
    return writeSaved(list);
  }

  function deleteSaved(id) {
    var list = loadSaved().filter(function (x) {
      return x && x.id !== id;
    });
    return writeSaved(list);
  }

  function answerLabel(key, value) {
    return t(
      "travelCourses.quiz.questions." + key + ".options." + value,
      value || ""
    );
  }

  function summaryChipsHtml(ans) {
    var src = ans || answers;
    var keys = ["party", "region", "vibe", "mobility", "budget", "pace"];
    return keys
      .map(function (k) {
        if (!src[k]) return "";
        return (
          '<span class="course-quiz-chip">' +
          escapeHtml(answerLabel(k, src[k])) +
          "</span>"
        );
      })
      .join("");
  }

  function formatSavedAt(ts) {
    try {
      var d = new Date(ts);
      if (isNaN(d.getTime())) return "";
      var y = d.getFullYear();
      var m = String(d.getMonth() + 1).padStart(2, "0");
      var day = String(d.getDate()).padStart(2, "0");
      var hh = String(d.getHours()).padStart(2, "0");
      var mm = String(d.getMinutes()).padStart(2, "0");
      return y + "-" + m + "-" + day + " " + hh + ":" + mm;
    } catch (e) {
      return "";
    }
  }

  function courseTitle(course) {
    var a = (course && course.answers) || {};
    var region = answerLabel("region", a.region) || "";
    if (region) return region;
    return t("travelCourses.quiz.resultEyebrow", "맞춤 코스");
  }

  function mountDialogOnBody() {
    if (!dialog || !document.body) return;
    if (dialog.parentNode !== document.body) {
      document.body.appendChild(dialog);
    }
  }

  function setOpen(open) {
    if (!dialog || !root) return;
    if (open) mountDialogOnBody();
    dialog.hidden = !open;
    root.classList.toggle("is-quiz-open", open);
    document.body.classList.toggle("course-quiz-lock", open);
    if (open) {
      lastFocus = document.activeElement;
      var closeBtn = dialog.querySelector("[data-course-quiz-close]");
      if (closeBtn) closeBtn.focus();
    } else if (lastFocus && lastFocus.focus) {
      lastFocus.focus();
      resetToolbarSaveBtn();
    }
  }

  function renderProgress(current, total) {
    var el = dialog.querySelector("[data-course-quiz-progress]");
    if (!el) return;
    var tmpl = t("travelCourses.quiz.progress", "{current} / {total}");
    el.textContent = tmpl
      .replace("{current}", String(current))
      .replace("{total}", String(total));
    el.setAttribute("aria-valuenow", String(current));
    el.setAttribute("aria-valuemax", String(total));
    var bar = dialog.querySelector("[data-course-quiz-bar]");
    if (bar) {
      var pct = total > 0 ? Math.round((current / total) * 100) : 0;
      bar.style.width = pct + "%";
    }
  }

  function setPendingChoice(optionId) {
    pendingChoice = optionId;
    if (!dialog) return;
    dialog.querySelectorAll("[data-course-quiz-option]").forEach(function (btn) {
      var on = btn.getAttribute("data-course-quiz-option") === optionId;
      btn.classList.toggle("is-selected", on);
      btn.setAttribute("aria-checked", on ? "true" : "false");
    });
    var nextBtn = dialog.querySelector("[data-course-quiz-next]");
    if (nextBtn) nextBtn.disabled = !optionId;
  }

  function renderQuestion() {
    var panel = dialog.querySelector("[data-course-quiz-panel]");
    if (!panel) return;
    viewingSavedId = null;

    var qid = activeQuestionIds[stepIndex];
    var q = questionById(qid);
    if (!q) {
      renderResult();
      return;
    }

    resetToolbarSaveBtn();

    var total = activeQuestionIds.length;
    renderProgress(stepIndex + 1, total);

    var backBtn = dialog.querySelector("[data-course-quiz-back]");
    if (backBtn) backBtn.hidden = historyStack.length === 0;

    var title = dialog.querySelector("[data-course-quiz-heading]");
    if (title) title.textContent = t("travelCourses.quiz.title", "여행 코스 추천");

    var prompt = t("travelCourses.quiz.questions." + q.id + ".prompt", q.id);
    var lead = t("travelCourses.quiz.questions." + q.id + ".lead", "");
    if (lead === "travelCourses.quiz.questions." + q.id + ".lead") lead = "";
    var nextLbl = t("travelCourses.quiz.next", "다음");
    var fallbackImg = optionThumbFallback();
    pendingChoice = answers[qid] || null;

    var optsHtml = q.options
      .map(function (opt) {
        var selected = pendingChoice === opt.id;
        var label = t(
          "travelCourses.quiz.questions." + q.id + ".options." + opt.id,
          opt.id
        );
        var hint = t(
          "travelCourses.quiz.questions." + q.id + ".hints." + opt.id,
          ""
        );
        if (
          hint ===
          "travelCourses.quiz.questions." + q.id + ".hints." + opt.id
        ) {
          hint = "";
        }
        var src = optionThumbSrc(opt);
        return (
          '<button type="button" class="course-quiz-option' +
          (selected ? " is-selected" : "") +
          '" data-course-quiz-option="' +
          opt.id +
          '" role="radio" aria-checked="' +
          (selected ? "true" : "false") +
          '">' +
          '<img class="course-quiz-option__thumb" src="' +
          escapeAttr(src) +
          '" alt="" loading="lazy" decoding="async" onerror="this.onerror=null;this.src=\'' +
          escapeAttr(fallbackImg) +
          '\'">' +
          '<span class="course-quiz-option__copy">' +
          '<span class="course-quiz-option__label">' +
          escapeHtml(label) +
          "</span>" +
          (hint
            ? '<span class="course-quiz-option__hint">' +
              escapeHtml(hint) +
              "</span>"
            : "") +
          "</span>" +
          '<span class="course-quiz-option__radio" aria-hidden="true"></span>' +
          "</button>"
        );
      })
      .join("");

    panel.innerHTML =
      '<div class="course-quiz-step"' +
      (reduceMotion ? "" : ' data-anim="in"') +
      ">" +
      '<p class="course-quiz-prompt">' +
      escapeHtml(prompt) +
      "</p>" +
      (lead
        ? '<p class="course-quiz-lead">' + escapeHtml(lead) + "</p>"
        : "") +
      '<div class="course-quiz-options" role="radiogroup" aria-label="' +
      escapeAttr(prompt) +
      '">' +
      optsHtml +
      "</div>" +
      '<button type="button" class="course-quiz-next" data-course-quiz-next' +
      (pendingChoice ? "" : " disabled") +
      ">" +
      escapeHtml(nextLbl) +
      "</button></div>";

    panel.querySelectorAll("[data-course-quiz-option]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        setPendingChoice(btn.getAttribute("data-course-quiz-option"));
      });
    });
    var nextBtn = panel.querySelector("[data-course-quiz-next]");
    if (nextBtn) {
      nextBtn.addEventListener("click", function () {
        if (pendingChoice) chooseOption(pendingChoice);
      });
    }
  }

  function typeLabel(type) {
    return t("travelCourses.quiz.placeType." + type, type || "");
  }

  function mealLabel(kind) {
    var fallbacks = {
      lunch: "점심",
      snack: "간식·디저트",
      dinner: "저녁",
    };
    return t("travelCourses.quiz.meal." + kind, fallbacks[kind] || kind);
  }

  function cardCopyHtml(item, badge, isMeal) {
    var introLbl = t("travelCourses.quiz.introLabel", "소개");
    var doLbl = t("travelCourses.quiz.doLabel", "이렇게 즐겨보세요");
    var howLbl = t("travelCourses.quiz.howLabel", "가는 방법");
    var html =
      '<div class="course-tl-card__copy">' +
      '<span class="course-tl-badge">' +
      escapeHtml(badge) +
      "</span>" +
      '<span class="course-tl-name">' +
      escapeHtml(item.name) +
      "</span>";
    if (item.desc) {
      html +=
        '<p class="course-tl-desc"><strong>' +
        escapeHtml(introLbl) +
        "</strong> " +
        escapeHtml(item.desc) +
        "</p>";
    }
    if (item.activity) {
      html +=
        '<p class="course-tl-activity"><strong>' +
        escapeHtml(doLbl) +
        "</strong> " +
        escapeHtml(item.activity) +
        "</p>";
    }
    if (!isMeal && item.how) {
      html +=
        '<p class="course-tl-how"><strong>' +
        escapeHtml(howLbl) +
        "</strong> " +
        escapeHtml(item.how) +
        "</p>";
    }
    if (item.durationMin) {
      html +=
        '<p class="course-tl-hint">' +
        escapeHtml(durationLabel(item.durationMin)) +
        "</p>";
    }
    html += "</div>";
    return html;
  }

  function thumbHtml(item) {
    var src = item.image || "";
    var fallback = item.imageFallback || "../../Images/menu/travel-courses.png";
    if (!src) return "";
    return (
      '<img class="course-tl-thumb" src="' +
      escapeAttr(src) +
      '" alt="' +
      escapeAttr(item.name || "") +
      '" loading="lazy" decoding="async" onerror="this.onerror=null;this.src=\'' +
      escapeAttr(fallback) +
      "'\">"
    );
  }

  function timelineItemHtml(item, isLast) {
    if (item.kind === "move") {
      return (
        '<li class="course-tl-item course-tl-item--move' +
        (isLast ? " is-last" : "") +
        '">' +
        '<div class="course-tl-rail"><span class="course-tl-dot course-tl-dot--move"></span></div>' +
        '<div class="course-tl-body"><p class="course-tl-move">' +
        escapeHtml(formatMove(item)) +
        "</p></div></li>"
      );
    }

    var timeLine = item.timeRange || item.time || "";

    if (item.kind === "meal") {
      return (
        '<li class="course-tl-item course-tl-item--meal' +
        (isLast ? " is-last" : "") +
        '">' +
        '<div class="course-tl-rail"><span class="course-tl-dot course-tl-dot--meal"></span></div>' +
        '<div class="course-tl-body">' +
        '<p class="course-tl-time">' +
        escapeHtml(timeLine) +
        "</p>" +
        '<a class="course-tl-card course-tl-card--meal course-tl-card--photo" href="' +
        escapeAttr(item.href) +
        '">' +
        thumbHtml(item) +
        cardCopyHtml(item, mealLabel(item.meal), true) +
        "</a></div></li>"
      );
    }

    return (
      '<li class="course-tl-item course-tl-item--place' +
      (isLast ? " is-last" : "") +
      '">' +
      '<div class="course-tl-rail"><span class="course-tl-dot"></span></div>' +
      '<div class="course-tl-body">' +
      '<p class="course-tl-time">' +
      escapeHtml(timeLine) +
      "</p>" +
      '<a class="course-tl-card course-tl-card--photo" href="' +
      escapeAttr(item.href) +
      '">' +
      thumbHtml(item) +
      cardCopyHtml(item, typeLabel(item.type), false) +
      "</a></div></li>"
    );
  }

  function daysTimelineHtml(course) {
    if (
      !course.days.length ||
      !course.days.some(function (d) {
        return d.timeline && d.timeline.length;
      })
    ) {
      return (
        '<p class="course-quiz-result__reason">' +
        escapeHtml(
          t(
            "travelCourses.quiz.emptyPlaces",
            "이 지역에 맞는 명소 데이터가 부족해요. 다른 지역을 골라 보세요."
          )
        ) +
        "</p>"
      );
    }

    return course.days
      .map(function (day) {
        var dayTitle = t("travelCourses.quiz.dayLabel", "{n}일차").replace(
          "{n}",
          String(day.day)
        );
        var items = day.timeline || [];
        var itemsHtml = items
          .map(function (item, idx) {
            return timelineItemHtml(item, idx === items.length - 1);
          })
          .join("");
        return (
          '<section class="course-quiz-day">' +
          '<h4 class="course-quiz-day__title">' +
          escapeHtml(dayTitle) +
          "</h4>" +
          '<ol class="course-tl">' +
          itemsHtml +
          "</ol></section>"
        );
      })
      .join("");
  }

  function saveIconHtml() {
    return (
      '<svg class="course-quiz-save-icon__svg" width="20" height="20" viewBox="0 0 24 24" aria-hidden="true" focusable="false">' +
      '<path class="course-quiz-save-icon__outline" d="M7 4h10a1 1 0 0 1 1 1v15.2a.8.8 0 0 1-1.24.67L12 17.5l-4.76 3.37A.8.8 0 0 1 6 20.2V5a1 1 0 0 1 1-1z" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linejoin="round"/>' +
      '<path class="course-quiz-save-icon__filled" d="M7 4h10a1 1 0 0 1 1 1v15.2a.8.8 0 0 1-1.24.67L12 17.5l-4.76 3.37A.8.8 0 0 1 6 20.2V5a1 1 0 0 1 1-1z" fill="currentColor" stroke="none"/>' +
      "</svg>"
    );
  }

  function resetToolbarSaveBtn() {
    var saveBtn = dialog && dialog.querySelector("[data-course-quiz-save]");
    if (!saveBtn) return;
    saveBtn.hidden = true;
    saveBtn.disabled = false;
    saveBtn.classList.remove("is-saved");
    var saveLabel = t("travelCourses.quiz.save", "내 기기에 저장");
    saveBtn.setAttribute("aria-label", saveLabel);
    saveBtn.setAttribute("title", saveLabel);
    saveBtn.innerHTML = saveIconHtml();
  }

  function showToolbarSaveBtn(readOnly) {
    var saveBtn = dialog && dialog.querySelector("[data-course-quiz-save]");
    if (!saveBtn) return null;
    saveBtn.hidden = !!readOnly;
    if (!readOnly) {
      var saveLabel = t("travelCourses.quiz.save", "내 기기에 저장");
      saveBtn.setAttribute("aria-label", saveLabel);
      saveBtn.setAttribute("title", saveLabel);
      saveBtn.disabled = false;
      saveBtn.classList.remove("is-saved");
    }
    return saveBtn;
  }

  function markToolbarSaved(saveBtn) {
    if (!saveBtn) return;
    var done = t("travelCourses.quiz.saveDone", "내 기기에 저장됨");
    saveBtn.classList.add("is-saved");
    saveBtn.setAttribute("aria-label", done);
    saveBtn.setAttribute("title", done);
    saveBtn.disabled = true;
  }
  function bindResultActions(panel, course, opts) {
    opts = opts || {};
    var restart = panel.querySelector("[data-course-quiz-restart]");
    if (restart) {
      restart.addEventListener("click", function () {
        startQuiz();
      });
    }
    var saveBtn = showToolbarSaveBtn(opts.readOnly);
    if (saveBtn && !opts.readOnly) {
      saveBtn.onclick = function () {
        var ok = saveCourse(course);
        if (ok) {
          markToolbarSaved(saveBtn);
        } else {
          var fail = t(
            "travelCourses.quiz.saveFail",
            "저장할 수 없어요. 브라우저 저장 공간을 확인해 주세요."
          );
          saveBtn.setAttribute("aria-label", fail);
          saveBtn.setAttribute("title", fail);
        }
        renderSavedList();
      };
    }
  }

  function renderCourseView(course, opts) {
    opts = opts || {};
    course = localizeCourse(course);
    if (!opts.readOnly) lastCourse = course;
    var panel = dialog.querySelector("[data-course-quiz-panel]");
    if (!panel || !course) return;

    var backBtn = dialog.querySelector("[data-course-quiz-back]");
    if (backBtn) backBtn.hidden = true;

    showToolbarSaveBtn(opts.readOnly);

    var bar = dialog.querySelector("[data-course-quiz-bar]");
    if (bar) bar.style.width = "100%";
    var prog = dialog.querySelector("[data-course-quiz-progress]");
    if (prog) prog.textContent = t("travelCourses.quiz.resultLabel", "결과");

    var title = dialog.querySelector("[data-course-quiz-heading]");
    if (title) {
      title.textContent = opts.readOnly
        ? t("travelCourses.quiz.savedViewTitle", "내 기기에 저장된 코스")
        : t("travelCourses.quiz.title", "여행 코스 추천");
    }

    var eyebrow = opts.readOnly
      ? t("travelCourses.quiz.savedViewTitle", "내 기기에 저장된 코스")
      : t("travelCourses.quiz.resultEyebrow", "맞춤 코스");
    var localNote = t(
      "travelCourses.quiz.savedLocalNote",
      "계정 없이 이 휴대폰·PC의 브라우저에만 저장됩니다. 서버로 전송되지 않으며, 다른 기기나 브라우저에서는 보이지 않아요."
    );
    var again = t("travelCourses.quiz.restart", "코스 다시찾기");
    var timelineTitle = t(
      "travelCourses.quiz.timelineTitle",
      "시간대별 이동 경로"
    );

    var actions =
      '<div class="course-quiz-result__actions">' +
      '<button type="button" class="course-quiz-restart" data-course-quiz-restart>' +
      escapeHtml(again) +
      "</button></div>";

    panel.innerHTML =
      '<div class="course-quiz-result course-quiz-result--timeline"' +
      (reduceMotion ? "" : ' data-anim="in"') +
      ">" +
      '<p class="course-quiz-result__eyebrow">' +
      escapeHtml(eyebrow) +
      "</p>" +
      '<h3 class="course-quiz-result__title">' +
      escapeHtml(courseTitle(course)) +
      "</h3>" +
      '<div class="course-quiz-chips">' +
      summaryChipsHtml(course.answers) +
      "</div>" +
      '<p class="course-quiz-result__reason">' +
      escapeHtml(course.reason || "") +
      "</p>" +
      (opts.readOnly
        ? ""
        : '<p class="course-quiz-result__local-note">' +
          escapeHtml(localNote) +
          "</p>") +
      '<p class="course-quiz-timeline-label">' +
      escapeHtml(timelineTitle) +
      "</p>" +
      '<div class="course-quiz-days">' +
      daysTimelineHtml(course) +
      "</div>" +
      actions +
      "</div>";

    bindResultActions(panel, course, opts);
  }

  function renderResult() {
    lastCourse = buildCourse();
    viewingSavedId = null;
    renderCourseView(lastCourse, { readOnly: false });
  }

  function openSavedCourse(id) {
    var list = loadSaved();
    var found = null;
    for (var i = 0; i < list.length; i++) {
      if (list[i] && list[i].id === id) {
        found = list[i];
        break;
      }
    }
    if (!found) return;
    viewingSavedId = id;
    lastCourse = found;
    answers = Object.assign({}, found.answers || {});
    setOpen(true);
    renderCourseView(found, { readOnly: true });
  }

  function renderSavedList() {
    var host = document.querySelector("[data-course-saved]");
    if (!host) return;
    var list = loadSaved();
    var title = t("travelCourses.quiz.savedTitle", "내 기기에 저장된 코스");
    var note = t(
      "travelCourses.quiz.savedLocalNote",
      "계정 없이 이 휴대폰·PC의 브라우저에만 저장됩니다. 서버로 전송되지 않으며, 다른 기기나 브라우저에서는 보이지 않아요."
    );
    var empty = t(
      "travelCourses.quiz.savedEmpty",
      "아직 저장된 코스가 없어요. 추천 후 북마크 아이콘으로 이 기기에 저장해 보세요."
    );
    var openLbl = t("travelCourses.quiz.openSaved", "보기");
    var delLbl = t("travelCourses.quiz.deleteSaved", "삭제");

    if (!list.length) {
      host.innerHTML =
        '<h2 class="course-saved__title">' +
        escapeHtml(title) +
        "</h2>" +
        '<p class="course-saved__note">' +
        escapeHtml(note) +
        "</p>" +
        '<p class="course-saved__empty">' +
        escapeHtml(empty) +
        "</p>";
      return;
    }

    var items = list
      .map(function (item) {
        var when = formatSavedAt(item.createdAt);
        var whenHtml = when
          ? '<span class="course-saved-card__when">' +
            escapeHtml(
              t("travelCourses.quiz.savedAt", "저장").replace("{when}", when)
            ) +
            "</span>"
          : "";
        return (
          '<article class="course-saved-card" data-saved-id="' +
          escapeAttr(item.id) +
          '">' +
          '<div class="course-saved-card__copy">' +
          '<h3 class="course-saved-card__name">' +
          escapeHtml(courseTitle(item)) +
          "</h3>" +
          whenHtml +
          '<div class="course-quiz-chips course-quiz-chips--compact">' +
          summaryChipsHtml(item.answers) +
          "</div></div>" +
          '<div class="course-saved-card__actions">' +
          '<button type="button" class="course-saved-open" data-saved-open="' +
          escapeAttr(item.id) +
          '">' +
          escapeHtml(openLbl) +
          "</button>" +
          '<button type="button" class="course-saved-delete" data-saved-delete="' +
          escapeAttr(item.id) +
          '">' +
          escapeHtml(delLbl) +
          "</button></div></article>"
        );
      })
      .join("");

    host.innerHTML =
      '<h2 class="course-saved__title">' +
      escapeHtml(title) +
      "</h2>" +
      '<p class="course-saved__note">' +
      escapeHtml(note) +
      "</p>" +
      '<div class="course-saved__list">' +
      items +
      "</div>";

    host.querySelectorAll("[data-saved-open]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        openSavedCourse(btn.getAttribute("data-saved-open"));
      });
    });
    host.querySelectorAll("[data-saved-delete]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        deleteSaved(btn.getAttribute("data-saved-delete"));
        renderSavedList();
        if (viewingSavedId === btn.getAttribute("data-saved-delete")) {
          setOpen(false);
        }
      });
    });
  }

  function rebuildActiveFromAnswers() {
    activeQuestionIds = visibleQuestions().map(function (q) {
      return q.id;
    });
  }

  function chooseOption(optionId) {
    var qid = activeQuestionIds[stepIndex];
    var q = questionById(qid);
    if (!q) return;
    var opt = null;
    for (var i = 0; i < q.options.length; i++) {
      if (q.options[i].id === optionId) {
        opt = q.options[i];
        break;
      }
    }
    if (!opt) return;

    historyStack.push({
      answers: Object.assign({}, answers),
      activeQuestionIds: activeQuestionIds.slice(),
      stepIndex: stepIndex,
    });

    answers[qid] = optionId;
    rebuildActiveFromAnswers();

    var nextIdx = activeQuestionIds.indexOf(qid) + 1;
    if (nextIdx >= activeQuestionIds.length) {
      stepIndex = activeQuestionIds.length;
      renderResult();
      return;
    }
    stepIndex = nextIdx;
    renderQuestion();
  }

  function goBack() {
    var prev = historyStack.pop();
    if (!prev) return;
    answers = prev.answers;
    activeQuestionIds = prev.activeQuestionIds;
    stepIndex = prev.stepIndex;
    renderQuestion();
  }

  function startQuiz() {
    answers = { duration: "day" };
    historyStack = [];
    lastCourse = null;
    viewingSavedId = null;
    pendingChoice = null;
    resetToolbarSaveBtn();
    rebuildActiveFromAnswers();
    stepIndex = 0;
    setOpen(true);
    renderQuestion();
  }

  function refreshBannerCopy() {
    if (!root) return;
    var title = root.querySelector("[data-course-quiz-banner-title]");
    var cta = root.querySelector("[data-course-quiz-banner-cta]");
    if (title) {
      title.textContent = t(
        "travelCourses.quiz.bannerTitle",
        "실시간으로 여행 코스를 추천받으세요."
      );
    }
    if (cta) {
      cta.textContent = t("travelCourses.quiz.bannerCta", "추천받기");
    }
    var closeBtn = dialog && dialog.querySelector("[data-course-quiz-close]");
    if (closeBtn) {
      closeBtn.setAttribute("aria-label", t("travelCourses.quiz.close", "닫기"));
    }
    var backBtn = dialog && dialog.querySelector("[data-course-quiz-back]");
    if (backBtn) {
      backBtn.textContent = t("travelCourses.quiz.back", "이전");
    }
    renderSavedList();
    if (dialog && !dialog.hidden) {
      if (viewingSavedId && lastCourse) {
        renderCourseView(lastCourse, { readOnly: true });
      } else if (
        stepIndex >= activeQuestionIds.length &&
        Object.keys(answers).length
      ) {
        if (lastCourse) renderCourseView(lastCourse, { readOnly: false });
        else renderResult();
      } else if (activeQuestionIds.length) {
        renderQuestion();
      }
    }
  }

  function onKeydown(e) {
    if (!dialog || dialog.hidden) return;
    if (e.key === "Escape") {
      e.preventDefault();
      setOpen(false);
    }
  }

  function init() {
    root = document.querySelector(ROOT_SEL);
    if (!root) return;
    dialog = root.querySelector("[data-course-quiz-dialog]");
    if (!dialog) return;
    mountDialogOnBody();

    root.querySelectorAll("[data-course-quiz-open]").forEach(function (el) {
      el.addEventListener("click", function () {
        startQuiz();
      });
    });

    var closeBtn = dialog.querySelector("[data-course-quiz-close]");
    if (closeBtn) {
      closeBtn.addEventListener("click", function () {
        setOpen(false);
      });
    }

    var backdrop = dialog.querySelector("[data-course-quiz-backdrop]");
    if (backdrop) {
      backdrop.addEventListener("click", function () {
        setOpen(false);
      });
    }

    var backBtn = dialog.querySelector("[data-course-quiz-back]");
    if (backBtn) backBtn.addEventListener("click", goBack);

    document.addEventListener("keydown", onKeydown);
    document.addEventListener("guide:langchange", refreshBannerCopy);
    refreshBannerCopy();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
