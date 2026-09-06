from ingestion_api.domain.search.schemas import SearchRequest, SearchResponse
from ingestion_api.domain.search.strategies.base import SearchStrategy
from ingestion_api.retrieval.hybrid import HybridRetriever


class NaturalLanguageSearchStrategy(SearchStrategy):

    def __init__(self, hybrid_retriever: HybridRetriever):
        self.hybrid_retriever = hybrid_retriever

    async def search(self, request: SearchRequest) -> SearchResponse:
        results = await self.hybrid_retriever.search(request, limit=request.limit)
        return SearchResponse(results=results, query=request.query, mode=request.mode, total=len(results))

