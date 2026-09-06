import os

from sqlalchemy import select

from ingestion_api.core.config import settings

from ingestion_api.core.database import AsyncSessionFactory

from ingestion_api.domain.documents.models import DocumentChunk

from ingestion_api.llm.embeddings.sentence_transformer import SentenceTransformerEmbeddingService

BATCH_SIZE = 32

async def main():
    embedding_service = SentenceTransformerEmbeddingService(
        settings.embedding_model
    )

    async with AsyncSessionFactory() as session:
        result = await session.execute(select(DocumentChunk).where(DocumentChunk.embedding.is_(None)).order_by(DocumentChunk.id, DocumentChunk.chunk_index))

        chunks = list(result.scalars().all())

        print(f"{len(chunks)} chunks to embed")

        for start in range(0, len(chunks), BATCH_SIZE):
            batch = chunks[start:start + BATCH_SIZE]
            texts = [
                (
                    f"Section: {chunk.sections}\n\n"
                    if chunk.sections else ""
                )
                + chunk.text for chunk in batch
            ]
            embeddings = embedding_service.embed_documents(texts)

            for chunk, embedding in zip(batch, embeddings, strict=True):
                chunk.embedding = embedding

            await session.commit()
            print(
                f"{min(start + BATCH_SIZE, len(chunks))} / {len(chunks)} chunks embedded: {batch[0].document_id}"
            )


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())