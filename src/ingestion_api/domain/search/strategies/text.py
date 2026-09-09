from ingestion_api.domain.search.schemas import SearchRequest, SearchResponse
from ingestion_api.domain.search.strategies.base import SearchStrategy
from ingestion_api.retrieval.lexical import LexicalRetriever
from sqlalchemy.ext.asyncio import AsyncSession

class TextSearchStrategy(SearchStrategy):

    def __init__(self, retriever: LexicalRetriever):
        self.retriever = retriever

    async def search(self, request: SearchRequest, session: AsyncSession) -> SearchResponse:
        results = await self.retriever.text_search(request, session)

        if not results:
            results = await self.retriever.fuzzy_text_search(request, session)
        return SearchResponse(results=results, query=request.query, mode=request.mode, total=len(results))

