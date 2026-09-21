from datetime import date
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select, update

from ingestion_api.domain.documents.models import Document, DocumentChunk


from ingestion_api.domain.ingestion.schemas import ChunkData

class DocumentRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_hash(self, content_hash: str) -> Document | None:
        result = await self.session.execute(
            select(Document).where(Document.content_hash == content_hash)
        )
        return result.scalar_one_or_none()

    async def get_by_source_url(self, url: str) -> Document | None:
        result = await self.session.execute(
            select(Document).where(Document.source_url == url)
        )
        return result.scalar_one_or_none()

    async def create_document(self, *, filename: str, content_hash: str, title: str, document_type: str = "text", publication_date: str = "2023-01-01", stored_filename: str) -> Document:
        document = Document(
            file_name=filename,
            stored_filename=stored_filename,
            content_hash=content_hash,
            title=title,
            document_type=document_type,
            publication_date=date.fromisoformat(publication_date),
            status="processing"
        )
        self.session.add(document)
        await self.session.flush()
        return document

    async def replace_chuncks(self, document_id: UUID, chunks: list[ChunkData], embeddings: list[list[float]]):
        await self.session.execute(delete(DocumentChunk).where(DocumentChunk.document_id == document_id))

        objects = []

        for chunk, embedding in zip(chunks, embeddings, strict=True):
            objects.append(
                DocumentChunk(
                    document_id=document_id,
                    chunk_index=chunk.chunk_index,
                    text=chunk.text,
                    sections=chunk.section,
                    page_start=chunk.page_start or 0,
                    page_end=chunk.page_end or 0,
                    metadata_=chunk.metadata,
                    embedding=embedding
                )
            )

        self.session.add_all(objects)

    async def mark_ready(self, document: Document):
        document.status = "ready"

    async def mark_failed(self, document: Document):
        document.status = "failed"

    async def attach_source_url(self, document_id: UUID, url: str):
        statement = (
            update(Document)
            .where(Document.id == document_id)
            .values(source_url=url)
        )
        await self.session.execute(statement)

    async def update_metadata(self, document: Document, metadata) -> None:
        document.countries = metadata.countries
        document.authority = metadata.authority
        document.legal_references = metadata.legal_references
        document.language = metadata.language
        document.source_url = ", ".join(metadata.source_urls) if metadata.source_urls else None
        document.publication_date = metadata.publication_date if metadata.publication_date else date.today()
        document.effective_date = metadata.effective_date
        document.expiration_date = metadata.expiration_date
        document.metadata_ = {
            **document.metadata_,
            'topics': metadata.topics,
            'metadata_confidence': metadata.confidence.model_dump()
        }

    async def update_processing_version(self, document: Document, *, processing_version: str, parser_version: str, chunking_version: str, metadata_version: str, embedding_model: str) -> None:
        document.processing_version = processing_version
        document.parser_version = parser_version
        document.chunking_version = chunking_version
        document.metadata_version = metadata_version
        document.embedding_model = embedding_model

        await self.session.flush()

    async def get_by_id(self, document_id: UUID) -> Optional[Document]:
        result = await self.session.execute(
            select(Document).where(Document.id == document_id)
        )
        return result.scalar_one_or_none()