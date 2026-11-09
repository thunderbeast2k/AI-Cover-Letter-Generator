import pytest
from unittest.mock import MagicMock
from app.services.ai_service import AIService
from app.config import Config


import json
import pytest
from unittest.mock import MagicMock
from openai import AuthenticationError, RateLimitError, APIConnectionError
from app.services.ai_service import AIService
from app.config import Config


def test_ai_demo_mode_generation():
    Config.DEMO_MODE = True
    Config.GEMINI_API_KEY = ""

    personal = {"full_name": "Jordan Lee", "email": "jordan@example.com"}
    job = {"job_title": "Frontend Engineer", "company_name": "PixelWorks", "hiring_manager_name": "Tech Lead"}
    prof = {"technical_skills": ["Vue 3", "TypeScript", "Tailwind CSS"], "projects": "SaaS Dashboard"}

    res = AIService.generate_cover_letter(personal, job, prof, writing_style="Technical")

    assert res.demo_mode is True
    assert "PixelWorks" in res.cover_letter
    assert "Jordan Lee" in res.cover_letter
    assert res.word_count > 50


def test_ai_missing_key_error(monkeypatch):
    monkeypatch.setattr(Config, "DEMO_MODE", False)
    monkeypatch.setattr(Config, "GEMINI_API_KEY", "")
    monkeypatch.setenv("GEMINI_API_KEY", "")

    personal = {"full_name": "Jordan Lee"}
    job = {"job_title": "Engineer", "company_name": "Acme"}
    prof = {}

    with pytest.raises(ValueError) as excinfo:
        AIService.generate_cover_letter(personal, job, prof)
    assert "Gemini API key is missing" in str(excinfo.value)


def test_ai_mocked_gemini_call(monkeypatch):
    monkeypatch.setattr(Config, "DEMO_MODE", False)
    monkeypatch.setattr(Config, "GEMINI_API_KEY", "AIzaSyMockKey1234567890")

    mock_client = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "Dear Hiring Manager,\n\nI am thrilled to apply for the role...\n\nSincerely,\nJordan Lee"
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_response

    monkeypatch.setattr(AIService, "get_client", classmethod(lambda cls: mock_client))

    personal = {"full_name": "Jordan Lee"}
    job = {"job_title": "Full Stack Dev", "company_name": "NovaLab"}
    prof = {"technical_skills": ["Python"]}

    result = AIService.generate_cover_letter(personal, job, prof, writing_style="Professional")
    assert result.demo_mode is False
    assert "Jordan Lee" in result.cover_letter
    assert mock_client.chat.completions.create.called


def test_gemini_test_connection_success(monkeypatch):
    monkeypatch.setattr(Config, "GEMINI_API_KEY", "AIzaSyMockKey1234567890")
    monkeypatch.setattr(Config, "DEMO_MODE", False)

    mock_client = MagicMock()
    mock_client.models.retrieve.return_value = MagicMock(id="gemini-3.8-flash")
    monkeypatch.setattr(AIService, "get_client", classmethod(lambda cls: mock_client))

    status, msg = AIService.test_connection()
    assert status == "Connected"
    assert "Gemini API connection verified" in msg


def test_gemini_test_connection_invalid_key(monkeypatch):
    monkeypatch.setattr(Config, "GEMINI_API_KEY", "invalid_key")
    monkeypatch.setattr(Config, "DEMO_MODE", False)

    mock_client = MagicMock()
    mock_client.models.retrieve.side_effect = Exception("API key not valid. Please pass a valid API key.")
    monkeypatch.setattr(AIService, "get_client", classmethod(lambda cls: mock_client))

    status, msg = AIService.test_connection()
    assert status == "Not Connected"
    assert "Invalid Gemini API key" in msg


def test_gemini_test_connection_missing_key(monkeypatch):
    monkeypatch.setattr(Config, "GEMINI_API_KEY", "")
    monkeypatch.setenv("GEMINI_API_KEY", "")
    monkeypatch.setattr(Config, "DEMO_MODE", False)

    status, msg = AIService.test_connection()
    assert status == "Not Connected"
    assert "GEMINI_API_KEY is not configured" in msg


def test_gemini_four_ai_operations_mocked(monkeypatch):
    monkeypatch.setattr(Config, "DEMO_MODE", False)
    monkeypatch.setattr(Config, "GEMINI_API_KEY", "AIzaSyMockKey1234567890")

    mock_client = MagicMock()

    # 1. Generate cover letter
    choice1 = MagicMock()
    choice1.message.content = "Dear Recruiter,\n\nI am applying for Frontend Lead.\n\nSincerely,\nAlice"

    # 2. Analyze job
    choice2 = MagicMock()
    analysis_dict = {
        "job_title": "Frontend Lead",
        "company_name": "Apex",
        "responsibilities": ["Lead UI development"],
        "required_skills": ["Vue", "TypeScript"],
        "preferred_skills": ["Tailwind"],
        "soft_skills": ["Mentorship"],
        "programming_languages": ["TypeScript"],
        "frameworks": ["Vue 3"],
        "tools": ["Vite"],
        "keywords": ["Vue", "Frontend"]
    }
    choice2.message.content = json.dumps(analysis_dict)

    # 3. Improve cover letter
    choice3 = MagicMock()
    choice3.message.content = "Dear Hiring Manager,\n\nRevised and strengthened cover letter.\n\nBest,\nAlice"

    # 4. Check quality
    choice4 = MagicMock()
    quality_dict = {
        "overall_score": 92,
        "assessment": "Excellent letter",
        "positive_observations": ["Great alignment", "Concise prose"],
        "areas_for_improvement": ["Add more metrics"],
        "specific_suggestions": [
            {
                "category": "Impact",
                "issue": "Needs metrics",
                "recommendation": "Mention 30% speedup",
                "example_snippet": "Improved performance by 30%"
            }
        ],
        "metrics": {
            "ats_compatibility": 95,
            "tone_consistency": 90,
            "persuasiveness": 92,
            "relevance": 94,
            "clarity": 90
        }
    }
    choice4.message.content = json.dumps(quality_dict)

    mock_resp1 = MagicMock(choices=[choice1])
    mock_resp2 = MagicMock(choices=[choice2])
    mock_resp3 = MagicMock(choices=[choice3])
    mock_resp4 = MagicMock(choices=[choice4])

    mock_client.chat.completions.create.side_effect = [
        mock_resp1,
        mock_resp2,
        mock_resp3,
        mock_resp4
    ]

    monkeypatch.setattr(AIService, "get_client", classmethod(lambda cls: mock_client))

    # Test 1: Generate
    res1 = AIService.generate_cover_letter({"full_name": "Alice"}, {"job_title": "Frontend Lead", "company_name": "Apex"}, {})
    assert "Frontend Lead" in res1.cover_letter or "Alice" in res1.cover_letter
    assert res1.demo_mode is False

    # Test 2: Analyze
    res2 = AIService.analyze_job_description("We are hiring a Frontend Lead at Apex with Vue.")
    assert res2.job_title == "Frontend Lead"
    assert "Vue" in res2.required_skills

    # Test 3: Improve
    res3 = AIService.improve_cover_letter("Original letter", "Make it punchier")
    assert "Revised" in res3

    # Test 4: Quality Check
    res4 = AIService.check_cover_letter_quality("Draft letter")
    assert res4.overall_score == 92
    assert len(res4.positive_observations) == 2


def test_quality_check_demo():
    letter = (
        "Dear Hiring Manager,\n\n"
        "I am writing to express my interest in the Senior Developer role. "
        "With 5 years of experience in Python and distributed systems, I have delivered scalable solutions. "
        "I look forward to discussing how my experience can benefit your team.\n\n"
        "Sincerely,\nTaylor Swift"
    )
    quality = AIService.check_cover_letter_quality(letter)
    assert quality.overall_score > 0
    assert len(quality.positive_observations) > 0
    assert len(quality.specific_suggestions) > 0
