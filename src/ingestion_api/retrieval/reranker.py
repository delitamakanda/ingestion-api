from abc import ABC, abstractmethod

from ingestion_api.domain.search.schemas import SearchResult

class Reranker(ABC):
    @abstractmethod
    def rerank(self, *, query: str, results: list[SearchResult], top_k: int) -> list[SearchResult]:
        ...