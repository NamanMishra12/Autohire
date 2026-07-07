import json

from app.llms.factory import llm_call
from app.prompts.cover_letter import SYSTEM_PROMPT, build_user_prompt
from app.utils.logger import logger


class CoverLetterAgent:
    """
    Generates a personalized cover letter for a specific
    resume + job combination using LLM.
    """

    async def generate(
        self,
        resume_text: str,
        job_title: str,
        company: str,
        job_analysis: dict,
        match_result: dict,
    ) -> dict:
        user_prompt = build_user_prompt(
            resume_text=resume_text,
            job_title=job_title,
            company=company,
            job_analysis=job_analysis,
            match_result=match_result,
        )

        raw = await llm_call(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.5,
            max_tokens=2000,
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
            logger.warning(
                f"CoverLetterAgent: failed to parse LLM response for '{job_title}'"
            )
            logger.warning(f"Raw response: {raw[:300]}")
            return {
                "subject": "",
                "opening_paragraph": "",
                "body_paragraph_1": "",
                "body_paragraph_2": "",
                "closing_paragraph": "",
                "full_cover_letter": "",
            }