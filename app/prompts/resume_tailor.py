SYSTEM_PROMPT = """
You are an expert resume writer and career coach.
Your job is to tailor a resume to match a specific job description.
Always respond with valid JSON only. No explanation, no markdown, no backticks.
""".strip()


def build_user_prompt(
    resume_text: str,
    job_title: str,
    job_analysis: dict,
    match_result: dict,
) -> str:
    return f"""
Tailor this resume for the job below. Respond with JSON only:

{{
  "summary": "rewritten professional summary targeting this job (2-3 sentences)",
  "skills": ["reordered skills list prioritizing job requirements, max 12 items"],
  "experience_highlights": ["3-5 bullet points from experience most relevant to this job"],
  "improvements": ["3-5 specific changes made and why"]
}}

Job Title: {job_title}
Required Skills: {", ".join(job_analysis.get("required_skills", []))}
Missing Skills to Address: {", ".join(match_result.get("missing_skills", []))}
Matching Skills to Highlight: {", ".join(match_result.get("matching_skills", []))}
Seniority: {job_analysis.get("seniority_level", "Not specified")}
Key Responsibilities: {", ".join(job_analysis.get("key_responsibilities", []))}

Original Resume:
{resume_text[:2000]}
""".strip()