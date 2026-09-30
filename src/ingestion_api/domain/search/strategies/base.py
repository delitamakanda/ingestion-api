from abc import ABC, abstractmethod

from ingestion_api.domain.search.schemas import SearchRequest, SearchResponse


class SearchStrategy(ABC):
    @abstractmethod
    async def search(self, request: SearchRequest, session) -> SearchResponse: ...
