# -*- coding: utf-8 -*-
"""Fix shopping/souvenir keys that still equal English (or empty) in non-EN locales.

Translates from English (polished guidebook copy) via deep-translator Google,
with atomic write retries for Windows file locks.
"""
from __future__ import annotations

import json
import re
import sys
import tempfile
import time
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
ROOT = TOOL_DIR.parent
sys.path.insert(0, str(TOOL_DIR))

from lib import i18n_store  # noqa: E402
from lib.cache_bust import bump_asset_version  # noqa: E402

SHOP = ROOT / "i18n" / "pages" / "shopping"
LANGS = ["ko", "en", "ja", "zh", "zh-Hant", "vi", "th", "ru"]
TARGETS = ["ja", "zh", "zh-Hant", "vi", "th", "ru"]
NS = ("buyHub", "souvenir", "shopping")
SKIP_SUFFIX = ("Img", "Url", "URL", "Href", "href", "Path", "path", "src")
LATIN = re.compile(r"[A-Za-z]{3,}")
NON_LATIN = re.compile(
    r"[\u3040-\u30ff\u3400-\u9fff\uac00-\ud7af\u0e00-\u0e7f\u0400-\u04ff]"
)
G_TARGETS = {
    "ja": "ja",
    "zh": "zh-CN",
    "zh-Hant": "zh-TW",
    "vi": "vi",
    "th": "th",
    "ru": "ru",
}
CACHE: dict[tuple[str, str], str] = {}
LOG = TOOL_DIR / "_tmp_shopping_i18n_fix_log.txt"


def looks_english(s: str) -> bool:
    if not isinstance(s, str) or not s.strip():
        return True
    latin = len(LATIN.findall(s))
    non = len(NON_LATIN.findall(s))
    if latin >= 2 and non == 0:
        return True
    if latin >= 1 and non == 0 and len(s) > 15:
        return True
    return False


def skip_key(key: str, val: str) -> bool:
    if key.endswith(SKIP_SUFFIX):
        return True
    if val.startswith(("http://", "https://", "Images/", "./", "../")):
        return True
    return False


def needs_fix(loc_val: str | None, en_val: str) -> bool:
    if loc_val is None or loc_val == "":
        return True
    if loc_val == en_val and looks_english(en_val):
        return True
    return False


def write_retry(path: Path, text: str, attempts: int = 16) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    last: Exception | None = None
    for i in range(attempts):
        tmp = None
        try:
            fd, tmp = tempfile.mkstemp(
                prefix=f".{path.stem}-", suffix=".tmp", dir=str(path.parent)
            )
            with open(fd, "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
            Path(tmp).replace(path)
            return
        except OSError as e:
            last = e
            time.sleep(0.4 + i * 0.3)
            if tmp:
                try:
                    Path(tmp).unlink(missing_ok=True)
                except OSError:
                    pass
    raise last  # type: ignore[misc]


def load_all() -> dict[str, dict]:
    return {
        lang: json.loads((SHOP / f"{lang}.json").read_text(encoding="utf-8"))
        for lang in LANGS
    }


def save_lang_page(lang: str, data: dict) -> None:
    write_retry(
        SHOP / f"{lang}.json",
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
    )


def translate_en(text: str, target: str) -> str:
    from deep_translator import GoogleTranslator

    text = (text or "").strip()
    if not text:
        return ""
    key = (target, text)
    if key in CACHE:
        return CACHE[key]
    g = G_TARGETS[target]
    last_err: Exception | None = None
    for attempt in range(5):
        try:
            out = GoogleTranslator(source="en", target=g).translate(text) or ""
            out = out.strip()
            if out:
                CACHE[key] = out
                return out
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            time.sleep(0.8 + attempt * 0.8)
    if last_err:
        print(f"translate fail {target}: {last_err}", flush=True)
    return ""


def collect_jobs(data: dict[str, dict], *, force_keys: set[str] | None = None) -> list[tuple[str, str, str]]:
    """Collect keys needing work. force_keys are 'ns.key' always re-translated (EN→targets)."""
    en = data["en"]
    jobs: list[tuple[str, str, str]] = []
    seen: set[tuple[str, str]] = set()
    force_keys = force_keys or set()
    for ns in NS:
        en_ns = en.get(ns) or {}
        for key, en_val in en_ns.items():
            if not isinstance(en_val, str) or skip_key(key, en_val):
                continue
            fq = f"{ns}.{key}"
            any_need = fq in force_keys
            if not any_need:
                for loc in TARGETS:
                    loc_val = (data[loc].get(ns) or {}).get(key)
                    if needs_fix(loc_val if isinstance(loc_val, str) else None, en_val):
                        any_need = True
                        break
            if any_need and (ns, key) not in seen:
                seen.add((ns, key))
                jobs.append((ns, key, en_val))
    return jobs


def load_force_keys() -> set[str]:
    report = TOOL_DIR / "_tmp_shopping_untranslated.txt"
    keys: set[str] = set()
    if not report.is_file():
        return keys
    for line in report.read_text(encoding="utf-8").splitlines():
        if line.startswith(("buyHub.", "souvenir.", "shopping.")):
            keys.add(line.split("\t", 1)[0])
    return keys


def fix_bad_ko_mt(data: dict[str, dict]) -> int:
    """Re-translate JA/ZH strings that still look broken (e.g. に住む from 사는)."""
    bad_markers = ("に住む", "住む微細")
    fixed = 0
    en_souv = data["en"].get("souvenir") or {}
    for loc in TARGETS:
        souv = data[loc].setdefault("souvenir", {})
        for key, val in list(souv.items()):
            if not isinstance(val, str):
                continue
            en_val = en_souv.get(key)
            if not isinstance(en_val, str):
                continue
            if any(m in val for m in bad_markers):
                tr = translate_en(en_val, loc)
                time.sleep(0.05)
                if tr:
                    souv[key] = tr
                    fixed += 1
    return fixed


def sync_nested_from_flat(data: dict[str, dict]) -> int:
    """If souvenir has nested Body arrays, fill missing target langs from flat keys when possible."""
    fixed = 0
    ko_souv = data["ko"].get("souvenir") or {}
    for key, blocks in ko_souv.items():
        if not isinstance(blocks, list):
            continue
        # Prefer per-lang flat keys: fooBody1 / fooBody2 / fooTip
        base = key[:-4] if key.endswith("Body") else key
        for i, block in enumerate(blocks):
            if not isinstance(block, dict):
                continue
            en_t = str(block.get("en") or "").strip()
            for lang in TARGETS:
                cur = str(block.get(lang) or "").strip()
                if cur and not (en_t and cur == en_t and looks_english(en_t)):
                    continue
                # try flat key match
                flat = None
                for cand in (f"{base}Body{i+1}", f"{base}Tip", key):
                    v = (data[lang].get("souvenir") or {}).get(cand)
                    if isinstance(v, str) and v.strip() and v != en_t:
                        flat = v
                        break
                if flat:
                    block[lang] = flat
                    fixed += 1
                elif en_t:
                    tr = translate_en(en_t, lang)
                    time.sleep(0.05)
                    if tr:
                        block[lang] = tr
                        fixed += 1
        for loc in LANGS:
            data[loc].setdefault("souvenir", {})[key] = blocks
    return fixed


def main() -> int:
    data = load_all()
    force_keys = load_force_keys()
    bad = fix_bad_ko_mt(data)
    print(f"fixed_bad_mt={bad} force_keys={len(force_keys)}", flush=True)

    jobs = collect_jobs(data, force_keys=force_keys)
    print(f"jobs={len(jobs)}", flush=True)
    lines = [f"jobs={len(jobs)} bad_mt={bad} force={len(force_keys)}"]
    fixed_cells = 0

    for i, (ns, key, en_val) in enumerate(jobs, 1):
        fq = f"{ns}.{key}"
        force = fq in force_keys
        for loc in TARGETS:
            loc_ns = data[loc].setdefault(ns, {})
            cur = loc_ns.get(key)
            if not force and not needs_fix(cur if isinstance(cur, str) else None, en_val):
                continue
            cache_hit = (loc, en_val.strip()) in CACHE
            tr = translate_en(en_val, loc)
            if not cache_hit:
                time.sleep(0.05)
            if not tr:
                loc_ns[key] = en_val
            else:
                loc_ns[key] = tr
                if tr != en_val:
                    fixed_cells += 1
        if i % 15 == 0 or i == len(jobs):
            msg = f"progress {i}/{len(jobs)} fixed_cells={fixed_cells}"
            print(msg, flush=True)
            lines.append(msg)
            for loc in TARGETS:
                save_lang_page(loc, data[loc])

    nested = sync_nested_from_flat(data)
    lines.append(f"nested_fixed={nested}")
    print(f"nested_fixed={nested}", flush=True)

    for loc in LANGS:
        save_lang_page(loc, data[loc])

    # Re-audit remaining English leftovers (ignore short brand equals)
    remaining = []
    for ns in NS:
        en_ns = data["en"].get(ns) or {}
        for key, en_val in en_ns.items():
            if not isinstance(en_val, str) or skip_key(key, en_val):
                continue
            for loc in TARGETS:
                cur = (data[loc].get(ns) or {}).get(key)
                if needs_fix(cur if isinstance(cur, str) else None, en_val):
                    if (
                        isinstance(cur, str)
                        and cur == en_val
                        and len(en_val) <= 28
                        and not any(
                            w in en_val.lower()
                            for w in (
                                " the ",
                                " and ",
                                " with ",
                                " from ",
                                " for ",
                                " — ",
                                " - ",
                            )
                        )
                        and en_val.count(" ") <= 2
                    ):
                        continue
                    remaining.append(f"{loc}.{ns}.{key}")

    lines.append(f"fixed_cells={fixed_cells} remaining_notable={len(remaining)}")
    lines.extend(remaining[:40])
    print(f"remaining_notable={len(remaining)}", flush=True)

    print("build_bundle…", flush=True)
    lines.append(str(i18n_store.build_bundle()))
    lines.append(str(bump_asset_version()))
    LOG.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[-6:]), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
