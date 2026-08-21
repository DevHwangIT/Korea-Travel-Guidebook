/**
 * Render freeform content body blocks from i18n messages.
 *
 * Mount: <div data-content-body data-body-path="beforeTrip.docsBody"></div>
 * Optional:
 *   data-body-show-tip-heading="1" — wrap like shop tip with TIP heading
 *   data-body-fallback-hide — CSS selector (within same parent) to hide when body present
 *
 * Shop compat: also mounts #shop-body[data-shop-slug] → restaurants.{slug}.body
 */
(function () {
  var YT_HOSTS = {
    "youtube.com": 1,
    "www.youtube.com": 1,
    "m.youtube.com": 1,
    "youtu.be": 1,
    "www.youtu.be": 1,
    "youtube-nocookie.com": 1,
    "www.youtube-nocookie.com": 1,
  };

  var SCRIPT_ROOT = (function () {
    var scr = document.currentScript;
    var src = (scr && scr.src) || "";
    var markers = ["/js/content-body.js", "/js/shop-body.js"];
    for (var m = 0; m < markers.length; m++) {
      var idx = src.indexOf(markers[m]);
      if (idx !== -1) return src.slice(0, idx + 1);
    }
    return "";
  })();

  function assetPrefix() {
    if (SCRIPT_ROOT) return SCRIPT_ROOT;
    var scripts = document.getElementsByTagName("script");
    for (var i = scripts.length - 1; i >= 0; i--) {
      var src = scripts[i].src || "";
      var markers = ["/js/content-body.js", "/js/shop-body.js"];
      for (var m = 0; m < markers.length; m++) {
        var idx = src.indexOf(markers[m]);
        if (idx !== -1) return src.slice(0, idx + 1);
      }
    }
    return "../../../../";
  }

  function extractYoutubeId(url) {
    if (!url) return "";
    var raw = String(url).trim();
    if (/^[A-Za-z0-9_-]{6,}$/.test(raw) && raw.indexOf("://") === -1) return raw;
    if (raw.indexOf("://") === -1) raw = "https://" + raw;
    try {
      var a = document.createElement("a");
      a.href = raw;
      var host = (a.hostname || "").toLowerCase();
      if (!YT_HOSTS[host]) return "";
      if (host === "youtu.be" || host === "www.youtu.be") {
        var id = (a.pathname || "").replace(/^\//, "").split("/")[0];
        return /^[A-Za-z0-9_-]{6,}$/.test(id) ? id : "";
      }
      var path = a.pathname || "";
      if (
        path.indexOf("/embed/") === 0 ||
        path.indexOf("/shorts/") === 0 ||
        path.indexOf("/live/") === 0
      ) {
        var parts = path.replace(/^\//, "").split("/");
        return parts[1] && /^[A-Za-z0-9_-]{6,}$/.test(parts[1]) ? parts[1] : "";
      }
      var m = /[?&]v=([A-Za-z0-9_-]{6,})/.exec(a.search || "");
      return m ? m[1] : "";
    } catch (e) {
      return "";
    }
  }

  function lookupRoot(lang) {
    return (window.__I18N_MESSAGES__ && window.__I18N_MESSAGES__[lang]) || null;
  }

  function lookupPath(root, dotted) {
    if (!root || !dotted) return null;
    var parts = String(dotted).split(".");
    var cur = root;
    for (var i = 0; i < parts.length; i++) {
      if (!cur || typeof cur !== "object") return null;
      cur = cur[parts[i]];
    }
    return cur;
  }

  function langFallbackOrder(lang) {
    var chain = [lang];
    if (lang === "zh-Hant") chain.push("zh");
    if (lang !== "en") chain.push("en");
    if (lang !== "ko") chain.push("ko");
    if (window.GuideI18n && typeof window.GuideI18n.fallbackLangs === "function") {
      try {
        chain = window.GuideI18n.fallbackLangs(lang) || chain;
      } catch (e) {
        /* keep local chain */
      }
    }
    var out = [];
    var seen = {};
    for (var i = 0; i < chain.length; i++) {
      var c = chain[i];
      if (!c || seen[c]) continue;
      seen[c] = true;
      out.push(c);
    }
    // Also try body keys stored without region tags
    ["ja", "zh"].forEach(function (extra) {
      if (!seen[extra]) {
        seen[extra] = true;
        out.push(extra);
      }
    });
    return out;
  }

  function tipLabel(lang) {
    var order = langFallbackOrder(lang);
    for (var i = 0; i < order.length; i++) {
      var root = lookupRoot(order[i]);
      if (root && root.common && root.common.tip) return String(root.common.tip);
    }
    return "TIP";
  }

  function getBody(path, lang) {
    var order = langFallbackOrder(lang);
    for (var i = 0; i < order.length; i++) {
      var root = lookupRoot(order[i]);
      var raw = lookupPath(root, path);
      if (Array.isArray(raw) && raw.length) return raw;
    }
    for (var j = 0; j < order.length; j++) {
      var root2 = lookupRoot(order[j]);
      var raw2 = lookupPath(root2, path);
      if (Array.isArray(raw2)) return raw2;
    }
    return [];
  }

  function textFor(block, lang) {
    if (!block) return "";
    var order = langFallbackOrder(lang);
    for (var i = 0; i < order.length; i++) {
      var key = order[i];
      if (block[key] != null && block[key] !== "") return String(block[key]);
    }
    return String(block.ko || block.en || block.ja || block.zh || "");
  }

  function looksLikeHtml(s) {
    return /<[a-z][\s\S]*>/i.test(String(s || ""));
  }

  var RICH_TAGS = {
    P: 1,
    BR: 1,
    STRONG: 1,
    EM: 1,
    B: 1,
    I: 1,
    UL: 1,
    OL: 1,
    LI: 1,
    H2: 1,
    H3: 1,
  };

  function sanitizeRichHtml(html) {
    var wrap = document.createElement("div");
    wrap.innerHTML = String(html || "");
    function clean(node) {
      var children = Array.prototype.slice.call(node.childNodes);
      children.forEach(function (child) {
        if (child.nodeType === 3) return;
        if (child.nodeType !== 1) {
          node.removeChild(child);
          return;
        }
        var tag = child.tagName;
        if (tag === "H1") {
          var h2 = document.createElement("h2");
          while (child.firstChild) h2.appendChild(child.firstChild);
          node.replaceChild(h2, child);
          clean(h2);
          return;
        }
        if (!RICH_TAGS[tag]) {
          while (child.firstChild) node.insertBefore(child.firstChild, child);
          node.removeChild(child);
          return;
        }
        while (child.attributes.length) {
          child.removeAttribute(child.attributes[0].name);
        }
        clean(child);
      });
    }
    clean(wrap);
    return wrap;
  }

  function resolveSrc(src, prefix) {
    var s = String(src || "").replace(/\\/g, "/");
    if (!s) return "";
    if (/^https?:\/\//i.test(s) || s.indexOf("//") === 0) return s;
    // Page-local media/ next to the HTML page (preferred for page-owned assets)
    if (s.indexOf("media/") === 0 || s.indexOf("./media/") === 0) {
      s = s.replace(/^\.\//, "");
      try {
        return new URL(s, document.baseURI || window.location.href).href;
      } catch (e) {
        var base = String(window.location.href || "").replace(/[^\/]*$/, "");
        return base + s;
      }
    }
    if (s.charAt(0) === "/") s = s.slice(1);
    // Legacy Images/... and site-root-relative pages/.../media/...
    return prefix + s;
  }

  function appendTextWithBreaks(el, text) {
    var lines = String(text || "").split("\n");
    for (var i = 0; i < lines.length; i++) {
      if (i) el.appendChild(document.createElement("br"));
      if (lines[i]) el.appendChild(document.createTextNode(lines[i]));
    }
  }

  function renderPlainTextBlock(text) {
    var parts = String(text || "")
      .split(/\n\n+/)
      .map(function (s) {
        return s.trim();
      })
      .filter(Boolean);
    if (!parts.length) return null;
    if (parts.length === 1) {
      var one = document.createElement("p");
      one.className = "shop-body__text content-body__text";
      appendTextWithBreaks(one, parts[0]);
      return one;
    }
    var wrap = document.createElement("div");
    wrap.className = "content-body__section";
    parts.forEach(function (part, idx) {
      var shortTitle = part.length < 48 && part.indexOf("\n") === -1;
      if (idx === 0 && shortTitle) {
        var h = document.createElement("h2");
        h.className = "content-body__heading";
        h.textContent = part;
        wrap.appendChild(h);
        return;
      }
      if (idx === 1 && part.length < 90 && part.indexOf("\n") === -1) {
        var mistake = document.createElement("p");
        mistake.className = "tip-mistake";
        mistake.textContent = part;
        wrap.appendChild(mistake);
        return;
      }
      var p = document.createElement("p");
      p.className = "shop-body__text content-body__text";
      appendTextWithBreaks(p, part);
      wrap.appendChild(p);
    });
    return wrap;
  }

  function renderBlock(block, lang, prefix) {
    var type = (block && block.type) || "";
    if (type === "text") {
      var text = textFor(block, lang).trim();
      if (!text) return null;
      if (looksLikeHtml(text)) {
        var rich = document.createElement("div");
        rich.className = "shop-body__text content-body__text content-body__rich";
        var cleaned = sanitizeRichHtml(text);
        while (cleaned.firstChild) rich.appendChild(cleaned.firstChild);
        if (!rich.childNodes.length) return null;
        return rich;
      }
      return renderPlainTextBlock(text);
    }
    if (type === "checklist") {
      var checkWrap = document.createElement("div");
      checkWrap.className = "content-body__section content-body__checklist";
      var checkTitle = textFor(block, lang).trim();
      if (checkTitle) {
        var checkH = document.createElement("h2");
        checkH.className = "content-body__heading";
        checkH.textContent = checkTitle;
        checkWrap.appendChild(checkH);
      }
      var rawItems = Array.isArray(block.items) ? block.items : [];
      var ul = document.createElement("ul");
      ul.className = "prep-check-list";
      for (var ci = 0; ci < rawItems.length; ci++) {
        var itemText = textFor(rawItems[ci], lang).trim();
        if (!itemText) continue;
        var li = document.createElement("li");
        li.textContent = itemText;
        ul.appendChild(li);
      }
      if (!ul.childNodes.length) return checkTitle ? checkWrap : null;
      checkWrap.appendChild(ul);
      return checkWrap;
    }
    if (type === "callout") {
      var call = document.createElement("aside");
      call.className = "guide-callout content-body__callout";
      var label = document.createElement("p");
      label.className = "guide-callout__label content-body__callout-label";
      label.textContent = tipLabel(lang);
      var body = document.createElement("p");
      body.className = "guide-callout__text content-body__callout-text";
      body.textContent = textFor(block, lang).trim();
      if (!body.textContent) return null;
      call.appendChild(label);
      call.appendChild(body);
      return call;
    }
    if (type === "image") {
      var resolved = resolveSrc(block.src, prefix);
      if (!resolved) return null;
      var fig = document.createElement("figure");
      fig.className = "menu-photo shop-body__image content-body__image";
      var img = document.createElement("img");
      img.src = resolved;
      img.alt = "";
      img.loading = "lazy";
      fig.appendChild(img);
      return fig;
    }
    if (type === "youtube") {
      var vid = extractYoutubeId(block.url || "");
      if (!vid) return null;
      var wrap = document.createElement("div");
      wrap.className = "shop-body__youtube content-body__youtube";
      var iframe = document.createElement("iframe");
      iframe.src = "https://www.youtube-nocookie.com/embed/" + vid;
      iframe.title = "YouTube";
      iframe.setAttribute("allowfullscreen", "");
      iframe.setAttribute(
        "allow",
        "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
      );
      iframe.setAttribute("referrerpolicy", "strict-origin-when-cross-origin");
      iframe.loading = "lazy";
      wrap.appendChild(iframe);
      return wrap;
    }
    return null;
  }

  function setFallbackVisible(mount, visible) {
    var sel = mount.getAttribute("data-body-fallback-hide");
    var nodes = [];
    if (sel) {
      var scope = mount.parentElement || document;
      try {
        nodes = Array.prototype.slice.call(scope.querySelectorAll(sel));
      } catch (e) {
        nodes = [];
      }
    }
    // Shop tip fallback
    if (mount.id === "shop-body" || mount.getAttribute("data-shop-slug")) {
      var tips = document.querySelectorAll("[data-shop-tip-fallback]");
      for (var t = 0; t < tips.length; t++) nodes.push(tips[t]);
    }
    // Generic content fallback siblings
    var local = mount.parentElement
      ? mount.parentElement.querySelectorAll("[data-content-body-fallback]")
      : [];
    for (var i = 0; i < local.length; i++) nodes.push(local[i]);

    for (var j = 0; j < nodes.length; j++) {
      var el = nodes[j];
      if (visible) {
        el.hidden = false;
        el.removeAttribute("data-shop-body-hides-tip");
        el.removeAttribute("data-content-body-hides");
      } else {
        el.hidden = true;
        el.setAttribute("data-shop-body-hides-tip", "1");
        el.setAttribute("data-content-body-hides", "1");
      }
    }
  }

  function ensureShopMountAttrs(mount) {
    if (mount.getAttribute("data-body-path")) return;
    var slug = mount.getAttribute("data-shop-slug") || "";
    if (!slug) return;
    mount.setAttribute("data-content-body", "");
    mount.setAttribute("data-body-path", "restaurants." + slug + ".body");
    if (!mount.getAttribute("data-body-show-tip-heading")) {
      mount.setAttribute("data-body-show-tip-heading", "1");
    }
  }

  function collectMounts() {
    var list = [];
    var marked = document.querySelectorAll("[data-content-body]");
    for (var i = 0; i < marked.length; i++) list.push(marked[i]);
    var shop = document.getElementById("shop-body");
    if (shop && list.indexOf(shop) === -1) list.push(shop);
    return list;
  }

  function renderMount(mount, lang) {
    ensureShopMountAttrs(mount);
    var path = mount.getAttribute("data-body-path") || "";
    if (!path) return;
    var body = getBody(path, lang);
    var prefix = assetPrefix();
    mount.innerHTML = "";
    if (!body || !body.length) {
      mount.classList.remove("tip");
      setFallbackVisible(mount, true);
      mount.hidden = true;
      return;
    }

    var nodes = [];
    for (var i = 0; i < body.length; i++) {
      var node = renderBlock(body[i], lang, prefix);
      if (node) nodes.push(node);
    }
    if (!nodes.length) {
      mount.classList.remove("tip");
      setFallbackVisible(mount, true);
      mount.hidden = true;
      return;
    }

    mount.hidden = false;
    setFallbackVisible(mount, false);

    var showTip = mount.getAttribute("data-body-show-tip-heading") === "1";
    if (showTip) {
      mount.classList.add("tip");
      var heading = document.createElement("h3");
      heading.className = "shop-body__heading content-body__heading";
      heading.textContent = tipLabel(lang);
      mount.appendChild(heading);
    } else {
      mount.classList.remove("tip");
    }

    for (var j = 0; j < nodes.length; j++) {
      mount.appendChild(nodes[j]);
    }
  }

  function currentLang() {
    if (window.GuideI18n && typeof window.GuideI18n.getLang === "function") {
      return window.GuideI18n.getLang();
    }
    var el = document.documentElement;
    return (el && el.lang) || "ko";
  }

  function lookupRestaurant(slug, lang) {
    var root = lookupRoot(lang) || lookupRoot("ko");
    if (!root || !root.restaurants) return null;
    return root.restaurants[slug] || null;
  }

  function syncShopPlaceVisual(lang) {
    var details = document.querySelectorAll("[data-shop-detail], [data-shop-place-panel]");
    for (var i = 0; i < details.length; i++) {
      var panel = details[i];
      var slug = panel.getAttribute("data-shop-slug") || "";
      var r = slug ? lookupRestaurant(slug, lang) : null;
      var placeUrl = r && String(r.placeUrl || "").trim();
      var openUrl =
        (r && String(r.placeUrl || r.mapsUrl || "").trim()) || "";
      var embed = r && String(r.mapsEmbedUrl || "").trim();
      var previewImage = r && String(r.previewImage || "").trim();
      var phone = r && String(r.phone || "").trim();
      var hours = r && String(r.hours || "").trim();
      var location = r && String(r.location || "").trim();
      var name = r && String(r.name || "").trim();
      var about = r && String(r.about || "").trim();
      var sourceType = r && String(r.sourceType || "").trim().toLowerCase();
      if (!sourceType) {
        if (placeUrl || embed) sourceType = "google";
        else sourceType = "custom";
      }
      panel.hidden = false;
      panel.setAttribute("data-source", sourceType);

      var nameRow = panel.querySelector('[data-shop-info-row="name"]');
      if (nameRow) {
        nameRow.hidden = !name;
        var nameDd = panel.querySelector("[data-shop-info-name]");
        if (nameDd && name) nameDd.textContent = name;
      }

      var locRow = panel.querySelector('[data-shop-info-row="location"]');
      if (locRow) locRow.hidden = !location;

      var phoneRow = panel.querySelector('[data-shop-info-row="phone"]');
      if (phoneRow) {
        phoneRow.hidden = !phone;
        var phoneDd = phoneRow.querySelector("dd");
        if (phoneDd && phone) phoneDd.textContent = phone;
      }

      var hoursRow = panel.querySelector('[data-shop-info-row="hours"]');
      if (hoursRow) {
        hoursRow.hidden = !hours;
        var hoursDd = hoursRow.querySelector("dd");
        if (hoursDd && hours) hoursDd.textContent = hours;
      }

      var aboutRow = panel.querySelector('[data-shop-info-row="about"]');
      if (aboutRow) {
        aboutRow.hidden = !about;
        var aboutDd =
          panel.querySelector("[data-shop-info-about]") ||
          (aboutRow && aboutRow.querySelector("dd"));
        if (aboutDd && about) aboutDd.textContent = about;
      }

      var placeRow = panel.querySelector('[data-shop-info-row="place"]');
      var placeLink = panel.querySelector("[data-shop-place-link]");
      if (placeRow) placeRow.hidden = !openUrl;
      if (placeLink) {
        if (openUrl) {
          placeLink.setAttribute("href", openUrl);
          placeLink.removeAttribute("aria-disabled");
        } else {
          placeLink.setAttribute("href", "#");
          placeLink.setAttribute("aria-disabled", "true");
        }
      }

      // Legacy card markup (older HTML) — keep minimal wiring
      var card = panel.querySelector("[data-shop-place-card]");
      if (card) {
        if (openUrl) {
          card.setAttribute("href", openUrl);
          card.removeAttribute("aria-disabled");
        } else {
          card.setAttribute("href", "#");
          card.setAttribute("aria-disabled", "true");
        }
      }

      var mapSection = panel.querySelector("[data-shop-map]");
      var iframe = panel.querySelector(
        "iframe.shop-map-embed, iframe.place-map-embed"
      );
      var showMap = !!embed;
      if (mapSection) mapSection.hidden = !showMap;
      if (iframe) {
        if (embed) {
          if (iframe.getAttribute("src") !== embed) {
            iframe.setAttribute("src", embed);
          }
        } else {
          iframe.setAttribute("src", "about:blank");
        }
      }

      var photo =
        panel.querySelector("img.shop-photo[data-shop-photo]") ||
        panel.querySelector("img.shop-photo") ||
        document.querySelector("img.shop-photo[data-shop-photo]") ||
        document.querySelector("img.shop-photo");
      if (photo) {
        photo.hidden = false;
        if (!photo.getAttribute("data-cover-fallback-bound")) {
          photo.setAttribute("data-cover-fallback-bound", "1");
          photo.addEventListener("error", function () {
            var img = previewImage;
            if (!img && r) img = String(r.previewImage || "").trim();
            if (img && photo.getAttribute("src") !== img) {
              photo.setAttribute("src", img);
            }
          });
        }
        // Prefer remote preview when local cover is missing (empty natural size after load)
        if (previewImage && photo.complete && photo.naturalWidth === 0) {
          photo.setAttribute("src", previewImage);
        }
      }

      renderShopMenuBlock(panel, r);
      renderShopPhotosCta(panel, r);
    }

    // Pages without detail markup: leave legacy photo alone
    if (!details.length) {
      var legacy = document.querySelector("img.shop-photo");
      if (legacy) legacy.hidden = false;
    }
  }

  function menuItemName(item, lang) {
    if (!item) return "";
    var name = item.name;
    if (name && typeof name === "object") {
      var localized =
        name[lang] || name.ko || name.en || name.ja || name.zh || "";
      return String(localized || "").trim();
    }
    if (lang === "en" && item.nameEn) return String(item.nameEn).trim();
    if (lang === "ja" && item.nameJa) return String(item.nameJa).trim();
    if (lang === "zh" && item.nameZh) return String(item.nameZh).trim();
    if (item.nameKo) return String(item.nameKo).trim();
    return String(name || "").trim();
  }

  function renderShopMenuBlock(panel, restaurant) {
    var block = panel.querySelector("[data-shop-menu-block]");
    var list = panel.querySelector("[data-shop-menu-list]");
    if (!block || !list) return;
    var items = restaurant && Array.isArray(restaurant.menuItems)
      ? restaurant.menuItems
      : [];
    var lang = currentLang();
    list.innerHTML = "";
    if (!items.length) {
      block.hidden = true;
      return;
    }
    block.hidden = false;
    for (var i = 0; i < items.length; i++) {
      var item = items[i] || {};
      var name = menuItemName(item, lang);
      if (!name) continue;
      var price = String(item.price || "").trim();
      var li = document.createElement("li");
      li.className = "shop-menu-item";
      if (item.recommend) li.className += " shop-menu-item--recommend";

      var meta = document.createElement("div");
      meta.className = "shop-menu-item__meta";
      var nameEl = document.createElement("span");
      nameEl.className = "shop-menu-item__name";
      nameEl.textContent = name;
      meta.appendChild(nameEl);
      if (price) {
        var priceEl = document.createElement("span");
        priceEl.className = "shop-menu-item__price";
        priceEl.textContent = price;
        meta.appendChild(priceEl);
      }
      li.appendChild(meta);
      list.appendChild(li);
    }
    if (!list.children.length) block.hidden = true;
  }

  function tField(key, fallback) {
    var root = lookupRoot(currentLang()) || lookupRoot("ko");
    var fields = root && root.restaurantFields;
    if (fields && fields[key]) return String(fields[key]);
    return fallback;
  }

  function renderShopPhotosCta(panel, restaurant) {
    var block =
      panel.querySelector("[data-shop-photos-cta]") ||
      panel.querySelector("[data-shop-gallery-block]");
    if (!block) return;
    var openUrl = restaurant
      ? String(restaurant.placeUrl || restaurant.mapsUrl || "").trim()
      : "";
    block.innerHTML = "";
    if (!openUrl) {
      block.hidden = true;
      return;
    }
    block.hidden = false;
    block.classList.add("shop-photos-cta");
    var title = document.createElement("h2");
    title.className = "shop-photos-cta__title shop-gallery-block__title";
    title.textContent = tField("photoGallery", "사진·리뷰 더 보기");
    block.appendChild(title);
    var note = document.createElement("p");
    note.className = "shop-photos-cta__note";
    note.textContent = tField(
      "photosOnMapsNote",
      "추가 사진과 리뷰는 지도·플레이스 페이지에서 확인할 수 있습니다."
    );
    block.appendChild(note);
    var link = document.createElement("a");
    link.className = "shop-place-link shop-photos-cta__link";
    link.href = openUrl;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.textContent = tField("viewOnPlaceMaps", "네이버 지도에서 보기");
    block.appendChild(link);
  }

  function render(lang) {
    var mounts = collectMounts();
    for (var i = 0; i < mounts.length; i++) {
      renderMount(mounts[i], lang);
    }
    syncShopPlaceVisual(lang);
  }

  var listening = false;
  function init() {
    render(currentLang());
    if (!listening) {
      listening = true;
      document.addEventListener("guide:langchange", function (e) {
        var lang = (e.detail && e.detail.lang) || currentLang();
        render(lang);
      });
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
  setTimeout(init, 0);

  window.GuideContentBody = {
    render: render,
    init: init,
    getBody: getBody,
  };
})();
