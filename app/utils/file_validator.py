from pathlib import Path

from fastapi import UploadFile

from app.common.constants import ALLOWED_RESUME_EXTENSIONS
from app.exceptions.custome_exceptions import UnsupportedFileTypeException


class FileValidator:
    """
    Validates upload metadata.

    File size validation is performed while streaming
    inside FileStorage.
    """

    @staticmethod
    async def validate(file: UploadFile) -> None:
        if not file.filename:
            raise UnsupportedFileTypeException(
                message="Filename is missing.",
            )

        extension = Path(file.filename).suffix.lower()

        if extension not in ALLOWED_RESUME_EXTENSIONS:
            raise UnsupportedFileTypeException(
                message=f"Unsupported file type '{extension}'.",
            )