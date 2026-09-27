from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi import status
from typing import Any


class SuccessResponse(JSONResponse):
    def __init__(self, data: Any = None,
                 message: str = "success",
                 code: int = 0,
                status_code: int = status.HTTP_200_OK) -> None:
        content = {"code": code, "message": message, "data": data}
        super().__init__(content=jsonable_encoder(content), status_code=status_code)
        self.headers["Content-Type"] = "application/json; charset=utf-8"


class ErrorResponse(JSONResponse):
    def __init__(self, data: Any = None,
                 message: str = "error",
                 code: int = 400,
                 status_code: int = status.HTTP_400_BAD_REQUEST) -> None:
        content = {"code": code, "message": message, "data": data}
        super().__init__(content=jsonable_encoder(content), status_code=status_code)
        self.headers["Content-Type"] = "application/json; charset=utf-8"