from pathlib import Path
import pdfplumber
import docx


class ExtractionError(Exception):
    pass


def extract_text_from_pdf(path: str) -> str:
    text_parts = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def extract_text_from_docx(path: str) -> str:
    document = docx.Document(path)
    paragraphs = [p.text for p in document.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def extract_text(stored_path: str) -> str:
    """
    Dispatches to the right extractor based on file extension.
    Raises ExtractionError if extraction fails or produces near-empty output.
    """
    ext = Path(stored_path).suffix.lower()

    try:
        if ext == ".pdf":
            text = extract_text_from_pdf(stored_path)
        elif ext == ".docx":
            text = extract_text_from_docx(stored_path)
        else:
            raise ExtractionError(f"Unsupported extension for extraction: {ext}")
    except Exception as e:
        raise ExtractionError(f"Failed to extract text: {e}")

    # Guard against scanned/image-based PDFs or corrupt files producing near-empty text
    if len(text.strip()) < 50:
        raise ExtractionError(
            "Extracted text is too short — file may be a scanned image, corrupt, or empty."
        )

    return text