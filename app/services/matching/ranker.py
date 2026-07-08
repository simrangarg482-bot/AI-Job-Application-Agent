from app.models.db_models import JobRecord
from app.models.parsed_resume import ParsedResume
from app.services.matching.hard_filters import apply_hard_filters
from app.services.matching.job_skill_extractor import analyze_job_fit
from app.services.matching.skill_gap import compute_skill_gap

VECTOR_WEIGHT = 0.6
SKILL_WEIGHT = 0.4
RERANK_POOL_SIZE = 15


def rank_jobs(
    shortlist: list[tuple[JobRecord, float]],
    parsed_resume: ParsedResume,
    resume_summary_text: str,
    location_contains: str | None = None,
    min_salary: int | None = None,
) -> list[dict]:
    # Hard filters first — never let similarity override an explicit constraint
    filtered = apply_hard_filters(shortlist, location_contains=location_contains, min_salary=min_salary)

    # Take the top N by vector similarity for expensive LLM analysis
    top_pool = filtered[:RERANK_POOL_SIZE]

    results = []
    for job, vector_score in top_pool:
        analysis = analyze_job_fit(resume_summary_text, job.title, job.description or "")
        gap = compute_skill_gap(parsed_resume.skills, parsed_resume.inferred_skills, analysis["required_skills"])

        blended_score = (VECTOR_WEIGHT * vector_score) + (SKILL_WEIGHT * gap["overlap_ratio"])

        results.append({
            "job_id": job.job_id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "apply_url": job.apply_url,
            "vector_similarity": round(vector_score, 4),
            "skill_overlap_ratio": gap["overlap_ratio"],
            "blended_score": round(blended_score, 4),
            "matched_skills": gap["matched_skills"],
            "missing_skills": gap["missing_skills"],
            "explanation": analysis["explanation"],
        })

    results.sort(key=lambda r: r["blended_score"], reverse=True)
    return results