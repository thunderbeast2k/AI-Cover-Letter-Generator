import pytest
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["status"] in ("Connected", "Not Connected")
    assert "config" in json_data
    assert json_data["config"]["model"] == "gemini-3.8-flash"
    assert "has_gemini_key" in json_data["config"]
    assert "connection" in json_data
    assert "connected" in json_data["connection"]


def test_not_found_endpoint(client):
    response = client.get("/api/nonexistent-route")
    assert response.status_code == 404
    json_data = response.get_json()
    assert json_data["success"] is False
    assert "Endpoint not found" in json_data["error"]


def test_generate_letter_endpoint(client):
    payload = {
        "personal_info": {"full_name": "Jane Smith", "email": "jane@example.com"},
        "job_info": {
            "job_title": "Full Stack Developer",
            "company_name": "InnovateCorp",
            "job_description": "We are looking for a Python and Vue developer."
        },
        "professional_info": {
            "technical_skills": ["Python", "Flask", "Vue.js"]
        },
        "writing_style": "Professional"
    }
    response = client.post("/api/letters/generate", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert "InnovateCorp" in data["data"]["cover_letter"]
    assert "Jane Smith" in data["data"]["cover_letter"]


def test_generate_letter_validation_error(client):
    # Missing required job_title and company_name
    payload = {
        "personal_info": {"full_name": "Jane Smith"},
        "job_info": {
            "job_title": "",
            "company_name": "",
            "job_description": "short"
        },
        "professional_info": {}
    }
    response = client.post("/api/letters/generate", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert "job_info" in data["error"]
