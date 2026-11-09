import os
import logging
from pathlib import Path
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from app.config import Config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


def create_app(config_class=Config) -> Flask:
    """Application factory for Flask backend with optional production frontend serving."""
    frontend_dist = Path(getattr(config_class, "FRONTEND_DIST_DIR", Config.BASE_DIR.parent / "frontend" / "dist"))
    has_frontend_build = frontend_dist.is_dir() and (frontend_dist / "index.html").is_file()

    app = Flask(__name__)
    app.config.from_object(config_class)

    # Enable CORS for API routes
    CORS(
        app,
        resources={r"/api/*": {"origins": "*"}},
        supports_credentials=True,
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"]
    )

    # Register blueprints
    from app.routes.health import health_bp
    from app.routes.resume import resume_bp
    from app.routes.jobs import jobs_bp
    from app.routes.letters import letters_bp

    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(resume_bp, url_prefix="/api")
    app.register_blueprint(jobs_bp, url_prefix="/api")
    app.register_blueprint(letters_bp, url_prefix="/api")

    # Production security headers
    @app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

    # Frontend SPA and static file serving (Unified production mode)
    if has_frontend_build:
        logger.info("Serving compiled production frontend from %s", frontend_dist)

        @app.route("/", defaults={"path": ""})
        @app.route("/<path:path>")
        def serve_frontend(path: str):
            # API requests that didn't match a blueprint must return JSON 404
            if path.startswith("api/") or path == "api":
                return jsonify({
                    "success": False,
                    "error": "Endpoint not found."
                }), 404

            # Serve actual static files if they exist in dist (e.g. assets, favicon)
            file_candidate = frontend_dist / path
            if path and file_candidate.is_file():
                response = send_from_directory(str(frontend_dist), path)
                if path.startswith("assets/"):
                    response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
                return response

            # SPA fallback: return index.html for all client-side routes
            response = send_from_directory(str(frontend_dist), "index.html")
            response.headers["Cache-Control"] = "no-cache, must-revalidate"
            return response

    # Error handlers
    @app.errorhandler(413)
    def request_entity_too_large(error):
        return jsonify({
            "success": False,
            "error": "The uploaded file exceeds the 5MB size limit."
        }), 413

    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith("/api/"):
            return jsonify({
                "success": False,
                "error": "Endpoint not found."
            }), 404
        if has_frontend_build:
            response = send_from_directory(str(frontend_dist), "index.html")
            response.headers["Cache-Control"] = "no-cache, must-revalidate"
            return response
        return jsonify({
            "success": False,
            "error": "Endpoint not found."
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "success": False,
            "error": "An internal server error occurred."
        }), 500

    return app
