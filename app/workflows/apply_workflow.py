from datetime import datetime

from langgraph.graph import END, START, StateGraph

from app.agents.cover_letter_agent import CoverLetterAgent
from app.agents.job_analyzer import JobAnalyzerAgent
from app.agents.matcher_agent import MatcherAgent
from app.common.enums import ApplicationStatus, ApplyMethod
from app.tools.auto_apply import AutoApplyTool
from app.tools.job_search import JSearchScraper
from app.tools.resume_parser import ResumeParserTool
from app.utils.logger import logger
from app.workflows.state import ApplyWorkflowState


def build_apply_workflow() -> StateGraph:
    """
    Builds the autonomous apply workflow graph.

    Nodes:
        load_context
            → search_jobs
            → filter_and_match
            → generate_cover_letters
            → auto_apply
            → track_results
            → END
    """

    async def load_context(state: ApplyWorkflowState) -> ApplyWorkflowState:
        """Load user profile and resume text."""
        logger.info("ApplyWorkflow: loading context")
        try:
            from app.database.session import SessionLocal
            from app.repositories.resume_repository import ResumeRepository
            from app.repositories.user_repository import UserRepository

            db = SessionLocal()
            user_repo = UserRepository(db)
            resume_repo = ResumeRepository(db)

            user = user_repo.get_by_id(state["user_id"])
            resume = resume_repo.get_by_id(state["resume_id"])

            db.close()

            if not user or not resume:
                state["errors"].append("User or resume not found")
                return state

            state["user_profile"] = {
                "name": user.name,
                "email": user.email,
                "phone": user.phone or "",
                "linkedin_url": user.linkedin_url or "",
                "portfolio_url": user.portfolio_url or "",
            }
            state["resume_path"] = resume.storage_path

            raw = ResumeParserTool.extract_text(resume.storage_path)
            state["resume_text"] = ResumeParserTool.clean_text(raw)

            # Load session cookies
            session_cookies = {}
            for platform in ["linkedin", "indeed", "naukri"]:
                from app.repositories.user_repository import UserRepository
                db2 = SessionLocal()
                repo2 = UserRepository(db2)
                cookies = repo2.get_session_cookies(
                    user_id=state["user_id"],
                    platform=platform,
                )
                db2.close()
                if cookies:
                    session_cookies[platform] = cookies

            state["session_cookies"] = session_cookies
            logger.info(f"ApplyWorkflow: sessions for {list(session_cookies.keys())}")

        except Exception as exc:
            logger.exception(exc)
            state["errors"].append(f"load_context failed: {str(exc)}")

        return state

    async def search_jobs(state: ApplyWorkflowState) -> ApplyWorkflowState:
        """Search for jobs."""
        logger.info(f"ApplyWorkflow: searching '{state['keyword']}'")
        try:
            scraper = JSearchScraper()
            raw_jobs = await scraper.search(
                keyword=state["keyword"],
                location=state["location"],
                max_results=state["max_jobs"],
            )
            state["raw_jobs"] = raw_jobs
            state["jobs_found"] = len(raw_jobs)
            logger.info(f"ApplyWorkflow: found {len(raw_jobs)} jobs")

        except Exception as exc:
            logger.exception(exc)
            state["errors"].append(f"search_jobs failed: {str(exc)}")
            state["raw_jobs"] = []
            state["jobs_found"] = 0

        return state

    async def filter_and_match(state: ApplyWorkflowState) -> ApplyWorkflowState:
        """Analyze and score each job, filter by threshold."""
        logger.info("ApplyWorkflow: filtering and matching jobs")
        analyzer = JobAnalyzerAgent()
        matcher = MatcherAgent()
        processed = []

        from app.database.session import SessionLocal
        from app.repositories.job_repository import JobRepository
        from app.models.job import Job

        for raw_job in state["raw_jobs"]:
            try:
                db = SessionLocal()
                job_repo = JobRepository(db)

                existing = job_repo.get_by_source_and_external_id(
                    source="NAUKRI",
                    external_id=raw_job.get("external_id", ""),
                )

                if existing:
                    job = existing
                else:
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
                    job = job_repo.create(job)

                db.close()

                analysis = await analyzer.analyze(
                    job_title=job.title,
                    job_description=job.description or "",
                )

                match_result = await matcher.match(
                    resume_text=state["resume_text"],
                    job_title=job.title,
                    job_analysis=analysis,
                )

                score = match_result.get("score", 0)

                processed.append({
                    "job_id": job.id,
                    "title": job.title,
                    "company": job.company,
                    "job_url": job.job_url,
                    "score": score,
                    "match_level": match_result.get("match_level", "POOR"),
                    "matching_skills": match_result.get("matching_skills", []),
                    "missing_skills": match_result.get("missing_skills", []),
                    "analysis": analysis,
                    "match_result": match_result,
                    "description": job.description or "",
                    "above_threshold": score >= state["threshold"],
                })

                if score >= state["threshold"]:
                    state["jobs_above_threshold"] = state.get("jobs_above_threshold", 0) + 1

            except Exception as exc:
                logger.warning(f"filter_and_match: failed for '{raw_job.get('title')}': {exc}")
                continue

        state["processed_jobs"] = processed
        return state

    async def generate_cover_letters(state: ApplyWorkflowState) -> ApplyWorkflowState:
        """Generate cover letters for jobs above threshold."""
        logger.info("ApplyWorkflow: generating cover letters")
        agent = CoverLetterAgent()

        for job in state["processed_jobs"]:
            if not job.get("above_threshold"):
                job["cover_letter"] = ""
                continue

            try:
                cl = await agent.generate(
                    resume_text=state["resume_text"],
                    job_title=job["title"],
                    company=job.get("company", ""),
                    job_analysis=job.get("analysis", {}),
                    match_result=job.get("match_result", {}),
                )
                job["cover_letter"] = cl.get("full_cover_letter", "")

            except Exception as exc:
                logger.warning(f"generate_cover_letters: failed for '{job['title']}': {exc}")
                job["cover_letter"] = ""

        return state

    async def auto_apply(state: ApplyWorkflowState) -> ApplyWorkflowState:
        """Attempt auto-apply for jobs above threshold."""
        logger.info("ApplyWorkflow: auto applying")
        tool = AutoApplyTool()
        results = []

        from app.database.session import SessionLocal
        from app.repositories.application_repository import ApplicationRepository
        from app.models.application import Application

        for job in state["processed_jobs"]:
            result = {
                "title": job["title"],
                "company": job.get("company", ""),
                "job_url": job.get("job_url", ""),
                "score": job["score"],
                "match_level": job["match_level"],
                "applied": False,
                "status": "",
                "failure_reason": "",
            }

            if not job.get("above_threshold"):
                result["status"] = "SKIPPED_LOW_SCORE"
                result["failure_reason"] = f"Score {job['score']} below threshold {state['threshold']}"
                state["applications_skipped"] = state.get("applications_skipped", 0) + 1
                results.append(result)
                continue

            try:
                db = SessionLocal()
                app_repo = ApplicationRepository(db)

                existing = app_repo.get_by_resume_and_job(
                    resume_id=state["resume_id"],
                    job_id=job["job_id"],
                )

                if existing:
                    result["status"] = "ALREADY_APPLIED"
                    state["applications_skipped"] = state.get("applications_skipped", 0) + 1
                    db.close()
                    results.append(result)
                    continue

                application = Application(
                    user_id=state["user_id"],
                    resume_id=state["resume_id"],
                    job_id=job["job_id"],
                    status=ApplicationStatus.APPLYING.value,
                    apply_method=ApplyMethod.AUTO.value,
                    match_score=job["score"],
                    match_level=job["match_level"],
                    cover_letter_used=bool(job.get("cover_letter")),
                    auto_apply_attempted=True,
                )
                application = app_repo.create(application)
                db.close()

                state["applications_attempted"] = state.get("applications_attempted", 0) + 1

                apply_result = await tool.apply(
                    job_url=job.get("job_url", ""),
                    user_profile=state["user_profile"],
                    resume_path=state["resume_path"],
                    cover_letter_text=job.get("cover_letter", ""),
                    session_cookies=state["session_cookies"],
                )

                db = SessionLocal()
                app_repo2 = ApplicationRepository(db)
                app2 = app_repo2.get_by_id(application.id)

                if apply_result["success"]:
                    app2.status = ApplicationStatus.APPLIED.value
                    app2.auto_apply_success = True
                    app2.applied_at = datetime.utcnow()
                    state["applications_succeeded"] = state.get("applications_succeeded", 0) + 1
                    result["applied"] = True
                    result["status"] = "APPLIED"
                else:
                    app2.status = ApplicationStatus.FAILED.value
                    app2.auto_apply_success = False
                    app2.failure_reason = apply_result.get("failure_reason", "")
                    state["applications_failed"] = state.get("applications_failed", 0) + 1
                    result["status"] = apply_result.get("method", "FAILED")
                    result["failure_reason"] = apply_result.get("failure_reason", "")

                app_repo2.update(app2)
                db.close()

            except Exception as exc:
                logger.exception(f"auto_apply: error for '{job['title']}': {exc}")
                result["status"] = "ERROR"
                result["failure_reason"] = str(exc)
                state["applications_failed"] = state.get("applications_failed", 0) + 1

            results.append(result)

        state["results"] = results
        return state

    graph = StateGraph(ApplyWorkflowState)

    graph.add_node("load_context", load_context)
    graph.add_node("search_jobs", search_jobs)
    graph.add_node("filter_and_match", filter_and_match)
    graph.add_node("generate_cover_letters", generate_cover_letters)
    graph.add_node("auto_apply", auto_apply)

    graph.add_edge(START, "load_context")
    graph.add_edge("load_context", "search_jobs")
    graph.add_edge("search_jobs", "filter_and_match")
    graph.add_edge("filter_and_match", "generate_cover_letters")
    graph.add_edge("generate_cover_letters", "auto_apply")
    graph.add_edge("auto_apply", END)

    return graph.compile()


apply_workflow = build_apply_workflow()