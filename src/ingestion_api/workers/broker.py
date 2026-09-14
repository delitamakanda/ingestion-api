from abc import ABC, abstractmethod
from uuid import UUID

from arq.connections import RedisSettings, create_pool

from ingestion_api.core.config import settings

class JobBroker(ABC):

    @abstractmethod
    async def enqueue_ingestion(self, job_id: UUID) -> None:
        ...

class ArqJobBroker(JobBroker):

    async def enqueue_ingestion(self, job_id: UUID) -> None:
        redis = await create_pool(RedisSettings.from_dsn(settings.redis_url))
        await redis.enqueue_job("ingest_document", str(job_id))