from sqlalchemy.orm import Session

from app.repositories.analytics_repository import AnalyticsRepository
from app.schemas.analytics import (
    ApplicationStats,
    DashboardResponse,
    JobInsights,
    SkillGapSummary,
    WeeklyActivity,
)


class AnalyticsService:

    def __init__(self, db: Session):
        self.db = db
        self.repo = AnalyticsRepository(db)

    def get_dashboard(self, user_id: int) -> DashboardResponse:
        stats = self.repo.get_application_stats(user_id)
        insights = self.repo.get_job_insights(user_id)
        weekly = self.repo.get_weekly_activity(user_id)
        skill_gap = self.repo.get_skill_gap_summary(user_id)

        return DashboardResponse(
            application_stats=ApplicationStats(**stats),
            job_insights=JobInsights(**insights),
            weekly_activity=[WeeklyActivity(**w) for w in weekly],
            skill_gap_summary=SkillGapSummary(**skill_gap),
        )