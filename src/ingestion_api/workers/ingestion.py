import time
import structlog
from uuid import UUID
from pathlib import Path

from ingestion_api.core.config import settings
from ingestion_api.domain.documents.models import Document
from ingestion_api.core.logging import get_logger
from ingestion_api.domain.ingestion.pipeline import IngestionPipeline
from ingestion_api.domain.jobs.enums import ProcessingStep
from ingestion_api.domain.jobs.models import JobType
from ingestion_api.domain.jobs.repository import JobRepository
from ingestion_api.llm.embeddings.sentence_transformer import SentenceTransformerEmbeddingService
from ingestion_api.domain.ingestion.exceptions import PermanentIngestionError, RetryableIngestionError
from ingestion_api.core.database import AsyncSessionFactory

logger = get_logger(__name__)

async def update_progress(*, job_id: UUID, step: str, progress: int):
    logger.info("ingestion.job.progress", job_id=job_id, step=step, progress=progress)
    async with AsyncSessionFactory() as session:
        jobs = JobRepository(session)
        job = await jobs.get_job_by_id(job_id)
        if job is None:
            raise RuntimeError(
                f"Ingestion job with ID {job_id} not found"
        )
    await jobs.update_job_status(job=job, step=ProcessingStep(step), progress=progress)
    await session.commit()


async def process_ingestion_job(*, job_id: UUID, session):
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(job_id=str(job_id))
    jobs = JobRepository(session)
    job = await jobs.get_job_by_id(job_id)
    if job is None:
        raise RuntimeError(
            f"Ingestion job with ID {job_id} not found"
        )
    if job.attempts >= settings.ingestion_max_attempts:
        await jobs.mark_failed(job, error_code='MAX_ATTEMPTS_EXCEEDED', error_message=f"Job has exceeded the maximum number of attempts ({settings.ingestion_max_attempts})")
        await session.commit()
        return
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
        )

    try:
        logger.info("ingestion.job.started", filename=job.original_filename, attempt=job.attempts + 1)
        start_time = time.perf_counter()
        document: Document = None
        if job.job_type == JobType.INGESTION:
            document = await pipeline.ingest(
                file_path=path,
                content_hash=job.content_hash,
                original_filename=job.original_filename,
                on_progress=progress_callback,
            )
        elif job.job_type == JobType.REINDEX:
            document = await pipeline.reindex(
                file_path=path,
                on_progress=progress_callback,
            )
        await jobs.attach_document(job, document_id=document.id)
        await jobs.mark_completed(job)
        await session.commit()
        end_time = time.perf_counter() - start_time * 1000
        logger.info("ingestion.job.completed", document_id=document.id, duration=round(end_time, 2))
    except PermanentIngestionError as e:
        await session.rollback()
        job = await jobs.get_job_by_id(job_id)
        if job:
            await jobs.mark_failed(job, error_code="PERMANENT_INGESTION_ERROR", error_message=str(e))
            await session.commit()
    except RetryableIngestionError:
        await session.rollback()
        raise
    except Exception as e:
        await session.rollback()
        job = await jobs.get_job_by_id(job_id)
        if job:
            await jobs.mark_failed(job, error_code="INGESTION_ERROR", error_message=str(e))
            await session.commit()
            logger.exception("ingestion.job.failed", job_id=job.id, error_message=str(e))
        raise
    finally:
        structlog.contextvars.clear_contextvars()

