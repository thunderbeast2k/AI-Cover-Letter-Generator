import os
import re
import logging
from pathlib import Path
from typing import Optional
from werkzeug.datastructures import FileStorage

import pymupdf  # PyMuPDF
import docx

from app.utils.helpers import extract_email, extract_phone, extract_links, extract_candidate_name
from app.utils.validators import sanitize_untrusted_text
from app.schemas.response_models import ParsedResumeData

logger = logging.getLogger(__name__)

# Common section headers in resumes
SECTION_KEYWORDS = {
    "summary": ["summary", "professional summary", "about me", "profile", "objective", "career objective"],
    "skills": ["skills", "technical skills", "technologies", "core competencies", "competencies", "tools & technologies"],
    "experience": ["experience", "work experience", "employment history", "professional experience", "internships", "work history"],
    "projects": ["projects", "personal projects", "academic projects", "key projects", "notable projects"],
    "education": ["education", "academic background", "qualifications", "educational qualifications", "academic history"],
    "certifications": ["certifications", "licenses", "certificates", "credentials"],
    "achievements": ["achievements", "honors", "awards", "accomplishments", "publications"]
}


class ResumeParserService:
    """Service to safely parse PDF and DOCX resume documents into structured data."""

    @staticmethod
    def extract_text_from_pdf(file_path: str | Path) -> tuple[str, int, list[str]]:
        """Extract plain text and page count from a PDF document using PyMuPDF."""
        warnings: list[str] = []
        full_text = []
        page_count = 0

        try:
            doc = pymupdf.open(file_path)
            page_count = len(doc)
            
            if page_count == 0:
                return "", 0, ["The uploaded PDF is empty."]

            if doc.is_encrypted:
                return "", 0, ["The uploaded PDF is password-protected. Please upload an unlocked PDF."]

            for page_index in range(page_count):
                page = doc[page_index]
                text = page.get_text("text") or ""
                full_text.append(text.strip())

            doc.close()
        except Exception as e:
            logger.error(f"PyMuPDF error reading {file_path}: {e}")
            raise ValueError(f"Could not parse PDF file: {str(e)}")

        combined_text = "\n\n".join(full_text).strip()
        if not combined_text or len(combined_text) < 20:
            warnings.append(
                "Very little text was extracted. If this is a scanned document or image, "
                "please provide a text-based PDF or DOCX file."
            )

        return combined_text, page_count, warnings

    @staticmethod
    def extract_text_from_docx(file_path: str | Path) -> tuple[str, int, list[str]]:
        """Extract plain text from DOCX document using python-docx."""
        warnings: list[str] = []
        full_text = []

        try:
            doc = docx.Document(file_path)
            for p in doc.paragraphs:
                if p.text.strip():
                    full_text.append(p.text.strip())

            # Also check table contents
            for table in doc.tables:
                for row in table.rows:
                    row_texts = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                    if row_texts:
                        full_text.append(" | ".join(row_texts))
        except Exception as e:
            logger.error(f"python-docx error reading {file_path}: {e}")
            raise ValueError(f"Could not parse DOCX file: {str(e)}")

        combined_text = "\n\n".join(full_text).strip()
        if not combined_text or len(combined_text) < 20:
            warnings.append("The DOCX document contained minimal or no readable text.")

        return combined_text, 1, warnings

    @classmethod
    def parse_document(cls, file_path: str | Path, original_filename: str) -> ParsedResumeData:
        """Extract text and segment resume into structured data."""
        ext = Path(original_filename).suffix.lower()

        if ext == ".pdf":
            raw_text, page_count, warnings = cls.extract_text_from_pdf(file_path)
        elif ext == ".docx":
            raw_text, page_count, warnings = cls.extract_text_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported extension: {ext}")

        sanitized_text = sanitize_untrusted_text(raw_text)

        # Contact info & links
        email = extract_email(sanitized_text)
        phone = extract_phone(sanitized_text)
        links = extract_links(sanitized_text)
        name = extract_candidate_name(sanitized_text)

        # Detect sections
        sections = cls._segment_sections(sanitized_text)

        # Extract skills list
        skills_raw = sections.get("skills", "")
        extracted_skills = cls._extract_skills_list(skills_raw)

        # Infer location if present near header
        location = cls._extract_location(sanitized_text)

        return ParsedResumeData(
            full_name=name,
            email=email,
            phone=phone,
            location=location,
            linkedin_url=links.get("linkedin"),
            github_url=links.get("github"),
            portfolio_url=links.get("portfolio"),
            summary=sections.get("summary"),
            technical_skills=extracted_skills,
            relevant_experience=sections.get("experience"),
            projects=sections.get("projects"),
            achievements=sections.get("achievements"),
            certifications=sections.get("certifications"),
            education=sections.get("education"),
            raw_text=sanitized_text,
            page_count=page_count,
            warnings=warnings
        )

    @classmethod
    def _segment_sections(cls, text: str) -> dict[str, str]:
        """Split resume into common sections using keyword headers."""
        lines = text.splitlines()
        sections: dict[str, list[str]] = {}
        current_section = "intro"
        sections[current_section] = []

        for line in lines:
            trimmed = line.strip()
            if not trimmed:
                continue

            # Check if this line looks like a header (short, uppercase or title, matches keyword)
            clean_line = re.sub(r"[:\-_|•*#]", "", trimmed).strip().lower()
            found_section = None
            if len(clean_line) <= 35:
                for section_name, keywords in SECTION_KEYWORDS.items():
                    if clean_line in keywords or any(clean_line.startswith(kw) for kw in keywords):
                        found_section = section_name
                        break

            if found_section:
                current_section = found_section
                if current_section not in sections:
                    sections[current_section] = []
            else:
                if current_section in sections:
                    sections[current_section].append(trimmed)

        return {k: "\n".join(v).strip() for k, v in sections.items() if v}

    @staticmethod
    def _extract_skills_list(skills_text: str) -> list[str]:
        """Extract individual skills by splitting bullet points, commas, pipelines."""
        if not skills_text:
            return []

        # Split on commas, bullets, pipes, newlines
        parts = re.split(r"[,;•|\n\t\u2022\u25E6\u2219]+", skills_text)
        skills = []
        for p in parts:
            item = p.strip()
            # Remove category prefixes like "Languages: Python, Go"
            item = re.sub(r"^[A-Za-z\s]+:\s*", "", item)
            # Remove parentheses content e.g. "(proficient)"
            item = re.sub(r"\(.*?\)", "", item).strip()
            if item and len(item) < 40 and not item.lower().startswith("skills"):
                if item not in skills:
                    skills.append(item)
        return skills[:40]  # Cap reasonable limit

    @staticmethod
    def _extract_location(text: str) -> Optional[str]:
        """Look for City, State / Country patterns in the first 10 lines."""
        lines = [l.strip() for l in text.splitlines()[:10] if l.strip()]
        # Matches patterns like "San Francisco, CA" or "Austin, Texas" or "London, UK"
        pattern = r"\b[A-Z][a-zA-Z\s]+,\s*[A-Z]{2}\b|\b[A-Z][a-zA-Z\s]+,\s*[A-Z][a-zA-Z]+\b"
        for line in lines:
            match = re.search(pattern, line)
            if match:
                return match.group(0)
        return None
