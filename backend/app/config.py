
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from the backend root directory
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Config:
    """Application configuration."""

    BASE_DIR = BASE_DIR

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "dev-secret-key-change-in-production"
    )

    # Google Gemini API configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
    GEMINI_MODEL = (
        os.getenv("GEMINI_MODEL")
        or os.getenv("AI_MODEL")
        or "gemini-3.8-flash"
    ).strip()

    # Keep old OpenAI settings for optional future compatibility
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()

    # Demo mode
    DEMO_MODE = os.getenv(
        "DEMO_MODE",
        "false"
    ).lower() in ("true", "1", "yes")

    # Flask server configuration
    FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0" if os.getenv("PORT") else "127.0.0.1")
    FLASK_PORT = int(os.getenv("PORT") or os.getenv("FLASK_PORT", "5000"))
    WAITRESS_THREADS = int(os.getenv("WAITRESS_THREADS", "8"))

    # Frontend compiled distribution directory (for unified production serving)
    FRONTEND_DIST_DIR = Path(
        os.getenv("FRONTEND_DIST_DIR", str(BASE_DIR.parent / "frontend" / "dist"))
    ).resolve()

    # File uploads: Maximum 5 MB
    MAX_CONTENT_LENGTH = int(
        os.getenv("MAX_CONTENT_LENGTH", str(5 * 1024 * 1024))
    )

    ALLOWED_EXTENSIONS = {".pdf", ".docx"}

    # Temporary directory for secure processing
    UPLOAD_TEMP_DIR = BASE_DIR / "temp_uploads"
