# -*- coding: utf-8 -*-
"""Retry Gyeonggi course photos with known Commons titles."""
from __future__ import annotations

import ssl
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IMG = ROOT / "Images" / "places" / "_courses"
UA = "KoreaTravelGuidebook/1.0 (gyeonggi course covers; educational; rate-limited)"

FILES = {
    "suwon-hwaseong": [
        "Hwaseong.Fortress-Janganmun.01.jpg",
        "Hwaseong Fortress 01.jpg",
        "Hwaseong Fortress, Suwon, Gyeonggi-do, Republic of Korea.jpg",
        "Hwaseong Fortress 03.jpg",
    ],
    "suwon-hwaseong-night": [
        "Hwaseong Fortress at night, Suwon.jpg",
        "Hwaseong Fortress at night, Suwon.2.jpg",
        "Hwaseong North Gate at night, Suwon.jpg",
        "Hwaseong Fortress Pavilion at night, Suwon.3.jpg",
    ],
    "hwaseong-haenggung-plaza": [
        "Hwaseong Haenggung Palace.jpg",
        "Hwaseong Haenggung Palace panorama.jpg",
    ],
    "heyri": [
        "Gongganpurple, Heyri, Paju (공간퍼플, 헤이리) - panoramio.jpg",
        "Gallery MOA, Heyri, Paju (갤러리 모아, 헤이리) - panoramio.jpg",
        "Keumsan Gallery, Heyri, Paju (금산 갤러리, 헤이리) - panoramio.jpg",
        "Gallery SoSo, Heyri, Paju (갤러리 소소, 헤이리) - panoramio.jpg",
        "Birth, Heyri, Paju (탄생, 헤이리) - panoramio.jpg",
    ],
    "pocheon-art-valley": [
        "ArtValleyInKorea 1.jpg",
        "Art Valley In Korea (65750913).jpeg",
        "Geology of South Korea - Cheonjuho(천주호) (21101174435).jpg",
    ],
    "dmz-dora": [
        "Civil Dora Observatory.jpg",
        "Dora Observatory 01.JPG",
        "Dora Observatory, Demilitarized Zone (DMZ), South Korea.jpg",
        "Dora Observatory 02.JPG",
    ],
    "imjingak-peace": [
        "Freedom Bridge at Imjingak, Demilitarized Zone (DMZ), South Korea.jpg",
        "Imjingak Park & the Freedom Bridge.jpg",
        "Imjingak Bridge, Demilitarized Zone (DMZ), South Korea.jpg",
    ],
    "semiwon": [
        "Semiwon (161373213).jpeg",
        "양평-세미원.JPG",
        "세미원 (41).JPG",
        "세미원 (38).JPG",
    ],
    "gwangmyeong-cave": [
        "Gwangmyeong Cave interior.jpg",
        "Inside Gwangmyeong Cave.jpg",
        "광명동굴 내부.jpg",
        "Gwangmyeong Cave wine cave.jpg",
    ],
    "garden-of-morning-calm": [
        "아침고요수목원.jpg",
        "Garden of Morning Calm autumn.jpg",
        "The Garden of Morning Calm Gapyeong.jpg",
        "Morning Calm Garden.jpg",
    ],
    "everland-rides": [
        "T Express 1.jpg",
        "T Express 2.jpg",
        "T Express station at Everland.jpg",
    ],
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


def http_get(url: str, timeout: int = 90) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout, context=ssl_ctx()) as r:
        return r.read()


def special_filepath(title: str, width: int = 1280) -> str:
    enc = urllib.parse.quote(title.replace(" ", "_"))
    return f"https://commons.wikimedia.org/wiki/Special:FilePath/{enc}?width={width}"


def save_image(url: str, dest: Path) -> bool:
    try:
        data = http_get(url)
    except Exception as exc:
        print(f"  dl err: {exc}", flush=True)
        return False
    if len(data) < 12000:
        print(f"  too small ({len(data)})", flush=True)
        return False
    head = data[:32].lstrip()
    if head.startswith(b"<") or head.startswith(b"<!DO"):
        print("  rejected html", flush=True)
        return False
    if not (
        data[:3] == b"\xff\xd8\xff"
        or data[:8] == b"\x89PNG\r\n\x1a\n"
        or data[:4] == b"RIFF"
    ):
        print("  bad magic", flush=True)
        return False
    dest.write_bytes(data)
    return True


def fetch_one(slug: str, titles: list[str]) -> bool:
    dest = IMG / f"{slug}.jpg"
    for title in titles:
        url = special_filepath(title)
        print(f"  try {title}", flush=True)
        if save_image(url, dest):
            print(f"+ {slug} <- {title} ({dest.stat().st_size})", flush=True)
            return True
        time.sleep(2.0)
    print(f"! FAIL {slug}", flush=True)
    return False


def main() -> int:
    IMG.mkdir(parents=True, exist_ok=True)
    ok = fail = 0
    for slug, titles in FILES.items():
        print(f"\n## {slug}", flush=True)
        if fetch_one(slug, titles):
            ok += 1
        else:
            fail += 1
        time.sleep(3.0)
    print(f"\ndone ok={ok} fail={fail}", flush=True)
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
