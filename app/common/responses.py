from typing import Any

from fastapi.responses import JSONResponse


class ApiResponse:

    @staticmethod
    def success(
        message: str = "Success",
        data: Any = None,
        status_code: int = 200,
    ):
        return JSONResponse(
            status_code=status_code,
            content={
                "success": True,
                "message": message,
                "data": data,
                "errors": None,
            },
        )

    @staticmethod
    def error(
        message: str,
        errors: Any = None,
        status_code: int = 400,
    ):
        return JSONResponse(
            status_code=status_code,
            content={
                "success": False,
                "message": message,
                "data": None,
                "errors": errors,
            },
        )