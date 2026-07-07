from __future__ import annotations

import hashlib
import uuid

from datetime import datetime
from pathlib import Path

from fastapi import UploadFile

from app.common.constants import MAX_FILE_SIZE
from app.core.config import settings
from app.exceptions.custome_exceptions import FileTooLargeException


class FileStorage:
    """
    Handles physical storage of uploaded files.
    """

    CHUNK_SIZE = 1024 * 1024  # 1 MB

    @staticmethod
    def generate_filename(extension: str) -> str:
        return f"{uuid.uuid4()}{extension}"

    @staticmethod
    def create_directory() -> Path:
        now = datetime.utcnow()

        directory = (
            Path(settings.UPLOAD_DIR)
            / str(now.year)
            / f"{now.month:02d}"
        )

        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        return directory

    @classmethod
    async def save(cls, file: UploadFile):
        extension = Path(file.filename).suffix.lower()

        directory = cls.create_directory()

        filename = cls.generate_filename(extension)

        filepath = directory / filename

        sha256 = hashlib.sha256()

        total_size = 0

        try:
            with filepath.open("wb") as output:

                while True:

                    chunk = await file.read(cls.CHUNK_SIZE)

                    if not chunk:
                        break

                    total_size += len(chunk)

                    if total_size > MAX_FILE_SIZE:

                        output.close()

                        filepath.unlink(missing_ok=True)

                        raise FileTooLargeException(
                            message="File exceeds maximum allowed size.",
                        )

                    sha256.update(chunk)

                    output.write(chunk)

            await file.seek(0)

            return {
                "filename": filename,
                "path": str(filepath),
                "checksum": sha256.hexdigest(),
                "size": total_size,
            }

        except Exception:

            if filepath.exists():
                filepath.unlink()

            raise