# -*- coding: utf-8 -*-
"""Best-effort place page scraping (Naver first; Kakao/Google OG fallback).

Fetches public place HTML with a browser-like User-Agent, parses Apollo /
Open Graph payloads, and returns structured shop fields. Results are disk-
cached under tool/.cache/place_scrape/ to avoid repeated hits.
"""
from __future__ import annotations

import hashlib
import html as html_lib
import json
import re
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urlparse
from urllib.request import Request, urlopen

TOOL_DIR = Path(__file__).resolve().parent.parent
CACHE_DIR = TOOL_DIR / ".cache" / "place_scrape"

_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

_DEFAULT_TIMEOUT = 12.0
_MIN_GAP_SEC = 0.8
_last_fetch_at = 0.0

_NAVER_PLACE_ID_RE = re.compile(
    r"(?:/entry/place/|/place/|/restaurant/|/cafe/|/attraction/|/hospital/|/nailshop/)"
    r"(\d{5,})",
    re.IGNORECASE,
)


def naver_place_id_from_url(url: str) -> str:
    u = (url or "").strip()
    if not u:
        return ""
    m = _NAVER_PLACE_ID_RE.search(u)
    if m:
        return m.group(1)
    m = re.search(r"[?&]id=(\d{5,})", u)
    return m.group(1) if m else ""


def naver_canonical_place_url(place_id: str) -> str:
    pid = (place_id or "").strip()
    if not pid:
        return ""
    return f"https://map.naver.com/p/entry/place/{pid}"


def _throttle() -> None:
    global _last_fetch_at
    now = time.monotonic()
    wait = _MIN_GAP_SEC - (now - _last_fetch_at)
    if wait > 0:
        time.sleep(wait)
    _last_fetch_at = time.monotonic()


def _cache_path(key: str, ext: str = "html") -> Path:
    digest = hashlib.sha1(key.encode("utf-8")).hexdigest()[:24]
    safe = re.sub(r"[^a-zA-Z0-9._-]+", "_", key)[:80]
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR / f"{safe}_{digest}.{ext}"


def fetch_text(
    url: str,
    *,
    timeout: float = _DEFAULT_TIMEOUT,
    cache_ttl: float = 6 * 3600,
    force: bool = False,
) -> str:
    """GET url as text with disk cache. Never raises — returns '' on failure."""
    target = (url or "").strip()
    if not target.startswith("http"):
        return ""
    path = _cache_path(target, "html")
    if not force and path.is_file():
        age = time.time() - path.stat().st_mtime
        if age < cache_ttl and path.stat().st_size > 200:
            try:
                return path.read_text(encoding="utf-8")
            except OSError:
                pass
    _throttle()
    try:
        req = Request(
            target,
            headers={
                "User-Agent": _UA,
                "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
                "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
                "Referer": "https://map.naver.com/",
            },
            method="GET",
        )
        with urlopen(req, timeout=timeout) as resp:
            raw = resp.read(1_200_000)
            ctype = (resp.headers.get("Content-Type") or "").lower()
        charset = "utf-8"
        m = re.search(r"charset=([\w-]+)", ctype)
        if m:
            charset = m.group(1)
        try:
            text = raw.decode(charset, errors="replace")
        except LookupError:
            text = raw.decode("utf-8", errors="replace")
        try:
            path.write_text(text, encoding="utf-8")
        except OSError:
            pass
        return text
    except (HTTPError, URLError, TimeoutError, ValueError, OSError):
        return ""
    except Exception:
        return ""


def fetch_bytes(
    url: str,
    *,
    timeout: float = _DEFAULT_TIMEOUT,
    max_bytes: int = 12_000_000,
) -> bytes:
    target = (url or "").strip()
    if not target.startswith("http"):
        return b""
    _throttle()
    try:
        req = Request(
            target,
            headers={
                "User-Agent": _UA,
                "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
                "Referer": "https://map.naver.com/",
            },
            method="GET",
        )
        with urlopen(req, timeout=timeout) as resp:
            return resp.read(max_bytes)
    except (HTTPError, URLError, TimeoutError, ValueError, OSError):
        return b""
    except Exception:
        return b""


def extract_js_object(html: str, marker: str) -> dict[str, Any] | None:
    """Extract a JSON object assigned after ``marker`` (e.g. window.__APOLLO_STATE__ =)."""
    if not html or not marker:
        return None
    m = re.search(re.escape(marker), html)
    if not m:
        return None
    start = html.find("{", m.end())
    if start < 0:
        return None
    depth = 0
    in_str = False
    esc = False
    quote_c = ""
    i = start
    n = len(html)
    # Cap scan to keep pathological pages bounded
    limit = min(n, start + 2_000_000)
    while i < limit:
        ch = html[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == quote_c:
                in_str = False
        else:
            if ch in ("'", '"'):
                in_str = True
                quote_c = ch
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    try:
                        data = json.loads(html[start : i + 1])
                    except json.JSONDecodeError:
                        return None
                    return data if isinstance(data, dict) else None
        i += 1
    return None


def extract_apollo_state(html: str) -> dict[str, Any] | None:
    for marker in (
        "window.__APOLLO_STATE__ =",
        "window.__APOLLO_STATE__=",
        "__APOLLO_STATE__ =",
    ):
        data = extract_js_object(html, marker)
        if data:
            return data
    return None


def _meta_content(html: str, *, prop: str = "", name: str = "") -> str:
    if prop:
        pats = (
            rf'<meta[^>]+property=["\']{re.escape(prop)}["\'][^>]+content=["\']([^"\']+)["\']',
            rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']{re.escape(prop)}["\']',
        )
    else:
        pats = (
            rf'<meta[^>]+name=["\']{re.escape(name)}["\'][^>]+content=["\']([^"\']+)["\']',
            rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']{re.escape(name)}["\']',
        )
    for pat in pats:
        m = re.search(pat, html, re.IGNORECASE)
        if m:
            return html_lib.unescape(m.group(1).strip())
    return ""


def _clean_title(title: str) -> str:
    t = (title or "").strip()
    if not t:
        return ""
    t = re.split(r"\s+[|\-–—]\s+", t, maxsplit=1)[0].strip() or t
    for noise in (
        "네이버 지도",
        "네이버 플레이스",
        "카카오맵",
        "KakaoMap",
        "Google Maps",
        "Google 지도",
    ):
        if t == noise:
            return ""
    return t[:120]


def _format_price(raw: Any) -> str:
    if raw is None:
        return ""
    s = str(raw).strip()
    if not s or s.lower() in ("none", "null", "0", "무료"):
        if s == "0" or s == "무료":
            return "무료" if s == "무료" else ""
        return ""
    digits = re.sub(r"[^\d]", "", s)
    if digits.isdigit() and len(digits) >= 3:
        try:
            return f"₩{int(digits):,}"
        except ValueError:
            return s
    return s[:40]


def _abs_url(url: str) -> str:
    u = html_lib.unescape((url or "").strip())
    if not u:
        return ""
    if u.startswith("//"):
        return "https:" + u
    return u


def _place_detail_base(apollo: dict[str, Any], place_id: str) -> dict[str, Any]:
    key = f"PlaceDetailBase:{place_id}"
    node = apollo.get(key)
    if isinstance(node, dict):
        return node
    for k, v in apollo.items():
        if (
            isinstance(v, dict)
            and v.get("__typename") == "PlaceDetailBase"
            and str(v.get("id") or "") == place_id
        ):
            return v
    return {}


def _place_detail_node(apollo: dict[str, Any], place_id: str) -> dict[str, Any]:
    root = apollo.get("ROOT_QUERY")
    if not isinstance(root, dict):
        return {}
    needle = f'"id":"{place_id}"'
    for k, v in root.items():
        if k.startswith("placeDetail") and needle in k.replace(" ", "") and isinstance(v, dict):
            return v
    for k, v in root.items():
        if k.startswith("placeDetail") and place_id in k and isinstance(v, dict):
            return v
    return {}


def _menus_from_apollo(apollo: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[tuple[int, dict[str, Any]]] = []
    for k, v in apollo.items():
        if not (isinstance(v, dict) and v.get("__typename") == "Menu"):
            continue
        name = str(v.get("name") or "").strip()
        if not name:
            continue
        images = v.get("images") or []
        image = ""
        if isinstance(images, list) and images:
            image = _abs_url(str(images[0] or ""))
        idx = v.get("index")
        try:
            order = int(idx) if idx is not None else 9999
        except (TypeError, ValueError):
            order = 9999
        # Prefer recommended items earlier when index ties
        if v.get("recommend"):
            order = min(order, -1)
        item: dict[str, Any] = {
            "name": name[:80],
            "price": _format_price(v.get("price")),
        }
        if image:
            item["image"] = image
        if v.get("recommend"):
            item["recommend"] = True
        items.append((order, item))
    items.sort(key=lambda x: x[0])
    return [it for _, it in items]


def _photos_from_apollo(apollo: dict[str, Any], *, limit: int = 8) -> list[str]:
    photos: list[str] = []
    seen: set[str] = set()

    def add(url: str) -> None:
        u = _abs_url(url)
        if not u or u in seen:
            return
        seen.add(u)
        photos.append(u)

    # Prefer business photos first
    business: list[str] = []
    others: list[str] = []
    for k, v in apollo.items():
        if not (isinstance(v, dict) and str(k).startswith("PlaceDetailTopPhotoItem:")):
            continue
        if v.get("video"):
            continue
        url = str(v.get("originalUrl") or v.get("thumbnailUrl") or "").strip()
        if not url:
            continue
        if "business" in str(k):
            business.append(url)
        else:
            others.append(url)
    for url in business + others:
        add(url)
        if len(photos) >= limit:
            break
    return photos


def _menu_board_images(detail: dict[str, Any], *, limit: int = 6) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for item in detail.get("menuImages") or []:
        if not isinstance(item, dict):
            continue
        url = _abs_url(str(item.get("imageUrl") or ""))
        if not url or url in seen:
            continue
        seen.add(url)
        out.append(url)
        if len(out) >= limit:
            break
    return out


def _hours_from_list_item(item: dict[str, Any]) -> str:
    nbh = item.get("newBusinessHours")
    if isinstance(nbh, dict):
        parts = [
            str(nbh.get("status") or "").strip(),
            str(nbh.get("description") or "").strip(),
        ]
        text = " · ".join(p for p in parts if p)
        if text:
            return text[:160]
        day_off = str(nbh.get("dayOffDescription") or nbh.get("dayOff") or "").strip()
        if day_off:
            return day_off[:160]
    bh = item.get("businessHours")
    if isinstance(bh, str) and bh.strip():
        return bh.strip()[:160]
    if isinstance(bh, dict):
        desc = str(bh.get("description") or bh.get("status") or "").strip()
        if desc:
            return desc[:160]
    return ""


def _about_from_base(base: dict[str, Any]) -> str:
    parts: list[str] = []
    road = str(base.get("road") or "").strip()
    if road:
        parts.append(road)
    score = base.get("visitorReviewsScore")
    total = base.get("visitorReviewsTotal")
    if score is not None:
        try:
            score_s = f"{float(score):.2g}"
        except (TypeError, ValueError):
            score_s = str(score)
        review_bit = f"방문자 평점 {score_s}"
        if total:
            review_bit += f" ({total}명)"
        parts.append(review_bit)
    conv = base.get("conveniences")
    if isinstance(conv, list) and conv:
        labels = [str(x).strip() for x in conv if str(x).strip()]
        if labels:
            parts.append("편의: " + ", ".join(labels[:8]))
    return " ".join(parts)[:400]


def scrape_naver_place(
    place_id: str,
    *,
    force: bool = False,
) -> dict[str, Any]:
    """
    Scrape a Naver place by numeric id.

    Returns dict with keys:
      ok, placeId, placeUrl, name, address, phone, hours, about, category,
      score, menus[{name,price,image}], photos[], menuBoardImages[],
      imageUrl, lat, lng, warnings[], notes[]
    """
    result: dict[str, Any] = {
        "ok": False,
        "sourceType": "naver",
        "placeId": "",
        "placeUrl": "",
        "name": "",
        "address": "",
        "phone": "",
        "hours": "",
        "about": "",
        "category": "",
        "score": "",
        "menus": [],
        "photos": [],
        "menuBoardImages": [],
        "imageUrl": "",
        "lat": "",
        "lng": "",
        "warnings": [],
        "notes": [],
    }
    pid = str(place_id or "").strip()
    if not pid.isdigit():
        result["warnings"].append("유효한 네이버 place id가 아닙니다.")
        return result

    result["placeId"] = pid
    result["placeUrl"] = naver_canonical_place_url(pid)
    home_url = f"https://m.place.naver.com/restaurant/{pid}/home"
    html = fetch_text(home_url, force=force)
    if not html:
        # Some places are cafes / shops — try generic place path
        html = fetch_text(f"https://m.place.naver.com/place/{pid}", force=force)
    if not html:
        result["warnings"].append("네이버 플레이스 페이지를 가져오지 못했습니다.")
        return result

    apollo = extract_apollo_state(html)
    if not apollo:
        # Fallback to OG only
        title = _clean_title(_meta_content(html, prop="og:title"))
        image = _abs_url(_meta_content(html, prop="og:image"))
        desc = _meta_content(html, prop="og:description")
        result["name"] = title
        result["imageUrl"] = image
        result["about"] = desc[:400] if desc else ""
        result["ok"] = bool(title or image)
        result["warnings"].append(
            "Apollo 상태가 없어 OG 메타만 사용했습니다."
        )
        return result

    base = _place_detail_base(apollo, pid)
    detail = _place_detail_node(apollo, pid)

    result["name"] = str(base.get("name") or "").strip()
    result["address"] = (
        str(base.get("roadAddress") or "").strip()
        or str(base.get("address") or "").strip()
    )
    result["phone"] = (
        str(base.get("phone") or "").strip()
        or str(base.get("virtualPhone") or "").strip()
    )
    result["category"] = str(base.get("category") or "").strip()
    score = base.get("visitorReviewsScore")
    if score is not None and score != "":
        result["score"] = str(score)
    result["about"] = _about_from_base(base)

    coord = base.get("coordinate") if isinstance(base.get("coordinate"), dict) else {}
    # Naver sometimes uses x=lng y=lat
    result["lng"] = str(coord.get("x") or coord.get("longitude") or "").strip()
    result["lat"] = str(coord.get("y") or coord.get("latitude") or "").strip()

    result["menus"] = _menus_from_apollo(apollo)
    result["photos"] = _photos_from_apollo(apollo)
    result["menuBoardImages"] = _menu_board_images(detail)
    if result["photos"]:
        result["imageUrl"] = result["photos"][0]
    else:
        og = _abs_url(_meta_content(html, prop="og:image"))
        if og:
            result["imageUrl"] = og

    # Hours often live on search list items — fetch lightly if missing
    if not result["hours"]:
        queries = []
        if result["name"]:
            queries.append(result["name"])
        combo = " ".join(
            x for x in (result["name"], result["address"]) if x
        ).strip()
        if combo and combo not in queries:
            queries.append(combo)
        for q in queries:
            hit = resolve_naver_search(q, prefer_id=pid, force=force)
            if hit.get("hours"):
                result["hours"] = hit["hours"]
                break
            if not result["lat"] and hit.get("lat"):
                result["lat"] = hit["lat"]
                result["lng"] = hit.get("lng") or ""

    notes = result["notes"]
    notes.append(f"네이버 플레이스 {pid} 스크래핑 완료")
    if result["menus"]:
        notes.append(f"메뉴 {len(result['menus'])}개")
    if result["menuBoardImages"]:
        notes.append(f"메뉴판 사진 {len(result['menuBoardImages'])}장")
    if result["photos"]:
        notes.append(f"매장 사진 {len(result['photos'])}장")
    if not result["hours"]:
        result["warnings"].append("영업시간 정보를 찾지 못했습니다.")
    if not result["menus"]:
        result["warnings"].append("등록된 메뉴 목록이 없거나 비공개입니다.")

    result["ok"] = bool(result["name"] or result["address"] or result["menus"])
    return result


def resolve_naver_search(
    query: str,
    *,
    prefer_id: str = "",
    force: bool = False,
) -> dict[str, Any]:
    """
    Resolve a free-text query to the best Naver place list hit.
    Returns placeId, name, address, phone, hours, imageUrl, lat, lng, …
    """
    out: dict[str, Any] = {
        "ok": False,
        "placeId": "",
        "name": "",
        "address": "",
        "phone": "",
        "hours": "",
        "imageUrl": "",
        "lat": "",
        "lng": "",
        "category": "",
        "score": "",
        "warnings": [],
        "notes": [],
    }
    q = (query or "").strip()
    if not q:
        out["warnings"].append("검색어가 비어 있습니다.")
        return out
    url = f"https://pcmap.place.naver.com/place/list?query={quote(q)}"
    html = fetch_text(url, force=force)
    if not html:
        out["warnings"].append("네이버 장소 검색 페이지를 가져오지 못했습니다.")
        return out
    apollo = extract_apollo_state(html)
    if not apollo:
        out["warnings"].append("검색 결과 Apollo 상태가 없습니다.")
        return out

    items: list[dict[str, Any]] = []
    for k, v in apollo.items():
        if isinstance(v, dict) and v.get("__typename") == "PlaceListBusinessesItem":
            items.append(v)
    if not items:
        out["warnings"].append("검색 결과가 없습니다.")
        return out

    chosen: dict[str, Any] | None = None
    if prefer_id:
        for it in items:
            if str(it.get("id") or "") == prefer_id:
                chosen = it
                break
    if chosen is None:
        # Prefer name containment
        q_compact = re.sub(r"\s+", "", q)
        for it in items:
            name = str(it.get("name") or "")
            if name and name.replace(" ", "") in q_compact:
                chosen = it
                break
            if name and name.replace(" ", "") and name.replace(" ", "")[:4] in q_compact:
                chosen = it
                break
    if chosen is None:
        chosen = items[0]

    out["ok"] = True
    out["placeId"] = str(chosen.get("id") or "")
    out["name"] = str(chosen.get("name") or "").strip()
    out["address"] = (
        str(chosen.get("fullAddress") or "").strip()
        or str(chosen.get("roadAddress") or "").strip()
        or str(chosen.get("address") or "").strip()
    )
    out["phone"] = (
        str(chosen.get("phone") or "").strip()
        or str(chosen.get("virtualPhone") or "").strip()
    )
    out["hours"] = _hours_from_list_item(chosen)
    out["imageUrl"] = _abs_url(str(chosen.get("imageUrl") or ""))
    out["lat"] = str(chosen.get("y") or "").strip()
    out["lng"] = str(chosen.get("x") or "").strip()
    out["category"] = str(chosen.get("category") or "").strip()
    score = chosen.get("visitorReviewScore")
    if score is not None and str(score).strip():
        out["score"] = str(score)
    out["notes"].append(f"검색 '{q[:40]}' → place {out['placeId']}")
    return out


def scrape_kakao_place(url: str, *, force: bool = False) -> dict[str, Any]:
    """Best-effort Kakao OG scrape (detail JSON often blocked)."""
    result: dict[str, Any] = {
        "ok": False,
        "sourceType": "kakao",
        "placeUrl": url,
        "name": "",
        "address": "",
        "phone": "",
        "hours": "",
        "about": "",
        "menus": [],
        "photos": [],
        "menuBoardImages": [],
        "imageUrl": "",
        "warnings": [],
        "notes": [],
    }
    html = fetch_text(url, force=force)
    if not html:
        result["warnings"].append("카카오맵 페이지를 가져오지 못했습니다.")
        return result
    title = _clean_title(_meta_content(html, prop="og:title"))
    image = _abs_url(_meta_content(html, prop="og:image"))
    desc = _meta_content(html, prop="og:description")
    result["name"] = title
    result["imageUrl"] = image
    if image:
        result["photos"] = [image]
    result["about"] = desc[:400] if desc else ""
    # Address sometimes in description "주소: …"
    m = re.search(r"(?:주소|道路名?|Address)\s*[:：]?\s*([^\n<]+)", desc or html)
    if m:
        result["address"] = html_lib.unescape(m.group(1)).strip()[:160]
    result["ok"] = bool(title or image)
    result["notes"].append("카카오 OG 메타 스크래핑")
    if not result["menus"]:
        result["warnings"].append("카카오는 메뉴 자동 수집이 제한됩니다.")
    return result


def scrape_google_place(url: str, *, force: bool = False) -> dict[str, Any]:
    """Best-effort Google Maps OG scrape (often blocked / thin)."""
    result: dict[str, Any] = {
        "ok": False,
        "sourceType": "google",
        "placeUrl": url,
        "name": "",
        "address": "",
        "phone": "",
        "hours": "",
        "about": "",
        "menus": [],
        "photos": [],
        "menuBoardImages": [],
        "imageUrl": "",
        "warnings": [],
        "notes": [],
    }
    html = fetch_text(url, force=force)
    if not html:
        result["warnings"].append("구글 지도 페이지를 가져오지 못했습니다.")
        # Still try name from URL path
        m = re.search(r"/place/([^/@]+)", url)
        if m:
            result["name"] = unquote(m.group(1).replace("+", " "))[:120]
            result["ok"] = True
        return result
    title = _clean_title(_meta_content(html, prop="og:title"))
    image = _abs_url(_meta_content(html, prop="og:image"))
    desc = _meta_content(html, prop="og:description")
    result["name"] = title
    result["imageUrl"] = image
    if image:
        result["photos"] = [image]
    result["about"] = desc[:400] if desc else ""
    result["ok"] = bool(title or image)
    result["notes"].append("구글 OG 메타 스크래핑")
    result["warnings"].append("구글은 API 없이 메뉴·전화 수집이 거의 불가합니다.")
    return result


def _normalize_url(raw: str) -> str:
    url = (raw or "").strip()
    if not url:
        return ""
    if url.startswith("//"):
        url = "https:" + url
    if "://" not in url:
        url = "https://" + url
    return url


def _detect_provider(url: str) -> str:
    try:
        host = (urlparse(url).hostname or "").lower()
    except Exception:
        host = ""
    if "naver" in host or host.endswith("naver.me"):
        return "naver"
    if "kakao" in host or host.endswith("kko.to"):
        return "kakao"
    if "google" in host or host.endswith("goo.gl"):
        return "google"
    return "other"


def _search_name_hint(name: str) -> str:
    """Strip Latin parentheticals for better Naver search (브랜드 (Brand) → 브랜드)."""
    n = (name or "").strip()
    n = re.sub(r"\s*\([^)]*\)\s*", " ", n)
    return re.sub(r"\s+", " ", n).strip()


def enrich_from_place_url(
    url: str,
    *,
    source_type: str = "",
    name_hint: str = "",
    address_hint: str = "",
    force: bool = False,
) -> dict[str, Any]:
    """
    High-level enricher used by resolve + batch migrate.
    Upgrades Naver search URLs to real place IDs when possible.
    """
    place = _normalize_url(url)
    detected = _detect_provider(place)
    st = (source_type or "").strip().lower() or detected
    empty: dict[str, Any] = {
        "ok": False,
        "sourceType": st if st in ("naver", "kakao", "google") else (detected or "custom"),
        "placeId": "",
        "placeUrl": place,
        "name": "",
        "address": "",
        "phone": "",
        "hours": "",
        "about": "",
        "category": "",
        "score": "",
        "menus": [],
        "photos": [],
        "menuBoardImages": [],
        "imageUrl": "",
        "lat": "",
        "lng": "",
        "warnings": [],
        "notes": [],
    }
    if not place:
        empty["warnings"].append("place URL이 없습니다.")
        return empty

    if st == "naver" or detected == "naver":
        pid = naver_place_id_from_url(place)
        list_hours = ""
        if not pid:
            name_q = _search_name_hint(name_hint) or (name_hint or "").strip()
            queries: list[str] = []
            for q in (
                name_q,
                " ".join(x for x in (name_q, address_hint) if x).strip(),
            ):
                if q and q not in queries:
                    queries.append(q)
            if not queries:
                m = re.search(r"/p/search/([^/?#]+)", place)
                if m:
                    queries.append(unquote(m.group(1)).replace("+", " "))
            hit: dict[str, Any] = {}
            for q in queries:
                hit = resolve_naver_search(q, force=force)
                empty["notes"].extend(hit.get("notes") or [])
                if hit.get("placeId"):
                    break
                # brief pause + retry once without cache when empty
                if hit.get("warnings") and not force:
                    hit = resolve_naver_search(q, force=True)
                    empty["notes"].extend(hit.get("notes") or [])
                    if hit.get("placeId"):
                        break
            empty["warnings"].extend(hit.get("warnings") or [])
            pid = hit.get("placeId") or ""
            list_hours = hit.get("hours") or ""
            if hit.get("name"):
                empty["name"] = hit["name"]
            if hit.get("address"):
                empty["address"] = hit["address"]
            if hit.get("phone"):
                empty["phone"] = hit["phone"]
            if hit.get("imageUrl"):
                empty["imageUrl"] = hit["imageUrl"]
            if hit.get("lat"):
                empty["lat"] = hit["lat"]
                empty["lng"] = hit.get("lng") or ""
            if not pid:
                empty["hours"] = list_hours
                empty["warnings"].append(
                    "네이버 검색 URL에서 place id를 찾지 못했습니다."
                )
                empty["ok"] = bool(empty.get("name") or empty.get("address"))
                return empty
        scraped = scrape_naver_place(pid, force=force)
        if not scraped.get("hours") and list_hours:
            scraped["hours"] = list_hours
        return scraped

    if st == "kakao" or detected == "kakao":
        return scrape_kakao_place(place, force=force)
    if st == "google" or detected == "google":
        return scrape_google_place(place, force=force)

    empty["warnings"].append("지원하지 않는 지도 출처입니다.")
    return empty


def download_image_to(dest: Path, url: str) -> bool:
    """Download remote image bytes to dest. Returns True on success."""
    data = fetch_bytes(url)
    if not data or len(data) < 64:
        return False
    # crude magic check
    head = data[:16]
    if not (
        head.startswith(b"\xff\xd8")
        or head.startswith(b"\x89PNG")
        or head.startswith(b"RIFF")
        or head.startswith(b"GIF")
        or b"ftyp" in head
    ):
        # allow anyway if large enough — some CDN wrap
        if len(data) < 1000:
            return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return True
