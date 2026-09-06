from datetime import datetime
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession

from ingestion_api.domain.documents.repository import DocumentRepository
from ingestion_api.domain.ingestion.chunking.semantic import SemanticChunker
from ingestion_api.domain.ingestion.parsers.registry import ParserRegistry
from ingestion_api.domain.ingestion.schemas import ChunkData
from ingestion_api.llm.embeddings.base import EmbeddingService

class IngestionPipeline:

    def __init__(self, session: AsyncSession, embedding_service: EmbeddingService):
        self.session = session
        self.embedding_service = embedding_service
        self.document_repository = DocumentRepository(session)
        self.parser_registry = ParserRegistry()
        self.chunker = SemanticChunker()

    async def ingest(self, *, file_path: Path, content_hash: str, original_filename: str):
        existing_document = await self.document_repository.get_by_hash(content_hash)

        if existing_document:
            return existing_document

        parser = self.parser_registry.get(file_path)

        parsed_document = await parser.parse(file_path)

        try:

            document = (
                await self.document_repository.create_document(
                    filename=original_filename,
                    content_hash=content_hash,
                    title=parsed_document.title,
                    document_type=file_path.suffix.lower().lstrip("."),
                    publication_date=datetime.now().strftime("%Y-%m-%d")
                )
            )

            chunks = self.chunker.chunk(parsed_document)

            embeddings = (
                self.embedding_service.embed_documents([
                    self._prepare_chunk_text(chunk) for chunk in chunks
                ])
            )

            await self.document_repository.replace_chuncks(document.id, chunks, embeddings)
            await self.document_repository.mark_ready(document)
            await self.session.commit()
            return document
        except Exception:
            await self.session.rollback()
            raise

    def _prepare_chunk_text(self, chunk: ChunkData) -> str:
        parts = []
        if chunk.section:
            parts.append(f"Section: {chunk.section}")

        parts.append(chunk.text)
        return "\n\n".join(parts)