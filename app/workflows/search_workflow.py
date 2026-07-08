from langgraph.graph import END, START, StateGraph

from app.agents.job_analyzer import JobAnalyzerAgent
from app.agents.matcher_agent import MatcherAgent
from app.tools.job_search import JSearchScraper
from app.tools.resume_parser import ResumeParserTool
from app.utils.logger import logger
from app.workflows.state import SearchWorkflowState


def build_search_workflow() -> StateGraph:
    """
    Builds the job search workflow graph.

    Nodes:
        load_resume → search_jobs → analyze_jobs → match_jobs → END
    """

    async def load_resume(state: SearchWorkflowState) -> SearchWorkflowState:
        """Extract and clean resume text from storage path."""
        logger.info("SearchWorkflow: loading resume")
        try:
            from app.database.session import SessionLocal
            from app.repositories.resume_repository import ResumeRepository

            db = SessionLocal()
            repo = ResumeRepository(db)
            resume = repo.get_by_id(state["resume_id"])
            db.close()

            if not resume:
                state["errors"].append(f"Resume {state['resume_id']} not found")
                state["resume_text"] = ""
                return state

            raw = ResumeParserTool.extract_text(resume.storage_path)
            state["resume_text"] = ResumeParserTool.clean_text(raw)

        except Exception as exc:
            logger.exception(exc)
            state["errors"].append(f"load_resume failed: {str(exc)}")
            state["resume_text"] = ""

        return state

    async def search_jobs(state: SearchWorkflowState) -> SearchWorkflowState:
        """Search for jobs using JSearch API."""
        logger.info(f"SearchWorkflow: searching '{state['keyword']}' in '{state['location']}'")
        try:
            scraper = JSearchScraper()
            raw_jobs = await scraper.search(
                keyword=state["keyword"],
                location=state["location"],
                max_results=state["max_results"],
            )
            state["raw_jobs"] = raw_jobs
            logger.info(f"SearchWorkflow: found {len(raw_jobs)} jobs")

        except Exception as exc:
            logger.exception(exc)
            state["errors"].append(f"search_jobs failed: {str(exc)}")
            state["raw_jobs"] = []

        return state

    async def analyze_jobs(state: SearchWorkflowState) -> SearchWorkflowState:
        """Run LLM job analyzer on each job description."""
        logger.info(f"SearchWorkflow: analyzing {len(state['raw_jobs'])} jobs")
        analyzer = JobAnalyzerAgent()
        analyzed = []

        for job in state["raw_jobs"]:
            try:
                analysis = await analyzer.analyze(
                    job_title=job.get("title", ""),
                    job_description=job.get("description", ""),
                )
                analyzed.append({**job, "analysis": analysis})

            except Exception as exc:
                logger.warning(f"analyze_jobs: failed for '{job.get('title')}': {exc}")
                analyzed.append({**job, "analysis": {}})

        state["analyzed_jobs"] = analyzed
        return state

    async def match_jobs(state: SearchWorkflowState) -> SearchWorkflowState:
        """Score resume against each analyzed job."""
        logger.info(f"SearchWorkflow: matching resume against {len(state['analyzed_jobs'])} jobs")
        matcher = MatcherAgent()
        matched = []

        for job in state["analyzed_jobs"]:
            try:
                match_result = await matcher.match(
                    resume_text=state["resume_text"],
                    job_title=job.get("title", ""),
                    job_analysis=job.get("analysis", {}),
                )
                matched.append({
                    **job,
                    "score": match_result.get("score", 0),
                    "match_level": match_result.get("match_level", "POOR"),
                    "matching_skills": match_result.get("matching_skills", []),
                    "missing_skills": match_result.get("missing_skills", []),
                    "recommendation": match_result.get("recommendation", ""),
                })

            except Exception as exc:
                logger.warning(f"match_jobs: failed for '{job.get('title')}': {exc}")
                matched.append({**job, "score": 0, "match_level": "POOR"})

        state["matched_jobs"] = sorted(
            matched,
            key=lambda x: x.get("score", 0),
            reverse=True,
        )
        return state

    graph = StateGraph(SearchWorkflowState)

    graph.add_node("load_resume", load_resume)
    graph.add_node("search_jobs", search_jobs)
    graph.add_node("analyze_jobs", analyze_jobs)
    graph.add_node("match_jobs", match_jobs)

    graph.add_edge(START, "load_resume")
    graph.add_edge("load_resume", "search_jobs")
    graph.add_edge("search_jobs", "analyze_jobs")
    graph.add_edge("analyze_jobs", "match_jobs")
    graph.add_edge("match_jobs", END)

    return graph.compile()


search_workflow = build_search_workflow()