import os
import uuid
import logging
from pathlib import Path
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from pydantic import ValidationError

from app.config import Config
from app.utils.validators import validate_resume_file
from app.services.resume_parser import ResumeParserService
from app.services.matching_service import MatchingService
from app.schemas.request_models import ResumeMatchRequest

logger = logging.getLogger(__name__)
resume_bp = Blueprint("resume", __name__)


@resume_bp.route("/resume/parse", methods=["POST"])
def parse_resume():
    """Accept multipart PDF/DOCX file and extract structured resume information."""
    if "file" not in request.files:
        return jsonify({
            "success": False,
            "error": "No file field found in upload request. Form field name must be 'file'."
        }), 400

    file = request.files["file"]
    is_valid, error_msg = validate_resume_file(file)
    if not is_valid:
        return jsonify({"success": False, "error": error_msg}), 400

    # Ensure upload directory exists
    temp_dir = Path(Config.UPLOAD_TEMP_DIR)
    temp_dir.mkdir(parents=True, exist_ok=True)

    original_filename = secure_filename(file.filename or "resume")
    ext = Path(original_filename).suffix.lower()
    temp_filename = f"upload_{uuid.uuid4().hex}{ext}"
    temp_filepath = temp_dir / temp_filename

    try:
        # Save temporary file
        file.save(str(temp_filepath))

        # Check actual file size on disk
        if temp_filepath.stat().st_size > Config.MAX_CONTENT_LENGTH:
            return jsonify({
                "success": False,
                "error": f"File exceeds maximum upload size of {round(Config.MAX_CONTENT_LENGTH / (1024*1024))}MB."
            }), 400

        # Parse document
        parsed_data = ResumeParserService.parse_document(temp_filepath, original_filename)

        return jsonify({
            "success": True,
            "data": parsed_data.model_dump(),
            "meta": {
                "filename": original_filename,
                "size_bytes": temp_filepath.stat().st_size
            }
        }), 200

    except ValueError as ve:
        logger.warning(f"Validation/parsing error: {ve}")
        return jsonify({"success": False, "error": str(ve)}), 422
    except Exception as e:
        logger.error(f"Unexpected document parsing failure: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Failed to parse document. Please ensure the file is not corrupted or password-protected."
        }), 500
    finally:
        # Guarantee cleanup of temporary file
        if temp_filepath.exists():
            try:
                temp_filepath.unlink()
            except OSError as cleanup_err:
                logger.warning(f"Failed to delete temporary file {temp_filepath}: {cleanup_err}")


@resume_bp.route("/resume/match", methods=["POST"])
def match_resume():
    """Calculate transparent heuristic match between candidate details and job requirements."""
    try:
        data = request.get_json(force=True, silent=False)
        if not data:
            return jsonify({"success": False, "error": "Request body must be a JSON object."}), 400

        req = ResumeMatchRequest(**data)
        match_result = MatchingService.calculate_match(
            candidate_skills=req.candidate_skills,
            job_description=req.job_description,
            resume_text=req.resume_text,
            candidate_experience=req.candidate_experience,
            candidate_projects=req.candidate_projects,
            candidate_education=req.candidate_education,
            job_title=req.job_title,
            company_name=req.company_name
        )

        return jsonify({
            "success": True,
            "data": match_result.model_dump()
        }), 200

    except ValidationError as ve:
        return jsonify({"success": False, "error": str(ve)}), 400
    except Exception as e:
        logger.error(f"Error during matching calculation: {e}", exc_info=True)
        return jsonify({"success": False, "error": "Internal error calculating match estimate."}), 500
