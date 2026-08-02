/**
 * Render useful-Korean phrase lists; show EN/JA/all by active language.
 */
(function () {
  var CAT_ORDER = ["daily", "restaurant", "shopping", "transport", "emergency", "swear"];
  var BADGE = { ko: "금지", en: "Do not say", ja: "使用禁止" };

  function lang() {
    return (window.GuideI18n && GuideI18n.getLang && GuideI18n.getLang()) || "ko";
  }

  function esc(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function itemHtml(p, isSwear, l) {
    return (
      '<li class="phrase-item' +
      (isSwear ? " phrase-item-swear" : "") +
      '">' +
      '<div class="phrase-main">' +
      (isSwear ? '<p class="phrase-ban">' + esc(BADGE[l] || BADGE.ko) + "</p>" : "") +
      '<p class="phrase-ko">' +
      esc(p.ko) +
      "</p>" +
      '<p class="phrase-rom">' +
      esc(p.rom) +
      "</p>" +
      '<p class="phrase-tr">' +
      '<span class="phrase-tr-en">' +
      esc(p.en) +
      "</span>" +
      '<span class="phrase-tr-sep"> · </span>' +
      '<span class="phrase-tr-ja">' +
      esc(p.ja) +
      "</span>" +
      "</p>" +
      "</div>" +
      '<button type="button" class="phrase-audio-btn" data-phrase-audio="' +
      esc(p.id) +
      '" aria-label="Play audio">▶</button>' +
      "</li>"
    );
  }

  function render() {
    var data = window.KOREAN_PHRASES;
    if (!data) return;
    var l = lang();
    CAT_ORDER.forEach(function (cat) {
      var panel = document.querySelector('[data-phrasecat-panel="' + cat + '"]');
      if (!panel) return;
      var list = panel.querySelector(".phrase-list");
      if (!list) return;
      var rows = data[cat] || [];
      list.innerHTML = rows
        .map(function (p) {
          return itemHtml(p, cat === "swear", l);
        })
        .join("");
    });
    document.documentElement.setAttribute("data-phrase-lang", l);
  }

  document.addEventListener("guide:langchange", function () {
    render();
  });

  function init() {
    render();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
