SYSTEM_PROMPT = """
You are an expert technical recruiter and resume analyst.
Your job is to evaluate how well a candidate's resume matches a job description.
Always respond with valid JSON only. No explanation, no markdown, no backticks.
""".strip()


def build_user_prompt(
    resume_text: str,
    job_title: str,
    job_analysis: dict,
) -> str:
    return f"""
Evaluate how well this resume matches the job and respond with JSON:

{{
  "score": <integer 0-100>,
  "match_level": "<EXCELLENT|GOOD|FAIR|POOR>",
  "matching_skills": ["skills found in both resume and job"],
  "missing_skills": ["required skills not found in resume"],
  "strengths": ["top 3 reasons this candidate is a good fit"],
  "gaps": ["top 3 areas where candidate falls short"],
  "recommendation": "<one sentence summary>"
}}

Job Title: {job_title}
Required Skills: {", ".join(job_analysis.get("required_skills", []))}
Experience Required: {job_analysis.get("experience_years", "Not specified")} years
Seniority: {job_analysis.get("seniority_level", "Not specified")}
Keywords: {", ".join(job_analysis.get("keywords", []))}

Resume:
{resume_text[:3000]}
""".strip()