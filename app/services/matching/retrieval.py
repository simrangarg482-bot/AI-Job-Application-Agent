from sqlalchemy.orm import Session
from app.models.db_models import JobRecord
from app.services.matching.job_vector_store import search_similar_jobs


def get_shortlist(
    db: Session,
    resume_embedding: list[float],
    top_n: int = 40,
) -> list[tuple[JobRecord, float]]:
    """
    Retrieves the top_n most similar jobs using Qdrant's indexed search,
    then fetches the corresponding full job records from Postgres.
    """
    qdrant_results = search_similar_jobs(resume_embedding, top_n=top_n)

    job_ids = [job_id for job_id, _ in qdrant_results]
    score_by_id = {job_id: score for job_id, score in qdrant_results}

    jobs = db.query(JobRecord).filter(JobRecord.job_id.in_(job_ids)).all()
    job_by_id = {job.job_id: job for job in jobs}

    # Preserve Qdrant's similarity-ranked order, not Postgres's arbitrary row order
    scored = [
        (job_by_id[job_id], score_by_id[job_id])
        for job_id in job_ids
        if job_id in job_by_id
    ]

    return scored