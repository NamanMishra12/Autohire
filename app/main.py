import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.applications import router as applications_router
from app.api.auto_apply import router as auto_apply_router
from app.api.cover_letter import router as cover_letter_router
from app.api.health import router as health_router
from app.api.info import router as info_router
from app.api.jobs import router as jobs_router
from app.api.match import router as match_router
from app.api.resume import router as resume_router
from app.api.tailor import router as tailor_router
from app.core.config import settings
from app.database.init_db import init_database
from app.exceptions.custome_exceptions import (
    DuplicateResumeException,
    FileTooLargeException,
    ResumeNotFoundException,
    UnsupportedFileTypeException,
)
from app.exceptions.handlers import (
    duplicate_resume_exception_handler,
    file_too_large_exception_handler,
    generic_exception_handler,
    resume_not_found_exception_handler,
    unsupported_file_type_exception_handler,
)
from app.middleware.request_logger import RequestLoggerMiddleware
from app.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("===================================")
    logger.info(f"Starting {settings.APP_NAME}")
    logger.info("===================================")
    init_database()
    yield
    logger.info("Application Shutdown")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

app.add_middleware(RequestLoggerMiddleware)

app.add_exception_handler(DuplicateResumeException, duplicate_resume_exception_handler)
app.add_exception_handler(UnsupportedFileTypeException, unsupported_file_type_exception_handler)
app.add_exception_handler(FileTooLargeException, file_too_large_exception_handler)
app.add_exception_handler(ResumeNotFoundException, resume_not_found_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

app.include_router(health_router)
app.include_router(info_router)
app.include_router(resume_router)
app.include_router(jobs_router)
app.include_router(match_router)
app.include_router(tailor_router)
app.include_router(cover_letter_router)
app.include_router(applications_router)
app.include_router(auto_apply_router)


@app.get("/", tags=["Root"])
async def root():
    return {
        "success": True,
        "message": f"Welcome to {settings.APP_NAME}",
    }