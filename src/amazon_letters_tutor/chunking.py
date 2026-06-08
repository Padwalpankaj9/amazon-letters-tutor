from __future__ import annotations

import re
from pathlib import Path

from amazon_letters_tutor.config import ProjectConfig
from amazon_letters_tutor.models import Chunk
from amazon_letters_tutor.storage import AmazonLettersStore
from amazon_letters_tutor.text_utils import sha256_text, slugify, word_count

SECTION_HINT_RE = re.compile(r"^[A-Z][A-Za-z0-9,'&() -]{3,80}$")
PAGE_MARKER_RE = re.compile(r"^\[Page (?P<page>\d+)\]$")


def split_paragraphs(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]


def looks_like_section_title(paragraph: str) -> bool:
    if "\n" in paragraph:
        return False
    if word_count(paragraph) > 10:
        return False
    return bool(SECTION_HINT_RE.match(paragraph)) and not paragraph.endswith(".")


def chunk_words(text: str, target_words: int, overlap_words: int) -> list[str]:
    words = text.split()
    if len(words) <= target_words:
        return [text]
    chunks = []
    step = max(target_words - overlap_words, 1)
    for start in range(0, len(words), step):
        piece = words[start : start + target_words]
        if not piece:
            continue
        chunks.append(" ".join(piece))
        if start + target_words >= len(words):
            break
    return chunks


def make_child_id(year: int, author: str, section_title: str, index: int, text: str) -> str:
    author_slug = "jassy" if "Jassy" in author else "bezos"
    section_slug = slugify(section_title)
    return f"amz_{year}_{author_slug}_{section_slug}_c{index:04d}_{sha256_text(text)[:8]}"


def make_parent_id(year: int, author: str, index: int, text: str) -> str:
    author_slug = "jassy" if "Jassy" in author else "bezos"
    return f"amz_{year}_{author_slug}_parent_{index:04d}_{sha256_text(text)[:8]}"


def build_chunks_for_document(
    config: ProjectConfig,
    *,
    doc_id: str,
    year: int,
    author: str,
    source_url: str,
    source_type: str,
    letter_type: str,
    extracted_file_path: Path,
) -> list[Chunk]:
    text = extracted_file_path.read_text(encoding="utf-8")
    paragraphs = split_paragraphs(text)
    section_title = "Full letter"
    sectioned_paragraphs: list[tuple[str, str, int | None]] = []
    current_page: int | None = None
    for paragraph in paragraphs:
        page_match = PAGE_MARKER_RE.match(paragraph)
        if page_match:
            current_page = int(page_match.group("page"))
            continue
        if looks_like_section_title(paragraph):
            section_title = paragraph
            continue
        sectioned_paragraphs.append((section_title, paragraph, current_page))

    parents: list[Chunk] = []
    children: list[Chunk] = []
    parent_index = 0
    child_index = 0
    buffer: list[tuple[str, str, int | None]] = []
    buffer_words = 0

    def flush_parent() -> None:
        nonlocal parent_index, child_index, buffer, buffer_words
        if not buffer:
            return
        parent_text = "\n\n".join(paragraph for _, paragraph, _ in buffer)
        parent_section = buffer[0][0]
        parent_pages = [page for _, _, page in buffer if page is not None]
        page_start = min(parent_pages) if parent_pages else None
        page_end = max(parent_pages) if parent_pages else None
        parent_id = make_parent_id(year, author, parent_index, parent_text)
        parents.append(
            Chunk(
                chunk_id=parent_id,
                doc_id=doc_id,
                parent_chunk_id=None,
                year=year,
                author=author,
                source_url=source_url,
                source_type=source_type,
                letter_type=letter_type,
                section_title=parent_section,
                chunk_index=parent_index,
                chunk_kind="parent",
                text=parent_text,
                text_hash=sha256_text(parent_text),
                word_count=word_count(parent_text),
                page_start=page_start,
                page_end=page_end,
            )
        )
        for child_text in chunk_words(
            parent_text, config.child_target_words, config.child_overlap_words
        ):
            child_id = make_child_id(year, author, parent_section, child_index, child_text)
            children.append(
                Chunk(
                    chunk_id=child_id,
                    doc_id=doc_id,
                    parent_chunk_id=parent_id,
                    year=year,
                    author=author,
                    source_url=source_url,
                    source_type=source_type,
                    letter_type=letter_type,
                    section_title=parent_section,
                    chunk_index=child_index,
                    chunk_kind="child",
                    text=child_text,
                    text_hash=sha256_text(child_text),
                    word_count=word_count(child_text),
                    page_start=page_start,
                    page_end=page_end,
                )
            )
            child_index += 1
        parent_index += 1
        buffer = []
        buffer_words = 0

    for item in sectioned_paragraphs:
        _, paragraph, _ = item
        paragraph_words = word_count(paragraph)
        if buffer and buffer_words + paragraph_words > config.parent_target_words:
            flush_parent()
        buffer.append(item)
        buffer_words += paragraph_words
    flush_parent()

    linked_children: list[Chunk] = []
    for index, chunk in enumerate(children):
        previous_id = children[index - 1].chunk_id if index > 0 else None
        next_id = children[index + 1].chunk_id if index + 1 < len(children) else None
        linked_children.append(
            Chunk(
                **{
                    **chunk.__dict__,
                    "previous_chunk_id": previous_id,
                    "next_chunk_id": next_id,
                }
            )
        )
    return parents + linked_children


def chunk_all(config: ProjectConfig, store: AmazonLettersStore, year: int | None = None) -> int:
    total = 0
    rows = [store.get_document_by_year(year)] if year is not None else store.extracted_documents()
    for row in rows:
        if row is None or not row["extracted_file_path"]:
            continue
        chunks = build_chunks_for_document(
            config,
            doc_id=row["doc_id"],
            year=row["year"],
            author=row["author"],
            source_url=row["source_url"],
            source_type=row["source_type"],
            letter_type=row["letter_type"],
            extracted_file_path=Path(row["extracted_file_path"]),
        )
        total += store.replace_chunks(row["doc_id"], chunks)
    return total
