# -*- coding: utf-8 -*-
"""KO → all GUIDE_LANGS auto-translate for admin save (pluggable providers).

Primary targets (en/ja/zh) are translated from Korean.
Secondary targets (zh-Hant/vi/th/ru) try the same engines; if unsupported or
failed, they copy English (preferred) then Korean so locale JSON keys always exist.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Callable

# In-process cache: (provider, target, sha256(ko)) → translated text
_CACHE: dict[tuple[str, str, str], str] = {}

_HTML_RE = re.compile(r"<[a-zA-Z][^>]*>")
_TAG_RE = re.compile(r"<[^>]+>")

# Keep in sync with i18n_store.LANGS / js/i18n.js GUIDE_LANGS (minus ko).
PRIMARY_TARGET_LANGS = ("en", "ja", "zh")
SECONDARY_TARGET_LANGS = ("zh-Hant", "vi", "th", "ru")
TARGET_LANGS = PRIMARY_TARGET_LANGS + SECONDARY_TARGET_LANGS
ALL_TEXT_LANGS = ("ko",) + TARGET_LANGS


@dataclass
class BatchStatus:
    """Aggregate outcome for one save operation."""

    translated: int = 0
    reused: int = 0
    copied: int = 0
    errors: list[str] = field(default_factory=list)
    provider: str = ""

    def note_lines(self) -> list[str]:
        lines: list[str] = []
        if self.provider:
            lines.append(f"번역 엔진: {self.provider}")
        if self.translated:
            lines.append(f"새로 번역: {self.translated}건")
        if self.reused:
            lines.append(f"변경 없어 기존 번역 유지: {self.reused}건")
        if self.copied:
            lines.append(
                f"번역 대신 EN/KO 복사: {self.copied}건 "
                "(API 키 없거나 엔진 미지원/실패)"
            )
        for err in self.errors[:5]:
            lines.append(f"번역 경고: {err}")
        return lines

    def flash_status(self) -> str:
        """Short Korean status for toast."""
        if self.translated > 0 and self.copied == 0:
            return "번역했어요 (전체 언어)"
        if self.copied > 0 and self.translated == 0:
            return "번역 실패 — 한국어·영문 복사로 저장"
        if self.translated > 0 and self.copied > 0:
            return "일부만 번역했어요 (나머지는 EN 복사)"
        # reused-only: no new translation work — keep toast as plain save
        return ""


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _looks_html(text: str) -> bool:
    return bool(_HTML_RE.search(text or ""))


def _plain_for_empty_check(text: str) -> str:
    t = _TAG_RE.sub(" ", text or "")
    t = re.sub(r"\s+", " ", t).strip()
    return t


def detect_provider() -> str:
    if os.environ.get("DEEPL_API_KEY", "").strip():
        return "deepl"
    if os.environ.get("GOOGLE_TRANSLATE_API_KEY", "").strip():
        return "google"
    if os.environ.get("OPENAI_API_KEY", "").strip():
        return "openai"
    try:
        import deep_translator  # noqa: F401

        return "deep-translator"
    except ImportError:
        return "copy"


def provider_hint() -> str:
    p = detect_provider()
    if p == "copy":
        return (
            "API 키 없음 — EN/JA/ZH/繁中/VI/TH/RU에 한국어 또는 영문을 복사합니다. "
            "품질을 높이려면 DEEPL_API_KEY / GOOGLE_TRANSLATE_API_KEY / "
            "OPENAI_API_KEY 중 하나를 설정하거나 pip install deep-translator"
        )
    return f"활성 번역: {p} (en/ja/zh + zh-Hant/vi/th/ru)"


def _http_json(
    url: str,
    *,
    method: str = "POST",
    headers: dict[str, str] | None = None,
    data: bytes | None = None,
    timeout: float = 45.0,
) -> dict[str, Any]:
    req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
    return json.loads(raw) if raw else {}


# DeepL: VI/TH not supported on all plans — missing keys fall back to EN copy.
_DEEPL_TARGETS = {
    "en": "EN-US",
    "ja": "JA",
    "zh": "ZH-HANS",
    "zh-Hant": "ZH-HANT",
    "ru": "RU",
}
_OPENAI_LANG_NAMES = {
    "en": "English",
    "ja": "Japanese",
    "zh": "Simplified Chinese",
    "zh-Hant": "Traditional Chinese (Taiwan)",
    "vi": "Vietnamese",
    "th": "Thai",
    "ru": "Russian",
}
_GOOGLE_TARGETS = {
    "en": "en",
    "ja": "ja",
    "zh": "zh-CN",
    "zh-Hant": "zh-TW",
    "vi": "vi",
    "th": "th",
    "ru": "ru",
}


def _translate_deepl(text: str, target: str) -> str:
    key = os.environ["DEEPL_API_KEY"].strip()
    # Free keys end with :fx
    base = (
        "https://api-free.deepl.com/v2/translate"
        if key.endswith(":fx")
        else "https://api.deepl.com/v2/translate"
    )
    tgt = _DEEPL_TARGETS.get(target)
    if not tgt:
        raise ValueError(f"DeepL unsupported target: {target}")
    payload = {
        "auth_key": key,
        "text": text,
        "source_lang": "KO",
        "target_lang": tgt,
    }
    if _looks_html(text):
        payload["tag_handling"] = "html"
    data = urllib.parse.urlencode(payload, doseq=True).encode("utf-8")
    out = _http_json(
        base,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=data,
    )
    translations = out.get("translations") or []
    if not translations:
        raise RuntimeError("DeepL 응답에 translations 없음")
    return str(translations[0].get("text") or "")


def _translate_google(text: str, target: str) -> str:
    key = os.environ["GOOGLE_TRANSLATE_API_KEY"].strip()
    url = "https://translation.googleapis.com/language/translate/v2?" + urllib.parse.urlencode(
        {"key": key}
    )
    g_target = _GOOGLE_TARGETS.get(target, target)
    body = {
        "q": text,
        "source": "ko",
        "target": g_target,
        "format": "html" if _looks_html(text) else "text",
    }
    out = _http_json(
        url,
        headers={"Content-Type": "application/json; charset=utf-8"},
        data=json.dumps(body).encode("utf-8"),
    )
    data = out.get("data") or {}
    translations = data.get("translations") or []
    if not translations:
        raise RuntimeError("Google Translate 응답 비어 있음")
    return str(translations[0].get("translatedText") or "")


def _translate_openai(text: str, target: str) -> str:
    key = os.environ["OPENAI_API_KEY"].strip()
    model = os.environ.get("OPENAI_TRANSLATE_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"
    lang_name = _OPENAI_LANG_NAMES.get(target, target)
    system = (
        "You are a travel-guide translator. Translate Korean into the target language. "
        "Preserve HTML tags and structure if present. Return only the translation, "
        "no quotes or commentary."
    )
    user = f"Target language: {lang_name}\n\n{text}"
    body = {
        "model": model,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    out = _http_json(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
        },
        data=json.dumps(body).encode("utf-8"),
    )
    choices = out.get("choices") or []
    if not choices:
        raise RuntimeError("OpenAI 응답 비어 있음")
    msg = (choices[0].get("message") or {}).get("content") or ""
    return str(msg).strip()


def _translate_deep_translator(text: str, target: str) -> str:
    from deep_translator import GoogleTranslator

    g_target = _GOOGLE_TARGETS.get(target, target)
    # Google web scrape backend may choke on large HTML; send as-is when short.
    if _looks_html(text) and len(text) > 4500:
        plain = _plain_for_empty_check(text)
        translated = GoogleTranslator(source="ko", target=g_target).translate(plain)
        return f"<p>{translated}</p>" if translated else ""
    return GoogleTranslator(source="ko", target=g_target).translate(text) or ""


_PROVIDERS: dict[str, Callable[[str, str], str]] = {
    "deepl": _translate_deepl,
    "google": _translate_google,
    "openai": _translate_openai,
    "deep-translator": _translate_deep_translator,
}


def translate_text(text: str, target: str, *, status: BatchStatus | None = None) -> str:
    """Translate KO text to a TARGET_LANG. On failure returns original KO (caller may copy EN)."""
    text = text or ""
    if not _plain_for_empty_check(text):
        return ""
    if target not in TARGET_LANGS:
        raise ValueError(f"target must be one of {TARGET_LANGS}")

    provider = detect_provider()
    if status is not None and not status.provider:
        status.provider = provider

    if provider == "copy":
        if status is not None:
            status.copied += 1
        return text

    # DeepL may not support vi/th — skip engine and let caller copy EN.
    if provider == "deepl" and target not in _DEEPL_TARGETS:
        if status is not None:
            status.errors.append(f"deepl/{target}: unsupported — will copy EN")
            status.copied += 1
        return text

    cache_key = (provider, target, _sha(text))
    if cache_key in _CACHE:
        return _CACHE[cache_key]

    try:
        fn = _PROVIDERS[provider]
        out = fn(text, target)
        out = (out or "").strip()
        if not out:
            raise RuntimeError("빈 번역 결과")
        _CACHE[cache_key] = out
        if status is not None:
            status.translated += 1
        return out
    except Exception as exc:  # noqa: BLE001
        if status is not None:
            status.errors.append(f"{provider}/{target}: {exc}")
            status.copied += 1
        return text


def fill_lang_targets(
    ko: str,
    *,
    old: dict[str, str] | None = None,
    force: bool = False,
    status: BatchStatus | None = None,
) -> dict[str, str]:
    """Return all TARGET_LANGS for a Korean string.

    Secondary langs (zh-Hant/vi/th/ru) prefer a real translation; if the engine
    copied Korean (or failed), fall back to English so public locales stay usable.
    """
    ko = (ko or "").strip()
    prev = old or {}
    old_ko = (prev.get("ko") or "").strip()
    if not ko:
        return {lang: "" for lang in TARGET_LANGS}
    existing = {lang: (prev.get(lang) or "").strip() for lang in TARGET_LANGS}
    if not force and ko == old_ko and all(existing.values()):
        if status is not None:
            status.reused += 1
        return existing

    out: dict[str, str] = {}
    for lang in PRIMARY_TARGET_LANGS:
        out[lang] = translate_text(ko, lang, status=status)

    en = (out.get("en") or "").strip() or ko
    for lang in SECONDARY_TARGET_LANGS:
        raw = translate_text(ko, lang, status=status)
        # If engine fell back to KO (copy/unsupported), prefer EN for secondary locales.
        if not raw or raw.strip() == ko:
            out[lang] = en
        else:
            out[lang] = raw
    return out


def fill_lang_pair(
    ko: str,
    *,
    old_ko: str = "",
    old_en: str = "",
    old_ja: str = "",
    old_zh: str = "",
    force: bool = False,
    status: BatchStatus | None = None,
) -> tuple[str, str]:
    """Return (en, ja) for a Korean string (legacy helper; prefer fill_lang_targets)."""
    filled = fill_lang_targets(
        ko,
        old={"ko": old_ko, "en": old_en, "ja": old_ja, "zh": old_zh},
        force=force,
        status=status,
    )
    return filled["en"], filled["ja"]


def fill_scalar_texts(
    texts: dict[str, dict[str, str]],
    fields: tuple[str, ...] | list[str],
    *,
    old_texts: dict[str, dict[str, str]] | None = None,
    force: bool = False,
    status: BatchStatus | None = None,
) -> dict[str, dict[str, str]]:
    """Fill all TARGET_LANGS scalar fields from KO. Keeps non-empty form overrides unless force."""
    st = status if status is not None else BatchStatus()
    old = old_texts or {}
    out: dict[str, dict[str, str]] = {
        lang: dict(texts.get(lang) or {}) for lang in ALL_TEXT_LANGS
    }
    for f in fields:
        ko = (out["ko"].get(f) or "").strip()
        out["ko"][f] = ko
        form: dict[str, str] = {}
        for lang in TARGET_LANGS:
            val = (out[lang].get(f) or "").strip()
            if val == ko:
                val = ""
            form[lang] = val
        if all(form.values()) and not force:
            for lang in TARGET_LANGS:
                out[lang][f] = form[lang]
            st.reused += 1
            continue
        old_map = {
            "ko": ((old.get("ko") or {}).get(f) or "").strip(),
            **{
                lang: ((old.get(lang) or {}).get(f) or "").strip()
                for lang in TARGET_LANGS
            },
        }
        filled = fill_lang_targets(ko, old=old_map, force=force, status=st)
        for lang in TARGET_LANGS:
            out[lang][f] = form[lang] if (form[lang] and not force) else filled[lang]
    return out


def fill_body_blocks(
    blocks: list[dict[str, Any]],
    *,
    old_blocks: list[dict[str, Any]] | None = None,
    force: bool = False,
    status: BatchStatus | None = None,
) -> list[dict[str, Any]]:
    """Fill all TARGET_LANGS on text blocks from ko; image/youtube unchanged."""
    st = status or BatchStatus()
    old_list = list(old_blocks or [])
    old_text = [b for b in old_list if str(b.get("type") or "") == "text"]
    ti = 0
    out: list[dict[str, Any]] = []
    for block in blocks:
        b = dict(block)
        if str(b.get("type") or "").lower() != "text":
            out.append(b)
            continue
        ko = str(b.get("ko") or "").strip()
        form: dict[str, str] = {}
        for lang in TARGET_LANGS:
            val = str(b.get(lang) or "").strip()
            if val == ko:
                val = ""
            form[lang] = val
        prev = old_text[ti] if ti < len(old_text) else {}
        ti += 1
        if all(form.values()) and not force:
            for lang in TARGET_LANGS:
                b[lang] = form[lang]
            st.reused += 1
            out.append(b)
            continue
        old_map = {
            "ko": str(prev.get("ko") or "").strip(),
            **{
                lang: str(prev.get(lang) or "").strip() for lang in TARGET_LANGS
            },
        }
        filled = fill_lang_targets(ko, old=old_map, force=force, status=st)
        for lang in TARGET_LANGS:
            b[lang] = form[lang] if (form[lang] and not force) else filled[lang]
        out.append(b)
    if status is not None and not status.provider and st.provider:
        status.provider = st.provider
    return out


def merge_flash(ok_msg: str, status: BatchStatus | None, notes: list[str] | None = None) -> str:
    """Build toast: primary line + optional translate status + detail notes."""
    parts = [ok_msg]
    if status:
        suffix = status.flash_status()
        if suffix:
            parts[0] = f"{ok_msg} · {suffix}"
        detail = list(notes or []) + status.note_lines()
    else:
        detail = list(notes or [])
    detail = [n for n in detail if n and str(n).strip()]
    if not detail:
        return parts[0]
    return parts[0] + "\n" + "\n".join(detail)
