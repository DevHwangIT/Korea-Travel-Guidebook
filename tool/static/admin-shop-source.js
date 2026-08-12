/**
 * Shop admin: sourceType panels + URL/주소 자동 채우기.
 */
(function () {
  var PLACEHOLDERS = {
    naver: "https://map.naver.com/… 또는 https://naver.me/…",
    kakao: "https://map.kakao.com/… 또는 https://kko.to/…",
    google: "https://maps.app.goo.gl/… 또는 Google Maps 공유 링크",
    custom: "서울 중구 … (주소만 입력해도 됩니다)",
  };

  var HINTS = {
    naver:
      "네이버 지도/플레이스 공유 링크를 붙여 넣고 ‘URL/주소로 채우기’를 누르세요. 이름·지도는 자동, 전화·영업시간은 직접 확인이 필요할 수 있습니다.",
    kakao:
      "카카오맵 가게 공유 링크를 붙여 넣고 ‘URL/주소로 채우기’를 누르세요.",
    google:
      "구글 지도·비즈니스 공유 링크를 붙여 넣고 ‘URL/주소로 채우기’를 누르세요.",
    custom:
      "도로명 주소(또는 상호+지역)를 넣고 ‘URL/주소로 채우기’를 누르면 지도가 채워집니다.",
  };

  function currentType(root) {
    var sel = root.querySelector("[data-shop-source-type]");
    var v = ((sel && sel.value) || "custom").toLowerCase();
    if (v !== "naver" && v !== "kakao" && v !== "google" && v !== "custom") {
      return "custom";
    }
    return v;
  }

  function setHidden(el, hidden) {
    if (!el) return;
    el.hidden = !!hidden;
  }

  function apply(root) {
    var form = root.closest("form") || document;
    var type = currentType(root);
    var isCustom = type === "custom";

    Array.prototype.forEach.call(
      form.querySelectorAll('[data-shop-source-panel="map"]'),
      function (el) {
        setHidden(el, isCustom);
      }
    );
    Array.prototype.forEach.call(
      form.querySelectorAll('[data-shop-source-panel="custom-extra"]'),
      function (el) {
        setHidden(el, !isCustom);
      }
    );
    // Cover photo always available
    Array.prototype.forEach.call(
      form.querySelectorAll('[data-shop-source-panel="custom-media"]'),
      function (el) {
        setHidden(el, false);
      }
    );

    var place = form.querySelector("[data-shop-place-url]");
    if (place) {
      place.placeholder = PLACEHOLDERS[type] || PLACEHOLDERS.google;
      if (!isCustom) place.setAttribute("required", "required");
      else place.removeAttribute("required");
    }
    var resolveInput = form.querySelector("[data-shop-resolve-input]");
    if (resolveInput) {
      resolveInput.placeholder = PLACEHOLDERS[type] || PLACEHOLDERS.google;
    }
    var hint = form.querySelector("[data-shop-place-hint]");
    if (hint) hint.textContent = HINTS[type] || HINTS.google;
  }

  function setStatus(form, msg, isError) {
    var el = form.querySelector("[data-shop-resolve-status]");
    if (!el) return;
    el.textContent = msg || "";
    el.style.color = isError ? "#b42318" : "#1f3a32";
  }

  function fillFromResolve(form, data) {
    if (!data) return;
    var sel = form.querySelector("[data-shop-source-type]");
    if (sel && data.sourceType) {
      sel.value = data.sourceType;
      apply(sel.closest("[data-shop-source-root]") || form);
    }

    function setVal(selector, value) {
      if (value == null || value === "") return;
      var el = form.querySelector(selector);
      if (el) el.value = value;
    }

    setVal('[data-shop-field="name"]', data.name);
    setVal('[name="name_ko"]', data.name);
    setVal('[data-shop-field="address"]', data.address);
    setVal('[name="location_ko"]', data.address);
    setVal('[data-shop-field="placeUrl"]', data.placeUrl);
    setVal("[data-shop-place-url]", data.placeUrl);
    setVal('[data-shop-field="phone"]', data.phone);
    setVal('[name="phone"]', data.phone);
    setVal('[data-shop-field="hours"]', data.hours);
    setVal('[name="hours"]', data.hours);
    setVal('[data-shop-field="imageUrl"]', data.imageUrl);

    var resolveInput = form.querySelector("[data-shop-resolve-input]");
    if (resolveInput && data.placeUrl) resolveInput.value = data.placeUrl;
    else if (resolveInput && data.address) resolveInput.value = data.address;

    var previewWrap = form.querySelector("[data-shop-resolve-preview]");
    var previewImg = form.querySelector("[data-shop-preview-img]");
    if (previewWrap && previewImg) {
      if (data.imageUrl) {
        previewWrap.hidden = false;
        previewImg.hidden = false;
        previewImg.src = data.imageUrl;
        previewImg.alt = data.name || data.previewTitle || "";
      } else {
        previewImg.hidden = true;
        previewImg.removeAttribute("src");
      }
    }

    var parts = [];
    if (data.notes && data.notes.length) parts = parts.concat(data.notes);
    if (data.warnings && data.warnings.length) {
      parts = parts.concat(data.warnings);
    }
    setStatus(form, parts.join(" ") || "채웠습니다. 저장 전 확인해 주세요.", false);
  }

  function resolveShop(form) {
    var input =
      form.querySelector("[data-shop-resolve-input]") ||
      form.querySelector("[data-shop-place-url]");
    var q = ((input && input.value) || "").trim();
    if (!q) {
      setStatus(form, "URL 또는 주소를 먼저 입력하세요.", true);
      return;
    }
    var sel = form.querySelector("[data-shop-source-type]");
    var sourceType = (sel && sel.value) || "";
    var btn = form.querySelector("[data-shop-resolve-btn]");
    if (btn) {
      btn.disabled = true;
      btn.textContent = "채우는 중…";
    }
    setStatus(form, "불러오는 중…", false);

    var body = new URLSearchParams();
    body.set("q", q);
    body.set("source_type", sourceType);

    fetch("/api/shop/resolve", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8" },
      body: body.toString(),
    })
      .then(function (res) {
        return res.json().then(function (data) {
          return { ok: res.ok, data: data };
        });
      })
      .then(function (pack) {
        if (!pack.data || pack.data.ok === false) {
          setStatus(
            form,
            (pack.data &&
              pack.data.warnings &&
              pack.data.warnings.join(" ")) ||
              "채우기에 실패했습니다.",
            true
          );
          return;
        }
        fillFromResolve(form, pack.data);
      })
      .catch(function () {
        setStatus(form, "네트워크 오류로 채우기에 실패했습니다.", true);
      })
      .finally(function () {
        if (btn) {
          btn.disabled = false;
          btn.textContent = "URL/주소로 채우기";
        }
      });
  }

  function boot() {
    document.querySelectorAll("[data-shop-source-type]").forEach(function (sel) {
      var root =
        sel.closest("[data-shop-source-root]") ||
        sel.closest("form") ||
        document;
      if (sel._shopSourceReady) return;
      sel._shopSourceReady = true;
      sel.addEventListener("change", function () {
        apply(root);
      });
      apply(root);
    });

    document.querySelectorAll("[data-shop-resolve-btn]").forEach(function (btn) {
      if (btn._shopResolveReady) return;
      btn._shopResolveReady = true;
      btn.addEventListener("click", function (e) {
        e.preventDefault();
        var form = btn.closest("form");
        if (form) resolveShop(form);
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
