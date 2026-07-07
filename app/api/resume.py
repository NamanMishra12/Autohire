from fastapi import APIRouter, Depends, File, UploadFile

from app.common.responses import ApiResponse
from app.core.dependencies import (
    get_current_user_id,
    get_document_service,
    get_resume_service,
)
from app.services.document_service import DocumentService
from app.services.resume_service import ResumeService

router = APIRouter(prefix="/resume", tags=["Resume"])


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
    resume_service: ResumeService = Depends(get_resume_service),
):
    """
    Upload a resume file.

    Validates extension, streams the file to disk while computing
    its SHA256 checksum, detects duplicate uploads, and persists
    the resulting metadata.
    """

    resume = await resume_service.upload_resume(
        file=file,
        user_id=user_id,
    )

    return ApiResponse.success(
        message="Resume uploaded successfully.",
        data=resume.model_dump(mode="json"),
    )


@router.post("/{resume_id}/parse")
async def parse_resume(
    resume_id: int,
    document_service: DocumentService = Depends(get_document_service),
):
    """
    Parses a previously uploaded resume: extracts text, chunks it,
    generates embeddings, and stores them in ChromaDB.
    """

    resume = document_service.parse_resume(resume_id)

    return ApiResponse.success(
        message="Resume parsed successfully.",
        data=resume.model_dump(mode="json"),
    )