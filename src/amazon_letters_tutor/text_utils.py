from __future__ import annotations

import hashlib
import re
from pathlib import Path

WORD_RE = re.compile(r"\S+")
YEAR_RE = re.compile(r"(19|20)\d{2}")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalize_whitespace(text: str) -> str:
    lines = []
    for raw_line in text.replace("\r", "\n").split("\n"):
        line = re.sub(r"[ \t]+", " ", raw_line).strip()
        if line:
            lines.append(line)
    return "\n\n".join(lines)


def word_count(text: str) -> int:
    return len(WORD_RE.findall(text))


def slugify(value: str, max_len: int = 48) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return (value or "section")[:max_len].strip("_")


def infer_year(*values: str) -> int | None:
    for value in values:
        match = YEAR_RE.search(value)
        if match:
            return int(match.group(0))
    return None
