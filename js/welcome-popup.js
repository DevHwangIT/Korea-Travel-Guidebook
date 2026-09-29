/**
 * Sitewide welcome notice (환영 안내 팝업) — once per calendar day (local TZ).
 * Hide key: korea-guide-welcome-hide-date (YYYY-MM-DD) — distinct from korea-guide-lang.
 * Loaded dynamically from i18n.js so every page gets it without editing all HTML.
 * Soft traveler greeting + tip contribution ask; does not touch partner-strip / partner-panel.
 */
(function () {
  var STORAGE_KEY = "korea-guide-welcome-hide-date";
  var DIALOG_ID = "guide-welcome-dialog";
  var UPDATED_ISO = "2026-09-29";
  var DATE_LOCALES = {
    ko: "ko-KR",
    en: "en-US",
    ja: "ja-JP",
    zh: "zh-CN",
    "zh-Hant": "zh-TW",
    vi: "vi-VN",
    th: "th-TH",
    ru: "ru-RU",
  };

  function todayLocal() {
    var d = new Date();
    var y = d.getFullYear();
    var m = String(d.getMonth() + 1).padStart
      ? String(d.getMonth() + 1).padStart(2, "0")
      : ("0" + (d.getMonth() + 1)).slice(-2);
    var day = String(d.getDate()).padStart
      ? String(d.getDate()).padStart(2, "0")
      : ("0" + d.getDate()).slice(-2);
    return y + "-" + m + "-" + day;
  }

  function isHiddenToday() {
    try {
      return localStorage.getItem(STORAGE_KEY) === todayLocal();
    } catch (e) {
      return false;
    }
  }

  function markHiddenToday() {
    try {
      localStorage.setItem(STORAGE_KEY, todayLocal());
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
      if (!cur || !Object.prototype.hasOwnProperty.call(cur, parts[i])) return fallback;
      cur = cur[parts[i]];
    }
    return cur == null || cur === "" ? fallback : String(cur);
  }

  function currentLang() {
    try {
      if (window.GuideI18n && typeof window.GuideI18n.getLang === "function") {
        return window.GuideI18n.getLang() || "en";
      }
    } catch (e) {}
    return document.documentElement.lang || "en";
  }

  function formatUpdatedDate() {
    try {
      var locale = DATE_LOCALES[currentLang()] || "en-US";
      return new Date(UPDATED_ISO + "T00:00:00").toLocaleDateString(locale, {
        year: "numeric",
        month: "short",
        day: "numeric",
      });
    } catch (e) {
      return UPDATED_ISO;
    }
  }

  function fillUpdated(root) {
    if (!root || !root.querySelectorAll) return;
    var stamp = formatUpdatedDate();
    root.querySelectorAll("[data-welcome-updated]").forEach(function (el) {
      el.setAttribute("datetime", UPDATED_ISO);
      el.textContent = stamp;
    });
  }

  function applyI18n(root) {
    root.querySelectorAll("[data-i18n]").forEach(function (el) {
      var key = el.getAttribute("data-i18n");
      var fallback = el.textContent;
      el.textContent = t(key, fallback);
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
    fillUpdated(root);
  }

  function closeDialog(dialog, hideToday) {
    if (hideToday) {
      var box = dialog.querySelector("[data-welcome-hide-today]");
      if (box && box.checked) markHiddenToday();
    }
    dialog.hidden = true;
    dialog.setAttribute("aria-hidden", "true");
    document.body.classList.remove("welcome-popup-lock");
    var previouslyFocused = dialog._guidePrevFocus;
    if (previouslyFocused && typeof previouslyFocused.focus === "function") {
      try {
        previouslyFocused.focus();
      } catch (e) {
        /* ignore */
      }
    }
  }

  function openDialog(dialog) {
    dialog._guidePrevFocus = document.activeElement;
    dialog.hidden = false;
    dialog.setAttribute("aria-hidden", "false");
    document.body.classList.add("welcome-popup-lock");
    var closeBtn = dialog.querySelector("[data-welcome-close]");
    if (closeBtn) closeBtn.focus();
  }

  function buildDialog() {
    if (document.getElementById(DIALOG_ID)) return document.getElementById(DIALOG_ID);

    var dialog = document.createElement("div");
    dialog.id = DIALOG_ID;
    dialog.className = "welcome-popup";
    dialog.setAttribute("role", "dialog");
    dialog.setAttribute("aria-modal", "true");
    dialog.setAttribute("aria-labelledby", "guide-welcome-title");
    dialog.setAttribute("aria-hidden", "true");
    dialog.hidden = true;
    dialog.innerHTML =
      '<div class="welcome-popup__backdrop" data-welcome-dismiss tabindex="-1"></div>' +
      '<div class="welcome-popup__sheet" role="document">' +
      '  <div class="welcome-popup__accent" aria-hidden="true"></div>' +
      '  <button type="button" class="welcome-popup__x" data-welcome-close data-i18n-attr="aria-label:welcome.close" aria-label="Close">×</button>' +
      '  <div class="welcome-popup__header">' +
      '    <span class="welcome-popup__icon" aria-hidden="true">' +
      '      <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' +
      '        <circle cx="12" cy="12" r="9"></circle>' +
      '        <path d="M12 8v5"></path>' +
      '        <circle cx="12" cy="16.5" r="0.75" fill="currentColor" stroke="none"></circle>' +
      "      </svg>" +
      "    </span>" +
      '    <h2 id="guide-welcome-title" class="welcome-popup__title" data-i18n="welcome.title">환영합니다</h2>' +
      "  </div>" +
      '  <div class="welcome-popup__body">' +
      '    <p data-i18n="welcome.body">한국을 방문하시는 분들이 조금 더 편리하고 유익하게 여행하시길 바라며 만들었습니다. 이용은 무료이며, 개선이 필요하시면 언제든 의견을 남겨 주세요. 여행을 준비 중이시거나 여행 중이신 모든 분들께 행복한 시간이 되기를 바랍니다.</p>' +
      '    <p data-i18n="welcome.bodyShare">사이트에 소개되는 맛집·정보는 웹에서 무작위로 모은 내용만이 아니라, 실제로 다녀오신 분들이 좋다고 하신 곳을 바탕으로 담아 가려 합니다. 한국 여행에서 좋았던 경험이나 추천 식당이 있으시면 메인 페이지 하단의 문의·피드백 영역을 확인해 주세요. 팁을 공유하시거나 연락처를 찾으실 수 있으며, 검토 후 가이드에 반영하겠습니다.</p>' +
      '    <section class="welcome-popup__news" aria-labelledby="guide-welcome-updates">' +
      '      <div class="welcome-popup__news-head">' +
      '        <h3 id="guide-welcome-updates" class="welcome-popup__h" data-i18n="welcome.updatesTitle">최근 수정</h3>' +
      '        <p class="welcome-popup__updated"><span data-i18n="welcome.updatedLabel">마지막 수정일</span> <time datetime="2026-09-29" data-welcome-updated>2026. 9. 29.</time></p>' +
      "      </div>" +
      '      <ul class="welcome-popup__list">' +
      '        <li data-i18n="welcome.updatePartner">제휴 가게를 추가했습니다.</li>' +
      '        <li data-i18n="welcome.updatePrep">여행 준비 팁을 보강하고, 기존 내용도 고쳤습니다.</li>' +
      "      </ul>" +
      '      <h3 class="welcome-popup__h" data-i18n="welcome.notesTitle">안내</h3>' +
      '      <ul class="welcome-popup__notes">' +
      '        <li data-i18n="welcome.notePhotos">식당 사진은 저작권 때문에, 직접 공유받은 경우에만 올립니다.</li>' +
      '        <li data-i18n="welcome.noteHotels">추천 호텔은 아직 계획이 없습니다. 필요하면 그때 추가하겠습니다.</li>' +
      '        <li data-i18n="welcome.noteTips">가볼 만한 식당은 하단 이메일이나 LINE으로 알려 주세요.</li>' +
      "        <li>" +
      '          <span data-i18n="welcome.noteGuide">사이트 운영자는 전문 가이드가 아니라, 전문적인 안내는 받지않고 있습니다.</span>' +
      '          <span class="welcome-popup__paren" data-i18n="welcome.noteHelp">( 다만, 한국을 처음 방문하셔서 도움이 필요한 분에 한해 요청하실 경우 간단한 안내와 도움을 드릴 수 있습니다. )</span>' +
      '          <span class="welcome-popup__bracket" data-i18n="welcome.noteCost">[ ※ 관광 중 발생하는 식사, 교통, 입장료 등의 개인적인 경비는 안내자가 부담하지 않습니다. ]</span>' +
      "        </li>" +
      "      </ul>" +
      "    </section>" +
      "  </div>" +
      '  <label class="welcome-popup__check">' +
      '    <input type="checkbox" data-welcome-hide-today>' +
      '    <span data-i18n="welcome.hideToday">오늘 하루 동안 이 창을 열지 않음</span>' +
      "  </label>" +
      '  <div class="welcome-popup__actions">' +
      '    <button type="button" class="welcome-popup__confirm" data-welcome-confirm data-i18n="welcome.confirm">확인</button>' +
      "  </div>" +
      "</div>";

    document.body.appendChild(dialog);

    dialog.addEventListener("click", function (e) {
      if (e.target.closest("[data-welcome-dismiss]")) {
        closeDialog(dialog, true);
        return;
      }
      if (e.target.closest("[data-welcome-close]") || e.target.closest("[data-welcome-confirm]")) {
        closeDialog(dialog, true);
      }
    });

    document.addEventListener("keydown", function (e) {
      if (dialog.hidden) return;
      if (e.key === "Escape") {
        e.preventDefault();
        closeDialog(dialog, true);
      }
    });

    return dialog;
  }

  function showIfNeeded() {
    if (isHiddenToday()) return;
    var dialog = buildDialog();
    applyI18n(dialog);
    openDialog(dialog);
  }

  function isCrawler() {
    var ua = String(navigator.userAgent || "").toLowerCase();
    return /mediapartners-google|googlebot|adsbot-google|bingbot|slurp|duckduckbot|baiduspider|yandexbot|facebookexternalhit|twitterbot/.test(
      ua
    );
  }

  function boot() {
    if (isCrawler()) return;
    window.setTimeout(showIfNeeded, 280);
  }

  document.addEventListener("guide:langchange", function () {
    var dialog = document.getElementById(DIALOG_ID);
    if (!dialog) return;
    if (window.GuideI18n && typeof window.GuideI18n.apply === "function") {
      window.GuideI18n.apply(dialog);
    } else {
      applyI18n(dialog);
    }
    fillUpdated(dialog);
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
