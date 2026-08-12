# -*- coding: utf-8 -*-
"""Derive map open + embed URLs from a shop place link; optional OG preview.

Supports explicit registration sourceType: naver | kakao | google | custom.
"""
from __future__ import annotations

import html as html_lib
import re
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen

from .scaffold import maps_embed_url_from_location, maps_url_from_location

_UA = (
    "Mozilla/5.0 (compatible; KoreaTravelGuidebook/1.0; +https://github.com/) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

SOURCE_TYPES = ("naver", "kakao", "google", "custom")

_GOOGLE_HOSTS = {
    "google.com",
    "www.google.com",
    "maps.google.com",
    "www.maps.google.com",
    "maps.app.goo.gl",
    "goo.gl",
}

_NAVER_HOSTS = {
    "map.naver.com",
    "m.map.naver.com",
    "naver.me",
    "pcmap.place.naver.com",
    "place.map.naver.com",
    "map.naver.me",
}

_KAKAO_HOSTS = {
    "map.kakao.com",
    "m.map.kakao.com",
    "place.map.kakao.com",
    "kko.to",
    "kko.kakao.com",
}


def _host(url: str) -> str:
    try:
        return (urlparse(url).hostname or "").lower()
    except Exception:
        return ""


def _is_google(url: str) -> bool:
    h = _host(url)
    if h in _GOOGLE_HOSTS:
        return True
    return h.endswith(".google.com") or h.endswith(".goo.gl")


def _is_naver(url: str) -> bool:
    h = _host(url)
    if h in _NAVER_HOSTS:
        return True
    return "naver.com" in h or h.endswith("naver.me")


def _is_kakao(url: str) -> bool:
    h = _host(url)
    if h in _KAKAO_HOSTS:
        return True
    return "kakao.com" in h or h.endswith("kko.to")


def detect_provider(url: str) -> str:
    """Return google|naver|kakao|other|none for a place URL."""
    place = normalize_place_url(url)
    if not place:
        return "none"
    if _is_google(place):
        return "google"
    if _is_naver(place):
        return "naver"
    if _is_kakao(place):
        return "kakao"
    return "other"


def normalize_source_type(raw: str | None) -> str:
    v = (raw or "").strip().lower()
    if v in SOURCE_TYPES:
        return v
    return ""


def infer_source_type(
    *,
    source_type: str = "",
    place_url: str = "",
    maps_provider: str = "",
) -> str:
    """
    Resolve registration mode for a shop entry.
    Prefer explicit sourceType; else derive from place URL / mapsProvider;
    default custom when no place link, else google for unknown map links.
    """
    explicit = normalize_source_type(source_type)
    if explicit:
        return explicit
    provider = (maps_provider or "").strip().lower()
    place = normalize_place_url(place_url)
    detected = detect_provider(place) if place else "none"
    if detected in ("naver", "kakao", "google"):
        return detected
    if provider in ("naver", "kakao", "google"):
        return provider
    if place:
        return "google"
    return "custom"


def _google_coords(url: str) -> tuple[str, str] | None:
    m = re.search(r"@(-?\d+\.\d+),(-?\d+\.\d+)", url)
    if m:
        return m.group(1), m.group(2)
    m = re.search(r"[?&]q=(-?\d+\.\d+),(-?\d+\.\d+)", url)
    if m:
        return m.group(1), m.group(2)
    m = re.search(r"!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)", url)
    if m:
        return m.group(1), m.group(2)
    return None


def _naver_place_id(url: str) -> str:
    patterns = (
        r"/place/(\d+)",
        r"/entry/place/(\d+)",
        r"/restaurant/(\d+)",
        r"/cafe/(\d+)",
        r"[?&]id=(\d+)",
        r"/(\d{6,})(?:/|$|\?)",
    )
    for pat in patterns:
        m = re.search(pat, url)
        if m:
            return m.group(1)
    return ""


def _kakao_coords(url: str) -> tuple[str, str] | None:
    m = re.search(r"[?&](?:q|x)=(-?\d+\.\d+).*?[?&](?:y)=(-?\d+\.\d+)", url)
    if m:
        # x=lng y=lat on some Kakao URLs
        return m.group(2), m.group(1)
    m = re.search(r"/link/map/[^,]+,(-?\d+\.\d+),(-?\d+\.\d+)", url)
    if m:
        return m.group(1), m.group(2)
    m = re.search(r"[?&]lat=(-?\d+\.\d+).*?[?&]lng=(-?\d+\.\d+)", url)
    if m:
        return m.group(1), m.group(2)
    return None


def normalize_place_url(raw: str) -> str:
    url = (raw or "").strip()
    if not url:
        return ""
    if url.startswith("//"):
        url = "https:" + url
    if "://" not in url:
        url = "https://" + url
    return url


def google_embed_from_query(query: str) -> str:
    q = quote((query or "").strip(), safe="")
    return f"https://maps.google.com/maps?q={q}&hl=ko&z=16&output=embed"


def google_embed_from_coords(lat: str, lng: str) -> str:
    return f"https://maps.google.com/maps?q={lat},{lng}&hl=ko&z=16&output=embed"


def is_google_maps_embed(url: str) -> bool:
    """True when URL is a framable Google Maps location embed."""
    u = (url or "").strip().lower()
    if not u:
        return False
    if "output=embed" in u or "/maps/embed" in u:
        return True
    return False


def is_blocked_place_page_embed(url: str) -> bool:
    """
    Naver Place / Kakao place pages set X-Frame-Options and cannot be iframed.
    Treat those (and any non-Google embed) as unsuitable for the map panel.
    """
    u = (url or "").strip().lower()
    if not u:
        return True
    if is_google_maps_embed(u):
        return False
    if "naver.com" in u or "naver.me" in u:
        return True
    if "kakao.com" in u or "kko.to" in u:
        return True
    # Non-embed Google place/search links also fail as map iframes
    if "google.com" in u or "goo.gl" in u:
        return True
    return True


def _location_map_embed(
    *,
    fallback_q: str = "",
    place: str = "",
    coords: tuple[str, str] | None = None,
) -> str:
    """Always return a Google Maps embed suitable for the bottom map panel."""
    if coords:
        return google_embed_from_coords(coords[0], coords[1])
    if fallback_q:
        return google_embed_from_query(fallback_q)
    if place and is_google_maps_embed(place):
        return place
    if place:
        # Last resort: query the place URL string (rarely ideal, but better than blank)
        return google_embed_from_query(place)
    return ""


def derive_shop_maps(
    place_url: str,
    *,
    location: str = "",
    name: str = "",
    source_type: str = "",
) -> dict[str, str]:
    """
    From a place URL (or blank), return:
      placeUrl, mapsUrl, mapsEmbedUrl, mapsProvider, sourceType

    Layout contract (public shop page):
      - placeUrl / mapsUrl → deep link for the top "shop info" place card
      - mapsEmbedUrl → Google Maps location iframe for the bottom map panel
        (never a Naver/Kakao place page — those block iframe embedding)

    mapsProvider: google|naver|kakao|location|other|none
    sourceType: naver|kakao|google|custom
    """
    place = normalize_place_url(place_url)
    loc = (location or "").strip()
    nm = (name or "").strip()
    fallback_q = loc or nm
    st = infer_source_type(
        source_type=source_type, place_url=place, maps_provider=""
    )

    if st == "custom" or (not place and st == "custom"):
        if fallback_q:
            return {
                "placeUrl": "",
                "mapsUrl": maps_url_from_location(fallback_q),
                "mapsEmbedUrl": maps_embed_url_from_location(fallback_q),
                "mapsProvider": "location",
                "sourceType": "custom",
            }
        return {
            "placeUrl": "",
            "mapsUrl": "",
            "mapsEmbedUrl": "",
            "mapsProvider": "none",
            "sourceType": "custom",
        }

    if not place:
        if not fallback_q:
            return {
                "placeUrl": "",
                "mapsUrl": "",
                "mapsEmbedUrl": "",
                "mapsProvider": "none",
                "sourceType": st or "custom",
            }
        # Map-based type without URL: location fallback embed (google panel)
        return {
            "placeUrl": "",
            "mapsUrl": maps_url_from_location(fallback_q),
            "mapsEmbedUrl": maps_embed_url_from_location(fallback_q),
            "mapsProvider": "location",
            "sourceType": st or "google",
        }

    # Resolve provider from explicit sourceType, else URL host
    provider = st if st in ("naver", "kakao", "google") else detect_provider(place)
    if provider == "other":
        provider = "google"

    if provider == "google":
        coords = _google_coords(place)
        embed = _location_map_embed(
            fallback_q=fallback_q, place=place, coords=coords
        )
        return {
            "placeUrl": place,
            "mapsUrl": place,
            "mapsEmbedUrl": embed,
            "mapsProvider": "google",
            "sourceType": "google",
        }

    if provider == "naver":
        # Place page cannot iframe; deep-link card + Google location map below
        embed = _location_map_embed(fallback_q=fallback_q, place="")
        if not embed:
            # No address: fall back to place name search on Google Maps embed
            embed = google_embed_from_query(nm or place)
        return {
            "placeUrl": place,
            "mapsUrl": place,
            "mapsEmbedUrl": embed,
            "mapsProvider": "naver",
            "sourceType": "naver",
        }

    if provider == "kakao":
        coords = _kakao_coords(place)
        embed = _location_map_embed(
            fallback_q=fallback_q, place="", coords=coords
        )
        if not embed:
            embed = google_embed_from_query(nm or place)
        return {
            "placeUrl": place,
            "mapsUrl": place,
            "mapsEmbedUrl": embed,
            "mapsProvider": "kakao",
            "sourceType": "kakao",
        }

    embed = _location_map_embed(fallback_q=fallback_q, place=place)
    return {
        "placeUrl": place,
        "mapsUrl": place,
        "mapsEmbedUrl": embed,
        "mapsProvider": "other",
        "sourceType": st if st in SOURCE_TYPES else "google",
    }


def validate_place_for_source(source_type: str, place_url: str) -> str:
    """Return an error message if invalid, else empty string."""
    st = normalize_source_type(source_type) or infer_source_type(
        source_type=source_type, place_url=place_url
    )
    place = normalize_place_url(place_url)
    if st == "custom":
        return ""
    if not place:
        labels = {
            "naver": "네이버 플레이스",
            "kakao": "카카오맵",
            "google": "구글 비즈니스/지도",
        }
        return f"{labels.get(st, '지도')} 링크를 입력하세요."
    detected = detect_provider(place)
    # Allow short/unknown hosts (other) that may redirect; hard-fail obvious mismatches
    if st == "naver" and detected in ("google", "kakao"):
        return "네이버 플레이스 링크가 아닙니다. 다른 등록 방식을 선택하거나 네이버 URL을 넣으세요."
    if st == "kakao" and detected in ("google", "naver"):
        return "카카오맵 링크가 아닙니다. 다른 등록 방식을 선택하거나 카카오 URL을 넣으세요."
    if st == "google" and detected in ("naver", "kakao"):
        return "구글 지도 링크가 아닙니다. 다른 등록 방식을 선택하거나 구글 URL을 넣으세요."
    return ""


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


def fetch_og_preview(url: str, *, timeout: float = 6.0) -> dict[str, str]:
    """
    Best-effort Open Graph title/image via stdlib urllib.
    Returns {previewTitle, previewImage} (may be empty). Never raises.
    """
    out = {"previewTitle": "", "previewImage": ""}
    target = normalize_place_url(url)
    if not target or not target.startswith("http"):
        return out
    try:
        req = Request(
            target,
            headers={
                "User-Agent": _UA,
                "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "ko,en;q=0.8",
            },
            method="GET",
        )
        with urlopen(req, timeout=timeout) as resp:
            raw = resp.read(250_000)
            ctype = (resp.headers.get("Content-Type") or "").lower()
            final_url = resp.geturl() or target
        if "html" not in ctype and not raw[:200].lstrip().lower().startswith(
            (b"<!doctype", b"<html")
        ):
            return out
        charset = "utf-8"
        m = re.search(r"charset=([\w-]+)", ctype)
        if m:
            charset = m.group(1)
        try:
            text = raw.decode(charset, errors="replace")
        except LookupError:
            text = raw.decode("utf-8", errors="replace")
        title = (
            _meta_content(text, prop="og:title")
            or _meta_content(text, name="title")
            or ""
        )
        if not title:
            tm = re.search(
                r"<title[^>]*>(.*?)</title>", text, re.IGNORECASE | re.DOTALL
            )
            if tm:
                title = html_lib.unescape(re.sub(r"\s+", " ", tm.group(1)).strip())
        image = _meta_content(text, prop="og:image") or _meta_content(
            text, prop="og:image:secure_url"
        )
        if image and image.startswith("//"):
            image = "https:" + image
        elif image and image.startswith("/"):
            parsed = urlparse(final_url)
            image = f"{parsed.scheme}://{parsed.netloc}{image}"
        out["previewTitle"] = title[:200]
        out["previewImage"] = image[:500]
    except (HTTPError, URLError, TimeoutError, ValueError, OSError):
        return out
    except Exception:
        return out
    return out


def apply_maps_and_preview(
    entry: dict[str, Any],
    *,
    place_url: str,
    location: str = "",
    name: str = "",
    source_type: str = "",
    fetch_preview: bool = True,
    regenerate: bool = True,
) -> dict[str, Any]:
    """Mutate restaurant entry with place/maps/embed/sourceType (+ optional OG preview)."""
    out = dict(entry)
    place = normalize_place_url(place_url)
    old_place = str(out.get("placeUrl") or "").strip()
    st = infer_source_type(
        source_type=source_type or str(out.get("sourceType") or ""),
        place_url=place or old_place,
        maps_provider=str(out.get("mapsProvider") or ""),
    )

    if st == "custom":
        out["sourceType"] = "custom"
        out["placeUrl"] = ""
        fallback_q = (location or "").strip() or (name or "").strip()
        if regenerate:
            if fallback_q:
                out["mapsUrl"] = maps_url_from_location(fallback_q)
                out["mapsEmbedUrl"] = maps_embed_url_from_location(fallback_q)
                out["mapsProvider"] = "location"
            else:
                out["mapsUrl"] = ""
                out["mapsEmbedUrl"] = ""
                out["mapsProvider"] = "none"
        if fetch_preview:
            out["previewTitle"] = ""
            out["previewImage"] = ""
        return out

    embed_broken = is_blocked_place_page_embed(str(out.get("mapsEmbedUrl") or ""))
    if (
        regenerate
        or place != old_place
        or not out.get("mapsEmbedUrl")
        or not out.get("sourceType")
        or embed_broken
    ):
        derived = derive_shop_maps(
            place, location=location, name=name, source_type=st
        )
        out["placeUrl"] = derived["placeUrl"]
        out["mapsUrl"] = derived["mapsUrl"]
        out["mapsEmbedUrl"] = derived["mapsEmbedUrl"]
        out["mapsProvider"] = derived["mapsProvider"]
        out["sourceType"] = derived["sourceType"]
    elif place:
        out["placeUrl"] = place
        out["sourceType"] = st
        if not out.get("mapsUrl"):
            out["mapsUrl"] = place

    if fetch_preview and out.get("placeUrl"):
        prev = fetch_og_preview(str(out["placeUrl"]))
        if prev.get("previewTitle"):
            out["previewTitle"] = prev["previewTitle"]
        if prev.get("previewImage"):
            out["previewImage"] = prev["previewImage"]
    return out


def _looks_like_url(raw: str) -> bool:
    s = (raw or "").strip()
    if not s:
        return False
    if "://" in s or s.startswith("//"):
        return True
    low = s.lower()
    if low.startswith(("www.", "map.", "maps.", "naver.me", "kko.to", "goo.gl")):
        return True
    if re.match(r"^[a-z0-9.-]+\.[a-z]{2,}(/|\?|$)", low):
        return True
    return False


def _google_place_name_from_url(url: str) -> str:
    """Best-effort place name from Google Maps path /place/Name/@…"""
    from urllib.parse import unquote

    m = re.search(r"/place/([^/@]+)", url)
    if m:
        name = unquote(m.group(1).replace("+", " ")).strip()
        name = re.sub(r"\s+", " ", name)
        # Drop trailing locality crumbs that are just coords leftovers
        if name and not re.fullmatch(r"-?\d+(\.\d+)?", name):
            return name[:120]
    m = re.search(r"[?&](?:q|query)=([^&]+)", url, re.IGNORECASE)
    if m:
        from urllib.parse import unquote

        q = unquote(m.group(1).replace("+", " ")).strip()
        # Skip pure lat,lng queries
        if q and not re.fullmatch(r"-?\d+\.\d+\s*,\s*-?\d+\.\d+", q):
            return q[:120]
    return ""


def _naver_name_hint_from_url(url: str) -> str:
    from urllib.parse import unquote

    m = re.search(r"/place/[^/]+/?(?:home)?", url)
    # Some share links encode name in path segments
    m = re.search(r"/entry/place/\d+/([^/?#]+)", url)
    if m:
        return unquote(m.group(1).replace("+", " "))[:120]
    m = re.search(r"[?&](?:query|q|search)=([^&]+)", url, re.IGNORECASE)
    if m:
        return unquote(m.group(1).replace("+", " "))[:120]
    return ""


def _kakao_name_hint_from_url(url: str) -> str:
    from urllib.parse import unquote

    m = re.search(r"/link/map/([^,/]+)", url)
    if m:
        return unquote(m.group(1).replace("+", " "))[:120]
    m = re.search(r"[?&](?:q|query)=([^&]+)", url, re.IGNORECASE)
    if m:
        return unquote(m.group(1).replace("+", " "))[:120]
    return ""


def _clean_og_title(title: str) -> str:
    t = (title or "").strip()
    if not t:
        return ""
    # Strip common suffixes: " - 네이버 지도", " | 카카오맵", " - Google Maps"
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


def geocode_nominatim(address: str, *, timeout: float = 8.0) -> dict[str, str]:
    """
    OpenStreetMap Nominatim geocode (no API key).
    Returns {displayName, lat, lng, address} (may be empty). Never raises.
    """
    out = {"displayName": "", "lat": "", "lng": "", "address": ""}
    q = (address or "").strip()
    if not q:
        return out
    try:
        from urllib.parse import urlencode

        qs = urlencode(
            {
                "q": q,
                "format": "json",
                "limit": "1",
                "addressdetails": "0",
            }
        )
        req = Request(
            f"https://nominatim.openstreetmap.org/search?{qs}",
            headers={
                "User-Agent": _UA,
                "Accept": "application/json",
                "Accept-Language": "ko,en;q=0.8",
            },
            method="GET",
        )
        with urlopen(req, timeout=timeout) as resp:
            raw = resp.read(200_000)
        import json as _json

        data = _json.loads(raw.decode("utf-8", errors="replace"))
        if not isinstance(data, list) or not data:
            return out
        hit = data[0] or {}
        out["displayName"] = str(hit.get("display_name") or "")[:240]
        out["lat"] = str(hit.get("lat") or "")
        out["lng"] = str(hit.get("lon") or "")
        out["address"] = out["displayName"]
    except (HTTPError, URLError, TimeoutError, ValueError, OSError):
        return out
    except Exception:
        return out
    return out


def resolve_shop_input(
    raw: str,
    *,
    source_type: str = "",
    fetch_preview: bool = True,
) -> dict[str, Any]:
    """
    Resolve a place URL or free-text address into form-ready shop fields.

    Returns:
      sourceType, name, address, mapsEmbedUrl, placeUrl, mapsUrl,
      phone, hours, about, imageUrl, previewTitle, placeId,
      menus, photos, menuBoardImages, notes, warnings
    Never raises.
    """
    from .place_scrape import enrich_from_place_url

    result: dict[str, Any] = {
        "ok": True,
        "sourceType": "custom",
        "name": "",
        "address": "",
        "mapsEmbedUrl": "",
        "placeUrl": "",
        "mapsUrl": "",
        "mapsProvider": "none",
        "phone": "",
        "hours": "",
        "about": "",
        "placeId": "",
        "imageUrl": "",
        "previewTitle": "",
        "menus": [],
        "photos": [],
        "menuBoardImages": [],
        "lat": "",
        "lng": "",
        "notes": [],
        "warnings": [],
    }
    text = (raw or "").strip()
    if not text:
        result["ok"] = False
        result["warnings"].append("URL 또는 주소를 입력하세요.")
        return result

    explicit = normalize_source_type(source_type)
    notes: list[str] = []
    warnings: list[str] = []

    if _looks_like_url(text):
        place = normalize_place_url(text)
        detected = detect_provider(place)
        st = explicit if explicit in ("naver", "kakao", "google") else (
            detected if detected in ("naver", "kakao", "google") else "google"
        )
        if explicit == "custom":
            st = (
                detected
                if detected in ("naver", "kakao", "google")
                else "google"
            )

        name_hint = ""
        if st == "google" or detected == "google":
            name_hint = _google_place_name_from_url(place)
        elif st == "naver":
            name_hint = _naver_name_hint_from_url(place)
        elif st == "kakao":
            name_hint = _kakao_name_hint_from_url(place)

        enriched: dict[str, Any] = {}
        if fetch_preview:
            enriched = enrich_from_place_url(
                place,
                source_type=st,
                name_hint=name_hint,
                address_hint="",
            )
            notes.extend(enriched.get("notes") or [])
            warnings.extend(enriched.get("warnings") or [])

        resolved_place = (
            str(enriched.get("placeUrl") or "").strip()
            or place
        )
        name = (
            str(enriched.get("name") or "").strip()
            or name_hint
        )
        address = str(enriched.get("address") or "").strip()
        coords = None
        if enriched.get("lat") and enriched.get("lng"):
            coords = (str(enriched["lat"]), str(enriched["lng"]))

        derived = derive_shop_maps(
            resolved_place,
            location=address,
            name=name,
            source_type=st,
        )
        # Prefer coordinate embed when scrape found lat/lng
        if coords and not is_google_maps_embed(derived.get("mapsEmbedUrl") or ""):
            derived["mapsEmbedUrl"] = google_embed_from_coords(coords[0], coords[1])
        elif coords and "q=" in (derived.get("mapsEmbedUrl") or "") and address:
            derived["mapsEmbedUrl"] = google_embed_from_coords(coords[0], coords[1])
        elif coords:
            derived["mapsEmbedUrl"] = google_embed_from_coords(coords[0], coords[1])

        result.update(
            {
                "sourceType": derived["sourceType"],
                "placeUrl": derived["placeUrl"],
                "mapsUrl": derived["mapsUrl"],
                "mapsEmbedUrl": derived["mapsEmbedUrl"],
                "mapsProvider": derived["mapsProvider"],
                "name": name,
                "address": address,
                "phone": str(enriched.get("phone") or "").strip(),
                "hours": str(enriched.get("hours") or "").strip(),
                "about": str(enriched.get("about") or "").strip(),
                "placeId": str(enriched.get("placeId") or "").strip(),
                "menus": list(enriched.get("menus") or []),
                "photos": list(enriched.get("photos") or []),
                "menuBoardImages": list(enriched.get("menuBoardImages") or []),
                "lat": str(enriched.get("lat") or ""),
                "lng": str(enriched.get("lng") or ""),
            }
        )
        notes.append(f"{st} 링크로 지도·원본 URL을 채웠습니다.")

        image = str(enriched.get("imageUrl") or "").strip()
        if image:
            result["imageUrl"] = image
            result["previewTitle"] = name or result["previewTitle"]
            notes.append("플레이스 이미지를 가져왔습니다.")
        elif fetch_preview:
            prev = fetch_og_preview(resolved_place)
            title = _clean_og_title(prev.get("previewTitle") or "")
            og_image = (prev.get("previewImage") or "").strip()
            if title:
                result["previewTitle"] = title
                if not result["name"]:
                    result["name"] = title
                notes.append("페이지 제목(OG)을 가져왔습니다.")
            if og_image:
                result["imageUrl"] = og_image
                notes.append("미리보기 이미지를 가져왔습니다.")

        if not result["mapsEmbedUrl"] and result["name"]:
            result["mapsEmbedUrl"] = google_embed_from_query(
                address or result["name"]
            )
            result["mapsUrl"] = result["mapsUrl"] or maps_url_from_location(
                address or result["name"]
            )
            notes.append("가게 이름으로 Google 지도 임베드를 만들었습니다.")

        if st in ("naver", "kakao") and not result["address"] and not result["menus"]:
            warnings.append(
                "주소·메뉴 자동 수집이 불완전할 수 있습니다. 저장 전 확인해 주세요."
            )
    else:
        # Free-text address (or place name)
        st = explicit if explicit == "custom" else (explicit or "custom")
        if st in ("naver", "kakao", "google"):
            # User picked a map type but pasted an address — treat as custom address
            st = "custom"
        result["sourceType"] = "custom"
        result["address"] = text
        result["placeUrl"] = ""

        geo = geocode_nominatim(text)
        if geo.get("lat") and geo.get("lng"):
            result["mapsEmbedUrl"] = google_embed_from_coords(
                geo["lat"], geo["lng"]
            )
            result["mapsUrl"] = maps_url_from_location(
                geo.get("displayName") or text
            )
            result["mapsProvider"] = "location"
            if geo.get("displayName"):
                result["address"] = geo["displayName"]
            notes.append("OpenStreetMap(Nominatim)으로 위치를 찾았습니다.")
        else:
            result["mapsEmbedUrl"] = google_embed_from_query(text)
            result["mapsUrl"] = maps_url_from_location(text)
            result["mapsProvider"] = "location"
            notes.append(
                "지오코딩 결과가 없어 주소 검색용 Google 지도 임베드를 넣었습니다."
            )
            warnings.append(
                "정확한 좌표를 못 찾았습니다. 지도 위치를 저장 전 확인해 주세요."
            )

    result["notes"] = notes
    result["warnings"] = warnings
    return result
