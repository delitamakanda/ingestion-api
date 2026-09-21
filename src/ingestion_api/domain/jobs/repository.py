from ingestion_api.domain.jobs.models import IngestionJob, JobType
from datetime import datetime, UTC
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ingestion_api.domain.jobs.enums import JobStatus, ProcessingStep



class JobRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_job(self, *, original_filename: str, stored_filename: str, content_hash: str, job_type: JobType = JobType.INGESTION) -> IngestionJob:
        job = IngestionJob(
            original_filename=original_filename,
            stored_filename=stored_filename,
            content_hash=content_hash,
            status=JobStatus.PENDING,
            job_type=job_type,
            progress=0,
        )
        self.session.add(job)
        await self.session.flush()
        return job

    async def get_job_by_id(self, job_id: UUID) -> IngestionJob | None:
        stmt = select(IngestionJob).where(IngestionJob.id == job_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_content_hash(self, content_hash: str) -> IngestionJob | None:
        active_statuses = [
            JobStatus.PENDING,
            JobStatus.PARSING,
            JobStatus.ENRICHING,
            JobStatus.EMBEDDING,
            JobStatus.CHUNKING,
            JobStatus.INDEXING
        ]
        stmt = select(IngestionJob).where(IngestionJob.content_hash == content_hash, IngestionJob.status.in_(
            [status.value for status in active_statuses]
        )).order_by(IngestionJob.started_at.desc()).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


    async def mark_started(self, job: IngestionJob) -> None:

        job.started_at = datetime.now(UTC)
        job.attempts += 1
        job.error_code = None
        job.error_message = None
        job.finished_at = None
        await self.session.flush()

    async def update_job_status(self, job: IngestionJob, *, step: ProcessingStep, progress: int):
        job.status = step.value
        job.current_step = step.value
        job.progress = progress
        await self.session.flush()

    async def attach_document(self, job: IngestionJob, *, document_id: UUID):
        job.document_id = document_id
        await self.session.flush()

    async def mark_completed(self, job: IngestionJob) -> None:
        job.status = JobStatus.COMPLETED
        job.progress = 100
        job.finished_at = datetime.now(UTC)
        job.error_code = None
        job.error_message = None
        await self.session.flush()

    async def mark_failed(self, job: IngestionJob, *, error_code: str, error_message: str) -> None:
        job.status = JobStatus.FAILED
        job.error_code = error_code
        job.error_message = error_message
        job.finished_at = datetime.now(UTC)
        await self.session.flush()

    async def find_stale_jobs(self, *, before: datetime) -> list[IngestionJob]:
        active = [
            JobStatus.PARSING.value,
            JobStatus.ENRICHING.value,
            JobStatus.EMBEDDING.value,
            JobStatus.CHUNKING.value,
            JobStatus.INDEXING.value
        ]
        stmt = select(IngestionJob).where(
            IngestionJob.status.in_(active),
            IngestionJob.updated_at < before
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_jobs(self, status: JobStatus | None = None) -> list[IngestionJob]:
        stmt = select(IngestionJob)
        if status is not None:
            stmt = stmt.where(IngestionJob.status == status)
        stmt = stmt.order_by(IngestionJob.created_at.asc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
