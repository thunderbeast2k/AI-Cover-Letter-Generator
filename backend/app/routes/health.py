from flask import Blueprint, jsonify
from app.config import Config
from app.services.ai_service import AIService

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health_check():
    """Return health status, Gemini connection readiness, and config without exposing secrets."""
    connection_status, connection_message = AIService.test_connection()
    has_gemini_key = bool(Config.GEMINI_API_KEY)

    return jsonify({
        "status": connection_status,
        "service": "AI Cover Letter Generator API",
        "version": "1.0.0",
        "config": {
            "model": Config.GEMINI_MODEL,
            "has_gemini_key": has_gemini_key,
            "has_openai_key": has_gemini_key,  # Retained for backward compatibility
            "demo_mode": Config.DEMO_MODE,
            "max_upload_size_mb": round(Config.MAX_CONTENT_LENGTH / (1024 * 1024), 1)
        },
        "connection": {
            "connected": connection_status == "Connected",
            "message": connection_message
        }
    }), 200
