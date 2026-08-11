# -*- coding: utf-8 -*-
"""Local comprehensive content admin for Korea Travel Guidebook (stdlib only).

Usage:
  python tool/content-admin.py
  double-click tool/content-admin.bat

Opens http://127.0.0.1:8765
"""
from __future__ import annotations

import html
import json
import re
import sys
import traceback
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, urlencode, urlparse

TOOL_DIR = Path(__file__).resolve().parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from lib import content, places, sections  # noqa: E402
from lib.cache_bust import bump_asset_version, read_version  # noqa: E402
from lib.images import (  # noqa: E402
    MAX_UPLOAD_BYTES,
    append_menu_uploads,
    delete_menu_image_at,
    dish_cover_path,
    dish_image_targets,
    rel_posix,
    renumber_menu_images,
    safe_media_path,
    save_uploads_for_targets,
    shop_image_targets,
    shop_photo_path,
)
from lib.multipart import parse_request_body, read_http_body  # noqa: E402
from lib.paths import ROOT  # noqa: E402
from lib.scaffold import (  # noqa: E402
    patch_all_shop_menu_galleries,
    sync_shop_page_body,
    sync_shop_page_menu_gallery,
    sync_shop_page_visual,
)
from lib import content_body  # noqa: E402
from lib.shop_body import body_from_form  # noqa: E402

HOST = "127.0.0.1"
PORT = 8765
MAX_BODY_BYTES = MAX_UPLOAD_BYTES * 12 + 512 * 1024

# Shown after successful CMS saves so the open viewer tab is refreshed.
VIEW_REFRESH_HINT = "강력 새로고침(Ctrl+F5) 또는 뷰어 다시 열기"


def h(text: object) -> str:
    return html.escape("" if text is None else str(text), quote=True)


def save_ok_message(base: str = "저장됨") -> str:
    """Primary toast line: saved + how to see updates immediately."""
    return f"{base} — {VIEW_REFRESH_HINT}"


def refresh_public_assets(notes: list[str] | None = None) -> list[str]:
    """Bump SITE_ASSET_VERSION + HTML ?v= after content/media changes.

    i18n saves already call build-bundle; this forces browsers (and GitHub Pages
    later) to fetch the new messages.js / CSS / JS instead of a stale ?v=.
    """
    out = list(notes or [])
    try:
        summary = bump_asset_version()
        out.append(
            f"캐시 버전 {summary['version']} "
            f"(HTML {summary['files_updated']}/{summary['files_scanned']}개 갱신, "
            f"검증 {summary['files_ok']}개)"
        )
    except Exception as exc:  # noqa: BLE001
        out.append(f"캐시 버전 자동 갱신 실패: {exc}")
    return out


REGION_OPTIONS = (
    ("seoul", "서울"),
    ("gyeonggi", "경기"),
    ("incheon", "인천"),
    ("gangwon", "강원"),
    ("busan", "부산"),
    ("gyeongju", "경주"),
    ("gyeongsang", "경상"),
    ("jeolla", "전라"),
    ("jeju", "제주"),
)
TYPE_OPTIONS = (
    ("city", "도시·번화가"),
    ("nature", "자연·공원"),
    ("heritage", "유적·문화"),
    ("airport", "공항"),
    ("info", "안내·대사관"),
)


def _region_select(selected: str = "seoul") -> str:
    return "".join(
        f'<option value="{h(r)}"{" selected" if r == selected else ""}>{h(label)}</option>'
        for r, label in REGION_OPTIONS
    )


def _type_select(selected: str = "city") -> str:
    return "".join(
        f'<option value="{h(t)}"{" selected" if t == selected else ""}>{h(label)}</option>'
        for t, label in TYPE_OPTIONS
    )


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
        "홈",
        [
            ("/", "대시보드", "홈", "/"),
        ],
    ),
    (
        "떠나기 전에",
        [
            ("/section?id=beforeTrip", "떠나기 전에", "전", "/section?id=beforeTrip"),
        ],
    ),
    (
        "준비·안내",
        [
            ("/section?id=apps", "추천 앱", "앱", "/section?id=apps"),
            ("/phrases", "유용한 한국어", "한", "/phrase"),
            ("/section?id=korean", "한국어 페이지", "문", "/section?id=korean"),
            ("/section?id=emergency", "긴급", "긴", "/section?id=emergency"),
        ],
    ),
    (
        "먹거리",
        [
            ("/dishes?kind=meals", "식사", "식", "/dishes?kind=meals"),
            ("/dishes?kind=desserts", "디저트", "디", "/dishes?kind=desserts"),
            ("/shops", "가게", "가", "/shop"),
            ("/section?id=convenience", "편의점", "편", "/section?id=convenience"),
        ],
    ),
    (
        "쇼핑 및 놀거리",
        [
            ("/section?id=souvenir", "쇼핑 상품", "쇼", "/section?id=souvenir"),
            ("/section?id=fun", "놀거리", "놀", "/section?id=fun"),
            ("/section?id=shopping", "쇼핑 팁", "팁", "/section?id=shopping"),
        ],
    ),
    (
        "명소",
        [
            ("/places", "대표 명소", "명", "/place"),
        ],
    ),
    (
        "여행 팁",
        [
            ("/section?id=tips", "여행 팁", "팁", "/section?id=tips"),
        ],
    ),
    (
        "설정",
        [
            ("/section?id=contact", "문의", "문의", "/section?id=contact"),
            ("/version", "사이트 새로고침", "새", "/version"),
            ("/tools/migrate-body", "본문 정리", "정", "/tools/migrate-body"),
            ("/tools/patch-menus", "메뉴 정리", "메", "/tools/patch-menus"),
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
    if match == "/place" and (
        nav_active.startswith("/places") or nav_active.startswith("/place")
    ):
        return True
    return False


def render_crumbs(crumbs: list[tuple[str, str]] | None) -> str:
    base = [("/", "관리")]
    items = list(crumbs or [])
    # Avoid duplicating leading 관리/대시보드
    if items and items[0][0] in ("/", "") and items[0][1] in ("대시보드", "관리"):
        items = items[1:]
    all_crumbs = base + items
    parts: list[str] = []
    for i, (href, label) in enumerate(all_crumbs):
        if i:
            parts.append('<span class="sep" aria-hidden="true">›</span>')
        is_last = i == len(all_crumbs) - 1
        if is_last or not href:
            parts.append(f'<span class="current">{h(label)}</span>')
        else:
            parts.append(f'<a href="{h(href)}">{h(label)}</a>')
    return f'<nav class="crumbs" aria-label="경로">{"".join(parts)}</nav>'


def render_toast(flash: str, *, error: bool = False) -> str:
    if not flash:
        return ""
    cls = "toast error" if error else "toast"
    lines = [ln for ln in flash.split("\n") if ln.strip()]
    head = lines[0] if lines else flash
    detail = ""
    if len(lines) > 1:
        detail = (
            '<details class="toast-detail"><summary>자세히</summary>'
            f"<pre>{h(chr(10).join(lines[1:]))}</pre></details>"
        )
    return (
        f'<div class="toast-stack" id="toast-stack">'
        f'<div class="{cls}" role="status">'
        f'<button type="button" class="toast-close" aria-label="닫기" '
        f"onclick=\"this.closest('.toast-stack')?.remove()\">×</button>"
        f"<strong class=\"toast-title\">{h(head)}</strong>{detail}</div></div>"
    )


def friendly_flash(ok_msg: str, notes: list[str] | None = None) -> str:
    """Primary Korean toast + optional technical notes under '자세히'."""
    notes = [n for n in (notes or []) if n and n.strip()]
    if not notes:
        return ok_msg
    return ok_msg + "\n" + "\n".join(notes)


def save_flash(
    ok_msg: str,
    notes: list[str] | None = None,
    status: object | None = None,
) -> str:
    """Toast with auto-translate status line when available."""
    try:
        from lib.translate import BatchStatus, merge_flash

        if isinstance(status, BatchStatus):
            return merge_flash(ok_msg, status, notes)
    except Exception:  # noqa: BLE001
        pass
    return friendly_flash(ok_msg, notes)


def render_force_translate_check() -> str:
    return (
        '<label class="check-row">'
        '<input type="checkbox" name="force_translate" value="1">'
        "<span>번역 다시 하기</span>"
        "</label>"
        '<p class="hint" style="margin:.35rem 0 0">'
        "이미 있는 영어·일본어를 한국어 기준으로 다시 만듭니다."
        "</p>"
    )


def layout(
    title: str,
    body: str,
    *,
    flash: str = "",
    flash_error: bool = False,
    nav_active: str = "/",
    crumbs: list[tuple[str, str]] | None = None,
    preview_href: str = "",
) -> str:
    nav_chunks: list[str] = []
    for group_label, items in NAV_GROUPS:
        links = []
        group_active = False
        for href, label, icon, match in items:
            active = _nav_is_active(nav_active, match, href)
            if active:
                group_active = True
            active_cls = " is-active" if active else ""
            links.append(
                f'<a class="nav-link{active_cls}" href="{h(href)}">'
                f'<span class="nav-ico" aria-hidden="true">{h(icon)}</span>'
                f"<span>{h(label)}</span></a>"
            )
        open_attr = " open" if group_active or group_label == "홈" else ""
        nav_chunks.append(
            f'<details class="nav-group"{open_attr}>'
            f'<summary class="nav-group-label">{h(group_label)}</summary>'
            f'<div class="nav-group-links">{"".join(links)}</div></details>'
        )
    toast = render_toast(flash, error=flash_error)
    crumbs_html = render_crumbs(crumbs)
    preview = ""
    if preview_href:
        preview = (
            f'<a class="topbar-preview" href="{h(preview_href)}" target="_blank" '
            f'rel="noopener">사이트 미리보기</a>'
        )
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{h(title)} · 가이드북 관리</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/static/admin.css">
  <link rel="stylesheet" href="/static/vendor/quill/quill.snow.css">
</head>
<body>
  {toast}
  <div class="app">
    <aside class="sidebar" aria-label="주요 메뉴">
      <div class="brand">
        <div class="brand-mark" aria-hidden="true">KR</div>
        <div class="brand-text">
          <strong>가이드북 관리</strong>
          <span>카페처럼 편하게 글 쓰기</span>
        </div>
      </div>
      {"".join(nav_chunks)}
      <div class="sidebar-foot">이 컴퓨터에서만 열림 · 저장 후 Ctrl+F5 또는 뷰어 다시 열기</div>
    </aside>
    <div class="main-wrap">
      <div class="topbar">
        {crumbs_html}
        <div class="topbar-actions">
          {preview}
          <span class="topbar-hint">게시판처럼 골라서 수정하세요</span>
        </div>
      </div>
      <main class="content">
        <div class="paper">
        {body}
        </div>
      </main>
    </div>
  </div>
  <script src="/static/vendor/quill/quill.js"></script>
  <script src="/static/admin-body.js"></script>
  <script src="/static/admin-list.js"></script>
  <script>
  (function () {{
    document.querySelectorAll("[data-nav-select]").forEach(function (sel) {{
      sel.addEventListener("change", function () {{
        if (sel.value) location.href = sel.value;
      }});
    }});
    var stack = document.getElementById("toast-stack");
    if (stack) {{
      setTimeout(function () {{ stack.remove(); }}, 9000);
    }}
    /* Required fields inside closed <details> used to fail submit with no visible error. */
    document.querySelectorAll("form").forEach(function (form) {{
      form.setAttribute("novalidate", "novalidate");
      form.addEventListener("invalid", function (e) {{
        var t = e.target;
        if (!t) return;
        var details = t.closest && t.closest("details");
        if (details && !details.open) details.open = true;
      }}, true);
      form.addEventListener("submit", function (e) {{
        if (typeof form.checkValidity === "function" && !form.checkValidity()) {{
          e.preventDefault();
          var bad = form.querySelector(":invalid");
          if (bad) {{
            var d = bad.closest && bad.closest("details");
            if (d && !d.open) d.open = true;
            try {{ bad.focus(); }} catch (err) {{}}
            var label = (bad.getAttribute("aria-label")
              || (bad.labels && bad.labels[0] && bad.labels[0].textContent)
              || bad.getAttribute("placeholder")
              || bad.getAttribute("name")
              || "필수 항목");
            window.alert("입력값을 확인해 주세요: " + String(label).trim().replace(/\\s+/g, " "));
          }} else {{
            window.alert("필수 항목을 확인해 주세요.");
          }}
        }}
      }});
    }});
  }})();
  </script>
</body>
</html>
"""


def media_url(rel_path: str) -> str:
    return "/media/" + rel_path.lstrip("/")


def public_href(rel_path: str) -> str:
    """Open public HTML via file:// is hard; serve relative path hint as /media won't work.
    Admin runs locally — link to path under ROOT for file explorers via custom route.
    We expose a simple /preview/ redirect that serves the HTML file.
    """
    rel = (rel_path or "").lstrip("/")
    if not rel:
        return ""
    return "/preview/" + rel


LANG_TAB_LABELS = {"ko": "한국어", "en": "영어", "ja": "일본어"}  # legacy; prefer KO-only forms
LANG_FULL_LABELS = {"ko": "한국어", "en": "영어", "ja": "일본어"}


def render_editor_actions(
    *,
    save_label: str = "저장",
    back_href: str = "/",
    back_label: str = "목록으로",
    delete_href: str = "",
) -> str:
    delete = ""
    if delete_href:
        delete = (
            f'<a class="btn danger ghost" href="{h(delete_href)}">삭제</a>'
        )
    return (
        f'<div class="editor-actions">'
        f'<button type="submit">{h(save_label)}</button>'
        f'<a class="btn secondary" href="{h(back_href)}">{h(back_label)}</a>'
        f"{delete}</div>"
    )


def render_expert(inner: str, *, summary: str = "전문가용") -> str:
    return (
        f'<details class="expert-box">'
        f"<summary>{h(summary)}</summary>"
        f'<div class="expert-body">{inner}</div></details>'
    )


def render_thumb(rel: str, *, alt: str = "") -> str:
    if not rel:
        return '<span class="list-thumb list-thumb--empty" aria-hidden="true"></span>'
    path = ROOT / rel
    if not path.is_file():
        return '<span class="list-thumb list-thumb--empty" aria-hidden="true"></span>'
    mtime = int(path.stat().st_mtime)
    return (
        f'<img class="list-thumb" src="{h(media_url(rel))}?t={mtime}" '
        f'alt="{h(alt)}" loading="lazy">'
    )


def render_list_row(
    *,
    href: str,
    title: str,
    subtitle: str = "",
    meta: str = "",
    thumb_rel: str = "",
    filter_text: str = "",
    filter_group: str = "",
) -> str:
    ftext = filter_text or f"{title} {subtitle} {meta}"
    group_attr = f' data-filter-group="{h(filter_group)}"' if filter_group else ""
    sub = f'<span class="list-row__sub">{h(subtitle)}</span>' if subtitle else ""
    meta_html = f'<span class="list-row__meta">{h(meta)}</span>' if meta else ""
    return (
        f'<a class="list-row" href="{h(href)}" data-filter-item '
        f'data-filter-text="{h(ftext)}"{group_attr}>'
        f"{render_thumb(thumb_rel, alt=title)}"
        f'<span class="list-row__body">'
        f'<strong class="list-row__title">{h(title)}</strong>'
        f"{sub}{meta_html}</span>"
        f'<span class="list-row__chev" aria-hidden="true">›</span></a>'
    )


def empty_state(title: str, lead: str, cta_href: str, cta_label: str) -> str:
    return (
        f'<div class="empty-state empty-state--panel">'
        f"<strong>{h(title)}</strong>"
        f'<span class="muted">{h(lead)}</span>'
        f'<a class="btn" href="{h(cta_href)}">{h(cta_label)}</a>'
        f"</div>"
    )


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





def place_texts_from_form(form: dict[str, str]) -> dict[str, dict[str, str]]:
    """KO-primary place fields; EN/JA filled on save."""
    ko = {
        "name": form.get("name_ko", ""),
        "desc": form.get("desc_ko", ""),
        "how": form.get("how_ko", ""),
        "address": form.get("address_ko", ""),
        "regionLabel": form.get("regionLabel_ko", ""),
    }
    # Optional body_ko → single text block handled by API layer
    return {
        "ko": ko,
        "en": {
            "name": form.get("name_en", ""),
            "desc": form.get("desc_en", ""),
            "how": form.get("how_en", ""),
            "address": form.get("address_en", ""),
            "regionLabel": form.get("regionLabel_en", ""),
        },
        "ja": {
            "name": form.get("name_ja", ""),
            "desc": form.get("desc_ja", ""),
            "how": form.get("how_ja", ""),
            "address": form.get("address_ja", ""),
            "regionLabel": form.get("regionLabel_ja", ""),
        },
    }


def body_blocks_from_place_form(form: dict[str, str], files) -> tuple[list | None, list[str]]:
    """Prefer WYSIWYG body_json; else wrap body_ko. None = leave existing body untouched."""
    has_json = bool((form.get("body_json") or form.get("body_json") or "").strip())
    has_count = (form.get("body_count") or "0").strip() not in ("", "0")
    has_ko = bool((form.get("body_ko") or "").strip())
    if not has_json and not has_count and not has_ko:
        # No body fields posted (overlay scalar-only) — keep existing
        if not any(k.startswith("body_") for k in form):
            return None, []
    body_blocks, body_notes = places.place_body_from_form(form, files)
    if body_blocks:
        return body_blocks, body_notes
    ko = (form.get("body_ko") or "").strip()
    if not ko:
        if has_json or has_count:
            return [], body_notes
        return None, body_notes
    return [{"type": "text", "ko": ko, "en": "", "ja": ""}], body_notes


ADMIN_BOOTSTRAP = """
<script>
(function(){
  try {
    var q = new URLSearchParams(location.search);
    if (q.get('admin') === '1') {
      localStorage.setItem('guideAdmin','1');
      document.cookie = 'guideAdmin=1; path=/; SameSite=Lax';
    }
    if (localStorage.getItem('guideAdmin') === '1' || q.get('admin') === '1') {
      var l = document.createElement('link');
      l.rel = 'stylesheet';
      l.href = '/static/admin-overlay.css';
      document.head.appendChild(l);
      var s = document.createElement('script');
      s.src = '/static/admin-overlay.js';
      s.defer = true;
      (document.body || document.documentElement).appendChild(s);
    }
  } catch (e) {}
})();
</script>
"""

def render_dish_primary_fields(texts: dict[str, dict[str, str]] | None = None) -> str:
    texts = texts or {lang: {"title": "", "desc": "", "about": ""} for lang in ("ko", "en", "ja")}
    ko = texts.get("ko") or {}
    return (
        '<div class="field field--hero">'
        "<label>한국어 이름</label>"
        f'<input class="input-hero" type="text" name="title_ko" value="{h(ko.get("title", ""))}" '
        'required placeholder="예: 떡볶이">'
        "</div>"
        '<div class="field">'
        "<label>짧은 소개 (카드에 보여요)</label>"
        f'<input type="text" name="desc_ko" value="{h(ko.get("desc", ""))}" '
        'placeholder="한 줄로 짧게">'
        "</div>"
        '<div class="field">'
        "<label>자세한 설명</label>"
        f'<textarea name="about_ko" rows="5" placeholder="이 음식에 대해 편하게 적어 주세요">'
        f'{h(ko.get("about", ""))}</textarea>'
        "</div>"
    )


def render_dish_lang_fields(texts: dict[str, dict[str, str]] | None = None) -> str:
    """Korean-only primary fields. EN/JA are filled on save via auto-translate."""
    return render_dish_primary_fields(texts)


def render_shop_primary_fields(
    texts: dict[str, dict[str, str]] | None = None,
    *,
    place_url: str = "",
) -> str:
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
    ko = texts.get("ko") or {}
    tip_hiddens = "".join(
        f'<input type="hidden" name="tip_{lang}" value="{h((texts.get(lang) or {}).get("tip", ""))}">'
        for lang in ("ko", "en", "ja")
    )
    return (
        tip_hiddens
        + '<div class="field field--hero">'
        "<label>가게 이름 (한국어)</label>"
        f'<input class="input-hero" type="text" name="name_ko" value="{h(ko.get("name", ""))}" '
        'required placeholder="예: 신당동 떡볶이">'
        "</div>"
        '<div class="field field--hero">'
        "<label>가게 링크 (Google Maps / 네이버 플레이스)</label>"
        f'<input class="input-hero" type="text" name="place_url" value="{h(place_url)}" '
        'inputmode="url" autocomplete="url" '
        'placeholder="https://maps.app.goo.gl/… 또는 https://naver.me/…">'
        '<span class="hint">'
        "링크가 있으면 공개 페이지에 지도 임베드를 우선 보여 줍니다. "
        "없을 때만 상호 사진·본문이 메인 비주얼이 됩니다. "
        "(브라우저 URL 검사로 등록이 막히지 않도록 일반 텍스트 입력입니다.)"
        "</span>"
        "</div>"
        '<div class="meta-grid">'
        '<div class="field"><label>주소 · 위치</label>'
        f'<input type="text" name="location_ko" value="{h(ko.get("location", ""))}" '
        'placeholder="예: 서울 중구 …"></div>'
        '<div class="field"><label>가격</label>'
        f'<input type="text" name="price_ko" value="{h(ko.get("price", ""))}" '
        'placeholder="예: 1인 8,000원~"></div>'
        '<div class="field"><label>대표 메뉴</label>'
        f'<input type="text" name="menu_ko" value="{h(ko.get("menu", ""))}" '
        'placeholder="예: 즉석 떡볶이"></div>'
        '<div class="field"><label>짧은 카드 소개</label>'
        f'<input type="text" name="about_ko" value="{h(ko.get("about", ""))}" '
        'placeholder="목록 카드에 보이는 한 줄"></div>'
        "</div>"
    )


def render_shop_lang_fields(
    texts: dict[str, dict[str, str]] | None = None,
    *,
    place_url: str = "",
) -> str:
    """Korean-only primary fields. EN/JA are filled on save via auto-translate."""
    return render_shop_primary_fields(texts, place_url=place_url)


def render_list_filters(
    *,
    placeholder: str = "이름으로 찾아보세요…",
    chips_html: str = "",
    select_html: str = "",
) -> str:
    chips = (
        f'<div class="list-filter-chips" data-filter-chips>{chips_html}</div>'
        if chips_html
        else ""
    )
    select = (
        f'<label class="list-filter-select">{select_html}</label>'
        if select_html
        else ""
    )
    return f"""
    <div class="list-filters" data-list-filters>
      <label class="list-search">
        <span class="sr-only">검색</span>
        <input type="search" data-list-search placeholder="{h(placeholder)}" autocomplete="off">
      </label>
      {select}
      {chips}
      <p class="list-filter-empty muted" data-list-empty hidden>찾는 글이 없어요. 검색어를 바꿔 보세요.</p>
    </div>
    """


def render_body_editor(
    blocks: list | None = None,
    *,
    shop_slug: str = "",
    field_prefix: str = "body",
    legend: str = "내용",
    hint_extra: str = "",
    image_hint: str = "",
) -> str:
    blocks = list(blocks or [])
    seed_json = json.dumps(blocks, ensure_ascii=False).replace("</", "<\\/")
    prefix = (field_prefix or "body").strip() or "body"
    _ = shop_slug
    _ = image_hint
    extra = f" {hint_extra}" if hint_extra else ""
    return f"""
    <fieldset class="fieldset highlight body-post-editor" data-body-editor data-body-prefix="{h(prefix)}" data-body-ko-only="1">
      <legend>{h(legend)}</legend>
      <p class="muted body-post-lead">한국어로 쓰세요. 저장하면 자동 번역됩니다.{extra}</p>
      <input type="hidden" name="{h(prefix)}_count" value="{len(blocks)}" data-body-count>
      <input type="hidden" name="{h(prefix)}_json" value="" data-body-json>
      <script type="application/json" data-body-seed>{seed_json}</script>
      <input type="file" accept=".jpg,.jpeg,.png,.webp,image/*" data-body-pick-image hidden>
      <div class="body-file-host" data-body-file-host hidden></div>
      <div class="body-quill-shell" data-body-quill-shell="ko">
        <p class="muted body-quill-fallback">글쓰기 창을 불러오는 중…</p>
      </div>
    </fieldset>
    """


def render_child_shops_readonly(kind: str, dish_slug: str) -> str:
    children = content.list_child_shops(kind, dish_slug)
    if not children:
        return (
            '<section class="related-box">'
            "<h2>이 음식 아래 가게</h2>"
            + empty_state(
                "아직 연결된 가게가 없어요",
                "새 가게를 등록할 때 이 음식을 골라 주세요.",
                "/shop/new",
                "새 가게 등록",
            )
            + "</section>"
        )
    rows = []
    for slug, name in children:
        rows.append(
            f'<a class="chip-link" href="/shop/edit?slug={h(slug)}">{h(name)}</a>'
        )
    return (
        '<section class="related-box">'
        "<h2>이 음식 아래 가게</h2>"
        f'<div class="chip-row">{"".join(rows)}</div>'
        "</section>"
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
    cta = "다른 사진으로 바꾸기" if has_file else "사진 넣기"
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
            hint = "지금 올라간 사진이에요"
        else:
            preview = '<span class="missing">업로드하면 이 경로에 저장됩니다</span>'
            hint = "아직 사진이 없어요"
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
        "사진을 클릭해서 올려 주세요 · JPG / PNG / WebP · 최대 8MB</p>"
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
      <legend>메뉴 사진 (여러 장)</legend>
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

            if path == "/" or path == "/admin" or path == "/cms":
                # Primary admin = CMS (sidebar, tips tabs, KO editors).
                # Viewer overlay is optional at /viewer.
                self._send(200, self.page_home())
            elif path == "/viewer":
                self._redirect("/index.html?admin=1")
                return
            elif path.startswith("/static/"):
                rel = path[len("/static/") :]
                ctype = "application/octet-stream"
                lower = rel.lower()
                if lower.endswith(".css"):
                    ctype = "text/css; charset=utf-8"
                elif lower.endswith(".js"):
                    ctype = "application/javascript; charset=utf-8"
                elif lower.endswith(".map"):
                    ctype = "application/json; charset=utf-8"
                elif lower.endswith(".woff2"):
                    ctype = "font/woff2"
                elif lower.endswith(".png"):
                    ctype = "image/png"
                elif lower.endswith(".svg"):
                    ctype = "image/svg+xml"
                self._serve_static(rel, ctype)
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
            elif path == "/places":
                self._send(200, self.page_places())
            elif path == "/place/edit":
                slug = (qs.get("slug") or [""])[0]
                self._send(200, self.page_place_edit(slug))
            elif path == "/place/new":
                self._send(200, self.page_place_new())
            elif path == "/place/delete":
                slug = (qs.get("slug") or [""])[0]
                self._send(200, self.page_place_delete(slug))
            elif path == "/api/places":
                self._send_json({"ok": True, "items": [
                    {
                        "slug": p.slug,
                        "name": p.name,
                        "region": p.region,
                        "desc": p.desc,
                        "address": p.address,
                        "href": f"/pages/transportation/places/{p.slug}/index.html?admin=1",
                    }
                    for p in places.list_places()
                ]})
            elif path == "/api/places/get":
                slug = (qs.get("slug") or [""])[0]
                self._send_json({"ok": True, **places.get_place(slug)})
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
            elif path == "/tools/migrate-body":
                self._send(200, self.page_migrate_body())
            elif path.startswith("/media/"):
                self._serve_media(path)
            elif path.startswith("/preview/"):
                self._serve_preview(path)
            else:
                if self._try_serve_site(path, qs):
                    return
                self._send(
                    404,
                    layout(
                        "404",
                        "<h1>페이지를 찾을 수 없어요</h1>"
                        "<p class='page-lead'><a class='btn secondary' href='/cms'>고급 관리</a></p>",
                        nav_active="/cms",
                        crumbs=[("/cms", "고급 관리"), ("", "404")],
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


    def _serve_preview(self, path: str) -> None:
        """Serve a site HTML file for local preview (same-origin under admin)."""
        rel = path[len("/preview/") :].lstrip("/")
        if not rel or ".." in rel.split("/"):
            self.send_error(404, "Not Found")
            return
        file_path = (ROOT / rel).resolve()
        if not str(file_path).startswith(str(ROOT.resolve())) or not file_path.is_file():
            self.send_error(404, "Not Found")
            return
        data = file_path.read_bytes()
        ctype = "text/html; charset=utf-8"
        if file_path.suffix.lower() == ".css":
            ctype = "text/css; charset=utf-8"
        elif file_path.suffix.lower() == ".js":
            ctype = "application/javascript; charset=utf-8"
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
            try:
                form_data = self._read_form()
            except ValueError as exc:
                self._send(
                    200,
                    layout(
                        "업로드 오류",
                        "<h1>요청을 읽지 못했어요</h1>"
                        f"<p class='page-lead'>{h(exc)}</p>"
                        "<p>사진이 8MB를 넘거나, 형식이 JPG/PNG/WebP가 아니면 실패할 수 있습니다.</p>"
                        "<p><a class='btn secondary' href='javascript:history.back()'>뒤로</a> "
                        "<a class='btn' href='/'>대시보드</a></p>",
                        flash=str(exc),
                        flash_error=True,
                        nav_active="/",
                        crumbs=[("/", "대시보드"), ("", "업로드 오류")],
                    ),
                )
                return
            form = form_data.fields
            files = form_data.files


            if path in ("/api/places/save", "/place/save"):
                texts = place_texts_from_form(form)
                body_blocks, body_notes = body_blocks_from_place_form(form, files)
                force_tr = form.get("force_translate") == "1"
                notes, tr_status = places.save_place(
                    form.get("slug", ""),
                    texts,
                    region=form.get("region", "seoul"),
                    place_type=form.get("place_type", "city"),
                    body=body_blocks,
                    force_translate=force_tr,
                )
                notes.extend(body_notes)
                notes = refresh_public_assets(notes)
                if path.startswith("/api/"):
                    self._send_json({
                        "ok": True,
                        "message": save_ok_message("저장됨"),
                        "notes": notes,
                    })
                    return
                self._redirect(
                    f"/place/edit?slug={content.validate_slug(form.get('slug',''))}",
                    flash=save_flash(save_ok_message("저장됨"), notes, tr_status),
                )
                return

            if path in ("/api/places/create", "/place/create"):
                texts = place_texts_from_form(form)
                body_blocks, body_notes = body_blocks_from_place_form(form, files)
                notes, tr_status = places.create_place(
                    form.get("slug", ""),
                    texts,
                    region=form.get("region", "seoul"),
                    place_type=form.get("place_type", "city"),
                    body=body_blocks,
                )
                notes.extend(body_notes)
                notes = refresh_public_assets(notes)
                slug = content.validate_slug(form["slug"])
                if path.startswith("/api/"):
                    self._send_json({
                        "ok": True,
                        "message": save_ok_message("새 명소를 만들었어요"),
                        "slug": slug,
                        "href": f"/pages/transportation/places/{slug}/index.html?admin=1",
                        "notes": notes,
                    })
                    return
                self._redirect(
                    f"/place/edit?slug={slug}",
                    flash=save_flash(
                        save_ok_message("새 명소를 만들었어요"), notes, tr_status
                    ),
                )
                return

            if path in ("/api/places/delete", "/place/delete"):
                notes = places.delete_place(
                    form.get("slug", ""),
                    delete_files=form.get("delete_files", "1") != "0",
                )
                notes = refresh_public_assets(notes)
                if path.startswith("/api/"):
                    self._send_json({
                        "ok": True,
                        "message": save_ok_message("삭제했어요"),
                        "notes": notes,
                    })
                    return
                self._redirect(
                    "/places",
                    flash=friendly_flash(save_ok_message("삭제했어요"), notes),
                )
                return

            if path == "/dish/save":
                kind = form.get("kind", "meals")
                texts = dish_texts_from_form(form)
                force_tr = form.get("force_translate") == "1"
                notes, tr_status = content.save_dish_fields(
                    kind,
                    form.get("slug", ""),
                    texts,
                    force_translate=force_tr,
                )
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
                upload_notes = save_uploads_for_targets(
                    dish_image_targets(slug, kind), files
                )
                notes.extend(upload_notes or ["이미지: 새로 올린 파일 없음 (기존 유지)"])
                notes = refresh_public_assets(notes)
                self._redirect(
                    f"/dish/edit?kind={kind}&slug={slug}",
                    flash=save_flash(save_ok_message("저장됨"), notes, tr_status),
                )
                return

            if path == "/dish/create":
                kind = form.get("kind", "meals")
                texts = dish_texts_from_form(form)
                notes, tr_status = content.create_dish(
                    kind,
                    form.get("slug", ""),
                    texts,
                    form.get("emoji", "").strip() or "🍽️",
                )
                slug = content.validate_slug(form["slug"])
                upload_notes = save_uploads_for_targets(
                    dish_image_targets(slug, kind), files
                )
                notes.extend(upload_notes or ["이미지: 업로드 없음 — 수정 화면에서 올릴 수 있습니다"])
                notes = refresh_public_assets(notes)
                self._redirect(
                    f"/dish/edit?kind={kind}&slug={slug}",
                    flash=save_flash(
                        save_ok_message("새 글을 만들었어요"), notes, tr_status
                    ),
                )
                return

            if path == "/dish/delete":
                notes = content.delete_dish(
                    form.get("kind", "meals"),
                    form.get("slug", ""),
                    delete_images=form.get("delete_images") == "1",
                )
                notes = refresh_public_assets(notes)
                self._redirect(
                    f"/dishes?kind={form.get('kind','meals')}",
                    flash=friendly_flash(save_ok_message("삭제했어요"), notes),
                )
                return

            if path == "/shop/save":
                slug = form.get("slug", "")
                texts = shop_texts_from_form(form)
                parent = form.get("parent", "")
                if "|" not in parent:
                    raise ValueError("부모 음식을 선택하세요.")
                kind, dish_slug = parent.split("|", 1)
                force_tr = form.get("force_translate") == "1"
                body_blocks, body_notes = body_from_form(
                    form,
                    files=files,
                    kind=kind,
                    dish_slug=dish_slug,
                    shop_slug=slug,
                )
                notes, tr_status = content.save_shop_fields(
                    slug,
                    texts,
                    regenerate_maps=form.get("regen_maps") == "1",
                    body=body_blocks,
                    force_translate=force_tr,
                    place_url=form.get("place_url", ""),
                    fetch_preview=form.get("fetch_preview") == "1",
                )
                notes.extend(body_notes)
                if form.get("new_slug", "").strip() and form.get("new_slug") != slug:
                    notes.extend(content.rename_shop(slug, form.get("new_slug", "")))
                    slug = content.validate_slug(form["new_slug"])
                notes.extend(content.set_shop_parent(slug, kind, dish_slug))
                upload_notes = save_uploads_for_targets(
                    shop_image_targets(kind, dish_slug, slug),
                    files,
                )
                notes.extend(upload_notes or ["상호 이미지: 새로 올린 파일 없음 (기존 유지)"])
                menu_uploads = form_data.getfiles("menu_images")
                if menu_uploads:
                    notes.extend(append_menu_uploads(kind, dish_slug, slug, menu_uploads))
                    notes.extend(sync_shop_page_menu_gallery(kind, dish_slug, slug))
                notes.extend(sync_shop_page_body(kind, dish_slug, slug))
                notes.extend(sync_shop_page_visual(kind, dish_slug, slug))
                notes = refresh_public_assets(notes)
                self._redirect(
                    f"/shop/edit?slug={slug}",
                    flash=save_flash(save_ok_message("저장됨"), notes, tr_status),
                )
                return

            if path == "/shop/create":
                parent = form.get("parent", "")
                if "|" not in parent:
                    raise ValueError("부모 음식을 선택하세요.")
                kind, dish_slug = parent.split("|", 1)
                texts = shop_texts_from_form(form)
                slug_raw = form.get("slug", "")
                slug = content.validate_slug(slug_raw)
                body_blocks, body_notes = body_from_form(
                    form,
                    files=files,
                    kind=kind,
                    dish_slug=dish_slug,
                    shop_slug=slug,
                )
                notes, tr_status = content.create_shop(
                    kind,
                    dish_slug,
                    slug_raw,
                    texts,
                    body=body_blocks,
                    place_url=form.get("place_url", ""),
                    fetch_preview=form.get("fetch_preview") == "1",
                )
                notes.extend(body_notes)
                upload_notes = save_uploads_for_targets(
                    shop_image_targets(kind, dish_slug, slug), files
                )
                notes.extend(
                    upload_notes
                    or ["상호 이미지: 업로드 없음 — 수정 화면에서 올릴 수 있습니다"]
                )
                menu_uploads = form_data.getfiles("menu_images")
                if menu_uploads:
                    notes.extend(append_menu_uploads(kind, dish_slug, slug, menu_uploads))
                    notes.extend(sync_shop_page_menu_gallery(kind, dish_slug, slug))
                notes.extend(sync_shop_page_body(kind, dish_slug, slug))
                notes.extend(sync_shop_page_visual(kind, dish_slug, slug))
                notes = refresh_public_assets(notes)
                self._redirect(
                    f"/shop/edit?slug={slug}",
                    flash=save_flash(
                        save_ok_message("새 가게를 등록했어요"), notes, tr_status
                    ),
                )
                return

            if path == "/shop/delete":
                notes = content.delete_shop(
                    form.get("slug", ""),
                    delete_images=form.get("delete_images") == "1",
                )
                notes = refresh_public_assets(notes)
                self._redirect(
                    "/shops",
                    flash=friendly_flash(save_ok_message("삭제했어요"), notes),
                )
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
                notes = refresh_public_assets(notes)
                self._redirect(
                    f"/shop/edit?slug={slug}",
                    flash=friendly_flash(save_ok_message("사진을 지웠어요"), notes),
                )
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
                notes = refresh_public_assets(notes)
                self._redirect(
                    f"/shop/edit?slug={slug}",
                    flash=friendly_flash(save_ok_message("순서를 바꿨어요"), notes),
                )
                return

            if path == "/section/save":
                from lib.translate import BatchStatus, fill_body_blocks

                sid = form.get("section_id", "")
                sec = sections.get_section(sid)
                force_tr = form.get("force_translate") == "1"
                keys = form_data.getlist("keys")
                updates: dict[str, dict[str, str]] = {}
                for key in keys:
                    updates[key] = {
                        "ko": form.get(f"v_{key}_ko", ""),
                        "en": form.get(f"v_{key}_en", ""),
                        "ja": form.get(f"v_{key}_ja", ""),
                    }
                tr_status = BatchStatus()
                if updates:
                    notes, tr_status = sections.save_entry_texts(
                        sec, updates, force_translate=force_tr
                    )
                else:
                    notes = []
                group = form.get("group", "")
                # Freeform body slots (optional)
                body_keys = form_data.getlist("body_keys")
                if body_keys:
                    from lib import i18n_store

                    bundle = i18n_store.load_all()
                    for bkey in body_keys:
                        slot_folder = form.get(f"body_folder_{bkey}", "")
                        slot_slug = form.get(f"body_slug_{bkey}", "")
                        blocks, body_notes = body_from_form(
                            form,
                            files=files,
                            field_prefix=bkey,
                            section_folder=slot_folder,
                            image_slug=slot_slug,
                        )
                        notes.extend(body_notes)
                        old_blocks = content_body.get_body_at(
                            sec.root_key, bkey, bundle=bundle
                        )
                        blocks = fill_body_blocks(
                            blocks,
                            old_blocks=old_blocks,
                            force=force_tr,
                            status=tr_status,
                        )
                        notes.extend(
                            content_body.write_body_at(
                                sec.root_key,
                                bkey,
                                blocks,
                                bundle=bundle,
                                persist=False,
                            )
                        )
                    i18n_store.save_all(bundle)
                    notes.append(i18n_store.build_bundle())
                notes = refresh_public_assets(notes)
                self._redirect(
                    f"/section?id={sid}",
                    flash=save_flash(save_ok_message("저장됨"), notes, tr_status),
                    group=group,
                )
                return

            if path == "/section/add":
                self._redirect(
                    "/",
                    flash="키 추가 기능은 더 이상 쓰지 않습니다. 글 목록에서 본문을 수정하세요.",
                    flash_error=True,
                )
                return

            if path == "/section/delete":
                self._redirect(
                    "/",
                    flash="키 삭제 기능은 더 이상 쓰지 않습니다.",
                    flash_error=True,
                )
                return

            if path == "/phrase/save":
                cat = form.get("cat", "daily")
                pid = form.get("id", "")
                is_new = form.get("is_new") == "1"
                force_tr = form.get("force_translate") == "1"
                notes, tr_status = sections.save_phrase_item(
                    cat,
                    pid,
                    {
                        "ko": form.get("ko", ""),
                        "rom": form.get("rom", ""),
                        "en": form.get("en", ""),
                        "ja": form.get("ja", ""),
                    },
                    is_new=is_new,
                    force_translate=force_tr,
                )
                notes = refresh_public_assets(notes)
                self._redirect(
                    f"/phrase/edit?cat={cat}&id={pid}",
                    flash=save_flash(save_ok_message("저장됨"), notes, tr_status),
                )
                return

            if path == "/phrase/delete":
                cat = form.get("cat", "daily")
                notes = sections.delete_phrase_item(cat, form.get("id", ""))
                notes = refresh_public_assets(notes)
                self._redirect(
                    f"/phrases?cat={cat}",
                    flash=friendly_flash(save_ok_message("삭제했어요"), notes),
                )
                return

            if path == "/version/run":
                summary = bump_asset_version()
                self._redirect(
                    "/version",
                    flash=friendly_flash(
                        save_ok_message("사이트 새로고침을 끝냈어요"),
                        [
                            f"버전 {summary['version']}",
                            f"HTML {summary['files_updated']}/{summary['files_scanned']}개 갱신 "
                            f"(검증 {summary['files_ok']}개)",
                        ],
                    ),
                )
                return

            if path == "/tools/patch-menus/run":
                notes = patch_all_shop_menu_galleries()
                notes = refresh_public_assets(notes)
                self._redirect(
                    "/tools/patch-menus",
                    flash=friendly_flash(save_ok_message("메뉴 정리를 끝냈어요"), notes),
                )
                return

            if path == "/tools/migrate-body/run":
                force = form.get("force") == "1"
                target = form.get("target", "shops")
                if target == "sections":
                    notes = content_body.migrate_all_section_bodies(force=force)
                else:
                    notes = content.migrate_all_shop_bodies(force=force)
                notes = refresh_public_assets(notes)
                self._redirect(
                    "/tools/migrate-body",
                    flash=friendly_flash(save_ok_message("본문 정리를 끝냈어요"), notes),
                )
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



    def _send_json(self, payload: dict, status: int = 200) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _try_serve_site(self, path: str, qs: dict) -> bool:
        """Serve guidebook static files from project root; inject admin bootstrap into HTML."""
        rel = path.lstrip("/")
        if not rel:
            rel = "index.html"
        if ".." in rel.split("/"):
            return False
        file_path = (ROOT / rel).resolve()
        root = ROOT.resolve()
        if not str(file_path).startswith(str(root)) or not file_path.is_file():
            # directory → index.html
            if (ROOT / rel).is_dir():
                file_path = (ROOT / rel / "index.html").resolve()
                if not file_path.is_file():
                    return False
            else:
                return False
        # Never expose tool/ internals as site (except already handled /static)
        try:
            rel_posix = file_path.relative_to(root).as_posix()
        except ValueError:
            return False
        if rel_posix.startswith("tool/") and not rel_posix.startswith("tool/static/"):
            return False

        data = file_path.read_bytes()
        suffix = file_path.suffix.lower()
        ctype = {
            ".html": "text/html; charset=utf-8",
            ".htm": "text/html; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".js": "application/javascript; charset=utf-8",
            ".json": "application/json; charset=utf-8",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
            ".gif": "image/gif",
            ".svg": "image/svg+xml",
            ".ico": "image/x-icon",
            ".mp3": "audio/mpeg",
            ".woff2": "font/woff2",
            ".map": "application/json",
        }.get(suffix, "application/octet-stream")

        if suffix in (".html", ".htm"):
            try:
                html_text = data.decode("utf-8")
            except UnicodeDecodeError:
                html_text = data.decode("utf-8", errors="replace")
            if "admin-overlay.js" not in html_text:
                if "</body>" in html_text.lower():
                    # case-sensitive safe replace once
                    idx = html_text.lower().rfind("</body>")
                    html_text = html_text[:idx] + ADMIN_BOOTSTRAP + html_text[idx:]
                else:
                    html_text += ADMIN_BOOTSTRAP
            data = html_text.encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)
        return True

    def page_places(self) -> str:
        rows = []
        for p in places.list_places():
            rows.append(
                render_list_row(
                    href=f"/place/edit?slug={p.slug}",
                    title=p.name,
                    subtitle=f"{p.region} · {p.desc[:80]}",
                    thumb_rel="",
                    filter_text=f"{p.slug} {p.name} {p.region} {p.desc}",
                )
            )
        list_html = (
            f'<div class="list-board">{"".join(rows)}</div>'
            if rows
            else empty_state("아직 명소가 없어요", "명소 지도에 소개할 장소를 추가하세요.", "/place/new", "새 명소")
        )
        body = f"""
        <div class="toolbar">
          <div>
            <h1>대표 명소</h1>
            <p class="page-lead"><a href="/pages/transportation/index.html?admin=1">사이트에서 바로 수정</a></p>
          </div>
          <a class="btn btn-lg" href="/place/new">새 명소</a>
        </div>
        {list_html}
        """
        return layout(
            "대표 명소",
            body,
            flash=self._pop_flash(),
            flash_error=self._flash_error(),
            nav_active="/places",
            crumbs=[("/places", "대표 명소")],
            preview_href="/pages/transportation/index.html?admin=1",
        )

    def page_place_new(self) -> str:
        body = f"""
        <h1>새 명소</h1>
        <form class="card editor-card" method="post" action="/place/create" enctype="multipart/form-data">
          <div class="field"><label>슬러그 (영문)</label>
            <input type="text" name="slug" required pattern="[a-z0-9]+(?:-[a-z0-9]+)*" placeholder="예: myeongdong"></div>
          <div class="field"><label>지역</label>
            <select name="region">{_region_select("seoul")}</select></div>
          <div class="field"><label>지도 핀 유형</label>
            <select name="place_type">{_type_select("city")}</select></div>
          <div class="field field--hero"><label>한국어 이름</label>
            <input class="input-hero" type="text" name="name_ko" required></div>
          <div class="field"><label>짧은 소개</label>
            <input type="text" name="desc_ko"></div>
          <div class="field"><label>지도 주소 / 장소명</label>
            <input type="text" name="address_ko" placeholder="Google 지도 검색에 쓰입니다"></div>
          <div class="field"><label>가는 방법</label>
            <textarea name="how_ko" rows="3"></textarea></div>
          {render_body_editor([], legend="내용")}
          {render_expert(render_force_translate_check(), summary="전문가용 · 번역 다시 하기")}
          {render_editor_actions(back_href="/places")}
        </form>
        """
        return layout(
            "새 명소",
            body,
            nav_active="/places",
            crumbs=[("/places", "대표 명소"), ("", "새 명소")],
        )

    def page_place_edit(self, slug: str) -> str:
        data = places.get_place(slug)
        ko = (data.get("texts") or {}).get("ko") or {}
        region = data.get("region") or "seoul"
        place_type = data.get("place_type") or "city"
        preview = f"/pages/transportation/places/{slug}/index.html?admin=1"
        body = f"""
        <h1>{h(ko.get("name") or slug)}</h1>
        <p class="page-lead"><a href="{h(preview)}">사이트에서 보기·수정</a></p>
        <form class="card editor-card" method="post" action="/place/save" enctype="multipart/form-data">
          <input type="hidden" name="slug" value="{h(slug)}">
          <div class="field"><label>지역</label><select name="region">{_region_select(region)}</select></div>
          <div class="field"><label>지도 핀 유형</label><select name="place_type">{_type_select(place_type)}</select></div>
          <div class="field field--hero"><label>한국어 이름</label>
            <input class="input-hero" type="text" name="name_ko" value="{h(ko.get("name",""))}" required></div>
          <div class="field"><label>짧은 소개</label>
            <input type="text" name="desc_ko" value="{h(ko.get("desc",""))}"></div>
          <div class="field"><label>지도 주소 / 장소명</label>
            <input type="text" name="address_ko" value="{h(ko.get("address",""))}"></div>
          <div class="field"><label>가는 방법</label>
            <textarea name="how_ko" rows="3">{h(ko.get("how",""))}</textarea></div>
          {render_body_editor(data.get("body") or [], legend="내용")}
          {render_expert(render_force_translate_check(), summary="전문가용 · 번역 다시 하기")}
          {render_editor_actions(back_href="/places", delete_href=f"/place/delete?slug={h(slug)}")}
        </form>
        """
        return layout(
            f"명소 · {ko.get('name') or slug}",
            body,
            flash=self._pop_flash(),
            flash_error=self._flash_error(),
            nav_active="/places",
            crumbs=[("/places", "대표 명소"), ("", ko.get("name") or slug)],
            preview_href=preview,
        )

    def page_place_delete(self, slug: str) -> str:
        data = places.get_place(slug)
        name = ((data.get("texts") or {}).get("ko") or {}).get("name") or slug
        body = f"""
        <h1>명소 삭제</h1>
        <p class="page-lead">「{h(name)}」({h(slug)})을(를) 삭제할까요?</p>
        <form method="post" action="/place/delete" class="card">
          <input type="hidden" name="slug" value="{h(slug)}">
          <label class="check-row"><input type="checkbox" name="delete_files" value="1" checked>
            <span>페이지 폴더(media 포함)도 삭제</span></label>
          <div class="row" style="margin-top:1rem">
            <button type="submit" class="danger">삭제</button>
            <a class="btn secondary" href="/place/edit?slug={h(slug)}">취소</a>
          </div>
        </form>
        """
        return layout(
            "명소 삭제",
            body,
            nav_active="/places",
            crumbs=[("/places", "대표 명소"), ("", "삭제")],
        )


    # ---------- pages ----------

    def page_home(self) -> str:
        try:
            ver = read_version()
        except SystemExit:
            ver = "(없음)"
        boards: dict[str, list[str]] = {g: [] for g in sections.BOARD_ORDER}
        for c in sections.dashboard_cards():
            count = f'<span class="count">{h(c.count)}</span>' if c.count else ""
            is_tool = c.group == "설정"
            card = (
                f'<a class="dash-card{" tools" if is_tool else ""}" href="{h(c.href)}">'
                f'<div class="dash-card-top"><strong>{h(c.title)}</strong>{count}</div>'
                f"<p>{h(c.desc)}</p></a>"
            )
            boards.setdefault(c.group or "기타", []).append(card)
        sections_html = []
        for group in sections.BOARD_ORDER:
            cards = boards.get(group) or []
            if not cards:
                continue
            sections_html.append(
                f'<section class="dash-section">'
                f'<div class="dash-section-head"><h2>{h(group)}</h2></div>'
                f'<div class="dash-grid">{"".join(cards)}</div></section>'
            )
        body = f"""
        <div class="dash-hero">
          <h1>가이드북 관리</h1>
          <p class="page-lead">왼쪽 메뉴에서 게시판을 고른 뒤 글을 수정하세요.
            <a href="/viewer">사이트 화면에서 보기</a>도 가능합니다.</p>
        </div>
        {"".join(sections_html)}
        <p class="dash-foot muted">글 저장 시 캐시 버전이 자동으로 올라갑니다. 화면이 안 바뀌면 <strong>Ctrl+F5</strong> 또는
          <a href="/viewer">뷰어</a>를 다시 여세요. · 현재 버전 {h(ver)}</p>
        """
        return layout(
            "대시보드",
            body,
            flash=self._pop_flash(),
            flash_error=self._flash_error(),
            nav_active="/",
            crumbs=[("", "대시보드")],
        )

    def page_dishes(self, kind: str) -> str:
        if kind not in ("meals", "desserts"):
            kind = "meals"
        label = "식사" if kind == "meals" else "디저트"
        rows = []
        for d in content.list_dishes(kind):
            cover = dish_cover_path(d.slug)
            thumb = rel_posix(cover) if cover.is_file() else ""
            rows.append(
                render_list_row(
                    href=f"/dish/edit?kind={kind}&slug={d.slug}",
                    title=d.title,
                    subtitle=d.desc[:80] + ("…" if len(d.desc) > 80 else ""),
                    thumb_rel=thumb,
                    filter_text=f"{d.slug} {d.title} {d.desc}",
                )
            )
        chips = (
            f'<a class="{"is-active" if kind == "meals" else ""}" '
            f'data-filter-chip href="/dishes?kind=meals">식사</a>'
            f'<a class="{"is-active" if kind == "desserts" else ""}" '
            f'data-filter-chip href="/dishes?kind=desserts">디저트</a>'
        )
        filters = render_list_filters(
            placeholder="음식 이름으로 찾아보세요…",
            chips_html=chips,
        )
        list_html = (
            f'<div class="list-board">{"".join(rows)}</div>'
            if rows
            else empty_state(
                f"아직 {label} 글이 없어요",
                "새 글을 추가해 가이드북을 채워 보세요.",
                f"/dish/new?kind={kind}",
                "새 글 추가",
            )
        )
        body = f"""
        <div class="toolbar">
          <div>
            <h1>{label}</h1>
          </div>
          <a class="btn btn-lg" href="/dish/new?kind={h(kind)}">새 글 추가</a>
        </div>
        {filters}
        {list_html}
        """
        return layout(
            label,
            body,
            flash=self._pop_flash(),
            flash_error=self._flash_error(),
            nav_active=f"/dishes?kind={kind}",
            crumbs=[(f"/dishes?kind={kind}", label)],
        )

    def page_dish_edit(self, kind: str, slug: str) -> str:
        d = content.get_dish(kind, slug)
        label = "식사" if kind == "meals" else "디저트"
        lang_html = render_dish_lang_fields(d.get("texts"))
        img_html = render_image_fields(dish_image_targets(slug, kind))
        children_html = render_child_shops_readonly(kind, slug)
        title_ko = (d.get("texts") or {}).get("ko", {}).get("title") or slug
        expert = render_expert(
            '<div class="field">'
            "<label>주소 이름 변경</label>"
            f'<input type="text" name="new_slug" value="{h(slug)}" '
            'pattern="[a-z0-9]+(-[a-z0-9]+)*" placeholder="예: tteokbokki">'
            '<span class="hint">영문 소문자·숫자·하이픈만. 바꾸면 관련 경로도 함께 맞춰요.</span>'
            "</div>"
            + render_force_translate_check()
        )
        preview = public_href(d["page"]) if d.get("page") else ""
        body = f"""
        <div class="toolbar">
          <div>
            <h1>글 수정</h1>
            <p class="page-lead">{h(title_ko)}</p>
          </div>
        </div>
        <form class="card editor-card" method="post" action="/dish/save" enctype="multipart/form-data">
          <input type="hidden" name="kind" value="{h(kind)}">
          <input type="hidden" name="slug" value="{h(slug)}">
          {lang_html}
          <fieldset class="fieldset">
            <legend>사진</legend>
            {img_html}
          </fieldset>
          {expert}
          {render_editor_actions(
                back_href=f"/dishes?kind={kind}",
                delete_href=f"/dish/delete?kind={kind}&slug={slug}",
            )}
        </form>
        {children_html}
        """
        return layout(
            f"글 수정 · {title_ko}",
            body,
            flash=self._pop_flash(),
            flash_error=self._flash_error(),
            nav_active=f"/dishes?kind={kind}",
            crumbs=[
                (f"/dishes?kind={kind}", label),
                ("", title_ko),
            ],
            preview_href=preview,
        )

    def page_dish_new(self, kind: str) -> str:
        label = "식사" if kind == "meals" else "디저트"
        default_emoji = "🍽️" if kind == "meals" else "🍰"
        lang_html = render_dish_lang_fields()
        img_html = render_upload_zone(
            name="cover_image",
            label="대표 사진",
            hint="나중에 수정 화면에서도 올릴 수 있어요",
            preview_html='<span class="missing">선택 사항</span>',
        )
        # Slug must stay visible — required fields inside closed <details> block submit silently.
        slug_field = (
            '<div class="field field--hero">'
            "<label>주소 이름 (영문)</label>"
            '<input class="input-hero" type="text" name="slug" placeholder="예: tteokbokki" required '
            'pattern="[a-z0-9]+(-[a-z0-9]+)*" autocomplete="off">'
            '<span class="hint">페이지 주소에 쓰입니다. 영문 소문자·숫자·하이픈만.</span>'
            "</div>"
            '<div class="field">'
            "<label>목록 이모지</label>"
            f'<input type="text" name="emoji" value="{h(default_emoji)}" style="max-width:6rem">'
            "</div>"
        )
        body = f"""
        <div class="toolbar">
          <div>
            <h1>새 글</h1>
            <p class="page-lead">{h(label)} 음식 소개를 새로 올립니다.</p>
          </div>
        </div>
        <form class="card editor-card" method="post" action="/dish/create" enctype="multipart/form-data">
          <input type="hidden" name="kind" value="{h(kind)}">
          {lang_html}
          {slug_field}
          <fieldset class="fieldset">
            <legend>사진</legend>
            {img_html}
          </fieldset>
          {render_editor_actions(save_label="등록", back_href=f"/dishes?kind={kind}")}
        </form>
        """
        return layout(
            "새 글",
            body,
            nav_active=f"/dishes?kind={kind}",
            crumbs=[
                (f"/dishes?kind={kind}", label),
                ("", "새 글"),
            ],
        )

    def page_dish_delete(self, kind: str, slug: str) -> str:
        label = "식사" if kind == "meals" else "디저트"
        try:
            d = content.get_dish(kind, slug)
            title = (d.get("texts") or {}).get("ko", {}).get("title") or slug
        except Exception:  # noqa: BLE001
            title = slug
        body = f"""
        <h1>정말 삭제할까요?</h1>
        <p class="page-lead"><strong>{h(title)}</strong> 글을 목록에서 지웁니다.</p>
        <form class="card" method="post" action="/dish/delete">
          <input type="hidden" name="kind" value="{h(kind)}">
          <input type="hidden" name="slug" value="{h(slug)}">
          <label class="check-row">
            <input type="checkbox" name="delete_images" value="1">
            <span>대표 사진도 함께 삭제</span>
          </label>
          <div class="row">
            <button type="submit" class="danger">삭제</button>
            <a class="btn secondary" href="/dish/edit?kind={h(kind)}&slug={h(slug)}">취소</a>
          </div>
        </form>
        """
        return layout(
            "삭제",
            body,
            nav_active=f"/dishes?kind={kind}",
            crumbs=[
                (f"/dishes?kind={kind}", label),
                (f"/dish/edit?kind={kind}&slug={slug}", title),
                ("", "삭제"),
            ],
        )

    def page_shops(self) -> str:
        shops = content.list_shops()
        dish_labels: dict[str, str] = {}
        for kind, dish_slug, label in content.dish_options_for_select():
            dish_labels[f"{kind}|{dish_slug}"] = label
        parent_counts: dict[str, int] = {}
        for s in shops:
            key = f"{s.kind}|{s.dish_slug}"
            parent_counts[key] = parent_counts.get(key, 0) + 1
        select_opts = ['<option value="">음식 전체</option>']
        for key, count in sorted(
            parent_counts.items(), key=lambda kv: dish_labels.get(kv[0], kv[0])
        ):
            select_opts.append(
                f'<option value="{h(key)}">{h(dish_labels.get(key, key))} ({count})</option>'
            )
        rows = []
        for s in shops:
            group = f"{s.kind}|{s.dish_slug}"
            try:
                thumb_path = shop_photo_path(s.kind, s.dish_slug, s.slug)
                thumb = rel_posix(thumb_path) if thumb_path.is_file() else ""
            except Exception:  # noqa: BLE001
                thumb = ""
            rows.append(
                render_list_row(
                    href=f"/shop/edit?slug={s.slug}",
                    title=s.name,
                    subtitle=dish_labels.get(group, s.dish_slug),
                    meta=s.location[:50] + ("…" if len(s.location) > 50 else ""),
                    thumb_rel=thumb,
                    filter_text=f"{s.slug} {s.name} {s.kind} {s.dish_slug} {s.location}",
                    filter_group=group,
                )
            )
        filters = render_list_filters(
            placeholder="가게 이름·위치로 찾아보세요…",
            select_html=(
                '<span class="sr-only">음식별 보기</span>'
                '<select data-filter-select>'
                + "".join(select_opts)
                + "</select>"
            ),
        )
        list_html = (
            f'<div class="list-board">{"".join(rows)}</div>'
            if rows
            else empty_state(
                "아직 가게가 없어요",
                "음식 아래에 가게 글을 등록해 보세요.",
                "/shop/new",
                "새 가게 등록",
            )
        )
        body = f"""
        <div class="toolbar">
          <div>
            <h1>가게</h1>
          </div>
          <a class="btn btn-lg" href="/shop/new">새 가게 등록</a>
        </div>
        {filters}
        {list_html}
        """
        return layout(
            "가게",
            body,
            flash=self._pop_flash(),
            flash_error=self._flash_error(),
            nav_active="/shops",
            crumbs=[("/shops", "가게")],
        )

    def page_shop_edit(self, slug: str) -> str:
        s = content.get_shop(slug)
        lang_html = render_shop_lang_fields(
            s.get("texts"), place_url=str(s.get("placeUrl") or "")
        )
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
            img_html = '<p class="muted" style="margin:0">소속 음식을 저장한 뒤 사진을 올릴 수 있어요.</p>'
        body_html = render_body_editor(
            s.get("body") or [],
            shop_slug=slug,
            legend="추가 메모 · 본문",
            hint_extra="가게 링크가 있으면 임베드가 메인입니다. 본문은 보충 설명용이에요.",
        )
        name_ko = (s.get("texts") or {}).get("ko", {}).get("name") or slug
        expert = render_expert(
            '<div class="field">'
            "<label>주소 이름 변경</label>"
            f'<input type="text" name="new_slug" value="{h(slug)}" '
            'pattern="[a-z0-9]+(-[a-z0-9]+)*" placeholder="예: tteokbokki">'
            '<span class="hint">영문 소문자·숫자·하이픈만.</span></div>'
            '<label class="check-row">'
            '<input type="checkbox" name="regen_maps" value="1" checked>'
            "<span>저장할 때 가게 링크·주소로 지도 임베드 다시 만들기</span></label>"
            '<label class="check-row">'
            '<input type="checkbox" name="fetch_preview" value="1" checked>'
            "<span>저장할 때 링크 미리보기(제목·이미지) 가져오기</span></label>"
            + render_force_translate_check()
        )
        preview = public_href(s["page"]) if s.get("page") else ""
        body = f"""
        <div class="toolbar">
          <div>
            <h1>글 수정</h1>
            <p class="page-lead">{h(name_ko)}</p>
            <p class="note">링크 있으면 임베드 우선, 없을 때만 직접 사진·본문</p>
          </div>
        </div>
        <form class="card editor-card" id="shop-main-form" method="post" action="/shop/save" enctype="multipart/form-data">
          <input type="hidden" name="slug" value="{h(slug)}">
          <fieldset class="fieldset highlight">
            <legend>어느 음식 아래에 둘까요?</legend>
            <div class="field">
              <label>소속 음식</label>
              <select class="parent-select" name="parent" required>
                <option value="">음식을 선택하세요…</option>
                {''.join(opts)}
              </select>
            </div>
          </fieldset>
          {lang_html}
          {body_html}
          <fieldset class="fieldset">
            <legend>상호 사진 (선택 · 링크 없을 때)</legend>
            <p class="hint" style="margin-top:0">가게 링크가 있으면 공개 페이지는 지도를 먼저 보여 줍니다.</p>
            {img_html}
          </fieldset>
          {expert}
          {render_editor_actions(
                back_href="/shops",
                delete_href=f"/shop/delete?slug={slug}",
            )}
        </form>
        """
        return layout(
            f"글 수정 · {name_ko}",
            body,
            flash=self._pop_flash(),
            flash_error=self._flash_error(),
            nav_active="/shops",
            crumbs=[("/shops", "가게"), ("", name_ko)],
            preview_href=preview,
        )

    def page_shop_new(self) -> str:
        opts = []
        for kind, slug, label in content.dish_options_for_select():
            opts.append(f'<option value="{h(kind)}|{h(slug)}">{h(label)}</option>')
        lang_html = render_shop_lang_fields()
        shop_upload = render_upload_zone(
            name="shop_image",
            label="상호 사진 (선택 · 링크 없을 때)",
            hint="가게 링크가 있으면 필수가 아닙니다 · JPG/PNG/WebP · 최대 8MB",
        )
        body_html = render_body_editor(
            [],
            shop_slug="",
            legend="추가 메모 · 본문",
            hint_extra="링크가 있으면 임베드가 메인입니다. 본문은 보충 설명용이에요.",
        )
        # Slug must stay visible — required fields inside closed <details> block submit silently.
        slug_field = (
            '<div class="field field--hero">'
            "<label>주소 이름 (영문)</label>"
            '<input class="input-hero" type="text" name="slug" required '
            'pattern="[a-z0-9]+(-[a-z0-9]+)*" '
            'placeholder="예: sindang-tteokbokki" autocomplete="off">'
            '<span class="hint">페이지 주소에 쓰입니다. 영문 소문자·숫자·하이픈만.</span>'
            "</div>"
        )
        expert = render_expert(
            '<label class="check-row">'
            '<input type="checkbox" name="fetch_preview" value="1" checked>'
            "<span>등록할 때 링크 미리보기(제목·이미지) 가져오기</span></label>"
        )
        body = f"""
        <div class="toolbar">
          <div>
            <h1>새 가게 등록</h1>
            <p class="page-lead">가게 링크를 넣으면 지도 임베드가 메인 비주얼이 됩니다.</p>
            <p class="note">링크 있으면 임베드 우선, 없을 때만 직접 사진·본문</p>
          </div>
        </div>
        <form class="card editor-card" id="shop-main-form" method="post" action="/shop/create" enctype="multipart/form-data">
          <fieldset class="fieldset highlight">
            <legend>어느 음식 아래에 둘까요?</legend>
            <div class="field">
              <label>소속 음식</label>
              <select class="parent-select" name="parent" required>
                <option value="">음식을 선택하세요…</option>
                {''.join(opts)}
              </select>
            </div>
          </fieldset>
          {lang_html}
          {slug_field}
          {body_html}
          <fieldset class="fieldset">
            <legend>상호 사진 (선택)</legend>
            {shop_upload}
          </fieldset>
          {expert}
          {render_editor_actions(save_label="등록", back_href="/shops")}
        </form>
        """
        return layout(
            "새 가게",
            body,
            nav_active="/shops",
            crumbs=[("/shops", "가게"), ("", "새 가게")],
        )

    def page_shop_delete(self, slug: str) -> str:
        try:
            s = content.get_shop(slug)
            name = (s.get("texts") or {}).get("ko", {}).get("name") or slug
        except Exception:  # noqa: BLE001
            name = slug
        body = f"""
        <h1>정말 삭제할까요?</h1>
        <p class="page-lead"><strong>{h(name)}</strong> 가게 글을 지웁니다.</p>
        <form class="card" method="post" action="/shop/delete">
          <input type="hidden" name="slug" value="{h(slug)}">
          <label class="check-row">
            <input type="checkbox" name="delete_images" value="1">
            <span>사진도 함께 삭제</span>
          </label>
          <div class="row">
            <button type="submit" class="danger">삭제</button>
            <a class="btn secondary" href="/shop/edit?slug={h(slug)}">취소</a>
          </div>
        </form>
        """
        return layout(
            "삭제",
            body,
            nav_active="/shops",
            crumbs=[
                ("/shops", "가게"),
                (f"/shop/edit?slug={slug}", name),
                ("", "삭제"),
            ],
        )

    def page_section(self, section_id: str, group: str) -> str:
        sec = sections.get_section(section_id)
        keys = sections.list_section_keys(sec)
        groups = sections.group_keys(sec, keys)
        group_names = list(groups.keys())
        all_slots = content_body.slots_for_section(sec.id, "")
        post_groups = [s.group for s in all_slots if s.group]
        content_boards = (
            "beforeTrip",
            "shopping",
            "convenience",
            "souvenir",
            "fun",
            "tips",
            "apps",
            "emergency",
        )
        # Tips use category tabs on one admin page (not a card hub).
        is_tips_tabs = sec.id == "tips" and len(post_groups) > 1
        is_post_board = (
            sec.id in (
                "beforeTrip",
                "shopping",
                "apps",
                "emergency",
                "fun",
                "souvenir",
            )
            and len(post_groups) > 1
        )
        hub_edit_keys = {
            "beforeTrip": ("title", "intro"),
            "shopping": ("intro",),
            "tips": (),
            "apps": (),
            "emergency": ("title",),
        }

        def post_preview(sec_id: str, g: str) -> str:
            if sec_id == "beforeTrip" and g:
                return f"/pages/before-trip/{g}/index.html?admin=1"
            if sec_id == "shopping" and g:
                return f"/pages/shopping/{g}/index.html?admin=1"
            if sec_id == "fun" and g:
                fun_slug = {
                    "pcbang": "pcbang",
                    "noraebang": "coin-noraebang",
                    "escape": "escape-room",
                    "jjim": "jjimjilbang",
                    "manga": "manga-cafe",
                    "boardgame": "boardgame-cafe",
                    "unmanned": "unmanned-store",
                    "photobooth": "photo-booth",
                    "lotte": "lotte-world",
                    "everland": "everland",
                }.get(g, g)
                return f"/pages/fun/{fun_slug}/index.html?admin=1"
            if sec_id == "souvenir" and g:
                return f"/pages/souvenir/{g}/index.html?admin=1"
            if sec_id == "tips" and g:
                # Public tips is one page with category tabs.
                return "/pages/travel-tips/index.html?admin=1"
            if sec_id == "apps" and g:
                return f"/pages/apps/{g}/index.html?admin=1"
            if sec_id == "emergency" and g:
                return f"/pages/emergency/{g}/index.html?admin=1"
            return public_href(sec.preview_path) if sec.preview_path else ""

        def title_key_for(sec_id: str, g: str, available: list[str]) -> str:
            special = {
                ("tips", "daily"): "catDaily",
                ("tips", "restaurant"): "catRestaurant",
                ("tips", "transport"): "catTransport",
                ("apps", "kakaotalk"): "talkName",
                ("emergency", "police"): "police",
                ("emergency", "fire"): "fire",
                ("emergency", "tourist"): "tourist",
                ("emergency", "guide"): "guideTitle",
            }
            if (sec_id, g) in special and special[(sec_id, g)] in available:
                return special[(sec_id, g)]
            for cand in (f"{g}Name", f"{g}Title", f"{g}_pageTitle", g):
                if cand in available:
                    return cand
            for k in available:
                if k.endswith("Title") and not k.startswith("cat"):
                    return k
            return ""

        # Hub board: pick a post instead of stacking every editor
        if is_post_board and (not group or group not in post_groups) and group != "_공통":
            cards = []
            for slot in all_slots:
                g = slot.group or ""
                cards.append(
                    f'<a class="dash-card" href="/section?id={uq(sec.id)}&group={uq(g)}">'
                    f'<div class="dash-card-top"><strong>{h(slot.label)}</strong></div>'
                    f"<p>글 수정</p></a>"
                )
            hub_keys = list(hub_edit_keys.get(sec.id, ()))
            hub_rows = []
            for key in hub_keys:
                if key not in keys:
                    continue
                texts = sections.load_entry_texts(sec, key)
                label = "소개" if key == "intro" else ("제목" if key == "title" else sections.friendly_key_label(key))
                hub_rows.append(
                    f'<div class="entry-row">'
                    f'<input type="hidden" name="keys" value="{h(key)}">'
                    f'<label class="entry-label">{h(label)}</label>'
                    f'<div class="field" style="margin:0">'
                    f"<label>한국어</label>"
                    f'<textarea name="v_{h(key)}_ko" rows="2">{h(texts["ko"])}</textarea>'
                    f"</div></div>"
                )
            hub_form = ""
            if hub_rows:
                hub_form = f"""
                <form class="card editor-card" method="post" action="/section/save">
                  <input type="hidden" name="section_id" value="{h(sec.id)}">
                  <input type="hidden" name="group" value="_공통">
                  <fieldset class="fieldset" style="box-shadow:none;background:#fff;margin:.75rem 0 0">
                    <legend>목록 제목·소개</legend>
                    {"".join(hub_rows)}
                  </fieldset>
                  {render_editor_actions(back_href="/", back_label="대시보드로")}
                </form>
                """
            body = f"""
            <div class="toolbar">
              <div>
                <h1>{h(sec.title)}</h1>
                <p class="page-lead">카드를 눌러 글 제목과 본문만 수정합니다.</p>
              </div>
            </div>
            <div class="dash-grid" style="margin-bottom:1.25rem">{"".join(cards)}</div>
            {hub_form}
            """
            return layout(
                sec.title,
                body,
                flash=self._pop_flash(),
                flash_error=self._flash_error(),
                nav_active=f"/section?id={sec.id}",
                crumbs=[(f"/section?id={sec.id}", sec.title)],
                preview_href=public_href(sec.preview_path) if sec.preview_path else "",
            )

        # Tips: default to first category (일상생활) — tabs switch one category at a time
        if is_tips_tabs and (not group or group not in post_groups):
            group = post_groups[0] if post_groups else "daily"

        if not group or group not in groups:
            group = ""
            for gname in group_names:
                if content_body.slots_for_section(sec.id, gname):
                    group = gname
                    break
            if not group:
                group = group_names[0] if group_names else ""
        show_keys = groups.get(group, keys) if group else keys
        body_slots = content_body.slots_for_section(sec.id, group)

        group_nav = ""
        if is_tips_tabs:
            tab_btns = []
            for slot in all_slots:
                g = slot.group or ""
                active = " is-active" if g == group else ""
                tab_btns.append(
                    f'<a class="section-tab{active}" href="/section?id={uq(sec.id)}&group={uq(g)}">'
                    f"{h(slot.label)}</a>"
                )
            group_nav = (
                '<nav class="section-tabs" aria-label="팁 대분류">'
                f'{"".join(tab_btns)}</nav>'
                '<p class="page-lead" style="margin:.35rem 0 1rem">'
                "대분류 탭을 고른 뒤, 한국어 제목과 본문만 수정합니다."
                "</p>"
            )
        elif sec.group_by_prefix and len(group_names) > 1 and not is_post_board:
            opts = []
            for gname in group_names:
                if gname in ("_공통", "_기타") and not content_body.slots_for_section(
                    sec.id, gname
                ):
                    continue
                sel = " selected" if gname == group else ""
                label = sections.friendly_group_label(gname)
                opts.append(
                    f'<option value="/section?id={uq(sec.id)}&group={uq(gname)}"{sel}>'
                    f"{h(label)}</option>"
                )
            group_nav = (
                '<label class="group-select-wrap">'
                "<span>항목</span>"
                '<select class="group-select" data-nav-select>'
                f'{"".join(opts)}</select></label>'
            )
        elif is_post_board and group in post_groups:
            group_nav = (
                f'<p class="back-link" style="margin:0 0 1rem">'
                f'<a href="/section?id={uq(sec.id)}">← {h(sec.title)} 목록</a></p>'
            )

        # Content boards: Korean title (one field) + WYSIWYG only — no key wall
        title_row = ""
        legacy_rows: list[str] = []
        if sec.id in content_boards:
            # Title keys (e.g. tips.catDaily) may live in _공통; search all keys.
            tkey = title_key_for(sec.id, group, keys)
            if tkey:
                texts = sections.load_entry_texts(sec, tkey)
                title_row = (
                    f'<div class="entry-row">'
                    f'<input type="hidden" name="keys" value="{h(tkey)}">'
                    f'<label class="entry-label">제목</label>'
                    f'<div class="field" style="margin:0">'
                    f"<label>한국어</label>"
                    f'<input type="text" name="v_{h(tkey)}_ko" value="{h(texts["ko"])}" '
                    f'style="width:100%;padding:.55rem .7rem;font:inherit">'
                    f"</div></div>"
                )
        else:
            for key in show_keys:
                texts = sections.load_entry_texts(sec, key)
                label = sections.friendly_key_label(key)
                ftext = f"{key} {label} {texts['ko']}"
                legacy_rows.append(
                    f'<div class="entry-row" data-filter-item data-filter-text="{h(ftext)}">'
                    f'<input type="hidden" name="keys" value="{h(key)}">'
                    f'<label class="entry-label">{h(label)}</label>'
                    f'<div class="field" style="margin:0">'
                    f"<label>한국어</label>"
                    f'<textarea name="v_{h(key)}_ko" rows="3">{h(texts["ko"])}</textarea>'
                    f"</div></div>"
                )

        filters = (
            render_list_filters(placeholder="문구 이름으로 찾아보세요…")
            if legacy_rows
            else ""
        )
        body_editors: list[str] = []
        for slot in body_slots:
            blocks = content_body.get_body_at(sec.root_key, slot.key)
            pretty = sections.friendly_group_label(slot.label)
            body_editors.append(
                f'<input type="hidden" name="body_keys" value="{h(slot.key)}">'
                f'<input type="hidden" name="body_folder_{h(slot.key)}" value="{h(slot.image_folder)}">'
                f'<input type="hidden" name="body_slug_{h(slot.key)}" value="{h(slot.image_slug)}">'
                + render_body_editor(
                    blocks,
                    field_prefix=slot.key,
                    legend=pretty,
                )
            )
        if body_editors:
            body_panel = (
                '<section class="body-editor-panel" id="body-editor-panel">'
                f'{"".join(body_editors)}'
                "</section>"
            )
        elif sec.id in content_boards:
            body_panel = (
                '<section class="body-editor-panel" id="body-editor-panel">'
                '<p class="note">이 항목에는 긴 글이 없습니다. 위에서 다른 글을 골라 주세요.</p>'
                "</section>"
            )
        else:
            body_panel = ""

        short_copy = ""
        if legacy_rows:
            short_copy = (
                f"{filters}"
                + '<fieldset class="fieldset" style="box-shadow:none;background:#fff;margin:0 0 .5rem">'
                + "".join(legacy_rows)
                + "</fieldset>"
            )

        title_panel = ""
        if title_row:
            title_panel = (
                '<fieldset class="fieldset" style="box-shadow:none;background:#fff;margin:0 0 1rem">'
                f"{title_row}"
                "</fieldset>"
            )

        crumb_tail = (
            sections.friendly_group_label(group) if group and group != "전체" else sec.title
        )
        preview = ""
        if is_tips_tabs:
            preview = "/pages/travel-tips/index.html?admin=1"
        elif is_post_board and group in post_groups:
            preview = post_preview(sec.id, group)
        elif sec.id == "beforeTrip" and group in post_groups:
            preview = post_preview(sec.id, group)
        elif sec.preview_path:
            preview = public_href(sec.preview_path)

        expert = ""
        if sec.id not in content_boards:
            expert = render_expert(
                render_force_translate_check(), summary="전문가용 · 번역 다시 하기"
            )

        page_h1 = sec.title if is_tips_tabs else (crumb_tail if is_post_board else sec.title)
        back_href = "/"
        back_label = "대시보드로"
        if is_post_board and not is_tips_tabs:
            back_href = f"/section?id={uq(sec.id)}"
            back_label = "목록으로"

        body = f"""
        <div class="toolbar">
          <div>
            <h1>{h(page_h1)}</h1>
          </div>
        </div>
        {group_nav}
        <form class="card editor-card" method="post" action="/section/save" enctype="multipart/form-data">
          <input type="hidden" name="section_id" value="{h(sec.id)}">
          <input type="hidden" name="group" value="{h(group)}">
          {title_panel}
          {body_panel}
          {short_copy}
          {expert}
          {render_editor_actions(back_href=back_href, back_label=back_label)}
        </form>
        """
        crumbs = [(f"/section?id={sec.id}", sec.title)]
        if group and group not in ("전체", "") and crumb_tail != sec.title:
            crumbs.append(("", crumb_tail))
        layout_title = sec.title
        if is_tips_tabs or is_post_board:
            layout_title = f"{sec.title} · {crumb_tail}"
        return layout(
            layout_title,
            body,
            flash=self._pop_flash(),
            flash_error=self._flash_error(),
            nav_active=f"/section?id={sec.id}",
            crumbs=crumbs,
            preview_href=preview,
        )

    def page_phrases(self, cat: str) -> str:
        cats = sections.list_phrase_categories()
        if cat not in cats:
            cat = cats[0] if cats else "daily"
        items = sections.get_phrases(cat)
        opts = "".join(
            f'<option value="/phrases?cat={h(c)}"'
            f'{" selected" if c == cat else ""}>{h(sections.phrase_cat_label(c))}</option>'
            for c in cats
        )
        nav = (
            '<label class="group-select-wrap"><span>분류</span>'
            f'<select class="group-select" data-nav-select>{opts}</select></label>'
        )
        rows = []
        for p in items:
            ftext = (
                f"{p.get('id','')} {p.get('ko','')} {p.get('en','')} "
                f"{p.get('ja','')} {p.get('rom','')}"
            )
            rows.append(
                render_list_row(
                    href=f"/phrase/edit?cat={cat}&id={p.get('id','')}",
                    title=p.get("ko") or p.get("id") or "",
                    subtitle=p.get("en") or "",
                    meta=p.get("rom") or "",
                    filter_text=ftext,
                )
            )
        filters = render_list_filters(placeholder="문장으로 찾아보세요…")
        list_html = (
            f'<div class="list-board">{"".join(rows)}</div>'
            if rows
            else empty_state(
                "이 분류에 문장이 없어요",
                "새 문장을 추가해 보세요.",
                f"/phrase/new?cat={cat}",
                "새 문장 추가",
            )
        )
        body = f"""
        <div class="toolbar">
          <div>
            <h1>유용한 한국어</h1>
          </div>
          <a class="btn btn-lg" href="/phrase/new?cat={h(cat)}">새 문장 추가</a>
        </div>
        {nav}
        {filters}
        {list_html}
        """
        return layout(
            "유용한 한국어",
            body,
            flash=self._pop_flash(),
            flash_error=self._flash_error(),
            nav_active="/phrases",
            crumbs=[("/phrases", "유용한 한국어")],
            preview_href=public_href("pages/useful-korean/"),
        )

    def page_phrase_edit(self, cat: str, phrase_id: str) -> str:
        items = sections.get_phrases(cat)
        item = next((p for p in items if p.get("id") == phrase_id), None)
        if not item:
            raise ValueError(f"문장 없음: {phrase_id}")
        body = f"""
        <div class="toolbar">
          <div>
            <h1>문장 수정</h1>
            <p class="page-lead">{h(sections.phrase_cat_label(cat))}</p>
          </div>
        </div>
        <form class="card editor-card" method="post" action="/phrase/save">
          <input type="hidden" name="cat" value="{h(cat)}">
          <input type="hidden" name="id" value="{h(phrase_id)}">
          <input type="hidden" name="is_new" value="0">
          <div class="field field--hero">
            <label>한국어</label>
            <textarea class="input-hero" name="ko" required rows="3">{h(item.get('ko',''))}</textarea>
          </div>
          <div class="field">
            <label>발음 표기 (로마자 · 번역하지 않음)</label>
            <input type="text" name="rom" value="{h(item.get('rom',''))}"
                   placeholder="예: annyeonghaseyo">
          </div>
          <p class="muted">의미(영어·일본어)는 저장할 때 한국어에서 자동 번역됩니다.</p>
          {render_expert(render_force_translate_check())}
          {render_editor_actions(back_href=f"/phrases?cat={cat}")}
        </form>
        <form class="danger-zone" method="post" action="/phrase/delete"
              onsubmit="return confirm('삭제할까요?');">
          <input type="hidden" name="cat" value="{h(cat)}">
          <input type="hidden" name="id" value="{h(phrase_id)}">
          <h2>삭제</h2>
          <p class="muted">이 문장을 목록에서 지웁니다.</p>
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
                ("/phrases", "유용한 한국어"),
                (f"/phrases?cat={cat}", sections.phrase_cat_label(cat)),
                ("", item.get("ko") or phrase_id),
            ],
        )

    def page_phrase_new(self, cat: str) -> str:
        # Id must stay visible — required fields inside closed <details> block submit silently.
        body = f"""
        <div class="toolbar">
          <div>
            <h1>새 문장</h1>
            <p class="page-lead">{h(sections.phrase_cat_label(cat))}에 추가합니다.</p>
          </div>
        </div>
        <form class="card editor-card" method="post" action="/phrase/save">
          <input type="hidden" name="cat" value="{h(cat)}">
          <input type="hidden" name="is_new" value="1">
          <div class="field field--hero">
            <label>한국어</label>
            <textarea class="input-hero" name="ko" required rows="3"></textarea>
          </div>
          <div class="field">
            <label>발음 표기 (로마자 · 번역하지 않음)</label>
            <input type="text" name="rom" placeholder="예: annyeonghaseyo">
          </div>
          <div class="field field--hero">
            <label>주소 이름 (영문 id)</label>
            <input class="input-hero" type="text" name="id" required pattern="[a-z0-9-]+"
              placeholder="my-phrase" autocomplete="off">
            <span class="hint">영문 소문자·숫자·하이픈</span>
          </div>
          <p class="muted">의미(영어·일본어)는 등록할 때 한국어에서 자동 번역됩니다.</p>
          {render_editor_actions(save_label="등록", back_href=f"/phrases?cat={cat}")}
        </form>
        """
        return layout(
            "새 문장",
            body,
            nav_active="/phrases",
            crumbs=[
                ("/phrases", "유용한 한국어"),
                (f"/phrases?cat={cat}", sections.phrase_cat_label(cat)),
                ("", "새 문장"),
            ],
        )

    def page_version(self) -> str:
        try:
            ver = read_version()
        except SystemExit:
            ver = "(없음)"
        body = f"""
        <h1>사이트 새로고침</h1>
        <p class="page-lead">글·이미지를 저장하면 캐시 버전이 자동으로 올라갑니다.
          여기서는 수동으로 한 번 더 올릴 수 있습니다. 반영이 안 보이면
          <strong>Ctrl+F5</strong> 또는 <a href="/viewer">뷰어</a>를 다시 여세요.</p>
        <form class="card" method="post" action="/version/run">
          <p class="muted" style="margin:0 0 .75rem">현재 버전: <strong>{h(ver)}</strong></p>
          <div class="row" style="margin-top:0">
            <button type="submit" class="btn-lg">지금 새로고침 실행</button>
          </div>
        </form>
        """
        return layout(
            "사이트 새로고침",
            body,
            flash=self._pop_flash(),
            flash_error=self._flash_error(),
            nav_active="/version",
            crumbs=[("/version", "사이트 새로고침")],
        )

    def page_patch_menus(self) -> str:
        body = """
        <h1>메뉴 정리</h1>
        <p class="page-lead">예전 가게 페이지의 메뉴 사진 칸을 맞춰 주는 전문가용 도구입니다.</p>
        <form class="card" method="post" action="/tools/patch-menus/run">
          <p class="muted" style="margin:0 0 .75rem">
            새 가게는 본문 글쓰기에서 사진을 넣으면 됩니다. 필요할 때만 실행하세요.
          </p>
          <div class="row" style="margin-top:0">
            <button type="submit">전체 가게에 적용</button>
          </div>
        </form>
        """
        return layout(
            "메뉴 정리",
            body,
            flash=self._pop_flash(),
            flash_error=self._flash_error(),
            nav_active="/tools/patch-menus",
            crumbs=[("/tools/patch-menus", "메뉴 정리")],
        )

    def page_migrate_body(self) -> str:
        body = """
        <h1>본문 정리</h1>
        <p class="page-lead">예전 고정 문구를 새 글쓰기 형식으로 옮기는 전문가용 도구입니다.</p>
        <form class="card" method="post" action="/tools/migrate-body/run">
          <h2>가게 글</h2>
          <p class="muted" style="margin:0 0 .75rem">
            예전 팁·메뉴 사진을 본문 글로 옮깁니다. 이미 본문이 있는 가게는 건너뜁니다.
          </p>
          <input type="hidden" name="target" value="shops">
          <label class="check-row">
            <input type="checkbox" name="force" value="1">
            <span>이미 있는 본문도 덮어쓰기</span>
          </label>
          <div class="row" style="margin-top:.75rem">
            <button type="submit">가게 본문 정리 실행</button>
          </div>
        </form>
        <form class="card" method="post" action="/tools/migrate-body/run">
          <h2>섹션 글 (여행 전 · 쇼핑 · 편의점 · 기념품)</h2>
          <p class="muted" style="margin:0 0 .75rem">
            탭/상세 페이지의 예전 문단을 새 본문으로 복사합니다.
          </p>
          <input type="hidden" name="target" value="sections">
          <label class="check-row">
            <input type="checkbox" name="force" value="1">
            <span>이미 있는 본문도 덮어쓰기</span>
          </label>
          <div class="row" style="margin-top:.75rem">
            <button type="submit">섹션 본문 정리 실행</button>
          </div>
        </form>
        """
        return layout(
            "본문 정리",
            body,
            flash=self._pop_flash(),
            flash_error=self._flash_error(),
            nav_active="/tools/migrate-body",
            crumbs=[("/tools/migrate-body", "본문 정리")],
        )




def main() -> int:
    server = ThreadingHTTPServer((HOST, PORT), AdminHandler)
    server.flash = ""  # type: ignore[attr-defined]
    url = f"http://{HOST}:{PORT}/"
    print(f"관리자(CMS): {url}")
    print(f"사이트 화면 모드: http://{HOST}:{PORT}/viewer")
    print("※ 반드시 이 창을 켠 채 브라우저에서 위 주소를 여세요. 예전에 켜 둔 서버가 있으면 종료 후 다시 실행하세요.")
    print("※ 저장 후 공개 화면이 안 바뀌면 Ctrl+F5, 또는 /viewer 를 다시 여세요. file:// 로 열지 마세요.")
    print("※ GitHub Pages에는 관리자가 없습니다 (로컬 전용).")
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
