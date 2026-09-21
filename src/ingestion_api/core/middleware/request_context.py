from uuid import uuid4

import structlog
import time
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp


class RequestContextMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, /) -> None:
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid4())
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)
        logger = structlog.get_logger("http")

        start_time = time.perf_counter()

        logger.info(
            "http.request.start",
            method=request.method,
            path=request.url.path,
        )

        request.state.request_id = request_id

        try:
            response = await call_next(request)

            duration = (time.perf_counter() - start_time) * 1000  # Convert to milliseconds

            logger.info(
                "http.request.end",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration=round(duration, 2)
            )

            response.headers["X-Request-ID"] = request_id

            return response
        except Exception:
            duration_ms = (time.perf_counter() - start_time) * 1000  # Convert to milliseconds
            logger.exception(
                "http.request.exception",
                method=request.method,
                path=request.url.path,
                duration=round(duration_ms, 2)
            )
            raise
        finally:
            structlog.contextvars.clear_contextvars()
