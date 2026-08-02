# -*- coding: utf-8 -*-
"""Local content admin for meals / desserts / shops (stdlib only).

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
from urllib.parse import parse_qs, urlparse

TOOL_DIR = Path(__file__).resolve().parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from lib import content  # noqa: E402
from lib.cache_bust import read_version  # noqa: E402
from lib.images import (  # noqa: E402
    MAX_UPLOAD_BYTES,
    dish_image_targets,
    safe_media_path,
    save_uploads_for_targets,
    shop_image_targets,
)
from lib.multipart import parse_request_body, read_http_body  # noqa: E402
from lib.paths import ROOT  # noqa: E402

HOST = "127.0.0.1"
PORT = 8765
# Body may include several images + fields
MAX_BODY_BYTES = MAX_UPLOAD_BYTES * 3 + 256 * 1024


def h(text: object) -> str:
    return html.escape("" if text is None else str(text), quote=True)


def layout(title: str, body: str, flash: str = "") -> str:
    flash_html = ""
    if flash:
        flash_html = f'<div class="flash">{flash}</div>'
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{h(title)} · 콘텐츠 관리</title>
  <style>
    :root {{
      --bg: #f6f3ee;
      --ink: #1c1917;
      --muted: #57534e;
      --line: #d6d3d1;
      --card: #fffdf9;
      --accent: #0f766e;
      --danger: #b91c1c;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0; font-family: "Malgun Gothic", "Apple SD Gothic Neo", sans-serif;
      background: linear-gradient(180deg, #efe8df 0%, var(--bg) 40%, #f8faf9 100%);
      color: var(--ink); line-height: 1.5;
    }}
    header {{
      padding: 1rem 1.25rem; border-bottom: 1px solid var(--line);
      background: rgba(255,253,249,.9); position: sticky; top: 0; backdrop-filter: blur(6px);
    }}
    header a {{ color: var(--accent); margin-right: 1rem; text-decoration: none; font-weight: 600; }}
    header a:hover {{ text-decoration: underline; }}
    main {{ max-width: 920px; margin: 0 auto; padding: 1.25rem; }}
    h1 {{ font-size: 1.4rem; margin: 0 0 .75rem; }}
    h2 {{ font-size: 1.15rem; margin: 1.5rem 0 .5rem; }}
    .muted {{ color: var(--muted); font-size: .92rem; }}
    .flash {{
      background: #ecfdf5; border: 1px solid #99f6e4; padding: .75rem 1rem;
      border-radius: 8px; margin-bottom: 1rem; white-space: pre-wrap;
    }}
    .flash.error {{ background: #fef2f2; border-color: #fecaca; }}
    table {{ width: 100%; border-collapse: collapse; background: var(--card);
      border: 1px solid var(--line); border-radius: 8px; overflow: hidden; }}
    th, td {{ padding: .55rem .7rem; border-bottom: 1px solid var(--line);
      text-align: left; vertical-align: top; font-size: .95rem; }}
    th {{ background: #f5f5f4; font-size: .85rem; }}
    tr:last-child td {{ border-bottom: 0; }}
    form.card {{
      background: var(--card); border: 1px solid var(--line); border-radius: 8px;
      padding: 1rem 1.1rem; margin: 1rem 0;
    }}
    label {{ display: block; font-weight: 600; margin: .7rem 0 .25rem; font-size: .9rem; }}
    input[type=text], input[type=search], textarea, select {{
      width: 100%; padding: .5rem .6rem; border: 1px solid var(--line);
      border-radius: 6px; font: inherit; background: #fff;
    }}
    textarea {{ min-height: 5rem; resize: vertical; }}
    .row {{ display: flex; gap: .6rem; flex-wrap: wrap; margin-top: 1rem; }}
    button, .btn {{
      appearance: none; border: 0; border-radius: 6px; padding: .55rem .9rem;
      background: var(--accent); color: #fff; font: inherit; font-weight: 600;
      cursor: pointer; text-decoration: none; display: inline-block;
    }}
    button.secondary, a.btn.secondary {{ background: #57534e; }}
    button.danger, a.btn.danger {{ background: var(--danger); }}
    .actions a {{ margin-right: .5rem; }}
    code {{ background: #f5f5f4; padding: .1rem .35rem; border-radius: 4px; font-size: .88rem; }}
    .note {{
      background: #fff7ed; border: 1px solid #fed7aa; padding: .75rem 1rem;
      border-radius: 8px; margin: 1rem 0; font-size: .92rem;
    }}
    .img-field {{
      border: 1px dashed var(--line); border-radius: 8px; padding: .75rem .9rem;
      margin: .85rem 0; background: #fafaf9;
    }}
    .img-field .thumb {{
      display: block; max-width: 220px; max-height: 140px; object-fit: cover;
      border-radius: 6px; border: 1px solid var(--line); margin: .4rem 0 .6rem;
      background: #fff;
    }}
    .img-field .missing {{
      display: inline-block; color: var(--muted); font-size: .9rem;
      padding: .4rem 0 .6rem;
    }}
    input[type=file] {{ width: 100%; font: inherit; }}
    .lang-block {{
      border: 1px solid var(--line); border-radius: 8px; padding: .75rem .9rem;
      margin: .75rem 0; background: #fafaf9;
    }}
    .lang-block h3 {{
      margin: 0 0 .35rem; font-size: 1rem; color: var(--accent);
    }}
    .lang-grid {{
      display: grid; gap: .75rem;
      grid-template-columns: 1fr;
    }}
    @media (min-width: 800px) {{
      .lang-grid {{ grid-template-columns: 1fr 1fr 1fr; }}
    }}
    .shop-pick {{
      max-height: 280px; overflow: auto; border: 1px solid var(--line);
      border-radius: 8px; padding: .5rem .75rem; background: #fff;
    }}
    .shop-pick label {{
      display: flex; gap: .5rem; align-items: flex-start;
      font-weight: 400; margin: .35rem 0; font-size: .92rem;
    }}
    .shop-pick label.already {{ opacity: .55; }}
    .shop-pick .meta {{ color: var(--muted); font-size: .85rem; }}
  </style>
</head>
<body>
  <header>
    <a href="/">홈</a>
    <a href="/dishes?kind=meals">식사 음식</a>
    <a href="/dishes?kind=desserts">디저트</a>
    <a href="/shops">가게</a>
    <a href="/version">버전</a>
  </header>
  <main>
    {flash_html}
    {body}
  </main>
</body>
</html>
"""


def media_url(rel_path: str) -> str:
    return "/media/" + rel_path.lstrip("/")


LANG_LABELS = {"ko": "한국어 (KO)", "en": "English (EN)", "ja": "日本語 (JA)"}


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


def render_dish_lang_fields(texts: dict[str, dict[str, str]] | None = None) -> str:
    texts = texts or {lang: {"title": "", "desc": "", "about": ""} for lang in ("ko", "en", "ja")}
    blocks = []
    for lang in ("ko", "en", "ja"):
        t = texts.get(lang) or {}
        req = " required" if lang == "ko" else ""
        blocks.append(
            f'<div class="lang-block">'
            f"<h3>{LANG_LABELS[lang]}</h3>"
            f'<label>이름 (title)</label>'
            f'<input type="text" name="title_{lang}" value="{h(t.get("title", ""))}"{req}>'
            f'<label>짧은 설명 (desc)</label>'
            f'<input type="text" name="desc_{lang}" value="{h(t.get("desc", ""))}">'
            f'<label>소개 (about)</label>'
            f'<textarea name="about_{lang}">{h(t.get("about", ""))}</textarea>'
            f"</div>"
        )
    return (
        '<h2>번역 (KO / EN / JA)</h2>'
        '<p class="muted">한국어는 필수입니다. EN·JA를 비우면 저장 시 한국어와 같게 채웁니다.</p>'
        f'<div class="lang-grid">{"".join(blocks)}</div>'
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
    blocks = []
    for lang in ("ko", "en", "ja"):
        t = texts.get(lang) or {}
        req = " required" if lang == "ko" else ""
        blocks.append(
            f'<div class="lang-block">'
            f"<h3>{LANG_LABELS[lang]}</h3>"
            f'<label>가게명 (name)</label>'
            f'<input type="text" name="name_{lang}" value="{h(t.get("name", ""))}"{req}>'
            f'<label>위치 (location)</label>'
            f'<input type="text" name="location_{lang}" value="{h(t.get("location", ""))}">'
            f'<label>대표 메뉴 (menu)</label>'
            f'<input type="text" name="menu_{lang}" value="{h(t.get("menu", ""))}">'
            f'<label>가격 (price)</label>'
            f'<input type="text" name="price_{lang}" value="{h(t.get("price", ""))}">'
            f'<label>팁 (tip)</label>'
            f'<textarea name="tip_{lang}">{h(t.get("tip", ""))}</textarea>'
            f'<label>소개 (about)</label>'
            f'<textarea name="about_{lang}">{h(t.get("about", ""))}</textarea>'
            f"</div>"
        )
    return (
        '<h2>번역 (KO / EN / JA)</h2>'
        '<p class="muted">한국어 가게명은 필수입니다. EN·JA를 비우면 저장 시 한국어와 같게 채웁니다. '
        "지도 링크(mapsUrl)는 한국어 location으로 생성합니다.</p>"
        f'<div class="lang-grid">{"".join(blocks)}</div>'
    )


def render_shop_attach_section(
    kind: str,
    dish_slug: str | None = None,
) -> str:
    """Checkbox list of all shops to attach under this dish."""
    already = content.shops_under_dish(kind, dish_slug) if dish_slug else set()
    catalog = content.list_shop_catalog()
    if not catalog:
        return (
            "<h2>하위 가게 추가</h2>"
            '<p class="muted">등록된 가게가 아직 없습니다. 가게 메뉴에서 먼저 추가하세요.</p>'
        )
    rows = []
    for item in catalog:
        mem = ", ".join(f"{k}/{d}" for k, d in item.memberships) or "(페이지 없음)"
        is_here = item.slug in already
        disabled = " disabled" if is_here else ""
        cls = ' class="already"' if is_here else ""
        checked = " checked" if is_here else ""
        mark = " · 이미 이 음식 하위" if is_here else ""
        rows.append(
            f"<label{cls}>"
            f'<input type="checkbox" name="attach_shops" value="{h(item.slug)}"'
            f"{checked}{disabled}>"
            f"<span><strong>{h(item.name)}</strong> <code>{h(item.slug)}</code>"
            f'<br><span class="meta">현재 소속: {h(mem)}{mark}</span></span>'
            f"</label>"
        )
    return (
        "<h2>하위 가게 추가</h2>"
        '<p class="muted">이미 등록된 가게를 복수 선택하면, 이 음식 아래 목록·상세 페이지에 연결됩니다. '
        "같은 가게 번역(i18n) 키를 공유하며, 상세 HTML이 없으면 복사·생성합니다.</p>"
        f'<div class="shop-pick">{"".join(rows)}</div>'
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
            status = f'<span class="muted">현재 파일 있음</span>'
        else:
            preview = '<span class="missing">아직 파일 없음 — 업로드하면 이 경로에 저장됩니다</span>'
            status = ""
        blocks.append(
            f'<div class="img-field">'
            f"<label>{h(t.label)}</label>"
            f"<p class=\"muted\">저장 경로: <code>{h(t.rel)}</code> {status}</p>"
            f"{preview}"
            f'<input type="file" name="{h(t.key)}" accept=".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp">'
            f"</div>"
        )
    return (
        '<p class="muted">JPG / PNG / WebP · 최대 8MB · 파일명은 슬러그 기준으로 저장됩니다.</p>'
        + "".join(blocks)
    )


class AdminHandler(BaseHTTPRequestHandler):
    server_version = "GuidebookContentAdmin/1.0"

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

    def _redirect(self, location: str) -> None:
        self.send_response(303)
        self.send_header("Location", location)
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        try:
            parsed = urlparse(self.path)
            path = parsed.path
            qs = parse_qs(parsed.query)

            if path == "/":
                self._send(200, self.page_home())
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
            elif path == "/version":
                self._send(200, self.page_version())
            elif path.startswith("/media/"):
                self._serve_media(path)
            else:
                self._send(404, layout("404", "<h1>페이지 없음</h1><p><a href='/'>홈</a></p>"))
        except Exception as exc:  # noqa: BLE001
            self._send(
                500,
                layout(
                    "오류",
                    f"<h1>오류</h1><pre class='flash error'>{h(traceback.format_exc())}</pre>",
                ),
            )
            sys.stderr.write(f"{exc}\n")

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
        # Sniff if mislabeled
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
                upload_notes = save_uploads_for_targets(
                    dish_image_targets(slug), files
                )
                if upload_notes:
                    notes.extend(upload_notes)
                else:
                    notes.append("이미지: 새로 올린 파일 없음 (기존 유지)")
                # Disabled checkboxes are not posted; merge already-attached + newly checked
                selected = form_data.getlist("attach_shops")
                if selected:
                    notes.extend(content.attach_shops_to_dish(kind, slug, selected))
                self.server.flash = "\n".join(notes)  # type: ignore[attr-defined]
                self._redirect(f"/dish/edit?kind={kind}&slug={slug}")
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
                upload_notes = save_uploads_for_targets(
                    dish_image_targets(slug), files
                )
                if upload_notes:
                    notes.extend(upload_notes)
                else:
                    notes.append("이미지: 업로드 없음 — 수정 화면에서 올릴 수 있습니다")
                selected = form_data.getlist("attach_shops")
                if selected:
                    notes.extend(content.attach_shops_to_dish(kind, slug, selected))
                self.server.flash = "\n".join(notes)  # type: ignore[attr-defined]
                self._redirect(f"/dish/edit?kind={kind}&slug={slug}")
                return

            if path == "/dish/delete":
                notes = content.delete_dish(
                    form.get("kind", "meals"),
                    form.get("slug", ""),
                    delete_images=form.get("delete_images") == "1",
                )
                self.server.flash = "\n".join(notes)  # type: ignore[attr-defined]
                self._redirect(f"/dishes?kind={form.get('kind','meals')}")
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
                shop = content.get_shop(slug)
                if shop.get("kind") and shop.get("dish_slug"):
                    upload_notes = save_uploads_for_targets(
                        shop_image_targets(
                            shop["kind"], shop["dish_slug"], slug
                        ),
                        files,
                    )
                    if upload_notes:
                        notes.extend(upload_notes)
                    else:
                        notes.append("이미지: 새로 올린 파일 없음 (기존 유지)")
                self.server.flash = "\n".join(notes)  # type: ignore[attr-defined]
                self._redirect(f"/shop/edit?slug={slug}")
                return

            if path == "/shop/create":
                parent = form.get("parent", "")  # kind|dish_slug
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
                if upload_notes:
                    notes.extend(upload_notes)
                else:
                    notes.append(
                        "이미지: 업로드 없음 — 수정 화면에서 언제든 올릴 수 있습니다"
                    )
                self.server.flash = "\n".join(notes)  # type: ignore[attr-defined]
                self._redirect(f"/shop/edit?slug={slug}")
                return

            if path == "/shop/delete":
                notes = content.delete_shop(
                    form.get("slug", ""),
                    delete_images=form.get("delete_images") == "1",
                )
                self.server.flash = "\n".join(notes)  # type: ignore[attr-defined]
                self._redirect("/shops")
                return

            if path == "/version/run":
                from datetime import datetime

                from lib.cache_bust import apply_cache_bust, write_version

                version = datetime.now().strftime("%Y%m%d%H%M%S")
                write_version(version)
                summary = apply_cache_bust(version)
                self.server.flash = (  # type: ignore[attr-defined]
                    f"버전 → {version}\n"
                    f"HTML 갱신 {summary['files_updated']}개 "
                    f"(교체 ~{summary['replacements']})"
                )
                self._redirect("/version")
                return

            self._send(404, layout("404", "<h1>POST 경로 없음</h1>"))
        except Exception as exc:  # noqa: BLE001
            self._send(
                200,
                layout(
                    "오류",
                    f"<h1>처리 실패</h1><div class='flash error'>{h(exc)}</div>"
                    f"<pre>{h(traceback.format_exc())}</pre><p><a href='/'>홈</a></p>",
                ),
            )

    def _pop_flash(self) -> str:
        flash = getattr(self.server, "flash", "") or ""
        self.server.flash = ""  # type: ignore[attr-defined]
        if not flash:
            return ""
        return f'<div class="flash">{h(flash)}</div>'

    def page_home(self) -> str:
        try:
            ver = read_version()
        except SystemExit:
            ver = "(없음)"
        meals_n = len(content.list_dishes("meals"))
        dess_n = len(content.list_dishes("desserts"))
        shops_n = len(content.list_shops())
        body = f"""
        {self._pop_flash()}
        <h1>콘텐츠 관리 (로컬 MVP)</h1>
        <p class="muted">프로젝트: <code>{h(ROOT)}</code></p>
        <p>식사 음식 <strong>{meals_n}</strong> · 디저트 <strong>{dess_n}</strong> · 가게 <strong>{shops_n}</strong></p>
        <p>현재 에셋 버전: <code>{h(ver)}</code></p>
        <div class="row">
          <a class="btn" href="/dishes?kind=meals">식사 음식 목록</a>
          <a class="btn" href="/dishes?kind=desserts">디저트 목록</a>
          <a class="btn" href="/shops">가게 목록</a>
          <a class="btn secondary" href="/version">버전 도구</a>
        </div>
        <div class="note">
          <strong>이 도구에서 할 수 있는 일</strong><br>
          · 식사/디저트 음식·가게 추가·수정·삭제<br>
          · KO / EN / JA 문구를 폼에서 직접 입력·저장<br>
          · 대표·상호·메뉴 이미지를 업로드하면 사이트 경로에 바로 저장<br>
          · 큰 배포 전에는 <a href="/version">버전 업데이트</a> 실행
        </div>
        """
        return layout("홈", body)

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
                f"<a href='/dish/delete?kind={h(kind)}&slug={h(d.slug)}'>삭제</a>"
                f"</td></tr>"
            )
        body = f"""
        {self._pop_flash()}
        <h1>{label}</h1>
        <p class="muted">i18n <code>dishes.*</code> + <code>pages/foods/{h(kind)}/</code></p>
        <div class="row">
          <a class="btn" href="/dish/new?kind={h(kind)}">+ 새 음식 추가</a>
        </div>
        <table>
          <tr><th>슬러그</th><th>이름</th><th>설명</th><th></th></tr>
          {''.join(rows) or '<tr><td colspan="4">항목 없음</td></tr>'}
        </table>
        """
        return layout(label, body)

    def page_dish_edit(self, kind: str, slug: str) -> str:
        d = content.get_dish(kind, slug)
        lang_html = render_dish_lang_fields(d.get("texts"))
        img_html = render_image_fields(dish_image_targets(slug))
        attach_html = render_shop_attach_section(kind, slug)
        body = f"""
        {self._pop_flash()}
        <h1>음식 수정 · {h(slug)}</h1>
        <p class="muted">페이지: <code>{h(d['page'] or '(없음)')}</code></p>
        <form class="card" method="post" action="/dish/save" enctype="multipart/form-data">
          <input type="hidden" name="kind" value="{h(kind)}">
          <input type="hidden" name="slug" value="{h(slug)}">
          <label>슬러그 변경 (rename)</label>
          <input type="text" name="new_slug" value="{h(slug)}" pattern="[a-z0-9]+(-[a-z0-9]+)*">
          {lang_html}
          <h2>이미지</h2>
          {img_html}
          {attach_html}
          <div class="row">
            <button type="submit">저장</button>
            <a class="btn secondary" href="/dishes?kind={h(kind)}">목록</a>
            <a class="btn danger" href="/dish/delete?kind={h(kind)}&slug={h(slug)}">삭제…</a>
          </div>
        </form>
        """
        return layout(f"수정 {slug}", body)

    def page_dish_new(self, kind: str) -> str:
        label = "식사" if kind == "meals" else "디저트"
        default_emoji = "🍽️" if kind == "meals" else "🍰"
        lang_html = render_dish_lang_fields()
        attach_html = render_shop_attach_section(kind, None)
        img_html = (
            '<div class="img-field">'
            "<label>음식 대표 이미지</label>"
            '<p class="muted">저장 경로: <code>Images/foods/dishes/&#123;슬러그&#125;.jpg</code> '
            "(아래에서 올리면 이 이름으로 저장)</p>"
            '<input type="file" name="cover_image" accept=".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp">'
            "</div>"
            '<p class="muted">JPG / PNG / WebP · 최대 8MB</p>'
        )
        body = f"""
        <h1>새 {label} 음식 추가</h1>
        <form class="card" method="post" action="/dish/create" enctype="multipart/form-data">
          <input type="hidden" name="kind" value="{h(kind)}">
          <label>슬러그 (영문 URL용)</label>
          <input type="text" name="slug" placeholder="예: gimbap-special" required
                 pattern="[a-z0-9]+(-[a-z0-9]+)*">
          <label>이모지 (목록 카드용)</label>
          <input type="text" name="emoji" value="{h(default_emoji)}" style="max-width:6rem">
          {lang_html}
          <h2>이미지</h2>
          {img_html}
          {attach_html}
          <div class="row">
            <button type="submit">생성</button>
            <a class="btn secondary" href="/dishes?kind={h(kind)}">취소</a>
          </div>
        </form>
        """
        return layout("새 음식", body)

    def page_dish_delete(self, kind: str, slug: str) -> str:
        body = f"""
        <h1>음식 삭제 확인</h1>
        <p><code>{h(slug)}</code> 을(를) 삭제할까요? i18n 키와 HTML 페이지·허브 카드가 제거됩니다.</p>
        <p class="muted">가게가 남아 있으면 삭제할 수 없습니다.</p>
        <form class="card" method="post" action="/dish/delete">
          <input type="hidden" name="kind" value="{h(kind)}">
          <input type="hidden" name="slug" value="{h(slug)}">
          <label><input type="checkbox" name="delete_images" value="1"> 대표 이미지도 삭제 (Images/foods/dishes/{h(slug)}.jpg)</label>
          <div class="row">
            <button type="submit" class="danger">삭제 실행</button>
            <a class="btn secondary" href="/dish/edit?kind={h(kind)}&slug={h(slug)}">취소</a>
          </div>
        </form>
        """
        return layout("삭제", body)

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
                f"<a href='/shop/delete?slug={h(s.slug)}'>삭제</a>"
                f"</td></tr>"
            )
        body = f"""
        {self._pop_flash()}
        <h1>가게 / 브랜드</h1>
        <p class="muted">i18n <code>restaurants.*</code></p>
        <div class="row">
          <a class="btn" href="/shop/new">+ 새 가게 추가</a>
        </div>
        <table>
          <tr><th>슬러그</th><th>이름</th><th>소속</th><th>위치</th><th></th></tr>
          {''.join(rows) or '<tr><td colspan="5">항목 없음</td></tr>'}
        </table>
        """
        return layout("가게", body)

    def page_shop_edit(self, slug: str) -> str:
        s = content.get_shop(slug)
        regen_checked = "checked"
        lang_html = render_shop_lang_fields(s.get("texts"))
        if s.get("kind") and s.get("dish_slug"):
            img_html = render_image_fields(
                shop_image_targets(s["kind"], s["dish_slug"], slug)
            )
        else:
            img_html = (
                '<p class="muted">소속 음식 페이지를 찾을 수 없어 업로드 경로를 정할 수 없습니다. '
                "음식 수정에서 이 가게를 하위로 연결한 뒤 이미지를 올리세요.</p>"
            )
        mems = content.find_all_shop_pages(slug)
        mem_txt = ", ".join(f"{k}/{d}" for k, d, _ in mems) or "(없음)"
        body = f"""
        {self._pop_flash()}
        <h1>가게 수정 · {h(slug)}</h1>
        <p class="muted">소속(페이지): <code>{h(mem_txt)}</code><br>
        대표 페이지: <code>{h(s['page'] or '(없음)')}</code></p>
        <form class="card" method="post" action="/shop/save" enctype="multipart/form-data">
          <input type="hidden" name="slug" value="{h(slug)}">
          <label>슬러그 변경 (rename)</label>
          <input type="text" name="new_slug" value="{h(slug)}" pattern="[a-z0-9]+(-[a-z0-9]+)*">
          {lang_html}
          <label><input type="checkbox" name="regen_maps" value="1" {regen_checked}>
            저장 시 한국어 location으로 mapsUrl 재생성</label>
          <h2>이미지</h2>
          {img_html}
          <p class="muted">현재 mapsUrl: <code>{h(s['mapsUrl'][:80])}{'…' if len(s['mapsUrl'])>80 else ''}</code></p>
          <div class="row">
            <button type="submit">저장</button>
            <a class="btn secondary" href="/shops">목록</a>
            <a class="btn danger" href="/shop/delete?slug={h(slug)}">삭제…</a>
          </div>
        </form>
        """
        return layout(f"가게 {slug}", body)

    def page_shop_new(self) -> str:
        opts = []
        for kind, slug, label in content.dish_options_for_select():
            opts.append(f'<option value="{h(kind)}|{h(slug)}">{h(label)}</option>')
        lang_html = render_shop_lang_fields()
        img_html = (
            '<div class="img-field">'
            "<label>상호 이미지</label>"
            '<p class="muted">식사: <code>Images/foods/restaurants/&#123;음식&#125;/&#123;슬러그&#125;.jpg</code><br>'
            "디저트: <code>Images/foods/brands/&#123;슬러그&#125;.jpg</code></p>"
            '<input type="file" name="shop_image" accept=".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp">'
            "</div>"
            '<div class="img-field">'
            "<label>대표 메뉴 이미지</label>"
            '<p class="muted">식사: <code>.../&#123;슬러그&#125;-menu.jpg</code> · '
            "디저트: <code>Images/foods/restaurants/desserts/&#123;슬러그&#125;-menu.jpg</code></p>"
            '<input type="file" name="menu_image" accept=".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp">'
            "</div>"
            '<p class="muted">JPG / PNG / WebP · 최대 8MB · 슬러그 파일명으로 저장</p>'
        )
        body = f"""
        <h1>새 가게 추가</h1>
        <form class="card" method="post" action="/shop/create" enctype="multipart/form-data">
          <label>부모 음식</label>
          <select name="parent" required>
            <option value="">선택…</option>
            {''.join(opts)}
          </select>
          <label>슬러그</label>
          <input type="text" name="slug" required pattern="[a-z0-9]+(-[a-z0-9]+)*" placeholder="예: my-kimbap-shop">
          {lang_html}
          <h2>이미지</h2>
          {img_html}
          <div class="row">
            <button type="submit">생성</button>
            <a class="btn secondary" href="/shops">취소</a>
          </div>
        </form>
        """
        return layout("새 가게", body)

    def page_shop_delete(self, slug: str) -> str:
        body = f"""
        <h1>가게 삭제 확인</h1>
        <p><code>{h(slug)}</code> 을(를) 삭제할까요?</p>
        <form class="card" method="post" action="/shop/delete">
          <input type="hidden" name="slug" value="{h(slug)}">
          <label><input type="checkbox" name="delete_images" value="1"> 이미지도 삭제 (있으면)</label>
          <div class="row">
            <button type="submit" class="danger">삭제 실행</button>
            <a class="btn secondary" href="/shop/edit?slug={h(slug)}">취소</a>
          </div>
        </form>
        """
        return layout("삭제", body)

    def page_version(self) -> str:
        try:
            ver = read_version()
        except SystemExit:
            ver = "(없음)"
        body = f"""
        {self._pop_flash()}
        <h1>캐시 버전</h1>
        <p>현재: <code>{h(ver)}</code></p>
        <p class="muted">형식: <code>YYYYMMDDHHMMSS</code> (예: 20260802125045)</p>
        <form class="card" method="post" action="/version/run">
          <p><code>js/cache-version.js</code>를 새 시각 버전으로 쓰고, 모든 HTML의 <code>?v=</code>를 일괄 적용합니다.</p>
          <div class="row">
            <button type="submit">지금 버전 업데이트 실행</button>
          </div>
        </form>
        <p class="muted">또는 탐색기에서 <code>tool\\update-version.bat</code>을 더블클릭하세요.</p>
        """
        return layout("버전", body)


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
