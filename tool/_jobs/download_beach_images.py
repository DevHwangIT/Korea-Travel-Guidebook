# -*- coding: utf-8 -*-
"""Fill remaining beach fallbacks via Wikipedia REST thumbnails + curated FilePath.

No Commons search API (avoids 429). Resume-friendly.
"""
from __future__ import annotations

import hashlib
import json
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
LOG = ROOT / "tool" / "_beach-photo-fetch-log.json"
CTX = None

# Remaining / all beaches: wiki REST titles + curated Commons filenames
BEACHES: dict[str, dict] = {
    "haeundae": {"wiki": ["해운대해수욕장"], "files": ["Haeundae_Beach.jpg"]},
    "gwangalli-beach": {
        "wiki": ["광안리해수욕장"],
        "files": ["Gwangalli_Beach_in_Busan.jpg"],
    },
    "songjeong-beach": {"wiki": ["송정해수욕장"], "files": []},
    "dadaepo-beach": {"wiki": ["다대포해수욕장"], "files": []},
    "songdo-beach": {"wiki": ["송도해수욕장"], "files": []},
    "ilgwang-beach": {
        "wiki": ["일광해수욕장"],
        "files": ["일광해수욕장.jpg", "Ilgwang_Beach.jpg"],
        "force": True,  # current image may be wrong place
    },
    "eulwangni-beach": {"wiki": ["을왕리해수욕장"], "files": []},
    "wangsan-beach": {"wiki": ["왕산해수욕장"], "files": ["Wangsan_Beach,_near_Incheon_Airport.jpg"]},
    "hanagae-beach": {"wiki": ["하나개해수욕장"], "files": []},
    "sipripo-beach": {
        "wiki": ["십리포해수욕장", "덕적도"],
        "files": ["Sipripo.jpg", "Deokjeokdo.jpg", "덕적도.jpg"],
    },
    "manseongni-black-sand-beach": {
        "wiki": ["만성리검은모래해변", "여수시"],
        "files": ["Manseongri.jpg", "Yeosu_Manseongri.jpg"],
    },
    "ungcheon-beach": {"wiki": ["웅천친수공원"], "files": ["Ungcheon_Beach_Park_01.jpg"]},
    "hyeopjae-beach": {"wiki": ["협재해수욕장"], "files": ["Hyeopjae.jpg"]},
    "geumneung-beach": {
        "wiki": ["금능해수욕장"],
        "files": ["Geumneung_Beach.jpg", "금능해수욕장.jpg", "Hyeopjae.jpg"],
    },
    "hamdeok-beach": {"wiki": ["함덕해수욕장"], "files": []},
    "woljeong-beach": {"wiki": ["월정리해수욕장"], "files": ["Jeju_woljeongri_beach_1.jpg"]},
    "gwakji-beach": {
        "wiki": ["곽지해수욕장"],
        "files": ["Gwakji_Beach_in_Jeju_Island,_2022.jpg"],
    },
    "iho-tewoo-beach": {
        "wiki": ["이호테우해수욕장"],
        "files": [
            "Iho_Tewoo_Beach.jpg",
            "이호테우해수욕장.jpg",
            "Iho_Beach.jpg",
            "Jeju_Iho_Tewoo.jpg",
        ],
    },
    "jungmun-saekdal-beach": {"wiki": ["중문색달해수욕장"], "files": ["Jungmun_Beach.jpg"]},
    "gimnyeong-beach": {"wiki": ["김녕해수욕장"], "files": []},
    "pyoseon-beach": {"wiki": ["표선해수욕장"], "files": []},
    "sokcho-beach": {"wiki": ["속초해수욕장"], "files": []},
    "gyeongpo-beach": {"wiki": ["경포해수욕장"], "files": []},
    "anmok-beach": {"wiki": ["안목해변"], "files": []},
    "gangmun-beach": {"wiki": ["강문해변"], "files": []},
    "jumunjin-beach": {"wiki": ["주문진해수욕장"], "files": []},
    "jeongdongjin-beach": {"wiki": ["정동진해수욕장"], "files": []},
    "yangyang-surfyy-beach": {
        "wiki": ["서피비치", "양양군"],
        "files": [
            "Yangyang_surfing.jpg",
            "Surfyy_Beach.jpg",
            "Yangyang_Beach.jpg",
            "양양_서핑.jpg",
        ],
    },
    "naksan-beach": {"wiki": ["낙산해수욕장"], "files": []},
    "hajodae-beach": {"wiki": ["하조대해수욕장"], "files": []},
    "jukdo-beach-yangyang": {
        "wiki": ["죽도해수욕장"],
        "files": ["Jukdo_Beach.jpg", "죽도해수욕장.jpg", "Yangyang_Jukdo.jpg"],
    },
    "samcheok-beach": {"wiki": ["삼척해수욕장"], "files": ["Korea-Samcheok-Beach-01.jpg"]},
    "mangsang-beach": {"wiki": ["망상해수욕장"], "files": []},
    "songjiho-beach": {
        "wiki": ["송지호해수욕장", "송지호"],
        "files": ["Songjiho.jpg", "송지호.jpg", "Songji_Lake.jpg"],
    },
    "yeongildae-beach": {
        "wiki": ["영일대해수욕장"],
        "files": ["Yeongildae_Beach.jpg", "영일대해수욕장.jpg", "Yeongilman.jpg"],
    },
    "guryongpo-beach": {
        "wiki": ["구룡포해수욕장", "구룡포"],
        "files": ["Guryongpo.jpg", "구룡포.jpg", "Guryongpo_Beach.jpg"],
    },
    "goraebul-beach": {
        "wiki": ["고래불해수욕장"],
        "files": ["Goraebul.jpg", "고래불해수욕장.jpg", "Goraebul_Beach.jpg"],
    },
    "wolpo-beach": {
        "wiki": ["월포해수욕장"],
        "files": ["Wolpo_Beach.jpg", "월포해수욕장.jpg"],
    },
    "hakdong-pebble-beach": {
        "wiki": ["학동흑진주몽돌해변", "학동몽돌해수욕장"],
        "files": [
            "Hakdong_Beach.jpg",
            "Hakdong_Mongdol.jpg",
            "학동몽돌해수욕장.jpg",
            "Geoje_Hakdong.jpg",
        ],
    },
    "gujora-beach": {
        "wiki": ["구조라해수욕장"],
        "files": ["Gujora_Beach.jpg", "구조라해수욕장.jpg"],
    },
    "wahyeon-sand-forest-beach": {
        "wiki": ["와현해수욕장"],
        "files": ["Wahyeon_Beach.jpg", "와현해수욕장.jpg"],
    },
    "sangju-silver-sand-beach": {
        "wiki": ["상주은모래비치", "상주해수욕장"],
        "files": ["Sangju_Beach.jpg", "상주은모래비치.jpg", "Namhae_Sangju.jpg"],
    },
    "myeongsasipri-beach": {
        "wiki": ["명사십리해수욕장"],
        "files": ["Myeongsasimni.jpg", "명사십리해수욕장.jpg", "Wando_Beach.jpg"],
    },
    "yulpo-pine-beach": {
        "wiki": ["율포해수욕장"],
        "files": ["Yulpo_Beach.jpg", "율포해수욕장.jpg", "Boseong_Yulpo.jpg"],
    },
    "namyeol-sunrise-beach": {
        "wiki": ["남열해돋이해수욕장"],
        "files": ["Namyeol_Beach.jpg", "남열해돋이해수욕장.jpg"],
    },
    "seonyudo-beach": {
        "wiki": ["선유도_(전라북도)", "선유도"],
        "files": ["Seonyudo.jpg", "선유도.jpg", "Seonyudo_Island.jpg"],
    },
    "byeonsan-beach": {
        "wiki": ["변산해수욕장"],
        "files": ["Byeonsan_Beach.jpg", "변산해수욕장.jpg", "Byeonsanbando.jpg"],
    },
    "gyeokpo-beach": {
        "wiki": ["격포해수욕장", "격포"],
        "files": ["Gyeokpo.jpg", "격포해수욕장.jpg", "Chaeseokgang.jpg"],
    },
    "daecheon-beach": {
        "wiki": ["대천해수욕장"],
        "files": ["Daecheon_Beach.jpg", "대천해수욕장.jpg", "Boryeong_Daecheon.jpg"],
    },
    "kkotji-beach": {
        "wiki": ["꽃지해수욕장"],
        "files": ["Kkotji_Beach.jpg", "꽃지해수욕장.jpg", "Anmyeondo_Kkotji.jpg"],
    },
    "manripo-beach": {
        "wiki": ["만리포해수욕장"],
        "files": ["Manripo_Beach.jpg", "만리포해수욕장.jpg", "Manripo.jpg"],
    },
    "chunjangdae-beach": {
        "wiki": ["춘장대해수욕장"],
        "files": ["Chunjangdae_Beach.jpg", "춘장대해수욕장.jpg"],
    },
    "muchangpo-beach": {
        "wiki": ["무창포해수욕장"],
        "files": ["Muchangpo_Beach.jpg", "무창포해수욕장.jpg", "Muchangpo.jpg"],
    },
    "ulsan-ilsan-beach": {
        "wiki": ["일산해수욕장_(울산)", "울산광역시"],
        "files": [
            "Ilsan_Beach_Ulsan.jpg",
            "울산_일산해수욕장.jpg",
            "Ilsan_Beach.jpg",
            "Ulsan_Ilsan_Beach.jpg",
        ],
    },
    "jinha-beach": {
        "wiki": ["진하해수욕장"],
        "files": ["Jinha_Beach.jpg", "진하해수욕장.jpg", "Jinha_Ulsan.jpg"],
    },
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


def http_get(url: str, timeout: int = 60, retries: int = 2) -> bytes:
    last: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout, context=ssl_ctx()) as r:
                return r.read()
        except urllib.error.HTTPError as exc:
            last = exc
            if exc.code in (429, 503):
                wait = 30 + attempt * 30
                print(f"  rate-limit {exc.code}; sleep {wait}s", flush=True)
                time.sleep(wait)
                continue
            if exc.code == 404:
                raise
            time.sleep(2)
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep(2)
    assert last is not None
    raise last


def save_image_bytes(data: bytes, dest: Path) -> bool:
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
        dest.write_bytes(data)
        return dest.stat().st_size >= 12000


def wiki_rest_thumb(title: str) -> str | None:
    # REST uses underscores
    enc = urllib.parse.quote(title.replace(" ", "_"), safe="")
    url = f"https://ko.wikipedia.org/api/rest_v1/page/summary/{enc}"
    try:
        data = json.loads(http_get(url, retries=2).decode())
    except Exception as exc:  # noqa: BLE001
        print(f"  rest err: {exc}", flush=True)
        return None
    thumb = (data.get("thumbnail") or {}).get("source")
    original = (data.get("originalimage") or {}).get("source")
    # Prefer larger original if present
    return original or thumb


def filepath_url(title: str, width: int = 1280) -> str:
    # Special:FilePath accepts spaces or underscores
    return (
        "https://commons.wikimedia.org/wiki/Special:FilePath/"
        + urllib.parse.quote(title)
        + f"?width={width}"
    )


def try_url(url: str, dest: Path) -> bool:
    try:
        return save_image_bytes(http_get(url, timeout=90, retries=2), dest)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            print("  404", flush=True)
        else:
            print(f"  http {exc.code}", flush=True)
        return False
    except Exception as exc:  # noqa: BLE001
        print(f"  err {exc}", flush=True)
        return False


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    fallback_hash = md5(TYPE_FALLBACK)
    results = []
    replaced = kept = failed = 0

    for slug, meta in BEACHES.items():
        dest = IMG / f"{slug}.jpg"
        force = bool(meta.get("force"))
        if (
            not force
            and dest.exists()
            and md5(dest) != fallback_hash
            and dest.stat().st_size > 20000
        ):
            print(f"KEEP {slug}", flush=True)
            kept += 1
            results.append({"slug": slug, "status": "kept"})
            continue

        print(f"=== {slug}", flush=True)
        ok = False
        info: dict = {}

        for wtitle in meta.get("wiki") or []:
            print(f"REST {wtitle}", flush=True)
            time.sleep(3.5)
            thumb = wiki_rest_thumb(wtitle)
            if not thumb:
                continue
            # Skip tiny icons sometimes returned
            print(f"TRY rest {thumb[:90]}...", flush=True)
            if try_url(thumb, dest):
                ok = True
                info = {"source": "wiki-rest", "title": wtitle, "url": thumb, "bytes": dest.stat().st_size}
                break

        if not ok:
            for title in meta.get("files") or []:
                print(f"TRY file {title}", flush=True)
                time.sleep(2.5)
                if try_url(filepath_url(title), dest):
                    ok = True
                    info = {"source": "filepath", "title": title, "bytes": dest.stat().st_size}
                    break

        if ok and dest.exists() and md5(dest) != fallback_hash:
            print(f"  OK {info.get('bytes')} <- {info.get('title')}", flush=True)
            replaced += 1
            results.append({"slug": slug, "status": "replaced", **info})
        else:
            print("  FAIL", flush=True)
            failed += 1
            results.append({"slug": slug, "status": "failed"})
            dest.write_bytes(TYPE_FALLBACK.read_bytes())
        time.sleep(3.0)

    remaining = [
        s for s in BEACHES if (IMG / f"{s}.jpg").exists() and md5(IMG / f"{s}.jpg") == fallback_hash
    ]
    unique = [s for s in BEACHES if s not in remaining]
    summary = {
        "replaced": replaced,
        "kept": kept,
        "failed": failed,
        "unique_total": len(unique),
        "remaining_fallback": remaining,
        "results": results,
    }
    LOG.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"\nDONE replaced={replaced} kept={kept} failed={failed} "
        f"unique_total={len(unique)} remaining_fallback={len(remaining)}",
        flush=True,
    )
    if remaining:
        print("REMAINING:", ", ".join(remaining), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
