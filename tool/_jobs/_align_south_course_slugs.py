# -*- coding: utf-8 -*-
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
repls = {
    "chungcheong-curated.js": [
        ('place: "muryeong-tomb"', 'place: "muryeong-tombs"'),
        ('place: "kkotji-beach"', 'place: "kkoji-beach"'),
        ('place: "kkotji-sunset"', 'place: "kkoji-sunset"'),
        ('place: "daejeon-science-museum"', 'place: "national-science-museum"'),
        ('place: "seongsimdang"', 'place: "sungsimdang"'),
        ('place: "daejeon-oldtown"', 'place: "daejeon-downtown"'),
    ],
    "jeolla-curated.js": [
        ('place: "jeonju-lunch"', 'place: "jeonju-bibimbap"'),
        ('place: "yeosu-cablecar"', 'place: "yeosu-cable"'),
        ('place: "yi-sunsin-square"', 'place: "isunsin-square"'),
        ('place: "yeosu-nangman-pocha"', 'place: "nangman-pocha"'),
        ('place: "suncheon-yongsan"', 'place: "yongsan-observatory"'),
        ('place: "metasequoia-road"', 'place: "metasequoia-damyang"'),
        ('place: "yulpo-walk"', 'place: "yulpo-coast"'),
        ('place: "mokpo-geundaeyeoksamunhwagotgan"', 'place: "mokpo-modern"'),
        ('place: "mokpo-cablecar"', 'place: "mokpo-cable"'),
        ('place: "mokpo-peace-plaza"', 'place: "gatbawi-mokpo"'),
    ],
    "gyeongsang-curated.js": [
        ('place: "woljeonggyo"', 'place: "gyochon-woljeonggyo"'),
        ('place: "byeongsan-seowon"', 'place: "byeongsanseowon"'),
        ('place: "wolyeonggyo"', 'place: "woryeonggyo"'),
        ('place: "tongyeong-cablecar"', 'place: "tongyeong-cable"'),
        ('place: "tongyeong-isunsin-park"', 'place: "yi-sun-sin-park"'),
        ('place: "oedo-botania"', 'place: "oeodo-botania"'),
        ('place: "windy-hill"', 'place: "baramui-eondeok"'),
        ('place: "yeongildae"', 'place: "yeongildae-beach"'),
        ('place: "space-walk"', 'place: "spacewalk"'),
        ('place: "daegu-modern-alley"', 'place: "daegu-modern"'),
        ('place: "haeinsa-cafe"', 'place: "hapcheon-cafe"'),
    ],
    "busan-curated.js": [
        ('place: "haeundae-blueline-park"', 'place: "blueline-cheongsapo"'),
        ('place: "cheongsapo"', 'place: "daritdol"'),
        ('place: "songdo-beach"', 'place: "busan-songdo"'),
        ('place: "songdo-cablecar"', 'place: "songdo-cable"'),
        ('place: "osiria"', 'place: "ananti-osiria"'),
        ('place: "yeongdo-cafe-2"', 'place: "yeongdo-cafe"'),
        ('place: "jeonpo"', 'place: "jeonpo-cafe"'),
    ],
    "jeju-curated.js": [
        ('place: "udo-beach"', 'place: "geommeolle"'),
        ('place: "westjeju-cafe"', 'place: "west-jeju-cafe"'),
        ('place: "westjeju-sunset"', 'place: "west-jeju-sunset"'),
        ('place: "gwokji"', 'place: "gwakji-beach"'),
        ('place: "saeyeon-bridge"', 'place: "saeyeongyo"'),
        ('place: "seogwipo-maeil-olle-market"', 'place: "olle-market"'),
        ('place: "jungmun-saekdal-beach"', 'place: "jungmun-beach"'),
        ('place: "jeju-mokgwanaji"', 'place: "jejumok-gwana"'),
        ('place: "dongmun-market"', 'place: "jeju-dongmun-market"'),
        ('place: "yongnuni"', 'place: "yongnuni-oreum"'),
        ('place: "eastjeju-cafe"', 'place: "east-jeju-cafe"'),
        ('place: "sagye-sunset"', 'place: "southwest-sunset"'),
    ],
}
featured = {
    "chungcheong-curated.js": ["c01", "c02", "c03", "c04"],
    "jeolla-curated.js": ["c01", "c02", "c03"],
    "gyeongsang-curated.js": ["c01", "c02", "c03", "c04"],
    "busan-curated.js": ["c01", "c02", "c03", "c04"],
    "jeju-curated.js": ["c01", "c02", "c03", "c04", "c05", "c07"],
}

for name, pairs in repls.items():
    path = ROOT / "data/courses" / name
    text = path.read_text(encoding="utf-8")
    for old, new in pairs:
        text = text.replace(old, new)
    for cid in featured[name]:
        marker = 'id: "%s",\n    featured: true' % cid
        if marker not in text:
            text = text.replace(
                'id: "%s",\n    mobility:' % cid,
                'id: "%s",\n    featured: true,\n    mobility:' % cid,
                1,
            )
    path.write_text(text, encoding="utf-8", newline="\n")
    print("patched", name)
