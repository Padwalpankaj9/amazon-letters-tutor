from __future__ import annotations

import json
import re
import sqlite3
from collections.abc import Iterable
from pathlib import Path

from amazon_letters_tutor.models import Chunk, ContextBlock, SearchHit, SourceRecord

FTS_TERM_RE = re.compile(r"[A-Za-z0-9]+")


def normalize_fts_query(query: str) -> str:
    terms = FTS_TERM_RE.findall(query)
    if not terms:
        raise ValueError("Search query must contain at least one word or number.")
    return " AND ".join(terms)


def truncate_words(text: str, max_words: int) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]) + " ..."


class AmazonLettersStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def init_schema(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    doc_id TEXT PRIMARY KEY,
                    year INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    author TEXT NOT NULL,
                    source_url TEXT NOT NULL UNIQUE,
                    source_type TEXT NOT NULL,
                    letter_type TEXT NOT NULL,
                    local_file_path TEXT,
                    raw_sha256 TEXT,
                    extracted_file_path TEXT,
                    text_sha256 TEXT,
                    ingestion_date TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS chunks (
                    chunk_id TEXT PRIMARY KEY,
                    doc_id TEXT NOT NULL REFERENCES documents(doc_id),
                    parent_chunk_id TEXT,
                    year INTEGER NOT NULL,
                    author TEXT NOT NULL,
                    source_url TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    letter_type TEXT NOT NULL,
                    section_title TEXT NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    chunk_kind TEXT NOT NULL,
                    text TEXT NOT NULL,
                    text_hash TEXT NOT NULL,
                    word_count INTEGER NOT NULL,
                    page_start INTEGER,
                    page_end INTEGER,
                    previous_chunk_id TEXT,
                    next_chunk_id TEXT
                );

                CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
                    chunk_id UNINDEXED,
                    text,
                    section_title,
                    year UNINDEXED,
                    author UNINDEXED
                );

                CREATE TABLE IF NOT EXISTS retrieval_logs (
                    query_id TEXT PRIMARY KEY,
                    query_text TEXT NOT NULL,
                    mode TEXT NOT NULL,
                    retrieved_chunk_ids TEXT NOT NULL,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            self._ensure_column(conn, "chunks", "page_start", "INTEGER")
            self._ensure_column(conn, "chunks", "page_end", "INTEGER")

    def _ensure_column(
        self,
        conn: sqlite3.Connection,
        table_name: str,
        column_name: str,
        column_type: str,
    ) -> None:
        columns = {row["name"] for row in conn.execute(f"PRAGMA table_info({table_name})")}
        if column_name not in columns:
            conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")

    def upsert_sources(self, sources: Iterable[SourceRecord]) -> int:
        rows = list(sources)
        with self.connect() as conn:
            conn.executemany(
                """
                INSERT INTO documents (
                    doc_id, year, title, author, source_url, source_type, letter_type
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(source_url) DO UPDATE SET
                    doc_id = excluded.doc_id,
                    year = excluded.year,
                    title = excluded.title,
                    author = excluded.author,
                    source_type = excluded.source_type,
                    letter_type = excluded.letter_type
                """,
                [
                    (
                        row.doc_id,
                        row.year,
                        row.title,
                        row.author,
                        row.source_url,
                        row.source_type,
                        row.letter_type,
                    )
                    for row in rows
                ],
            )
        return len(rows)

    def update_raw_file(self, doc_id: str, local_file_path: Path, raw_sha256: str) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                UPDATE documents
                SET local_file_path = ?, raw_sha256 = ?
                WHERE doc_id = ?
                """,
                (str(local_file_path), raw_sha256, doc_id),
            )

    def update_extracted_file(
        self,
        doc_id: str,
        extracted_file_path: Path,
        text_sha256: str,
    ) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                UPDATE documents
                SET extracted_file_path = ?, text_sha256 = ?
                WHERE doc_id = ?
                """,
                (str(extracted_file_path), text_sha256, doc_id),
            )

    def list_documents(self) -> list[sqlite3.Row]:
        with self.connect() as conn:
            return list(conn.execute("SELECT * FROM documents ORDER BY year"))

    def get_document(self, doc_id: str) -> sqlite3.Row | None:
        with self.connect() as conn:
            return conn.execute("SELECT * FROM documents WHERE doc_id = ?", (doc_id,)).fetchone()

    def get_document_by_year(self, year: int) -> sqlite3.Row | None:
        with self.connect() as conn:
            return conn.execute(
                "SELECT * FROM documents WHERE year = ? ORDER BY source_type LIMIT 1", (year,)
            ).fetchone()

    def downloaded_documents(self) -> list[sqlite3.Row]:
        with self.connect() as conn:
            return list(
                conn.execute(
                    """
                    SELECT * FROM documents
                    WHERE local_file_path IS NOT NULL
                    ORDER BY year
                    """
                )
            )

    def extracted_documents(self) -> list[sqlite3.Row]:
        with self.connect() as conn:
            return list(
                conn.execute(
                    """
                    SELECT * FROM documents
                    WHERE extracted_file_path IS NOT NULL
                    ORDER BY year
                    """
                )
            )

    def replace_chunks(self, doc_id: str, chunks: Iterable[Chunk]) -> int:
        rows = list(chunks)
        with self.connect() as conn:
            existing = list(conn.execute("SELECT chunk_id FROM chunks WHERE doc_id = ?", (doc_id,)))
            for row in existing:
                conn.execute("DELETE FROM chunks_fts WHERE chunk_id = ?", (row["chunk_id"],))
            conn.execute("DELETE FROM chunks WHERE doc_id = ?", (doc_id,))
            conn.executemany(
                """
                INSERT INTO chunks (
                    chunk_id, doc_id, parent_chunk_id, year, author, source_url,
                    source_type, letter_type, section_title, chunk_index, chunk_kind,
                    text, text_hash, word_count, page_start, page_end,
                    previous_chunk_id, next_chunk_id
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        chunk.chunk_id,
                        chunk.doc_id,
                        chunk.parent_chunk_id,
                        chunk.year,
                        chunk.author,
                        chunk.source_url,
                        chunk.source_type,
                        chunk.letter_type,
                        chunk.section_title,
                        chunk.chunk_index,
                        chunk.chunk_kind,
                        chunk.text,
                        chunk.text_hash,
                        chunk.word_count,
                        chunk.page_start,
                        chunk.page_end,
                        chunk.previous_chunk_id,
                        chunk.next_chunk_id,
                    )
                    for chunk in rows
                ],
            )
            conn.executemany(
                """
                INSERT INTO chunks_fts (chunk_id, text, section_title, year, author)
                VALUES (?, ?, ?, ?, ?)
                """,
                [
                    (
                        chunk.chunk_id,
                        chunk.text,
                        chunk.section_title,
                        chunk.year,
                        chunk.author,
                    )
                    for chunk in rows
                    if chunk.chunk_kind == "child"
                ],
            )
        return len(rows)

    def search(self, query: str, top_k: int = 8, year: int | None = None) -> list[SearchHit]:
        sql = """
            SELECT c.chunk_id, c.year, c.author, c.section_title, c.source_url,
                   c.page_start, c.page_end,
                   bm25(chunks_fts) AS score, c.text
            FROM chunks_fts
            JOIN chunks c ON c.chunk_id = chunks_fts.chunk_id
            WHERE chunks_fts MATCH ?
        """
        params: list[str | int] = [normalize_fts_query(query)]
        if year is not None:
            sql += " AND c.year = ?"
            params.append(year)
        sql += " ORDER BY score LIMIT ?"
        params.append(top_k)
        with self.connect() as conn:
            return [
                SearchHit(
                    chunk_id=row["chunk_id"],
                    year=row["year"],
                    author=row["author"],
                    section_title=row["section_title"],
                    source_url=row["source_url"],
                    score=row["score"],
                    text=row["text"],
                    page_start=row["page_start"],
                    page_end=row["page_end"],
                )
                for row in conn.execute(sql, params)
            ]

    def inspect_chunk(self, chunk_id: str) -> sqlite3.Row | None:
        with self.connect() as conn:
            return conn.execute("SELECT * FROM chunks WHERE chunk_id = ?", (chunk_id,)).fetchone()

    def child_chunks(self) -> list[sqlite3.Row]:
        with self.connect() as conn:
            return list(
                conn.execute(
                    """
                    SELECT * FROM chunks
                    WHERE chunk_kind = 'child'
                    ORDER BY year, chunk_index
                    """
                )
            )

    def search_hit_from_chunk(self, chunk_id: str, score: float = 0.0) -> SearchHit | None:
        row = self.inspect_chunk(chunk_id)
        if row is None:
            return None
        return SearchHit(
            chunk_id=row["chunk_id"],
            year=row["year"],
            author=row["author"],
            section_title=row["section_title"],
            source_url=row["source_url"],
            score=score,
            text=row["text"],
            page_start=row["page_start"],
            page_end=row["page_end"],
        )

    def expand_hit(
        self,
        hit: SearchHit,
        rank: int,
        include_parent: bool = False,
        max_words_per_chunk: int = 450,
    ) -> ContextBlock:
        row = self.inspect_chunk(hit.chunk_id)
        if row is None:
            return ContextBlock(
                rank=rank,
                hit=hit,
                expanded_chunk_ids=[hit.chunk_id],
                text=hit.text,
            )
        candidate_ids = [row["previous_chunk_id"], row["chunk_id"], row["next_chunk_id"]]
        if include_parent:
            candidate_ids.insert(0, row["parent_chunk_id"])
        seen: set[str] = set()
        chunks: list[sqlite3.Row] = []
        for chunk_id in candidate_ids:
            if not chunk_id or chunk_id in seen:
                continue
            seen.add(chunk_id)
            expanded = self.inspect_chunk(chunk_id)
            if expanded is not None:
                chunks.append(expanded)
        text_parts = []
        for expanded in chunks:
            ljassy = (
                "matched chunk"
                if expanded["chunk_id"] == hit.chunk_id
                else expanded["chunk_kind"]
            )
            text_parts.append(
                f"{ljassy}: {expanded['chunk_id']}\n"
                f"{truncate_words(expanded['text'], max_words_per_chunk)}"
            )
        parent_line = ""
        if row["parent_chunk_id"] and not include_parent:
            parent_line = f"parent_context: {row['parent_chunk_id']}\n\n"
        return ContextBlock(
            rank=rank,
            hit=hit,
            expanded_chunk_ids=[chunk["chunk_id"] for chunk in chunks],
            text=parent_line + "\n\n".join(text_parts),
        )

    def log_retrieval(self, query_id: str, query: str, mode: str, chunk_ids: list[str]) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO retrieval_logs (query_id, query_text, mode, retrieved_chunk_ids)
                VALUES (?, ?, ?, ?)
                """,
                (query_id, query, mode, json.dumps(chunk_ids)),
            )
