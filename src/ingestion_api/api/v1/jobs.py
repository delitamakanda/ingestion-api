from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ingestion_api.domain.jobs.enums import JobStatus
from ingestion_api.domain.jobs.schemas import JobResponse
from ingestion_api.core.database import get_db
from ingestion_api.domain.jobs.repository import JobRepository
from ingestion_api.workers.broker import ArqJobBroker

broker = ArqJobBroker()


router = APIRouter(
    prefix="/jobs",
    tags=["jobs"]
)

@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: UUID, session: AsyncSession = Depends(get_db)):
    job_repository = JobRepository(session)
    job = await job_repository.get_job_by_id(job_id)

    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    return job

@router.get("/", response_model=list[JobResponse])
async def list_jobs(status: JobStatus | None = None, session: AsyncSession = Depends(get_db)):
    job_repository = JobRepository(session)
    return await job_repository.list_jobs(status=status)


@router.post("/{job_id}/retry", response_model=JobResponse)
async def retry_job(job_id: UUID, session: AsyncSession = Depends(get_db)):
    job_repository = JobRepository(session)
    job = await job_repository.get_job_by_id(job_id)

    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    if job.status != JobStatus.FAILED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only failed jobs can be retried")

    job.status = JobStatus.PENDING
    job.finished_at = None
    await session.commit()

    await broker.enqueue_ingestion(job.id)

    return {
        "id": job.id,
        "status": job.status,
        "current_step": job.current_step,
        "progress": job.progress,
        "attempts": job.attempts,
        "error_code": job.error_code,
        "error_message": job.error_message,
        "created_at": job.created_at,
        "started_at": job.started_at,
        "finished_at": job.finished_at,
    }
