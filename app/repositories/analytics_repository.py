from collections import Counter
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.job import Job


class AnalyticsRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_application_stats(self, user_id: int) -> dict:
        apps = (
            self.db.query(Application)
            .filter(Application.user_id == user_id)
            .all()
        )

        total = len(apps)
        counts = Counter(a.status.lower() for a in apps)
        auto_apps = [a for a in apps if a.apply_method == "AUTO"]
        auto_success = sum(1 for a in auto_apps if a.auto_apply_success)

        return {
            "total": total,
            "pending": counts.get("pending", 0),
            "applied": counts.get("applied", 0),
            "interview": counts.get("interview", 0),
            "offer": counts.get("offer", 0),
            "rejected": counts.get("rejected", 0),
            "failed": counts.get("failed", 0),
            "success_rate": round(
                (counts.get("interview", 0) + counts.get("offer", 0)) / total * 100, 1
            ) if total > 0 else 0.0,
            "auto_apply_count": len(auto_apps),
            "manual_apply_count": total - len(auto_apps),
            "auto_apply_success_rate": round(
                auto_success / len(auto_apps) * 100, 1
            ) if auto_apps else 0.0,
        }

    def get_job_insights(self, user_id: int) -> dict:
        apps = (
            self.db.query(Application, Job)
            .join(Job, Application.job_id == Job.id)
            .filter(Application.user_id == user_id)
            .all()
        )

        if not apps:
            return {
                "top_companies": [],
                "top_locations": [],
                "average_match_score": 0.0,
                "score_distribution": {"EXCELLENT": 0, "GOOD": 0, "FAIR": 0, "POOR": 0},
                "most_common_missing_skills": [],
                "most_common_matching_skills": [],
            }

        companies = Counter(job.company for _, job in apps if job.company)
        locations = Counter(job.location for _, job in apps if job.location)
        scores = [a.match_score for a, _ in apps if a.match_score]
        levels = Counter(a.match_level for a, _ in apps if a.match_level)

        return {
            "top_companies": [
                {"company": c, "count": n}
                for c, n in companies.most_common(5)
            ],
            "top_locations": [
                {"location": l, "count": n}
                for l, n in locations.most_common(5)
            ],
            "average_match_score": round(sum(scores) / len(scores), 1) if scores else 0.0,
            "score_distribution": {
                "EXCELLENT": levels.get("EXCELLENT", 0),
                "GOOD": levels.get("GOOD", 0),
                "FAIR": levels.get("FAIR", 0),
                "POOR": levels.get("POOR", 0),
            },
            "most_common_missing_skills": [],
            "most_common_matching_skills": [],
        }

    def get_weekly_activity(self, user_id: int) -> list[dict]:
        weeks = []
        today = datetime.utcnow()

        for i in range(7, -1, -1):
            week_start = today - timedelta(weeks=i)
            week_end = week_start + timedelta(weeks=1)
            week_label = week_start.strftime("%b %d")

            apps = (
                self.db.query(Application)
                .filter(
                    Application.user_id == user_id,
                    Application.created_at >= week_start,
                    Application.created_at < week_end,
                )
                .all()
            )

            weeks.append({
                "week": week_label,
                "applications": len(apps),
                "interviews": sum(1 for a in apps if a.status == "INTERVIEW"),
                "offers": sum(1 for a in apps if a.status == "OFFER"),
            })

        return weeks

    def get_skill_gap_summary(self, user_id: int) -> dict:
        apps = (
            self.db.query(Application, Job)
            .join(Job, Application.job_id == Job.id)
            .filter(Application.user_id == user_id)
            .all()
        )

        all_skills = []
        for _, job in apps:
            if job.skills:
                skills = [s.strip() for s in job.skills.split(",") if s.strip()]
                all_skills.extend(skills)

        skill_counts = Counter(all_skills)
        top_skills = skill_counts.most_common(10)

        return {
            "total_jobs_analyzed": len(apps),
            "most_missing_skills": [
                {"skill": s, "count": c} for s, c in top_skills[:5]
            ],
            "most_matching_skills": [
                {"skill": s, "count": c} for s, c in top_skills[5:]
            ],
            "recommended_skills_to_learn": [s for s, _ in top_skills[:5]],
        }