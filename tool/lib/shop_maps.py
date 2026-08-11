# -*- coding: utf-8 -*-
"""Derive Google/Naver map open + embed URLs from a shop place link; optional OG preview."""
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


def derive_shop_maps(
    place_url: str,
    *,
    location: str = "",
    name: str = "",
) -> dict[str, str]:
    """
    From a Google Maps / Naver Place URL (or blank), return:
      placeUrl, mapsUrl, mapsEmbedUrl, mapsProvider (google|naver|location|none)
    """
    place = normalize_place_url(place_url)
    loc = (location or "").strip()
    nm = (name or "").strip()
    fallback_q = loc or nm

    if not place:
        if not fallback_q:
            return {
                "placeUrl": "",
                "mapsUrl": "",
                "mapsEmbedUrl": "",
                "mapsProvider": "none",
            }
        return {
            "placeUrl": "",
            "mapsUrl": maps_url_from_location(fallback_q),
            "mapsEmbedUrl": maps_embed_url_from_location(fallback_q),
            "mapsProvider": "location",
        }

    if _is_google(place):
        maps_url = place
        coords = _google_coords(place)
        if "output=embed" in place or "/maps/embed" in place:
            embed = place
        elif coords:
            lat, lng = coords
            embed = (
                f"https://maps.google.com/maps?q={lat},{lng}&hl=ko&z=16&output=embed"
            )
        elif fallback_q:
            embed = google_embed_from_query(fallback_q)
        else:
            embed = google_embed_from_query(place)
        return {
            "placeUrl": place,
            "mapsUrl": maps_url,
            "mapsEmbedUrl": embed,
            "mapsProvider": "google",
        }

    if _is_naver(place):
        maps_url = place
        pid = _naver_place_id(place)
        if pid:
            embed = f"https://map.naver.com/p/entry/place/{pid}"
        elif fallback_q:
            # Keep Naver as outbound link; use Google query embed for the panel.
            embed = google_embed_from_query(fallback_q)
        else:
            embed = google_embed_from_query(place)
        return {
            "placeUrl": place,
            "mapsUrl": maps_url,
            "mapsEmbedUrl": embed,
            "mapsProvider": "naver",
        }

    embed = (
        maps_embed_url_from_location(fallback_q)
        if fallback_q
        else google_embed_from_query(place)
    )
    maps_url = place if place else (
        maps_url_from_location(fallback_q) if fallback_q else ""
    )
    return {
        "placeUrl": place,
        "mapsUrl": maps_url,
        "mapsEmbedUrl": embed,
        "mapsProvider": "other",
    }


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
    fetch_preview: bool = True,
    regenerate: bool = True,
) -> dict[str, Any]:
    """Mutate restaurant entry with place/maps/embed (+ optional OG preview)."""
    out = dict(entry)
    place = normalize_place_url(place_url)
    old_place = str(out.get("placeUrl") or "").strip()

    if regenerate or place != old_place or not out.get("mapsEmbedUrl"):
        derived = derive_shop_maps(place, location=location, name=name)
        out["placeUrl"] = derived["placeUrl"]
        out["mapsUrl"] = derived["mapsUrl"]
        out["mapsEmbedUrl"] = derived["mapsEmbedUrl"]
        out["mapsProvider"] = derived["mapsProvider"]
    elif place:
        out["placeUrl"] = place
        if not out.get("mapsUrl"):
            out["mapsUrl"] = place

    if fetch_preview and out.get("placeUrl"):
        prev = fetch_og_preview(str(out["placeUrl"]))
        if prev.get("previewTitle"):
            out["previewTitle"] = prev["previewTitle"]
        if prev.get("previewImage"):
            out["previewImage"] = prev["previewImage"]
    return out
