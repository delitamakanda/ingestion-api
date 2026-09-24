from fastapi import APIRouter, Response

from prometheus_client import (
CONTENT_TYPE_LATEST,
generate_latest,
)

router = APIRouter(
    tags=["metrics"]
)

@router.get("/metrics", include_in_schema=True)
async def metrics() -> Response:
    """
    Endpoint to expose Prometheus metrics.
    """
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)