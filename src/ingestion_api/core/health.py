import time
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from ingestion_api.core.logging import get_logger
from enum import StrEnum
from pydantic import BaseModel
from arq.connections import RedisSettings, create_pool

from ingestion_api.core.config import settings

logger = get_logger(__name__)

class HealthStatus(StrEnum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNAVAILABLE = "unavailable"

class HealthResponse(BaseModel):
    status: HealthStatus

class DependencyHealth(BaseModel):
    status: HealthStatus
    latency: float
    error: str

class ReadinessResponse(BaseModel):
    status: HealthStatus
    dependencies: dict[str, DependencyHealth]

async def check_database_health(session: AsyncSession) -> DependencyHealth:
    """
    Check the health of the database by executing a simple query.
    """
    start_time = time.perf_counter()
    try:
        await session.execute(text("SELECT 1"))
        latency = (time.perf_counter() - start_time) * 1000  # Convert to milliseconds
        return DependencyHealth(status=HealthStatus.HEALTHY, latency=latency, error="")
    except Exception as e:
        latency = (time.perf_counter() - start_time) * 1000  # Convert to milliseconds
        logger.exception("health.database.check_failed", exc_info=e)
        return DependencyHealth(status=HealthStatus.UNHEALTHY, latency=latency, error=str(e))

async def check_redis_health() -> DependencyHealth:
    """
    Check the health of the Redis connection by pinging the Redis server.
    """
    start_time = time.perf_counter()

    redis_pool = None
    try:
        redis_pool = await create_pool(RedisSettings.from_dsn(settings.redis_url))

        await redis_pool.ping()

        latency = (time.perf_counter() - start_time) * 1000  # Convert to milliseconds
        return DependencyHealth(status=HealthStatus.HEALTHY, latency=latency, error="")
    except Exception as e:
        latency = (time.perf_counter() - start_time) * 1000  # Convert to milliseconds
        logger.exception("health.redis.check_failed", exc_info=e)
        return DependencyHealth(status=HealthStatus.UNHEALTHY, latency=latency, error=str(e))
    finally:
        if redis_pool:
            await redis_pool.aclose()