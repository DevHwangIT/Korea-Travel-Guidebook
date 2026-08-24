/**
 * Region id → curated course arrays for the travel-courses hub.
 * Seoul data: data/courses/seoul-curated.js (window.SEOUL_CURATED_COURSES).
 * Add another region the same way, then assign the array here.
 */
(function () {
  var byRegion = window.CURATED_COURSES_BY_REGION || {};
  if (!Array.isArray(byRegion.seoul)) {
    byRegion.seoul = window.SEOUL_CURATED_COURSES || [];
  }
  ["gyeonggi", "incheon", "gyeongju", "busan", "jeju"].forEach(function (id) {
    if (!Array.isArray(byRegion[id])) byRegion[id] = [];
  });
  window.CURATED_COURSES_BY_REGION = byRegion;
})();
