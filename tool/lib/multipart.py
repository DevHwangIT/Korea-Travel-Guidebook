# -*- coding: utf-8 -*-
"""Minimal multipart/form-data parser (stdlib only)."""
from __future__ import annotations

from dataclasses import dataclass, field
from email.parser import BytesParser
from email.policy import default as email_policy
from typing import Any
from urllib.parse import parse_qs, unquote


@dataclass
class FormData:
    fields: dict[str, str] = field(default_factory=dict)
    files: dict[str, tuple[str, bytes]] = field(default_factory=dict)
    file_lists: dict[str, list[tuple[str, bytes]]] = field(default_factory=dict)
    lists: dict[str, list[str]] = field(default_factory=dict)
    # files[name] = last (filename, raw_bytes)
    # file_lists[name] = all uploads for that field (supports multiple)

    def get(self, name: str, default: str = "") -> str:
        return self.fields.get(name, default)

    def getlist(self, name: str) -> list[str]:
        if name in self.lists:
            return list(self.lists[name])
        if name in self.fields:
            return [self.fields[name]]
        return []

    def getfiles(self, name: str) -> list[tuple[str, bytes]]:
        if name in self.file_lists:
            return list(self.file_lists[name])
        if name in self.files:
            return [self.files[name]]
        return []


def _boundary_from_content_type(content_type: str) -> bytes | None:
    parts = [p.strip() for p in content_type.split(";")]
    for part in parts[1:]:
        if part.lower().startswith("boundary="):
            val = part.split("=", 1)[1].strip().strip('"')
            return val.encode("ascii", errors="ignore")
    return None


def _set_field(form: FormData, name: str, value: str) -> None:
    if name in form.fields:
        form.lists.setdefault(name, [form.fields[name]]).append(value)
        form.fields[name] = value
    else:
        form.fields[name] = value
        form.lists[name] = [value]


def parse_urlencoded(body: bytes) -> FormData:
    text = body.decode("utf-8", errors="replace")
    parsed = parse_qs(text, keep_blank_values=True)
    form = FormData()
    for k, values in parsed.items():
        form.lists[k] = list(values)
        form.fields[k] = values[-1] if values else ""
    return form


def parse_multipart(body: bytes, boundary: bytes) -> FormData:
    """Parse multipart body into fields and files."""
    form = FormData()
    if not boundary:
        return form

    delimiter = b"--" + boundary
    parts = body.split(delimiter)
    for part in parts:
        if not part or part in (b"--", b"--\r\n", b"--\n"):
            continue
        if part.startswith(b"--"):
            continue
        if part.startswith(b"\r\n"):
            part = part[2:]
        elif part.startswith(b"\n"):
            part = part[1:]
        if part.endswith(b"--\r\n"):
            part = part[:-4]
        elif part.endswith(b"--"):
            part = part[:-2]
        if part.endswith(b"\r\n"):
            part = part[:-2]
        elif part.endswith(b"\n"):
            part = part[:-1]

        header_blob, sep, content = part.partition(b"\r\n\r\n")
        if not sep:
            header_blob, sep, content = part.partition(b"\n\n")
        if not sep:
            continue

        header_bytes = header_blob + b"\r\n\r\n"
        msg = BytesParser(policy=email_policy).parsebytes(header_bytes)
        disp = msg.get("Content-Disposition", "")
        if not disp:
            continue
        params: dict[str, str] = {}
        for item in disp.split(";"):
            item = item.strip()
            if "=" in item:
                k, v = item.split("=", 1)
                params[k.strip().lower()] = v.strip().strip('"')
        name = params.get("name")
        if not name:
            continue
        filename = params.get("filename")
        if filename is not None:
            filename = unquote(filename)
            item = (filename, content)
            form.files[name] = item
            form.file_lists.setdefault(name, []).append(item)
        else:
            _set_field(form, name, content.decode("utf-8", errors="replace"))
    return form


def parse_request_body(content_type: str, body: bytes) -> FormData:
    ctype = (content_type or "").lower()
    if "multipart/form-data" in ctype:
        boundary = _boundary_from_content_type(content_type)
        if not boundary:
            raise ValueError("multipart boundary를 찾을 수 없습니다.")
        return parse_multipart(body, boundary)
    return parse_urlencoded(body)


def read_http_body(handler: Any, *, max_bytes: int) -> bytes:
    length = int(handler.headers.get("Content-Length") or 0)
    if length < 0:
        raise ValueError("잘못된 Content-Length")
    if length > max_bytes:
        raise ValueError(
            f"요청 본문이 너무 큽니다. 최대 약 {max_bytes // (1024 * 1024)}MB까지 가능합니다."
        )
    return handler.rfile.read(length) if length else b""
