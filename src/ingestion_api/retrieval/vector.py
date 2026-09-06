from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

from ingestion_api.domain.documents.models import DocumentChunk, Document

from ingestion_api.domain.search.schemas import SearchResult, SearchRequest
from ingestion_api.llm.embeddings.base import EmbeddingService
from ingestion_api.retrieval.filters import apply_search_filters


class VectorRetriever:
    def __init__(self, session: AsyncSession, embedding_service: EmbeddingService):
        self.session = session
        self.embedding_service = embedding_service

    async def search(self, request: SearchRequest, limit: int = 30) -> list[SearchResult]:
        query_embedding = self.embedding_service.embed_query(request.query)

        distance = (
            DocumentChunk.embedding.cosine_distance(query_embedding)
        )

        statement = (
            select(
                DocumentChunk,
                Document,
                distance.label("distance")
            ).join(
                Document,
                Document.id == DocumentChunk.document_id
            ).where(
                DocumentChunk.embedding.is_not(None)
            )
        )

        statement = apply_search_filters(statement, request)

        statement = (
            statement.order_by(distance.asc()).limit(limit)
        )

        rows = (await self.session.execute(statement)).all()

        return [
            SearchResult(
                document_id=str(document.id),
                chunk_id=str(chunk.id),
                filename=document.file_name,
                chunk_index=chunk.chunk_index,
                text=chunk.text,
                sections=chunk.sections,
                page_start=chunk.page_start,
                page_end=chunk.page_end,
                score=max(0.0, 0.1 - float(distance_value))

            ) for (chunk, document, distance_value) in rows
        ]
