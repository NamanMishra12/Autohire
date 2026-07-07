from sqlalchemy.orm import Session

from app.agents.job_analyzer import JobAnalyzerAgent
from app.common.enums import JobSource
from app.exceptions.custome_exceptions import ResumeNotFoundException
from app.models.job import Job
from app.repositories.job_repository import JobRepository
from app.schemas.job import JobAnalysisResponse, JobResponse
from app.tools.job_search import JSearchScraper
from app.utils.logger import logger


class JobService:

    def __init__(self, db: Session):
        self.db = db
        self.job_repository = JobRepository(db)

    async def search_naukri(
        self,
        keyword: str,
        location: str = "",
        max_results: int = 20,
    ) -> list[JobResponse]:

        scraper = JSearchScraper()
        raw_jobs = await scraper.search(
            keyword=keyword,
            location=location,
            max_results=max_results,
        )

        saved_jobs = []

        for raw_job in raw_jobs:
            if not raw_job.get("external_id"):
                continue

            existing = self.job_repository.get_by_source_and_external_id(
                source=JobSource.NAUKRI.value,
                external_id=raw_job["external_id"],
            )

            if existing:
                saved_jobs.append(existing)
                continue

            job = Job(
                source=JobSource.NAUKRI.value,
                external_id=raw_job["external_id"],
                title=raw_job["title"],
                company=raw_job["company"],
                location=raw_job["location"],
                experience=raw_job["experience"],
                salary=raw_job.get("salary", ""),
                skills=raw_job["skills"],
                posted_label=raw_job["posted_label"],
                job_url=raw_job["job_url"],
                description=raw_job["description"],
            )

            try:
                job = self.job_repository.create(job)
            except Exception as exc:
                logger.warning(f"Skipping job due to insert error: {exc}")
                continue

            saved_jobs.append(job)

        return [JobResponse.model_validate(job) for job in saved_jobs]

    async def analyze_job(self, job_id: int) -> JobAnalysisResponse:
        job = self.job_repository.get_by_id(job_id)

        if not job:
            raise ResumeNotFoundException(
                message=f"Job with id {job_id} not found."
            )

        agent = JobAnalyzerAgent()

        analysis = await agent.analyze(
            job_title=job.title,
            job_description=job.description or "",
        )

        return JobAnalysisResponse(
            job_id=job.id,
            title=job.title,
            analysis=analysis,
        )