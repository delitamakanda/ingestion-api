from  fastapi import APIRouter

from ingestion_api.api.v1.ingestion import router as ingestion_router
from ingestion_api.api.v1.documents import router as documents_router
from ingestion_api.api.v1.search import router as search_router

api_router = APIRouter(
    prefix="/api/v1",
)

api_router.include_router(ingestion_router)
api_router.include_router(documents_router)
api_router.include_router(search_router)