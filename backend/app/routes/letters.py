import io
import re
import logging
from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
from pydantic import ValidationError

from app.schemas.request_models import (
    CoverLetterGenerateRequest,
    LetterImproveRequest,
    LetterQualityRequest,
    ExportRequest
)
from app.services.ai_service import AIService
from app.services.document_service import DocumentService

logger = logging.getLogger(__name__)
letters_bp = Blueprint("letters", __name__)


def make_safe_download_filename(candidate_name: str, company_name: str, ext: str) -> str:
    """Create clean, human-readable download filename."""
    clean_name = re.sub(r"[^\w\s-]", "", candidate_name).strip().replace(" ", "_")
    clean_comp = re.sub(r"[^\w\s-]", "", company_name).strip().replace(" ", "_")
    base = f"Cover_Letter_{clean_comp}_{clean_name}" if (clean_comp and clean_name) else "Cover_Letter"
    return f"{secure_filename(base)}.{ext}"


def format_validation_error(ve: ValidationError) -> str:
    """Format Pydantic validation errors into readable user messages."""
    errors = []
    for err in ve.errors():
        field = " -> ".join(str(loc) for loc in err.get("loc", []))
        msg = err.get("msg", "invalid")
        errors.append(f"{field}: {msg}")
    return "; ".join(errors) if errors else "Validation failed."


@letters_bp.route("/letters/generate", methods=["POST"])
def generate_letter():
    """Generate personalized cover letter based on candidate credentials and job description."""
    try:
        data = request.get_json(force=True, silent=False)
        if not data:
            return jsonify({"success": False, "error": "Request body must be valid JSON."}), 400

        req = CoverLetterGenerateRequest(**data)
        generated = AIService.generate_cover_letter(
            personal_info=req.personal_info.model_dump(),
            job_info=req.job_info.model_dump(),
            professional_info=req.professional_info.model_dump(),
            writing_style=req.writing_style
        )

        return jsonify({
            "success": True,
            "data": generated.model_dump()
        }), 200

    except ValidationError as ve:
        return jsonify({"success": False, "error": format_validation_error(ve)}), 400
    except ValueError as ve:
        return jsonify({"success": False, "error": str(ve)}), 400
    except Exception as e:
        logger.error(f"Cover letter generation error: {e}", exc_info=True)
        return jsonify({"success": False, "error": f"Failed to generate cover letter: {str(e)}"}), 500


@letters_bp.route("/letters/improve", methods=["POST"])
def improve_letter():
    """Improve complete cover letter or rewrite selected text segment."""
    try:
        data = request.get_json(force=True, silent=False)
        if not data:
            return jsonify({"success": False, "error": "Request body must be valid JSON."}), 400

        req = LetterImproveRequest(**data)
        improved_text = AIService.improve_cover_letter(
            cover_letter=req.cover_letter,
            action=req.action,
            selected_text=req.selected_text,
            job_title=req.job_title,
            company_name=req.company_name,
            custom_instruction=req.custom_instruction
        )

        return jsonify({
            "success": True,
            "data": {
                "improved_text": improved_text,
                "action": req.action,
                "is_selection_replacement": bool(req.action == "rewrite_selection" and req.selected_text)
            }
        }), 200

    except ValidationError as ve:
        return jsonify({"success": False, "error": str(ve)}), 400
    except ValueError as ve:
        return jsonify({"success": False, "error": str(ve)}), 400
    except Exception as e:
        logger.error(f"Letter improvement error: {e}", exc_info=True)
        return jsonify({"success": False, "error": "Failed to improve letter text."}), 500


@letters_bp.route("/letters/quality", methods=["POST"])
def check_quality():
    """Evaluate quality, grammar, readability, and job alignment of cover letter."""
    try:
        data = request.get_json(force=True, silent=False)
        if not data:
            return jsonify({"success": False, "error": "Request body must be valid JSON."}), 400

        req = LetterQualityRequest(**data)
        quality_data = AIService.check_cover_letter_quality(
            cover_letter=req.cover_letter,
            job_description=req.job_description,
            job_title=req.job_title
        )

        return jsonify({
            "success": True,
            "data": quality_data.model_dump()
        }), 200

    except ValidationError as ve:
        return jsonify({"success": False, "error": str(ve)}), 400
    except Exception as e:
        logger.error(f"Quality analysis error: {e}", exc_info=True)
        return jsonify({"success": False, "error": "Failed to analyze letter quality."}), 500


@letters_bp.route("/letters/export/pdf", methods=["POST"])
def export_pdf():
    """Render and download cover letter as formatted PDF."""
    try:
        data = request.get_json(force=True, silent=False)
        if not data:
            return jsonify({"success": False, "error": "Request body must be valid JSON."}), 400

        req = ExportRequest(**data)
        pdf_bytes = DocumentService.generate_pdf(
            cover_letter=req.cover_letter,
            personal_info=req.personal_info,
            job_info=req.job_info,
            template_id=req.template_id
        )

        filename = make_safe_download_filename(
            candidate_name=req.personal_info.full_name,
            company_name=req.job_info.company_name,
            ext="pdf"
        )

        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=filename
        )

    except ValidationError as ve:
        return jsonify({"success": False, "error": str(ve)}), 400
    except Exception as e:
        logger.error(f"PDF generation error: {e}", exc_info=True)
        return jsonify({"success": False, "error": "Failed to generate PDF document."}), 500


@letters_bp.route("/letters/export/docx", methods=["POST"])
def export_docx():
    """Render and download cover letter as formatted DOCX."""
    try:
        data = request.get_json(force=True, silent=False)
        if not data:
            return jsonify({"success": False, "error": "Request body must be valid JSON."}), 400

        req = ExportRequest(**data)
        docx_bytes = DocumentService.generate_docx(
            cover_letter=req.cover_letter,
            personal_info=req.personal_info,
            job_info=req.job_info,
            template_id=req.template_id
        )

        filename = make_safe_download_filename(
            candidate_name=req.personal_info.full_name,
            company_name=req.job_info.company_name,
            ext="docx"
        )

        return send_file(
            io.BytesIO(docx_bytes),
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            as_attachment=True,
            download_name=filename
        )

    except ValidationError as ve:
        return jsonify({"success": False, "error": str(ve)}), 400
    except Exception as e:
        logger.error(f"DOCX generation error: {e}", exc_info=True)
        return jsonify({"success": False, "error": "Failed to generate DOCX document."}), 500
