from __future__ import annotations

import uuid

import typer
from rich.console import Console
from rich.table import Table

from amazon_letters_tutor.chunking import chunk_all
from amazon_letters_tutor.config import default_config
from amazon_letters_tutor.evals import run_eval
from amazon_letters_tutor.extract import extract_all
from amazon_letters_tutor.ingest import discover_sources, download_sources
from amazon_letters_tutor.retrieval import reciprocal_rank_fusion, rerank_hits
from amazon_letters_tutor.storage import AmazonLettersStore
from amazon_letters_tutor.vector import VectorIndex

app = typer.Typer(help="Local Amazon letters retrieval tool.")
console = Console()


def get_store() -> tuple[AmazonLettersStore, object]:
    config = default_config()
    config.ensure_dirs()
    store = AmazonLettersStore(config.db_path)
    store.init_schema()
    return store, config


@app.command()
def init_db() -> None:
    """Create the local SQLite database and data folders."""
    store, config = get_store()
    store.init_schema()
    console.print(f"Initialized database: {config.db_path}")


@app.command()
def discover() -> None:
    """Discover official Amazon shareholder-letter sources."""
    store, config = get_store()
    sources = discover_sources(config, store)
    console.print(f"Discovered {len(sources)} official letter sources.")


@app.command()
def download(
    year_start: int | None = typer.Option(None),
    year_end: int | None = typer.Option(None),
) -> None:
    """Download discovered official sources into data/raw."""
    store, config = get_store()
    count = download_sources(config, store, year_start=year_start, year_end=year_end)
    console.print(f"Downloaded or verified {count} source files.")


@app.command()
def extract(year: int | None = typer.Option(None)) -> None:
    """Extract raw HTML/PDF files into clean text."""
    store, config = get_store()
    count = extract_all(config, store, year=year)
    console.print(f"Extracted {count} documents.")


@app.command()
def chunk(year: int | None = typer.Option(None)) -> None:
    """Create parent and child chunks, then index child chunks with SQLite FTS."""
    store, config = get_store()
    count = chunk_all(config, store, year=year)
    console.print(f"Stored {count} chunks.")


@app.command()
def ingest(
    year_start: int | None = typer.Option(None),
    year_end: int | None = typer.Option(None),
) -> None:
    """Run discover, download, extract, and chunk in one pass."""
    store, config = get_store()
    sources = discover_sources(config, store)
    downloaded = download_sources(config, store, year_start=year_start, year_end=year_end)
    extracted = extract_all(config, store)
    chunks = chunk_all(config, store)
    console.print(
        f"Discovered {len(sources)}, downloaded {downloaded}, extracted {extracted}, "
        f"stored {chunks} chunks."
    )


@app.command()
def manifest() -> None:
    """Show discovered and processed documents."""
    store, _ = get_store()
    table = Table("Year", "Author", "Type", "Raw", "Extracted", "URL")
    for row in store.list_documents():
        table.add_row(
            str(row["year"]),
            row["author"],
            row["source_type"],
            "yes" if row["local_file_path"] else "no",
            "yes" if row["extracted_file_path"] else "no",
            row["source_url"],
        )
    console.print(table)


@app.command()
def search(
    query: str,
    top: int = typer.Option(8, "--top", "-k"),
    year: int | None = typer.Option(None),
    show_text: bool = typer.Option(False, "--show-text"),
) -> None:
    """Search indexed Amazon chunks with SQLite FTS."""
    store, _ = get_store()
    hits = store.search(query, top_k=top, year=year)
    store.log_retrieval(str(uuid.uuid4()), query, "fts", [hit.chunk_id for hit in hits])
    for index, hit in enumerate(hits, start=1):
        console.print(f"\n[C{index}] {hit.citation}")
        console.print(f"score={hit.score:.4f} url={hit.source_url}")
        if show_text:
            console.print(hit.text)


@app.command()
def retrieve(
    query: str,
    top: int = typer.Option(8, "--top", "-k"),
    year: int | None = typer.Option(None),
) -> None:
    """Return citation-ready context for Codex to use while tutoring."""
    store, _ = get_store()
    hits = store.search(query, top_k=top, year=year)
    store.log_retrieval(str(uuid.uuid4()), query, "fts_context", [hit.chunk_id for hit in hits])
    for index, hit in enumerate(hits, start=1):
        console.print(f"\n[C{index}]")
        console.print(f"citation: {hit.citation}")
        console.print(f"url: {hit.source_url}")
        console.print("text:")
        console.print(hit.text)


@app.command("index-vector")
def index_vector(
    batch_size: int = typer.Option(32),
    limit: int | None = typer.Option(None, help="Index only the first N child chunks."),
    reset: bool = typer.Option(True, help="Delete and recreate the Chroma collection first."),
) -> None:
    """Build the local Chroma vector index from child chunks."""
    store, config = get_store()
    count = VectorIndex(config, store).build(batch_size=batch_size, limit=limit, reset=reset)
    console.print(
        f"Indexed {count} child chunks into {config.chroma_dir} "
        f"using {config.embedding_model}."
    )


@app.command("vector-search")
def vector_search(
    query: str,
    top: int = typer.Option(8, "--top", "-k"),
    year: int | None = typer.Option(None),
) -> None:
    """Semantic search over the Chroma vector index."""
    store, config = get_store()
    hits = VectorIndex(config, store).search(query, top_k=top, year=year)
    for index, hit in enumerate(hits, start=1):
        console.print(f"\n[V{index}] {hit.citation}")
        console.print(f"distance={hit.score:.4f} url={hit.source_url}")
        console.print(hit.text)


@app.command("hybrid-search")
def hybrid_search(
    query: str,
    top: int = typer.Option(8, "--top", "-k"),
    candidate_top: int = typer.Option(20),
    year: int | None = typer.Option(None),
    include_parent: bool = typer.Option(False, help="Include full parent chunk text."),
    max_words_per_chunk: int = typer.Option(450),
    rerank: bool = typer.Option(False, help="Rerank fused candidates with a cross-encoder."),
    rerank_top: int = typer.Option(30, help="Number of fused candidates to rerank."),
) -> None:
    """Combine keyword and vector search using reciprocal rank fusion."""
    store, config = get_store()
    keyword_hits = store.search(query, top_k=candidate_top, year=year)
    vector_hits = VectorIndex(config, store).search(query, top_k=candidate_top, year=year)
    fused_top = max(top, rerank_top) if rerank else top
    hits = reciprocal_rank_fusion([keyword_hits, vector_hits], top_k=fused_top)
    mode = "hybrid_rrf"
    if rerank:
        hits = rerank_hits(query, hits, model_name=config.reranker_model, top_k=top)
        mode = "hybrid_rrf_rerank"
    store.log_retrieval(str(uuid.uuid4()), query, mode, [hit.chunk_id for hit in hits])
    for index, hit in enumerate(hits, start=1):
        block = store.expand_hit(
            hit,
            rank=index,
            include_parent=include_parent,
            max_words_per_chunk=max_words_per_chunk,
        )
        console.print(f"\n[H{index}] {block.citation}", markup=False)
        console.print(f"rrf_score={hit.score:.4f} url={hit.source_url}", markup=False)
        console.print(f"expanded_chunks={', '.join(block.expanded_chunk_ids)}", markup=False)
        console.print(block.text, markup=False)


@app.command()
def inspect(chunk_id: str) -> None:
    """Inspect one stored chunk by ID."""
    store, _ = get_store()
    row = store.inspect_chunk(chunk_id)
    if row is None:
        raise typer.BadParameter(f"Unknown chunk: {chunk_id}")
    console.print(dict(row))


@app.command("eval")
def eval_command(
    golden_file: str = typer.Option("evals/golden_questions.json"),
    top: int = typer.Option(5, "--top", "-k"),
) -> None:
    """Run golden retrieval checks and save a JSON report."""
    store, config = get_store()
    results, out_path = run_eval(config, store, config.project_root / golden_file, top_k=top)
    table = Table("ID", "Pass", "Years", "Notes")
    for result in results:
        table.add_row(
            result.id,
            "yes" if result.passed else "no",
            ", ".join(str(year) for year in result.retrieved_years[:top]),
            "; ".join(result.notes),
        )
    console.print(table)
    passed = sum(1 for result in results if result.passed)
    console.print(f"{passed}/{len(results)} checks passed. Report: {out_path}")
