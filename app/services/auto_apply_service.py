from datetime import datetime

from sqlalchemy.orm import Session

from app.agents.cover_letter_agent import CoverLetterAgent
from app.agents.job_analyzer import JobAnalyzerAgent
from app.agents.matcher_agent import MatcherAgent
from app.common.enums import ApplicationStatus, ApplyMethod
from app.models.application import Application
from app.repositories.application_repository import ApplicationRepository
from app.repositories.job_repository import JobRepository
from app.repositories.resume_repository import ResumeRepository
from app.repositories.user_repository import UserRepository
from app.schemas.application import ApplicationResponse
from app.tools.auto_apply import AutoApplyTool
from app.tools.job_search import JSearchScraper
from app.tools.resume_parser import ResumeParserTool
from app.utils.logger import logger
from app.core.config import settings


class AutoApplyService:
    """
    The core autonomous pipeline:
    Search → Match → Filter by threshold → Generate cover letter
    → Auto apply → Track result.
    """

    DEFAULT_THRESHOLD = 70

    def __init__(self, db: Session):
        self.db = db
        self.resume_repository = ResumeRepository(db)
        self.job_repository = JobRepository(db)
        self.application_repository = ApplicationRepository(db)
        self.user_repository = UserRepository(db)

    async def run(
        self,
        user_id: int,
        resume_id: int,
        keyword: str,
        location: str = "",
        max_jobs: int = 10,
        threshold: int = DEFAULT_THRESHOLD,
    ) -> dict:
        """
        Full autonomous pipeline.
        Returns summary of what was searched, matched, attempted, and succeeded.
        """

        summary = {
            "resume_id": resume_id,
            "keyword": keyword,
            "location": location,
            "threshold": threshold,
            "jobs_found": 0,
            "jobs_above_threshold": 0,
            "applications_attempted": 0,
            "applications_succeeded": 0,
            "applications_skipped": 0,
            "applications_failed": 0,
            "results": [],
        }

        # Step 1: Load user profile
        user = self.user_repository.get_by_id(user_id)
        if not user:
            summary["error"] = "User not found."
            return summary

        user_profile = {
            "name": user.name,
            "email": user.email,
            "phone": user.phone or "",
            "linkedin_url": user.linkedin_url or "",
            "portfolio_url": user.portfolio_url or "",
        }

        # Step 2: Load resume
        resume = self.resume_repository.get_by_id(resume_id)
        if not resume:
            summary["error"] = "Resume not found."
            return summary

        raw_text = ResumeParserTool.extract_text(resume.storage_path)
        resume_text = ResumeParserTool.clean_text(raw_text)

        # Step 3: Search jobs
        logger.info(f"AutoApply: searching '{keyword}' in '{location}'")
        scraper = JSearchScraper()
        raw_jobs = await scraper.search(
            keyword=keyword,
            location=location,
            max_results=max_jobs,
        )

        summary["jobs_found"] = len(raw_jobs)
        logger.info(f"AutoApply: found {len(raw_jobs)} jobs")

        analyzer = JobAnalyzerAgent()
        matcher = MatcherAgent()
        cover_letter_agent = CoverLetterAgent()
        auto_apply_tool = AutoApplyTool()

        for raw_job in raw_jobs:
            job_result = {
                "title": raw_job.get("title", ""),
                "company": raw_job.get("company", ""),
                "job_url": raw_job.get("job_url", ""),
                "score": 0,
                "match_level": "",
                "applied": False,
                "status": "",
                "failure_reason": "",
            }

            try:
                # Step 4: Save job to DB if not exists
                existing_job = self.job_repository.get_by_source_and_external_id(
                    source="NAUKRI",
                    external_id=raw_job.get("external_id", ""),
                )

                if existing_job:
                    job = existing_job
                else:
                    from app.models.job import Job
                    job = Job(
                        source="NAUKRI",
                        external_id=raw_job.get("external_id", ""),
                        title=raw_job.get("title", ""),
                        company=raw_job.get("company", ""),
                        location=raw_job.get("location", ""),
                        experience=raw_job.get("experience", ""),
                        salary=raw_job.get("salary", ""),
                        skills=raw_job.get("skills", ""),
                        posted_label=raw_job.get("posted_label", ""),
                        job_url=raw_job.get("job_url", ""),
                        description=raw_job.get("description", ""),
                    )
                    job = self.job_repository.create(job)

                # Step 5: Analyze job
                job_analysis = await analyzer.analyze(
                    job_title=job.title,
                    job_description=job.description or "",
                )

                # Step 6: Match resume to job
                match_result = await matcher.match(
                    resume_text=resume_text,
                    job_title=job.title,
                    job_analysis=job_analysis,
                )

                score = match_result.get("score", 0)
                match_level = match_result.get("match_level", "POOR")

                job_result["score"] = score
                job_result["match_level"] = match_level

                # Step 7: Filter by threshold
                if score < threshold:
                    job_result["status"] = "SKIPPED_LOW_SCORE"
                    job_result["failure_reason"] = f"Score {score} below threshold {threshold}"
                    summary["applications_skipped"] += 1
                    summary["results"].append(job_result)
                    continue

                summary["jobs_above_threshold"] += 1

                # Step 8: Check if already applied
                existing_app = self.application_repository.get_by_resume_and_job(
                    resume_id=resume_id,
                    job_id=job.id,
                )
                if existing_app:
                    job_result["status"] = "ALREADY_APPLIED"
                    summary["applications_skipped"] += 1
                    summary["results"].append(job_result)
                    continue

                # Step 9: Generate cover letter
                cover_letter = await cover_letter_agent.generate(
                    resume_text=resume_text,
                    job_title=job.title,
                    company=job.company or "",
                    job_analysis=job_analysis,
                    match_result=match_result,
                )
                cover_letter_text = cover_letter.get("full_cover_letter", "")

                # Step 10: Create application record
                application = Application(
                    user_id=user_id,
                    resume_id=resume_id,
                    job_id=job.id,
                    status=ApplicationStatus.APPLYING.value,
                    apply_method=ApplyMethod.AUTO.value,
                    match_score=score,
                    match_level=match_level,
                    cover_letter_used=bool(cover_letter_text),
                    auto_apply_attempted=True,
                )
                application = self.application_repository.create(application)

                summary["applications_attempted"] += 1

                # Step 11: Auto apply
                apply_result = await auto_apply_tool.apply(
                    job_url=job.job_url or "",
                    user_profile=user_profile,
                    resume_path=resume.storage_path,
                    cover_letter_text=cover_letter_text,
                )

                # Step 12: Update application record
                if apply_result["success"]:
                    application.status = ApplicationStatus.APPLIED.value
                    application.auto_apply_success = True
                    application.applied_at = datetime.utcnow()
                    summary["applications_succeeded"] += 1
                    job_result["applied"] = True
                    job_result["status"] = "APPLIED"
                else:
                    application.status = ApplicationStatus.FAILED.value
                    application.auto_apply_success = False
                    application.failure_reason = apply_result.get("failure_reason", "")
                    summary["applications_failed"] += 1
                    job_result["status"] = apply_result.get("method", "FAILED")
                    job_result["failure_reason"] = apply_result.get("failure_reason", "")

                self.application_repository.update(application)

            except Exception as exc:
                logger.exception(f"AutoApply pipeline error for job '{raw_job.get('title')}': {exc}")
                job_result["status"] = "ERROR"
                job_result["failure_reason"] = str(exc)
                summary["applications_failed"] += 1

            summary["results"].append(job_result)

        logger.info(
            f"AutoApply complete: {summary['applications_succeeded']} succeeded, "
            f"{summary['applications_failed']} failed, "
            f"{summary['applications_skipped']} skipped"
        )

        return summary