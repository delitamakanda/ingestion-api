from ingestion_api.domain.search.enums import SearchMode
from ingestion_api.domain.search.schemas import SearchRequest, SearchResponse
from ingestion_api.domain.search.strategies.base import SearchStrategy


class SearchRouter:

    def __init__(self, keyword_strategy: SearchStrategy, text_strategy: SearchStrategy, natural_language_strategy: SearchStrategy):
        self.strategies: dict[SearchMode, SearchStrategy] = {
            SearchMode.KEYWORD: keyword_strategy,
            SearchMode.TEXT: text_strategy,
            SearchMode.NATURAL_LANGUAGE: natural_language_strategy
        }

    async def search(self, request: SearchRequest) -> SearchResponse:
        strategy = self.strategies.get(request.mode)
        if not strategy:
            raise NotImplementedError(f"Search mode {request.mode} not implemented")
        return await strategy.search(request)
