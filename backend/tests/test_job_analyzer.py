from app.services.job_analyzer import JobAnalyzerService


def test_heuristic_job_analysis():
    job_desc = (
        "We are looking for a Senior Full Stack Engineer at Acme Innovations.\n"
        "Requirements:\n"
        "- Strong proficiency in Python, TypeScript, and React.\n"
        "- Experience with Docker, PostgreSQL, and AWS cloud architecture.\n"
        "- 3+ years of experience building production APIs.\n"
        "- Bachelor's degree in Computer Science or related field.\n\n"
        "Responsibilities:\n"
        "- Build resilient microservices and frontend web apps.\n"
        "- Collaborate with designers and product leads.\n"
        "- Maintain high automated test coverage."
    )

    data = JobAnalyzerService.analyze_heuristic(
        job_description=job_desc,
        job_title="Full Stack Engineer",
        company_name="Acme Innovations"
    )

    assert data.job_title == "Full Stack Engineer"
    assert data.company_name == "Acme Innovations"
    assert "Python" in data.programming_languages
    assert "TypeScript" in data.programming_languages
    assert "React" in data.frameworks
    assert "Docker" in data.tools
    assert "3+ years" in data.experience_requirements.lower() or "years" in data.experience_requirements.lower()
    assert len(data.responsibilities) > 0
    assert len(data.keywords) > 0
