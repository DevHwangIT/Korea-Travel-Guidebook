# -*- coding: utf-8 -*-
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
p = ROOT / "data/places/places-coords.js"
text = p.read_text(encoding="utf-8")
repls = {
    'slug: "ananti-osiria"': ('Images/places/_types/city.jpg', 'Images/places/_courses/osiria.jpg'),
    'slug: "blueline-cheongsapo"': ('Images/places/_types/city.jpg', 'Images/places/city/haeundae-blueline-park.jpg'),
    'slug: "busosanseong"': ('Images/places/_types/heritage.jpg', 'Images/places/heritage/busosanseot.jpg'),
    'slug: "buyeo-museum"': ('Images/places/_types/heritage.jpg', 'Images/places/heritage/gukrimbuyeobakmulgwan.jpg'),
    'slug: "daritdol"': ('Images/places/_types/nature.jpg', 'Images/places/_courses/cheongsapo.jpg'),
    'slug: "dolsan-park"': ('Images/places/_types/nature.jpg', 'Images/places/nature/dolsando.jpg'),
    'slug: "geommeolle"': ('Images/places/_types/beach.jpg', 'Images/places/_courses/udo-beach.jpg'),
    'slug: "gongsanseong"': ('Images/places/_types/heritage.jpg', 'Images/places/heritage/gotsanseot.jpg'),
    'slug: "gwangalli"': ('Images/places/_types/beach.jpg', 'Images/places/beach/gwangalli-beach.jpg'),
    'slug: "gyeongpodae"': ('Images/places/_types/heritage.jpg', 'Images/places/lake/gyeongpo-lake.jpg'),
    'slug: "gyochon-woljeonggyo"': ('Images/places/_types/heritage.jpg', 'Images/places/heritage/wolyeotgyo.jpg'),
    'slug: "hajodae"': ('Images/places/_types/beach.jpg', 'Images/places/beach/hajodae-beach.jpg'),
    'slug: "isunsin-square"': ('Images/places/_types/city.jpg', 'Images/places/_courses/yi-sunsin-square.jpg'),
    'slug: "jagalchi"': ('Images/places/_types/market.jpg', 'Images/places/market/jagalchi-market.jpg'),
    'slug: "jeonpo-cafe"': ('Images/places/_types/city.jpg', 'Images/places/_courses/jeonpo.jpg'),
    'slug: "kkoji-beach"': ('Images/places/_types/beach.jpg', 'Images/places/beach/kkotji-beach.jpg'),
    'slug: "metasequoia-damyang"': ('Images/places/_types/nature.jpg', 'Images/places/_courses/metasequoia-road.jpg'),
    'slug: "mokpo-modern"': ('Images/places/_types/heritage.jpg', 'Images/places/heritage/mokpo-geundaeyeoksamunhwagotgan.jpg'),
    'slug: "muryeong-tombs"': ('Images/places/_types/heritage.jpg', 'Images/places/_courses/muryeong-tomb.jpg'),
    'slug: "nami-island"': ('Images/places/_types/nature.jpg', 'Images/places/_courses/nami-trees.jpg'),
    'slug: "national-science-museum"': ('Images/places/_types/city.jpg', 'Images/places/_courses/daejeon-science-museum.jpg'),
    'slug: "oeongchi"': ('Images/places/_types/nature.jpg', 'Images/places/_courses/oeongchi-hyanggiro.jpg'),
    'slug: "olle-market"': ('Images/places/_types/market.jpg', 'Images/places/market/seogwipo-maeil-olle-market.jpg'),
    'slug: "sungsimdang"': ('Images/places/_types/city.jpg', 'Images/places/food-bread-daejeon.jpg'),
    'slug: "tongyeong-cable"': ('Images/places/_types/city.jpg', 'Images/places/_courses/tongyeong-cablecar.jpg'),
    'slug: "anmok-coffee"': ('Images/places/_types/city.jpg', 'Images/places/food-cafe-anmok.jpg'),
}
for marker, (old, new) in repls.items():
    idx = text.find(marker)
    if idx < 0:
        print("no slug", marker)
        continue
    end = text.find("\n", idx)
    chunk = text[idx:end]
    if old in chunk:
        text = text[:idx] + chunk.replace(old, new, 1) + text[end:]
        print("fixed", marker)
    else:
        print("already", marker)
p.write_text(text, encoding="utf-8")
