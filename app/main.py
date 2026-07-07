from fastapi import FastAPI
from app.api import resumes
from app.core.database import Base, engine
from app.models import db_models

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Job Application Agent", version="0.1.0")

app.include_router(resumes.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}