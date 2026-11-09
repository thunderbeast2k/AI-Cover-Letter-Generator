from app.services.matching_service import MatchingService


def test_matching_calculation_experienced_candidate():
    job_desc = (
        "Role: Python Backend Developer\n"
        "Requirements: Python, FastAPI, Docker, PostgreSQL, Redis, AWS.\n"
        "Requirements: 3 years experience building APIs."
    )
    candidate_skills = ["Python", "FastAPI", "Docker", "PostgreSQL", "Git"]
    candidate_exp = "3 years working as Backend Developer at Tech Startups."

    result = MatchingService.calculate_match(
        candidate_skills=candidate_skills,
        job_description=job_desc,
        candidate_experience=candidate_exp,
        job_title="Python Backend Developer",
        company_name="CloudCorp"
    )

    assert result.match_percentage >= 50
    assert "Python" in result.matched_skills
    assert "Docker" in result.matched_skills
    assert "Heuristic Breakdown" in result.scoring_explanation
    assert len(result.recommendations) > 0


def test_matching_fresher_friendly_recognition():
    job_desc = (
        "We are hiring a Junior Software Developer (Fresher / Graduate role).\n"
        "Skills: Python, React, SQL.\n"
        "No prior industry experience required. Passion for learning is key!"
    )
    candidate_skills = ["Python", "React", "SQL"]
    candidate_projects = "Built a full-stack campus management portal and an e-commerce platform using Python and React."

    result = MatchingService.calculate_match(
        candidate_skills=candidate_skills,
        job_description=job_desc,
        candidate_projects=candidate_projects,
        job_title="Junior Software Developer"
    )

    assert result.is_fresher_friendly is True
    assert result.match_percentage >= 70
    assert "Python" in result.matched_skills
