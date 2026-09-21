import time

from sentence_transformers import CrossEncoder

from ingestion_api.domain.search.schemas import SearchResult

from ingestion_api.retrieval.reranker import Reranker
from ingestion_api.core.logging import get_logger

logger = get_logger(__name__)

class CrossEncoderReranker(Reranker):
    def __init__(self, model_name: str):
        self.model = CrossEncoder(model_name)

    def rerank(self, *, query: str, results: list[SearchResult], top_k: int) -> list[SearchResult]:
        start_time = time.perf_counter()
        if not results:
            return []

        pairs = [(query, self._build_passages(result)) for result in results]

        scores = self.model.predict(pairs)
        ranked = sorted(zip(results, scores), key=lambda x: float(x[1]), reverse=True)

        output = []
        for result, score in ranked[:top_k]:
            output.append(
                result.model_copy(update={"reranker_score": float(score)})
            )
        logger.info("cross_encoder_reranker.rerank.completed", query=query, top_k=top_k, elapsed=(time.perf_counter() - start_time) * 1000)
        return output


    @staticmethod
    def _build_passages(result: SearchResult) -> str:
        parts = []

        if result.filename:
            parts.append(f"Document: {result.filename}")
        if result.sections:
            parts.append(f"{result.sections}")
        parts.append(
            result.text
        )
        return "\n\n".join(parts)