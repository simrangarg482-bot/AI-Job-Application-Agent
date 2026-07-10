import json
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.job_sources.adzuna_client import fetch_jobs
from app.services.job_sources.adzuna_normalizer import normalize_adzuna_job
from app.services import job_repository
from app.services.job_text_builder import build_job_summary_text
from app.services.embedding_service import generate_embedding
from app.services.matching.job_vector_store import upsert_job_vector

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/ingest")
def ingest_jobs(
    query: str = Query(..., description="Search term, e.g. 'backend engineer'"),
    country: str = Query("gb"),
    location: str | None = Query(None),
    results: int = Query(20, le=50),
    db: Session = Depends(get_db),
):
    raw_jobs = fetch_jobs(query=query, country=country, location=location, results=results)

    ingested_ids = []
    for raw in raw_jobs:
        job_dict = normalize_adzuna_job(raw)
        if not job_dict["title"] or not job_dict["description"]:
            continue  # skip garbage/incomplete listings rather than storing junk
        record = job_repository.upsert_job(db, job_dict)
        ingested_ids.append(record.job_id)

    return {"ingested_count": len(ingested_ids), "job_ids": ingested_ids}


@router.post("/embed-pending")
def embed_pending_jobs(db: Session = Depends(get_db)):
    pending = job_repository.get_unembedded_jobs(db)

    for job in pending:
        text = build_job_summary_text(job)
        vector = generate_embedding(text)
        upsert_job_vector(job.job_id, vector)
        job.embedding = "stored_in_qdrant"  # marker, so get_unembedded_jobs() skips it next time

    db.commit()

    return {"embedded_count": len(pending)}