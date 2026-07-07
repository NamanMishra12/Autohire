from sqlalchemy.orm import Session

from app.agents.cover_letter_agent import CoverLetterAgent
from app.agents.job_analyzer import JobAnalyzerAgent
from app.agents.matcher_agent import MatcherAgent
from app.exceptions.custome_exceptions import ResumeNotFoundException
from app.repositories.job_repository import JobRepository
from app.repositories.resume_repository import ResumeRepository
from app.schemas.cover_letter import CoverLetterResponse
from app.tools.resume_parser import ResumeParserTool
from app.utils.logger import logger


class CoverLetterService:
    """
    Orchestrates cover letter generation pipeline:
    1. Extract resume text
    2. Analyze job with LLM
    3. Score resume against job
    4. Generate personalized cover letter
    """

    def __init__(self, db: Session):
        self.db = db
        self.resume_repository = ResumeRepository(db)
        self.job_repository = JobRepository(db)

    async def generate_cover_letter(
        self,
        resume_id: int,
        job_id: int,
    ) -> CoverLetterResponse:

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
        logger.info(f"Generating cover letter for resume {resume_id} / job {job_id}")
        analyzer = JobAnalyzerAgent()
        job_analysis = await analyzer.analyze(
            job_title=job.title,
            job_description=job.description or "",
        )

        # Step 5: Match resume to job
        matcher = MatcherAgent()
        match_result = await matcher.match(
            resume_text=cleaned_text,
            job_title=job.title,
            job_analysis=job_analysis,
        )

        # Step 6: Generate cover letter
        agent = CoverLetterAgent()
        cover_letter = await agent.generate(
            resume_text=cleaned_text,
            job_title=job.title,
            company=job.company or "the company",
            job_analysis=job_analysis,
            match_result=match_result,
        )

        return CoverLetterResponse(
            resume_id=resume_id,
            job_id=job_id,
            job_title=job.title,
            company=job.company or "",
            score_before=match_result.get("score", 0),
            match_level_before=match_result.get("match_level", "POOR"),
            subject=cover_letter.get("subject", ""),
            opening_paragraph=cover_letter.get("opening_paragraph", ""),
            body_paragraph_1=cover_letter.get("body_paragraph_1", ""),
            body_paragraph_2=cover_letter.get("body_paragraph_2", ""),
            closing_paragraph=cover_letter.get("closing_paragraph", ""),
            full_cover_letter=cover_letter.get("full_cover_letter", ""),
        )