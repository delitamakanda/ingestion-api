from uuid import UUID
from fastapi import APIRouter, Depends

from ingestion_api.core.database import get_db
from ingestion_api.domain.documents.models import DocumentChunk

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)

@router.get("/{document_id}/chunks")
async def get_document_chunks(document_id: UUID, db: AsyncSession = Depends(get_db)):
    statement = select(DocumentChunk).where(DocumentChunk.document_id == document_id).order_by(DocumentChunk.chunk_index)
    result = await db.execute(statement)
    chunks = result.scalars().all()
    return [
        {
            "id": str(chunk.id),
            "index": chunk.chunk_index,
            "sections": chunk.sections,
            "text": chunk.text,
            "page_start": chunk.page_start,
            "page_end": chunk.page_end,
            "metadata": chunk.metadata_,
        } for chunk in chunks
    ]