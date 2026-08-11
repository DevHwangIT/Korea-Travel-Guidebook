/**
 * WYSIWYG body editor (shops + guidebook sections).
 * Quill compose → on save HTML↔body blocks (text / image / youtube).
 * Optional data-body-prefix on [data-body-editor] (default "body").
 */
(function () {
  function qs(root, sel) {
    return root.querySelector(sel);
  }
  function qsa(root, sel) {
    return Array.prototype.slice.call(root.querySelectorAll(sel));
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
      if (host === "youtu.be" || host === "www.youtu.be") {
        var id = (a.pathname || "").replace(/^\//, "").split("/")[0];
        return /^[A-Za-z0-9_-]{6,}$/.test(id) ? id : "";
      }
      if (host.indexOf("youtube") === -1) return "";
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

  function youtubeWatchUrl(url) {
    var id = extractYoutubeId(url);
    return id ? "https://www.youtube.com/watch?v=" + id : "";
  }

  function youtubeEmbedUrl(url) {
    var id = extractYoutubeId(url);
    return id ? "https://www.youtube-nocookie.com/embed/" + id : "";
  }

  function escapeHtml(s) {
    return String(s || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function uid() {
    return "p" + Date.now().toString(36) + Math.random().toString(36).slice(2, 7);
  }

  function mediaSrcForEditor(src, editor) {
    var raw = String(src || "").trim();
    if (!raw) return "";
    var pm = /^pending:([A-Za-z0-9_-]+)$/.exec(raw);
    if (pm) {
      return (editor && editor._pendingUrls && editor._pendingUrls[pm[1]]) || "";
    }
    if (/^https?:\/\//i.test(raw) || raw.indexOf("blob:") === 0) return raw;
    if (raw.indexOf("/media/") === 0) return raw;
    return "/media/" + raw.replace(/^\/+/, "");
  }

  function normalizeStoredSrc(src, imgEl) {
    if (imgEl) {
      var pending = imgEl.getAttribute("data-pending");
      if (pending) return "pending:" + pending;
    }
    var raw = String(src || "").trim();
    if (!raw) return "";
    if (/^pending:/.test(raw)) return raw;
    if (raw.indexOf("blob:") === 0) return "";
    if (raw.indexOf("/media/") === 0) raw = raw.slice("/media/".length);
    return raw.replace(/^\/+/, "");
  }

  var TEXT_TAGS = {
    P: 1,
    BR: 1,
    STRONG: 1,
    EM: 1,
    B: 1,
    I: 1,
    U: 1,
    UL: 1,
    OL: 1,
    LI: 1,
    H1: 1,
    H2: 1,
    H3: 1,
    H4: 1,
    BLOCKQUOTE: 1,
    SPAN: 1,
    DIV: 1,
  };

  function sanitizeTextHtml(html) {
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
        if (tag === "IMG" || tag === "IFRAME" || child.getAttribute("data-youtube")) {
          node.removeChild(child);
          return;
        }
        if (!TEXT_TAGS[tag]) {
          while (child.firstChild) node.insertBefore(child.firstChild, child);
          node.removeChild(child);
          return;
        }
        var keepAttrs = [];
        if (tag === "SPAN" || tag === "DIV") {
          // unwrap decorative wrappers from Quill
          while (child.firstChild) node.insertBefore(child.firstChild, child);
          node.removeChild(child);
          return;
        }
        Array.prototype.slice.call(child.attributes).forEach(function (attr) {
          if (keepAttrs.indexOf(attr.name) === -1) {
            child.removeAttribute(attr.name);
          }
        });
        if (tag === "H1") {
          var h2 = document.createElement("h2");
          while (child.firstChild) h2.appendChild(child.firstChild);
          node.replaceChild(h2, child);
          clean(h2);
          return;
        }
        clean(child);
      });
    }
    clean(wrap);
    return wrap.innerHTML.trim();
  }

  function plainTextToHtml(text) {
    var t = String(text || "").replace(/\r\n/g, "\n").trim();
    if (!t) return "";
    if (/<[a-z][\s\S]*>/i.test(t)) return sanitizeTextHtml(t);
    return t
      .split(/\n{2,}/)
      .map(function (para) {
        return "<p>" + escapeHtml(para).replace(/\n/g, "<br>") + "</p>";
      })
      .join("");
  }

  function isMediaOnlyElement(el) {
    if (!el || el.nodeType !== 1) return false;
    var tag = el.tagName;
    if (tag === "IMG" || tag === "IFRAME") return true;
    if (el.getAttribute("data-youtube")) return true;
    if (el.classList && (el.classList.contains("ql-video") || el.classList.contains("ql-youtube")))
      return true;
    if (tag === "P" || tag === "DIV" || tag === "FIGURE") {
      var elems = el.querySelectorAll("img, iframe, [data-youtube], .ql-video");
      if (!elems.length) return false;
      var text = (el.textContent || "").replace(/\u00a0/g, " ").trim();
      return !text;
    }
    return false;
  }

  function extractYoutubeFromEl(el) {
    if (!el) return "";
    var data = el.getAttribute && el.getAttribute("data-youtube");
    if (data) return youtubeWatchUrl(data) || data;
    var iframe =
      el.tagName === "IFRAME" ? el : el.querySelector && el.querySelector("iframe");
    if (iframe) {
      return youtubeWatchUrl(iframe.getAttribute("src") || "") || "";
    }
    var video = el.classList && el.classList.contains("ql-video") ? el : null;
    if (video && video.getAttribute("src")) {
      return youtubeWatchUrl(video.getAttribute("src")) || "";
    }
    return "";
  }

  function extractImageFromEl(el) {
    if (!el) return null;
    var img = el.tagName === "IMG" ? el : el.querySelector && el.querySelector("img");
    if (!img) return null;
    return {
      type: "image",
      alt: img.getAttribute("alt") || "",
      src: normalizeStoredSrc(img.getAttribute("src") || "", img),
      pending: img.getAttribute("data-pending") || null,
      el: img,
    };
  }

  function parseHtmlToSegments(html) {
    var wrap = document.createElement("div");
    wrap.innerHTML = String(html || "");
    var segs = [];
    var textBuf = [];

    function flushText() {
      if (!textBuf.length) return;
      var joined = sanitizeTextHtml(textBuf.join(""));
      textBuf = [];
      var plain = joined.replace(/<[^>]+>/g, "").replace(/&nbsp;/g, " ").trim();
      if (!joined || (!plain && !/<(ul|ol|h2|h3|li)\b/i.test(joined))) return;
      segs.push({ type: "text", html: joined });
    }

    function handleMedia(el) {
      flushText();
      var img = extractImageFromEl(el);
      if (img && (img.src || img.pending)) {
        segs.push({
          type: "image",
          alt: img.alt,
          src: img.src || (img.pending ? "pending:" + img.pending : ""),
        });
        return;
      }
      var yt = extractYoutubeFromEl(el);
      if (yt) {
        segs.push({ type: "youtube", url: yt });
      }
    }

    function walk(nodes) {
      Array.prototype.slice.call(nodes).forEach(function (node) {
        if (node.nodeType === 3) {
          var t = node.textContent.replace(/\u00a0/g, " ");
          if (t.trim()) textBuf.push("<p>" + escapeHtml(t) + "</p>");
          return;
        }
        if (node.nodeType !== 1) return;

        if (isMediaOnlyElement(node)) {
          handleMedia(node);
          return;
        }

        var tag = node.tagName;
        if (
          tag === "P" ||
          tag === "H1" ||
          tag === "H2" ||
          tag === "H3" ||
          tag === "H4" ||
          tag === "UL" ||
          tag === "OL" ||
          tag === "BLOCKQUOTE"
        ) {
          if (node.querySelector("img, iframe, [data-youtube], .ql-video")) {
            Array.prototype.slice.call(node.childNodes).forEach(function (child) {
              if (child.nodeType === 1 && isMediaOnlyElement(child)) {
                handleMedia(child);
              } else if (child.nodeType === 3) {
                var ct = child.textContent.replace(/\u00a0/g, " ");
                if (ct.trim()) textBuf.push("<p>" + escapeHtml(ct) + "</p>");
              } else if (child.nodeType === 1) {
                if (isMediaOnlyElement(child)) handleMedia(child);
                else textBuf.push(child.outerHTML);
              }
            });
          } else {
            textBuf.push(node.outerHTML);
          }
          return;
        }

        if (tag === "DIV" || tag === "FIGURE" || tag === "SPAN") {
          walk(node.childNodes);
          return;
        }

        if (TEXT_TAGS[tag]) {
          textBuf.push(node.outerHTML);
          return;
        }

        walk(node.childNodes);
      });
    }

    walk(wrap.childNodes);
    flushText();
    return segs;
  }

  function blocksToHtml(blocks, lang, editor) {
    return (blocks || [])
      .map(function (b) {
        var t = b.type || "text";
        if (t === "text") {
          return plainTextToHtml(b[lang] || b.ko || b.en || b.ja || "");
        }
        if (t === "image") {
          var src = String(b.src || "").trim();
          var url = mediaSrcForEditor(src, editor);
          if (!url) return "";
          var pendingAttr = /^pending:/.test(src)
            ? ' data-pending="' + escapeHtml(src.slice(8)) + '"'
            : "";
          return (
            "<p><img src=\"" +
            escapeHtml(url) +
            '"' +
            pendingAttr +
            ' alt=""></p>'
          );
        }
        if (t === "youtube") {
          var embed = youtubeEmbedUrl(b.url || "");
          var watch = youtubeWatchUrl(b.url || "") || String(b.url || "").trim();
          if (!embed) return "";
          return (
            '<div class="ql-youtube" data-youtube="' +
            escapeHtml(watch) +
            '" contenteditable="false">' +
            '<iframe src="' +
            escapeHtml(embed) +
            '" frameborder="0" allowfullscreen="true" title="YouTube"></iframe>' +
            "</div>"
          );
        }
        return "";
      })
      .filter(Boolean)
      .join("");
  }

  function htmlLangsToBlocks(htmlKo, htmlEn, htmlJa, pendingFiles) {
    var segKo = parseHtmlToSegments(htmlKo);
    var textEn = parseHtmlToSegments(htmlEn || "")
      .filter(function (s) {
        return s.type === "text";
      })
      .map(function (s) {
        return s.html;
      });
    var textJa = parseHtmlToSegments(htmlJa || "")
      .filter(function (s) {
        return s.type === "text";
      })
      .map(function (s) {
        return s.html;
      });
    var out = [];
    var ti = 0;
    var fileSlots = [];

    segKo.forEach(function (seg) {
      if (seg.type === "text") {
        out.push({
          type: "text",
          ko: seg.html || "",
          en: textEn[ti] || "",
          ja: textJa[ti] || "",
        });
        ti += 1;
      } else if (seg.type === "image") {
        var src = seg.src || "";
        var pm = /^pending:([A-Za-z0-9_-]+)$/.exec(src);
        if (pm) {
          var key = pm[1];
          var file = pendingFiles && pendingFiles[key];
          out.push({ type: "image", src: "" });
          fileSlots.push({ index: out.length - 1, file: file || null, key: key });
        } else {
          out.push({ type: "image", src: src.replace(/^\/+/, "") });
          fileSlots.push({ index: out.length - 1, file: null, key: null });
        }
      } else if (seg.type === "youtube") {
        out.push({ type: "youtube", url: seg.url || "" });
      }
    });

    return { blocks: out, fileSlots: fileSlots };
  }

  function isKoOnly(editor) {
    return editor.getAttribute("data-body-ko-only") === "1";
  }

  function editorLangs(editor) {
    return isKoOnly(editor) ? ["ko"] : ["ko", "en", "ja"];
  }

  function bindLangTabs(root) {
    qsa(root, "[data-lang-tabs]").forEach(function (tabsRoot) {
      if (tabsRoot._boundLangTabs) return;
      tabsRoot._boundLangTabs = true;
      var tabs = qsa(tabsRoot, ".lang-tab");
      var panels = qsa(tabsRoot, ".lang-panel");
      tabs.forEach(function (tab) {
        tab.addEventListener("click", function () {
          var lang = tab.getAttribute("data-lang");
          tabs.forEach(function (t) {
            t.classList.toggle("is-active", t === tab);
          });
          panels.forEach(function (p) {
            p.classList.toggle("is-active", p.getAttribute("data-panel") === lang);
          });
        });
      });
    });
  }

  function fieldPrefix(editor) {
    return (editor.getAttribute("data-body-prefix") || "body").trim() || "body";
  }

  function getQuill(editor, lang) {
    return editor._quills && editor._quills[lang];
  }

  function activeLang(editor) {
    if (isKoOnly(editor)) return "ko";
    var tab = qs(editor, ".lang-tab.is-active");
    return (tab && tab.getAttribute("data-lang")) || "ko";
  }

  function insertEmbedAll(editor, kind, value, pendingKey) {
    editorLangs(editor).forEach(function (lang) {
      var q = getQuill(editor, lang);
      if (!q) return;
      var range = q.getSelection(true);
      var index =
        range && typeof range.index === "number" ? range.index : q.getLength();
      if (kind === "image") {
        q.insertEmbed(index, "image", value, "user");
        q.setSelection(index + 1, 0, "silent");
        if (pendingKey) {
          qsa(q.root, "img").forEach(function (img) {
            if (img.src === value || img.getAttribute("src") === value) {
              img.setAttribute("data-pending", pendingKey);
            }
          });
        }
      } else if (kind === "youtube") {
        q.insertEmbed(index, "youtube", value, "user");
        q.setSelection(index + 1, 0, "silent");
      }
    });
  }

  function prepareSubmit(editor) {
    var prefix = fieldPrefix(editor);
    var htmlKo = "";
    var htmlEn = "";
    var htmlJa = "";
    editorLangs(editor).forEach(function (lang) {
      var q = getQuill(editor, lang);
      var html = q ? q.root.innerHTML : "";
      // Re-attach pending attrs from our map if Quill stripped them
      if (q && editor._pendingFiles) {
        Object.keys(editor._pendingFiles).forEach(function (key) {
          var url = editor._pendingUrls && editor._pendingUrls[key];
          if (!url) return;
          qsa(q.root, "img").forEach(function (img) {
            if (img.src === url || img.getAttribute("src") === url) {
              img.setAttribute("data-pending", key);
            }
          });
        });
        html = q.root.innerHTML;
      }
      if (lang === "ko") htmlKo = html;
      if (lang === "en") htmlEn = html;
      if (lang === "ja") htmlJa = html;
    });

    // KO-only: leave en/ja empty — server auto-translates on save.
    var parsed = htmlLangsToBlocks(
      htmlKo,
      htmlEn,
      htmlJa,
      editor._pendingFiles || {}
    );
    var jsonInput = qs(editor, "[data-body-json]");
    if (jsonInput) jsonInput.value = JSON.stringify(parsed.blocks);
    var countInput = qs(editor, "[data-body-count]");
    if (countInput) countInput.value = String(parsed.blocks.length);

    var fileHost = qs(editor, "[data-body-file-host]");
    if (fileHost) {
      fileHost.innerHTML = "";
      parsed.fileSlots.forEach(function (slot) {
        if (!slot.file) return;
        var input = document.createElement("input");
        input.type = "file";
        input.name = prefix + "_" + slot.index + "_file";
        input.setAttribute("data-body-file", "");
        try {
          var dt = new DataTransfer();
          dt.items.add(slot.file);
          input.files = dt.files;
        } catch (e) {
          console.error("본문 이미지 첨부 실패", e);
          window.alert(
            "본문 사진을 폼에 실지 못했습니다. 다른 브라우저에서 다시 시도하거나, 상호 사진 업로드를 이용해 주세요."
          );
        }
        input.hidden = true;
        fileHost.appendChild(input);
      });
    }
  }

  function toolbarHtml(lang) {
    return (
      '<div class="body-quill-toolbar" data-body-toolbar="' +
      lang +
      '">' +
      '<span class="ql-formats">' +
      '<select class="ql-header" title="제목/본문">' +
      '<option value="2">제목</option>' +
      '<option value="3">소제목</option>' +
      '<option selected value="">본문</option>' +
      "</select>" +
      '<button type="button" class="ql-bold" title="굵게"></button>' +
      '<button type="button" class="ql-list" value="ordered" title="번호 목록"></button>' +
      '<button type="button" class="ql-list" value="bullet" title="글머리 목록"></button>' +
      "</span>" +
      '<span class="ql-formats">' +
      '<button type="button" class="body-quill-btn" data-body-insert-image title="사진 넣기">사진</button>' +
      '<button type="button" class="body-quill-btn" data-body-insert-youtube title="유튜브">유튜브</button>' +
      '<button type="button" class="body-quill-btn" data-body-undo title="실행취소">실행취소</button>' +
      "</span>" +
      "</div>"
    );
  }

  function ensureQuillMounts(editor) {
    editorLangs(editor).forEach(function (lang) {
      var panel = qs(editor, '.lang-panel[data-panel="' + lang + '"]');
      var shell =
        (panel && (qs(panel, "[data-body-quill-shell]") || panel)) ||
        qs(editor, '[data-body-quill-shell="' + lang + '"]') ||
        qs(editor, "[data-body-quill-shell]");
      if (!shell) return;
      if (qs(shell, '[data-body-quill="' + lang + '"]') || qs(editor, '[data-body-quill="' + lang + '"]'))
        return;
      shell.innerHTML =
        toolbarHtml(lang) +
        '<div class="body-quill-editor" data-body-quill="' +
        lang +
        '"></div>';
      if (!shell.classList.contains("body-quill-shell")) {
        shell.classList.add("body-quill-shell");
      }
    });
  }

  function loadSeed(editor) {
    var seedEl = qs(editor, "[data-body-seed]");
    var blocks = [];
    if (seedEl) {
      try {
        blocks = JSON.parse(seedEl.textContent || "[]");
        if (!Array.isArray(blocks)) blocks = [];
      } catch (e) {
        blocks = [];
      }
    }
    editor._seedBlocks = blocks;
  }

  function registerYoutubeBlot() {
    if (typeof Quill === "undefined" || Quill.__guideYoutube) return;
    var BlockEmbed = Quill.import("blots/block/embed");
    class YoutubeBlot extends BlockEmbed {
      static create(value) {
        var node = super.create();
        var watch = youtubeWatchUrl(value) || String(value || "").trim();
        var embed = youtubeEmbedUrl(watch);
        node.setAttribute("data-youtube", watch);
        node.setAttribute("contenteditable", "false");
        if (embed) {
          var iframe = document.createElement("iframe");
          iframe.setAttribute("src", embed);
          iframe.setAttribute("frameborder", "0");
          iframe.setAttribute("allowfullscreen", "true");
          iframe.setAttribute("title", "YouTube");
          node.appendChild(iframe);
        }
        return node;
      }
      static value(node) {
        return node.getAttribute("data-youtube") || "";
      }
    }
    YoutubeBlot.blotName = "youtube";
    YoutubeBlot.className = "ql-youtube";
    YoutubeBlot.tagName = "DIV";
    Quill.register(YoutubeBlot);
    Quill.__guideYoutube = true;
  }

  function initQuills(editor) {
    if (typeof Quill === "undefined") {
      console.error("Quill failed to load — body editor unavailable");
      return;
    }
    registerYoutubeBlot();
    editor._quills = {};
    editorLangs(editor).forEach(function (lang) {
      var mount = qs(editor, '[data-body-quill="' + lang + '"]');
      var toolbar = qs(editor, '[data-body-toolbar="' + lang + '"]');
      if (!mount || !toolbar) return;
      var quill = new Quill(mount, {
        theme: "snow",
        modules: {
          toolbar: {
            container: toolbar,
          },
          history: { delay: 400, maxStack: 100, userOnly: true },
        },
        placeholder: "한국어로 편하게 작성하세요…",
      });
      loadBlocksIntoQuill(quill, editor._seedBlocks || [], lang, editor);
      editor._quills[lang] = quill;
    });
  }

  function loadBlocksIntoQuill(quill, blocks, lang, editor) {
    quill.setText("");
    var index = 0;
    (blocks || []).forEach(function (b) {
      var t = b.type || "text";
      if (t === "text") {
        var html = plainTextToHtml(b[lang] || b.ko || b.en || b.ja || "");
        if (!html) return;
        quill.clipboard.dangerouslyPasteHTML(index, html);
        index = quill.getLength();
        return;
      }
      if (t === "image") {
        var url = mediaSrcForEditor(b.src || "", editor);
        if (!url) return;
        // avoid trailing empty line eating the embed index
        if (index > 0) {
          quill.insertText(index, "\n", "silent");
          index += 1;
        }
        quill.insertEmbed(index, "image", url, "silent");
        index += 1;
        return;
      }
      if (t === "youtube") {
        var watch = youtubeWatchUrl(b.url || "") || String(b.url || "").trim();
        if (!watch || !extractYoutubeId(watch)) return;
        if (index > 0) {
          quill.insertText(index, "\n", "silent");
          index += 1;
        }
        quill.insertEmbed(index, "youtube", watch, "silent");
        index += 1;
      }
    });
    // Drop a trailing lone newline Quill leaves
    var len = quill.getLength();
    if (len > 1) {
      try {
        quill.setSelection(0, 0, "silent");
      } catch (e) {}
    }
  }

  function initEditor(editor) {
    if (editor._bodyEditorReady) return;
    editor._bodyEditorReady = true;
    editor._pendingFiles = {};
    editor._pendingUrls = {};

    var form = editor.closest("form");
    var filePicker = qs(editor, "[data-body-pick-image]");

    loadSeed(editor);
    ensureQuillMounts(editor);
    if (!isKoOnly(editor)) bindLangTabs(editor);
    initQuills(editor);

    editor.addEventListener("click", function (e) {
      var insertImg = e.target.closest("[data-body-insert-image]");
      if (insertImg && editor.contains(insertImg)) {
        e.preventDefault();
        if (filePicker) filePicker.click();
        return;
      }

      var insertYt = e.target.closest("[data-body-insert-youtube]");
      if (insertYt && editor.contains(insertYt)) {
        e.preventDefault();
        var url = window.prompt(
          "유튜브 주소를 붙여넣으세요",
          "https://www.youtube.com/watch?v="
        );
        if (!url) return;
        var watch = youtubeWatchUrl(url);
        if (!watch) {
          window.alert("올바른 유튜브 주소가 아닙니다.");
          return;
        }
        insertEmbedAll(editor, "youtube", watch);
        return;
      }

      var undoBtn = e.target.closest("[data-body-undo]");
      if (undoBtn && editor.contains(undoBtn)) {
        e.preventDefault();
        var lang = undoBtn.closest("[data-body-toolbar]");
        var L = (lang && lang.getAttribute("data-body-toolbar")) || activeLang(editor);
        var q = getQuill(editor, L);
        if (q && q.history) q.history.undo();
      }
    });

    if (filePicker) {
      filePicker.addEventListener("change", function () {
        var file = filePicker.files && filePicker.files[0];
        if (!file) return;
        var key = uid();
        editor._pendingFiles[key] = file;
        var objUrl = URL.createObjectURL(file);
        editor._pendingUrls[key] = objUrl;
        insertEmbedAll(editor, "image", objUrl, key);
        filePicker.value = "";
      });
    }

    if (form) {
      form.addEventListener("submit", function () {
        prepareSubmit(editor);
      });
    }
  }

  function boot() {
    qsa(document, "[data-body-editor]").forEach(initEditor);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }

  window.GuideBodyEditor = {
    htmlLangsToBlocks: htmlLangsToBlocks,
    blocksToHtml: blocksToHtml,
    parseHtmlToSegments: parseHtmlToSegments,
  };
})();
