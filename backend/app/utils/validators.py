import re
from pathlib import Path
from werkzeug.datastructures import FileStorage

ALLOWED_EXTENSIONS = {".pdf", ".docx"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


def validate_resume_file(file: FileStorage) -> tuple[bool, str]:
    """Validate uploaded file for size, extension, and binary signature."""
    if not file or not file.filename:
        return False, "No file was uploaded."

    filename = file.filename.strip()
    ext = Path(filename).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Unsupported file type '{ext}'. Allowed types: PDF, DOCX."

    # Read the first few bytes to verify magic number
    header = file.read(8)
    file.seek(0)

    if ext == ".pdf":
        if not header.startswith(b"%PDF-"):
            return False, "Invalid PDF file structure or corrupted document."
    elif ext == ".docx":
        # DOCX is a zipped XML format starting with PK\x03\x04
        if not header.startswith(b"PK\x03\x04"):
            return False, "Invalid DOCX file structure or corrupted document."

    return True, ""


def sanitize_untrusted_text(text: str) -> str:
    """
    Sanitizes user/resume/job text to defend against prompt injection attempts.
    Preserves actual applicant facts while disarming jailbreak and instruction overrides.
    """
    if not text:
        return ""

    # Normalize excessive null or control chars
    clean = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)

    # Neutralize prompt injection phrases that try to override system persona
    injection_patterns = [
        r"(?i)ignore\s+(all\s+)?(previous|prior|above)\s+instructions?",
        r"(?i)system\s*:\s*you\s+are",
        r"(?i)developer\s+mode\s+(enabled|on)",
        r"(?i)disregard\s+the\s+instructions\s+above",
    ]
    for pattern in injection_patterns:
        clean = re.sub(pattern, "[sanitized-instruction]", clean)

    return clean.strip()
