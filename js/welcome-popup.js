/**
 * Sitewide welcome modal — once per calendar day (local TZ).
 * Hide key: korea-guide-welcome-hide-date (YYYY-MM-DD) — distinct from korea-guide-lang.
 * Loaded dynamically from i18n.js so every page gets it without editing all HTML.
 * Soft traveler greeting only; does not touch partner-strip / partner-panel.
 */
(function () {
  var STORAGE_KEY = "korea-guide-welcome-hide-date";
  var DIALOG_ID = "guide-welcome-dialog";

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
      '  <button type="button" class="welcome-popup__x" data-welcome-close data-i18n-attr="aria-label:welcome.close" aria-label="Close">×</button>' +
      '  <h2 id="guide-welcome-title" class="welcome-popup__title" data-i18n="welcome.title">환영합니다</h2>' +
      '  <p class="welcome-popup__body" data-i18n="welcome.body">한국을 방문하시는 분들이 조금 더 편리하고 유익하게 여행하시길 바라며 만들었습니다. 이용은 무료이며, 개선이 필요하시면 언제든 의견을 남겨 주세요. 여행을 준비 중이시거나 여행 중이신 모든 분들께 행복한 시간이 되기를 바랍니다.</p>' +
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

  function boot() {
    // Slight delay so first paint / partner strip settle; modal stacks above (z-index 90).
    window.setTimeout(showIfNeeded, 280);
  }

  document.addEventListener("guide:langchange", function () {
    var dialog = document.getElementById(DIALOG_ID);
    if (dialog && !dialog.hidden) applyI18n(dialog);
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
