from abc import ABC, abstractmethod

from ingestion_api.domain.search.schemas import SearchResponse, SearchRequest


class SearchStrategy(ABC):
    @abstractmethod
    async def search(self, request: SearchRequest) -> SearchResponse:
        ...
