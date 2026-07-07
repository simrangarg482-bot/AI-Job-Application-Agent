from sentence_transformers import SentenceTransformer
import numpy as np

# Loaded once at module import — reused across requests, not reloaded per call
_model = SentenceTransformer("all-MiniLM-L6-v2")

EMBEDDING_DIM = 384  # matches all-MiniLM-L6-v2's output size


def generate_embedding(text: str) -> list[float]:
    """
    Generates a normalized embedding vector for the given text.
    Normalized so cosine similarity reduces to a simple dot product later.
    """
    vector = _model.encode(text, normalize_embeddings=True)
    return vector.tolist()