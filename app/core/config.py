import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")

if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
    raise RuntimeError("ADZUNA_APP_ID / ADZUNA_APP_KEY not set in .env")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not set in .env")