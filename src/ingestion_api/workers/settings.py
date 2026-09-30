from typing import ClassVar
from uuid import UUID

from arq import Retry

from ingestion_api.core.database import AsyncSessionFactory
from ingestion_api.core.logging import get_logger
from ingestion_api.workers.ingestion import process_ingestion_job

logger = get_logger(__name__)


async def ingest_document(ctx, job_id: UUID):
    async with AsyncSessionFactory() as session:
        try:
            await process_ingestion_job(job_id=job_id, session=session)
        except Exception as e:  # noqa: BLE001 - unexpected worker failures should be retried
            logger.error(f"Error processing ingestion job {job_id}: {e}")
            raise Retry(defer=30)


class WorkerSettings:
    functions: ClassVar[list] = [ingest_document]
    max_tries = 3
