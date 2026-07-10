from qdrant_client.models import PointStruct
from app.core.qdrant_client import client, COLLECTION_NAME


def upsert_job_vector(job_id: str, vector: list[float]) -> None:
    """
    Stores/updates a job's embedding in Qdrant.
    Qdrant's point IDs must be int or UUID — we use the job_id string as the
    payload, and a stable hash of it as the point ID.
    """
    point_id = _job_id_to_point_id(job_id)
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
                id=point_id,
                vector=vector,
                payload={"job_id": job_id},
            )
        ],
    )


def _job_id_to_point_id(job_id: str) -> str:
    """
    Qdrant point IDs must be unsigned int or UUID.
    Our job_ids look like 'adzuna_12345' — not a valid UUID —
    so we deterministically derive a UUID from it instead.
    Same job_id always maps to the same point_id, so upserts are idempotent.
    """
    import uuid
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, job_id))


def search_similar_jobs(query_vector: list[float], top_n: int = 40) -> list[tuple[str, float]]:
    """
    Returns list of (job_id, similarity_score) sorted by similarity descending.
    """
    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=top_n,
    )
    return [(hit.payload["job_id"], hit.score) for hit in results]