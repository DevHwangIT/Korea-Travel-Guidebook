# -*- coding: utf-8 -*-
"""Download real heritage cover photos (Wikipedia REST thumbs + Commons).

Prefer Wikipedia page summary thumbnails (rate-friendlier). Fall back to
Wikimedia Commons search. Never invent AI images — leave type fallback.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COORDS = ROOT / "data" / "places" / "places-coords.js"
IMG = ROOT / "Images" / "places"
TYPE_FALLBACK = IMG / "_types" / "heritage.jpg"
LOG = ROOT / "tool" / "_heritage_image_fetch_log.json"
UA = (
    "KoreaTravelGuidebook/1.0 (https://github.com/; heritage place covers; "
    "offline mirror for personal guidebook; rate-limited)"
)
CTX = None
SLEEP = 4.0

# slug -> English Wikipedia title(s)
WIKI_TITLES: dict[str, list[str]] = {
    "chatdeokgut": ["Changdeokgung"],
    "chatgyeotgut": ["Changgyeonggung"],
    "deoksugut": ["Deoksugung"],
    "gyeothuigut": ["Gyeonghuigung"],
    "jotmyo": ["Jongmyo"],
    "nalsangolhanokmaeul": ["Namsangol Hanok Village"],
    "hanyatdoseot": ["Seoul City Wall"],
    "sutryemun": ["Sungnyemun"],
    "heutinjimun": ["Heunginjimun"],
    "gwathwamun": ["Gwanghwamun"],
    "unhyeongut": ["Unhyeongung"],
    "seodaemunhyeotmusoyeoksagwan": ["Seodaemun Prison"],
    "dokrimmun": ["Independence Gate"],
    "tamgolgotwon": ["Tapgol Park"],
    "bosingak": ["Bosingak"],
    "boteunsa": ["Bongeunsa"],
    "jingwansa": ["Jingwansa"],
    "gilsatsa": ["Gilsangsa"],
    "seotgyungwan": ["Sungkyunkwan"],
    "hwaseothaetgut": ["Hwaseong Haenggung"],
    "nalhansanseot": ["Namhansanseong"],
    "sinreuksa": ["Silleuksa"],
    "yotjusa": ["Yongjusa"],
    "beoleosa": ["Beomeosa"],
    "dothwasa": ["Donghwasa"],
    "seokgulal": ["Seokguram"],
    "bunhwatsa": ["Bunhwangsa"],
    "hwatryotsaji": ["Hwangnyongsa"],
    "gotsanseot": ["Gongsanseong"],
    "gotju-magoksa": ["Magoksa"],
    "busosanseot": ["Busosanseong"],
    "naksansa": ["Naksansa"],
    "woljeotsa": ["Woljeongsa"],
    "haeinsa": ["Haeinsa"],
    "totdosa": ["Tongdosa"],
    "beomjusa": ["Beopjusa"],
    "buseoksa": ["Buseoksa"],
    "sotgwatsa": ["Songgwangsa"],
    "suncheon-sotgwatsa": ["Songgwangsa"],
    "gurye-hwaeolsa": ["Hwaeomsa"],
    "suncheon-seonalsa": ["Seonamsa"],
    "buan-naesosa": ["Naesosa"],
    "gilje-geulsansa": ["Geumsansa"],
    "jinjuseot": ["Jinjuseong"],
    "chokseokru": ["Chokseongnu", "촉석루"],
    "dalyat-soswaewon": ["Soswaewon"],
    "gwandeokjeot": ["Gwandeokjeong", "관덕정"],
    "ojeukheon": ["Ojukheon"],
    "seotgyejang": ["Seongyojang"],
    "dosanseowon": ["Dosan Seowon"],
    "byeotsanseowon": ["Byeongsan Seowon"],
    "gyeotgijeon": ["Gyeonggijeon", "경기전"],
    "suncheon-nakaneumseot": ["Naganeupseong"],
    "gathwa-jeondeutsa": ["Jeondeungsa"],
    "haemieumseot": ["Haemieupseong", "해미읍성"],
    "hwaseothaetgut": ["Hwaseong Haenggung", "화성행궁"],
    "jingwansa": ["Jingwansa", "진관사"],
    "gapbawi": ["Gatbawi"],
    "bialsa": ["Biamsa", "비암사"],
    "bogyeotsa": ["Bogyeongsa", "보경사"],
    "andot-bothwatsa": ["Bonghwangsa", "봉황사"],
    "motchontoseot": ["Mongchontoseong"],
    "putnamtoseot": ["Pungnaptoseong"],
    "hangukminsokchon": ["Korean Folk Village"],
    "gwatmyeotdotgul": ["Gwangmyeong Cave"],
    "sejotdaewatreut": ["Royal Tomb of King Sejong", "Yeongnyeongneung"],
    "yutgeonreut": ["Yungneung", "Geolleung"],
    "gwatreut": ["Gwangneung"],
    "gathwa-goindol": ["Ganghwa Dolmen", "Gochang, Hwasun and Ganghwa Dolmen Sites"],
    "gathwa-chojijin": ["Chojijin"],
    "gathwa-gwatseotbo": ["Gwangseongbo"],
    "gathwa-deokjinjin": ["Deokjinjin"],
    "gathwa-oegyujatgak": ["Oegyujanggak"],
    "cheotseotdae": ["Cheomseongdae"],
    "seokgulal": ["Seokguram"],
    "donalseowon": ["Donam Seowon", "Donamseowon"],
    "heutinjimun": ["Heunginjimun"],
    "sutryemun": ["Sungnyemun"],
    "naksansa": ["Naksansa"],
    "woljeotsa": ["Woljeongsa"],
    "totdosa": ["Tongdosa"],
    "nalhansanseot": ["Namhansanseong"],
    "bosingak": ["Bosingak"],
    "unhyeongut": ["Unhyeongung"],
}


def ssl_ctx() -> ssl.SSLContext:
    global CTX
    if CTX is None:
        try:
            import certifi

            CTX = ssl.create_default_context(cafile=certifi.where())
        except Exception:
            CTX = ssl._create_unverified_context()
    return CTX


def md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def http_get(url: str, timeout: int = 50, retries: int = 3) -> bytes:
    last: Exception | None = None
    for attempt in range(retries):
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=ssl_ctx()) as r:
                return r.read()
        except urllib.error.HTTPError as exc:
            last = exc
            if exc.code in (429, 503):
                wait = 20 * (attempt + 1)
                print(f"  HTTP {exc.code}, wait {wait}s", flush=True)
                time.sleep(wait)
                continue
            if exc.code == 404:
                raise
            time.sleep(2)
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep(2 * (attempt + 1))
    if last:
        raise last
    raise RuntimeError("http_get failed")


def parse_heritage_places() -> list[dict]:
    text = COORDS.read_text(encoding="utf-8")
    places: list[dict] = []
    for m in re.finditer(
        r'\{\s*slug:\s*"([^"]+)",\s*lat:\s*([^,]+),\s*lng:\s*([^,]+),'
        r'\s*region:\s*"([^"]*)",\s*type:\s*"([^"]+)",\s*note:\s*"([^"]*)",'
        r'\s*image:\s*"([^"]+)"\s*\}',
        text,
    ):
        slug, _a, _b, region, typ, note, image = m.groups()
        if typ != "heritage":
            continue
        places.append({"slug": slug, "note": note, "region": region, "image": image})
    return places


def needs_photo(slug: str, fallback_hash: str) -> bool:
    dest = IMG / f"{slug}.jpg"
    if not dest.exists():
        return True
    return md5(dest) == fallback_hash


def note_to_wiki_titles(note: str) -> list[str]:
    bare = re.sub(r"\s*\([^)]*\)\s*", " ", note).strip()
    titles = [bare]
    # first multi-word chunk before comma/&
    first = re.split(r"[,&/]", bare)[0].strip()
    if first and first not in titles:
        titles.append(first)
    # drop trailing generic nouns for page title guess
    for drop in (
        " Palace",
        " Temple",
        " Fortress",
        " Shrine",
        " Village",
        " Museum",
        " Park",
        " Gate",
        " Tomb",
        " Tombs",
        " Site",
        " Hall",
        " Bridge",
        " Garden",
        " Pavilion",
    ):
        if first.endswith(drop):
            titles.append(first[: -len(drop)].strip())
    # dedupe preserve order
    out: list[str] = []
    for t in titles:
        if t and t not in out:
            out.append(t)
    return out[:4]


def wiki_opensearch(query: str, lang: str = "en") -> list[str]:
    api = f"https://{lang}.wikipedia.org/w/api.php?" + urllib.parse.urlencode(
        {
            "action": "opensearch",
            "search": query,
            "limit": "3",
            "namespace": "0",
            "format": "json",
        }
    )
    try:
        data = json.loads(http_get(api).decode())
    except Exception as exc:  # noqa: BLE001
        print(f"  opensearch err: {exc}", flush=True)
        return []
    # [query, [titles], [descs], [urls]]
    if isinstance(data, list) and len(data) > 1:
        return list(data[1] or [])
    return []


def wiki_summary_thumb(title: str, lang: str = "en") -> str | None:
    api = (
        f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/"
        + urllib.parse.quote(title.replace(" ", "_"))
    )
    try:
        data = json.loads(http_get(api).decode())
    except Exception as exc:  # noqa: BLE001
        print(f"  wiki miss ({lang}): {title} ({exc})", flush=True)
        return None
    if data.get("type") == "disambiguation":
        return None
    thumb = data.get("thumbnail") or {}
    src = thumb.get("source")
    if not src:
        orig = data.get("originalimage") or {}
        src = orig.get("source")
    return src


def commons_search(query: str, limit: int = 5) -> list[str]:
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
        if t.startswith("File:"):
            t = t[5:]
        low = t.lower()
        if any(x in low for x in (".pdf", ".svg", "map of", "locator", "logo", "icon")):
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
        if not mime.startswith("image/") or "svg" in mime or "pdf" in mime:
            return None
        return info.get("thumburl") or info.get("url")
    return None


def core_name_tokens(note: str) -> list[str]:
    """Distinctive proper-name tokens from English note (not generic nouns)."""
    bare = re.sub(r"\s*\([^)]*\)\s*", " ", note).strip()
    first = re.split(r"[,&/]", bare)[0].strip()
    fillers = {
        "palace",
        "temple",
        "fortress",
        "shrine",
        "village",
        "museum",
        "park",
        "gate",
        "tomb",
        "tombs",
        "royal",
        "site",
        "historic",
        "history",
        "hall",
        "bridge",
        "garden",
        "pavilion",
        "national",
        "korea",
        "korean",
        "modern",
        "underwater",
        "japanese",
        "foreign",
        "missionary",
        "cemetery",
        "general",
        "king",
        "seowon",
        "eupseong",
        "sanseong",
        "and",
        "the",
        "of",
        "for",
    }
    toks = [w.lower() for w in re.findall(r"[A-Za-z가-힣0-9]+", first)]
    keys = [w for w in toks if len(w) >= 4 and w not in fillers]
    if not keys:
        keys = [w for w in toks if len(w) >= 3 and w not in fillers]
    return keys


def names_match(candidate: str, note: str) -> bool:
    """Require the place's primary proper name to appear in wiki/commons title."""
    keys = core_name_tokens(note)
    if not keys:
        return False
    c_raw = candidate.lower()
    c = re.sub(r"[\s\-_]+", "", c_raw)
    k = re.sub(r"[\s\-_]+", "", keys[0])
    latin_ok = bool(k and k in c) or (keys[0] in c_raw)

    # Reject obvious off-topic museum/artifact shots for place covers
    if "museum" in note.lower():
        bad = ("university museum", "항아리", "pottery", "artifact")
        if any(b in c_raw for b in bad) and "bakmul" not in c and "박물관" not in candidate:
            return False

    if latin_ok:
        return True

    # Hangul Commons titles: only when title has Hangul AND no conflicting Latin mismatch.
    # Do NOT accept Hangul-only just because search returned it — too many false friends.
    return False


def save_image(url: str, dest: Path) -> bool:
    try:
        # prefer larger wiki thumbs
        if "wikipedia/commons" in url and "/thumb/" in url:
            # bump size if small
            url = re.sub(r"/\d+px-", "/1280px-", url)
        data = http_get(url, timeout=70, retries=2)
    except Exception as exc:  # noqa: BLE001
        print(f"  dl err: {exc}", flush=True)
        return False
    if len(data) < 6000:
        return False
    head = data[:32].lstrip()
    if head.startswith(b"<") or head.startswith(b"%PDF"):
        return False
    ok = (
        data[:3] == b"\xff\xd8\xff"
        or data[:8] == b"\x89PNG\r\n\x1a\n"
        or data[:4] == b"RIFF"
        or data[:6] in (b"GIF87a", b"GIF89a")
    )
    if not ok:
        return False
    dest.write_bytes(data)
    return True


def fetch_place(
    slug: str, note: str, fallback_hash: str, *, wiki_only: bool = False
) -> tuple[bool, str]:
    dest = IMG / f"{slug}.jpg"
    titles = list(WIKI_TITLES.get(slug, []))
    for t in note_to_wiki_titles(note):
        if t not in titles:
            titles.append(t)

    # Wikipedia EN then KO for mapped/Korean titles
    tried_titles: list[str] = []
    for title in titles[:3]:
        tried_titles.append(title)
        if not re.search(r"[가-힣]", title) and not names_match(title, note):
            # skip obviously mismatched curated/guessed Latin titles
            continue
        is_ko = bool(re.search(r"[가-힣]", title))
        langs = ("ko", "en") if is_ko else ("en",)
        for lang in langs:
            print(f"  wiki {lang}: {title}", flush=True)
            time.sleep(SLEEP)
            src = wiki_summary_thumb(title, lang=lang)
            if not src:
                continue
            if not names_match(title, note) and not is_ko:
                print(f"  skip name mismatch: {title}", flush=True)
                continue
            if save_image(src, dest) and md5(dest) != fallback_hash:
                if dest.stat().st_size < 20000:
                    print("    too small, reject", flush=True)
                    continue
                print(f"    OK wiki {dest.stat().st_size}b", flush=True)
                return True, f"wiki:{lang}:{title}"

    # OpenSearch to resolve alternate spellings
    bare = re.sub(r"\s*\([^)]*\)\s*", " ", note).strip()
    time.sleep(SLEEP)
    for hit in wiki_opensearch(bare, "en")[:2]:
        if hit in tried_titles:
            continue
        if not names_match(hit, note):
            print(f"  skip search mismatch: {hit}", flush=True)
            continue
        print(f"  wiki en (search): {hit}", flush=True)
        time.sleep(SLEEP)
        src = wiki_summary_thumb(hit, lang="en")
        if src and save_image(src, dest) and md5(dest) != fallback_hash:
            if dest.stat().st_size < 20000:
                print("    too small, reject", flush=True)
                continue
            print(f"    OK wiki {dest.stat().st_size}b", flush=True)
            return True, f"wiki:en:{hit}"

    if wiki_only:
        return False, ""

    # Commons search once
    print(f"  commons search: {note}", flush=True)
    time.sleep(SLEEP)
    for file_title in commons_search(note, limit=4):
        if not names_match(file_title, note):
            print(f"  skip unrelated: {file_title}", flush=True)
            continue
        print(f"  commons: {file_title}", flush=True)
        time.sleep(SLEEP)
        url = commons_thumb_url(file_title)
        if not url:
            continue
        if save_image(url, dest) and md5(dest) != fallback_hash:
            if dest.stat().st_size < 20000:
                print("    too small, reject", flush=True)
                continue
            print(f"    OK commons {dest.stat().st_size}b", flush=True)
            return True, f"commons:{file_title}"
    return False, ""


def priority_key(slug: str, note: str) -> tuple[int, str]:
    if slug in WIKI_TITLES:
        return (0, slug)
    n = note.lower()
    if any(
        k in n
        for k in (
            "palace",
            "temple",
            "fortress",
            "shrine",
            "seowon",
            "tomb",
            "gate",
            "hanok",
            "museum",
        )
    ):
        return (1, slug)
    return (2, slug)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--offset", type=int, default=0)
    ap.add_argument("--only", type=str, default="")
    ap.add_argument("--sleep", type=float, default=4.0)
    ap.add_argument("--wiki-only", action="store_true", help="Skip Commons fallback")
    args = ap.parse_args()
    global SLEEP
    SLEEP = max(1.5, float(args.sleep))

    fallback_hash = md5(TYPE_FALLBACK)
    IMG.mkdir(parents=True, exist_ok=True)
    places = parse_heritage_places()
    need = [p for p in places if needs_photo(p["slug"], fallback_hash)]
    already = len(places) - len(need)
    print(f"heritage total={len(places)} real={already} need={len(need)}", flush=True)

    if args.only:
        only = {s.strip() for s in args.only.split(",") if s.strip()}
        need = [p for p in need if p["slug"] in only]
    need.sort(key=lambda p: priority_key(p["slug"], p["note"]))
    if args.offset:
        need = need[args.offset :]
    if args.limit > 0:
        need = need[: args.limit]

    # merge previous log
    prev: dict = {}
    if LOG.exists():
        try:
            prev = json.loads(LOG.read_text(encoding="utf-8"))
        except Exception:
            prev = {}
    ok_all = list(prev.get("ok") or [])
    miss_all = list(prev.get("miss") or [])

    ok = miss = 0
    run_ok: list[str] = []
    run_miss: list[dict] = []

    for i, place in enumerate(need, 1):
        slug, note = place["slug"], place["note"]
        print(f"\n[{i}/{len(need)}] {slug} — {note}", flush=True)
        success, used = fetch_place(
            slug, note, fallback_hash, wiki_only=bool(args.wiki_only)
        )
        if success:
            ok += 1
            run_ok.append(slug)
            if slug not in ok_all:
                ok_all.append(slug)
            miss_all = [m for m in miss_all if (m.get("slug") if isinstance(m, dict) else m) != slug]
            print(f"  SOURCE {used}", flush=True)
        else:
            miss += 1
            run_miss.append({"slug": slug, "note": note})
            print("  MISS — keep fallback", flush=True)
        time.sleep(0.5)

    places2 = parse_heritage_places()
    still = sum(1 for p in places2 if needs_photo(p["slug"], fallback_hash))
    real = len(places2) - still
    log = {
        "ok": ok_all,
        "miss": run_miss + [m for m in miss_all if isinstance(m, dict)],
        "run_ok": run_ok,
        "run_miss": run_miss,
        "summary": {
            "total": len(places2),
            "real_now": real,
            "fallback_remaining": still,
            "replaced_this_run": ok,
            "missed_this_run": miss,
        },
    }
    LOG.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"\nDONE replaced={ok} miss={miss} real_now={real} fallback_remaining={still}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
