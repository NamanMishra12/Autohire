from __future__ import annotations

import asyncio
from pathlib import Path

from playwright.async_api import async_playwright

from app.utils.logger import logger


class AutoApplyTool:
    """
    Handles browser automation for job application form filling.
    Uses a tiered strategy:
    - Tier 1: Direct company career pages (standard form fields)
    - Tier 2: Flag as manual review if form is too complex
    """

    UNSUPPORTED_DOMAINS = [
        "linkedin.com",
        "naukri.com",
        "indeed.com",
        "glassdoor.com",
        "wellfound.com",
    ]

    HUMAN_DELAY_MS = 500

    async def apply(
        self,
        job_url: str,
        user_profile: dict,
        resume_path: str,
        cover_letter_text: str = "",
    ) -> dict:
        """
        Attempts to auto-apply to a job URL.
        Returns result dict with success, method, and failure_reason.
        """

        if self._is_unsupported_domain(job_url):
            return {
                "success": False,
                "method": "SKIPPED",
                "failure_reason": f"Platform requires authenticated session: {job_url}",
            }

        try:
            result = await self._apply_direct(
                job_url=job_url,
                user_profile=user_profile,
                resume_path=resume_path,
                cover_letter_text=cover_letter_text,
            )
            return result

        except Exception as exc:
            logger.warning(f"AutoApply failed for {job_url}: {exc}")
            return {
                "success": False,
                "method": "DIRECT",
                "failure_reason": str(exc),
            }

    def _is_unsupported_domain(self, url: str) -> bool:
        return any(domain in url for domain in self.UNSUPPORTED_DOMAINS)

    async def _apply_direct(
        self,
        job_url: str,
        user_profile: dict,
        resume_path: str,
        cover_letter_text: str,
    ) -> dict:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                )
            )
            page = await context.new_page()

            try:
                await page.goto(job_url, timeout=30000)
                await page.wait_for_timeout(2000)

                filled = await self._fill_standard_fields(
                    page=page,
                    user_profile=user_profile,
                    resume_path=resume_path,
                    cover_letter_text=cover_letter_text,
                )

                if not filled:
                    return {
                        "success": False,
                        "method": "DIRECT",
                        "failure_reason": "Could not detect standard application form fields.",
                    }

                await page.wait_for_timeout(1000)

                submitted = await self._submit_form(page)

                if submitted:
                    logger.info(f"AutoApply succeeded: {job_url}")
                    return {
                        "success": True,
                        "method": "DIRECT",
                        "failure_reason": None,
                    }

                return {
                    "success": False,
                    "method": "DIRECT",
                    "failure_reason": "Form submit button not found.",
                }

            finally:
                await browser.close()

    async def _fill_standard_fields(
        self,
        page,
        user_profile: dict,
        resume_path: str,
        cover_letter_text: str,
    ) -> bool:
        """
        Tries to fill common application form fields.
        Returns True if at least resume upload or name field was filled.
        """
        filled_any = False

        field_map = {
            "name": user_profile.get("name", ""),
            "full_name": user_profile.get("name", ""),
            "first_name": user_profile.get("name", "").split()[0] if user_profile.get("name") else "",
            "last_name": user_profile.get("name", "").split()[-1] if user_profile.get("name") else "",
            "email": user_profile.get("email", ""),
            "phone": user_profile.get("phone", ""),
            "linkedin": user_profile.get("linkedin_url", ""),
            "portfolio": user_profile.get("portfolio_url", ""),
            "website": user_profile.get("portfolio_url", ""),
            "cover_letter": cover_letter_text,
            "coverletter": cover_letter_text,
            "message": cover_letter_text,
        }

        for field_name, value in field_map.items():
            if not value:
                continue

            selectors = [
                f"input[name*='{field_name}' i]",
                f"input[placeholder*='{field_name}' i]",
                f"input[id*='{field_name}' i]",
                f"textarea[name*='{field_name}' i]",
                f"textarea[placeholder*='{field_name}' i]",
                f"textarea[id*='{field_name}' i]",
            ]

            for selector in selectors:
                try:
                    el = page.locator(selector).first
                    count = await el.count()
                    if count > 0:
                        await el.fill(value)
                        await page.wait_for_timeout(self.HUMAN_DELAY_MS)
                        filled_any = True
                        break
                except Exception:
                    continue

        # Resume upload
        if resume_path and Path(resume_path).exists():
            upload_selectors = [
                "input[type='file']",
                "input[name*='resume' i]",
                "input[name*='cv' i]",
                "input[accept*='pdf' i]",
            ]
            for selector in upload_selectors:
                try:
                    el = page.locator(selector).first
                    count = await el.count()
                    if count > 0:
                        await el.set_input_files(resume_path)
                        await page.wait_for_timeout(self.HUMAN_DELAY_MS)
                        filled_any = True
                        break
                except Exception:
                    continue

        return filled_any

    async def _submit_form(self, page) -> bool:
        submit_selectors = [
            "button[type='submit']",
            "input[type='submit']",
            "button:has-text('Submit')",
            "button:has-text('Apply')",
            "button:has-text('Send Application')",
            "button:has-text('Apply Now')",
        ]

        for selector in submit_selectors:
            try:
                el = page.locator(selector).first
                count = await el.count()
                if count > 0:
                    await el.click()
                    await page.wait_for_timeout(2000)
                    return True
            except Exception:
                continue

        return False