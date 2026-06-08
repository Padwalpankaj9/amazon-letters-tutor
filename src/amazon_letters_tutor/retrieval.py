from __future__ import annotations

from amazon_letters_tutor.models import SearchHit


def reciprocal_rank_fusion(
    ranked_lists: list[list[SearchHit]],
    k: int = 60,
    top_k: int = 8,
) -> list[SearchHit]:
    scores: dict[str, float] = {}
    hits_by_id: dict[str, SearchHit] = {}
    for hits in ranked_lists:
        for rank, hit in enumerate(hits, start=1):
            scores[hit.chunk_id] = scores.get(hit.chunk_id, 0.0) + 1 / (k + rank)
            hits_by_id.setdefault(hit.chunk_id, hit)
    ranked_ids = sorted(scores, key=lambda chunk_id: scores[chunk_id], reverse=True)
    fused: list[SearchHit] = []
    for chunk_id in ranked_ids[:top_k]:
        hit = hits_by_id[chunk_id]
        fused.append(
            SearchHit(
                chunk_id=hit.chunk_id,
                year=hit.year,
                author=hit.author,
                section_title=hit.section_title,
                source_url=hit.source_url,
                score=scores[chunk_id],
                text=hit.text,
                page_start=hit.page_start,
                page_end=hit.page_end,
            )
        )
    return fused


def rerank_hits(
    query: str,
    hits: list[SearchHit],
    model_name: str,
    top_k: int,
    scores: list[float] | None = None,
) -> list[SearchHit]:
    if not hits:
        return []
    if scores is None:
        from sentence_transformers import CrossEncoder

        model = CrossEncoder(model_name)
        predicted = model.predict([(query, hit.text) for hit in hits])
        scores = [float(score) for score in predicted]
    reranked = sorted(zip(hits, scores, strict=True), key=lambda item: item[1], reverse=True)
    return [
        SearchHit(
            chunk_id=hit.chunk_id,
            year=hit.year,
            author=hit.author,
            section_title=hit.section_title,
            source_url=hit.source_url,
            score=float(score),
            text=hit.text,
            page_start=hit.page_start,
            page_end=hit.page_end,
        )
        for hit, score in reranked[:top_k]
    ]
