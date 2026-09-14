from uuid import UUID
from pathlib import Path

from ingestion_api.core.config import settings
from ingestion_api.domain.ingestion.pipeline import IngestionPipeline
from ingestion_api.domain.jobs.enums import ProcessingStep
from ingestion_api.domain.jobs.repository import JobRepository
from ingestion_api.llm.embeddings.sentence_transformer import SentenceTransformerEmbeddingService

async def update_progress(*, job_id: UUID, step: str, progress: int, session):
    jobs = JobRepository(session)
    job = await jobs.get_job_by_id(job_id)
    if job is None:
        raise RuntimeError(
            f"Ingestion job with ID {job_id} not found"
        )
    await jobs.update_job_status(job=job, step=ProcessingStep(step), progress=progress)
    await session.commit()


async def process_ingestion_job(*, job_id: UUID, session):
    jobs = JobRepository(session)
    job = await jobs.get_job_by_id(job_id)
    if job is None:
        raise RuntimeError(
            f"Ingestion job with ID {job_id} not found"
        )
    await jobs.mark_started(job)

    await session.commit()

    path = Path(settings.upload_dir) / job.stored_filename
    embedding_service = SentenceTransformerEmbeddingService(model_name=settings.embedding_model)
    pipeline = IngestionPipeline(session=session, embedding_service=embedding_service)

    async def progress_callback(
            step: str,
            progress: int,
    ):
        await update_progress(
            job_id=job_id,
            step=step,
            progress=progress,
            session=session,
        )

    try:
        document = await pipeline.ingest(
            file_path=path,
            content_hash=job.content_hash,
            original_filename=job.original_filename,
            on_progress=progress_callback,
        )
        await jobs.attach_document(job, document_id=document.id)
        await jobs.mark_completed(job)
        await session.commit()
    except Exception as e:
        await session.rollback()
        job = await jobs.get_job_by_id(job_id)
        if job:
            await jobs.mark_failed(job, error_code="INGESTION_ERROR", error_message=str(e))
            await session.commit()
        raise

