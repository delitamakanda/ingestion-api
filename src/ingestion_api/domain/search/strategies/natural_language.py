from ingestion_api.domain.search.schemas import SearchRequest, SearchResponse
from ingestion_api.domain.search.strategies.base import SearchStrategy
from ingestion_api.retrieval.vector import VectorRetriever


class NaturalLanguageSearchStrategy(SearchStrategy):

    def __init__(self, retriever: VectorRetriever):
        self.retriever = retriever

    async def search(self, request: SearchRequest) -> SearchResponse:
        results = await self.retriever.search(request)
        return SearchResponse(results=results, query=request.query, mode=request.mode, total=len(results))

