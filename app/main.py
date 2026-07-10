from fastapi import FastAPI
from app.api import resumes
from app.core.database import Base, engine
from app.models import db_models
from app.api import resumes, jobs
from app.core.qdrant_client import ensure_collection_exists

Base.metadata.create_all(bind=engine)

ensure_collection_exists()

app = FastAPI(title="AI Job Application Agent", version="0.1.0")

app.include_router(resumes.router)
app.include_router(resumes.router)
app.include_router(jobs.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}