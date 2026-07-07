from sqlalchemy import Column, String, DateTime, Text
from datetime import datetime, timezone

from app.core.database import Base


class ResumeRecord(Base):
    __tablename__ = "resumes"

    resume_id = Column(String, primary_key=True)
    original_filename = Column(String, nullable=False)
    stored_path = Column(String, nullable=False)
    file_hash = Column(String, nullable=False, index=True, unique=True)
    status = Column(String, nullable=False, default="uploaded")
    extracted_text = Column(Text, nullable=True)  # filled in once Node 4 runs
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    parsed_data = Column(Text, nullable=True)       # JSON-serialized ParsedResume
    confidence_score = Column(String, nullable=True)  # store as string for simplicity now
    embedding = Column(Text, nullable=True)  # JSON-serialized list[float]

class JobRecord(Base):
    __tablename__ = "jobs"

    job_id = Column(String, primary_key=True)          # Adzuna's own job id
    title = Column(String, nullable=False)
    company = Column(String, nullable=True)
    location = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    min_years_experience = Column(String, nullable=True)  # parsed later if needed
    salary_min = Column(String, nullable=True)
    salary_max = Column(String, nullable=True)
    remote = Column(String, nullable=True)              # "yes"/"no"/"unknown"
    apply_url = Column(String, nullable=True)
    source = Column(String, nullable=False, default="adzuna")
    embedding = Column(Text, nullable=True)              # JSON-serialized vector, cached
    fetched_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))