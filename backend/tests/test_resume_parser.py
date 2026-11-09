import io
import pytest
import pymupdf
import docx
from pathlib import Path
from app.services.resume_parser import ResumeParserService
from app.utils.validators import validate_resume_file
from werkzeug.datastructures import FileStorage


def create_sample_pdf(tmp_path: Path) -> Path:
    """Generate a clean test PDF resume."""
    pdf_path = tmp_path / "sample_resume.pdf"
    doc = pymupdf.open()
    page = doc.new_page()
    text = (
        "Sarah Jenkins\n"
        "sarah.jenkins@example.com | (555) 234-5678 | San Francisco, CA\n"
        "https://linkedin.com/in/sarahjenkins | https://github.com/sarahj\n\n"
        "Professional Summary\n"
        "Results-oriented Full Stack Engineer with 4 years building scalable web services.\n\n"
        "Technical Skills\n"
        "Python, JavaScript, TypeScript, React, Vue, FastAPI, Docker, PostgreSQL\n\n"
        "Work Experience\n"
        "Senior Developer at TechCorp (2021-Present)\n"
        "- Built microservices serving 1M daily requests.\n\n"
        "Education\n"
        "B.S. in Computer Science, UC Berkeley (2017-2021)\n"
    )
    page.insert_text((50, 50), text, fontsize=11)
    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


def create_sample_docx(tmp_path: Path) -> Path:
    """Generate a clean test DOCX resume."""
    docx_path = tmp_path / "sample_resume.docx"
    doc = docx.Document()
    doc.add_heading("Marcus Vance", level=0)
    doc.add_paragraph("marcus.vance@testmail.com | 555-876-5432 | Austin, TX")
    doc.add_heading("Skills", level=1)
    doc.add_paragraph("Python, Go, Kubernetes, AWS, Terraform, Redis")
    doc.add_heading("Projects", level=1)
    doc.add_paragraph("Cloud Pipeline Orchestrator: Built CI/CD automation in Go.")
    doc.add_heading("Education", level=1)
    doc.add_paragraph("M.S. Software Engineering, UT Austin")
    doc.save(str(docx_path))
    return docx_path


def test_parse_pdf_resume(tmp_path):
    pdf_path = create_sample_pdf(tmp_path)
    parsed = ResumeParserService.parse_document(pdf_path, "sample_resume.pdf")

    assert parsed.full_name == "Sarah Jenkins"
    assert parsed.email == "sarah.jenkins@example.com"
    assert parsed.phone == "(555) 234-5678"
    assert parsed.location == "San Francisco, CA"
    assert parsed.linkedin_url == "https://linkedin.com/in/sarahjenkins"
    assert parsed.github_url == "https://github.com/sarahj"
    assert "Python" in parsed.technical_skills
    assert "React" in parsed.technical_skills
    assert parsed.page_count == 1
    assert "TechCorp" in (parsed.relevant_experience or "")


def test_parse_docx_resume(tmp_path):
    docx_path = create_sample_docx(tmp_path)
    parsed = ResumeParserService.parse_document(docx_path, "sample_resume.docx")

    assert parsed.full_name == "Marcus Vance"
    assert parsed.email == "marcus.vance@testmail.com"
    assert "Kubernetes" in parsed.technical_skills
    assert "Cloud Pipeline Orchestrator" in (parsed.projects or "")


def test_file_validation_rejects_invalid_extension():
    storage = FileStorage(
        stream=io.BytesIO(b"malicious executable"),
        filename="resume.exe"
    )
    is_valid, msg = validate_resume_file(storage)
    assert not is_valid
    assert "Unsupported file type" in msg


def test_file_validation_rejects_corrupted_pdf():
    storage = FileStorage(
        stream=io.BytesIO(b"This is not a real PDF document"),
        filename="resume.pdf"
    )
    is_valid, msg = validate_resume_file(storage)
    assert not is_valid
    assert "Invalid PDF" in msg
