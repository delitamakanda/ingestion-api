from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException

from ingestion_api.core.database import get_db
from ingestion_api.domain.documents.models import DocumentChunk, Document

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ingestion_api.domain.jobs.models import JobType
from ingestion_api.domain.jobs.repository import JobRepository
from ingestion_api.workers.broker import ArqJobBroker

broker = ArqJobBroker()

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

@router.post("/{document_id}/reindex", status_code=202)
async def reindex_document(document_id: UUID, db: AsyncSession = Depends(get_db)):
    job_repository = JobRepository(db)
    statement = select(Document).where(Document.id == document_id)
    result = await db.execute(statement)
    document = result.scalar_one_or_none()
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    job = await job_repository.create_job(
        original_filename=document.file_name,
        stored_filename=document.stored_filename,
        content_hash=document.content_hash,
        job_type=JobType.REINDEX
    )
    await db.commit()
    await broker.enqueue_ingestion(job.id)
    if job is None:
        raise HTTPException(status_code=500, detail="Failed to create reindex job")
    return {"job_id": str(job.id)}