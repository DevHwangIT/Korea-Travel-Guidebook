# -*- coding: utf-8 -*-
"""Shop detail cleanup + source re-resolve (Naver → Kakao → Google).

1) Prefer place deep-link: Naver place/search → Kakao → Google
2) Strip Tip/body image blocks from restaurants.*.body and delete media/body-*.jpg
3) Sync public shop HTML visuals, rebuild i18n, bump cache version
4) Delete unreferenced orphan body/menu images under pages/foods/**/media/

Usage:
  python tool/migrate_shop_detail_cleanup.py
"""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.parse import quote

TOOL_DIR = Path(__file__).resolve().parent
ROOT = TOOL_DIR.parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

from lib import i18n_store  # noqa: E402
from lib.cache_bust import bump_asset_version  # noqa: E402
from lib.scaffold import sync_all_shop_page_visuals  # noqa: E402
from lib.shop_maps import (  # noqa: E402
    apply_maps_and_preview,
    detect_provider,
    google_embed_from_query,
    normalize_place_url,
    resolve_shop_input,
)


SYNC_KEYS = (
    "placeUrl",
    "mapsUrl",
    "mapsEmbedUrl",
    "mapsProvider",
    "sourceType",
    "previewTitle",
    "previewImage",
    "phone",
    "hours",
)


def _candidate_urls(entry: dict[str, Any]) -> list[tuple[str, str]]:
    """Return [(provider, url), ...] for known map links on the entry."""
    out: list[tuple[str, str]] = []
    seen: set[str] = set()
    for key in ("placeUrl", "mapsUrl"):
        url = normalize_place_url(str(entry.get(key) or ""))
        if not url or url in seen:
            continue
        seen.add(url)
        prov = detect_provider(url)
        if prov in ("naver", "kakao", "google"):
            out.append((prov, url))
    return out


def _pick_preferred_url(entry: dict[str, Any]) -> tuple[str, str]:
    """Pick best URL by priority Naver → Kakao → Google."""
    urls = _candidate_urls(entry)
    by_prov = {p: u for p, u in urls}
    for pref in ("naver", "kakao", "google"):
        if pref in by_prov:
            return pref, by_prov[pref]
    return "", ""


def _naver_search_url(name: str, location: str = "") -> str:
    q = " ".join(x for x in (name.strip(), location.strip()) if x).strip()
    if not q:
        return ""
    return f"https://map.naver.com/p/search/{quote(q)}"


def _kakao_search_url(name: str, location: str = "") -> str:
    q = " ".join(x for x in (name.strip(), location.strip()) if x).strip()
    if not q:
        return ""
    return f"https://map.kakao.com/?q={quote(q)}"


def _enrich_from_resolve(entry: dict[str, Any], url: str, source_type: str) -> dict[str, Any]:
    """Call resolve_shop_input and merge useful fields without wiping text."""
    resolved = resolve_shop_input(url, source_type=source_type, fetch_preview=True)
    if not resolved.get("ok"):
        return entry
    out = dict(entry)
    for key in ("phone", "hours"):
        val = str(resolved.get(key) or "").strip()
        if val and not str(out.get(key) or "").strip():
            out[key] = val
    addr = str(resolved.get("address") or "").strip()
    if addr and not str(out.get("location") or "").strip():
        out["location"] = addr
    name = str(resolved.get("name") or resolved.get("previewTitle") or "").strip()
    if name and not str(out.get("name") or "").strip():
        out["name"] = name
    img = str(resolved.get("imageUrl") or "").strip()
    if img:
        out["previewImage"] = img
    title = str(resolved.get("previewTitle") or "").strip()
    if title:
        out["previewTitle"] = title
    if resolved.get("mapsEmbedUrl"):
        out["mapsEmbedUrl"] = resolved["mapsEmbedUrl"]
    if resolved.get("placeUrl"):
        out["placeUrl"] = resolved["placeUrl"]
    if resolved.get("mapsUrl"):
        out["mapsUrl"] = resolved["mapsUrl"]
    if resolved.get("sourceType"):
        out["sourceType"] = resolved["sourceType"]
    if resolved.get("mapsProvider"):
        out["mapsProvider"] = resolved["mapsProvider"]
    return out


def re_resolve_shop(entry: dict[str, Any]) -> tuple[dict[str, Any], str]:
    """
    Re-resolve shop map/info with priority Naver → Kakao → Google.

    - Keep existing Naver/Kakao/Google place URLs when present (by priority).
    - If only Google (or none) and we have name/location, upgrade deep-link to
      Naver search URL while keeping Google Maps embed for the iframe.
    """
    name = str(entry.get("name") or "").strip()
    location = str(entry.get("location") or "").strip()
    pref, url = _pick_preferred_url(entry)
    old_st = str(entry.get("sourceType") or "").strip().lower()

    if pref == "naver" and url:
        # Prefer concrete place id URLs; refresh via resolve
        updated = apply_maps_and_preview(
            entry,
            place_url=url,
            location=location,
            name=name,
            source_type="naver",
            fetch_preview=False,
            regenerate=True,
        )
        if re.search(r"/place/\d+", url):
            updated = _enrich_from_resolve(updated, url, "naver")
        label = "naver" if old_st != "naver" else "refresh-naver"
        return updated, label

    if pref == "kakao" and url:
        updated = apply_maps_and_preview(
            entry,
            place_url=url,
            location=location,
            name=name,
            source_type="kakao",
            fetch_preview=False,
            regenerate=True,
        )
        updated = _enrich_from_resolve(updated, url, "kakao")
        label = "kakao" if old_st != "kakao" else "refresh-kakao"
        return updated, label

    # Google only / custom — try upgrade deep-link to Naver search
    naver_q = _naver_search_url(name, location)
    if naver_q:
        updated = dict(entry)
        updated["sourceType"] = "naver"
        updated["placeUrl"] = naver_q
        updated["mapsUrl"] = naver_q
        updated["mapsProvider"] = "naver"
        # Embed must stay Google (Naver blocks iframe)
        embed_q = location or name
        if embed_q:
            updated["mapsEmbedUrl"] = google_embed_from_query(embed_q)
        elif not str(updated.get("mapsEmbedUrl") or "").strip():
            updated["mapsEmbedUrl"] = google_embed_from_query(name or "Korea")
        label = "upgrade-naver-search" if pref in ("", "google") else "naver-search"
        return updated, label

    if pref == "google" and url:
        updated = apply_maps_and_preview(
            entry,
            place_url=url,
            location=location,
            name=name,
            source_type="google",
            fetch_preview=False,
            regenerate=True,
        )
        label = "google" if old_st != "google" else "refresh-google"
        return updated, label

    # Last resort: Kakao search if somehow name exists but Naver skipped
    kakao_q = _kakao_search_url(name, location)
    if kakao_q:
        updated = dict(entry)
        updated["sourceType"] = "kakao"
        updated["placeUrl"] = kakao_q
        updated["mapsUrl"] = kakao_q
        updated["mapsProvider"] = "kakao"
        if location or name:
            updated["mapsEmbedUrl"] = google_embed_from_query(location or name)
        return updated, "kakao-search"

    updated = apply_maps_and_preview(
        entry,
        place_url="",
        location=location,
        name=name,
        source_type="custom",
        fetch_preview=False,
        regenerate=True,
    )
    return updated, "custom"


def strip_body_images(entry: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """Remove image blocks from body; return (entry, removed src paths)."""
    body = entry.get("body")
    if not isinstance(body, list):
        return entry, []
    kept: list[Any] = []
    removed: list[str] = []
    for block in body:
        if isinstance(block, dict) and str(block.get("type") or "").lower() == "image":
            src = str(block.get("src") or "").strip()
            if src:
                removed.append(src)
            continue
        kept.append(block)
    out = dict(entry)
    out["body"] = kept
    return out, removed


def _resolve_media_path(src: str) -> Path | None:
    s = (src or "").strip().replace("\\", "/")
    if not s:
        return None
    if s.startswith("pages/") or s.startswith("Images/"):
        p = ROOT / s
        return p if p.is_file() else None
    # relative media/body-N.jpg — resolve under foods later via glob
    return None


def collect_referenced_paths(bundle: dict[str, Any]) -> set[str]:
    refs: set[str] = set()
    text_blobs: list[str] = []
    for lang in i18n_store.LANGS:
        text_blobs.append(
            Path(ROOT / "i18n" / f"{lang}.json").read_text(encoding="utf-8")
        )
    for html in ROOT.rglob("*.html"):
        if "node_modules" in html.parts:
            continue
        try:
            text_blobs.append(html.read_text(encoding="utf-8"))
        except OSError:
            continue
    joined = "\n".join(text_blobs)
    for m in re.finditer(
        r"(?:pages/foods/[^\s\"'<>]+\.(?:jpg|jpeg|png|webp)|"
        r"Images/[^\s\"'<>]+\.(?:jpg|jpeg|png|webp))",
        joined,
        re.IGNORECASE,
    ):
        refs.add(m.group(0).replace("\\", "/"))
    # Also relative media refs from shop HTML (cover.jpg etc. are local)
    for m in re.finditer(r'src="(media/[^"]+)"', joined, re.IGNORECASE):
        refs.add(m.group(1).replace("\\", "/"))
    return refs


def delete_unreferenced_shop_media(
    *,
    forced_delete: set[Path],
    referenced: set[str],
) -> list[str]:
    """Delete forced tip body images + orphan body/menu files under shop media."""
    notes: list[str] = []
    for path in sorted(forced_delete):
        if path.is_file():
            rel = path.relative_to(ROOT).as_posix()
            path.unlink()
            notes.append(f"deleted tip body: {rel}")

    # Orphan body-*/menu-* under pages/foods/**/media/
    foods = ROOT / "pages" / "foods"
    if not foods.is_dir():
        return notes
    for media_dir in foods.rglob("media"):
        if not media_dir.is_dir():
            continue
        for f in sorted(media_dir.iterdir()):
            if not f.is_file():
                continue
            name = f.name.lower()
            if not (
                name.startswith("body-")
                or name.startswith("menu-")
                or name == "menu.jpg"
            ):
                continue
            if name.startswith("cover"):
                continue
            rel = f.relative_to(ROOT).as_posix()
            # Referenced if full path or basename appears for this shop folder
            shop_rel_media = f"media/{f.name}"
            if rel in referenced or shop_rel_media in referenced:
                continue
            # Also check if any body still points at this file path fragment
            fragment = "/".join(rel.split("/")[-4:])  # dish/shop/media/file
            hit = any(fragment in r or rel in r for r in referenced)
            if hit:
                continue
            f.unlink()
            notes.append(f"deleted orphan: {rel}")
    return notes


def main() -> int:
    bundle = i18n_store.load_all()
    ko_restaurants = bundle["ko"].setdefault("restaurants", {})
    actions: list[tuple[str, str]] = []
    source_counts: Counter[str] = Counter()
    tip_images_removed = 0
    forced_delete: set[Path] = set()
    removed_srcs: list[str] = []

    for slug, ko_entry in sorted(ko_restaurants.items()):
        if not isinstance(ko_entry, dict):
            continue

        # 1) Strip tip/body images from all langs (KO body is canonical)
        stripped, imgs = strip_body_images(ko_entry)
        tip_images_removed += len(imgs)
        removed_srcs.extend(imgs)
        for src in imgs:
            p = _resolve_media_path(src)
            if p:
                forced_delete.add(p)

        # 2) Re-resolve source preference
        updated, action = re_resolve_shop(stripped)
        actions.append((slug, action))
        source_counts[str(updated.get("sourceType") or "(none)")] += 1

        for lang in i18n_store.LANGS:
            restaurants = bundle[lang].setdefault("restaurants", {})
            entry = dict(restaurants.get(slug) or {})
            if lang == "ko":
                # Keep updated body (text only) + map fields
                restaurants[slug] = updated
                continue
            # Sync map/registration fields; strip images from body if present
            entry, _ = strip_body_images(entry)
            # Prefer KO body text blocks (shared structure)
            if isinstance(updated.get("body"), list):
                # Rebuild body: keep per-lang text from existing blocks when possible
                ko_body = updated.get("body") or []
                old_body = entry.get("body") if isinstance(entry.get("body"), list) else []
                new_body: list[dict[str, Any]] = []
                text_idx = 0
                old_texts = [
                    b
                    for b in old_body
                    if isinstance(b, dict) and str(b.get("type") or "").lower() == "text"
                ]
                for block in ko_body:
                    if not isinstance(block, dict):
                        continue
                    if str(block.get("type") or "").lower() != "text":
                        continue
                    if text_idx < len(old_texts):
                        merged = dict(old_texts[text_idx])
                        # Ensure KO matches
                        merged["ko"] = block.get("ko", merged.get("ko", ""))
                        new_body.append(merged)
                    else:
                        new_body.append(dict(block))
                    text_idx += 1
                entry["body"] = new_body
            for key in SYNC_KEYS:
                if key in updated:
                    entry[key] = updated[key]
            restaurants[slug] = entry

    i18n_store.save_all(bundle)
    build_msg = i18n_store.build_bundle()

    # Sync HTML visuals
    visual_notes = sync_all_shop_page_visuals()

    # Collect refs AFTER i18n save (images already stripped)
    referenced = collect_referenced_paths(bundle)
    delete_notes = delete_unreferenced_shop_media(
        forced_delete=forced_delete, referenced=referenced
    )

    version = bump_asset_version()

    print("=== Shop detail cleanup ===")
    for slug, action in actions:
        print(f"  {slug}: {action}")
    print("Re-resolve sourceType counts:", dict(source_counts))
    print(f"Tip/body images removed from i18n: {tip_images_removed}")
    print(f"Files deleted: {len(delete_notes)}")
    for n in delete_notes:
        print(f"  {n}")
    print("Visual sync:")
    for n in visual_notes[:30]:
        print(f"  {n}")
    if len(visual_notes) > 30:
        print(f"  ... +{len(visual_notes) - 30} more")
    print(build_msg)
    print(
        f"Cache version: {version.get('version')} "
        f"(HTML updated {version.get('files_updated')})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
