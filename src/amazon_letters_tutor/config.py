from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT_ENV = "AMAZON_LETTERS_TUTOR_ROOT"
OFFICIAL_LETTERS_URL = (
    "https://ir.aboutamazon.com/annual-reports-proxies-and-shareholder-letters/default.aspx"
)


def default_project_root() -> Path:
    configured = os.environ.get(PROJECT_ROOT_ENV)
    return Path(configured).expanduser().resolve() if configured else Path.cwd().resolve()


@dataclass(frozen=True)
class ProjectConfig:
    project_root: Path = field(default_factory=default_project_root)
    official_letters_url: str = OFFICIAL_LETTERS_URL
    parent_target_words: int = 1500
    child_target_words: int = 380
    child_overlap_words: int = 75
    embedding_model: str = "BAAI/bge-base-en-v1.5"
    vector_collection: str = "amz_letters_bge_base_v1_5_child_v1"
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L6-v2"

    @property
    def data_dir(self) -> Path:
        return self.project_root / "data"

    @property
    def raw_dir(self) -> Path:
        return self.data_dir / "raw"

    @property
    def extracted_dir(self) -> Path:
        return self.data_dir / "extracted"

    @property
    def db_path(self) -> Path:
        return self.data_dir / "db" / "amazon_letters.sqlite"

    @property
    def chroma_dir(self) -> Path:
        return self.data_dir / "indexes" / "chroma"

    def ensure_dirs(self) -> None:
        for path in (self.raw_dir, self.extracted_dir, self.db_path.parent):
            path.mkdir(parents=True, exist_ok=True)


def default_config() -> ProjectConfig:
    return ProjectConfig()
