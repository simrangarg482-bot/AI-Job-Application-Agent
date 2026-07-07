import uuid
from pathlib import Path
import hashlib

STORAGE_DIR = Path("storage/resumes")
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".docx"}


def validate_extension(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}. Only PDF and DOCX are allowed.")
    return ext


def save_resume_file(filename: str, content: bytes) -> tuple[str, str]:
    """
    Saves file to disk under a unique ID.
    Returns (resume_id, stored_path).
    """
    ext = validate_extension(filename)
    resume_id = str(uuid.uuid4())
    stored_filename = f"{resume_id}{ext}"
    stored_path = STORAGE_DIR / stored_filename

    with open(stored_path, "wb") as f:
        f.write(content)

    return resume_id, str(stored_path)

def compute_file_hash(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()