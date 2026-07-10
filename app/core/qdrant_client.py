from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from app.core.config import QDRANT_URL, QDRANT_API_KEY

COLLECTION_NAME = "jobs"
EMBEDDING_DIM = 384  # matches all-MiniLM-L6-v2, from Node 6

client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)


def ensure_collection_exists():
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
        )