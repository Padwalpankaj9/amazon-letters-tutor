from pathlib import Path

from amazon_letters_tutor.extract import (
    normalize_pre_text,
    to_markdown_document,
    trim_to_current_letter,
)
from amazon_letters_tutor.models import ExtractedDocument


def test_normalize_pre_text_joins_wrapped_lines_but_keeps_paragraphs() -> None:
    raw = "This is a wrapped\nline in one paragraph.\n\nThis is another paragraph."

    text = normalize_pre_text(raw)

    assert text == "This is a wrapped line in one paragraph.\n\nThis is another paragraph."


def test_trim_to_current_letter_removes_reprinted_1997_appendix() -> None:
    raw = (
        "[Page 1]\n\n"
        "To our shareowners:\n\n"
        "We will discuss Type 1 decisions and Type 2 decisions.\n\n"
        "Jeffrey P. Bezos\n\n"
        "1997 LETTER TO SHAREHOLDERS\n\n"
        "To our shareholders:\n\n"
        "This reprinted appendix should not be indexed for 2015."
    )

    text = trim_to_current_letter(raw, 2015)

    assert "Type 1 decisions" in text
    assert "reprinted appendix" not in text


def test_trim_to_current_letter_removes_parenthetical_1997_appendix_marker() -> None:
    raw = (
        "To our shareholders, customers, and employees:\n\n"
        "The last 3.5 years have been exciting.\n\n"
        "Jeffrey P. Bezos\n\n"
        "(Reprinted from the 1997 Annual Report)\n\n"
        "Amazon.com passed many milestones in 1997."
    )

    text = trim_to_current_letter(raw, 1998)

    assert "The last 3.5 years" in text
    assert "Amazon.com passed many milestones in 1997" not in text


def test_trim_to_current_letter_keeps_original_1997_letter() -> None:
    raw = "To our shareholders:\n\nIt is Day 1.\n\n1997 LETTER TO SHAREHOLDERS"

    text = trim_to_current_letter(raw, 1997)

    assert "It is Day 1" in text
    assert "1997 LETTER TO SHAREHOLDERS" in text


def test_to_markdown_document_adds_citation_metadata() -> None:
    document = ExtractedDocument(
        doc_id="amz_2020_pdf",
        year=2020,
        author="Jeffrey P. Bezos",
        source_url="https://example.com/2020.pdf",
        source_type="pdf",
        letter_type="bezos_letter",
        local_file_path=Path("2020.pdf"),
        text="To our shareowners:",
    )

    text = to_markdown_document(document, "To our shareowners:")

    assert text.startswith("# 2020 Amazon Shareholder Letter")
    assert "Author: Jeffrey P. Bezos" in text
    assert "Source: https://example.com/2020.pdf" in text
