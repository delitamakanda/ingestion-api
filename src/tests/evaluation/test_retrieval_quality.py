import pytest

from ingestion_api.core.config import settings
from tests.evaluation.dataset import load_dataset
from tests.evaluation.evaluator import RetrievalEvaluator


@pytest.mark.asyncio
@pytest.mark.skipif(
    not settings.openai_api_key.strip(),
    reason="Retrieval quality evaluation requires an OpenAI API key.",
)
async def test_retrieval_quality(search_router, db_session):
    evaluator = RetrievalEvaluator(search_router, db_session)

    results = []

    for case in load_dataset():
        result = await evaluator.evaluate(case)
        results.append(result)

    avg_term_hit = sum(result.term_hit_rate for result in results) / len(results)

    assert avg_term_hit >= 0.5, "Average term hit rate is below the expected threshold."
