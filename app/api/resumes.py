from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.services.file_storage import save_resume_file, compute_file_hash, STORAGE_DIR
from app.services.text_extraction import extract_text, ExtractionError
from app.models.resume import ResumeUploadResponse
from app.core.database import get_db
from app.services import resume_repository
from app.services.resume_parser import parse_resume_text, ParsingError

router = APIRouter(prefix="/resumes", tags=["resumes"])

MAX_FILE_SIZE_MB = 5


@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()

    size_mb = len(content) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(status_code=413, detail=f"File too large ({size_mb:.1f} MB). Max {MAX_FILE_SIZE_MB} MB.")
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    file_hash = compute_file_hash(content)

    # Dedup check — if we've seen this exact file before, return the existing record
    existing = resume_repository.get_by_hash(db, file_hash)
    if existing:
        return ResumeUploadResponse(
            resume_id=existing.resume_id,
            original_filename=existing.original_filename,
            stored_path=existing.stored_path,
            uploaded_at=existing.uploaded_at,
            status="duplicate_of_existing",
        )

    try:
        resume_id, stored_path = save_resume_file(file.filename, content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    record = resume_repository.create_resume(
        db=db,
        resume_id=resume_id,
        original_filename=file.filename,
        stored_path=stored_path,
        file_hash=file_hash,
    )

    return ResumeUploadResponse(
        resume_id=record.resume_id,
        original_filename=record.original_filename,
        stored_path=record.stored_path,
        uploaded_at=record.uploaded_at,
        status=record.status,
    )


@router.get("/{resume_id}/extract")
def extract_resume_text(resume_id: str, db: Session = Depends(get_db)):
    record = resume_repository.get_by_id(db, resume_id)
    if not record:
        raise HTTPException(status_code=404, detail="Resume not found.")

    try:
        text = extract_text(record.stored_path)
    except ExtractionError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # Persist it so Node 4 doesn't need to re-extract every time
    record.extracted_text = text
    db.commit()

    return {"resume_id": resume_id, "extracted_text": text}

@router.post("/{resume_id}/parse")
def parse_resume(resume_id: str, db: Session = Depends(get_db)):
    record = resume_repository.get_by_id(db, resume_id)
    if not record:
        raise HTTPException(status_code=404, detail="Resume not found.")

    if not record.extracted_text:
        raise HTTPException(
            status_code=400,
            detail="No extracted text found. Call /extract first.",
        )

    try:
        parsed, confidence = parse_resume_text(record.extracted_text)
    except ParsingError as e:
        raise HTTPException(status_code=422, detail=str(e))

    record.parsed_data = parsed.model_dump_json()
    record.confidence_score = str(confidence)
    record.status = "parsed"
    db.commit()

    return {
        "resume_id": resume_id,
        "confidence_score": confidence,
        "parsed_resume": parsed.model_dump(),
    }