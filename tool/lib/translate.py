# -*- coding: utf-8 -*-
"""KO → EN/JA auto-translate for admin save (pluggable providers)."""
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
                f"번역 대신 한국어 복사: {self.copied}건 "
                "(API 키 없거나 엔진 실패)"
            )
        for err in self.errors[:5]:
            lines.append(f"번역 경고: {err}")
        return lines

    def flash_status(self) -> str:
        """Short Korean status for toast."""
        if self.translated > 0 and self.copied == 0:
            return "번역했어요 (영어·일본어)"
        if self.copied > 0 and self.translated == 0:
            return "번역 실패 — 한국어만 저장됨"
        if self.translated > 0 and self.copied > 0:
            return "일부만 번역했어요 (영어·일본어)"
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
            "API 키 없음 — EN/JA에 한국어를 복사합니다. "
            "품질을 높이려면 DEEPL_API_KEY / GOOGLE_TRANSLATE_API_KEY / "
            "OPENAI_API_KEY 중 하나를 설정하거나 pip install deep-translator"
        )
    return f"활성 번역: {p}"


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


def _translate_deepl(text: str, target: str) -> str:
    key = os.environ["DEEPL_API_KEY"].strip()
    # Free keys end with :fx
    base = (
        "https://api-free.deepl.com/v2/translate"
        if key.endswith(":fx")
        else "https://api.deepl.com/v2/translate"
    )
    tgt = "EN-US" if target == "en" else "JA"
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
    body = {
        "q": text,
        "source": "ko",
        "target": target,
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
    lang_name = "English" if target == "en" else "Japanese"
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

    # Google web scrape backend may choke on large HTML; send as-is when short.
    if _looks_html(text) and len(text) > 4500:
        plain = _plain_for_empty_check(text)
        translated = GoogleTranslator(source="ko", target=target).translate(plain)
        return f"<p>{translated}</p>" if translated else ""
    return GoogleTranslator(source="ko", target=target).translate(text) or ""


_PROVIDERS: dict[str, Callable[[str, str], str]] = {
    "deepl": _translate_deepl,
    "google": _translate_google,
    "openai": _translate_openai,
    "deep-translator": _translate_deep_translator,
}


def translate_text(text: str, target: str, *, status: BatchStatus | None = None) -> str:
    """Translate KO text to en or ja. On failure returns original KO (caller may copy)."""
    text = text or ""
    if not _plain_for_empty_check(text):
        return ""
    if target not in ("en", "ja"):
        raise ValueError("target must be en or ja")

    provider = detect_provider()
    if status is not None and not status.provider:
        status.provider = provider

    if provider == "copy":
        if status is not None:
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


def fill_lang_pair(
    ko: str,
    *,
    old_ko: str = "",
    old_en: str = "",
    old_ja: str = "",
    force: bool = False,
    status: BatchStatus | None = None,
) -> tuple[str, str]:
    """Return (en, ja) for a Korean string, reusing prior translations when KO unchanged."""
    ko = (ko or "").strip()
    old_ko = (old_ko or "").strip()
    old_en = (old_en or "").strip()
    old_ja = (old_ja or "").strip()
    if not ko:
        return "", ""
    if (
        not force
        and ko == old_ko
        and old_en
        and old_ja
    ):
        if status is not None:
            status.reused += 1
        return old_en, old_ja
    en = translate_text(ko, "en", status=status)
    ja = translate_text(ko, "ja", status=status)
    return en, ja


def fill_scalar_texts(
    texts: dict[str, dict[str, str]],
    fields: tuple[str, ...] | list[str],
    *,
    old_texts: dict[str, dict[str, str]] | None = None,
    force: bool = False,
    status: BatchStatus | None = None,
) -> dict[str, dict[str, str]]:
    """Fill EN/JA scalar fields from KO. Keeps non-empty form overrides unless force."""
    st = status if status is not None else BatchStatus()
    old = old_texts or {}
    out: dict[str, dict[str, str]] = {
        lang: dict(texts.get(lang) or {}) for lang in ("ko", "en", "ja")
    }
    for f in fields:
        ko = (out["ko"].get(f) or "").strip()
        out["ko"][f] = ko
        form_en = (out["en"].get(f) or "").strip()
        form_ja = (out["ja"].get(f) or "").strip()
        if form_en == ko:
            form_en = ""
        if form_ja == ko:
            form_ja = ""
        if form_en and form_ja and not force:
            out["en"][f] = form_en
            out["ja"][f] = form_ja
            st.reused += 1
            continue
        old_ko = ((old.get("ko") or {}).get(f) or "").strip()
        old_en = ((old.get("en") or {}).get(f) or "").strip()
        old_ja = ((old.get("ja") or {}).get(f) or "").strip()
        en, ja = fill_lang_pair(
            ko,
            old_ko=old_ko,
            old_en=old_en,
            old_ja=old_ja,
            force=force,
            status=st,
        )
        out["en"][f] = form_en if (form_en and not force) else en
        out["ja"][f] = form_ja if (form_ja and not force) else ja
    return out


def fill_body_blocks(
    blocks: list[dict[str, Any]],
    *,
    old_blocks: list[dict[str, Any]] | None = None,
    force: bool = False,
    status: BatchStatus | None = None,
) -> list[dict[str, Any]]:
    """Fill en/ja on text blocks from ko; image/youtube unchanged."""
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
        form_en = str(b.get("en") or "").strip()
        form_ja = str(b.get("ja") or "").strip()
        prev = old_text[ti] if ti < len(old_text) else {}
        ti += 1
        old_ko = str(prev.get("ko") or "").strip()
        old_en = str(prev.get("en") or "").strip()
        old_ja = str(prev.get("ja") or "").strip()
        # Treat en/ja identical to ko as "not provided" (legacy KO-copy filler).
        if form_en == ko:
            form_en = ""
        if form_ja == ko:
            form_ja = ""
        if form_en and form_ja and not force:
            b["en"] = form_en
            b["ja"] = form_ja
            st.reused += 1
            out.append(b)
            continue
        en, ja = fill_lang_pair(
            ko,
            old_ko=old_ko,
            old_en=old_en,
            old_ja=old_ja,
            force=force,
            status=st,
        )
        b["en"] = form_en if (form_en and not force) else en
        b["ja"] = form_ja if (form_ja and not force) else ja
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
