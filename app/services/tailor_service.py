from sqlalchemy.orm import Session

from app.agents.job_analyzer import JobAnalyzerAgent
from app.agents.matcher_agent import MatcherAgent
from app.agents.resume_tailor_agent import ResumeTailorAgent
from app.exceptions.custome_exceptions import ResumeNotFoundException
from app.repositories.job_repository import JobRepository
from app.repositories.resume_repository import ResumeRepository
from app.schemas.tailor import TailorResponse
from app.tools.resume_parser import ResumeParserTool
from app.utils.logger import logger


class TailorService:
    """
    Orchestrates the resume tailoring pipeline:
    1. Extract resume text
    2. Analyze job with LLM
    3. Score resume against job
    4. Tailor resume using match gaps
    5. Return tailored content
    """

    def __init__(self, db: Session):
        self.db = db
        self.resume_repository = ResumeRepository(db)
        self.job_repository = JobRepository(db)

    async def tailor_resume(
        self,
        resume_id: int,
        job_id: int,
    ) -> TailorResponse:

        # Step 1: Load resume
        resume = self.resume_repository.get_by_id(resume_id)
        if not resume:
            raise ResumeNotFoundException(
                message=f"Resume with id {resume_id} not found."
            )

        # Step 2: Load job
        job = self.job_repository.get_by_id(job_id)
        if not job:
            raise ResumeNotFoundException(
                message=f"Job with id {job_id} not found."
            )

        # Step 3: Extract resume text
        raw_text = ResumeParserTool.extract_text(resume.storage_path)
        cleaned_text = ResumeParserTool.clean_text(raw_text)

        # Step 4: Analyze job
        logger.info(f"Tailoring resume {resume_id} for job {job_id}")
        analyzer = JobAnalyzerAgent()
        job_analysis = await analyzer.analyze(
            job_title=job.title,
            job_description=job.description or "",
        )

        # Step 5: Score resume against job first
        matcher = MatcherAgent()
        match_result = await matcher.match(
            resume_text=cleaned_text,
            job_title=job.title,
            job_analysis=job_analysis,
        )

        # Step 6: Tailor resume using match gaps
        tailor = ResumeTailorAgent()
        tailored = await tailor.tailor(
            resume_text=cleaned_text,
            job_title=job.title,
            job_analysis=job_analysis,
            match_result=match_result,
        )

        return TailorResponse(
            resume_id=resume_id,
            job_id=job_id,
            job_title=job.title,
            score_before=match_result.get("score", 0),
            match_level_before=match_result.get("match_level", "POOR"),
            summary=tailored.get("summary", ""),
            skills=tailored.get("skills", []),
            experience_highlights=tailored.get("experience_highlights", []),
            improvements=tailored.get("improvements", []),
        )