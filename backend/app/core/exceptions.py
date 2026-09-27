from fastapi import Request, FastAPI
# from fastapi.responses import JSONResponse
from fastapi import status
from typing import Any
from app.common.response import ErrorResponse
from app.core.log_config import logger

class CustomException(Exception):
    def __init__(self, message: str = None,
                 code: int = 500,
                 status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
                 ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code


def register_exception_handler(app: FastAPI) -> Any:

    @app.exception_handler(CustomException)
    async def custom_exception_handler(request: Request, exc: CustomException):
        logger.exception(f"Error:{request.method} - {request.url.path} - {exc.message}")
        return ErrorResponse(message=str(exc), status_code=exc.status_code, code=exc.code, data=None)


    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.exception(f"Error:{request.method} - {request.url.path} - {exc}")
        return ErrorResponse(message="服务器错误", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, code=5000, data=None)