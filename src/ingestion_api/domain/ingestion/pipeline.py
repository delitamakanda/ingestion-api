from datetime import datetime
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession

from ingestion_api.core.config import settings
from ingestion_api.domain.documents.repository import DocumentRepository
from ingestion_api.domain.ingestion.chunking.semantic import SemanticChunker
from ingestion_api.domain.ingestion.enrichment.deterministic import DeterminisiticMetadataExtractor
from ingestion_api.domain.ingestion.enrichment.extractor import MetadataExtractor
from ingestion_api.domain.ingestion.enrichment.llm import LLMMetadataExtractor
from ingestion_api.domain.ingestion.enrichment.normalizer import MetadataNormalizer
from ingestion_api.domain.ingestion.parsers.registry import ParserRegistry
from ingestion_api.domain.ingestion.schemas import ChunkData
from ingestion_api.llm.embeddings.base import EmbeddingService
from ingestion_api.llm.providers.openai import OpenAILLMProvider


class IngestionPipeline:

    def __init__(self, session: AsyncSession, embedding_service: EmbeddingService):
        self.session = session
        self.embedding_service = embedding_service
        self.document_repository = DocumentRepository(session)
        self.parser_registry = ParserRegistry()
        self.chunker = SemanticChunker()
        self.metadata_extractor = MetadataExtractor(DeterminisiticMetadataExtractor(), LLMMetadataExtractor(OpenAILLMProvider(api_key=settings.openai_api_key, model=settings.llm_model)), MetadataNormalizer())

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

            metadata = await self.metadata_extractor.extract_metadata(parsed_document)

            chunks = self.chunker.chunk(parsed_document)

            embeddings = (
                self.embedding_service.embed_documents([
                    self._prepare_chunk_text(chunk, metadata) for chunk in chunks
                ])
            )

            await self.document_repository.update_metadata(document, metadata)

            for chunk in chunks:
                chunk.metadata.update({
                    "countries": metadata.countries,
                    "source_type": metadata.source_type,
                    "authority": metadata.authority,
                    "legal_references": metadata.legal_references,
                    "publication_date": metadata.publication_date.isoformat() if metadata.publication_date else None,
                    "effective_date": metadata.effective_date.isoformat() if metadata.effective_date else None,
                })

            await self.document_repository.replace_chuncks(document.id, chunks, embeddings)
            await self.document_repository.mark_ready(document)
            await self.session.commit()
            return document
        except Exception:
            await self.session.rollback()
            raise

    def _prepare_chunk_text(self, chunk: ChunkData, metadata) -> str:
        parts = []

        if metadata.countries:
            parts.append(f"Countries: {', '.join(metadata.countries)}")
        if metadata.authority:
            parts.append(f"Authority: {metadata.authority}")
        if metadata.legal_references:
            parts.append(f"Legal References: {', '.join(metadata.legal_references)}")
        if chunk.section:
            parts.append(f"Section: {chunk.section}")

        parts.append(chunk.text)
        return "\n\n".join(parts)