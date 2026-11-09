import re
import json
import logging
from typing import Optional

from app.schemas.response_models import JobAnalysisData
from app.utils.validators import sanitize_untrusted_text

logger = logging.getLogger(__name__)

COMMON_LANGUAGES = [
    "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Golang", "Rust", "Ruby",
    "PHP", "Swift", "Kotlin", "SQL", "HTML", "CSS", "Bash", "Shell", "R", "Scala", "Dart"
]

COMMON_FRAMEWORKS = [
    "React", "Vue", "Vue.js", "Angular", "Next.js", "Nuxt", "Svelte", "Node.js", "Express",
    "Django", "Flask", "FastAPI", "Spring Boot", "ASP.NET", ".NET", "Ruby on Rails", "Laravel",
    "Tailwind CSS", "Bootstrap", "PyTorch", "TensorFlow", "Scikit-Learn", "Pandas"
]

COMMON_TOOLS = [
    "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Google Cloud", "Git", "GitHub", "GitLab",
    "CI/CD", "Jenkins", "Linux", "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch",
    "GraphQL", "REST APIs", "Kafka", "Terraform", "Postman", "Figma", "Jira"
]

COMMON_SOFT_SKILLS = [
    "Communication", "Problem-solving", "Team collaboration", "Critical thinking",
    "Adaptability", "Time management", "Attention to detail", "Leadership",
    "Work ethic", "Empathy", "Creativity", "Conflict resolution"
]


class JobAnalyzerService:
    """Service to parse and extract structured requirements from job descriptions."""

    @classmethod
    def analyze_heuristic(
        cls,
        job_description: str,
        job_title: Optional[str] = None,
        company_name: Optional[str] = None
    ) -> JobAnalysisData:
        """Heuristic analysis of job description text using keyword extraction and patterns."""
        clean_text = sanitize_untrusted_text(job_description)

        # 1. Infer job title if not provided
        inferred_title = job_title
        if not inferred_title:
            title_match = re.search(
                r"(?i)(?:role|position|job\s+title|we\s+are\s+hiring\s+a(?:n)?)\s*[:\-]?\s*([A-Za-z\s/]{3,40})",
                clean_text[:500]
            )
            if title_match:
                inferred_title = title_match.group(1).strip()
            else:
                first_line = clean_text.splitlines()[0] if clean_text else ""
                if len(first_line) < 50:
                    inferred_title = first_line.strip()

        # 2. Extract technical languages, frameworks, tools
        found_langs = cls._find_matches(clean_text, COMMON_LANGUAGES)
        found_frameworks = cls._find_matches(clean_text, COMMON_FRAMEWORKS)
        found_tools = cls._find_matches(clean_text, COMMON_TOOLS)
        found_soft = cls._find_matches(clean_text, COMMON_SOFT_SKILLS)

        # 3. Categorize into required and preferred skills
        required_skills = []
        preferred_skills = []

        # Look for sections like "Requirements" vs "Nice to have"
        lines = clean_text.splitlines()
        current_bucket = "required"
        for line in lines:
            lower = line.lower()
            if any(term in lower for term in ["nice to have", "preferred", "bonus", "plus", "desirable"]):
                current_bucket = "preferred"
            elif any(term in lower for term in ["requirement", "qualifications", "must have", "what you need", "who you are"]):
                current_bucket = "required"

            for skill in found_langs + found_frameworks + found_tools:
                pattern = r"\b" + re.escape(skill) + r"\b"
                if re.search(pattern, line, re.IGNORECASE):
                    if current_bucket == "preferred":
                        if skill not in preferred_skills:
                            preferred_skills.append(skill)
                    else:
                        if skill not in required_skills:
                            required_skills.append(skill)

        # Ensure required has items if empty
        if not required_skills and (found_langs or found_frameworks):
            required_skills = (found_langs + found_frameworks)[:8]

        # 4. Experience requirements pattern
        exp_match = re.search(
            r"(?i)(\d+[\+\-]?\s*(?:to\s*\d+)?\s*years?(?:\s+of)?\s*(?:experience|exp)?)|\b(?:entry[- ]level|fresh\s+grad(?:uate)?|internship|no\s+prior\s+experience)\b",
            clean_text
        )
        experience_req = exp_match.group(0).strip() if exp_match else "Experience level not explicitly stated"

        # 5. Educational qualifications
        edu_match = re.search(
            r"(?i)(?:bachelor['’]?s|master['’]?s|phd|degree\s+in\s+[a-zA-Z\s]+|bs|ms|computer\s+science|equivalent\s+practical\s+experience)",
            clean_text
        )
        education_req = edu_match.group(0).strip() if edu_match else "Degree or equivalent practical experience"

        # 6. Extract responsibilities (bullet points or action lines)
        responsibilities = cls._extract_responsibilities(clean_text)

        # 7. Important keywords
        keywords = list(dict.fromkeys(required_skills + preferred_skills + found_soft + [
            "Team Collaboration", "Agile", "Problem Solving", "Scalability", "Clean Code"
        ]))[:15]

        return JobAnalysisData(
            job_title=inferred_title,
            company_name=company_name,
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            programming_languages=found_langs,
            frameworks=found_frameworks,
            tools=found_tools,
            experience_requirements=experience_req,
            educational_qualifications=education_req,
            responsibilities=responsibilities,
            keywords=keywords,
            soft_skills=found_soft
        )

    @staticmethod
    def _find_matches(text: str, targets: list[str]) -> list[str]:
        found = []
        for item in targets:
            # Word boundary regex with special character safety
            pattern = r"(?<!\w)" + re.escape(item) + r"(?!\w)"
            if re.search(pattern, text, re.IGNORECASE):
                found.append(item)
        return found

    @staticmethod
    def _extract_responsibilities(text: str) -> list[str]:
        """Extract lines that look like job duties/responsibilities."""
        lines = text.splitlines()
        responsibilities = []
        in_resp_section = False

        for line in lines:
            trimmed = line.strip()
            if not trimmed:
                continue

            lower = trimmed.lower()
            if any(term in lower for term in ["responsibilities", "what you will do", "what you'll do", "the role", "duties"]):
                in_resp_section = True
                continue
            elif in_resp_section and any(term in lower for term in ["qualifications", "requirements", "about you", "benefits"]):
                in_resp_section = False
                break

            if in_resp_section:
                # Remove bullets
                clean = re.sub(r"^[\*\-•\d\.\)]\s*", "", trimmed)
                if len(clean) > 15 and len(clean) < 200:
                    responsibilities.append(clean)

        # Fallback: find lines starting with action verbs
        if not responsibilities:
            action_verbs = ["Develop", "Build", "Design", "Collaborate", "Implement", "Maintain", "Create", "Manage", "Optimize"]
            for line in lines:
                trimmed = line.strip()
                clean = re.sub(r"^[\*\-•\d\.\)]\s*", "", trimmed)
                if any(clean.startswith(verb) for verb in action_verbs) and len(clean) > 20:
                    responsibilities.append(clean)

        return responsibilities[:6]
