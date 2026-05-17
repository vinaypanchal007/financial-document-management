from sentence_transformers import CrossEncoder

_reranker = None


def _get_reranker():
    global _reranker
    if _reranker is None:
        _reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    return _reranker


def rerank_results(query: str, documents: list, top_k: int = 5):
    """
    Takes a query and list of document chunks,
    scores each with the cross-encoder,
    returns top_k most relevant sorted by score.
    """

    if not documents:
        return []

    reranker = _get_reranker()
    pairs = [[query, doc] for doc in documents]
    scores = reranker.predict(pairs)
    scored = sorted(
        zip(documents, scores),
        key=lambda x: x[1],
        reverse=True
    )

    return [
        {
            "chunk": doc,
            "score": float(score)
        }
        for doc, score in scored[:top_k]
    ]
