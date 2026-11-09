# AI Cover Letter Generator - API Documentation

The backend exposes a clean RESTful JSON API running on `http://127.0.0.1:5000/api`.

---

## 1. Health & Configuration

### `GET /api/health`
Checks backend connectivity and service configuration.

**Response `200 OK`**:
```json
{
  "status": "healthy",
  "service": "AI Cover Letter Generator API",
  "version": "1.0.0",
  "config": {
    "model": "gpt-4o-mini",
    "has_openai_key": true,
    "demo_mode": false,
    "max_upload_size_mb": 5.0
  }
}
```

---

## 2. Resume Parsing & Matching

### `POST /api/resume/parse`
Extracts structured credentials from an uploaded PDF or DOCX file.

- **Content-Type**: `multipart/form-data`
- **Body**: `file` (Binary FileStorage, <= 5MB)

**Response `200 OK`**:
```json
{
  "success": true,
  "data": {
    "full_name": "Jordan Miller",
    "email": "jordan.miller@example.com",
    "phone": "(555) 123-4567",
    "location": "San Francisco, CA",
    "linkedin_url": "https://linkedin.com/in/jordanm",
    "github_url": "https://github.com/jordanm",
    "summary": "Full Stack Engineer with 4 years experience...",
    "technical_skills": ["Python", "TypeScript", "React", "Docker", "PostgreSQL"],
    "relevant_experience": "Software Engineer at TechCorp...",
    "projects": "Distributed Job Scheduler...",
    "education": "B.S. in Computer Science",
    "raw_text": "...",
    "page_count": 1,
    "warnings": []
  }
}
```

---

### `POST /api/resume/match`
Calculates transparent heuristic match estimate between candidate credentials and target job requirements.

- **Content-Type**: `application/json`
- **Body**:
```json
{
  "candidate_skills": ["Python", "FastAPI", "React", "Docker"],
  "job_description": "We need a Senior Backend Developer with Python, FastAPI, Docker, and Kubernetes...",
  "candidate_experience": "3 years building APIs",
  "candidate_projects": "Built cloud container orchestrator",
  "job_title": "Backend Developer",
  "company_name": "CloudWorks"
}
```

**Response `200 OK`**:
```json
{
  "success": true,
  "data": {
    "match_percentage": 82,
    "scoring_explanation": "Heuristic Breakdown: Technical Skills (40/50 pts, 3 of 4 detected)...",
    "matched_skills": ["Python", "FastAPI", "Docker"],
    "missing_skills": ["Kubernetes"],
    "suggested_keywords": ["Kubernetes", "Scalability"],
    "experience_match_summary": "Candidate exhibits strong alignment with 3 core technical criteria...",
    "recommendations": ["Highlight personal labs or container workflows with Kubernetes."],
    "is_fresher_friendly": false
  }
}
```

---

## 3. Job Description Analysis

### `POST /api/jobs/analyze`
Extracts structured skills, tools, experience expectations, and keywords from raw job posting text.

- **Content-Type**: `application/json`
- **Body**:
```json
{
  "job_title": "Full Stack Engineer",
  "company_name": "Acme Innovations",
  "job_description": "Looking for a Full Stack Engineer with Vue 3, TypeScript, and Python..."
}
```

**Response `200 OK`**:
```json
{
  "success": true,
  "data": {
    "job_title": "Full Stack Engineer",
    "company_name": "Acme Innovations",
    "required_skills": ["Vue 3", "TypeScript", "Python"],
    "preferred_skills": ["Tailwind CSS", "Docker"],
    "programming_languages": ["TypeScript", "Python"],
    "frameworks": ["Vue", "Vue 3"],
    "tools": ["Docker"],
    "experience_requirements": "3+ years",
    "educational_qualifications": "Bachelor's degree or equivalent experience",
    "responsibilities": ["Build responsive web apps"],
    "keywords": ["Vue 3", "TypeScript", "Python", "Clean Code"],
    "soft_skills": ["Communication", "Team collaboration"]
  }
}
```

---

## 4. Cover Letter Generation & Refinement

### `POST /api/letters/generate`
Generates a customized, factually grounded cover letter.

- **Content-Type**: `application/json`
- **Body**:
```json
{
  "personal_info": {
    "full_name": "Alex Taylor",
    "email": "alex@example.com",
    "location": "Seattle, WA"
  },
  "job_info": {
    "job_title": "Senior Engineer",
    "company_name": "PixelCorp",
    "job_description": "Architect high performance web apps..."
  },
  "professional_info": {
    "technical_skills": ["Python", "FastAPI", "Docker"],
    "projects": "High-throughput API"
  },
  "writing_style": "Professional",
  "template_id": "classic"
}
```

---

### `POST /api/letters/improve`
Refines the letter or rewrites selected excerpts.

- **Content-Type**: `application/json`
- **Body**:
```json
{
  "cover_letter": "Current text of the letter...",
  "action": "make_concise",
  "selected_text": null,
  "job_title": "Senior Engineer",
  "company_name": "PixelCorp"
}
```

Supported actions:
- `improve_writing`
- `make_professional`
- `make_concise`
- `make_confident`
- `improve_technical`
- `improve_opening`
- `improve_closing`
- `fix_grammar`
- `rewrite_selection`

---

### `POST /api/letters/quality`
Returns comprehensive quality metrics, strengths, and actionable suggestions.

- **Content-Type**: `application/json`
- **Body**:
```json
{
  "cover_letter": "Full text of letter...",
  "job_description": "Target job description text...",
  "job_title": "Lead Developer"
}
```

---

## 5. Document Exports

### `POST /api/letters/export/pdf`
Returns a dynamically rendered PDF file stream (`application/pdf`).

### `POST /api/letters/export/docx`
Returns an editable Microsoft Word document stream (`application/vnd.openxmlformats-officedocument.wordprocessingml.document`).
