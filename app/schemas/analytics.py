from pydantic import BaseModel


class ApplicationStats(BaseModel):
    total: int
    pending: int
    applied: int
    interview: int
    offer: int
    rejected: int
    failed: int
    success_rate: float
    auto_apply_count: int
    manual_apply_count: int
    auto_apply_success_rate: float


class JobInsights(BaseModel):
    top_companies: list[dict]
    top_locations: list[dict]
    average_match_score: float
    score_distribution: dict
    most_common_missing_skills: list[str]
    most_common_matching_skills: list[str]


class WeeklyActivity(BaseModel):
    week: str
    applications: int
    interviews: int
    offers: int


class SkillGapSummary(BaseModel):
    total_jobs_analyzed: int
    most_missing_skills: list[dict]
    most_matching_skills: list[dict]
    recommended_skills_to_learn: list[str]


class DashboardResponse(BaseModel):
    application_stats: ApplicationStats
    job_insights: JobInsights
    weekly_activity: list[WeeklyActivity]
    skill_gap_summary: SkillGapSummary