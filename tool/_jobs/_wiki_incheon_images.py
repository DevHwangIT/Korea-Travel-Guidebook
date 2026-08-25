# -*- coding: utf-8 -*-
"""Wikipedia lead images for remaining Incheon stops."""
from __future__ import annotations

import json
import ssl
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IMG = ROOT / "Images" / "places" / "_courses"
UA = "KoreaTravelGuidebook/1.0 (incheon covers)"

PAGES = {
    "wolmido-night": [("ko.wikipedia.org", "월미도"), ("en.wikipedia.org", "Wolmi Island")],
    "tribowl": [("ko.wikipedia.org", "트라이보울"), ("en.wikipedia.org", "Tri-bowl")],
    "songdo-outlet": [("ko.wikipedia.org", "현대 프리미엄 아울렛"), ("ko.wikipedia.org", "송도국제도시")],
    "paradise-city": [("ko.wikipedia.org", "파라다이스시티"), ("en.wikipedia.org", "Paradise City (Incheon)")],
    "masian-beach": [("ko.wikipedia.org", "마시안해변"), ("ko.wikipedia.org", "무의도")],
    "dongmak-beach": [("ko.wikipedia.org", "동막해수욕장"), ("ko.wikipedia.org", "강화도")],
    "ganghwa-peace": [("ko.wikipedia.org", "강화평화전망대"), ("ko.wikipedia.org", "교동도")],
}

CTX = None


def ssl_ctx():
    global CTX
    if CTX is None:
        try:
            import certifi

            CTX = ssl.create_default_context(cafile=certifi.where())
        except Exception:
            CTX = ssl._create_unverified_context()
    return CTX


def http_get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60, context=ssl_ctx()) as r:
        return r.read()


def pageimage(host: str, title: str) -> str | None:
    api = f"https://{host}/w/api.php?" + urllib.parse.urlencode(
        {
            "action": "query",
            "titles": title,
            "prop": "pageimages|images",
            "pithumbsize": "1280",
            "imlimit": "20",
            "format": "json",
        }
    )
    data = json.loads(http_get(api).decode())
    pages = data.get("query", {}).get("pages", {})
    for page in pages.values():
        thumb = (page.get("thumbnail") or {}).get("source")
        if thumb:
            return thumb
    return None


def save_image(url: str, dest: Path) -> bool:
    try:
        data = http_get(url)
    except Exception as exc:
        print(f"  dl err: {exc}", flush=True)
        return False
    if len(data) < 12000:
        print(f"  too small ({len(data)})", flush=True)
        return False
    if data[:32].lstrip()[:1] == b"<":
        print("  html", flush=True)
        return False
    if not (data[:3] == b"\xff\xd8\xff" or data[:8] == b"\x89PNG\r\n\x1a\n" or data[:4] == b"RIFF"):
        print("  magic", data[:8], flush=True)
        return False
    dest.write_bytes(data)
    return True


def list_images(host: str, title: str) -> list[str]:
    api = f"https://{host}/w/api.php?" + urllib.parse.urlencode(
        {
            "action": "query",
            "titles": title,
            "prop": "images",
            "imlimit": "30",
            "format": "json",
        }
    )
    data = json.loads(http_get(api).decode())
    out = []
    for page in data.get("query", {}).get("pages", {}).values():
        for im in page.get("images") or []:
            t = im.get("title", "")
            if t.startswith("파일:") or t.startswith("File:"):
                out.append(t.split(":", 1)[-1])
    return out


def special(title: str) -> str:
    enc = urllib.parse.quote(title.replace(" ", "_"))
    return f"https://commons.wikimedia.org/wiki/Special:FilePath/{enc}?width=1280"


def main() -> int:
    IMG.mkdir(parents=True, exist_ok=True)
    for slug, pages in PAGES.items():
        print(f"\n## {slug}", flush=True)
        dest = IMG / f"{slug}.jpg"
        got = False
        for host, title in pages:
            print(f"  wiki {host} {title}", flush=True)
            try:
                url = pageimage(host, title)
                print(f"  thumb {url}", flush=True)
                if url and save_image(url, dest):
                    print(f"+ {slug} from thumb ({dest.stat().st_size})", flush=True)
                    got = True
                    break
                for fname in list_images(host, title):
                    low = fname.lower()
                    if low.endswith((".svg", ".gif", ".pdf")):
                        continue
                    print(f"  file {fname}", flush=True)
                    if save_image(special(fname), dest):
                        print(f"+ {slug} <- {fname}", flush=True)
                        got = True
                        break
                    time.sleep(1.2)
                if got:
                    break
            except Exception as exc:
                print(f"  err {exc}", flush=True)
            time.sleep(2)
        if not got:
            print(f"! FAIL {slug}", flush=True)
        time.sleep(2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
