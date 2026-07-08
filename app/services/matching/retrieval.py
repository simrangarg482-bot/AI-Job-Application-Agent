import json
from sqlalchemy.orm import Session

from app.models.db_models import JobRecord
from app.services.matching.vector_similarity import cosine_similarity


def get_shortlist(
    db: Session,
    resume_embedding: list[float],
    top_n: int = 40,
) -> list[tuple[JobRecord, float]]:
    """
    Computes cosine similarity between the resume embedding and every
    embedded job in the database, returning the top_n highest-scoring
    (job, similarity_score) pairs, sorted descending.
    """
    jobs = db.query(JobRecord).filter(JobRecord.embedding.isnot(None)).all()

    scored = []
    for job in jobs:
        job_vector = json.loads(job.embedding)
        score = cosine_similarity(resume_embedding, job_vector)
        scored.append((job, score))

    scored.sort(key=lambda pair: pair[1], reverse=True)

    return scored[:top_n]