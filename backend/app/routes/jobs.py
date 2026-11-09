import logging
from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from app.schemas.request_models import JobAnalysisRequest
from app.services.ai_service import AIService

logger = logging.getLogger(__name__)
jobs_bp = Blueprint("jobs", __name__)


@jobs_bp.route("/jobs/analyze", methods=["POST"])
def analyze_job():
    """Analyze provided job description text and extract structured criteria."""
    try:
        data = request.get_json(force=True, silent=False)
        if not data:
            return jsonify({"success": False, "error": "Request body must be a JSON object."}), 400

        req = JobAnalysisRequest(**data)
        analysis_data = AIService.analyze_job_description(
            job_description=req.job_description,
            job_title=req.job_title,
            company_name=req.company_name
        )

        return jsonify({
            "success": True,
            "data": analysis_data.model_dump()
        }), 200

    except ValidationError as ve:
        return jsonify({"success": False, "error": str(ve)}), 400
    except Exception as e:
        logger.error(f"Failed to analyze job description: {e}", exc_info=True)
        return jsonify({"success": False, "error": "An error occurred while analyzing the job description."}), 500
