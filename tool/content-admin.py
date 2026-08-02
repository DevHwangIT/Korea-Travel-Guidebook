# -*- coding: utf-8 -*-
"""Local comprehensive content admin for Korea Travel Guidebook (stdlib only).

Usage:
  python tool/content-admin.py
  double-click tool/content-admin.bat

Opens http://127.0.0.1:8765
"""
from __future__ import annotations

import html
import sys
import traceback
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, urlencode, urlparse

TOOL_DIR = Path(__file__).resolve().parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from lib import content, sections  # noqa: E402
from lib.cache_bust import read_version  # noqa: E402
from lib.images import (  # noqa: E402
    MAX_UPLOAD_BYTES,
    append_menu_uploads,
    delete_menu_image_at,
    dish_image_targets,
    renumber_menu_images,
    safe_media_path,
    save_uploads_for_targets,
    shop_image_targets,
)
from lib.multipart import parse_request_body, read_http_body  # noqa: E402
from lib.paths import ROOT  # noqa: E402
from lib.scaffold import (  # noqa: E402
    patch_all_shop_menu_galleries,
    sync_shop_page_menu_gallery,
)

HOST = "127.0.0.1"
PORT = 8765
MAX_BODY_BYTES = MAX_UPLOAD_BYTES * 12 + 512 * 1024


def h(text: object) -> str:
    return html.escape("" if text is None else str(text), quote=True)


def uq(text: object) -> str:
    """Percent-encode for query values (UTF-8). Safe for HTTP Location (latin-1)."""
    return quote("" if text is None else str(text), safe="", encoding="utf-8")


def build_location(path: str, **params: object) -> str:
    """Build an ASCII-safe redirect Location with UTF-8-quoted query values."""
    base = path.split("?", 1)[0]
    items: list[tuple[str, str]] = []
    if "?" in path:
        existing = parse_qs(path.split("?", 1)[1], keep_blank_values=True)
        for key, values in existing.items():
            for val in values:
                items.append((key, val))
    for key, val in params.items():
        if val is None or val is False:
            continue
        if val is True:
            items.append((key, "1"))
            continue
        s = str(val)
        if s == "":
            continue
        items.append((key, s))
    if not items:
        return base
    return base + "?" + urlencode(items, encoding="utf-8", quote_via=quote)


# (href, label, icon, match_prefix) — match_prefix used for active nav
NAV_GROUPS: list[tuple[str, list[tuple[str, str, str, str]]]] = [
    (
        "콘텐츠",
        [
            ("/", "대시보드", "·", "/"),
            ("/dishes?kind=meals", "식사", "식", "/dishes?kind=meals"),
            ("/dishes?kind=desserts", "디저트", "디", "/dishes?kind=desserts"),
            ("/shops", "가게", "가", "/shop"),
            ("/section?id=convenience", "편의점", "편", "/section?id=convenience"),
            ("/section?id=tips", "팁", "팁", "/section?id=tips"),
            ("/section?id=beforeTrip", "여행 전", "전", "/section?id=beforeTrip"),
            ("/section?id=souvenir", "기념품", "기", "/section?id=souvenir"),
            ("/section?id=shopping", "쇼핑", "쇼", "/section?id=shopping"),
            ("/section?id=apps", "앱", "앱", "/section?id=apps"),
            ("/section?id=emergency", "긴급", "긴", "/section?id=emergency"),
            ("/section?id=contact", "문의", "문", "/section?id=contact"),
            ("/phrases", "한국어", "한", "/phrase"),
        ],
    ),
    (
        "설정 / 도구",
        [
            ("/version", "버전", "버", "/version"),
            ("/tools/patch-menus", "메뉴 패치", "패", "/tools/patch-menus"),
        ],
    ),
]

STATIC_DIR = TOOL_DIR / "static"


def _nav_is_active(nav_active: str, match: str, href: str) -> bool:
    if not nav_active:
        return False
    if href == "/" or match == "/":
        return nav_active == "/"
    if nav_active == href or nav_active.startswith(match):
        return True
    # shops list vs shop edit
    if match == "/shop" and (nav_active.startswith("/shops") or nav_active.startswith("/shop")):
        return True
    if match == "/phrase" and (
        nav_active.startswith("/phrases") or nav_active.startswith("/phrase")
    ):
        return True
    return False


def render_crumbs(crumbs: list[tuple[str, str]] | None) -> str:
    if not crumbs:
        return '<nav class="crumbs" aria-label="경로"><span class="current">콘텐츠 관리</span></nav>'
    parts: list[str] = []
    for i, (href, label) in enumerate(crumbs):
        if i:
            parts.append('<span class="sep" aria-hidden="true">/</span>')
        is_last = i == len(crumbs) - 1
        if is_last or not href:
            parts.append(f'<span class="current">{h(label)}</span>')
        else:
            parts.append(f'<a href="{h(href)}">{h(label)}</a>')
    return f'<nav class="crumbs" aria-label="경로">{"".join(parts)}</nav>'


def render_toast(flash: str, *, error: bool = False) -> str:
    if not flash:
        return ""
    cls = "toast error" if error else "toast"
    return (
        f'<div class="toast-stack" id="toast-stack">'
        f'<div class="{cls}" role="status">'
        f'<button type="button" class="toast-close" aria-label="닫기" '
        f"onclick=\"this.closest('.toast-stack')?.remove()\">×</button>"
        f"{h(flash)}</div></div>"
    )


def layout(
    title: str,
    body: str,
    *,
    flash: str = "",
    flash_error: bool = False,
    nav_active: str = "/",
    crumbs: list[tuple[str, str]] | None = None,
) -> str:
    nav_chunks: list[str] = []
    for group_label, items in NAV_GROUPS:
        links = []
        for href, label, icon, match in items:
            active = " is-active" if _nav_is_active(nav_active, match, href) else ""
            links.append(
                f'<a class="nav-link{active}" href="{h(href)}">'
                f'<span class="nav-ico" aria-hidden="true">{h(icon)}</span>'
                f"<span>{h(label)}</span></a>"
            )
        nav_chunks.append(
            f'<div class="nav-group">'
            f'<div class="nav-group-label">{h(group_label)}</div>'
            f'{"".join(links)}</div>'
        )
    toast = render_toast(flash, error=flash_error)
    crumbs_html = render_crumbs(crumbs)
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{h(title)} · 콘텐츠 관리</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/static/admin.css">
</head>
<body>
  {toast}
  <div class="app">
    <aside class="sidebar" aria-label="주요 메뉴">
      <div class="brand">
        <div class="brand-mark" aria-hidden="true">KR</div>
        <div class="brand-text">
          <strong>가이드북 관리</strong>
          <span>로컬 콘텐츠 어드민</span>
        </div>
      </div>
      {"".join(nav_chunks)}
      <div class="sidebar-foot">로컬 전용 · 저장 즉시 파일에 반영됩니다</div>
    </aside>
    <div class="main-wrap">
      <div class="topbar">
        {crumbs_html}
        <div class="topbar-hint">무엇을 수정할까요?</div>
      </div>
      <main class="content">
        {body}
      </main>
    </div>
  </div>
  <script>
  (function () {{
    document.querySelectorAll("[data-lang-tabs]").forEach(function (root) {{
      var tabs = root.querySelectorAll(".lang-tab");
      var panels = root.querySelectorAll(".lang-panel");
      tabs.forEach(function (tab) {{
        tab.addEventListener("click", function () {{
          var lang = tab.getAttribute("data-lang");
          tabs.forEach(function (t) {{ t.classList.toggle("is-active", t === tab); }});
          panels.forEach(function (p) {{
            p.classList.toggle("is-active", p.getAttribute("data-panel") === lang);
          }});
        }});
      }});
    }});
    var stack = document.getElementById("toast-stack");
    if (stack) {{
      setTimeout(function () {{ stack.remove(); }}, 7000);
    }}
  }})();
  </script>
</body>
</html>
"""


def media_url(rel_path: str) -> str:
    return "/media/" + rel_path.lstrip("/")


LANG_TAB_LABELS = {"ko": "KO", "en": "EN", "ja": "JA"}
LANG_FULL_LABELS = {"ko": "한국어", "en": "English", "ja": "日本語"}


def dish_texts_from_form(form: dict[str, str]) -> dict[str, dict[str, str]]:
    texts: dict[str, dict[str, str]] = {}
    for lang in ("ko", "en", "ja"):
        texts[lang] = {
            "title": form.get(f"title_{lang}", "").strip(),
            "desc": form.get(f"desc_{lang}", "").strip(),
            "about": form.get(f"about_{lang}", "").strip(),
        }
    return texts


def shop_texts_from_form(form: dict[str, str]) -> dict[str, dict[str, str]]:
    texts: dict[str, dict[str, str]] = {}
    for lang in ("ko", "en", "ja"):
        texts[lang] = {
            "name": form.get(f"name_{lang}", "").strip(),
            "location": form.get(f"location_{lang}", "").strip(),
            "menu": form.get(f"menu_{lang}", "").strip(),
            "price": form.get(f"price_{lang}", "").strip(),
            "tip": form.get(f"tip_{lang}", "").strip(),
            "about": form.get(f"about_{lang}", "").strip(),
        }
    return texts


def _lang_tabs_shell(panels: dict[str, str], hint: str) -> str:
    tab_btns = []
    panel_html = []
    for lang in ("ko", "en", "ja"):
        active = " is-active" if lang == "ko" else ""
        tab_btns.append(
            f'<button type="button" class="lang-tab{active}" data-lang="{lang}">'
            f"{LANG_TAB_LABELS[lang]} · {LANG_FULL_LABELS[lang]}</button>"
        )
        panel_html.append(
            f'<div class="lang-panel{active}" data-panel="{lang}">{panels[lang]}</div>'
        )
    return (
        '<div class="lang-section">'
        "<h2>번역</h2>"
        f'<p class="muted">{h(hint)}</p>'
        '<div class="lang-tabs" data-lang-tabs>'
        f'<div class="lang-tablist" role="tablist">{"".join(tab_btns)}</div>'
        f'{"".join(panel_html)}</div></div>'
    )


def render_dish_lang_fields(texts: dict[str, dict[str, str]] | None = None) -> str:
    texts = texts or {lang: {"title": "", "desc": "", "about": ""} for lang in ("ko", "en", "ja")}
    panels: dict[str, str] = {}
    for lang in ("ko", "en", "ja"):
        t = texts.get(lang) or {}
        req = " required" if lang == "ko" else ""
        panels[lang] = (
            f'<div class="field"><label>이름 <span class="hint">title</span></label>'
            f'<input type="text" name="title_{lang}" value="{h(t.get("title", ""))}"{req}></div>'
            f'<div class="field"><label>짧은 설명 <span class="hint">desc</span></label>'
            f'<input type="text" name="desc_{lang}" value="{h(t.get("desc", ""))}"></div>'
            f'<div class="field"><label>소개 <span class="hint">about</span></label>'
            f'<textarea name="about_{lang}">{h(t.get("about", ""))}</textarea></div>'
        )
    return _lang_tabs_shell(
        panels,
        "한국어는 필수입니다. EN·JA를 비우면 저장 시 한국어와 같게 채웁니다.",
    )


def render_shop_lang_fields(texts: dict[str, dict[str, str]] | None = None) -> str:
    texts = texts or {
        lang: {
            "name": "",
            "location": "",
            "menu": "",
            "price": "",
            "tip": "",
            "about": "",
        }
        for lang in ("ko", "en", "ja")
    }
    panels: dict[str, str] = {}
    for lang in ("ko", "en", "ja"):
        t = texts.get(lang) or {}
        req = " required" if lang == "ko" else ""
        panels[lang] = (
            f'<div class="field"><label>가게명 <span class="hint">name</span></label>'
            f'<input type="text" name="name_{lang}" value="{h(t.get("name", ""))}"{req}></div>'
            f'<div class="field"><label>위치 <span class="hint">location</span></label>'
            f'<input type="text" name="location_{lang}" value="{h(t.get("location", ""))}"></div>'
            f'<div class="field"><label>대표 메뉴 <span class="hint">menu</span></label>'
            f'<input type="text" name="menu_{lang}" value="{h(t.get("menu", ""))}"></div>'
            f'<div class="field"><label>가격 <span class="hint">price</span></label>'
            f'<input type="text" name="price_{lang}" value="{h(t.get("price", ""))}"></div>'
            f'<div class="field"><label>팁 <span class="hint">tip</span></label>'
            f'<textarea name="tip_{lang}">{h(t.get("tip", ""))}</textarea></div>'
            f'<div class="field"><label>소개 <span class="hint">about</span></label>'
            f'<textarea name="about_{lang}">{h(t.get("about", ""))}</textarea></div>'
        )
    return _lang_tabs_shell(
        panels,
        "한국어 가게명은 필수입니다. EN·JA를 비우면 저장 시 한국어와 같게 채웁니다. "
        "지도 링크(mapsUrl)는 한국어 location으로 생성합니다.",
    )


def render_child_shops_readonly(kind: str, dish_slug: str) -> str:
    children = content.list_child_shops(kind, dish_slug)
    if not children:
        return (
            '<fieldset class="fieldset"><legend>이 음식 하위 가게</legend>'
            '<div class="empty-state">'
            "<strong>아직 연결된 가게가 없어요</strong>"
            '<span class="muted"><a href="/shop/new">가게 추가</a>에서 부모 음식을 지정해 등록하세요.</span>'
            "</div></fieldset>"
        )
    rows = []
    for slug, name in children:
        rows.append(
            f'<li><a href="/shop/edit?slug={h(slug)}"><strong>{h(name)}</strong></a> '
            f"<code>{h(slug)}</code></li>"
        )
    return (
        '<fieldset class="fieldset"><legend>이 음식 하위 가게</legend>'
        '<p class="muted" style="margin:0 0 .35rem">표시만 됩니다. 소속 변경·등록은 가게 수정/추가에서 합니다.</p>'
        f'<div class="child-shops" style="box-shadow:none;margin:0"><ul>{"".join(rows)}</ul></div>'
        "</fieldset>"
    )


def render_upload_zone(
    *,
    name: str,
    label: str,
    hint: str = "",
    preview_html: str = "",
    multiple: bool = False,
    form_id: str = "",
    has_file: bool = False,
) -> str:
    multi = " multiple" if multiple else ""
    form_attr = f' form="{h(form_id)}"' if form_id else ""
    zone_cls = "upload-zone has-preview" if has_file else "upload-zone"
    body_preview = preview_html or '<span class="missing">아직 파일 없음</span>'
    cta = "다른 이미지로 바꾸려면 클릭" if has_file else "클릭하여 이미지 선택"
    return (
        f'<label class="{zone_cls}">'
        f'<input class="upload-zone__input" type="file" name="{h(name)}"{multi}{form_attr} '
        f'accept=".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp">'
        f'<span class="upload-zone__body">'
        f"<strong style=\"font-size:.92rem\">{h(label)}</strong>"
        f"{body_preview}"
        f'<span class="upload-zone__cta">{h(cta)}</span>'
        f'<span class="upload-zone__hint">{h(hint)}</span>'
        f"</span></label>"
    )


def render_image_fields(targets) -> str:
    blocks = []
    for t in targets:
        exists = t.path.is_file()
        if exists:
            preview = (
                f'<img class="thumb" src="{h(media_url(t.rel))}?t={int(t.path.stat().st_mtime)}" '
                f'alt="{h(t.label)}">'
            )
            hint = f"저장 경로: {t.rel} · 현재 파일 있음"
        else:
            preview = '<span class="missing">업로드하면 이 경로에 저장됩니다</span>'
            hint = f"저장 경로: {t.rel}"
        blocks.append(
            render_upload_zone(
                name=t.key,
                label=t.label,
                hint=hint,
                preview_html=preview,
                has_file=exists,
            )
        )
    return (
        '<p class="muted" style="margin:.25rem 0 .5rem">'
        "JPG / PNG / WebP · 최대 8MB · 파일명은 슬러그 기준으로 저장됩니다.</p>"
        + "".join(blocks)
    )


def render_menu_images_manager(shop: dict) -> str:
    """List / delete / reorder / multi-upload for shop menu photos."""
    slug = shop["slug"]
    kind = shop.get("kind") or ""
    dish = shop.get("dish_slug") or ""
    if not kind or not dish:
        return (
            '<fieldset class="fieldset"><legend>메뉴 / 대표 사진</legend>'
            '<p class="muted" style="margin:0">부모 음식을 저장한 뒤 메뉴 이미지를 관리할 수 있습니다.</p>'
            "</fieldset>"
        )
    menus = shop.get("menu_images") or []
    items = []
    for m in menus:
        preview = (
            f'<img src="{h(media_url(m["rel"]))}?t=1" alt="menu-{m["index"]}">'
            if m.get("exists")
            else '<span class="missing">없음</span>'
        )
        legacy = " · 레거시" if m.get("legacy") else ""
        items.append(
            f'<div class="menu-item">'
            f"{preview}"
            f'<div class="meta"><strong>menu-{h(m["index"])}</strong>{legacy}<br>'
            f'<code>{h(m["rel"])}</code></div>'
            f'<form method="post" action="/shop/menu/delete" style="margin:0">'
            f'<input type="hidden" name="slug" value="{h(slug)}">'
            f'<input type="hidden" name="index" value="{h(m["index"])}">'
            f'<button type="submit" class="danger ghost">삭제</button></form>'
            f"</div>"
        )
    order_inputs = ""
    if menus:
        order_inputs = (
            '<div class="field"><label>순서 바꾸기</label>'
            f'<input type="text" name="order" value="{h(",".join(str(m["index"]) for m in menus))}" '
            'placeholder="2,1,3">'
            '<span class="hint">쉼표로 현재 번호를 원하는 순서로 입력 (예: 2,1,3)</span></div>'
            '<div class="row" style="margin-top:.65rem">'
            '<button type="submit" class="secondary">순서 적용</button></div>'
        )
    list_html = (
        "".join(items)
        if items
        else '<div class="empty-state"><strong>아직 메뉴 이미지가 없어요</strong>'
        '<span class="muted">아래에서 여러 장을 한 번에 추가할 수 있습니다.</span></div>'
    )
    upload = render_upload_zone(
        name="menu_images",
        label="메뉴 이미지 추가",
        hint="여러 장 선택 가능 · 저장 시 이어지는 번호로 추가 (가게 저장과 함께 전송)",
        multiple=True,
        form_id="shop-main-form",
        preview_html='<span class="missing">파일을 끌어다 놓거나 클릭하세요</span>',
    )
    return f"""
    <fieldset class="fieldset">
      <legend>메뉴 / 대표 사진 (여러 장)</legend>
      <p class="muted" style="margin:0 0 .65rem">파일명: <code>{{슬러그}}-menu-1.jpg</code>, <code>-menu-2.jpg</code> …
      · 예전 <code>{{슬러그}}-menu.jpg</code>는 menu-1로 취급됩니다.</p>
      <div class="menu-list">{list_html}</div>
      <form class="card" method="post" action="/shop/menu/reorder" style="box-shadow:none;margin:.5rem 0">
        <input type="hidden" name="slug" value="{h(slug)}">
        {order_inputs or '<p class="muted" style="margin:0">이미지가 있으면 순서를 바꿀 수 있습니다.</p>'}
      </form>
      {upload}
    </fieldset>
    """


class AdminHandler(BaseHTTPRequestHandler):
    server_version = "GuidebookContentAdmin/2.0"

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _send(self, code: int, body: str, content_type: str = "text/html; charset=utf-8") -> None:
        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _redirect(
        self,
        location: str,
        *,
        flash: str = "",
        flash_error: bool = False,
        **extra_query: object,
    ) -> None:
        """303 redirect. Query values (incl. Korean flash) are UTF-8 percent-encoded."""
        params = dict(extra_query)
        if flash:
            params["flash"] = flash
        if flash_error:
            params["flash_error"] = "1"
        location = build_location(location, **params)
        # Location header must be latin-1; percent-encoding keeps it ASCII-safe.
        location.encode("latin-1")
        self.send_response(303)
        self.send_header("Location", location)
        self.end_headers()

    def _pop_flash(self) -> str:
        """Prefer ?flash= from request (parse_qs already unquotes UTF-8)."""
        flash = getattr(self, "_qs_flash", "") or ""
        self._flash_is_error = bool(getattr(self, "_qs_flash_error", False))
        self._qs_flash = ""
        self._qs_flash_error = False
        if not flash:
            flash = getattr(self.server, "flash", "") or ""
            self._flash_is_error = False
        self.server.flash = ""  # type: ignore[attr-defined]
        return flash

    def _flash_error(self) -> bool:
        return bool(getattr(self, "_flash_is_error", False))

    def do_GET(self) -> None:  # noqa: N802
        try:
            parsed = urlparse(self.path)
            path = parsed.path
            qs = parse_qs(parsed.query)
            # parse_qs percent-decodes UTF-8 (unquote) for flash / other params
            self._qs_flash = (qs.get("flash") or [""])[0]
            self._qs_flash_error = (qs.get("flash_error") or [""])[0] in (
                "1",
                "true",
                "yes",
            )

            if path == "/":
                self._send(200, self.page_home())
            elif path == "/static/admin.css":
                self._serve_static("admin.css", "text/css; charset=utf-8")
            elif path == "/dishes":
                kind = (qs.get("kind") or ["meals"])[0]
                self._send(200, self.page_dishes(kind))
            elif path == "/dish/edit":
                kind = (qs.get("kind") or ["meals"])[0]
                slug = (qs.get("slug") or [""])[0]
                self._send(200, self.page_dish_edit(kind, slug))
            elif path == "/dish/new":
                kind = (qs.get("kind") or ["meals"])[0]
                self._send(200, self.page_dish_new(kind))
            elif path == "/dish/delete":
                kind = (qs.get("kind") or ["meals"])[0]
                slug = (qs.get("slug") or [""])[0]
                self._send(200, self.page_dish_delete(kind, slug))
            elif path == "/shops":
                self._send(200, self.page_shops())
            elif path == "/shop/edit":
                slug = (qs.get("slug") or [""])[0]
                self._send(200, self.page_shop_edit(slug))
            elif path == "/shop/new":
                self._send(200, self.page_shop_new())
            elif path == "/shop/delete":
                slug = (qs.get("slug") or [""])[0]
                self._send(200, self.page_shop_delete(slug))
            elif path == "/section":
                sid = (qs.get("id") or [""])[0]
                group = (qs.get("group") or [""])[0]
                self._send(200, self.page_section(sid, group))
            elif path == "/phrases":
                cat = (qs.get("cat") or ["daily"])[0]
                self._send(200, self.page_phrases(cat))
            elif path == "/phrase/edit":
                cat = (qs.get("cat") or ["daily"])[0]
                pid = (qs.get("id") or [""])[0]
                self._send(200, self.page_phrase_edit(cat, pid))
            elif path == "/phrase/new":
                cat = (qs.get("cat") or ["daily"])[0]
                self._send(200, self.page_phrase_new(cat))
            elif path == "/version":
                self._send(200, self.page_version())
            elif path == "/tools/patch-menus":
                self._send(200, self.page_patch_menus())
            elif path.startswith("/media/"):
                self._serve_media(path)
            else:
                self._send(
                    404,
                    layout(
                        "404",
                        "<h1>페이지를 찾을 수 없어요</h1>"
                        "<p class='page-lead'><a class='btn secondary' href='/'>대시보드로</a></p>",
                        nav_active="/",
                        crumbs=[("/", "대시보드"), ("", "404")],
                    ),
                )
        except Exception as exc:  # noqa: BLE001
            self._send(
                500,
                layout(
                    "오류",
                    f"<h1>오류가 발생했어요</h1><pre>{h(traceback.format_exc())}</pre>",
                    flash=str(exc),
                    flash_error=True,
                    nav_active="/",
                    crumbs=[("/", "대시보드"), ("", "오류")],
                ),
            )
            sys.stderr.write(f"{exc}\n")

    def _serve_static(self, name: str, content_type: str) -> None:
        file_path = (STATIC_DIR / name).resolve()
        if not str(file_path).startswith(str(STATIC_DIR.resolve())) or not file_path.is_file():
            self.send_error(404, "Not Found")
            return
        data = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _serve_media(self, path: str) -> None:
        file_path = safe_media_path(path)
        if not file_path:
            self.send_error(404, "Not Found")
            return
        data = file_path.read_bytes()
        suffix = file_path.suffix.lower()
        ctype = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp",
            ".gif": "image/gif",
        }.get(suffix, "application/octet-stream")
        if data.startswith(b"\xff\xd8\xff"):
            ctype = "image/jpeg"
        elif data.startswith(b"\x89PNG"):
            ctype = "image/png"
        elif len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
            ctype = "image/webp"
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _read_form(self):
        body = read_http_body(self, max_bytes=MAX_BODY_BYTES)
        ctype = self.headers.get("Content-Type", "")
        return parse_request_body(ctype, body)

    def do_POST(self) -> None:  # noqa: N802
        try:
            parsed = urlparse(self.path)
            path = parsed.path
            form_data = self._read_form()
            form = form_data.fields
            files = form_data.files

            if path == "/dish/save":
                kind = form.get("kind", "meals")
                texts = dish_texts_from_form(form)
                notes = content.save_dish_fields(kind, form.get("slug", ""), texts)
                if form.get("new_slug", "").strip() and form.get("new_slug") != form.get("slug"):
                    notes.extend(
                        content.rename_dish(
                            kind,
                            form.get("slug", ""),
                            form.get("new_slug", ""),
                        )
                    )
                    slug = content.validate_slug(form["new_slug"])
                else:
                    slug = form.get("slug", "")
                upload_notes = save_uploads_for_targets(dish_image_targets(slug), files)
                notes.extend(upload_notes or ["이미지: 새로 올린 파일 없음 (기존 유지)"])
                self._redirect(
                    f"/dish/edit?kind={kind}&slug={slug}",
                    flash="\n".join(notes),
                )
                return

            if path == "/dish/create":
                kind = form.get("kind", "meals")
                texts = dish_texts_from_form(form)
                notes = content.create_dish(
                    kind,
                    form.get("slug", ""),
                    texts,
                    form.get("emoji", "").strip() or "🍽️",
                )
                slug = content.validate_slug(form["slug"])
                upload_notes = save_uploads_for_targets(dish_image_targets(slug), files)
                notes.extend(upload_notes or ["이미지: 업로드 없음 — 수정 화면에서 올릴 수 있습니다"])
                self._redirect(
                    f"/dish/edit?kind={kind}&slug={slug}",
                    flash="\n".join(notes),
                )
                return

            if path == "/dish/delete":
                notes = content.delete_dish(
                    form.get("kind", "meals"),
                    form.get("slug", ""),
                    delete_images=form.get("delete_images") == "1",
                )
                self._redirect(
                    f"/dishes?kind={form.get('kind','meals')}",
                    flash="\n".join(notes),
                )
                return

            if path == "/shop/save":
                slug = form.get("slug", "")
                texts = shop_texts_from_form(form)
                notes = content.save_shop_fields(
                    slug,
                    texts,
                    regenerate_maps=form.get("regen_maps") == "1",
                )
                if form.get("new_slug", "").strip() and form.get("new_slug") != slug:
                    notes.extend(content.rename_shop(slug, form.get("new_slug", "")))
                    slug = content.validate_slug(form["new_slug"])
                parent = form.get("parent", "")
                if "|" not in parent:
                    raise ValueError("부모 음식을 선택하세요.")
                kind, dish_slug = parent.split("|", 1)
                notes.extend(content.set_shop_parent(slug, kind, dish_slug))
                upload_notes = save_uploads_for_targets(
                    shop_image_targets(kind, dish_slug, slug),
                    files,
                )
                notes.extend(upload_notes or ["상호 이미지: 새로 올린 파일 없음 (기존 유지)"])
                menu_uploads = [
                    (fn, data)
                    for fn, data in form_data.getfiles("menu_images")
                    if data
                ]
                if menu_uploads:
                    notes.extend(append_menu_uploads(kind, dish_slug, slug, menu_uploads))
                notes.extend(sync_shop_page_menu_gallery(kind, dish_slug, slug))
                self._redirect(f"/shop/edit?slug={slug}", flash="\n".join(notes))
                return

            if path == "/shop/create":
                parent = form.get("parent", "")
                if "|" not in parent:
                    raise ValueError("부모 음식을 선택하세요.")
                kind, dish_slug = parent.split("|", 1)
                texts = shop_texts_from_form(form)
                notes = content.create_shop(
                    kind,
                    dish_slug,
                    form.get("slug", ""),
                    texts,
                )
                slug = content.validate_slug(form["slug"])
                upload_notes = save_uploads_for_targets(
                    shop_image_targets(kind, dish_slug, slug), files
                )
                notes.extend(
                    upload_notes
                    or ["상호 이미지: 업로드 없음 — 수정 화면에서 올릴 수 있습니다"]
                )
                menu_uploads = [
                    (fn, data)
                    for fn, data in form_data.getfiles("menu_images")
                    if data
                ]
                if menu_uploads:
                    notes.extend(append_menu_uploads(kind, dish_slug, slug, menu_uploads))
                notes.extend(sync_shop_page_menu_gallery(kind, dish_slug, slug))
                self._redirect(f"/shop/edit?slug={slug}", flash="\n".join(notes))
                return

            if path == "/shop/delete":
                notes = content.delete_shop(
                    form.get("slug", ""),
                    delete_images=form.get("delete_images") == "1",
                )
                self._redirect("/shops", flash="\n".join(notes))
                return

            if path == "/shop/menu/delete":
                slug = form.get("slug", "")
                shop = content.get_shop(slug)
                kind = shop.get("kind") or ""
                dish = shop.get("dish_slug") or ""
                if not kind or not dish:
                    raise ValueError("부모 음식이 없습니다.")
                idx = int(form.get("index") or "0")
                notes = delete_menu_image_at(kind, dish, slug, idx)
                notes.extend(sync_shop_page_menu_gallery(kind, dish, slug))
                self._redirect(f"/shop/edit?slug={slug}", flash="\n".join(notes))
                return

            if path == "/shop/menu/reorder":
                slug = form.get("slug", "")
                shop = content.get_shop(slug)
                kind = shop.get("kind") or ""
                dish = shop.get("dish_slug") or ""
                if not kind or not dish:
                    raise ValueError("부모 음식이 없습니다.")
                raw = form.get("order", "")
                order = [int(x.strip()) for x in raw.split(",") if x.strip().isdigit()]
                notes = renumber_menu_images(kind, dish, slug, order or None)
                notes.extend(sync_shop_page_menu_gallery(kind, dish, slug))
                if not notes:
                    notes = ["순서 변경 없음"]
                self._redirect(f"/shop/edit?slug={slug}", flash="\n".join(notes))
                return

            if path == "/section/save":
                sid = form.get("section_id", "")
                sec = sections.get_section(sid)
                keys = form_data.getlist("keys")
                updates: dict[str, dict[str, str]] = {}
                for key in keys:
                    updates[key] = {
                        "ko": form.get(f"v_{key}_ko", ""),
                        "en": form.get(f"v_{key}_en", ""),
                        "ja": form.get(f"v_{key}_ja", ""),
                    }
                notes = sections.save_entry_texts(sec, updates)
                group = form.get("group", "")
                self._redirect(
                    f"/section?id={sid}",
                    flash="\n".join(notes),
                    group=group,
                )
                return

            if path == "/section/add":
                sid = form.get("section_id", "")
                sec = sections.get_section(sid)
                notes = sections.add_string_key(
                    sec,
                    form.get("new_key", ""),
                    {
                        "ko": form.get("new_ko", ""),
                        "en": form.get("new_en", ""),
                        "ja": form.get("new_ja", ""),
                    },
                )
                self._redirect(f"/section?id={sid}", flash="\n".join(notes))
                return

            if path == "/section/delete":
                sid = form.get("section_id", "")
                sec = sections.get_section(sid)
                notes = sections.delete_string_key(sec, form.get("key", ""))
                self._redirect(f"/section?id={sid}", flash="\n".join(notes))
                return

            if path == "/phrase/save":
                cat = form.get("cat", "daily")
                pid = form.get("id", "")
                is_new = form.get("is_new") == "1"
                notes = sections.save_phrase_item(
                    cat,
                    pid,
                    {
                        "ko": form.get("ko", ""),
                        "rom": form.get("rom", ""),
                        "en": form.get("en", ""),
                        "ja": form.get("ja", ""),
                    },
                    is_new=is_new,
                )
                self._redirect(
                    f"/phrase/edit?cat={cat}&id={pid}",
                    flash="\n".join(notes),
                )
                return

            if path == "/phrase/delete":
                cat = form.get("cat", "daily")
                notes = sections.delete_phrase_item(cat, form.get("id", ""))
                self._redirect(f"/phrases?cat={cat}", flash="\n".join(notes))
                return

            if path == "/version/run":
                from datetime import datetime

                from lib.cache_bust import apply_cache_bust, write_version

                version = datetime.now().strftime("%Y%m%d%H%M%S")
                write_version(version)
                summary = apply_cache_bust(version)
                self._redirect(
                    "/version",
                    flash=(
                        f"버전 → {version}\n"
                        f"HTML 갱신 {summary['files_updated']}개 "
                        f"(교체 ~{summary['replacements']})"
                    ),
                )
                return

            if path == "/tools/patch-menus/run":
                notes = patch_all_shop_menu_galleries()
                self._redirect("/tools/patch-menus", flash="\n".join(notes))
                return

            self._send(
                404,
                layout(
                    "404",
                    "<h1>POST 경로 없음</h1><p><a class='btn secondary' href='/'>대시보드</a></p>",
                    nav_active="/",
                ),
            )
        except Exception as exc:  # noqa: BLE001
            self._send(
                200,
                layout(
                    "오류",
                    f"<h1>처리에 실패했어요</h1>"
                    f"<pre>{h(traceback.format_exc())}</pre>"
                    f"<p><a class='btn secondary' href='/'>대시보드로</a></p>",
                    flash=str(exc),
                    flash_error=True,
                    nav_active="/",
                    crumbs=[("/", "대시보드"), ("", "오류")],
                ),
            )

    # ---------- pages ----------

    def page_home(self) -> str:
        try:
            ver = read_version()
        except SystemExit:
            ver = "(없음)"
        content_cards: list[str] = []
        tool_cards: list[str] = []
        for c in sections.dashboard_cards():
            is_tool = c.href.startswith("/version") or c.href.startswith("/tools/")
            count = f'<span class="count">{h(c.count)}</span>' if c.count else ""
            card = (
                f'<a class="dash-card{" tools" if is_tool else ""}" href="{h(c.href)}">'
                f'<div class="dash-card-top"><strong>{h(c.title)}</strong>{count}</div>'
                f"<p>{h(c.desc)}</p></a>"
            )
            (tool_cards if is_tool else content_cards).append(card)
        body = f"""
        <div class="dash-hero">
          <h1>무엇을 수정할까요?</h1>
          <p class="page-lead">가이드북 콘텐츠를 이 화면에서 바로 고칠 수 있어요.</p>
          <div class="dash-meta">
            <span>에셋 버전 <code>{h(ver)}</code></span>
            <span>루트 <code>{h(ROOT)}</code></span>
          </div>
        </div>
        <section class="dash-section">
          <div class="dash-section-head">
            <h2>콘텐츠</h2>
            <span class="muted">음식 · 가게 · 섹션 · 문장</span>
          </div>
          <div class="dash-grid">{''.join(content_cards)}</div>
        </section>
        <section class="dash-section">
          <div class="dash-section-head">
            <h2>설정 / 도구</h2>
            <span class="muted">배포 전 작업</span>
          </div>
          <div class="dash-grid">{''.join(tool_cards)}</div>
        </section>
        <div class="note">
          <strong>짧게 알아두기</strong><br>
          · 음식/가게: 추가·수정·삭제·슬러그 변경 · 메뉴 사진 여러 장<br>
          · 편의점·팁·여행 전·기념품·쇼핑·앱·긴급·문의: KO/EN/JA 편집<br>
          · 유용한 한국어: 문장 데이터(JS) 편집<br>
          · 배포 전 <a href="/version">버전 업데이트</a>를 실행하세요
        </div>
        """
        return layout(
            "대시보드",
            body,
            flash=self._pop_flash(),
            flash_error=self._flash_error(),
            nav_active="/",
            crumbs=[("/", "대시보드")],
        )

    def page_dishes(self, kind: str) -> str:
        if kind not in ("meals", "desserts"):
            kind = "meals"
        label = "식사 음식" if kind == "meals" else "디저트"
        rows = []
        for d in content.list_dishes(kind):
            rows.append(
                "<tr>"
                f"<td><code>{h(d.slug)}</code></td>"
                f"<td>{h(d.title)}</td>"
                f"<td>{h(d.desc[:60])}{'…' if len(d.desc) > 60 else ''}</td>"
                f"<td class='actions'>"
                f"<a href='/dish/edit?kind={h(kind)}&slug={h(d.slug)}'>수정</a>"
                f"<a class='muted' href='/dish/delete?kind={h(kind)}&slug={h(d.slug)}'>삭제</a>"
                f"</td></tr>"
            )
        empty = (
            '<tr><td colspan="4"><div class="empty-state">'
            f"<strong>등록된 {h(label)}이 없어요</strong>"
            '<span class="muted">오른쪽 위 버튼으로 새 음식을 추가해 보세요.</span>'
            "</div></td></tr>"
        )
        body = f"""
        <div class="toolbar">
          <div>
            <h1>{label}</h1>
            <p class="page-lead">i18n <code>dishes.*</code> · <code>pages/foods/{h(kind)}/</code></p>
          </div>
          <a class="btn" href="/dish/new?kind={h(kind)}">+ 새 음식 추가</a>
        </div>
        <div class="table-wrap">
          <table>
            <thead><tr><th>슬러그 (영문 ID)</th><th>이름</th><th>설명</th><th></th></tr></thead>
            <tbody>{''.join(rows) or empty}</tbody>
          </table>
        </div>
        """
        return layout(
            label,
            body,
            flash=self._pop_flash(),
            flash_error=self._flash_error(),
            nav_active=f"/dishes?kind={kind}",
            crumbs=[("/", "대시보드"), (f"/dishes?kind={kind}", label)],
        )

    def page_dish_edit(self, kind: str, slug: str) -> str:
        d = content.get_dish(kind, slug)
        label = "식사" if kind == "meals" else "디저트"
        lang_html = render_dish_lang_fields(d.get("texts"))
        img_html = render_image_fields(dish_image_targets(slug))
        children_html = render_child_shops_readonly(kind, slug)
        body = f"""
        <h1>음식 수정</h1>
        <p class="page-lead"><code>{h(slug)}</code> · 페이지 <code>{h(d['page'] or '(없음)')}</code></p>
        <form class="card" method="post" action="/dish/save" enctype="multipart/form-data">
          <input type="hidden" name="kind" value="{h(kind)}">
          <input type="hidden" name="slug" value="{h(slug)}">
          <fieldset class="fieldset">
            <legend>기본 정보</legend>
            <div class="field">
              <label>슬러그 (영문 ID) 변경</label>
              <input type="text" name="new_slug" value="{h(slug)}" pattern="[a-z0-9]+(-[a-z0-9]+)*"
                     placeholder="예: tteokbokki">
              <span class="hint">예: tteokbokki — 주소·파일명에 쓰는 영문 소문자 (한글 불가). 변경 시 관련 경로도 함께 맞춥니다.</span>
            </div>
          </fieldset>
          {lang_html}
          <fieldset class="fieldset">
            <legend>이미지</legend>
            {img_html}
          </fieldset>
          <div class="row">
            <button type="submit">저장</button>
            <a class="btn secondary" href="/dishes?kind={h(kind)}">목록</a>
            <a class="btn danger ghost" href="/dish/delete?kind={h(kind)}&slug={h(slug)}">삭제…</a>
          </div>
        </form>
        {children_html}
        """
        return layout(
            f"수정 {slug}",
            body,
            flash=self._pop_flash(),
            flash_error=self._flash_error(),
            nav_active=f"/dishes?kind={kind}",
            crumbs=[
                ("/", "대시보드"),
                (f"/dishes?kind={kind}", label),
                ("", slug),
            ],
        )

    def page_dish_new(self, kind: str) -> str:
        label = "식사" if kind == "meals" else "디저트"
        default_emoji = "🍽️" if kind == "meals" else "🍰"
        lang_html = render_dish_lang_fields()
        img_html = render_upload_zone(
            name="cover_image",
            label="음식 대표 이미지",
            hint="저장 경로: Images/foods/dishes/{슬러그}.jpg",
            preview_html='<span class="missing">선택 사항 — 나중에 수정 화면에서도 올릴 수 있어요</span>',
        )
        body = f"""
        <h1>새 {label} 음식 추가</h1>
        <p class="page-lead">기본 정보와 번역을 채운 뒤 생성하세요.</p>
        <form class="card" method="post" action="/dish/create" enctype="multipart/form-data">
          <input type="hidden" name="kind" value="{h(kind)}">
          <fieldset class="fieldset">
            <legend>기본 정보</legend>
            <div class="field">
              <label>슬러그 (영문 ID)</label>
              <input type="text" name="slug" placeholder="예: tteokbokki" required
                     pattern="[a-z0-9]+(-[a-z0-9]+)*">
              <span class="hint">예: tteokbokki — 주소·파일명에 쓰는 영문 소문자 (한글 불가)</span>
            </div>
            <div class="field">
              <label>이모지</label>
              <input type="text" name="emoji" value="{h(default_emoji)}" style="max-width:6rem">
              <span class="hint">목록 카드에 표시됩니다</span>
            </div>
          </fieldset>
          {lang_html}
          <fieldset class="fieldset">
            <legend>이미지</legend>
            {img_html}
          </fieldset>
          <div class="row">
            <button type="submit">생성</button>
            <a class="btn secondary" href="/dishes?kind={h(kind)}">취소</a>
          </div>
        </form>
        """
        return layout(
            "새 음식",
            body,
            nav_active=f"/dishes?kind={kind}",
            crumbs=[
                ("/", "대시보드"),
                (f"/dishes?kind={kind}", label),
                ("", "새 음식"),
            ],
        )

    def page_dish_delete(self, kind: str, slug: str) -> str:
        label = "식사" if kind == "meals" else "디저트"
        body = f"""
        <h1>음식 삭제 확인</h1>
        <p class="page-lead"><code>{h(slug)}</code> 을(를) 정말 삭제할까요?</p>
        <form class="card" method="post" action="/dish/delete">
          <input type="hidden" name="kind" value="{h(kind)}">
          <input type="hidden" name="slug" value="{h(slug)}">
          <label class="check-row">
            <input type="checkbox" name="delete_images" value="1">
            <span>대표 이미지도 함께 삭제</span>
          </label>
          <div class="row">
            <button type="submit" class="danger">삭제 실행</button>
            <a class="btn secondary" href="/dish/edit?kind={h(kind)}&slug={h(slug)}">취소</a>
          </div>
        </form>
        """
        return layout(
            "삭제",
            body,
            nav_active=f"/dishes?kind={kind}",
            crumbs=[
                ("/", "대시보드"),
                (f"/dishes?kind={kind}", label),
                (f"/dish/edit?kind={kind}&slug={slug}", slug),
                ("", "삭제"),
            ],
        )

    def page_shops(self) -> str:
        rows = []
        for s in content.list_shops():
            rows.append(
                "<tr>"
                f"<td><code>{h(s.slug)}</code></td>"
                f"<td>{h(s.name)}</td>"
                f"<td>{h(s.kind)} / {h(s.dish_slug)}</td>"
                f"<td>{h(s.location[:40])}{'…' if len(s.location) > 40 else ''}</td>"
                f"<td class='actions'>"
                f"<a href='/shop/edit?slug={h(s.slug)}'>수정</a>"
                f"<a class='muted' href='/shop/delete?slug={h(s.slug)}'>삭제</a>"
                f"</td></tr>"
            )
        empty = (
            '<tr><td colspan="5"><div class="empty-state">'
            "<strong>등록된 가게가 없어요</strong>"
            '<span class="muted">새 가게를 추가해 부모 음식에 연결해 보세요.</span>'
            "</div></td></tr>"
        )
        body = f"""
        <div class="toolbar">
          <div>
            <h1>가게 / 브랜드</h1>
            <p class="page-lead">i18n <code>restaurants.*</code> · 메뉴 사진 여러 장 지원</p>
          </div>
          <a class="btn" href="/shop/new">+ 새 가게 추가</a>
        </div>
        <div class="table-wrap">
          <table>
            <thead><tr><th>슬러그 (영문 ID)</th><th>이름</th><th>소속</th><th>위치</th><th></th></tr></thead>
            <tbody>{''.join(rows) or empty}</tbody>
          </table>
        </div>
        """
        return layout(
            "가게",
            body,
            flash=self._pop_flash(),
            flash_error=self._flash_error(),
            nav_active="/shops",
            crumbs=[("/", "대시보드"), ("/shops", "가게")],
        )

    def page_shop_edit(self, slug: str) -> str:
        s = content.get_shop(slug)
        lang_html = render_shop_lang_fields(s.get("texts"))
        current_parent = (
            f"{s['kind']}|{s['dish_slug']}"
            if s.get("kind") and s.get("dish_slug")
            else ""
        )
        opts = []
        for kind, dish_slug, label in content.dish_options_for_select():
            value = f"{kind}|{dish_slug}"
            sel = " selected" if value == current_parent else ""
            opts.append(f'<option value="{h(value)}"{sel}>{h(label)}</option>')
        if s.get("kind") and s.get("dish_slug"):
            img_html = render_image_fields(
                shop_image_targets(s["kind"], s["dish_slug"], slug)
            )
        else:
            img_html = (
                '<p class="muted" style="margin:0">'
                "부모 음식을 선택한 뒤 저장하면 이미지 경로가 정해집니다.</p>"
            )
        menu_html = render_menu_images_manager(s)
        maps = s.get("mapsUrl") or ""
        maps_short = f"{maps[:80]}{'…' if len(maps) > 80 else ''}"
        body = f"""
        <h1>가게 수정</h1>
        <p class="page-lead"><code>{h(slug)}</code> · 페이지 <code>{h(s['page'] or '(없음)')}</code></p>
        <form class="card" id="shop-main-form" method="post" action="/shop/save" enctype="multipart/form-data">
          <input type="hidden" name="slug" value="{h(slug)}">
          <fieldset class="fieldset highlight">
            <legend>부모 음식 (필수)</legend>
            <div class="field">
              <label>이 가게가 속한 음식</label>
              <select class="parent-select" name="parent" required>
                <option value="">음식을 선택하세요…</option>
                {''.join(opts)}
              </select>
              <span class="hint">목록·경로·이미지 폴더가 이 선택에 맞춰집니다.</span>
            </div>
          </fieldset>
          <fieldset class="fieldset">
            <legend>기본 정보</legend>
            <div class="field">
              <label>슬러그 (영문 ID) 변경</label>
              <input type="text" name="new_slug" value="{h(slug)}" pattern="[a-z0-9]+(-[a-z0-9]+)*"
                     placeholder="예: tteokbokki">
              <span class="hint">예: tteokbokki — 주소·파일명에 쓰는 영문 소문자 (한글 불가)</span>
            </div>
            <label class="check-row">
              <input type="checkbox" name="regen_maps" value="1" checked>
              <span>저장 시 한국어 location으로 mapsUrl 재생성</span>
            </label>
            <p class="muted" style="margin:.35rem 0 0">현재 mapsUrl: <code>{h(maps_short)}</code></p>
          </fieldset>
          {lang_html}
          <fieldset class="fieldset">
            <legend>상호 이미지</legend>
            {img_html}
          </fieldset>
          {menu_html}
          <div class="row">
            <button type="submit">저장</button>
            <a class="btn secondary" href="/shops">목록</a>
            <a class="btn danger ghost" href="/shop/delete?slug={h(slug)}">삭제…</a>
          </div>
        </form>
        """
        return layout(
            f"가게 {slug}",
            body,
            flash=self._pop_flash(),
            flash_error=self._flash_error(),
            nav_active="/shops",
            crumbs=[("/", "대시보드"), ("/shops", "가게"), ("", slug)],
        )

    def page_shop_new(self) -> str:
        opts = []
        for kind, slug, label in content.dish_options_for_select():
            opts.append(f'<option value="{h(kind)}|{h(slug)}">{h(label)}</option>')
        lang_html = render_shop_lang_fields()
        shop_upload = render_upload_zone(
            name="shop_image",
            label="상호 이미지",
            hint="선택 사항 — 생성 후에도 수정 화면에서 올릴 수 있어요",
        )
        menu_upload = render_upload_zone(
            name="menu_images",
            label="메뉴 이미지",
            hint="{슬러그}-menu-1.jpg 부터 순서대로 저장 · 여러 장 가능",
            multiple=True,
        )
        body = f"""
        <h1>새 가게 추가</h1>
        <p class="page-lead">먼저 부모 음식을 고른 뒤 가게 정보를 입력하세요.</p>
        <form class="card" id="shop-main-form" method="post" action="/shop/create" enctype="multipart/form-data">
          <fieldset class="fieldset highlight">
            <legend>부모 음식 (필수)</legend>
            <div class="field">
              <label>이 가게가 속한 음식</label>
              <select class="parent-select" name="parent" required>
                <option value="">음식을 선택하세요…</option>
                {''.join(opts)}
              </select>
              <span class="hint">가게 페이지·이미지 경로가 이 음식 아래에 만들어집니다.</span>
            </div>
          </fieldset>
          <fieldset class="fieldset">
            <legend>기본 정보</legend>
            <div class="field">
              <label>슬러그 (영문 ID)</label>
              <input type="text" name="slug" required pattern="[a-z0-9]+(-[a-z0-9]+)*"
                     placeholder="예: tteokbokki">
              <span class="hint">예: tteokbokki — 주소·파일명에 쓰는 영문 소문자 (한글 불가)</span>
            </div>
          </fieldset>
          {lang_html}
          <fieldset class="fieldset">
            <legend>이미지</legend>
            {shop_upload}
            {menu_upload}
          </fieldset>
          <div class="row">
            <button type="submit">생성</button>
            <a class="btn secondary" href="/shops">취소</a>
          </div>
        </form>
        """
        return layout(
            "새 가게",
            body,
            nav_active="/shops",
            crumbs=[("/", "대시보드"), ("/shops", "가게"), ("", "새 가게")],
        )

    def page_shop_delete(self, slug: str) -> str:
        body = f"""
        <h1>가게 삭제 확인</h1>
        <p class="page-lead"><code>{h(slug)}</code> 을(를) 정말 삭제할까요?</p>
        <form class="card" method="post" action="/shop/delete">
          <input type="hidden" name="slug" value="{h(slug)}">
          <label class="check-row">
            <input type="checkbox" name="delete_images" value="1">
            <span>이미지도 삭제 (상호 + 모든 메뉴)</span>
          </label>
          <div class="row">
            <button type="submit" class="danger">삭제 실행</button>
            <a class="btn secondary" href="/shop/edit?slug={h(slug)}">취소</a>
          </div>
        </form>
        """
        return layout(
            "삭제",
            body,
            nav_active="/shops",
            crumbs=[
                ("/", "대시보드"),
                ("/shops", "가게"),
                (f"/shop/edit?slug={slug}", slug),
                ("", "삭제"),
            ],
        )

    def page_section(self, section_id: str, group: str) -> str:
        sec = sections.get_section(section_id)
        keys = sections.list_section_keys(sec)
        groups = sections.group_keys(sec, keys)
        group_names = list(groups.keys())
        if not group or group not in groups:
            group = group_names[0] if group_names else ""
        show_keys = groups.get(group, keys) if group else keys
        # Cap editor size for huge groups
        MAX_EDIT = 40
        truncated = False
        if len(show_keys) > MAX_EDIT:
            show_keys = show_keys[:MAX_EDIT]
            truncated = True

        group_nav = ""
        if sec.group_by_prefix and len(group_names) > 1:
            links = []
            for gname in group_names:
                active = " active" if gname == group else ""
                links.append(
                    f'<a class="{active.strip()}" '
                    f'href="/section?id={uq(sec.id)}&group={uq(gname)}">'
                    f"{h(gname)} ({len(groups[gname])})</a>"
                )
            group_nav = f'<div class="group-nav">{"".join(links)}</div>'

        rows = []
        delete_rows = []
        for key in show_keys:
            texts = sections.load_entry_texts(sec, key)
            rows.append(
                f'<div class="entry-row">'
                f'<input type="hidden" name="keys" value="{h(key)}">'
                f'<label><code>{h(sec.root_key)}.{h(key)}</code></label>'
                f'<div class="side-langs">'
                f'<div><label>KO</label><textarea name="v_{h(key)}_ko">{h(texts["ko"])}</textarea></div>'
                f'<div><label>EN</label><textarea name="v_{h(key)}_en">{h(texts["en"])}</textarea></div>'
                f'<div><label>JA</label><textarea name="v_{h(key)}_ja">{h(texts["ja"])}</textarea></div>'
                f"</div></div>"
            )
            delete_rows.append(
                f'<form method="post" action="/section/delete" style="display:inline" '
                f'onsubmit="return confirm(\'{h(key)} 삭제할까요?\');">'
                f'<input type="hidden" name="section_id" value="{h(sec.id)}">'
                f'<input type="hidden" name="key" value="{h(key)}">'
                f'<button type="submit" class="danger ghost">삭제 {h(key)}</button></form>'
            )

        body = f"""
        <h1>{h(sec.title)}</h1>
        <p class="page-lead">{h(sec.description)} · 루트 키 <code>{h(sec.root_key)}</code> · 총 {len(keys)}키</p>
        {group_nav}
        {"<p class='note'>이 그룹이 커서 처음 40개만 표시합니다. 그룹 탭으로 나눠 편집하세요.</p>" if truncated else ""}
        <form class="card" method="post" action="/section/save">
          <input type="hidden" name="section_id" value="{h(sec.id)}">
          <input type="hidden" name="group" value="{h(group)}">
          <fieldset class="fieldset" style="box-shadow:none;background:#fff;margin:0 0 .5rem">
            <legend>번역 편집</legend>
            {''.join(rows) or '<div class="empty-state"><strong>키가 없어요</strong></div>'}
          </fieldset>
          <div class="row">
            <button type="submit">이 화면 저장 + messages.js 빌드</button>
            <a class="btn secondary" href="/">대시보드</a>
          </div>
        </form>
        <div class="panel danger-zone">
          <h2>키 삭제</h2>
          <p class="muted">저장과 별개로 개별 키를 제거할 수 있습니다.</p>
          <div class="row">{''.join(delete_rows) or '<span class="muted">없음</span>'}</div>
        </div>
        <form class="card" method="post" action="/section/add">
          <fieldset class="fieldset" style="box-shadow:none;margin:0">
            <legend>키 추가</legend>
            <input type="hidden" name="section_id" value="{h(sec.id)}">
            <div class="field">
              <label>새 키 이름</label>
              <input type="text" name="new_key" required pattern="[A-Za-z0-9_-]+" placeholder="예: myTipTitle">
            </div>
            <div class="side-langs">
              <div><label>KO</label><textarea name="new_ko" required></textarea></div>
              <div><label>EN</label><textarea name="new_en"></textarea></div>
              <div><label>JA</label><textarea name="new_ja"></textarea></div>
            </div>
            <div class="row"><button type="submit">키 추가</button></div>
          </fieldset>
        </form>
        """
        return layout(
            sec.title,
            body,
            flash=self._pop_flash(),
            flash_error=self._flash_error(),
            nav_active=f"/section?id={sec.id}",
            crumbs=[("/", "대시보드"), (f"/section?id={sec.id}", sec.title)],
        )

    def page_phrases(self, cat: str) -> str:
        cats = sections.list_phrase_categories()
        if cat not in cats:
            cat = cats[0] if cats else "daily"
        items = sections.get_phrases(cat)
        nav = "".join(
            f'<a class="{"active" if c == cat else ""}" href="/phrases?cat={h(c)}">{h(c)}</a>'
            for c in cats
        )
        rows = []
        for p in items:
            rows.append(
                "<tr>"
                f"<td><code>{h(p.get('id',''))}</code></td>"
                f"<td>{h(p.get('ko',''))}</td>"
                f"<td>{h(p.get('en','')[:40])}</td>"
                f"<td class='actions'><a href='/phrase/edit?cat={h(cat)}&id={h(p.get('id',''))}'>수정</a></td>"
                "</tr>"
            )
        empty = (
            '<tr><td colspan="4"><div class="empty-state">'
            "<strong>이 카테고리에 문장이 없어요</strong>"
            '<span class="muted">새 문장을 추가해 보세요.</span></div></td></tr>'
        )
        body = f"""
        <div class="toolbar">
          <div>
            <h1>유용한 한국어 문장</h1>
            <p class="page-lead">데이터 <code>js/korean-phrases-data.js</code> · 페이지 탭 문구는
            <a href="/section?id=korean">korean i18n</a></p>
          </div>
          <a class="btn" href="/phrase/new?cat={h(cat)}">+ 문장 추가</a>
        </div>
        <div class="group-nav">{nav}</div>
        <div class="table-wrap">
          <table>
            <thead><tr><th>id</th><th>KO</th><th>EN</th><th></th></tr></thead>
            <tbody>{''.join(rows) or empty}</tbody>
          </table>
        </div>
        """
        return layout(
            "한국어 문장",
            body,
            flash=self._pop_flash(),
            flash_error=self._flash_error(),
            nav_active="/phrases",
            crumbs=[("/", "대시보드"), ("/phrases", "한국어")],
        )

    def page_phrase_edit(self, cat: str, phrase_id: str) -> str:
        items = sections.get_phrases(cat)
        item = next((p for p in items if p.get("id") == phrase_id), None)
        if not item:
            raise ValueError(f"문장 없음: {phrase_id}")
        body = f"""
        <h1>문장 수정</h1>
        <p class="page-lead"><code>{h(phrase_id)}</code> · 카테고리 <code>{h(cat)}</code></p>
        <form class="card" method="post" action="/phrase/save">
          <input type="hidden" name="cat" value="{h(cat)}">
          <input type="hidden" name="id" value="{h(phrase_id)}">
          <input type="hidden" name="is_new" value="0">
          <fieldset class="fieldset">
            <legend>문장 내용</legend>
            <div class="field"><label>한국어</label>
              <textarea name="ko" required>{h(item.get('ko',''))}</textarea></div>
            <div class="field"><label>발음 표기 (영문)</label>
              <input type="text" name="rom" value="{h(item.get('rom',''))}"
                     placeholder="예: annyeonghaseyo">
              <span class="hint">한글 발음을 알파벳으로 적은 것 (읽기 도움용 · URL 슬러그와 다름)</span></div>
            <div class="field"><label>English</label>
              <textarea name="en">{h(item.get('en',''))}</textarea></div>
            <div class="field"><label>日本語</label>
              <textarea name="ja">{h(item.get('ja',''))}</textarea></div>
          </fieldset>
          <div class="row">
            <button type="submit">저장</button>
            <a class="btn secondary" href="/phrases?cat={h(cat)}">목록</a>
          </div>
        </form>
        <form class="danger-zone" method="post" action="/phrase/delete"
              onsubmit="return confirm('삭제할까요?');">
          <input type="hidden" name="cat" value="{h(cat)}">
          <input type="hidden" name="id" value="{h(phrase_id)}">
          <h2>위험 구역</h2>
          <p class="muted">이 문장을 목록에서 제거합니다.</p>
          <button type="submit" class="danger">삭제</button>
        </form>
        """
        return layout(
            "문장 수정",
            body,
            flash=self._pop_flash(),
            flash_error=self._flash_error(),
            nav_active="/phrases",
            crumbs=[
                ("/", "대시보드"),
                ("/phrases", "한국어"),
                (f"/phrases?cat={cat}", cat),
                ("", phrase_id),
            ],
        )

    def page_phrase_new(self, cat: str) -> str:
        body = f"""
        <h1>새 문장</h1>
        <p class="page-lead">카테고리 <code>{h(cat)}</code></p>
        <form class="card" method="post" action="/phrase/save">
          <input type="hidden" name="cat" value="{h(cat)}">
          <input type="hidden" name="is_new" value="1">
          <fieldset class="fieldset">
            <legend>기본 정보</legend>
            <div class="field">
              <label>id</label>
              <input type="text" name="id" required pattern="[a-z0-9-]+" placeholder="my-phrase">
              <span class="hint">영문 소문자·숫자·하이픈</span>
            </div>
          </fieldset>
          <fieldset class="fieldset">
            <legend>문장 내용</legend>
            <div class="field"><label>한국어</label><textarea name="ko" required></textarea></div>
            <div class="field"><label>발음 표기 (영문)</label>
              <input type="text" name="rom" placeholder="예: annyeonghaseyo">
              <span class="hint">한글 발음을 알파벳으로 적은 것 (읽기 도움용 · URL 슬러그와 다름)</span></div>
            <div class="field"><label>English</label><textarea name="en"></textarea></div>
            <div class="field"><label>日本語</label><textarea name="ja"></textarea></div>
          </fieldset>
          <div class="row">
            <button type="submit">추가</button>
            <a class="btn secondary" href="/phrases?cat={h(cat)}">취소</a>
          </div>
        </form>
        """
        return layout(
            "새 문장",
            body,
            nav_active="/phrases",
            crumbs=[
                ("/", "대시보드"),
                ("/phrases", "한국어"),
                (f"/phrases?cat={cat}", cat),
                ("", "새 문장"),
            ],
        )

    def page_version(self) -> str:
        try:
            ver = read_version()
        except SystemExit:
            ver = "(없음)"
        body = f"""
        <h1>캐시 버전</h1>
        <p class="page-lead">현재 버전 <code>{h(ver)}</code></p>
        <form class="card" method="post" action="/version/run">
          <fieldset class="fieldset" style="margin:0">
            <legend>버전 업데이트</legend>
            <p class="muted" style="margin:0 0 .75rem">
              <code>js/cache-version.js</code>를 새 시각 버전으로 쓰고,
              모든 HTML의 <code>?v=</code>를 일괄 적용합니다. 배포 전에 한 번 실행하세요.
            </p>
            <div class="row" style="margin-top:0">
              <button type="submit">지금 버전 업데이트 실행</button>
            </div>
          </fieldset>
        </form>
        """
        return layout(
            "버전",
            body,
            flash=self._pop_flash(),
            flash_error=self._flash_error(),
            nav_active="/version",
            crumbs=[("/", "대시보드"), ("/version", "버전")],
        )

    def page_patch_menus(self) -> str:
        body = f"""
        <h1>메뉴 갤러리 패치</h1>
        <p class="page-lead">기존 가게 HTML의 단일 메뉴 사진을 다중 갤러리로 맞춥니다.</p>
        <form class="card" method="post" action="/tools/patch-menus/run">
          <fieldset class="fieldset" style="margin:0">
            <legend>일괄 적용</legend>
            <p class="muted" style="margin:0 0 .75rem">
              가게 상세 HTML의 단일 <code>menu-photo</code>를
              발견된 모든 <code>*-menu*.jpg</code> 갤러리로 확장합니다.
            </p>
            <div class="row" style="margin-top:0">
              <button type="submit">전체 가게 페이지에 적용</button>
            </div>
          </fieldset>
        </form>
        """
        return layout(
            "메뉴 패치",
            body,
            flash=self._pop_flash(),
            flash_error=self._flash_error(),
            nav_active="/tools/patch-menus",
            crumbs=[("/", "대시보드"), ("/tools/patch-menus", "메뉴 패치")],
        )


def main() -> int:
    server = ThreadingHTTPServer((HOST, PORT), AdminHandler)
    server.flash = ""  # type: ignore[attr-defined]
    url = f"http://{HOST}:{PORT}/"
    print(f"콘텐츠 관리 서버: {url}")
    print(f"프로젝트 루트: {ROOT}")
    print("종료: Ctrl+C")
    try:
        webbrowser.open(url)
    except Exception:  # noqa: BLE001
        pass
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n종료합니다.")
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
