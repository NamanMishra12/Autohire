import json

from app.llms.factory import llm_call
from app.prompts.matcher import SYSTEM_PROMPT, build_user_prompt
from app.utils.logger import logger


class MatcherAgent:
    """
    Scores a resume against a job description using LLM reasoning.
    Uses resume text + job analysis output from JobAnalyzerAgent.
    """

    async def match(
        self,
        resume_text: str,
        job_title: str,
        job_analysis: dict,
    ) -> dict:
        user_prompt = build_user_prompt(
            resume_text=resume_text,
            job_title=job_title,
            job_analysis=job_analysis,
        )

        raw = await llm_call(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.1,
            max_tokens=1000,
        )

        return self._parse_response(raw, job_title)

    @staticmethod
    def _parse_response(raw: str, job_title: str) -> dict:
        try:
            clean = (
                raw.strip()
                .removeprefix("```json")
                .removeprefix("```")
                .removesuffix("```")
                .strip()
            )
            return json.loads(clean)

        except json.JSONDecodeError:
            logger.warning(f"MatcherAgent: failed to parse LLM response for '{job_title}'")
            return {
                "score": 0,
                "match_level": "POOR",
                "matching_skills": [],
                "missing_skills": [],
                "strengths": [],
                "gaps": [],
                "recommendation": "Could not analyze match.",
            }