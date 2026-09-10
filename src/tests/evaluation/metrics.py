def recall_at_k(
        *,
        expected_ids: set[str],
        retrieved_ids: list[str],
        k: int,
) -> float:
    if not expected_ids:
        return 0.0

    retrieved = set(retrieved_ids[:k])

    relevant = (expected_ids & retrieved)

    return len(relevant) / len(expected_ids)

def precision_at_k(
        *,
        expected_ids: set[str],
        retrieved_ids: list[str],
        k: int,
) -> float:
    if k == 0:
        return 0.0


    retrieved = set(retrieved_ids[:k])

    if not retrieved:
        return 0.0

    relevant = sum(1 for id in retrieved if id in expected_ids)

    return relevant / len(retrieved)

def reciprocal_rank(
        *,
        expected_ids: set[str],
        retrieved_ids: list[str],
) -> float:
    for rank, id in enumerate(retrieved_ids, start=1):
        if id in expected_ids:
            return 1.0 / rank
    return 0.0

def term_hit_rate(
        *,
        expected_terms: list[str],
        texts: list[str],
        k: int
) -> float:
    if not expected_terms:
        return 0.0

    corpus = "".join(texts[:k]).lower()

    hits = sum(1 for term in expected_terms if term.lower() in corpus)

    return hits / len(expected_terms)