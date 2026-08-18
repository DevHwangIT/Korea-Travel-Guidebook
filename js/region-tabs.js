/* Generic tab / select switcher for guidebook sections.
 * Optional deep links: root with data-hash-tabs syncs #category[/sub] to nested tabs.
 */
(function () {
  function activate(root, name, kind) {
    var buttons = root.querySelectorAll("[data-" + kind + "-tab]");
    var panels = root.querySelectorAll("[data-" + kind + "-panel]");
    var select = root.querySelector("[data-" + kind + "-select]");
    buttons.forEach(function (btn) {
      var on = btn.getAttribute("data-" + kind + "-tab") === name;
      btn.classList.toggle("is-active", on);
      btn.setAttribute("aria-selected", on ? "true" : "false");
    });
    panels.forEach(function (panel) {
      var on = panel.getAttribute("data-" + kind + "-panel") === name;
      panel.classList.toggle("is-active", on);
      panel.hidden = !on;
    });
    if (select && select.value !== name) {
      select.value = name;
    }
    if (kind === "courseRegion") {
      var regionPanel = root.querySelector(
        '[data-courseRegion-panel="' + name + '"]'
      );
      if (regionPanel) {
        var nestedRoot = regionPanel.querySelector("[data-tabs]");
        if (nestedRoot) {
          var nestedKind = (nestedRoot.getAttribute("data-tabs") || "")
            .split(",")[0]
            .trim();
          if (nestedKind) {
            var nestedVisible = nestedRoot.querySelector(
              "[data-" + nestedKind + "-panel]:not([hidden])"
            );
            if (!nestedVisible) {
              var nestedSelect = nestedRoot.querySelector(
                "[data-" + nestedKind + "-select]"
              );
              var nestedFirst = nestedSelect
                ? nestedSelect.value ||
                  (nestedSelect.options[0] && nestedSelect.options[0].value)
                : nestedRoot.querySelector("[data-" + nestedKind + "-tab]") &&
                  nestedRoot
                    .querySelector("[data-" + nestedKind + "-tab]")
                    .getAttribute("data-" + nestedKind + "-tab");
              if (nestedFirst) activate(nestedRoot, nestedFirst, nestedKind);
            }
          }
        }
      }
    }
  }

  function bind(root, kind, onChange) {
    var buttons = root.querySelectorAll("[data-" + kind + "-tab]");
    var select = root.querySelector("[data-" + kind + "-select]");
    if (!buttons.length && !select) return;

    function pick(name) {
      if (!name) return;
      activate(root, name, kind);
      if (onChange) onChange(name, kind);
    }

    buttons.forEach(function (btn) {
      btn.addEventListener("click", function () {
        pick(btn.getAttribute("data-" + kind + "-tab"));
      });
    });
    if (select) {
      select.addEventListener("change", function () {
        if (select.value) pick(select.value);
      });
    }

    var first = select
      ? select.value || (select.options[0] && select.options[0].value)
      : buttons[0] && buttons[0].getAttribute("data-" + kind + "-tab");
    if (first) activate(root, first, kind);
  }

  function nestedRoots(root) {
    return Array.prototype.slice.call(root.querySelectorAll("[data-tabs]")).filter(
      function (nested) {
        return nested !== root;
      }
    );
  }

  function activeName(el, kind) {
    var active = el.querySelector("[data-" + kind + "-tab].is-active");
    if (active) return active.getAttribute("data-" + kind + "-tab");
    var select = el.querySelector("[data-" + kind + "-select]");
    if (select && select.value) return select.value;
    var first = el.querySelector("[data-" + kind + "-tab]");
    return first ? first.getAttribute("data-" + kind + "-tab") : "";
  }

  function parseHash() {
    var raw = (window.location.hash || "").replace(/^#/, "").trim();
    if (!raw) return null;
    var parts = raw.split("/").filter(Boolean);
    if (!parts.length) return null;
    return {
      cat: decodeURIComponent(parts[0]).toLowerCase(),
      sub: parts[1] ? decodeURIComponent(parts[1]).toLowerCase() : "",
    };
  }

  function writeHash(cat, sub) {
    if (!cat) return;
    var next = "#" + encodeURIComponent(cat);
    if (sub) next += "/" + encodeURIComponent(sub);
    if (window.location.hash === next) return;
    if (history.replaceState) {
      var url = new URL(window.location.href);
      url.hash = next.slice(1);
      history.replaceState(null, "", url.pathname + url.search + url.hash);
    } else {
      window.location.hash = next;
    }
  }

  function bindHashRoot(root, kinds) {
    var catKind = kinds[0];
    if (!catKind) return;

    function syncFromUi() {
      var cat = activeName(root, catKind);
      var panel = root.querySelector(
        "[data-" + catKind + '-panel="' + cat + '"]'
      );
      var sub = "";
      if (panel) {
        var nested = panel.querySelector("[data-tabs]");
        if (nested) {
          var nestedKinds = (nested.getAttribute("data-tabs") || "")
            .split(",")
            .map(function (k) {
              return k.trim();
            })
            .filter(Boolean);
          var subKind = nestedKinds[0];
          if (subKind) sub = activeName(nested, subKind) || "";
        }
      }
      writeHash(cat, sub);
    }

    function applyHash(state) {
      if (!state || !state.cat) return false;
      var catBtn = root.querySelector(
        "[data-" + catKind + '-tab="' + state.cat + '"]'
      );
      if (!catBtn) return false;
      activate(root, state.cat, catKind);
      var panel = root.querySelector(
        "[data-" + catKind + '-panel="' + state.cat + '"]'
      );
      if (!panel || !state.sub) {
        syncFromUi();
        return true;
      }
      var nested = panel.querySelector("[data-tabs]");
      if (!nested) return true;
      var nestedKinds = (nested.getAttribute("data-tabs") || "")
        .split(",")
        .map(function (k) {
          return k.trim();
        })
        .filter(Boolean);
      var subKind = nestedKinds[0];
      if (!subKind) return true;
      var subBtn = nested.querySelector(
        "[data-" + subKind + '-tab="' + state.sub + '"]'
      );
      if (subBtn) activate(nested, state.sub, subKind);
      return true;
    }

    kinds.forEach(function (kind) {
      bind(root, kind, function () {
        syncFromUi();
      });
    });

    nestedRoots(root).forEach(function (nested) {
      var nestedKinds = (nested.getAttribute("data-tabs") || "")
        .split(",")
        .map(function (k) {
          return k.trim();
        })
        .filter(Boolean);
      nestedKinds.forEach(function (k) {
        bind(nested, k, function () {
          syncFromUi();
        });
      });
    });

    var fromHash = parseHash();
    if (!applyHash(fromHash)) {
      syncFromUi();
    }

    window.addEventListener("hashchange", function () {
      applyHash(parseHash());
    });
  }

  function bindRoot(root, kinds) {
    if (root.hasAttribute("data-hash-tabs")) {
      bindHashRoot(root, kinds);
      return;
    }
    kinds.forEach(function (kind) {
      bind(root, kind);
    });
    nestedRoots(root).forEach(function (nested) {
      var nestedKinds = (nested.getAttribute("data-tabs") || "")
        .split(",")
        .map(function (k) {
          return k.trim();
        })
        .filter(Boolean);
      nestedKinds.forEach(function (k) {
        bind(nested, k);
      });
    });
  }

  document.querySelectorAll("[data-tabs]").forEach(function (root) {
    if (root.parentElement && root.parentElement.closest("[data-tabs]")) return;
    var kinds = (root.getAttribute("data-tabs") || "")
      .split(",")
      .map(function (k) {
        return k.trim();
      })
      .filter(Boolean);
    if (!kinds.length) return;
    bindRoot(root, kinds);
  });

  // Food pages (legacy attributes)
  document.querySelectorAll("[data-city-tabs]").forEach(function (root) {
    bind(root, "city");
    root.querySelectorAll("[data-area-tabs]").forEach(function (areaRoot) {
      bind(areaRoot, "area");
    });
  });
})();
