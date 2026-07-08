from app.models.db_models import JobRecord


def apply_hard_filters(
    scored_jobs: list[tuple[JobRecord, float]],
    location_contains: str | None = None,
    min_salary: int | None = None,
) -> list[tuple[JobRecord, float]]:
    """
    Filters out jobs that fail explicit hard constraints, BEFORE any scoring blend.
    A semantically similar job that fails a hard constraint should never
    outrank one that passes it, regardless of vector similarity.
    """
    result = []
    for job, score in scored_jobs:
        if location_contains:
            if not job.location or location_contains.lower() not in job.location.lower():
                continue
        if min_salary:
            try:
                if job.salary_min and int(float(job.salary_min)) < min_salary:
                    continue
            except ValueError:
                pass  # unparseable salary — don't filter it out over bad data
        result.append((job, score))
    return result