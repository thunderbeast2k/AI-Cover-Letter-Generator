from app.services.document_service import DocumentService
from app.schemas.request_models import PersonalInfo, JobInfo


def get_sample_info():
    personal = PersonalInfo(
        full_name="Elena Rostova",
        email="elena.rostova@example.com",
        phone="555-123-9876",
        location="Seattle, WA",
        linkedin_url="https://linkedin.com/in/elenarostova",
        github_url="https://github.com/elenar"
    )
    job = JobInfo(
        job_title="Lead Data Engineer",
        company_name="Vanguard Analytics",
        hiring_manager_name="Hiring Team",
        company_location="Seattle, WA",
        job_description="Seeking a talented Data Engineer to lead pipeline scaling."
    )
    letter = (
        "Dear Hiring Team,\n\n"
        "I am writing to express my enthusiastic interest in the Lead Data Engineer role at Vanguard Analytics. "
        "With deep expertise in distributed data architecture and cloud systems, I am excited about the opportunity "
        "to contribute to your data infrastructure.\n\n"
        "In my previous roles, I designed automated ETL pipelines processing multi-terabyte datasets daily. "
        "I welcome the chance to bring this hands-on engineering focus to Vanguard Analytics.\n\n"
        "Sincerely,\nElena Rostova"
    )
    return personal, job, letter


def test_pdf_export_all_templates():
    personal, job, letter = get_sample_info()

    for tmpl in ["classic", "minimal", "technical", "graduate", "internship"]:
        pdf_bytes = DocumentService.generate_pdf(
            cover_letter=letter,
            personal_info=personal,
            job_info=job,
            template_id=tmpl
        )
        assert len(pdf_bytes) > 500
        # Check PDF magic header
        assert pdf_bytes.startswith(b"%PDF-")


def test_docx_export_all_templates():
    personal, job, letter = get_sample_info()

    for tmpl in ["classic", "minimal", "technical"]:
        docx_bytes = DocumentService.generate_docx(
            cover_letter=letter,
            personal_info=personal,
            job_info=job,
            template_id=tmpl
        )
        assert len(docx_bytes) > 500
        # Check DOCX ZIP magic header
        assert docx_bytes.startswith(b"PK\x03\x04")
