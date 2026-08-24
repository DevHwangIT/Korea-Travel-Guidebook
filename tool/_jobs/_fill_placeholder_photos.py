# -*- coding: utf-8 -*-
"""Replace type-placeholder JPGs with real Wikipedia/Commons photos.

Groups duplicate slugs (same Korean name / English note / region prefix) so
each unique place is downloaded once, then copied.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COORDS = ROOT / "data" / "places" / "places-coords.js"
IMG = ROOT / "Images" / "places"
KO_JSON = ROOT / "i18n" / "pages" / "transport" / "ko.json"
LOG = ROOT / "tool" / "_placeholder_fill_log.json"
UA = (
    "KoreaTravelGuidebook/1.0 (place covers; educational offline mirror; "
    "rate-limited)"
)
SLEEP = 2.0
CTX = None
MIN_BYTES = 18000

SKIP_NAME = (
    "logo",
    "icon",
    "map of",
    "locator",
    "flag of",
    "coat of arms",
    "diagram",
    "qr code",
    "infobox",
    "portrait",
    "selfie",
    "headshot",
    "위치도",
    "안내도",
    "노선도",
    "초상",
    "로고",
    "question book",
    "commons-logo",
    "wikimedia",
    "edit-clear",
    "nuvola",
    "crystal_clear",
    "ambox",
    "disambig",
    "padlock",
)

REGION_PREFIXES = (
    "jeonnal-",
    "chutbuk-",
    "gwatju-gwatju-",
    "gwatju-",
    "ulsan-",
    "daejeon-",
    "sejot-",
    "yeotju-",
    "andot-",
    "dalyat-",
)


def ssl_ctx() -> ssl.SSLContext:
    global CTX
    if CTX is None:
        try:
            import certifi

            CTX = ssl.create_default_context(cafile=certifi.where())
        except Exception:
            CTX = ssl._create_unverified_context()
    return CTX


def sha1(path: Path) -> str:
    h = hashlib.sha1()
    h.update(path.read_bytes())
    return h.hexdigest()


def http_get(url: str, timeout: int = 55, retries: int = 2) -> bytes:
    last: Exception | None = None
    for attempt in range(retries):
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=ssl_ctx()) as r:
                return r.read()
        except urllib.error.HTTPError as exc:
            last = exc
            if exc.code in (429, 503):
                wait = 8 * (attempt + 1)
                print(f"  HTTP {exc.code}, wait {wait}s", flush=True)
                time.sleep(wait)
                continue
            if exc.code == 404:
                raise
            time.sleep(1)
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep(1 * (attempt + 1))
    if last:
        raise last
    raise RuntimeError("http_get failed")


def type_hashes() -> dict[str, str]:
    out: dict[str, str] = {}
    types_dir = IMG / "_types"
    if not types_dir.exists():
        return out
    for f in types_dir.glob("*.jpg"):
        out[sha1(f)] = f.stem
    for f in types_dir.glob("*.png"):
        out[sha1(f)] = f.stem
    return out


def parse_places() -> list[dict]:
    text = COORDS.read_text(encoding="utf-8")
    places: list[dict] = []
    for m in re.finditer(
        r'\{\s*slug:\s*"([^"]+)",\s*lat:\s*([^,]+),\s*lng:\s*([^,]+),'
        r'\s*region:\s*"([^"]*)",\s*type:\s*"([^"]+)",\s*note:\s*"([^"]*)",'
        r'\s*image:\s*"([^"]+)"\s*\}',
        text,
    ):
        slug, _a, _b, region, typ, note, image = m.groups()
        places.append(
            {
                "slug": slug,
                "region": region,
                "type": typ,
                "note": note,
                "image": image,
            }
        )
    return places


def load_ko_names() -> dict[str, str]:
    data = json.loads(KO_JSON.read_text(encoding="utf-8"))
    places = data.get("places") or {}
    out: dict[str, str] = {}
    for slug, rec in places.items():
        if isinstance(rec, dict) and rec.get("name"):
            out[slug] = str(rec["name"]).strip()
    return out


def dest_path(slug: str) -> Path:
    return IMG / f"{slug}.jpg"


def is_placeholder(slug: str, hashes: dict[str, str]) -> bool:
    p = dest_path(slug)
    if not p.exists():
        return True
    return sha1(p) in hashes


def norm(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"\s*\([^)]*\)\s*", " ", s)
    s = re.sub(r"[^a-z0-9가-힣]+", "", s)
    return s


def canonical_slug(slug: str) -> str:
    s = slug
    changed = True
    while changed:
        changed = False
        for p in sorted(REGION_PREFIXES, key=len, reverse=True):
            if s.startswith(p) and len(s) > len(p) + 2:
                s = s[len(p) :]
                changed = True
                break
    return s


class UnionFind:
    def __init__(self) -> None:
        self.p: dict[str, str] = {}

    def add(self, x: str) -> None:
        self.p.setdefault(x, x)

    def find(self, x: str) -> str:
        self.add(x)
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[rb] = ra


def group_places(places: list[dict], ko_names: dict[str, str]) -> list[list[dict]]:
    uf = UnionFind()
    by_key: dict[tuple[str, str], list[str]] = defaultdict(list)
    by_slug = {p["slug"]: p for p in places}
    for p in places:
        slug = p["slug"]
        uf.add(slug)
        by_key[("note", norm(p["note"]))].append(slug)
        by_key[("cslug", canonical_slug(slug))].append(slug)
        ko = ko_names.get(slug, "")
        if ko:
            by_key[("ko", norm(ko))].append(slug)
    for slugs in by_key.values():
        if len(slugs) < 2:
            continue
        head = slugs[0]
        for s in slugs[1:]:
            uf.union(head, s)
    buckets: dict[str, list[dict]] = defaultdict(list)
    for p in places:
        buckets[uf.find(p["slug"])].append(p)
    return list(buckets.values())


def bad_filename(name: str) -> bool:
    low = name.lower()
    if any(x in low for x in SKIP_NAME):
        return True
    if low.endswith((".svg", ".pdf", ".gif")):
        return True
    return False


def save_image(url: str, dest: Path) -> bool:
    try:
        if "wikipedia/commons" in url and "/thumb/" in url:
            url = re.sub(r"/\d+px-", "/800px-", url)
        data = http_get(url, timeout=70, retries=3)
    except Exception as exc:  # noqa: BLE001
        print(f"  dl err: {exc}", flush=True)
        return False
    if len(data) < MIN_BYTES:
        print(f"  too small {len(data)}b", flush=True)
        return False
    head = data[:32].lstrip()
    if head.startswith(b"<") or head.startswith(b"%PDF"):
        return False
    ok = (
        data[:3] == b"\xff\xd8\xff"
        or data[:8] == b"\x89PNG\r\n\x1a\n"
        or data[:4] == b"RIFF"
    )
    if not ok:
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        dest.write_bytes(data)
    except OSError:
        try:
            dest.unlink(missing_ok=True)
            dest.write_bytes(data)
        except OSError as exc:
            print(f"  write err: {exc}", flush=True)
            return False
    return True


def wiki_page_bundle(title: str, lang: str) -> dict:
    """One API call: thumbnail + files on the article. Empty dict if missing."""
    api = f"https://{lang}.wikipedia.org/w/api.php?" + urllib.parse.urlencode(
        {
            "action": "query",
            "titles": title,
            "prop": "pageimages|images|pageprops",
            "pithumbsize": "800",
            "piprop": "thumbnail|name|original",
            "imlimit": "12",
            "redirects": "1",
            "format": "json",
        }
    )
    try:
        data = json.loads(http_get(api).decode())
    except Exception as exc:  # noqa: BLE001
        print(f"  wiki {lang} err {title}: {exc}", flush=True)
        return {}
    pages = (data.get("query") or {}).get("pages") or {}
    for page in pages.values():
        if "missing" in page:
            return {}
        props = page.get("pageprops") or {}
        if "disambiguation" in props:
            print(f"  skip disambiguation: {title}", flush=True)
            return {}
        return page
    return {}


def wiki_thumb_from_page(page: dict) -> str | None:
    thumb = page.get("thumbnail") or {}
    orig = page.get("original") or {}
    src = thumb.get("source") or orig.get("source")
    iname = (page.get("pageimage") or "") + " " + (thumb.get("source") or "")
    if src and not bad_filename(iname):
        return src
    return None


GENERIC_PAGE_FILES = (
    "insoo peak",
    "ku-dwa1",
    "nh-da-klgr",
    "sainam cliff",
    "seorak m.t.",
    "question book",
    "commons-logo",
    "folder hex",
    "crystal_clear",
    "nuvola",
    "ambox",
    "wikimedia-logo",
    "edit-clear",
    "padlock",
    "disambig",
    "symbol_support",
    "increase2",
    "decrease2",
    "red pog",
    "green pog",
    "blue pog",
)


def strip_file_prefix(title: str) -> str:
    t = title.strip()
    for prefix in ("File:", "파일:"):
        if t.startswith(prefix):
            return t[len(prefix) :]
    return t


def is_generic_file(name: str) -> bool:
    low = name.lower()
    return any(g in low for g in GENERIC_PAGE_FILES)


def wiki_files_from_page(page: dict) -> list[str]:
    out = []
    for img in page.get("images") or []:
        t = strip_file_prefix(img.get("title") or "")
        if bad_filename(t) or is_generic_file(t):
            continue
        low = t.lower()
        if not any(low.endswith(ext) for ext in (".jpg", ".jpeg", ".png", ".webp")):
            continue
        out.append(t)
    return out


def wiki_pageimage(title: str, lang: str) -> str | None:
    page = wiki_page_bundle(title, lang)
    if not page:
        return None
    src = wiki_thumb_from_page(page)
    if src:
        return src
    for file_title in wiki_files_from_page(page)[:6]:
        url = commons_thumb_url(file_title)
        if url:
            return url
    return None


def wiki_opensearch(query: str, lang: str) -> list[str]:
    api = f"https://{lang}.wikipedia.org/w/api.php?" + urllib.parse.urlencode(
        {
            "action": "opensearch",
            "search": query,
            "limit": "4",
            "namespace": "0",
            "format": "json",
        }
    )
    try:
        data = json.loads(http_get(api).decode())
    except Exception as exc:  # noqa: BLE001
        print(f"  opensearch err: {exc}", flush=True)
        return []
    if isinstance(data, list) and len(data) > 1:
        return list(data[1] or [])
    return []


def commons_search(query: str, limit: int = 6) -> list[str]:
    api = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(
        {
            "action": "query",
            "list": "search",
            "srsearch": f"{query} filetype:bitmap",
            "srnamespace": "6",
            "srlimit": str(limit),
            "format": "json",
        }
    )
    try:
        data = json.loads(http_get(api).decode())
    except Exception as exc:  # noqa: BLE001
        print(f"  commons search err: {exc}", flush=True)
        return []
    out = []
    for item in data.get("query", {}).get("search", []):
        t = item.get("title", "")
        t = strip_file_prefix(t)
        if bad_filename(t):
            continue
        out.append(t)
    return out


def commons_thumb_url(title: str, width: int = 1280) -> str | None:
    api = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(
        {
            "action": "query",
            "titles": f"File:{title}",
            "prop": "imageinfo",
            "iiprop": "url|mime",
            "iiurlwidth": str(width),
            "format": "json",
        }
    )
    try:
        data = json.loads(http_get(api).decode())
    except Exception as exc:  # noqa: BLE001
        print(f"  imageinfo err: {exc}", flush=True)
        return None
    for page in data.get("query", {}).get("pages", {}).values():
        if "missing" in page:
            return None
        infos = page.get("imageinfo") or []
        if not infos:
            return None
        info = infos[0]
        mime = (info.get("mime") or "").lower()
        if not mime.startswith("image/") or "svg" in mime:
            return None
        return info.get("thumburl") or info.get("url")
    return None


def name_in_candidate(candidate: str, keys: list[str]) -> bool:
    c = re.sub(r"[\s\-_]+", "", candidate.lower())
    for k in keys:
        kn = re.sub(r"[\s\-_]+", "", k.lower())
        if len(kn) >= 2 and kn in c:
            return True
        if k.lower() in candidate.lower():
            return True
    return False


def titles_for(place: dict, ko_names: dict[str, str]) -> list[str]:
    slug = place["slug"]
    note = place["note"]
    titles: list[str] = []
    ko = ko_names.get(slug, "")
    if ko:
        titles.append(ko)
        stripped = re.sub(r"\s*\([^)]*\)\s*", " ", ko).strip()
        if stripped:
            titles.append(stripped)
        titles.append(re.sub(r"\s+", "", stripped or ko))
    bare = re.sub(r"\s*\([^)]*\)\s*", " ", note).strip()
    if bare:
        titles.append(bare)
        first = re.split(r"[,&/]", bare)[0].strip()
        if first and first not in titles:
            titles.append(first)
    out: list[str] = []
    for t in titles:
        t = t.strip()
        if t and t not in out:
            out.append(t)
    return out


def try_save(src: str, dest: Path, hashes: dict[str, str], label: str) -> bool:
    if not src:
        return False
    if save_image(src, dest) and sha1(dest) not in hashes:
        print(f"    OK {label} {dest.stat().st_size}b", flush=True)
        return True
    if dest.exists() and sha1(dest) in hashes:
        dest.unlink()
    return False


def rest_summary_thumb(title: str, lang: str = "ko") -> str | None:
    api = (
        f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/"
        + urllib.parse.quote(title.replace(" ", "_"))
    )
    try:
        data = json.loads(http_get(api, timeout=40, retries=2).decode())
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        print(f"  rest {lang} {title}: {exc}", flush=True)
        return None
    except Exception as exc:  # noqa: BLE001
        print(f"  rest {lang} {title}: {exc}", flush=True)
        return None
    if data.get("type") == "disambiguation":
        return None
    thumb = data.get("thumbnail") or {}
    orig = data.get("originalimage") or {}
    src = orig.get("source") or thumb.get("source")
    title_hint = (data.get("title") or "") + " " + (src or "")
    if src and not bad_filename(title_hint):
        return src
    return None


def fetch_one(place: dict, ko_names: dict[str, str], hashes: dict[str, str]) -> tuple[bool, str]:
    slug = place["slug"]
    dest = dest_path(slug)
    titles = titles_for(place, ko_names)
    ko = ko_names.get(slug, "")
    stripped_ko = re.sub(r"\s*\([^)]*\)\s*", " ", ko).strip() if ko else ""
    bare = re.sub(r"\s*\([^)]*\)\s*", " ", place["note"]).strip()

    tried: set[str] = set()
    for title in (stripped_ko, ko, bare):
        if not title or title in tried:
            continue
        tried.add(title)
        lang = "ko" if re.search(r"[가-힣]", title) else "en"
        print(f"  rest {lang}: {title}", flush=True)
        time.sleep(SLEEP)
        src = rest_summary_thumb(title, lang)
        if try_save(src, dest, hashes, f"rest:{lang}:{title}"):
            return True, f"rest:{lang}:{title}"

    q = stripped_ko or bare
    if q:
        print(f"  commons: {q}", flush=True)
        time.sleep(SLEEP)
        for file_title in commons_search(q, limit=3):
            print(f"  commons file: {file_title}", flush=True)
            time.sleep(SLEEP)
            url = commons_thumb_url(file_title)
            if try_save(url, dest, hashes, f"commons:{file_title}"):
                return True, f"commons:{file_title}"
    return False, ""


def copy_to(src_slug: str, dest_slug: str) -> None:
    if src_slug == dest_slug:
        return
    shutil.copy2(dest_path(src_slug), dest_path(dest_slug))


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--sleep", type=float, default=2.0)
    ap.add_argument("--copy-only", action="store_true")
    args = ap.parse_args()
    global SLEEP
    SLEEP = max(1.2, float(args.sleep))

    hashes = type_hashes()
    if not hashes:
        print("no _types hashes", file=sys.stderr)
        return 1
    ko_names = load_ko_names()
    places = parse_places()
    need = [p for p in places if is_placeholder(p["slug"], hashes)]
    print(
        f"places={len(places)} placeholder={len(need)} ko_names={len(ko_names)}",
        flush=True,
    )

    groups = group_places(need, ko_names)
    # Also attach already-real photos that share a group key with placeholders
    real = [p for p in places if not is_placeholder(p["slug"], hashes)]
    extra_groups = group_places(need + real, ko_names)

    copied = 0
    still_need_groups: list[list[dict]] = []
    seen_need: set[str] = set()

    for g in extra_groups:
        ph = [p for p in g if is_placeholder(p["slug"], hashes)]
        good = [p for p in g if not is_placeholder(p["slug"], hashes)]
        if not ph:
            continue
        if good:
            src = good[0]["slug"]
            for p in ph:
                copy_to(src, p["slug"])
                copied += 1
                print(f"COPY {src} -> {p['slug']}", flush=True)
            continue
        key = tuple(sorted(p["slug"] for p in ph))
        if key in seen_need:
            continue
        seen_need.add(key)
        still_need_groups.append(ph)

    print(f"copied_from_existing={copied} groups_to_download={len(still_need_groups)}", flush=True)
    if args.copy_only:
        remain = sum(1 for p in parse_places() if is_placeholder(p["slug"], hashes))
        print(f"placeholder_remaining={remain}", flush=True)
        return 0

    if args.limit > 0:
        still_need_groups = still_need_groups[: args.limit]

    ok = miss = 0
    run_ok: list[str] = []
    run_miss: list[dict] = []

    for i, group in enumerate(still_need_groups, 1):
        primary = group[0]
        others = group[1:]
        print(
            f"\n[{i}/{len(still_need_groups)}] {primary['slug']} — "
            f"{ko_names.get(primary['slug'], primary['note'])} "
            f"(+{len(others)} copies)",
            flush=True,
        )
        success, used = fetch_one(primary, ko_names, hashes)
        if success:
            ok += 1
            run_ok.append(primary["slug"])
            for p in others:
                copy_to(primary["slug"], p["slug"])
                print(f"  COPY -> {p['slug']}", flush=True)
            print(f"  SOURCE {used}", flush=True)
        else:
            miss += 1
            run_miss.append(
                {
                    "slug": primary["slug"],
                    "note": primary["note"],
                    "ko": ko_names.get(primary["slug"], ""),
                    "also": [p["slug"] for p in others],
                }
            )
            print("  MISS", flush=True)

    remain = sum(1 for p in parse_places() if is_placeholder(p["slug"], hashes))
    log = {
        "copied_from_existing": copied,
        "downloaded": run_ok,
        "miss": run_miss,
        "ok": ok,
        "miss_count": miss,
        "placeholder_remaining": remain,
    }
    LOG.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"\nDONE copy={copied} download={ok} miss={miss} remaining={remain}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
