from fastapi import FastAPI

from ingestion_api.api.router import api_router
from ingestion_api.core.config import settings
from ingestion_api.core.logging import configure_logging, get_logger
from ingestion_api.core.middleware.request_context import RequestContextMiddleware

configure_logging()
logger = get_logger(__name__)


app = FastAPI(
    title="Ingestion API",
    version="0.1.0",
    description="Ingestion API",
    docs_url="/docs",
)

app.add_middleware(RequestContextMiddleware)


app.include_router(api_router)


@app.get("/health")
async def health():
    logger.info("Health check endpoint called", environment=settings.environment)
    return {"status": "ok", "service": "ingestion-api"}
