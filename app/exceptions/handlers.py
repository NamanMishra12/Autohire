from fastapi import Request
from fastapi.responses import JSONResponse

from app.exceptions.custome_exceptions import (
    DuplicateResumeException,
    FileTooLargeException,
    ResumeNotFoundException,
    UnsupportedFileTypeException,
    UnauthorizedException,
    InvalidCredentialsException,
)
from app.utils.logger import logger


async def generic_exception_handler(
    request: Request,
    exc: Exception,
):
    logger.exception(exc)

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal Server Error",
            "data": None,
            "errors": None,
        },
    )


async def duplicate_resume_exception_handler(
    request: Request,
    exc: DuplicateResumeException,
):
    return JSONResponse(
        status_code=409,
        content={
            "success": False,
            "message": exc.message,
            "data": None,
            "errors": None,
        },
    )


async def unsupported_file_type_exception_handler(
    request: Request,
    exc: UnsupportedFileTypeException,
):
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "message": exc.message,
            "data": None,
            "errors": None,
        },
    )


async def file_too_large_exception_handler(
    request: Request,
    exc: FileTooLargeException,
):
    return JSONResponse(
        status_code=413,
        content={
            "success": False,
            "message": exc.message,
            "data": None,
            "errors": None,
        },
    )


async def resume_not_found_exception_handler(
    request: Request,
    exc: ResumeNotFoundException,
):
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "message": exc.message,
            "data": None,
            "errors": None,
        },
    )

async def unauthorized_exception_handler(
    request: Request,
    exc: UnauthorizedException,
):
    return JSONResponse(
        status_code=401,
        content={
            "success": False,
            "message": exc.message,
            "data": None,
            "errors": None,
        },
    )

async def invalid_credentials_exception_handler(
    request: Request,
    exc: InvalidCredentialsException,
):
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "message": exc.message,
            "data": None,
            "errors": None,
        },
    )