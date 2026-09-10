from sqlalchemy.ext.asyncio import AsyncSession

from ingestion_api.domain.search.router import SearchRouter
from ingestion_api.domain.search.schemas import SearchRequest, SearchResponse

from tests.evaluation.metrics import (
precision_at_k,
recall_at_k,
reciprocal_rank,
term_hit_rate,
)

from tests.evaluation.models import EvaluationResult, EvaluationCase
class RetrievalEvaluator:

    def __init__(self, search_router: SearchRouter, session: AsyncSession):
        self.search_router = search_router
        self.session = session

    async def evaluate(self, evaluation_case: EvaluationCase) -> EvaluationResult:

        request = SearchRequest(
            query=evaluation_case.query,
            mode=evaluation_case.mode,
            countries=evaluation_case.countries,
            limit=20,
        )

        response = await self.search_router.search(request, session=self.session)

        chunk_ids = [chunk.chunk_id for chunk in response.results]

        texts = self._texts_for_evaluation(response)

        expected_chunk_ids = set(evaluation_case.chunks_ids)

        return EvaluationResult(
            case_id=evaluation_case.id,
            recall_at_5=recall_at_k(
                expected_ids=expected_chunk_ids,
                retrieved_ids=chunk_ids,
                k=5),
            recall_at_10=recall_at_k(
                expected_ids=expected_chunk_ids,
                retrieved_ids=chunk_ids,
                k=10),
            precision_at_5=precision_at_k(
                expected_ids=expected_chunk_ids,
                retrieved_ids=chunk_ids,
                k=5),
            reciprocal_rank=reciprocal_rank(
                expected_ids=expected_chunk_ids,
                retrieved_ids=chunk_ids),
            term_hit_rate=term_hit_rate(
                expected_terms=evaluation_case.terms,
                texts=texts,
                k=5
            ),
            retrieved_chunks_ids=chunk_ids
        )

    def _texts_for_evaluation(self, response: SearchResponse) -> list[str]:
        if response.results:
            return [chunk.text for chunk in response.results]

        if response.sources:
            return [source.excerpt for source in response.sources]

        return []