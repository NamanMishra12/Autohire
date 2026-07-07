# from sqlalchemy.orm import Session

# from app.models.job import Job
# from app.repositories.base_repository import BaseRepository


# class JobRepository(BaseRepository):

#     def __init__(self, db: Session):
#         super().__init__(db)

#     def create(self, job: Job) -> Job:
#         """
#         Persist a new job record.
#         """
#         return self.add(job)

#     def get_by_source_and_external_id(
#         self,
#         source: str,
#         external_id: str,
#     ) -> Job | None:
#         """
#         Used to detect jobs already scraped from a given source,
#         so re-running a search doesn't create duplicates.
#         """
#         return (
#             self.db.query(Job)
#             .filter(
#                 Job.source == source,
#                 Job.external_id == external_id,
#             )
#             .first()
#         )

#     def get_recent(self, limit: int = 50):
#         return (
#             self.db.query(Job)
#             .order_by(Job.created_at.desc())
#             .limit(limit)
#             .all()
#         )

from sqlalchemy.orm import Session

from app.models.job import Job
from app.repositories.base_repository import BaseRepository


class JobRepository(BaseRepository):

    def __init__(self, db: Session):
        super().__init__(db)

    def create(self, job: Job) -> Job:
        return self.add(job)

    def get_by_id(self, job_id: int) -> Job | None:
        return self.db.query(Job).filter(Job.id == job_id).first()

    def get_by_source_and_external_id(
        self,
        source: str,
        external_id: str,
    ) -> Job | None:
        return (
            self.db.query(Job)
            .filter(
                Job.source == source,
                Job.external_id == external_id,
            )
            .first()
        )

    def get_recent(self, limit: int = 50):
        return (
            self.db.query(Job)
            .order_by(Job.created_at.desc())
            .limit(limit)
            .all()
        )