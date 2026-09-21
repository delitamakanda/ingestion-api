from uuid import UUID
from ingestion_api.core.database import AsyncSessionFactory
from ingestion_api.workers.ingestion import process_ingestion_job
from arq import Retry

async def ingest_document(ctx, job_id: UUID):
    async with AsyncSessionFactory() as session:
        try:
            await process_ingestion_job(job_id=job_id, session=session)
        except Exception:
            raise Retry(
                defer=30
            )

class WorkerSettings:
    functions = [
        ingest_document
    ]
    max_tries = 3