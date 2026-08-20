# -*- coding: utf-8 -*-
"""Fill remaining/bad beach images via curated Commons Special:FilePath only (no search API)."""
from __future__ import annotations

import hashlib
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "Images" / "places"
TYPE_FALLBACK = IMG / "_types" / "beach.jpg"
UA = "KoreaTravelGuidebook/1.0 (beach covers; educational; github mirror)"
CTX = None

# Only beaches that still need a real photo (fallback or known-bad).
# Filenames verified via Commons categories / known pages.
TARGETS: dict[str, list[str]] = {
    "ilgwang-beach": [
        "일광해수욕장 오리배.jpg",
        "일광해수욕장 수상레저.jpg",
        "바다미술제 준비 1.jpg",
    ],
    "ulsan-ilsan-beach": [
        "Korea-Ulsan-Ilsan Beach-01.jpg",
        "Ilsan Beach Ulsan.jpg",
        "울산 일산해수욕장.jpg",
        "Daewangam Park.jpg",
        "Korea-Ulsan-Daewangam-01.jpg",
    ],
    "manseongni-black-sand-beach": [
        "Manseongri Beach.jpg",
        "만성리검은모래해변.jpg",
        "Yeosu black sand beach.jpg",
        "Korea-Yeosu-Manseongri-01.jpg",
    ],
    "sipripo-beach": [
        "Sipripo Beach.jpg",
        "십리포해수욕장.jpg",
        "Deokjeokdo Beach.jpg",
        "Korea-Deokjeokdo-01.jpg",
    ],
    "iho-tewoo-beach": [
        "Iho Tewoo Beach.jpg",
        "이호테우해수욕장.jpg",
        "Iho Beach Jeju.jpg",
        "Jeju Iho Tewoo Beach.jpg",
        "이호테우.jpg",
    ],
    "yangyang-surfyy-beach": [
        "Yangyang surfing.jpg",
        "Surfyy Beach.jpg",
        "Hajodae Beach, Yangyang (양양 하조대 해수욕장) - panoramio.jpg",
        "Naksan Beach.jpg",
    ],
    "jukdo-beach-yangyang": [
        "Jukdo Beach Yangyang.jpg",
        "죽도해수욕장.jpg",
        "Yangyang Jukdo Beach.jpg",
    ],
    "yeongildae-beach": [
        "영일대해수욕장.jpg",
        "Yeongildae Beach.jpg",
        "Yeongildae Pavilion on September 19th, 2016.jpg",
        "Korea-Pohang-Yeongildae-01.jpg",
    ],
    "goraebul-beach": [
        "Goraebul Beach.jpg",
        "고래불해수욕장.jpg",
        "Korea-Yeongdeok-Goraebul-01.jpg",
    ],
    "wolpo-beach": [
        "Wolpo Beach.jpg",
        "월포해수욕장.jpg",
        "Korea-Pohang-Wolpo-01.jpg",
    ],
    "gujora-beach": [
        "Gujora Beach.jpg",
        "구조라해수욕장.jpg",
        "Geoje Gujora.jpg",
    ],
    "wahyeon-sand-forest-beach": [
        "Wahyeon Beach.jpg",
        "와현해수욕장.jpg",
        "Geoje Wahyeon.jpg",
    ],
    "sangju-silver-sand-beach": [
        "Sangju Beach Namhae.jpg",
        "상주은모래비치.jpg",
        "Namhae Sangju Beach.jpg",
        "Namhae Gun County 37 (16513873940).jpg",
    ],
    "myeongsasipri-beach": [
        "Myeongsasimni Beach.jpg",
        "명사십리해수욕장.jpg",
        "Wando Myeongsasimni.jpg",
    ],
    "yulpo-pine-beach": [
        "Yulpo Beach.jpg",
        "율포해수욕장.jpg",
        "Boseong Yulpo.jpg",
    ],
    "namyeol-sunrise-beach": [
        "Namyeol Beach.jpg",
        "남열해돋이해수욕장.jpg",
        "Goheung Namyeol.jpg",
    ],
    "seonyudo-beach": [
        "Seonyudo Island.jpg",
        "선유도.jpg",
        "Gunsan Seonyudo.jpg",
        "Seonyudo Beach Gunsan.jpg",
        "Korea-Gunsan-Seonyudo-01.jpg",
    ],
    "byeonsan-beach": [
        "Byeonsan-bando.jpg",
        "Mt. Byeonsan Peninsula National Park - panoramio.jpg",
        "변산해수욕장.jpg",
        "Korea-Buan County-Chaeseokgang-01.jpg",
    ],
    "gyeokpo-beach": [
        "Korea-Buan County-Gyeokpo Harbor at dawn-01.jpg",
        "격포해수욕장.jpg",
        "Gyeokpo Beach.jpg",
    ],
    "kkotji-beach": [
        "Kkotji Beach in Buan.jpg",  # Commons title; verify after download
        "꽃지해수욕장.jpg",
        "Kkotji Beach.jpg",
        "Anmyeondo Kkotji.jpg",
    ],
    "chunjangdae-beach": [
        "Chunjangdae Beach.jpg",
        "춘장대해수욕장.jpg",
        "Korea-Seocheon-Chunjangdae-01.jpg",
    ],
    "muchangpo-beach": [
        "Muchangpo Beach.jpg",
        "무창포해수욕장.jpg",
        "Korea-Boryeong-Muchangpo-01.jpg",
    ],
    "jinha-beach": [
        "Jinha Beach.jpg",
        "진하해수욕장.jpg",
        "Korea-Ulsan-Jinha-01.jpg",
    ],
    "geumneung-beach": [
        # Prefer dedicated Geumneung if available; Hyeopjae is adjacent OK as last resort
        "Geumneung Beach.jpg",
        "금능해수욕장.jpg",
        "Hyeopjae Beach.jpg",
        "Hyeopjae.jpg",
    ],
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


def http_get(url: str, timeout: int = 90, retries: int = 2) -> bytes:
    last: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout, context=ssl_ctx()) as r:
                return r.read()
        except urllib.error.HTTPError as exc:
            last = exc
            if exc.code in (429, 503):
                wait = 45 + attempt * 45
                print(f"  rate-limit {exc.code}; sleep {wait}s", flush=True)
                time.sleep(wait)
                continue
            raise
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep(3)
    assert last is not None
    raise last


def filepath_url(title: str, width: int = 1280) -> str:
    return (
        "https://commons.wikimedia.org/wiki/Special:FilePath/"
        + urllib.parse.quote(title)
        + f"?width={width}"
    )


def save_jpeg(data: bytes, dest: Path) -> bool:
    if len(data) < 12000:
        return False
    if data[:32].lstrip().startswith(b"<") or data[:4] == b"<!DO":
        return False
    is_jpeg = len(data) >= 3 and data[0] == 0xFF and data[1] == 0xD8
    if is_jpeg:
        dest.write_bytes(data)
        return True
    try:
        from io import BytesIO

        from PIL import Image

        img = Image.open(BytesIO(data))
        if img.mode != "RGB":
            img = img.convert("RGB")
        img.save(dest, "JPEG", quality=85, optimize=True)
        return True
    except Exception:
        return False


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    fb_hash = md5(TYPE_FALLBACK)
    replaced = failed = 0
    remaining = []

    for slug, files in TARGETS.items():
        dest = IMG / f"{slug}.jpg"
        # Skip if already unique and not in force list — we only listed needful ones
        print(f"=== {slug}", flush=True)
        ok = False
        for title in files:
            print(f"TRY {title}", flush=True)
            time.sleep(4.0)
            try:
                data = http_get(filepath_url(title))
            except urllib.error.HTTPError as exc:
                print(f"  http {exc.code}", flush=True)
                continue
            except Exception as exc:  # noqa: BLE001
                print(f"  err {exc}", flush=True)
                continue
            if save_jpeg(data, dest) and md5(dest) != fb_hash:
                print(f"  OK {dest.stat().st_size} bytes", flush=True)
                ok = True
                replaced += 1
                break
            print("  bad payload", flush=True)
        if not ok:
            print("  FAIL", flush=True)
            failed += 1
            remaining.append(slug)
            dest.write_bytes(TYPE_FALLBACK.read_bytes())
        time.sleep(5.0)

    # Full inventory
    all_slugs = [
        "haeundae",
        "gwangalli-beach",
        "songjeong-beach",
        "dadaepo-beach",
        "songdo-beach",
        "ilgwang-beach",
        "eulwangni-beach",
        "wangsan-beach",
        "hanagae-beach",
        "sipripo-beach",
        "manseongni-black-sand-beach",
        "ungcheon-beach",
        "hyeopjae-beach",
        "geumneung-beach",
        "hamdeok-beach",
        "woljeong-beach",
        "gwakji-beach",
        "iho-tewoo-beach",
        "jungmun-saekdal-beach",
        "gimnyeong-beach",
        "pyoseon-beach",
        "sokcho-beach",
        "gyeongpo-beach",
        "anmok-beach",
        "gangmun-beach",
        "jumunjin-beach",
        "jeongdongjin-beach",
        "yangyang-surfyy-beach",
        "naksan-beach",
        "hajodae-beach",
        "jukdo-beach-yangyang",
        "samcheok-beach",
        "mangsang-beach",
        "songjiho-beach",
        "yeongildae-beach",
        "guryongpo-beach",
        "goraebul-beach",
        "wolpo-beach",
        "hakdong-pebble-beach",
        "gujora-beach",
        "wahyeon-sand-forest-beach",
        "sangju-silver-sand-beach",
        "myeongsasipri-beach",
        "yulpo-pine-beach",
        "namyeol-sunrise-beach",
        "seonyudo-beach",
        "byeonsan-beach",
        "gyeokpo-beach",
        "daecheon-beach",
        "kkotji-beach",
        "manripo-beach",
        "chunjangdae-beach",
        "muchangpo-beach",
        "ulsan-ilsan-beach",
        "jinha-beach",
    ]
    still = [s for s in all_slugs if md5(IMG / f"{s}.jpg") == fb_hash]
    unique = [s for s in all_slugs if s not in still]
    print(
        f"\nDONE replaced={replaced} failed={failed} "
        f"unique_total={len(unique)} remaining_fallback={len(still)}",
        flush=True,
    )
    print("REMAINING:", ", ".join(still), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
