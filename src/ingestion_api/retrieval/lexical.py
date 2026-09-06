from urllib import request

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ingestion_api.domain.documents.models import Document, DocumentChunk
from ingestion_api.domain.search.schemas import SearchResult, SearchRequest
from ingestion_api.retrieval.filters import apply_search_filters


class LexicalRetriever:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def fuzzy_text_search(self, request: SearchRequest) -> list[SearchResult]:
        similar_query = func.similarity(
            DocumentChunk.text, request.query)

        statement = (
            select(
                DocumentChunk,
                Document,
                similar_query.label("score")
            ).join(
                Document,
                Document.id == DocumentChunk.document_id
            ).where(
                similar_query > 0.15
            )
        )

        statement = apply_search_filters(statement, request)
        statement = statement.order_by(similar_query.desc())
        statement = statement.limit(request.limit)
        result = await self.session.execute(statement)
        return [
            self._to_result(chunk,document, float(score_value)) for chunk, document, score_value in result.all()
        ]

    async def keyword_search(self, request: SearchRequest) -> list[SearchResult]:
        ts_query = func.websearch_to_tsquery("simple", request.query)
        score = func.ts_rank_cd(
            DocumentChunk.search_vector, ts_query
        )
        statement = (
            select(
                DocumentChunk,
                Document,
                score.label("score")
            ).join(
                Document,
                Document.id == DocumentChunk.document_id
            ).where(
                DocumentChunk.search_vector.op("@@")(ts_query)
            )
        )

        statement = apply_search_filters(statement, request)
        statement = statement.order_by(score.desc())
        statement = statement.limit(request.limit)
        result = await self.session.execute(statement)
        return [
            self._to_result(chunk,document, float(score_value)) for chunk, document, score_value in result.all()
        ]

    async def text_search(self, request: SearchRequest) -> list[SearchResult]:
        ts_query = func.phraseto_tsquery("simple", request.query)
        score = func.ts_rank_cd(
            DocumentChunk.search_vector, ts_query
        )
        statement = (
            select(
                DocumentChunk,
                Document,
                score.label("score")
            ).join(
                Document,
                Document.id == DocumentChunk.document_id
            ).where(
                DocumentChunk.search_vector.op("@@")(ts_query)
            )
        )

        statement = apply_search_filters(statement, request)
        statement = statement.order_by(score.desc())
        statement = statement.limit(request.limit)
        result = await self.session.execute(statement)
        return [
            self._to_result(chunk,document, float(score_value)) for chunk, document, score_value in result.all()
        ]

    def _to_result(self, chunk: DocumentChunk, document: Document, score: float) -> SearchResult:
        return SearchResult(
            document_id=str(document.id),
            chunk_id=str(chunk.id),
            filename=document.file_name,
            score=score,
            chunk_index=chunk.chunk_index,
            sections=chunk.sections,
            page_end=chunk.page_end,
            page_start=chunk.page_start,
            text=chunk.text,
        )