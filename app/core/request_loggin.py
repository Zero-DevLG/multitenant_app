import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.core.logging import get_logger

logger = get_logger("request")

class RequestLogginMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        
        logger.info(
            f"{request.method} {request.url.path} "
            f"| host={request.headers.get('host')} ß"
            f"| status={response.status_code} "
            f"| {duration_ms:.1f}ms"
        )
        return  response
        