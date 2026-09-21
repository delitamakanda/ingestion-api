from abc import ABC, abstractmethod
from uuid import UUID

from arq.connections import RedisSettings, create_pool

from ingestion_api.core.config import settings

class JobBroker(ABC):

    @abstractmethod
    async def enqueue_ingestion(self, job_id: UUID) -> None:
        ...

class ArqJobBroker(JobBroker):

    def __init__(self):
        self._pool = None

    async def _get_pool(self):
        if self._pool is None:
            self._pool = await create_pool(RedisSettings.from_dsn(settings.redis_url))
        return self._pool

    async def enqueue_ingestion(self, job_id: UUID) -> None:
        redis = await self._get_pool()
        await redis.enqueue_job("ingest_document", str(job_id))