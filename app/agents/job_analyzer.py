import json

from app.llms.factory import llm_call
from app.prompts.job_analyzer import SYSTEM_PROMPT, build_user_prompt
from app.utils.logger import logger


class JobAnalyzerAgent:
    """
    Uses an LLM to extract structured data from a raw job description.
    Returns a clean dict ready for matching against resume embeddings.
    """

    async def analyze(self, job_title: str, job_description: str) -> dict:
        user_prompt = build_user_prompt(job_title, job_description)

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
            # Strip markdown fences if LLM ignores instructions
            clean = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            return json.loads(clean)

        except json.JSONDecodeError:
            logger.warning(f"JobAnalyzerAgent: failed to parse LLM response for '{job_title}'")
            return {
                "required_skills": [],
                "nice_to_have_skills": [],
                "experience_years": None,
                "employment_type": None,
                "seniority_level": None,
                "key_responsibilities": [],
                "keywords": [],
            }