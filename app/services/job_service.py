# from sqlalchemy.orm import Session

# from app.common.enums import JobSource
# from app.models.job import Job
# from app.repositories.job_repository import JobRepository
# from app.schemas.job import JobResponse
# from app.tools.job_search import NaukriScraper
# from app.utils.logger import logger


# class JobService:
#     """
#     Orchestrates job search scraping and persistence.
#     Deduplicates against existing jobs by (source, external_id).
#     """

#     def __init__(self, db: Session):
#         self.db = db
#         self.job_repository = JobRepository(db)

#     async def search_naukri(
#         self,
#         keyword: str,
#         location: str = "",
#         max_results: int = 20,
#     ) -> list[JobResponse]:
#         async with NaukriScraper() as scraper:
#             raw_jobs = await scraper.search(
#                 keyword=keyword,
#                 location=location,
#                 max_results=max_results,
#             )

#         saved_jobs = []

#         for raw_job in raw_jobs:
#             if not raw_job.get("external_id"):
#                 continue

#             existing = self.job_repository.get_by_source_and_external_id(
#                 source=JobSource.NAUKRI.value,
#                 external_id=raw_job["external_id"],
#             )

#             if existing:
#                 saved_jobs.append(existing)
#                 continue

#             job = Job(
#                 source=JobSource.NAUKRI.value,
#                 external_id=raw_job["external_id"],
#                 title=raw_job["title"],
#                 company=raw_job["company"],
#                 location=raw_job["location"],
#                 experience=raw_job["experience"],
#                 skills=raw_job["skills"],
#                 posted_label=raw_job["posted_label"],
#                 job_url=raw_job["job_url"],
#                 description=raw_job["description"],
#             )

#             try:
#                 job = self.job_repository.create(job)
#             except Exception as exc:
#                 logger.warning(f"Skipping job due to insert error: {exc}")
#                 continue

#             saved_jobs.append(job)

#         return [JobResponse.model_validate(job) for job in saved_jobs]

from sqlalchemy.orm import Session

from app.common.enums import JobSource
from app.models.job import Job
from app.repositories.job_repository import JobRepository
from app.schemas.job import JobResponse
# from app.tools.job_search import NaukriScraper
from app.utils.logger import logger
from app.tools.job_search import JSearchScraper


class JobService:

    def __init__(self, db: Session):
        self.db = db
        self.job_repository = JobRepository(db)

    async def search_naukri(  # keep name for now, swap later
        self,
        keyword: str,
        location: str = "",
        max_results: int = 20,
    ) -> list[JobResponse]:

        scraper = JSearchScraper()  # changed
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