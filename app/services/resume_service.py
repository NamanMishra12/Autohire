from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.exceptions.custome_exceptions import DuplicateResumeException
from app.models.resume import Resume
from app.repositories.resume_repository import ResumeRepository
from app.schemas.resume import ResumeResponse
from app.storage.file_storage import FileStorage
from app.utils.file_validator import FileValidator


class ResumeService:
    """
    Handles resume upload business logic.
    """

    def __init__(self, db: Session):
        self.db = db
        self.resume_repository = ResumeRepository(db)

    async def upload_resume(
        self,
        file: UploadFile,
        user_id: int,
    ) -> ResumeResponse:
        """
        Upload a resume, detect duplicates,
        persist metadata, and return the created record.
        """

        # Step 1: Validate uploaded file metadata
        await FileValidator.validate(file)

        # Step 2: Save file while computing checksum
        file_info = await FileStorage.save(file)

        # Step 3: Check for duplicate resume
        existing_resume = self.resume_repository.get_by_checksum(
            file_info["checksum"]
        )

        if existing_resume:
            Path(file_info["path"]).unlink(missing_ok=True)

            raise DuplicateResumeException()

        # Step 4: Create Resume model
        resume = Resume(
            user_id=user_id,
            original_filename=file.filename,
            stored_filename=file_info["filename"],
            storage_path=file_info["path"],
            mime_type=file.content_type or "application/pdf",
            file_size=file_info["size"],
            checksum=file_info["checksum"],
        )

        # Step 5: Save metadata to database
        try:
            resume = self.resume_repository.create(resume)

        except Exception:
            # Remove uploaded file if database insert fails
            Path(file_info["path"]).unlink(missing_ok=True)
            raise

        # Step 6: Return response schema
        return ResumeResponse.model_validate(resume)