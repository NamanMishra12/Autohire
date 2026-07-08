from __future__ import annotations

import asyncio
from pathlib import Path

from playwright.async_api import async_playwright

from app.utils.logger import logger


class AutoApplyTool:
    """
    Handles browser automation for job application form filling.

    Tier 1: Authenticated session apply (LinkedIn, Indeed, Naukri)
             Uses user's own session cookies — applies as real user.
    Tier 2: Direct company career page apply (standard form fields)
    Tier 3: Flag as manual review if form is too complex
    """

    PLATFORM_DOMAINS = {
        "linkedin": "linkedin.com",
        "indeed": "indeed.com",
        "naukri": "naukri.com",
    }

    HUMAN_DELAY_MS = 800

    async def apply(
        self,
        job_url: str,
        user_profile: dict,
        resume_path: str,
        cover_letter_text: str = "",
        session_cookies: dict | None = None,
    ) -> dict:
        """
        Attempts to auto-apply to a job URL.
        session_cookies = {"linkedin": [...], "indeed": [...], "naukri": [...]}
        """
        platform = self._detect_platform(job_url)

        # Tier 1: Authenticated session apply
        if platform and session_cookies and session_cookies.get(platform):
            logger.info(f"AutoApply: using authenticated session for {platform}")
            return await self._apply_with_session(
                platform=platform,
                job_url=job_url,
                user_profile=user_profile,
                resume_path=resume_path,
                cover_letter_text=cover_letter_text,
                cookies=session_cookies[platform],
            )

        # Tier 2: Direct apply on company career page
        if not platform:
            return await self._apply_direct(
                job_url=job_url,
                user_profile=user_profile,
                resume_path=resume_path,
                cover_letter_text=cover_letter_text,
            )

        # Platform detected but no cookies — skip
        return {
            "success": False,
            "method": "SKIPPED",
            "failure_reason": f"{platform.title()} session not configured. Upload cookies first via /users/session-cookies.",
        }

    def _detect_platform(self, url: str) -> str | None:
        for platform, domain in self.PLATFORM_DOMAINS.items():
            if domain in url:
                return platform
        return None

    async def _apply_with_session(
        self,
        platform: str,
        job_url: str,
        user_profile: dict,
        resume_path: str,
        cover_letter_text: str,
        cookies: list,
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

            # Inject session cookies
            await context.add_cookies(cookies)

            page = await context.new_page()

            try:
                if platform == "linkedin":
                    return await self._apply_linkedin(
                        page=page,
                        job_url=job_url,
                        user_profile=user_profile,
                        resume_path=resume_path,
                        cover_letter_text=cover_letter_text,
                    )

                if platform == "indeed":
                    return await self._apply_indeed(
                        page=page,
                        job_url=job_url,
                        user_profile=user_profile,
                        resume_path=resume_path,
                    )

                if platform == "naukri":
                    return await self._apply_naukri(
                        page=page,
                        job_url=job_url,
                    )

                return {
                    "success": False,
                    "method": "SESSION",
                    "failure_reason": f"No session apply handler for {platform}",
                }

            finally:
                await browser.close()

    async def _apply_linkedin(
        self,
        page,
        job_url: str,
        user_profile: dict,
        resume_path: str,
        cover_letter_text: str,
    ) -> dict:
        try:
            await page.goto(job_url, timeout=30000)
            await page.wait_for_timeout(2000)

            # Click Easy Apply button
            easy_apply = page.locator("button.jobs-apply-button").first
            count = await easy_apply.count()

            if not count:
                easy_apply = page.locator("button:has-text('Easy Apply')").first
                count = await easy_apply.count()

            if not count:
                return {
                    "success": False,
                    "method": "LINKEDIN",
                    "failure_reason": "Easy Apply button not found — job may require external apply.",
                }

            await easy_apply.click()
            await page.wait_for_timeout(2000)

            # Handle multi-step Easy Apply modal
            max_steps = 8
            for step in range(max_steps):

                # Fill cover letter if field exists
                if cover_letter_text:
                    cl_field = page.locator("textarea[id*='cover-letter'], textarea[placeholder*='cover letter' i]").first
                    if await cl_field.count() > 0:
                        await cl_field.fill(cover_letter_text)
                        await page.wait_for_timeout(self.HUMAN_DELAY_MS)

                # Upload resume if file input exists
                if resume_path and Path(resume_path).exists():
                    file_input = page.locator("input[type='file']").first
                    if await file_input.count() > 0:
                        await file_input.set_input_files(resume_path)
                        await page.wait_for_timeout(self.HUMAN_DELAY_MS)

                # Check for Submit button
                submit_btn = page.locator("button:has-text('Submit application')").first
                if await submit_btn.count() > 0:
                    await submit_btn.click()
                    await page.wait_for_timeout(2000)
                    logger.info(f"LinkedIn Easy Apply submitted: {job_url}")
                    return {
                        "success": True,
                        "method": "LINKEDIN",
                        "failure_reason": None,
                    }

                # Click Next to proceed through steps
                next_btn = page.locator("button:has-text('Next'), button:has-text('Continue'), button:has-text('Review')").first
                if await next_btn.count() > 0:
                    await next_btn.click()
                    await page.wait_for_timeout(1500)
                    continue

                break

            return {
                "success": False,
                "method": "LINKEDIN",
                "failure_reason": "Could not complete LinkedIn Easy Apply flow.",
            }

        except Exception as exc:
            return {
                "success": False,
                "method": "LINKEDIN",
                "failure_reason": str(exc),
            }

    async def _apply_indeed(
        self,
        page,
        job_url: str,
        user_profile: dict,
        resume_path: str,
    ) -> dict:
        try:
            await page.goto(job_url, timeout=30000)
            await page.wait_for_timeout(2000)

            # Click Apply Now
            apply_btn = page.locator("button:has-text('Apply now'), a:has-text('Apply now')").first
            if await apply_btn.count() == 0:
                return {
                    "success": False,
                    "method": "INDEED",
                    "failure_reason": "Apply button not found on Indeed job page.",
                }

            await apply_btn.click()
            await page.wait_for_timeout(2000)

            # Handle multi-step Indeed apply
            max_steps = 6
            for step in range(max_steps):

                # Upload resume
                if resume_path and Path(resume_path).exists():
                    file_input = page.locator("input[type='file']").first
                    if await file_input.count() > 0:
                        await file_input.set_input_files(resume_path)
                        await page.wait_for_timeout(self.HUMAN_DELAY_MS)

                # Submit
                submit_btn = page.locator("button:has-text('Submit'), button[type='submit']").first
                if await submit_btn.count() > 0:
                    await submit_btn.click()
                    await page.wait_for_timeout(2000)
                    return {
                        "success": True,
                        "method": "INDEED",
                        "failure_reason": None,
                    }

                # Next step
                next_btn = page.locator("button:has-text('Continue'), button:has-text('Next')").first
                if await next_btn.count() > 0:
                    await next_btn.click()
                    await page.wait_for_timeout(1500)
                    continue

                break

            return {
                "success": False,
                "method": "INDEED",
                "failure_reason": "Could not complete Indeed apply flow.",
            }

        except Exception as exc:
            return {
                "success": False,
                "method": "INDEED",
                "failure_reason": str(exc),
            }

    async def _apply_naukri(
        self,
        page,
        job_url: str,
    ) -> dict:
        try:
            await page.goto(job_url, timeout=30000)
            await page.wait_for_timeout(2000)

            apply_btn = page.locator("button:has-text('Apply'), a:has-text('Apply')").first
            if await apply_btn.count() == 0:
                return {
                    "success": False,
                    "method": "NAUKRI",
                    "failure_reason": "Apply button not found on Naukri job page.",
                }

            await apply_btn.click()
            await page.wait_for_timeout(2000)

            # Naukri one-click apply confirmation
            confirm_btn = page.locator("button:has-text('Apply'), button:has-text('Confirm')").first
            if await confirm_btn.count() > 0:
                await confirm_btn.click()
                await page.wait_for_timeout(1500)
                return {
                    "success": True,
                    "method": "NAUKRI",
                    "failure_reason": None,
                }

            return {
                "success": False,
                "method": "NAUKRI",
                "failure_reason": "Could not confirm Naukri application.",
            }

        except Exception as exc:
            return {
                "success": False,
                "method": "NAUKRI",
                "failure_reason": str(exc),
            }

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

                await self._click_apply_button(page)
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

    async def _click_apply_button(self, page) -> bool:
        apply_selectors = [
            "a:has-text('Apply Now')",
            "a:has-text('Apply')",
            "button:has-text('Apply Now')",
            "button:has-text('Apply')",
            "a[href*='apply']",
            ".apply-button",
            "#apply-button",
            "[data-automation='apply-button']",
            "[data-testid='apply-button']",
        ]

        for selector in apply_selectors:
            try:
                el = page.locator(selector).first
                if await el.count() > 0:
                    await el.click()
                    await page.wait_for_timeout(1500)
                    return True
            except Exception:
                continue

        return False

    async def _fill_standard_fields(
        self,
        page,
        user_profile: dict,
        resume_path: str,
        cover_letter_text: str,
    ) -> bool:
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
                    if await el.count() > 0:
                        await el.fill(value)
                        await page.wait_for_timeout(self.HUMAN_DELAY_MS)
                        filled_any = True
                        break
                except Exception:
                    continue

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
                    if await el.count() > 0:
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
                if await el.count() > 0:
                    await el.click()
                    await page.wait_for_timeout(2000)
                    return True
            except Exception:
                continue

        return False