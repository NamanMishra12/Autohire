from sqlalchemy.orm import Session

from app.common.enums import ParsingStatus
from app.exceptions.custome_exceptions import ResumeNotFoundException
from app.repositories.resume_repository import ResumeRepository
from app.schemas.resume import ResumeResponse
from app.services.vector_service import VectorService
from app.tools.resume_parser import ResumeParserTool
from app.utils.logger import logger


class DocumentService:
    """
    Orchestrates the resume parsing pipeline:
    extract text -> clean -> chunk -> embed -> store in ChromaDB
    -> update Resume status.
    """

    def __init__(self, db: Session):
        self.db = db
        self.resume_repository = ResumeRepository(db)
        self.vector_service = VectorService()

    def parse_resume(self, resume_id: int) -> ResumeResponse:
        resume = self.resume_repository.get_by_id(resume_id)

        if not resume:
            raise ResumeNotFoundException()

        resume.parsing_status = ParsingStatus.PROCESSING.value
        self.resume_repository.update(resume)

        try:
            raw_text = ResumeParserTool.extract_text(resume.storage_path)
            cleaned_text = ResumeParserTool.clean_text(raw_text)
            chunks = ResumeParserTool.chunk_text(cleaned_text)

            chunk_count = self.vector_service.store_resume_chunks(
                resume_id=resume.id,
                chunks=chunks,
            )

            resume.parsed = True
            resume.parsing_status = ParsingStatus.COMPLETED.value
            resume.embedding_generated = chunk_count > 0

        except Exception as exc:
            resume.parsed = False
            resume.parsing_status = ParsingStatus.FAILED.value
            resume.embedding_generated = False

            self.resume_repository.update(resume)

            logger.exception(exc)
            raise

        self.resume_repository.update(resume)

        return ResumeResponse.model_validate(resume)