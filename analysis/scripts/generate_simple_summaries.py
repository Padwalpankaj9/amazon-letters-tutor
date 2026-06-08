#!/usr/bin/env python3
"""Generate simple learning summaries for the Bezos deep-dive cards."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
GENERATOR_PATH = Path(__file__).resolve().parent / "generate_deep_dive_pages.py"
OUTPUT_PATH = Path(__file__).resolve().parent / "simple_summaries.json"
MODEL = "gemini-3.1-pro-preview"
BATCH_SIZE = 10


def load_generator() -> Any:
    spec = importlib.util.spec_from_file_location("deep_dive_generator", GENERATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {GENERATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def clean_text(text: str) -> str:
    text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\[Page \d+\]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_excerpt(source: str, line_ranges: list[list[int]]) -> str:
    path = (ROOT / source.replace("../", "")).resolve()
    lines = path.read_text(encoding="utf-8").splitlines()
    chunks = []
    for start, end in line_ranges:
        chunks.append("\n".join(lines[start - 1 : end]))
    return clean_text("\n\n".join(chunks))


def summary_key(year: int, title: str, line_ranges: list[list[int]]) -> str:
    ranges = ",".join(f"{start}-{end}" for start, end in line_ranges)
    return f"{year}|{ranges}|{title}"


def collect_items() -> list[dict[str, Any]]:
    generator = load_generator()
    items = []
    for idea in generator.IDEAS:
        for card in idea["cards"]:
            items.append(
                {
                    "key": summary_key(card["year"], card["title"], card["lineRanges"]),
                    "idea": idea["title"],
                    "year": card["year"],
                    "title": card["title"],
                    "quote": card["quote"],
                    "current_why": card["why"],
                    "current_support": card["support"],
                    "current_takeaway": card["takeaway"],
                    "source_excerpt": extract_excerpt(card["source"], card["lineRanges"]),
                }
            )
    return items


def parse_json(output: str) -> dict[str, Any]:
    output = output.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", output, flags=re.DOTALL)
    if fenced:
        output = fenced.group(1)
    else:
        start = output.find("{")
        end = output.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("Gemini output did not contain a JSON object")
        output = output[start : end + 1]
    return json.loads(output)


def call_gemini(items: list[dict[str, Any]]) -> dict[str, Any]:
    instructions = """
You are writing learning summaries for a personal study tool about Jeff Bezos'
Amazon shareholder letters.

Rewrite each card in very simple English for an adult beginner reading at about
a 10- to 15-year-old level.
Use short sentences. Use concrete language. Do not sound childish.
Do not copy the source excerpt. Do not add facts that are not supported by the excerpt or notes.

Return one JSON object only.
Each key must be the input key.
Each value must have exactly these string fields:
- summary: 2 to 4 short sentences explaining the idea.
- why_it_matters: 1 or 2 short sentences explaining why the idea matters in life or business.
- try_this: 1 short sentence that turns the idea into a practical question or action.
""".strip()
    payload = json.dumps({"items": items}, ensure_ascii=False)
    result = subprocess.run(
        ["gemini", "--no-sandbox", "--model", MODEL, "--prompt", instructions],
        input=payload,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        raise SystemExit(result.returncode)
    return parse_json(result.stdout)


def summary_entries(data: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in data.items() if not key.startswith("_")}


def load_existing() -> dict[str, Any]:
    if not OUTPUT_PATH.exists():
        return {}
    return summary_entries(json.loads(OUTPUT_PATH.read_text(encoding="utf-8")))


def write_output(data: dict[str, Any], item_count: int) -> None:
    output = {
        "_meta": {
            "model": MODEL,
            "purpose": "Plain-language learning summaries for generated Bezos letter reader pages.",
            "item_count": item_count,
            "generated_count": len(data),
        },
        **dict(sorted(data.items())),
    }
    OUTPUT_PATH.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def validate(data: dict[str, Any], items: list[dict[str, Any]]) -> None:
    expected = {item["key"] for item in items}
    actual = set(data)
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing or extra:
        raise ValueError(f"Summary key mismatch. Missing={len(missing)} Extra={len(extra)}")
    for key in expected:
        value = data[key]
        for field in ("summary", "why_it_matters", "try_this"):
            if not isinstance(value.get(field), str) or not value[field].strip():
                raise ValueError(f"{key} is missing {field}")


def main() -> None:
    items = collect_items()
    data = load_existing()
    pending = [item for item in items if item["key"] not in data]
    for index in range(0, len(pending), BATCH_SIZE):
        batch = pending[index : index + BATCH_SIZE]
        start = index + 1
        end = index + len(batch)
        print(f"Generating summaries {start}-{end} of {len(pending)} pending...")
        data.update(call_gemini(batch))
        write_output(data, len(items))
    validate(data, items)
    write_output(data, len(items))
    print(f"Wrote {len(items)} summaries to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
