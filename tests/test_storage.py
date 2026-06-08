from pathlib import Path

from amazon_letters_tutor.models import Chunk, SourceRecord
from amazon_letters_tutor.storage import AmazonLettersStore, normalize_fts_query, truncate_words
from amazon_letters_tutor.text_utils import sha256_text


def test_store_search_returns_citation_ready_hits(tmp_path: Path) -> None:
    store = AmazonLettersStore(tmp_path / "amazon_letters.sqlite")
    store.init_schema()
    source = SourceRecord(
        doc_id="amz_2016_pdf",
        year=2016,
        title="2016 Amazon shareholder letter",
        author="Jeffrey P. Bezos",
        source_url="https://s2.q4cdn.com/299287126/files/doc_financials/annual/2016-Letter-to-Shareholders.pdf",
        source_type="pdf",
        letter_type="bezos_letter",
    )
    store.upsert_sources([source])
    chunk = Chunk(
        chunk_id="amz_2016_bezos_disagree_and_commit_c0001_deadbeef",
        doc_id=source.doc_id,
        parent_chunk_id="parent",
        year=2016,
        author=source.author,
        source_url=source.source_url,
        source_type=source.source_type,
        letter_type=source.letter_type,
        section_title="Disagree and Commit",
        chunk_index=1,
        chunk_kind="child",
        text="Disagree and commit lets teams move fast without consensus.",
        text_hash=sha256_text("disagree and commit"),
        word_count=9,
    )
    store.replace_chunks(source.doc_id, [chunk])

    hits = store.search("disagree and commit", top_k=3)

    assert len(hits) == 1
    assert hits[0].year == 2016
    assert "Disagree and Commit" in hits[0].citation


def test_normalize_fts_query_handles_hyphenated_terms() -> None:
    assert normalize_fts_query("look-through earnings") == "look AND through AND earnings"


def test_truncate_words_limits_long_text() -> None:
    assert truncate_words("one two three four", 2) == "one two ..."
