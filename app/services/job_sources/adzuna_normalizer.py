def normalize_adzuna_job(raw: dict) -> dict:
    """
    Maps Adzuna's raw job dict into our internal JobRecord shape.
    """
    return {
        "job_id": f"adzuna_{raw.get('id')}",
        "title": raw.get("title", "").strip(),
        "company": (raw.get("company") or {}).get("display_name"),
        "location": (raw.get("location") or {}).get("display_name"),
        "description": raw.get("description", "").strip(),
        "salary_min": str(raw["salary_min"]) if raw.get("salary_min") else None,
        "salary_max": str(raw["salary_max"]) if raw.get("salary_max") else None,
        "apply_url": raw.get("redirect_url"),
        "source": "adzuna",
    }