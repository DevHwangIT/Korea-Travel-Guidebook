/**
 * Region id → curated course arrays for the travel-courses hub.
 * Seoul: data/courses/seoul-curated.js
 * Gyeonggi: data/courses/gyeonggi-curated.js
 * Incheon: data/courses/incheon-curated.js
 * Gangwon / Chungcheong / Jeolla / Gyeongsang / Busan / Jeju: matching *-curated.js
 */
(function () {
  var byRegion = window.CURATED_COURSES_BY_REGION || {};
  var sources = {
    seoul: window.SEOUL_CURATED_COURSES,
    gyeonggi: window.GYEONGGI_CURATED_COURSES,
    incheon: window.INCHEON_CURATED_COURSES,
    gangwon: window.GANGWON_CURATED_COURSES,
    chungcheong: window.CHUNGCHEONG_CURATED_COURSES,
    jeolla: window.JEOLLA_CURATED_COURSES,
    gyeongsang: window.GYEONGSANG_CURATED_COURSES,
    busan: window.BUSAN_CURATED_COURSES,
    jeju: window.JEJU_CURATED_COURSES,
  };
  Object.keys(sources).forEach(function (id) {
    if (!Array.isArray(byRegion[id]) || !byRegion[id].length) {
      byRegion[id] = sources[id] || [];
    }
  });
  window.CURATED_COURSES_BY_REGION = byRegion;
})();
