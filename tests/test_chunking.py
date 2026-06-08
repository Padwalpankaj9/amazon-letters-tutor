from pathlib import Path

from amazon_letters_tutor.chunking import build_chunks_for_document
from amazon_letters_tutor.config import ProjectConfig


def test_build_chunks_creates_parent_and_child_chunks(tmp_path: Path) -> None:
    text_path = tmp_path / "2016.md"
    text_path.write_text(
        "Disagree and Commit\n\n"
        + " ".join(["Disagree and commit helps teams move quickly."] * 160)
        + "\n\nTwo-Way Doors\n\n"
        + " ".join(["Many decisions are reversible two-way doors."] * 80),
        encoding="utf-8",
    )
    config = ProjectConfig(project_root=tmp_path, parent_target_words=300, child_target_words=90)

    chunks = build_chunks_for_document(
        config,
        doc_id="amz_2016_pdf",
        year=2016,
        author="Jeffrey P. Bezos",
        source_url="https://s2.q4cdn.com/299287126/files/doc_financials/annual/2016-Letter-to-Shareholders.pdf",
        source_type="pdf",
        letter_type="bezos_letter",
        extracted_file_path=text_path,
    )

    parent_chunks = [chunk for chunk in chunks if chunk.chunk_kind == "parent"]
    child_chunks = [chunk for chunk in chunks if chunk.chunk_kind == "child"]
    assert parent_chunks
    assert child_chunks
    assert all(chunk.parent_chunk_id for chunk in child_chunks)
    assert all(chunk.year == 2016 for chunk in chunks)
    assert child_chunks[0].next_chunk_id == child_chunks[1].chunk_id


def test_child_chunk_ids_are_deterministic(tmp_path: Path) -> None:
    text_path = tmp_path / "2017.md"
    text_path.write_text("High Standards\n\n" + "alpha beta gamma " * 60, encoding="utf-8")
    config = ProjectConfig(project_root=tmp_path, child_target_words=50)
    kwargs = dict(
        config=config,
        doc_id="amz_2017_pdf",
        year=2017,
        author="Jeffrey P. Bezos",
        source_url="https://s2.q4cdn.com/299287126/files/doc_financials/annual/Amazon_Shareholder_Letter.pdf",
        source_type="pdf",
        letter_type="bezos_letter",
        extracted_file_path=text_path,
    )

    first = build_chunks_for_document(**kwargs)
    second = build_chunks_for_document(**kwargs)

    assert [chunk.chunk_id for chunk in first] == [chunk.chunk_id for chunk in second]
