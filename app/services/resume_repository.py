from sqlalchemy.orm import Session
from app.models.db_models import ResumeRecord


def get_by_hash(db: Session, file_hash: str) -> ResumeRecord | None:
    return db.query(ResumeRecord).filter(ResumeRecord.file_hash == file_hash).first()


def get_by_id(db: Session, resume_id: str) -> ResumeRecord | None:
    return db.query(ResumeRecord).filter(ResumeRecord.resume_id == resume_id).first()


def create_resume(
    db: Session,
    resume_id: str,
    original_filename: str,
    stored_path: str,
    file_hash: str,
) -> ResumeRecord:
    record = ResumeRecord(
        resume_id=resume_id,
        original_filename=original_filename,
        stored_path=stored_path,
        file_hash=file_hash,
        status="uploaded",
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record