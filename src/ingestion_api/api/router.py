from  fastapi import APIRouter

from ingestion_api.api.v1.ingestion import router as ingestion_router

api_router = APIRouter(
    prefix="/api/v1",
)

api_router.include_router(ingestion_router)