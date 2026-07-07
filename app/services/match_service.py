from sqlalchemy.orm import Session

from app.agents.job_analyzer import JobAnalyzerAgent
from app.agents.matcher_agent import MatcherAgent
from app.exceptions.custome_exceptions import ResumeNotFoundException
from app.repositories.job_repository import JobRepository
from app.repositories.resume_repository import ResumeRepository
from app.schemas.match import MatchResponse
from app.tools.resume_parser import ResumeParserTool
from app.utils.logger import logger


class MatchService:
    """
    Orchestrates resume-to-job matching:
    1. Load resume file and extract text
    2. Analyze job description with LLM
    3. Score resume against job with LLM
    4. Return structured match result
    """

    def __init__(self, db: Session):
        self.db = db
        self.resume_repository = ResumeRepository(db)
        self.job_repository = JobRepository(db)

    async def match_resume_to_job(
        self,
        resume_id: int,
        job_id: int,
    ) -> MatchResponse:

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

        # Step 4: Analyze job with LLM
        logger.info(f"Analyzing job {job_id} for match with resume {resume_id}")
        analyzer = JobAnalyzerAgent()
        job_analysis = await analyzer.analyze(
            job_title=job.title,
            job_description=job.description or "",
        )

        # Step 5: Score resume against job
        logger.info(f"Scoring resume {resume_id} against job {job_id}")
        matcher = MatcherAgent()
        match_result = await matcher.match(
            resume_text=cleaned_text,
            job_title=job.title,
            job_analysis=job_analysis,
        )

        return MatchResponse(
            resume_id=resume_id,
            job_id=job_id,
            job_title=job.title,
            score=match_result.get("score", 0),
            match_level=match_result.get("match_level", "POOR"),
            matching_skills=match_result.get("matching_skills", []),
            missing_skills=match_result.get("missing_skills", []),
            strengths=match_result.get("strengths", []),
            gaps=match_result.get("gaps", []),
            recommendation=match_result.get("recommendation", ""),
        )