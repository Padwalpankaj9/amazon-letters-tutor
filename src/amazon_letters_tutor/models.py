from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SourceRecord:
    doc_id: str
    year: int
    title: str
    author: str
    source_url: str
    source_type: str
    letter_type: str


@dataclass(frozen=True)
class ExtractedDocument:
    doc_id: str
    year: int
    author: str
    source_url: str
    source_type: str
    letter_type: str
    local_file_path: Path
    text: str


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    doc_id: str
    parent_chunk_id: str | None
    year: int
    author: str
    source_url: str
    source_type: str
    letter_type: str
    section_title: str
    chunk_index: int
    chunk_kind: str
    text: str
    text_hash: str
    word_count: int
    page_start: int | None = None
    page_end: int | None = None
    previous_chunk_id: str | None = None
    next_chunk_id: str | None = None


@dataclass(frozen=True)
class SearchHit:
    chunk_id: str
    year: int
    author: str
    section_title: str
    source_url: str
    score: float
    text: str
    page_start: int | None = None
    page_end: int | None = None

    @property
    def citation(self) -> str:
        page_part = ""
        if self.page_start is not None and self.page_end is not None:
            if self.page_start == self.page_end:
                page_part = f", p. {self.page_start}"
            else:
                page_part = f", pp. {self.page_start}-{self.page_end}"
        return f"{self.year} {self.author} letter, {self.section_title}{page_part}"


@dataclass(frozen=True)
class ContextBlock:
    rank: int
    hit: SearchHit
    expanded_chunk_ids: list[str]
    text: str

    @property
    def citation(self) -> str:
        return self.hit.citation
