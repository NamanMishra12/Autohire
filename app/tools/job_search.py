# # from __future__ import annotations

# # import re
# # from urllib.parse import quote

# # from app.tools.scraper import BaseScraperTool
# # from app.utils.logger import logger


# # class NaukriScraper(BaseScraperTool):
# #     """
# #     Scrapes job listings from Naukri.com's public search results.

# #     NOTE: Naukri's HTML structure changes periodically. If this
# #     returns zero results, open a search page in a real browser,
# #     right-click a job card -> Inspect, and update SELECTORS below
# #     to match the current class names.
# #     """

# #     BASE_URL = "https://www.naukri.com"

# #     SELECTORS = {
# #     "job_card": "div.cust-job-tuple",
# #     "title": "a.title",
# #     "company": "a.comp-name",
# #     "location": ".locWdth",
# #     "experience": ".expwdth",
# #     "skills": "ul.tags-gt li",
# #     "posted": ".job-post-day",
# # }

# #     async def search(
# #         self,
# #         keyword: str,
# #         location: str = "",
# #         max_results: int = 20,
# #     ) -> list[dict]:
# #         search_url = self._build_search_url(keyword, location)
# #         logger.debug(f"Naukri URL: {search_url}")

# #         page = await self.new_page()

# #         try:
# #             await page.goto(search_url, timeout=30000)
# #             await page.wait_for_timeout(3000)
# #             await page.screenshot(path="naukri_debug.png", full_page=True)
# #             await page.wait_for_selector(
# #                 "div.cust-job-tuple a.title",
# #                 timeout=15000,
# #             )
# #             await page.wait_for_timeout(2000)

# #             cards = await page.query_selector_all(self.SELECTORS["job_card"])
# #             logger.debug(f"Cards found: {len(cards)}")

# #             results = []

# #             for i, card in enumerate(cards[:max_results]):
# #                 job = await self._extract_job(card)
# #                 logger.debug(f"Card {i}: {job}")

# #                 if job:
# #                     results.append(job)
# #             logger.debug(f"Total extracted: {len(results)}")
# #             return results

# #         except Exception as exc:
# #             logger.warning(f"Naukri scrape failed or returned no results: {exc}")
# #             return []

# #         finally:
# #             await page.close()

# #     def _build_search_url(self, keyword: str, location: str) -> str:
# #         slug = re.sub(r"\s+", "-", keyword.strip().lower())

# #         url = f"{self.BASE_URL}/{slug}-jobs"

# #         params = [f"k={quote(keyword)}"]

# #         if location:
# #             params.append(f"l={quote(location)}")

# #         return f"{url}?{'&'.join(params)}"

# #     async def _extract_job(self, card) -> dict | None:
# #         title_el = await card.query_selector(self.SELECTORS["title"])

# #         if not title_el:
# #             return None

# #         title = (await title_el.inner_text()).strip()
# #         job_url = await title_el.get_attribute("href")

# #         company_el = await card.query_selector(self.SELECTORS["company"])
# #         company = (await company_el.inner_text()).strip() if company_el else ""

# #         location_el = await card.query_selector(self.SELECTORS["location"])
# #         location_text = (
# #             (await location_el.inner_text()).strip() if location_el else ""
# #         )

# #         experience_el = await card.query_selector(self.SELECTORS["experience"])
# #         experience = (
# #             (await experience_el.inner_text()).strip() if experience_el else ""
# #         )

# #         posted_el = await card.query_selector(self.SELECTORS["posted"])
# #         posted_label = (
# #             (await posted_el.inner_text()).strip() if posted_el else ""
# #         )

# #         skill_elements = await card.query_selector_all(self.SELECTORS["skills"])
# #         skills = (
# #             ", ".join([(await el.inner_text()).strip() for el in skill_elements])
# #             if skill_elements
# #             else ""
# #         )

# #         external_id = self._extract_external_id(job_url)

# #         return {
# #             "external_id": external_id,
# #             "title": title,
# #             "company": company,
# #             "location": location_text,
# #             "experience": experience,
# #             "skills": skills,
# #             "posted_label": posted_label,
# #             "job_url": job_url,
# #             "description": "",
# #         }

# #     @staticmethod
# #     def _extract_external_id(job_url: str | None) -> str:
# #         if not job_url:
# #             return ""

# #         match = re.search(r"-(\d+)(?:\?|$)", job_url)
# #         return match.group(1) if match else job_url


# from __future__ import annotations

# import re
# import httpx

# from app.utils.logger import logger


# class NaukriScraper:
#     """
#     Hits Naukri's internal JSON search API directly.
#     No browser needed — faster and not blocked by Akamai.
#     """

#     API_URL = "https://www.naukri.com/jobapi/v3/search"

#     HEADERS = {
#     "User-Agent": (
#         "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#         "AppleWebKit/537.36 (KHTML, like Gecko) "
#         "Chrome/124.0.0.0 Safari/537.36"
#     ),
#     "Accept": "application/json",
#     "Accept-Language": "en-US,en;q=0.9",
#     "Accept-Encoding": "gzip, deflate, br",
#     "Referer": "https://www.naukri.com/",
#     "Origin": "https://www.naukri.com",
#     "appid": "109",
#     "systemid": "109",
#     "gid": "LOCATION,INDUSTRY,EDUCATION,FAREA_ROLE",
#     "Connection": "keep-alive",
#     "Sec-Fetch-Dest": "empty",
#     "Sec-Fetch-Mode": "cors",
#     "Sec-Fetch-Site": "same-origin",
#     "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124"',
#     "sec-ch-ua-mobile": "?0",
#     "sec-ch-ua-platform": '"Windows"',
# }

#     async def search(
#         self,
#         keyword: str,
#         location: str = "",
#         max_results: int = 20,
#     ) -> list[dict]:
#         params = {
#             "noOfResults": max_results,
#             "urlType": "search_by_keyword",
#             "searchType": "adv",
#             "keyword": keyword,
#             "pageNo": 1,
#             "k": keyword,
#             "seoKey": f"{keyword.lower().replace(' ', '-')}-jobs",
#             "src": "jobsearchDesk",
#             "latLong": "",
#         }

#         if location:
#             params["location"] = location
#             params["l"] = location

#         logger.debug(f"Naukri API params: {params}")

#         try:
#             async with httpx.AsyncClient(
#                 headers=self.HEADERS,
#                 timeout=20.0,
#                 follow_redirects=True,
#             ) as client:
#                 response = await client.get(self.API_URL, params=params)

#             logger.debug(f"Naukri API status: {response.status_code}")

#             if response.status_code != 200:
#                 logger.warning(f"Naukri API returned {response.status_code}")
#                 return []

#             data = response.json()
#             job_details = data.get("jobDetails", [])

#             logger.debug(f"Raw jobs from API: {len(job_details)}")

#             results = []

#             for job in job_details:
#                 parsed = self._parse_job(job)
#                 if parsed:
#                     results.append(parsed)

#             return results

#         except Exception as exc:
#             logger.warning(f"Naukri API call failed: {exc}")
#             return []

#     def _parse_job(self, job: dict) -> dict | None:
#         title = job.get("title", "").strip()

#         if not title:
#             return None

#         external_id = str(job.get("jobId", ""))

#         company_info = job.get("companyDetail", {})
#         company = company_info.get("name", "").strip()

#         placeholders = job.get("placeholders", [])
#         experience = ""
#         location = ""
#         salary = ""

#         for p in placeholders:
#             ptype = p.get("type", "")
#             label = p.get("label", "")
#             if ptype == "experience":
#                 experience = label
#             elif ptype == "location":
#                 location = label
#             elif ptype == "salary":
#                 salary = label

#         skills_list = job.get("tagsAndSkills", "")
#         skills = skills_list if isinstance(skills_list, str) else ", ".join(skills_list)

#         posted_label = job.get("footerPlaceholderLabel", "")

#         job_url = job.get("jdURL", "") or job.get("staticUrl", "")

#         return {
#             "external_id": external_id,
#             "title": title,
#             "company": company,
#             "location": location,
#             "experience": experience,
#             "salary": salary,
#             "skills": skills,
#             "posted_label": posted_label,
#             "job_url": job_url,
#             "description": job.get("jobDescription", ""),
#         }



from __future__ import annotations

import httpx

from app.core.config import settings
from app.utils.logger import logger


class JSearchScraper:
    """
    Fetches real jobs from LinkedIn, Indeed, Glassdoor etc
    via JSearch API on RapidAPI. No scraping, no captcha.
    """

    API_URL = "https://jsearch.p.rapidapi.com/search-v2"

    HEADERS = {
        "x-rapidapi-key": settings.RAPIDAPI_KEY,
        "x-rapidapi-host": "jsearch.p.rapidapi.com",
        "Content-Type": "application/json",
    }

    async def search(
        self,
        keyword: str,
        location: str = "",
        max_results: int = 20,
    ) -> list[dict]:
        query = f"{keyword} in {location}" if location else keyword

        params = {
        "query": f"{keyword} jobs in {location}" if location else f"{keyword} jobs",
        "num_pages": "1",
        "country": "in",
        "date_posted": "all",
    }

        logger.debug(f"JSearch query: {query}")

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.get(
                    self.API_URL,
                    headers=self.HEADERS,
                    params=params,
                )

            logger.debug(f"JSearch status: {response.status_code}")

            if response.status_code != 200:
                logger.warning(f"JSearch API returned {response.status_code}: {response.text[:200]}")
                return []

            data = response.json()
            raw_jobs = data.get("data", {}).get("jobs", [])

            logger.debug(f"Raw jobs from API: {len(raw_jobs)}")

            return [self._parse_job(job) for job in raw_jobs[:max_results] if self._parse_job(job)]

        except Exception as exc:
            logger.warning(f"JSearch API call failed: {exc}", exc_info=True)
            return []

    def _parse_job(self, job: dict) -> dict | None:
        title = job.get("job_title", "").strip()

        if not title:
            return None

        return {
            "external_id": job.get("job_id", ""),
            "title": title,
            "company": job.get("employer_name", ""),
            "location": f"{job.get('job_city', '')} {job.get('job_country', '')}".strip(),
            "experience": job.get("job_required_experience", {}).get("required_experience_in_months", ""),
            "salary": self._parse_salary(job),
            "skills": ", ".join(job.get("job_required_skills") or []),
            "posted_label": job.get("job_posted_at_datetime_utc", ""),
            "job_url": job.get("job_apply_link", ""),
            "description": (job.get("job_description") or "")[:1000],
        }

    @staticmethod
    def _parse_salary(job: dict) -> str:
        min_sal = job.get("job_min_salary")
        max_sal = job.get("job_max_salary")
        currency = job.get("job_salary_currency", "")

        if min_sal and max_sal:
            return f"{currency} {min_sal}-{max_sal}"
        if min_sal:
            return f"{currency} {min_sal}+"
        return ""