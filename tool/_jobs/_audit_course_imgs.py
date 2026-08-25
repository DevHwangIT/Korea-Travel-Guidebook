# -*- coding: utf-8 -*-
from collections import defaultdict
from pathlib import Path
import json
import re

root = Path(__file__).resolve().parents[2]
files = {
    "incheon": root / "data/courses/incheon-curated.js",
    "gyeonggi": root / "data/courses/gyeonggi-curated.js",
    "seoul": root / "data/courses/seoul-curated.js",
}
ko = json.loads((root / "i18n/pages/travel-courses/ko.json").read_text(encoding="utf-8"))


def stop_name(region, cid, idx):
    try:
        if region == "seoul":
            return ko["travelCourses"]["seoulCurated"]["courses"][cid]["stops"][idx]["name"]
        return ko["travelCourses"]["curated"][region]["courses"][cid]["stops"][idx]["name"]
    except Exception:
        return "?"


usage = defaultdict(list)
missing = []
for region, path in files.items():
    text = path.read_text(encoding="utf-8")
    courses = re.findall(r'(?:id:|"id":)\s*"(c\d+)"(.*?)(?=\n  \{|\n\];|\n\])', text, re.S)
    print("===", region, "courses", len(courses))
    for cid, body in courses:
        cover_m = re.search(r'(?:cover:|"cover":)\s*"([^"]+)"', body)
        if cover_m:
            usage[cover_m.group(1)].append("%s/%s/COVER" % (region, cid))
        stop_blob = body.split("stops", 1)[-1]
        stops = re.findall(r"\{([^{}]+)\}", stop_blob)
        for i, s in enumerate(stops):
            img = re.search(r'(?:image:|"image":)\s*"([^"]+)"', s)
            place = re.search(r'(?:place:|"place":)\s*"([^"]+)"', s)
            time_m = re.search(r'(?:time:|"time":)\s*"([^"]+)"', s)
            name = stop_name(region, cid, i)
            rec = "%s/%s[%d] %s %s place=%s" % (
                region,
                cid,
                i,
                time_m.group(1) if time_m else "",
                name,
                place.group(1) if place else "-",
            )
            if img:
                usage[img.group(1)].append(rec)
                rel = img.group(1).replace("../../", "")
                if not (root / rel).exists():
                    print(" MISSING FILE", rel)
            else:
                missing.append(rec)

print("\n--- STOPS WITHOUT IMAGE ---")
for m in missing:
    print(" ", m)

print("\n--- DUPLICATE IMAGE FILES ---")
for img, refs in sorted(usage.items(), key=lambda x: -len(x[1])):
    if len(refs) > 1:
        print(img, "x%d" % len(refs))
        for r in refs:
            print("   ", r)
