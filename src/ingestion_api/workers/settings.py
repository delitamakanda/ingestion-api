from uuid import UUID
from ingestion_api.core.database import AsyncSessionFactory
from ingestion_api.workers.ingestion import process_ingestion_job

async def ingest_document(ctx, job_id: UUID):
    async with AsyncSessionFactory() as session:
        await process_ingestion_job(job_id=job_id, session=session)

class WorkerSettings:
    functions = [
        ingest_document
    ]