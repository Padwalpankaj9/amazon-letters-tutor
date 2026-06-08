from amazon_letters_tutor.models import SearchHit
from amazon_letters_tutor.retrieval import reciprocal_rank_fusion, rerank_hits


def make_hit(chunk_id: str, year: int = 1991) -> SearchHit:
    return SearchHit(
        chunk_id=chunk_id,
        year=year,
        author="Jeffrey P. Bezos",
        section_title="Full letter",
        source_url="https://example.com",
        score=0.0,
        text="text",
    )


def test_reciprocal_rank_fusion_promotes_hits_seen_in_multiple_lists() -> None:
    fused = reciprocal_rank_fusion(
        [
            [make_hit("a"), make_hit("shared"), make_hit("b")],
            [make_hit("shared"), make_hit("c")],
        ],
        top_k=2,
    )

    assert [hit.chunk_id for hit in fused] == ["shared", "a"]


def test_rerank_hits_uses_scores_without_loading_model() -> None:
    hits = [make_hit("low"), make_hit("high")]

    reranked = rerank_hits("query", hits, model_name="unused", top_k=2, scores=[0.1, 0.9])

    assert [hit.chunk_id for hit in reranked] == ["high", "low"]
    assert reranked[0].score == 0.9
