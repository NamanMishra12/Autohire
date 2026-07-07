SYSTEM_PROMPT = """
You are an expert career coach and professional cover letter writer.
Your job is to write compelling, personalized cover letters.
Always respond with valid JSON only. No explanation, no markdown, no backticks.
""".strip()


def build_user_prompt(
    resume_text: str,
    job_title: str,
    company: str,
    job_analysis: dict,
    match_result: dict,
) -> str:
    return f"""
Write a professional cover letter for this candidate applying to this job.
Respond with JSON only:

{{
  "subject": "email subject line for this application",
  "opening_paragraph": "compelling opening that mentions the role and company",
  "body_paragraph_1": "highlight most relevant experience and matching skills",
  "body_paragraph_2": "address how candidate can contribute, reference key responsibilities",
  "closing_paragraph": "strong closing with call to action",
  "full_cover_letter": "complete cover letter as plain text combining all paragraphs"
}}

Job Title: {job_title}
Company: {company}
Required Skills: {", ".join(job_analysis.get("required_skills", []))}
Key Responsibilities: {", ".join(job_analysis.get("key_responsibilities", []))}
Matching Skills: {", ".join(match_result.get("matching_skills", []))}
Candidate Strengths: {", ".join(match_result.get("strengths", []))}
Seniority Level: {job_analysis.get("seniority_level", "Not specified")}

Resume:
{resume_text[:2000]}
""".strip()