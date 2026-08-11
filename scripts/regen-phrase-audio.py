# -*- coding: utf-8 -*-
"""Regenerate Korean phrase MP3s with edge-tts and prune unused files."""
from __future__ import annotations

import asyncio
import re
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "js" / "korean-phrases-data.js"
AUDIO = ROOT / "audio" / "korean"
VOICE = "ko-KR-SunHiNeural"

# Phrases whose Korean text changed or are newly added — always regenerate.
FORCE = {
    "excuse-me",
    "other-color",
    "to-airport",
    "how-to-go",
    "bus-stop",
    "where-am-i",
    "call-112",
    "call-119",
}


def load_phrases() -> dict[str, str]:
    text = DATA.read_text(encoding="utf-8")
    # naive extract of id/ko pairs in order
    ids = re.findall(r'"id":\s*"([^"]+)"', text)
    kos = re.findall(r'"ko":\s*"([^"]+)"', text)
    # swear + categories share structure; zip by appearance — but help appears twice
    # Better: parse objects
    objs = re.findall(
        r'\{\s*"id":\s*"([^"]+)",\s*"ko":\s*"([^"]+)"',
        text,
        flags=re.M,
    )
    out: dict[str, str] = {}
    for pid, ko in objs:
        out[pid] = ko  # last wins for duplicate help id (same text)
    return out


async def synth(pid: str, ko: str) -> None:
    out = AUDIO / f"{pid}.mp3"
    communicate = edge_tts.Communicate(ko, VOICE)
    await communicate.save(str(out))
    print(f"audio {pid}: {out.stat().st_size // 1024}KB | {ko}")


async def main() -> None:
    AUDIO.mkdir(parents=True, exist_ok=True)
    phrases = load_phrases()
    print(f"phrases: {len(phrases)}")

    to_make = []
    for pid, ko in phrases.items():
        path = AUDIO / f"{pid}.mp3"
        if pid in FORCE or not path.exists():
            to_make.append((pid, ko))

    # also regenerate if empty
    for pid, ko in phrases.items():
        path = AUDIO / f"{pid}.mp3"
        if path.exists() and path.stat().st_size < 500 and (pid, ko) not in to_make:
            to_make.append((pid, ko))

    for pid, ko in to_make:
        await synth(pid, ko)

    keep = set(phrases)
    removed = []
    for mp3 in AUDIO.glob("*.mp3"):
        if mp3.stem not in keep:
            mp3.unlink()
            removed.append(mp3.name)
    if removed:
        print("removed:", ", ".join(sorted(removed)))
    else:
        print("removed: none")


if __name__ == "__main__":
    asyncio.run(main())
