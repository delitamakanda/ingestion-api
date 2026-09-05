from ingestion_api.domain.search.schemas import SearchRequest, SearchResponse
from ingestion_api.domain.search.strategies.base import SearchStrategy
from ingestion_api.retrieval.lexical import LexicalRetriever

class TextSearchStrategy(SearchStrategy):

    def __init__(self, retriever: LexicalRetriever):
        self.retriever = retriever

    async def search(self, request: SearchRequest) -> SearchResponse:
        results = await self.retriever.text_search(request)

        if not results:
            results = await self.retriever.fuzzy_text_search(request)
        return SearchResponse(results=results, query=request.query, mode=request.mode, total=len(results))

