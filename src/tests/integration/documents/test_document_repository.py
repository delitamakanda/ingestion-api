import pytest

from ingestion_api.domain.documents.repository import DocumentRepository
from ingestion_api.domain.ingestion.schemas import ChunkData


@pytest.mark.integration
async def test_create_document(db_session):
    document_repository = DocumentRepository(db_session)
    await document_repository.create_document(
        filename="regulation1.pdf",
        stored_filename="regulation1.pdf",
        content_hash="doc-hash",
        title="Biomethane Regulation bis",
    )
    await db_session.commit()

    found = await document_repository.get_by_hash("doc-hash")
    assert found is not None
    assert found.title == "Biomethane Regulation bis"


@pytest.mark.integration
async def test_replace_chunks(db_session):
    document_repository = DocumentRepository(db_session)
    document = await document_repository.create_document(
        filename="regulation3.pdf",
        stored_filename="regulation3.pdf",
        content_hash="doc-hash-1233",
        title="Biomethane Regulation ter",
    )
    await db_session.commit()

    # Replace chunks
    new_chunks: list[ChunkData] = [
        ChunkData(
            text="chunk1",
            page_start=1,
            page_end=1,
            section="section1",
            chunk_index=0,
            metadata={},
        ),
    ]
    embedding: list[list[float | int]] = [[0.01] * 768]
    await document_repository.replace_chuncks(
        document.id, new_chunks, embeddings=embedding
    )
    await db_session.commit()

    found = await document_repository.get_by_hash("doc-hash-1233")
    assert found is not None
    assert found.title == "Biomethane Regulation ter"
