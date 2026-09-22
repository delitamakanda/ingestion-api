from fastapi import APIRouter, status, Depends, Response

from sqlalchemy.ext.asyncio import AsyncSession

from ingestion_api.core.database import get_db

from ingestion_api.core.health import HealthResponse, HealthStatus, ReadinessResponse, check_database_health, check_redis_health

router = APIRouter(
    tags=["health"]
)

@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """
    Health check endpoint.
    """
    return HealthResponse(status=HealthStatus.HEALTHY)

@router.get("/ready", response_model=ReadinessResponse)
async def readiness(response: Response, db: AsyncSession = Depends(get_db)) -> ReadinessResponse:
    """
    Readiness check endpoint.
    """
    database_health = await check_database_health(db)
    redis_health = await check_redis_health()

    dependencies = {
        "database": database_health,
        "redis": redis_health,
    }

    ready = all(dep.status == HealthStatus.HEALTHY for dep in dependencies.values())

    if not ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return ReadinessResponse(status=HealthStatus.UNAVAILABLE if not ready else HealthStatus.HEALTHY, dependencies=dependencies)