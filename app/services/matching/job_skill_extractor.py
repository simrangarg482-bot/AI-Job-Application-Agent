import json
import re
from openai import OpenAI
from app.core.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

MODEL = "gpt-4.1-mini"


SYSTEM_PROMPT = """You analyze a job description against a candidate's resume summary.
Extract ONLY skills/technologies explicitly required or clearly implied by the job description.
Do not invent requirements that aren't stated or strongly implied.
Output ONLY valid JSON, no markdown, no commentary.
"""


def _strip_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    return text


def analyze_job_fit(
    resume_summary: str,
    job_title: str,
    job_description: str
) -> dict:
    """
    Single LLM call that does two things at once:
    1. Extracts the job's required skills from free-text description.
    2. Writes a short 1-2 sentence explanation of why this resume fits (or doesn't).

    Returns dict with:
    - required_skills
    - explanation

    Falls back safely if model output is malformed.
    """

    prompt = f"""Job title: {job_title}

Job description:
\"\"\"
{job_description[:3000]}
\"\"\"

Candidate resume summary:
\"\"\"
{resume_summary}
\"\"\"

Respond with ONLY this JSON shape:

{{
  "required_skills": ["string"],
  "explanation": "1-2 sentence explanation of fit, mentioning specific overlaps or gaps"
}}
"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            temperature=0,
            max_completion_tokens=500,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
        )

        raw = response.choices[0].message.content

        raw = _strip_fences(raw)

        data = json.loads(raw)

        return {
            "required_skills": data.get("required_skills", []),
            "explanation": data.get("explanation", ""),
        }

    except Exception:
        # One bad job should not break complete ranking
        return {
            "required_skills": [],
            "explanation": "Could not generate explanation."
        }