from __future__ import annotations

from playwright.async_api import Browser, Page, async_playwright


class BaseScraperTool:
    """
    Shared Playwright browser lifecycle management for site-specific
    scrapers. Subclasses implement their own search() method.

    Usage:
        async with SomeScraper() as scraper:
            jobs = await scraper.search("python developer", "bangalore")
    """

    HEADLESS = True

    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )

    def __init__(self):
        self._playwright = None
        self._browser: Browser | None = None

    async def __aenter__(self):
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=self.HEADLESS,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._browser:
            await self._browser.close()

        if self._playwright:
            await self._playwright.stop()

    async def new_page(self) -> Page:
        context = await self._browser.new_context(user_agent=self.USER_AGENT)
        return await context.new_page()