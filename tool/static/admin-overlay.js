/**
 * Viewer-identical admin overlay (localhost content-admin only).
 * Enabled by ?admin=1 or localStorage.guideAdmin=1.
 * Does not ship enabled on GitHub Pages (bootstrap is injected only by admin server).
 */
(function () {
  var STORAGE_KEY = "guideAdmin";
  var API = "";

  function qs(sel, root) {
    return (root || document).querySelector(sel);
  }
  function qsa(sel, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(sel));
  }

  function isAdminEnabled() {
    try {
      var q = new URLSearchParams(location.search);
      if (q.get("admin") === "1") {
        localStorage.setItem(STORAGE_KEY, "1");
        document.cookie = "guideAdmin=1; path=/; SameSite=Lax";
        return true;
      }
      if (q.get("admin") === "0") {
        localStorage.removeItem(STORAGE_KEY);
        document.cookie = "guideAdmin=; path=/; Max-Age=0";
        return false;
      }
      return localStorage.getItem(STORAGE_KEY) === "1";
    } catch (e) {
      return false;
    }
  }

  function toast(msg, isError) {
    var el = document.createElement("div");
    el.className = "ga-toast" + (isError ? " error" : "");
    el.textContent = msg;
    document.body.appendChild(el);
    setTimeout(function () {
      el.remove();
    }, 3200);
  }

  function pathInfo() {
    var p = location.pathname.replace(/\\/g, "/");
    var place = /\/pages\/transportation\/places\/([^/]+)\/(?:index\.html)?$/.exec(p);
    if (place) return { kind: "place", slug: place[1] };
    var prep = /\/pages\/before-trip\/(docs|money|connect|pack|solo)\/(?:index\.html)?$/.exec(p);
    if (prep) return { kind: "before-trip", slug: prep[1] };
    var prepHub = /\/pages\/before-trip\/(?:index\.html)?$/.exec(p);
    if (prepHub) return { kind: "before-trip-hub" };
    var funPost = /\/pages\/fun\/([^/]+)\/(?:index\.html)?$/.exec(p);
    if (funPost) return { kind: "fun", slug: funPost[1] };
    var buyHub = /\/pages\/buy\/(?:index\.html)?$/.exec(p);
    if (buyHub) return { kind: "buy-hub" };
    var shopPost = /\/pages\/shopping\/(olive|daiso|duty|market)\/(?:index\.html)?$/.exec(p);
    if (shopPost) return { kind: "shopping", slug: shopPost[1] };
    var shopHub = /\/pages\/shopping\/(?:index\.html)?$/.exec(p);
    if (shopHub) return { kind: "shopping-hub" };
    var tipPost = /\/pages\/travel-tips\/(daily|restaurant|transport)\/(?:index\.html)?$/.exec(p);
    if (tipPost) return { kind: "tips", slug: tipPost[1] };
    var tipHub = /\/pages\/travel-tips\/(?:index\.html)?$/.exec(p);
    if (tipHub) return { kind: "tips-hub" };
    var appPost =
      /\/pages\/apps\/(kakao|naver|papago|kakaotalk|yanolja|yeogi|coupang|tmoney)\/(?:index\.html)?$/.exec(
        p
      );
    if (appPost) return { kind: "apps", slug: appPost[1] };
    var appHub = /\/pages\/apps\/(?:index\.html)?$/.exec(p);
    if (appHub) return { kind: "apps-hub" };
    var emPost =
      /\/pages\/emergency\/(police|fire|tourist|guide)\/(?:index\.html)?$/.exec(p);
    if (emPost) return { kind: "emergency", slug: emPost[1] };
    var emHub = /\/pages\/emergency\/(?:index\.html)?$/.exec(p);
    if (emHub) return { kind: "emergency-hub" };
    var shop = /\/pages\/foods\/(?:meals|desserts)\/[^/]+\/([^/]+)\/(?:index\.html)?$/.exec(p);
    if (shop && shop[1] !== "index") return { kind: "shop", slug: shop[1] };
    var souvenir = /\/pages\/souvenir\/([^/]+)\/(?:index\.html)?$/.exec(p);
    if (souvenir && souvenir[1] !== "index") return { kind: "souvenir", slug: souvenir[1] };
    var transport = /\/pages\/transportation\/(?:index\.html)?$/.exec(p);
    if (transport) return { kind: "transport-hub" };
    var souvenirHub = /\/pages\/souvenir\/(?:index\.html)?$/.exec(p);
    if (souvenirHub) return { kind: "souvenir-hub" };
    var foods = /\/pages\/foods\/(meals|desserts)\/([^/]+)\/(?:index\.html)?$/.exec(p);
    if (foods) return { kind: "dish", dishKind: foods[1], slug: foods[2] };
    return { kind: "other" };
  }

  function api(path, opts) {
    opts = opts || {};
    return fetch(API + path, opts).then(function (r) {
      var ct = r.headers.get("content-type") || "";
      if (ct.indexOf("application/json") !== -1) {
        return r.json().then(function (j) {
          if (!r.ok || j.ok === false) {
            throw new Error((j && j.error) || "요청 실패");
          }
          return j;
        });
      }
      if (!r.ok) throw new Error("요청 실패 (" + r.status + ")");
      return r.text();
    });
  }

  function buildBar(info) {
    var bar = document.createElement("div");
    bar.className = "ga-bar";
    bar.innerHTML =
      "<strong>관리 모드</strong>" +
      '<span class="ga-note">로컬 관리 서버에서만 최신이 보입니다. GitHub Pages는 푸시 후 반영</span>' +
      '<span class="ga-spacer"></span>' +
      '<button type="button" class="ga-btn primary" data-ga-new>새 글</button>' +
      '<a class="ga-btn ghost ga-hide-sm" href="/cms">전체 목록</a>' +
      '<button type="button" class="ga-btn ghost" data-ga-exit>관리 종료</button>';
    bar.querySelector("[data-ga-exit]").addEventListener("click", function () {
      localStorage.removeItem(STORAGE_KEY);
      document.cookie = "guideAdmin=; path=/; Max-Age=0";
      var u = new URL(location.href);
      u.searchParams.delete("admin");
      location.href = u.pathname + u.search + u.hash;
    });
    bar.querySelector("[data-ga-new]").addEventListener("click", function () {
      openCreate(info);
    });
    return bar;
  }

  var panelEl = null;
  var backdropEl = null;

  function ensurePanel() {
    if (panelEl) return panelEl;
    backdropEl = document.createElement("div");
    backdropEl.className = "ga-backdrop";
    backdropEl.addEventListener("click", closePanel);
    panelEl = document.createElement("aside");
    panelEl.className = "ga-panel";
    panelEl.innerHTML =
      '<div class="ga-panel-head"><h2 data-ga-title>수정</h2>' +
      '<button type="button" class="ga-btn ghost" data-ga-close>닫기</button></div>' +
      '<div class="ga-panel-body" data-ga-body></div>' +
      '<div class="ga-panel-foot">' +
      '<button type="button" class="ga-btn primary" data-ga-save>저장</button>' +
      '<button type="button" class="ga-btn danger" data-ga-delete hidden>삭제</button>' +
      "</div>";
    panelEl.querySelector("[data-ga-close]").addEventListener("click", closePanel);
    document.body.appendChild(backdropEl);
    document.body.appendChild(panelEl);
    return panelEl;
  }

  function closePanel() {
    if (!panelEl) return;
    panelEl.classList.remove("is-open");
    if (backdropEl) backdropEl.classList.remove("is-open");
  }

  function openPanel(title, bodyHtml, onSave, onDelete) {
    var panel = ensurePanel();
    qs("[data-ga-title]", panel).textContent = title;
    qs("[data-ga-body]", panel).innerHTML = bodyHtml;
    var saveBtn = qs("[data-ga-save]", panel);
    var delBtn = qs("[data-ga-delete]", panel);
    saveBtn.onclick = function () {
      Promise.resolve(onSave(qs("[data-ga-body]", panel)))
        .then(function (msg) {
          toast(msg || "저장했어요");
          closePanel();
          setTimeout(function () {
            location.reload();
          }, 450);
        })
        .catch(function (err) {
          toast(String(err.message || err), true);
        });
    };
    if (onDelete) {
      delBtn.hidden = false;
      delBtn.onclick = function () {
        if (!confirm("정말 삭제할까요?")) return;
        Promise.resolve(onDelete())
          .then(function (msg) {
            var redirect =
              msg && typeof msg === "object" && msg.redirect
                ? msg.redirect
                : "/pages/transportation/index.html?admin=1";
            toast(
              msg && typeof msg === "object"
                ? msg.message || "삭제했어요"
                : msg || "삭제했어요"
            );
            closePanel();
            setTimeout(function () {
              location.href = redirect;
            }, 400);
          })
          .catch(function (err) {
            toast(String(err.message || err), true);
          });
      };
    } else {
      delBtn.hidden = true;
      delBtn.onclick = null;
    }
    backdropEl.classList.add("is-open");
    panel.classList.add("is-open");
  }

  function field(name, label, value, type) {
    type = type || "text";
    if (type === "textarea") {
      return (
        '<div class="field"><label>' +
        label +
        '</label><textarea name="' +
        name +
        '" rows="5">' +
        escapeHtml(value || "") +
        "</textarea></div>"
      );
    }
    if (type === "select") {
      return (
        '<div class="field"><label>' +
        label +
        '</label><select name="' +
        name +
        '">' +
        value +
        "</select></div>"
      );
    }
    return (
      '<div class="field"><label>' +
      label +
      '</label><input type="' +
      type +
      '" name="' +
      name +
      '" value="' +
      escapeAttr(value || "") +
      '"></div>'
    );
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }
  function escapeAttr(s) {
    return escapeHtml(s).replace(/"/g, "&quot;");
  }

  function formValues(root) {
    var out = {};
    qsa("input, textarea, select", root).forEach(function (el) {
      if (!el.name) return;
      out[el.name] = el.value;
    });
    return out;
  }

  function regionOptions(selected) {
    return [
      "seoul",
      "gyeonggi",
      "incheon",
      "gangwon",
      "busan",
      "gyeongju",
      "gyeongsang",
      "jeolla",
      "jeju",
    ]
      .map(function (r) {
        var labels = {
          seoul: "서울",
          gyeonggi: "경기",
          incheon: "인천",
          gangwon: "강원",
          busan: "부산",
          gyeongju: "경주",
          gyeongsang: "경상",
          jeolla: "전라",
          jeju: "제주",
        };
        return (
          '<option value="' +
          r +
          '"' +
          (r === selected ? " selected" : "") +
          ">" +
          labels[r] +
          "</option>"
        );
      })
      .join("");
  }

  function typeOptions(selected) {
    return [
      ["city", "도시·번화가"],
      ["nature", "자연·공원"],
      ["heritage", "유적·문화"],
      ["airport", "공항"],
      ["info", "안내·대사관"],
    ]
      .map(function (pair) {
        return (
          '<option value="' +
          pair[0] +
          '"' +
          (pair[0] === selected ? " selected" : "") +
          ">" +
          pair[1] +
          "</option>"
        );
      })
      .join("");
  }

  function openPlaceEditor(slug, isNew) {
    var load = isNew
      ? Promise.resolve({
          slug: "",
          region: "seoul",
          texts: { ko: { name: "", desc: "", how: "", address: "" } },
          body: [],
        })
      : api("/api/places/get?slug=" + encodeURIComponent(slug));

    load.then(function (data) {
      var ko = (data.texts && data.texts.ko) || {};
      var bodyText = "";
      (data.body || []).forEach(function (b) {
        if (b && b.type === "text") bodyText += (b.ko || "") + "\n\n";
      });
      bodyText = bodyText.trim();
      var html =
        (isNew
          ? field("slug", "슬러그 (영문)", "", "text")
          : '<input type="hidden" name="slug" value="' + escapeAttr(data.slug) + '">') +
        field("region", "지역", regionOptions(data.region || "seoul"), "select") +
        field("place_type", "지도 핀 유형", typeOptions(data.place_type || "city"), "select") +
        field("name_ko", "이름 (한국어)", ko.name) +
        field("desc_ko", "짧은 소개", ko.desc) +
        field("address_ko", "지도 주소/장소명", ko.address) +
        field("how_ko", "가는 방법", ko.how, "textarea") +
        field("body_ko", "내용", bodyText, "textarea") +
        '<p class="muted" style="font-size:12px;opacity:.75">저장하면 자동 번역됩니다.</p>';

      openPanel(isNew ? "새 명소" : "명소 수정", html, function (root) {
        var v = formValues(root);
        var fd = new FormData();
        Object.keys(v).forEach(function (k) {
          fd.append(k, v[k]);
        });
        fd.append("name_ko", v.name_ko || "");
        fd.append("desc_ko", v.desc_ko || "");
        fd.append("address_ko", v.address_ko || "");
        fd.append("how_ko", v.how_ko || "");
        return api(isNew ? "/api/places/create" : "/api/places/save", {
          method: "POST",
          body: fd,
        }).then(function (j) {
          return j.message || "저장했어요";
        });
      }, isNew
        ? null
        : function () {
            var fd = new FormData();
            fd.append("slug", slug);
            return api("/api/places/delete", { method: "POST", body: fd }).then(function () {
              return {
                message: "삭제했어요",
                redirect: "/pages/transportation/index.html?admin=1",
              };
            });
          });
    }).catch(function (err) {
      toast(String(err.message || err), true);
    });
  }

  function openCreate(info) {
    if (info.kind === "transport-hub" || info.kind === "place") {
      openPlaceEditor("", true);
      return;
    }
    if (info.kind === "before-trip-hub" || info.kind === "before-trip") {
      location.href = "/section?id=beforeTrip";
      return;
    }
    if (info.kind === "shopping-hub" || info.kind === "shopping") {
      location.href = "/section?id=shopping";
      return;
    }
    if (info.kind === "tips-hub" || info.kind === "tips") {
      location.href = "/section?id=tips";
      return;
    }
    if (info.kind === "apps-hub" || info.kind === "apps") {
      location.href = "/section?id=apps";
      return;
    }
    if (info.kind === "emergency-hub" || info.kind === "emergency") {
      location.href = "/section?id=emergency";
      return;
    }
    if (info.kind === "shop") {
      location.href = "/shop/new";
      return;
    }
    if (info.kind === "souvenir" || info.kind === "souvenir-hub") {
      location.href = "/section?id=souvenir";
      return;
    }
    if (info.kind === "fun" || info.kind === "buy-hub") {
      location.href = "/section?id=fun";
      return;
    }
    if (info.kind === "dish") {
      location.href = "/dish/new?kind=" + encodeURIComponent(info.dishKind || "meals");
      return;
    }
    location.href = "/cms";
  }

  function decoratePlaceCards() {
    qsa("[data-place-slug]").forEach(function (el) {
      var slug = el.getAttribute("data-place-slug");
      if (!slug || el.querySelector(".ga-card-actions")) return;
      var host = el.classList.contains("place-card-link") ? el : el;
      host.style.position = "relative";
      var box = document.createElement("div");
      box.className = "ga-card-actions";
      box.innerHTML =
        '<button type="button" class="ga-fab-edit" title="수정">✎</button>' +
        '<button type="button" class="ga-fab-del" title="삭제">×</button>';
      box.querySelector(".ga-fab-edit").addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();
        openPlaceEditor(slug, false);
      });
      box.querySelector(".ga-fab-del").addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();
        if (!confirm("「" + slug + "」 명소를 삭제할까요?")) return;
        var fd = new FormData();
        fd.append("slug", slug);
        api("/api/places/delete", { method: "POST", body: fd })
          .then(function () {
            toast("삭제했어요");
            location.reload();
          })
          .catch(function (err) {
            toast(String(err.message || err), true);
          });
      });
      host.appendChild(box);
    });
  }

  function decorateDetail(info) {
    var sectionEdit = {
      "before-trip": "beforeTrip",
      shopping: "shopping",
      tips: "tips",
      apps: "apps",
      emergency: "emergency",
      souvenir: "souvenir",
      fun: "fun",
    };
    if (
      info.kind !== "place" &&
      info.kind !== "shop" &&
      !sectionEdit[info.kind]
    ) {
      return;
    }
    var main = qs("main.page") || qs("main");
    if (!main || qs("[data-ga-edit-this]")) return;
    var wrap = document.createElement("p");
    wrap.className = "ga-list-add";
    wrap.innerHTML =
      '<button type="button" class="ga-btn primary" data-ga-edit-this>이 글 수정</button>';
    var btn = wrap.querySelector("[data-ga-edit-this]");
    btn.addEventListener("click", function () {
      if (info.kind === "place") openPlaceEditor(info.slug, false);
      else if (info.kind === "shop")
        location.href = "/shop/edit?slug=" + encodeURIComponent(info.slug);
      else if (info.kind === "souvenir")
        location.href =
          "/section?id=souvenir&group=" + encodeURIComponent(info.slug);
      else
        location.href =
          "/section?id=" +
          encodeURIComponent(sectionEdit[info.kind]) +
          "&group=" +
          encodeURIComponent(info.slug);
    });
    main.insertBefore(wrap, main.firstChild);
  }

  function decorateSectionCards(attr, sectionId) {
    qsa("[" + attr + "]").forEach(function (el) {
      var slug = el.getAttribute(attr);
      if (!slug || el.querySelector(".ga-card-actions")) return;
      el.style.position = "relative";
      var box = document.createElement("div");
      box.className = "ga-card-actions";
      box.innerHTML =
        '<button type="button" class="ga-fab-edit" title="수정">✎</button>';
      box.querySelector(".ga-fab-edit").addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();
        location.href =
          "/section?id=" +
          encodeURIComponent(sectionId) +
          "&group=" +
          encodeURIComponent(slug);
      });
      el.appendChild(box);
    });
  }

  function decoratePrepCards() {
    decorateSectionCards("data-prep-slug", "beforeTrip");
  }

  function decorateShopCards() {
    decorateSectionCards("data-shop-slug", "shopping");
  }

  function decorateTipCards() {
    decorateSectionCards("data-tip-slug", "tips");
  }

  function decorateAppCards() {
    decorateSectionCards("data-app-slug", "apps");
  }

  function decorateEmergencyCards() {
    decorateSectionCards("data-emergency-slug", "emergency");
  }

  function decorateFunCards() {
    decorateSectionCards("data-fun-slug", "fun");
    // buy hub fun cards use href path — also decorate buy-fun-card links
    qsa(".buy-fun-card[href]").forEach(function (el) {
      if (el.querySelector(".ga-card-actions")) return;
      var m = /\/fun\/([^/]+)\//.exec(el.getAttribute("href") || "");
      if (!m) return;
      var slug = m[1];
      var groupMap = {
        "coin-noraebang": "noraebang",
        "escape-room": "escape",
        "jjimjilbang": "jjim",
        "manga-cafe": "manga",
        "boardgame-cafe": "boardgame",
        "unmanned-store": "unmanned",
        "photo-booth": "photobooth",
        "lotte-world": "lotte",
        pcbang: "pcbang",
        everland: "everland",
      };
      var group = groupMap[slug] || slug;
      el.style.position = "relative";
      var box = document.createElement("div");
      box.className = "ga-card-actions";
      box.innerHTML =
        '<button type="button" class="ga-fab-edit" title="수정">✎</button>';
      box.querySelector(".ga-fab-edit").addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();
        location.href =
          "/section?id=fun&group=" + encodeURIComponent(group);
      });
      el.appendChild(box);
    });
  }

  function decorateHubAdd(info) {
    if (info.kind !== "transport-hub") return;
    var list = qs("[data-places-list]") || qs(".place-grid");
    if (!list || qs("[data-ga-add-place]")) return;
    var row = document.createElement("p");
    row.className = "ga-list-add";
    row.innerHTML =
      '<button type="button" class="ga-btn primary" data-ga-add-place>+ 명소 추가</button>';
    row.querySelector("button").addEventListener("click", function () {
      openPlaceEditor("", true);
    });
    var intro =
      qs("[data-places-list] > p") ||
      qs('[data-topic-panel="routes"] > p') ||
      list;
    if (intro && intro.parentNode) {
      intro.parentNode.insertBefore(row, intro.nextSibling);
    } else {
      list.parentNode.insertBefore(row, list);
    }
  }

  function boot() {
    if (!isAdminEnabled()) return;
    document.documentElement.classList.add("guide-admin-on");
    document.body.classList.add("guide-admin-on");
    var info = pathInfo();
    document.body.prepend(buildBar(info));
    decoratePlaceCards();
    decoratePrepCards();
    decorateShopCards();
    decorateTipCards();
    decorateAppCards();
    decorateEmergencyCards();
    decorateFunCards();
    decorateDetail(info);
    decorateHubAdd(info);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
