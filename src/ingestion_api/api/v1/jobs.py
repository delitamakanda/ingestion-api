from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ingestion_api.domain.jobs.schemas import JobResponse
from ingestion_api.core.database import get_db
from ingestion_api.domain.jobs.repository import JobRepository


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