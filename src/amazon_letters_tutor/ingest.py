from __future__ import annotations

from pathlib import Path
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from amazon_letters_tutor.config import ProjectConfig
from amazon_letters_tutor.models import SourceRecord
from amazon_letters_tutor.storage import AmazonLettersStore
from amazon_letters_tutor.text_utils import infer_year, sha256_bytes

AMAZON_SOURCE_URLS: dict[int, str] = {
    1997: "https://s2.q4cdn.com/299287126/files/doc_financials/annual/Shareholderletter97.pdf",
    1998: "https://s2.q4cdn.com/299287126/files/doc_financials/annual/Shareholderletter98.pdf",
    1999: "https://s2.q4cdn.com/299287126/files/doc_financials/annual/Shareholderletter99.pdf",
    2000: "https://s2.q4cdn.com/299287126/files/doc_financials/annual/00ar_letter.pdf",
    2001: "https://s2.q4cdn.com/299287126/files/doc_financials/annual/2001_shareholderLetter.pdf",
    2002: "https://s2.q4cdn.com/299287126/files/doc_financials/annual/2002_shareholderLetter.pdf",
    2003: "https://s2.q4cdn.com/299287126/files/doc_financials/annual/Annual_Report_2003041304.pdf",
    2004: "https://s2.q4cdn.com/299287126/files/doc_financials/annual/2004_Annual_report.pdf",
    2005: "https://s2.q4cdn.com/299287126/files/doc_financials/annual/AMZN2005AnnualReport.pdf",
    2006: "https://s2.q4cdn.com/299287126/files/doc_financials/annual/2006AnnualReport.pdf",
    2007: "https://s2.q4cdn.com/299287126/files/doc_financials/annual/2007AR.pdf",
    2008: "https://s2.q4cdn.com/299287126/files/doc_financials/annual/Amazon_Annual_Report_2008.pdf",
    2009: (
        "https://s2.q4cdn.com/299287126/files/doc_financials/annual/"
        "AMZN_Annual-Report-2009-(final).pdf"
    ),
    2010: "https://s2.q4cdn.com/299287126/files/doc_financials/annual/117006_099_bmk_AR.pdf",
    2011: "https://s2.q4cdn.com/299287126/files/doc_financials/annual/269317_023_bmk.pdf",
    2012: "https://s2.q4cdn.com/299287126/files/doc_financials/annual/2012-Shareholder-Letter.pdf",
    2013: "https://s2.q4cdn.com/299287126/files/doc_financials/annual/2013-Letter-to-Shareholders.pdf",
    2014: "https://s2.q4cdn.com/299287126/files/doc_financials/annual/AMAZON-2014-Shareholder-Letter.pdf",
    2015: "https://s2.q4cdn.com/299287126/files/doc_financials/annual/2015-Letter-to-Shareholders.PDF",
    2016: "https://s2.q4cdn.com/299287126/files/doc_financials/annual/2016-Letter-to-Shareholders.pdf",
    2017: "https://s2.q4cdn.com/299287126/files/doc_financials/annual/Amazon_Shareholder_Letter.pdf",
    2018: "https://s2.q4cdn.com/299287126/files/doc_financials/annual/2018-Letter-to-Shareholders.pdf",
    2019: "https://s2.q4cdn.com/299287126/files/doc_financials/2020/ar/2019-Shareholder-Letter.pdf",
    2020: (
        "https://s2.q4cdn.com/299287126/files/doc_financials/2021/ar/"
        "Amazon-2020-Shareholder-Letter-and-1997-Shareholder-Letter.pdf"
    ),
}


def author_for_year(year: int) -> str:
    return "Andrew R. Jassy" if year >= 2021 else "Jeffrey P. Bezos"


def letter_type_for_year(year: int) -> str:
    return "jassy_letter" if year >= 2021 else "bezos_letter"


def source_type_from_url(url: str) -> str:
    if url.lower().endswith(".pdf"):
        return "pdf"
    return "html"


def discover_from_html(index_html: str, base_url: str) -> list[SourceRecord]:
    soup = BeautifulSoup(index_html, "html.parser")
    sources: dict[int, SourceRecord] = {}
    for link in soup.find_all("a", href=True):
        href = str(link["href"])
        label = link.get_text(" ", strip=True)
        url = urljoin(base_url, href)
        year = infer_year(label, href, url)
        if year is None:
            continue
        if not 1997 <= year <= 2020:
            continue
        if not (url.endswith(".html") or url.endswith(".pdf")):
            continue
        if "q4cdn.com/299287126/" not in url and "aboutamazon.com" not in url:
            continue
        source_type = source_type_from_url(url)
        author = author_for_year(year)
        doc_id = f"amz_{year}_{source_type}"
        sources[year] = SourceRecord(
            doc_id=doc_id,
            year=year,
            title=f"{year} Amazon shareholder letter",
            author=author,
            source_url=url,
            source_type=source_type,
            letter_type=letter_type_for_year(year),
        )
    return [sources[year] for year in sorted(sources)]


def curated_bezos_sources() -> list[SourceRecord]:
    sources = []
    for year, url in AMAZON_SOURCE_URLS.items():
        source_type = source_type_from_url(url)
        sources.append(
            SourceRecord(
                doc_id=f"amz_{year}_{source_type}",
                year=year,
                title=f"{year} Amazon shareholder letter",
                author=author_for_year(year),
                source_url=url,
                source_type=source_type,
                letter_type=letter_type_for_year(year),
            )
        )
    return sources


def discover_sources(config: ProjectConfig, store: AmazonLettersStore) -> list[SourceRecord]:
    # Amazon's IR page is Cloudflare-protected for plain scripts, so keep a curated
    # official-source manifest and merge any reachable IR links later if available.
    sources_by_year = {source.year: source for source in curated_bezos_sources()}
    try:
        response = httpx.get(config.official_letters_url, follow_redirects=True, timeout=30)
        response.raise_for_status()
    except httpx.HTTPError:
        pass
    else:
        for source in discover_from_html(response.text, config.official_letters_url):
            if 1997 <= source.year <= 2020:
                sources_by_year[source.year] = source
    sources = [sources_by_year[year] for year in sorted(sources_by_year)]
    store.upsert_sources(sources)
    return sources


def raw_path_for_source(config: ProjectConfig, source: SourceRecord) -> Path:
    suffix = ".pdf" if source.source_type == "pdf" else ".html"
    return config.raw_dir / f"{source.year}{suffix}"


def download_sources(
    config: ProjectConfig,
    store: AmazonLettersStore,
    year_start: int | None = None,
    year_end: int | None = None,
) -> int:
    config.ensure_dirs()
    downloaded = 0
    for row in store.list_documents():
        year = int(row["year"])
        if year_start is not None and year < year_start:
            continue
        if year_end is not None and year > year_end:
            continue
        source = SourceRecord(
            doc_id=row["doc_id"],
            year=year,
            title=row["title"],
            author=row["author"],
            source_url=row["source_url"],
            source_type=row["source_type"],
            letter_type=row["letter_type"],
        )
        path = raw_path_for_source(config, source)
        if path.exists():
            data = path.read_bytes()
        else:
            response = httpx.get(source.source_url, follow_redirects=True, timeout=60)
            response.raise_for_status()
            data = response.content
            path.write_bytes(data)
        store.update_raw_file(source.doc_id, path, sha256_bytes(data))
        downloaded += 1
    return downloaded
