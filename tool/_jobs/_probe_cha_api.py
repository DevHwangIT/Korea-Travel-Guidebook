# -*- coding: utf-8 -*-
from __future__ import annotations

import ssl
import urllib.parse
import urllib.request

UA = "KoreaTravelGuidebook/1.0 (educational place covers)"
CTX = ssl._create_unverified_context()


def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=40, context=CTX) as r:
        return r.read()


def main() -> None:
    q = "명옥헌"
    bases = [
        "http://www.khs.go.kr/cha/SearchKindOpenapiList.do",
        "http://www.cha.go.kr/cha/SearchKindOpenapiList.do",
    ]
    variants = []
    for enc in ("utf-8", "euc-kr"):
        qs = urllib.parse.urlencode(
            {"ccbaCndt": q, "pageUnit": 5, "pageIndex": 1},
            encoding=enc,
        )
        variants.append((enc, "ccbaCndt", qs))
        qs2 = urllib.parse.urlencode(
            {"ccbaMnm1": q, "pageUnit": 5, "pageIndex": 1},
            encoding=enc,
        )
        variants.append((enc, "ccbaMnm1", qs2))
        qs3 = urllib.parse.urlencode(
            {"st": q, "pageUnit": 5, "pageIndex": 1},
            encoding=enc,
        )
        variants.append((enc, "st", qs3))

    for base in bases[:1]:
        for enc, key, qs in variants:
            url = f"{base}?{qs}"
            print(f"\n=== {enc} {key} ===")
            try:
                data = get(url)
            except Exception as exc:
                print("ERR", exc)
                continue
            text = data.decode("utf-8", errors="replace")
            # print first item name
            if "<ccbaMnm1>" in text:
                start = text.find("<ccbaMnm1>")
                print(text[start : start + 180].replace("\n", " "))
                print("total", text[text.find("<totalCnt>") : text.find("</totalCnt>") + 11])
            else:
                print(text[:400])

    # Direct image lookup for 명승 58 전남
    for kd, asno, ct in (
        ("16", "0000580000000", "36"),
        ("15", "0000580000000", "36"),
        ("16", "00580000", "36"),
    ):
        url = (
            "http://www.khs.go.kr/cha/SearchImageOpenapi.do?"
            + urllib.parse.urlencode(
                {"ccbaKdcd": kd, "ccbaAsno": asno, "ccbaCtcd": ct}
            )
        )
        print("\n=== IMAGE", kd, asno, ct, "===")
        try:
            data = get(url)
            print(data.decode("utf-8", errors="replace")[:1500])
        except Exception as exc:
            print("ERR", exc)


if __name__ == "__main__":
    main()
