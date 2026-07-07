SYSTEM_PROMPT = """
You are an expert job description analyzer.
Your job is to extract structured information from job descriptions.
Always respond with valid JSON only. No explanation, no markdown, no backticks.
""".strip()


def build_user_prompt(job_title: str, job_description: str) -> str:
    return f"""
Analyze this job posting and extract the following information as JSON:

{{
  "required_skills": ["list of required technical skills"],
  "nice_to_have_skills": ["list of optional/preferred skills"],
  "experience_years": "minimum years of experience as a number or null",
  "employment_type": "Full-time / Part-time / Contract / Internship or null",
  "seniority_level": "Entry / Mid / Senior / Lead / Manager or null",
  "key_responsibilities": ["top 5 responsibilities as short bullet points"],
  "keywords": ["important keywords for resume matching"]
}}

Job Title: {job_title}

Job Description:
{job_description[:3000]}
""".strip()