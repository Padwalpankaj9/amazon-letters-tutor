from __future__ import annotations

import re
from pathlib import Path

import fitz
from bs4 import BeautifulSoup

from amazon_letters_tutor.config import ProjectConfig
from amazon_letters_tutor.models import ExtractedDocument
from amazon_letters_tutor.storage import AmazonLettersStore
from amazon_letters_tutor.text_utils import normalize_whitespace, sha256_text

APPENDIX_MARKERS = [
    "1997 LETTER TO SHAREHOLDERS",
    "1997 LETTER TO SHAREOWNERS",
    "(Reprinted from the 1997 Annual Report)",
]
FORM_10K_MARKERS = [
    "UNITED STATES SECURITIES AND EXCHANGE COMMISSION",
    "FORM 10-K",
]
LETTER_START_RE = re.compile(
    r"\bTo our (?:shareholders|shareowners)(?:, customers, and employees)?:",
    re.IGNORECASE,
)


def normalize_pre_text(text: str) -> str:
    paragraphs: list[str] = []
    current: list[str] = []
    for raw_line in text.replace("\r", "\n").split("\n"):
        line = raw_line.strip()
        if not line:
            if current:
                paragraphs.append(" ".join(current))
                current = []
            continue
        current.append(line)
    if current:
        paragraphs.append(" ".join(current))
    return "\n\n".join(paragraphs)


def extract_html(path: Path) -> str:
    soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="ignore"), "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    pre = soup.find("pre")
    if pre is not None:
        return normalize_pre_text(pre.get_text("\n"))
    body = soup.body or soup
    blocks = [block.get_text(" ", strip=True) for block in body.find_all(["p", "div", "td", "li"])]
    text = "\n\n".join(block for block in blocks if block)
    return normalize_whitespace(text or body.get_text("\n", strip=True))


def extract_pdf(path: Path) -> str:
    pages = []
    with fitz.open(path) as doc:
        for index, page in enumerate(doc, start=1):
            text = normalize_whitespace(page.get_text("text"))
            if text:
                pages.append(f"[Page {index}]\n\n{text}")
    return "\n\n".join(pages)


def trim_to_current_letter(text: str, year: int) -> str:
    trimmed = text
    if year != 1997:
        appendix_indexes = [
            trimmed.find(marker) for marker in APPENDIX_MARKERS if trimmed.find(marker) >= 0
        ]
        if appendix_indexes:
            trimmed = trimmed[: min(appendix_indexes)]

    form_indexes = [
        trimmed.find(marker) for marker in FORM_10K_MARKERS if trimmed.find(marker) >= 0
    ]
    if form_indexes:
        trimmed = trimmed[: min(form_indexes)]

    start_match = LETTER_START_RE.search(trimmed)
    if start_match:
        page_marker_start = trimmed.rfind("[Page ", 0, start_match.start())
        start_index = page_marker_start if page_marker_start >= 0 else start_match.start()
        trimmed = trimmed[start_index:]

    return trimmed.strip()


def to_markdown_document(document: ExtractedDocument, text: str) -> str:
    return "\n\n".join(
        [
            f"# {document.year} Amazon Shareholder Letter",
            f"Author: {document.author}",
            f"Source: {document.source_url}",
            text.strip(),
        ]
    )


def extract_document(
    config: ProjectConfig,
    store: AmazonLettersStore,
    doc_id: str,
) -> ExtractedDocument:
    row = store.get_document(doc_id)
    if row is None:
        raise ValueError(f"Unknown document: {doc_id}")
    if not row["local_file_path"]:
        raise ValueError(f"Document has not been downloaded: {doc_id}")
    local_file_path = Path(row["local_file_path"])
    if row["source_type"] == "pdf":
        text = extract_pdf(local_file_path)
    else:
        text = extract_html(local_file_path)
    text = trim_to_current_letter(text, int(row["year"]))
    extracted = ExtractedDocument(
        doc_id=row["doc_id"],
        year=row["year"],
        author=row["author"],
        source_url=row["source_url"],
        source_type=row["source_type"],
        letter_type=row["letter_type"],
        local_file_path=local_file_path,
        text=text,
    )
    text = to_markdown_document(extracted, text)
    out_path = config.extracted_dir / f"{row['year']}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")
    store.update_extracted_file(doc_id, out_path, sha256_text(text))
    return ExtractedDocument(**{**extracted.__dict__, "text": text})


def extract_all(config: ProjectConfig, store: AmazonLettersStore, year: int | None = None) -> int:
    count = 0
    rows = [store.get_document_by_year(year)] if year is not None else store.downloaded_documents()
    for row in rows:
        if row is None:
            continue
        extract_document(config, store, row["doc_id"])
        count += 1
    return count
