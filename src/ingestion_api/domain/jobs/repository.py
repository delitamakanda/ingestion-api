from ingestion_api.domain.jobs.models import IngestionJob
from datetime import datetime, UTC
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ingestion_api.domain.jobs.enums import JobStatus, ProcessingStep



class JobRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_job(self, *, original_filename: str, stored_filename: str, content_hash: str) -> IngestionJob:
        job = IngestionJob(
            original_filename=original_filename,
            stored_filename=stored_filename,
            content_hash=content_hash,
            status=JobStatus.PENDING,
            progress=0,
        )
        self.session.add(job)
        await self.session.flush()
        return job

    async def get_job_by_id(self, job_id: UUID) -> IngestionJob | None:
        stmt = select(IngestionJob).where(IngestionJob.id == job_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def mark_started(self, job: IngestionJob) -> None:

        job.started_at = datetime.now(UTC)
        job.attempts += 1
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