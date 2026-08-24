# -*- coding: utf-8 -*-
"""Fill leftover place placeholders from verified Commons / exact wiki pages.

Accepts a file only when the Korean place name is in the file title or
description. False-friend photos (하회, 직지사, maps, portraits) are skipped.
Saves to Images/places/{type}/{slug}.jpg (max edge 1280).
"""
from __future__ import annotations

import importlib.util
import io
import json
import re
import shutil
import sys
import time
import urllib.parse
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "fill_ph", ROOT / "tool" / "_fill_placeholder_photos.py"
)
fill = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fill)

COORDS = ROOT / "data" / "places" / "places-coords.js"
I18N_TRANSPORT = ROOT / "i18n" / "pages" / "transport"
SLEEP = 1.7
MAX_EDGE = 1280

SKIP_SLUGS = {
    "nohyeong-supermarket",
    "arte-museum-jeju",
    "seonbichon",
    "yeotju-seonbichon",
    "chwigajeot",
    "gwatju-chwigajeot",
    "hamcheon-salgahyatgyo",
    "yeotju-geundaeyeoksamunhwageori",
    "yeotju-yeotju-geundaeyeoksamunhwageori",
}

# File pages already opened and confirmed as that place.
VERIFIED_FILES: dict[str, str] = {
    "boryeong-lake": "내려다본 보령호.jpg",
}

FALSE_FRIENDS: dict[str, tuple[str, ...]] = {
    "andotminsokchon": ("하회", "hahoe", "한국민속촌", "용인"),
    "andot-andotminsokchon": ("하회", "hahoe", "한국민속촌", "용인"),
    "daegokbakmulgwan": ("반구대", "bangudae", "암각화"),
    "ulsan-daegokbakmulgwan": ("반구대", "bangudae", "암각화"),
    "hwangaksan": ("직지사", "jikjisa"),
    "namdeogyusan": ("무주", "덕유산리조트", "곤돌라"),
    "damyang-lake": ("호국사", "불상"),
    "wolbotseowon": ("김해", "고문서"),
    "gwatju-wolbotseowon": ("김해", "고문서"),
}

EXTRA_QUERIES: dict[str, list[str]] = {
    "andotminsokchon": ["안동민속촌"],
    "andot-andotminsokchon": ["안동민속촌"],
    "daegokbakmulgwan": ["울산대곡박물관", "대곡박물관"],
    "ulsan-daegokbakmulgwan": ["울산대곡박물관", "대곡박물관"],
    "boryeong-lake": ["보령호", "보령댐"],
    "isathwa-gotaek": ["이상화생가", "이상화 고택"],
    "seosatdon-gotaek": ["서상돈생가", "서상돈 고택"],
    "bus-terminal-ulsan": ["울산고속버스터미널"],
}


def dest_for(place: dict) -> Path:
    return fill.IMG / place["type"] / f"{place['slug']}.jpg"


def optimize_jpeg(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(src)
    im = ImageOps.exif_transpose(im)
    if im.mode in ("RGBA", "LA", "P"):
        bg = Image.new("RGB", im.size, (255, 255, 255))
        if im.mode == "P":
            im = im.convert("RGBA")
        bg.paste(im, mask=im.split()[-1] if im.mode == "RGBA" else None)
        im = bg
    elif im.mode != "RGB":
        im = im.convert("RGB")
    if max(im.size) > MAX_EDGE:
        im.thumbnail((MAX_EDGE, MAX_EDGE), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=85, optimize=True, progressive=True)
    tmp = dest.with_suffix(".tmp.jpg")
    tmp.write_bytes(buf.getvalue())
    tmp.replace(dest)


def blob_ok(slug: str, query: str, blob: str) -> bool:
    if query not in blob:
        return False
    low = blob.lower()
    if fill.bad_filename(blob):
        return False
    for part in FALSE_FRIENDS.get(slug, ()):
        if part.lower() in low:
            return False
    if slug.startswith("namdeogyusan") and "남덕유" not in blob and "Namdeogyu" not in blob:
        if "덕유산" in blob and "남" not in blob:
            return False
    return True


def commons_file_meta(file_title: str) -> dict:
    title = file_title if file_title.startswith("File:") else f"File:{file_title}"
    api = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(
        {
            "action": "query",
            "titles": title,
            "prop": "imageinfo",
            "iiprop": "url|size|mime|extmetadata",
            "iiurlwidth": str(MAX_EDGE),
            "format": "json",
        }
    )
    data = json.loads(fill.http_get(api).decode())
    pages = (data.get("query") or {}).get("pages") or {}
    for page in pages.values():
        infos = page.get("imageinfo") or []
        if infos:
            return infos[0]
    return {}


def commons_search_titles(query: str, limit: int = 8) -> list[str]:
    api = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(
        {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srnamespace": "6",
            "srlimit": str(limit),
            "format": "json",
        }
    )
    data = json.loads(fill.http_get(api).decode())
    out = []
    for hit in (data.get("query") or {}).get("search") or []:
        title = hit.get("title") or ""
        if title:
            out.append(title)
    return out


def meta_blob(file_title: str, info: dict) -> str:
    ext = info.get("extmetadata") or {}
    parts = [file_title]
    for key in ("ImageDescription", "ObjectName", "Categories"):
        rec = ext.get(key) or {}
        val = rec.get("value") or ""
        parts.append(re.sub(r"<[^>]+>", " ", str(val)))
    return " ".join(parts)


def file_url(info: dict) -> str | None:
    mime = (info.get("mime") or "").lower()
    if mime not in ("image/jpeg", "image/png", "image/webp"):
        return None
    if int(info.get("size") or 0) < 18000:
        return None
    return info.get("thumburl") or info.get("url")


def try_file(slug: str, query: str, file_title: str, dest: Path, hashes: dict) -> bool:
    time.sleep(SLEEP)
    info = commons_file_meta(file_title)
    blob = meta_blob(file_title, info)
    if not blob_ok(slug, query, blob):
        print(f"    skip name mismatch: {file_title}", flush=True)
        return False
    url = file_url(info)
    if not url:
        return False
    tmp = dest.with_suffix(".dl.bin")
    if not fill.save_image(url, tmp):
        if tmp.exists():
            tmp.unlink()
        return False
    optimize_jpeg(tmp, dest)
    tmp.unlink(missing_ok=True)
    if fill.sha1(dest) in hashes:
        dest.unlink(missing_ok=True)
        print(f"    skip placeholder hash: {file_title}", flush=True)
        return False
    print(f"    OK {file_title} {dest.stat().st_size}b", flush=True)
    return True


def wiki_lead(query: str) -> tuple[str, str] | None:
    api = "https://ko.wikipedia.org/w/api.php?" + urllib.parse.urlencode(
        {
            "action": "query",
            "titles": query,
            "prop": "pageimages|pageprops",
            "pithumbsize": str(MAX_EDGE),
            "piprop": "thumbnail|name|original",
            "redirects": "1",
            "format": "json",
        }
    )
    data = json.loads(fill.http_get(api).decode())
    pages = (data.get("query") or {}).get("pages") or {}
    for page in pages.values():
        if "missing" in page:
            return None
        props = page.get("pageprops") or {}
        if "disambiguation" in props:
            return None
        title = page.get("title") or ""
        if query not in title and title not in query:
            return None
        name = page.get("pageimage") or ""
        thumb = (page.get("thumbnail") or {}).get("source") or ""
        orig = (page.get("original") or {}).get("source") or ""
        hint = f"{title} {name} {thumb} {orig}"
        if fill.bad_filename(hint):
            return None
        src = orig or thumb
        if src and re.search(r"\.(jpe?g)(\?|$)", src, re.I):
            return name, src
    return None


def queries_for(place: dict, ko_names: dict[str, str]) -> list[str]:
    slug = place["slug"]
    out: list[str] = []
    out.extend(EXTRA_QUERIES.get(slug, []))
    ko = ko_names.get(slug, "")
    if ko:
        bare = re.sub(r"\s*\([^)]*\)\s*", " ", ko).strip()
        out.append(bare)
    if place["note"]:
        out.append(place["note"])
    uniq: list[str] = []
    for q in out:
        q = q.strip()
        if q and q not in uniq:
            uniq.append(q)
    return uniq


def rewrite_image_fields(slug_to_image: dict[str, str]) -> None:
    text = COORDS.read_text(encoding="utf-8")
    for slug, image in slug_to_image.items():
        pat = re.compile(rf'(slug:\s*"{re.escape(slug)}"[\s\S]*?image:\s*")[^"]*"')
        text, n = pat.subn(rf'\1{image}"', text, count=1)
        if n != 1:
            print(f"WARN coords not rewritten: {slug}", flush=True)
    COORDS.write_text(text, encoding="utf-8")
    if not I18N_TRANSPORT.exists():
        return
    for path in I18N_TRANSPORT.glob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        places = data.get("places") or {}
        changed = False
        for slug, rec in places.items():
            if not isinstance(rec, dict):
                continue
            img = slug_to_image.get(slug)
            if img and rec.get("image") and rec["image"] != img:
                rec["image"] = img
                changed = True
        if changed:
            path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )


def copy_to_twins(src_place: dict, groups: list[list[dict]], hashes: dict) -> dict[str, str]:
    out: dict[str, str] = {}
    src_slug = src_place["slug"]
    src_path = dest_for(src_place)
    for group in groups:
        slugs = {p["slug"] for p in group}
        if src_slug not in slugs:
            continue
        for p in group:
            if p["slug"] == src_slug:
                continue
            dest = dest_for(p)
            dest.parent.mkdir(parents=True, exist_ok=True)
            if dest.resolve() != src_path.resolve():
                shutil.copy2(src_path, dest)
            if fill.sha1(dest) in hashes:
                dest.unlink(missing_ok=True)
                continue
            out[p["slug"]] = f"Images/places/{p['type']}/{p['slug']}.jpg"
            print(f"    copy -> {p['type']}/{p['slug']}.jpg", flush=True)
        break
    return out


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    hashes = fill.type_hashes()
    places = fill.parse_places()
    ko_names = fill.load_ko_names()
    groups = fill.group_places(places, ko_names)
    remaining = [
        p
        for p in places
        if p["image"].startswith("Images/places/_types/") and p["slug"] not in SKIP_SLUGS
    ]
    print(f"placeholders={len(remaining)} skip={len(SKIP_SLUGS)}", flush=True)
    slug_to_image: dict[str, str] = {}
    ok = 0
    done_canon: set[str] = set()

    for place in remaining:
        slug = place["slug"]
        canon = fill.canonical_slug(slug)
        if canon in done_canon and slug not in slug_to_image:
            continue
        dest = dest_for(place)
        print(f"{slug} ({place['type']}) {ko_names.get(slug, place['note'])}", flush=True)
        saved = False

        verified = VERIFIED_FILES.get(slug)
        if verified:
            q = next((x for x in queries_for(place, ko_names) if x in verified), None)
            if q:
                saved = try_file(slug, q, verified, dest, hashes)

        if not saved:
            for q in queries_for(place, ko_names):
                if not re.search(r"[가-힣]", q):
                    continue
                print(f"  commons {q}", flush=True)
                time.sleep(SLEEP)
                try:
                    titles = commons_search_titles(q)
                except Exception as exc:  # noqa: BLE001
                    print(f"  search err: {exc}", flush=True)
                    continue
                for title in titles:
                    if try_file(slug, q, title, dest, hashes):
                        saved = True
                        break
                if saved:
                    break
                print(f"  wiki {q}", flush=True)
                time.sleep(SLEEP)
                try:
                    lead = wiki_lead(q)
                except Exception as exc:  # noqa: BLE001
                    print(f"  wiki err: {exc}", flush=True)
                    lead = None
                if lead:
                    name, url = lead
                    hint = f"{name} {url}"
                    friends_hit = any(
                        p.lower() in hint.lower() for p in FALSE_FRIENDS.get(slug, ())
                    )
                    if friends_hit or fill.bad_filename(hint):
                        print(f"    skip wiki lead: {name}", flush=True)
                    else:
                        tmp = dest.with_suffix(".dl.bin")
                        if fill.save_image(url, tmp):
                            optimize_jpeg(tmp, dest)
                            tmp.unlink(missing_ok=True)
                            if dest.exists() and fill.sha1(dest) not in hashes:
                                print(f"    OK wiki:{name}", flush=True)
                                saved = True
                            else:
                                dest.unlink(missing_ok=True)
                if saved:
                    break

        if saved and dest.exists():
            ok += 1
            done_canon.add(canon)
            img = f"Images/places/{place['type']}/{slug}.jpg"
            slug_to_image[slug] = img
            slug_to_image.update(copy_to_twins(place, groups, hashes))
        else:
            print("  leave placeholder", flush=True)

    if slug_to_image:
        rewrite_image_fields(slug_to_image)
    print(f"DONE filled={ok} rewritten={len(slug_to_image)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
