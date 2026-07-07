import json

from app.llms.factory import llm_call
from app.prompts.resume_tailor import SYSTEM_PROMPT, build_user_prompt
from app.utils.logger import logger


class ResumeTailorAgent:
    """
    Rewrites resume content to better match a specific job description.
    Uses match analysis output to know what to highlight and what to address.
    """

    async def tailor(
        self,
        resume_text: str,
        job_title: str,
        job_analysis: dict,
        match_result: dict,
    ) -> dict:
        user_prompt = build_user_prompt(
            resume_text=resume_text,
            job_title=job_title,
            job_analysis=job_analysis,
            match_result=match_result,
        )

        raw = await llm_call(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.4,
            max_tokens=4000,
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
            logger.warning(f"ResumeTailorAgent: failed to parse LLM response for '{job_title}'")
            logger.warning(f"Raw response was: {raw[:500]}")
            return {
                "summary": "",
                "skills": [],
                "experience_highlights": [],
                "improvements": [],
                "tailored_resume_text": "",
            }

        except json.JSONDecodeError:
            logger.warning(f"ResumeTailorAgent: failed to parse LLM response for '{job_title}'")
            return {
                "summary": "",
                "skills": [],
                "experience_highlights": [],
                "improvements": [],
                "tailored_resume_text": "",
            }