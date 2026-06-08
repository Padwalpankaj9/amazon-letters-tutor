from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from amazon_letters_tutor.config import ProjectConfig
from amazon_letters_tutor.storage import AmazonLettersStore


@dataclass(frozen=True)
class GoldenQuestion:
    id: str
    query: str
    expected_years: list[int]
    must_contain_terms: list[str]
    expect_no_hits: bool = False


@dataclass(frozen=True)
class EvalResult:
    id: str
    query: str
    passed: bool
    retrieved_years: list[int]
    retrieved_chunk_ids: list[str]
    notes: list[str]


def load_golden_questions(path: Path) -> list[GoldenQuestion]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [
        GoldenQuestion(
            id=item["id"],
            query=item["query"],
            expected_years=item.get("expected_years", []),
            must_contain_terms=item.get("must_contain_terms", []),
            expect_no_hits=item.get("expect_no_hits", False),
        )
        for item in data
    ]


def evaluate_question(
    store: AmazonLettersStore,
    question: GoldenQuestion,
    top_k: int = 5,
) -> EvalResult:
    hits = store.search(question.query, top_k=top_k)
    retrieved_years = [hit.year for hit in hits]
    retrieved_chunk_ids = [hit.chunk_id for hit in hits]
    notes: list[str] = []

    if question.expect_no_hits:
        if hits:
            notes.append("Expected no hits, but retrieval returned chunks.")
        return EvalResult(
            id=question.id,
            query=question.query,
            passed=not hits,
            retrieved_years=retrieved_years,
            retrieved_chunk_ids=retrieved_chunk_ids,
            notes=notes,
        )

    if question.expected_years and not set(question.expected_years).intersection(retrieved_years):
        notes.append(f"Expected one of years {question.expected_years}.")

    text_blob = "\n".join(hit.text.lower() for hit in hits)
    for term in question.must_contain_terms:
        if term.lower() not in text_blob:
            notes.append(f"Missing required term: {term}")

    return EvalResult(
        id=question.id,
        query=question.query,
        passed=not notes and bool(hits),
        retrieved_years=retrieved_years,
        retrieved_chunk_ids=retrieved_chunk_ids,
        notes=notes,
    )


def run_eval(
    config: ProjectConfig,
    store: AmazonLettersStore,
    golden_file: Path,
    top_k: int = 5,
) -> tuple[list[EvalResult], Path]:
    questions = load_golden_questions(golden_file)
    results = [evaluate_question(store, question, top_k=top_k) for question in questions]
    out_dir = config.data_dir / "evals"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"eval_{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}.json"
    out_path.write_text(
        json.dumps(
            [
                {
                    "id": result.id,
                    "query": result.query,
                    "passed": result.passed,
                    "retrieved_years": result.retrieved_years,
                    "retrieved_chunk_ids": result.retrieved_chunk_ids,
                    "notes": result.notes,
                }
                for result in results
            ],
            indent=2,
        ),
        encoding="utf-8",
    )
    return results, out_path
