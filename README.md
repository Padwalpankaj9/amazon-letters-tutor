# Amazon Letters Tutor

A local-first retrieval and study system for Jeff Bezos's Amazon shareholder letters.

The project has two parts:

- `amz`, a Python CLI that discovers official Amazon-hosted letters, downloads them locally, extracts Markdown, chunks the text, and builds keyword or semantic search indexes.
- `analysis/`, a static concept explorer and deep-dive reader UI for studying recurring Bezos ideas such as Day 1, customer obsession, high standards, decision speed, free cash flow, and platform design.

## Corpus and Attribution

This repository includes extracted Markdown copies of Jeff Bezos's Amazon shareholder letters from 1997 through 2020 under `data/extracted/`.

The source letter text is credited to Amazon.com, Inc. and Jeffrey P. Bezos. The official Amazon-hosted PDF URLs are listed in `data/SOURCES.md`, and each extracted Markdown file includes its author and source URL in the header.

The repository does not commit raw PDF files, SQLite databases, Chroma indexes, or local evaluation output. Those files are generated locally under `data/`.

## Quick Start

Install dependencies:

```bash
uv sync
```

Build or refresh the local SQLite search index:

```bash
uv run --no-editable amz init-db
uv run --no-editable amz ingest --year-start 1997 --year-end 2020
uv run --no-editable amz retrieve "type 1 decisions" --top 5
```

Run retrieval checks:

```bash
uv run --no-editable amz eval
```

Build and query the optional semantic index:

```bash
uv run --no-editable amz index-vector
uv run --no-editable amz vector-search "why Amazon accepts short term accounting pain" --top 5
uv run --no-editable amz hybrid-search "why high standards matter" --top 5
uv run --no-editable amz hybrid-search "why high standards matter" --top 5 --rerank
```

For a smaller smoke test:

```bash
uv run --no-editable amz discover
uv run --no-editable amz download --year-start 2016 --year-end 2016
uv run --no-editable amz extract --year 2016
uv run --no-editable amz chunk --year 2016
uv run --no-editable amz retrieve "disagree and commit" --top 5
```

## Static Concept Explorer

The static study UI lives in `analysis/`.

Serve the project root:

```bash
python3 -m http.server 8765
```

Then open:

```text
http://127.0.0.1:8765/analysis/bezos_concepts_explorer.html
```

The deep-dive reader pages fetch local files from `data/extracted/*.md`, so the "Read In Letter" context pane works from the committed extracted corpus.

Regenerate the concept deep-dive pages from the shared template:

```bash
python3 analysis/scripts/generate_deep_dive_pages.py
```

## Project Root

By default, `amz` writes generated data into `./data` under your current working directory. To pin the project root explicitly:

```bash
export AMAZON_LETTERS_TUTOR_ROOT=/path/to/amazon_letters_tutor
```

## Design Choices

- SQLite is the canonical database.
- Raw PDF files are preserved locally under `data/raw`.
- Extracted Markdown is preserved locally under `data/extracted`.
- Parent chunks preserve broader context.
- Child chunks are indexed for precise retrieval.
- SQLite FTS is the v1 search engine.
- Chroma plus BGE embeddings provide optional semantic search.
- Optional cross-encoder reranking can be enabled with `--rerank`.
- The curated v1 source manifest covers Bezos-authored shareholder letters from 1997 through 2020, his last annual shareholder letter as Amazon CEO.
- Later Amazon letters are Andy Jassy letters and are intentionally excluded from the Bezos corpus for now.
- Many Amazon PDFs append the original 1997 letter. Extraction trims that appendix for non-1997 years so retrieval is not dominated by duplicate text.

## Development

Run tests and lint:

```bash
uv run --no-editable pytest -q
uv run --no-editable ruff check src tests
```

## License

MIT. See `LICENSE`.

The MIT License applies to the software, tests, templates, and original analysis code. It does not claim ownership of Amazon's original shareholder letter text or any Amazon trademarks. See `NOTICE` and `data/SOURCES.md`.
