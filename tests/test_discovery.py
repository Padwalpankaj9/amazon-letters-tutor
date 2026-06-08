from amazon_letters_tutor.ingest import curated_bezos_sources, discover_from_html


def test_discover_from_html_keeps_official_amazon_links() -> None:
    letter_2018 = (
        "https://s2.q4cdn.com/299287126/files/doc_financials/annual/"
        "2018-Letter-to-Shareholders.pdf"
    )
    letter_2020 = (
        "https://s2.q4cdn.com/299287126/files/doc_financials/2021/ar/"
        "Amazon-2020-Shareholder-Letter-and-1997-Shareholder-Letter.pdf"
    )
    html = f"""
    <a href="{letter_2018}">2018 Letter</a>
    <a href="{letter_2020}">2020 Letter</a>
    <a href="../reports/2024ar.pdf">Annual report</a>
    """

    sources = discover_from_html(
        html,
        "https://ir.aboutamazon.com/annual-reports-proxies-and-shareholder-letters/default.aspx",
    )

    assert [source.year for source in sources] == [2018, 2020]
    assert sources[0].source_type == "pdf"
    assert sources[1].source_type == "pdf"
    assert sources[1].author == "Jeffrey P. Bezos"


def test_curated_bezos_sources_cover_1997_through_2020() -> None:
    sources = curated_bezos_sources()

    assert [source.year for source in sources] == list(range(1997, 2021))
    assert all(source.author == "Jeffrey P. Bezos" for source in sources)
    assert all(source.source_type == "pdf" for source in sources)
