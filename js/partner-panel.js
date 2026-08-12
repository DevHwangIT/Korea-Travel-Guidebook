/**
 * Home partner / affiliate panel — fixed right rail (desktop), FAB + sheet (mobile).
 */
(function () {
  function qs(sel, root) {
    return (root || document).querySelector(sel);
  }

  function init() {
    var panel = qs("[data-partner-panel]");
    if (!panel) return;
    var fab = qs("[data-partner-fab]");
    var backdrop = qs("[data-partner-backdrop]");
    var closeBtn = qs("[data-partner-close]");

    function setOpen(open) {
      document.documentElement.classList.toggle("partner-panel-open", open);
      if (fab) fab.setAttribute("aria-expanded", open ? "true" : "false");
      if (panel) panel.setAttribute("aria-hidden", open ? "false" : "true");
      if (backdrop) {
        if (open) backdrop.removeAttribute("hidden");
        else backdrop.setAttribute("hidden", "");
      }
    }

    function isMobile() {
      return window.matchMedia("(max-width: 960px)").matches;
    }

    if (fab) {
      fab.addEventListener("click", function () {
        setOpen(!document.documentElement.classList.contains("partner-panel-open"));
      });
    }
    if (closeBtn) {
      closeBtn.addEventListener("click", function () {
        setOpen(false);
      });
    }
    if (backdrop) {
      backdrop.addEventListener("click", function () {
        setOpen(false);
      });
    }
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") setOpen(false);
    });
    window.addEventListener("resize", function () {
      if (!isMobile()) setOpen(false);
    });

    // Desktop: panel always visible (aria-hidden false). Mobile: start closed.
    if (!isMobile()) {
      panel.setAttribute("aria-hidden", "false");
    } else {
      setOpen(false);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
