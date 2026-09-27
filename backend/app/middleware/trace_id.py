from http.client import responses

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from uuid import uuid4

from app.core.log_config import logger


class TraceIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        trace_id = str(uuid4())[:8]
        ip = request.headers.get("X-Forwarded-For") if request.headers.get("X-Forwarded-For") else request.client.host
        method = request.method
        url_path = request.url.path
        with logger.contextualize(trace_id=trace_id):
            logger.info(f"request: trace_id:{trace_id}, ip:{ip}, method:{method}, path:{url_path}")
            response = await call_next(request)
            logger.info(f"response: trace_id:{trace_id}, code:{response.status_code}")
        return response

# if __name__ == '__main__':
#     print(uuid4())