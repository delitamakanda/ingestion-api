from dataclasses import dataclass

from ingestion_api.domain.documents.schemas import SOURCE_WEIGHTS, SourceType
from ingestion_api.domain.search.schemas import SearchResult, RetrievalRequest
from ingestion_api.llm.schemas import SearchPlan

from sqlalchemy.ext.asyncio import AsyncSession
from ingestion_api.retrieval.cross_encoder_reranker import CrossEncoderReranker

def get_session(session: AsyncSession):
    return session

@dataclass
class RankedResult:
    result: SearchResult
    score: float

class HybridRetriever:
    def __init__(self, lexical_retriever, vector_retriever, rrf_k: int = 50, reranker: CrossEncoderReranker | None = None):
        self.lexical_retriever = lexical_retriever
        self.vector_retriever = vector_retriever
        self.rrf_k = rrf_k  # Reciprocal Rank Fusion parameter
        self.reranker = reranker

    async def search_plan(self, plan: SearchPlan, session: AsyncSession, *, limit: int = 10):
        requests = [
            RetrievalRequest(
                query=query,
                countries=plan.countries,
                start_date=plan.start_date,
                end_date=plan.end_date,
                limit=30,
            ) for query in plan.queries
        ]
        result_sets = []
        for request in requests:
            results = await self.search(request=request, session=session, limit=30)
            result_sets.append(results)

        candidates = self._merge_query_results(result_sets, limit=10)

        if self.reranker:
            return self.reranker.rerank(query=" ".join(plan.queries), results=candidates, top_k=limit)
        return candidates[:limit]

    async def search(self, request: RetrievalRequest, session: AsyncSession, limit: int = 10):
        lexical_results = await self.lexical_retriever.keyword_search( request, session)
        vector_results = await self.vector_retriever.search(request, session=session, limit=30)

        combined_results: dict[str, RankedResult] = {}

        self._merge(combined_results, lexical_results)
        self._merge(combined_results, vector_results)

        ranked = sorted(combined_results.values(), key=lambda x: x.score, reverse=True)
        # Add lexical results to the combined results
        results = []
        for item in ranked[:limit]:
            item.result.score = item.score
            results.append(item.result)
        return results


    def _merge(self, combined_results: dict[str, RankedResult], new_results: list[SearchResult]):
        for rank, result in enumerate(new_results, start=1):
            rrf_score = (1 / ( self.rrf_k + rank))
            existing = combined_results.get(result.chunk_id)
            if existing:
                existing.score += rrf_score
            else:
                combined_results[result.chunk_id] = RankedResult(result=result, score=rrf_score)


    def _merge_query_results(self, result_sets: list[list[SearchResult]], *, limit: int = 10):
        scores: dict[str, RankedResult] = {}
        for results in result_sets:
            for rank, result in enumerate(results, start=1):
                score = (1 / (self.rrf_k + rank))
                existing = scores.get(result.chunk_id)

                if existing:
                    existing.score += score
                else:
                    scores[result.chunk_id] = RankedResult(result=result, score=score)

        for item in scores.values():
            source_weight = self._source_weight(item.result)
            item.score *= source_weight
            item.result.score = item.score

        ranked = sorted(scores.values(), key=lambda x: x.score, reverse=True)

        return [
            item.result for item in ranked[:limit]
        ]

    def _source_weight(self, result: SearchResult) -> float:
        return SOURCE_WEIGHTS.get(
            result.source_type,
            SOURCE_WEIGHTS[SourceType.OTHER]
        )

