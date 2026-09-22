from fastapi import FastAPI

from ingestion_api.api.router import api_router
from ingestion_api.core.logging import configure_logging, get_logger
from ingestion_api.core.middleware.request_context import RequestContextMiddleware
from ingestion_api.api.health import router as health_router

configure_logging()
logger = get_logger(__name__)


app = FastAPI(
    title="Ingestion API",
    version="0.1.0",
    description="Ingestion API",
    docs_url="/docs",
)

app.add_middleware(RequestContextMiddleware)
app.include_router(health_router)


app.include_router(api_router)
