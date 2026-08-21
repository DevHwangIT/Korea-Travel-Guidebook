/**
 * Festivals stacked deck — overlapping cards that zoom toward center (no tilt).
 * JS-driven horizontal drag + soft settle + seamless infinite loop (cloned deck).
 */
(function () {
  var DRAG_THRESHOLD = 8;
  /** Cards farther than this use a static far pose (skip per-frame style work). */
  var FAR_ABS = 2.35;
  /** Hydrate clone/deferred images within this distance of center. */
  var HYDRATE_ABS = 1.65;

  function clamp(n, min, max) {
    return Math.max(min, Math.min(max, n));
  }

  function easeOutCubic(t) {
    return 1 - Math.pow(1 - t, 3);
  }

  function demoteCloneMedia(card) {
    var imgs = card.querySelectorAll("img");
    for (var i = 0; i < imgs.length; i++) {
      var img = imgs[i];
      var src = img.getAttribute("src");
      if (!src) continue;
      img.setAttribute("data-src", src);
      img.removeAttribute("src");
      img.setAttribute("loading", "lazy");
      img.setAttribute("decoding", "async");
      img.setAttribute("fetchpriority", "low");
    }
  }

  function hydrateCardMedia(card) {
    if (card.getAttribute("data-fest-hydrated") === "1") return;
    var imgs = card.querySelectorAll("img[data-src]");
    if (!imgs.length) {
      card.setAttribute("data-fest-hydrated", "1");
      return;
    }
    for (var i = 0; i < imgs.length; i++) {
      var img = imgs[i];
      var src = img.getAttribute("data-src");
      if (!src) continue;
      img.setAttribute("src", src);
      img.removeAttribute("data-src");
      img.setAttribute("decoding", "async");
      if (img.decode) {
        try {
          img.decode().catch(function () {});
        } catch (_) {}
      }
    }
    card.setAttribute("data-fest-hydrated", "1");
  }

  function bind(root) {
    if (root.getAttribute("data-festivals-bound") === "1") return;
    root.setAttribute("data-festivals-bound", "1");

    var track = root.querySelector("[data-festivals-track]");
    var dotsWrap = root.querySelector("[data-festivals-dots]");
    if (!track) return;

    var realCards = Array.prototype.slice.call(track.querySelectorAll(".festivals-poster"));
    var realCount = realCards.length;
    if (!realCount) return;

    var loop = realCount >= 2;

    if (loop) {
      var preFrag = document.createDocumentFragment();
      var postFrag = document.createDocumentFragment();
      realCards.forEach(function (card) {
        var pre = card.cloneNode(true);
        pre.setAttribute("data-fest-clone", "1");
        pre.setAttribute("aria-hidden", "true");
        demoteCloneMedia(pre);
        preFrag.appendChild(pre);

        var post = card.cloneNode(true);
        post.setAttribute("data-fest-clone", "1");
        post.setAttribute("aria-hidden", "true");
        demoteCloneMedia(post);
        postFrag.appendChild(post);
      });
      track.insertBefore(preFrag, track.firstChild);
      track.appendChild(postFrag);
    }

    var cards = Array.prototype.slice.call(track.querySelectorAll(".festivals-poster"));
    var layoutLeft = new Array(cards.length);
    var layoutWidth = new Array(cards.length);
    var layoutReady = false;
    var cachedSpan = 0;
    var farPoseApplied = new Array(cards.length);

    var dots = [];
    var activeIndex = Math.floor(realCount / 2);
    var ticking = false;
    var dragTick = false;
    var animFrame = 0;
    var wrapping = false;
    var reduced =
      window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    var pointerId = null;
    var dragActive = false;
    var suppressClick = false;
    var pressCard = null;
    var linkOpened = false;
    var startX = 0;
    var startScroll = 0;
    var lastX = 0;
    var lastT = 0;
    var velocity = 0;
    var settleTimer = 0;

    function openCardLink(card) {
      if (!card || linkOpened) return;
      var href = card.getAttribute("href");
      if (!href) return;
      linkOpened = true;
      setTimeout(function () {
        linkOpened = false;
      }, 400);
      // Prefer a real <a> activation over window.open(features) — the latter is
      // often treated as a popup and blocked after pointer-capture drag setup.
      var a = document.createElement("a");
      a.href = href;
      a.target = card.getAttribute("target") || "_blank";
      a.rel = card.getAttribute("rel") || "noopener noreferrer";
      a.style.display = "none";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    }

    function armClickSuppress() {
      suppressClick = true;
      setTimeout(function () {
        suppressClick = false;
      }, 0);
    }

    function logicalOf(physical) {
      return ((physical % realCount) + realCount) % realCount;
    }

    function middlePhysical(logical) {
      if (!loop) return clamp(logical, 0, realCount - 1);
      return realCount + clamp(logical, 0, realCount - 1);
    }

    if (dotsWrap) {
      dotsWrap.innerHTML = "";
      for (var d = 0; d < realCount; d++) {
        (function (logical) {
          var dot = document.createElement("button");
          dot.type = "button";
          dot.className = "festivals-deck__dot";
          dot.setAttribute("aria-label", String(logical + 1));
          dot.addEventListener("click", function () {
            scrollToIndex(middlePhysical(logical));
          });
          dotsWrap.appendChild(dot);
          dots.push(dot);
        })(d);
      }
    }

    function refreshLayoutCache() {
      for (var i = 0; i < cards.length; i++) {
        layoutLeft[i] = cards[i].offsetLeft;
        layoutWidth[i] = cards[i].offsetWidth;
        farPoseApplied[i] = false;
      }
      layoutReady = true;
      cachedSpan =
        loop && cards.length > realCount
          ? layoutLeft[realCount] - layoutLeft[0]
          : 0;
    }

    function ensureLayout() {
      if (!layoutReady) refreshLayoutCache();
    }

    function setSpan() {
      ensureLayout();
      return cachedSpan;
    }

    function targetLeftFor(i) {
      ensureLayout();
      var idx = clamp(i, 0, cards.length - 1);
      var mid = layoutLeft[idx] + layoutWidth[idx] / 2;
      var maxScroll = Math.max(0, track.scrollWidth - track.clientWidth);
      return clamp(mid - track.clientWidth / 2, 0, maxScroll);
    }

    function nearestIndex() {
      ensureLayout();
      var center = track.scrollLeft + track.clientWidth / 2;
      var best = 0;
      var bestDist = Infinity;
      for (var i = 0; i < cards.length; i++) {
        var mid = layoutLeft[i] + layoutWidth[i] / 2;
        var dist = Math.abs(mid - center);
        if (dist < bestDist) {
          bestDist = dist;
          best = i;
        }
      }
      return best;
    }

    /**
     * If viewport is on a clone set, jump by one deck width with no animation
     * so the middle set stays under the finger / settle target.
     */
    function normalizeLoop() {
      if (!loop || wrapping) return 0;
      var idx = nearestIndex();
      var span = setSpan();
      if (!span) return 0;

      var jumped = 0;
      if (idx < realCount) {
        wrapping = true;
        track.scrollLeft += span;
        jumped = span;
        wrapping = false;
      } else if (idx >= realCount * 2) {
        wrapping = true;
        track.scrollLeft -= span;
        jumped = -span;
        wrapping = false;
      }
      return jumped;
    }

    function applyFarPose(card, i) {
      if (farPoseApplied[i]) return;
      card.style.setProperty("--fest-scale", "0.68");
      card.style.setProperty("--fest-opacity", "0.32");
      card.style.setProperty("--fest-lift", "0px");
      card.style.setProperty("--fest-x", "0px");
      card.style.zIndex = "0";
      card.classList.remove("is-active");
      farPoseApplied[i] = true;
    }

    function updateMotion() {
      ensureLayout();
      var viewCenter = track.scrollLeft + track.clientWidth / 2;
      var best = 0;
      var bestAbs = Infinity;

      for (var i = 0; i < cards.length; i++) {
        var w = Math.max(layoutWidth[i], 1);
        var mid = layoutLeft[i] + w / 2;
        var delta = (mid - viewCenter) / w;
        var abs = Math.abs(delta);

        if (abs < bestAbs) {
          bestAbs = abs;
          best = i;
        }

        if (abs <= HYDRATE_ABS) {
          hydrateCardMedia(cards[i]);
        }

        if (abs > FAR_ABS) {
          applyFarPose(cards[i], i);
          continue;
        }

        farPoseApplied[i] = false;
        var proximity = clamp(1 - abs * 0.72, 0, 1);
        var ease = proximity * proximity * (3 - 2 * proximity);

        var scale = 0.68 + ease * 0.4;
        var opacity = 0.32 + ease * 0.68;
        var lift = ease * 26;
        var shift = clamp(-delta * 34, -44, 44);
        var z = Math.round(ease * 50);

        var card = cards[i];
        card.style.setProperty("--fest-scale", scale.toFixed(4));
        card.style.setProperty("--fest-opacity", opacity.toFixed(4));
        card.style.setProperty("--fest-lift", lift.toFixed(2) + "px");
        card.style.setProperty("--fest-x", shift.toFixed(2) + "px");
        card.style.zIndex = String(z);
        card.classList.toggle("is-active", abs < 0.38);
      }

      var logical = logicalOf(best);
      hydrateCardMedia(cards[middlePhysical(logical)]);
      if (loop) {
        hydrateCardMedia(cards[middlePhysical((logical + 1) % realCount)]);
        hydrateCardMedia(cards[middlePhysical((logical - 1 + realCount) % realCount)]);
      }

      if (logical !== activeIndex) {
        activeIndex = logical;
        for (var di = 0; di < dots.length; di++) {
          dots[di].classList.toggle("is-active", di === activeIndex);
        }
      }

      ticking = false;
      dragTick = false;
    }

    function animateScrollTo(left) {
      if (animFrame) cancelAnimationFrame(animFrame);
      var maxScroll = Math.max(0, track.scrollWidth - track.clientWidth);
      left = clamp(left, 0, maxScroll);
      var start = track.scrollLeft;
      var delta = left - start;
      if (Math.abs(delta) < 1) {
        track.scrollLeft = left;
        normalizeLoop();
        updateMotion();
        animFrame = 0;
        return;
      }
      if (reduced) {
        track.scrollLeft = left;
        normalizeLoop();
        updateMotion();
        animFrame = 0;
        return;
      }
      var duration = clamp(Math.abs(delta) * 0.5, 320, 620);
      var t0 = performance.now();

      function step(now) {
        var t = clamp((now - t0) / duration, 0, 1);
        track.scrollLeft = start + delta * easeOutCubic(t);
        updateMotion();
        if (t < 1) {
          animFrame = requestAnimationFrame(step);
        } else {
          animFrame = 0;
          normalizeLoop();
          updateMotion();
        }
      }
      animFrame = requestAnimationFrame(step);
    }

    function scrollToIndex(i) {
      animateScrollTo(targetLeftFor(i));
    }

    function settleToNearest(preferDir) {
      ensureLayout();
      var idx = nearestIndex();
      if (preferDir === 1 && idx < cards.length - 1) {
        var center = track.scrollLeft + track.clientWidth / 2;
        var mid = layoutLeft[idx] + layoutWidth[idx] / 2;
        if (center > mid + 8) idx += 1;
      } else if (preferDir === -1 && idx > 0) {
        var center2 = track.scrollLeft + track.clientWidth / 2;
        var mid2 = layoutLeft[idx] + layoutWidth[idx] / 2;
        if (center2 < mid2 - 8) idx -= 1;
      }
      animateScrollTo(targetLeftFor(idx));
    }

    function onScrollCoalesced() {
      if (wrapping) return;
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(function () {
        if (!dragActive) normalizeLoop();
        updateMotion();
      });
    }

    function scheduleSettle() {
      if (animFrame || dragActive) return;
      clearTimeout(settleTimer);
      settleTimer = setTimeout(function () {
        if (animFrame || dragActive) return;
        normalizeLoop();
        var idx = nearestIndex();
        var target = targetLeftFor(idx);
        if (Math.abs(track.scrollLeft - target) > 6) {
          animateScrollTo(target);
        } else {
          updateMotion();
        }
      }, 80);
    }

    function endDrag(e) {
      if (pointerId === null || (e && e.pointerId !== pointerId)) return;
      try {
        if (typeof track.hasPointerCapture === "function") {
          if (track.hasPointerCapture(pointerId)) track.releasePointerCapture(pointerId);
        } else {
          track.releasePointerCapture(pointerId);
        }
      } catch (_) {}
      pointerId = null;
      track.classList.remove("is-dragging");

      var card = pressCard;
      pressCard = null;
      var cancelled = e && e.type === "pointercancel";
      var wasDragging = dragActive;
      dragActive = false;

      // Tap (movement < DRAG_THRESHOLD): open official site.
      // Native click is unreliable with touch-action:none + optional capture.
      if (!wasDragging) {
        velocity = 0;
        if (card && !cancelled) {
          armClickSuppress();
          openCardLink(card);
        }
        return;
      }

      // Real drag: suppress the following ghost click; do not navigate.
      armClickSuppress();

      normalizeLoop();
      updateMotion();

      if (Math.abs(velocity) > 0.45) {
        var dir = velocity > 0 ? -1 : 1;
        scrollToIndex(clamp(nearestIndex() + dir, 0, cards.length - 1));
      } else {
        settleToNearest(0);
      }
      velocity = 0;
    }

    track.addEventListener("pointerdown", function (e) {
      if (e.pointerType === "mouse" && e.button !== 0) return;
      if (animFrame) {
        cancelAnimationFrame(animFrame);
        animFrame = 0;
      }
      clearTimeout(settleTimer);

      pointerId = e.pointerId;
      dragActive = false;
      suppressClick = false;
      pressCard =
        e.target && e.target.closest
          ? e.target.closest(".festivals-poster")
          : null;
      if (pressCard && !track.contains(pressCard)) pressCard = null;
      startX = e.clientX;
      lastX = e.clientX;
      lastT = performance.now();
      startScroll = track.scrollLeft;
      velocity = 0;
      // Do not setPointerCapture until drag threshold — keeps taps clickable.
    });

    track.addEventListener("pointermove", function (e) {
      if (pointerId === null || e.pointerId !== pointerId) return;

      var dx = e.clientX - startX;
      var now = performance.now();
      var dt = Math.max(now - lastT, 1);
      var instantV = (e.clientX - lastX) / dt;
      velocity = velocity * 0.7 + instantV * 0.3;
      lastX = e.clientX;
      lastT = now;

      if (!dragActive && Math.abs(dx) >= DRAG_THRESHOLD) {
        dragActive = true;
        track.classList.add("is-dragging");
        try {
          track.setPointerCapture(pointerId);
        } catch (_) {}
      }

      if (dragActive) {
        if (e.cancelable) e.preventDefault();
        track.scrollLeft = startScroll - dx;
        var jumped = normalizeLoop();
        if (jumped) startScroll += jumped;
        if (!dragTick) {
          dragTick = true;
          requestAnimationFrame(function () {
            updateMotion();
          });
        }
      }
    });

    track.addEventListener("pointerup", endDrag);
    track.addEventListener("pointercancel", endDrag);

    cards.forEach(function (card) {
      // Clones keep href/target via cloneNode; ensure blank target for safety.
      if (!card.getAttribute("href")) return;
      if (!card.getAttribute("target")) {
        card.setAttribute("target", "_blank");
      }
      if (!card.getAttribute("rel")) {
        card.setAttribute("rel", "noopener noreferrer");
      }

      card.addEventListener(
        "click",
        function (e) {
          // After a drag (or pointerup that already opened): block ghost clicks.
          if (suppressClick || dragActive || linkOpened) {
            e.preventDefault();
            e.stopPropagation();
            return;
          }
          // Fallback if pointerup did not open (e.g. keyboard activation).
          if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
          e.preventDefault();
          e.stopPropagation();
          openCardLink(card);
        },
        true
      );
      card.addEventListener("dragstart", function (e) {
        e.preventDefault();
      });
    });

    track.addEventListener("scroll", onScrollCoalesced, { passive: true });

    var resizeTimer = 0;
    window.addEventListener("resize", function () {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(function () {
        layoutReady = false;
        refreshLayoutCache();
        scrollToIndex(middlePhysical(activeIndex));
      }, 100);
    });

    track.addEventListener("keydown", function (e) {
      if (e.key === "ArrowLeft") {
        e.preventDefault();
        scrollToIndex(clamp(nearestIndex() - 1, 0, cards.length - 1));
      } else if (e.key === "ArrowRight") {
        e.preventDefault();
        scrollToIndex(clamp(nearestIndex() + 1, 0, cards.length - 1));
      }
    });

    track.addEventListener("scrollend", scheduleSettle);

    function goHome() {
      refreshLayoutCache();
      var home = middlePhysical(Math.floor(realCount / 2));
      hydrateCardMedia(cards[home]);
      if (home > 0) hydrateCardMedia(cards[home - 1]);
      if (home < cards.length - 1) hydrateCardMedia(cards[home + 1]);
      track.scrollLeft = targetLeftFor(home);
      normalizeLoop();
      updateMotion();
    }

    function afterLayout(fn) {
      requestAnimationFrame(function () {
        requestAnimationFrame(fn);
      });
    }

    /** Wait only for home-neighbor middle-deck images (skip far lazy + clones). */
    function whenReady(fn) {
      var home = middlePhysical(Math.floor(realCount / 2));
      var pending = 0;
      var done = false;

      function finish() {
        if (done) return;
        done = true;
        afterLayout(fn);
      }

      function onOne() {
        pending -= 1;
        if (pending <= 0) finish();
      }

      for (var i = home - 1; i <= home + 1; i++) {
        if (i < 0 || i >= cards.length) continue;
        var imgs = cards[i].querySelectorAll("img[src]");
        for (var j = 0; j < imgs.length; j++) {
          var img = imgs[j];
          if (img.complete) continue;
          pending += 1;
          img.addEventListener("load", onOne, { once: true });
          img.addEventListener("error", onOne, { once: true });
        }
      }

      if (pending === 0) finish();
      else setTimeout(finish, 400);
    }

    var homeLogical = Math.floor(realCount / 2);
    for (var hi = 0; hi < realCount; hi++) {
      var physical = middlePhysical(hi);
      if (Math.abs(hi - homeLogical) <= 1) {
        hydrateCardMedia(cards[physical]);
        var img0 = cards[physical].querySelector("img");
        if (img0) {
          img0.setAttribute("loading", "eager");
          img0.setAttribute("fetchpriority", hi === homeLogical ? "high" : "auto");
          img0.setAttribute("decoding", "async");
        }
      } else {
        cards[physical].setAttribute("data-fest-hydrated", "1");
        var imgL = cards[physical].querySelector("img");
        if (imgL) {
          imgL.setAttribute("loading", "lazy");
          imgL.setAttribute("decoding", "async");
        }
      }
    }

    whenReady(goHome);
  }

  function init() {
    document.querySelectorAll("[data-festivals-slider]").forEach(bind);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
