
from sqlalchemy import select
from pathlib import Path

from ingestion_api.domain.ingestion.enrichment.deterministic import DeterminisiticMetadataExtractor
from ingestion_api.domain.ingestion.enrichment.llm import LLMMetadataExtractor
from ingestion_api.domain.ingestion.enrichment.normalizer import MetadataNormalizer
from ingestion_api.domain.ingestion.parsers.registry import ParserRegistry
from ingestion_api.domain.ingestion.enrichment.extractor import MetadataExtractor

from ingestion_api.core.config import settings

from ingestion_api.core.database import AsyncSessionFactory
from ingestion_api.domain.documents.models import Document
from ingestion_api.llm.providers.openai import OpenAILLMProvider


def compute_hash(file_path: Path) -> str:
    import hashlib

    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(8192), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


async def main():
    parser_registry = ParserRegistry()
    metadata_extractor = MetadataExtractor(DeterminisiticMetadataExtractor(), LLMMetadataExtractor(OpenAILLMProvider(api_key=settings.openai_api_key, model=settings.llm_model)), MetadataNormalizer())
    upload_dir = Path(settings.upload_dir)

    async with AsyncSessionFactory() as session:
        result = await session.execute(select(Document))

        documents = result.scalars().all()

        documents_by_hash = {
            document.content_hash: document for document in documents
        }



        for file_path in upload_dir.iterdir():
            if not file_path.is_file():
                continue

            try:
                content_hash = compute_hash(file_path)

                document = documents_by_hash.get(content_hash)
                if not document:
                    print(f"No document found for file {file_path} with hash {content_hash}")
                    continue
                parser = parser_registry.get(file_path)

                parsed_doc = await parser.parse(file_path)

                metadata = await metadata_extractor.extract_metadata(parsed_doc)

                document.countries = metadata.countries
                document.source_type = metadata.source_type
                document.authority = metadata.authority

                print(
                    f"[OK] {document.file_name}"
                    f" -> {file_path.name}"
                    f" -> {metadata.source_type.value}"
                    f" -> {metadata.countries}"
                )
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")

        await session.commit()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
