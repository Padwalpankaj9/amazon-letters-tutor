from __future__ import annotations

from collections.abc import Iterable

from amazon_letters_tutor.config import ProjectConfig
from amazon_letters_tutor.models import SearchHit
from amazon_letters_tutor.storage import AmazonLettersStore


def batched[T](items: list[T], batch_size: int) -> Iterable[list[T]]:
    for index in range(0, len(items), batch_size):
        yield items[index : index + batch_size]


class VectorIndex:
    def __init__(self, config: ProjectConfig, store: AmazonLettersStore) -> None:
        self.config = config
        self.store = store

    def _collection(self, reset: bool = False):
        import chromadb

        self.config.chroma_dir.mkdir(parents=True, exist_ok=True)
        client = chromadb.PersistentClient(path=str(self.config.chroma_dir))
        if reset:
            try:
                client.delete_collection(self.config.vector_collection)
            except Exception:
                pass
        return client.get_or_create_collection(
            name=self.config.vector_collection,
            metadata={"embedding_model": self.config.embedding_model},
            embedding_function=None,
        )

    def _model(self):
        from sentence_transformers import SentenceTransformer

        return SentenceTransformer(self.config.embedding_model)

    def build(self, batch_size: int = 32, limit: int | None = None, reset: bool = True) -> int:
        rows = self.store.child_chunks()
        if limit is not None:
            rows = rows[:limit]
        if not rows:
            return 0

        model = self._model()
        collection = self._collection(reset=reset)
        indexed = 0
        for batch in batched(rows, batch_size):
            documents = [row["text"] for row in batch]
            embeddings = model.encode(
                documents,
                batch_size=batch_size,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False,
            )
            collection.upsert(
                ids=[row["chunk_id"] for row in batch],
                documents=documents,
                embeddings=embeddings.tolist(),
                metadatas=[
                    {
                        "year": int(row["year"]),
                        "author": row["author"],
                        "section_title": row["section_title"],
                        "source_url": row["source_url"],
                        "letter_type": row["letter_type"],
                        "page_start": row["page_start"] or 0,
                        "page_end": row["page_end"] or 0,
                    }
                    for row in batch
                ],
            )
            indexed += len(batch)
        return indexed

    def search(self, query: str, top_k: int = 8, year: int | None = None) -> list[SearchHit]:
        model = self._model()
        collection = self._collection()
        query_embedding = model.encode(
            query,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        where = {"year": year} if year is not None else None
        result = collection.query(
            query_embeddings=[query_embedding.tolist()],
            where=where,
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )
        hits: list[SearchHit] = []
        ids = result.get("ids", [[]])[0]
        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]
        for chunk_id, text, metadata, distance in zip(
            ids, documents, metadatas, distances, strict=False
        ):
            hits.append(
                SearchHit(
                    chunk_id=chunk_id,
                    year=int(metadata["year"]),
                    author=metadata["author"],
                    section_title=metadata["section_title"],
                    source_url=metadata["source_url"],
                    score=float(distance),
                    text=text,
                    page_start=int(metadata["page_start"]) or None,
                    page_end=int(metadata["page_end"]) or None,
                )
            )
        return hits
