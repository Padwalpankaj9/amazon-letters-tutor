from pathlib import Path

from amazon_letters_tutor.evals import GoldenQuestion, evaluate_question
from amazon_letters_tutor.models import Chunk, SourceRecord
from amazon_letters_tutor.storage import AmazonLettersStore
from amazon_letters_tutor.text_utils import sha256_text


def test_evaluate_question_passes_when_expected_year_is_retrieved(tmp_path: Path) -> None:
    store = AmazonLettersStore(tmp_path / "amazon_letters.sqlite")
    store.init_schema()
    source = SourceRecord(
        doc_id="amz_2017_pdf",
        year=2017,
        title="2017 Amazon shareholder letter",
        author="Jeffrey P. Bezos",
        source_url="https://s2.q4cdn.com/299287126/files/doc_financials/annual/Amazon_Shareholder_Letter.pdf",
        source_type="pdf",
        letter_type="bezos_letter",
    )
    store.upsert_sources([source])
    text = "High standards are teachable, contagious, and domain specific."
    store.replace_chunks(
        source.doc_id,
        [
            Chunk(
                chunk_id="amz_2017_bezos_high_standards_c0001_deadbeef",
                doc_id=source.doc_id,
                parent_chunk_id="parent",
                year=2017,
                author=source.author,
                source_url=source.source_url,
                source_type=source.source_type,
                letter_type=source.letter_type,
                section_title="High Standards",
                chunk_index=1,
                chunk_kind="child",
                text=text,
                text_hash=sha256_text(text),
                word_count=7,
            )
        ],
    )

    result = evaluate_question(
        store,
        GoldenQuestion(
            id="high_standards",
            query="high standards",
            expected_years=[2017],
            must_contain_terms=["high", "standards"],
        ),
    )

    assert result.passed is True


def test_evaluate_question_supports_expected_no_hits(tmp_path: Path) -> None:
    store = AmazonLettersStore(tmp_path / "amazon_letters.sqlite")
    store.init_schema()

    result = evaluate_question(
        store,
        GoldenQuestion(
            id="abstain",
            query="insurance float",
            expected_years=[],
            must_contain_terms=[],
            expect_no_hits=True,
        ),
    )

    assert result.passed is True
