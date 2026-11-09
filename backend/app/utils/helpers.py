import re
from typing import Optional


def extract_email(text: str) -> Optional[str]:
    """Find the first valid email address in text."""
    pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    match = re.search(pattern, text)
    return match.group(0).strip(".,") if match else None


def extract_phone(text: str) -> Optional[str]:
    """Find phone number formatted with international or local digits."""
    # Matches formats like: +1 (555) 123-4567, 555-123-4567, +91 9876543210, (123) 456 7890
    pattern = r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
    match = re.search(pattern, text)
    if match:
        return match.group(0).strip()

    # Generic 10-digit number
    pattern2 = r"\b\d{10}\b"
    match2 = re.search(pattern2, text)
    return match2.group(0) if match2 else None


def extract_links(text: str) -> dict[str, Optional[str]]:
    """Extract LinkedIn, GitHub, and portfolio links from text."""
    links = {
        "linkedin": None,
        "github": None,
        "portfolio": None,
    }

    # LinkedIn
    linkedin_match = re.search(r"https?://(?:www\.)?linkedin\.com/in/[\w\-_/]+", text, re.IGNORECASE)
    if linkedin_match:
        links["linkedin"] = linkedin_match.group(0)

    # GitHub
    github_match = re.search(r"https?://(?:www\.)?github\.com/[\w\-_/]+", text, re.IGNORECASE)
    if github_match:
        links["github"] = github_match.group(0)

    # Portfolio / generic personal website
    portfolio_match = re.search(
        r"https?://(?:www\.)?(?!linkedin|github)[\w\-_]+\.(?:io|me|dev|com|org|net|app)(?:/[\w\-_/]+)?",
        text,
        re.IGNORECASE,
    )
    if portfolio_match:
        links["portfolio"] = portfolio_match.group(0)

    return links


def extract_candidate_name(text: str) -> Optional[str]:
    """
    Attempt to extract applicant name from the top header lines of a resume.
    Usually the name appears in the first 3-5 lines without numbers or special labels.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in lines[:5]:
        # Filter out lines that look like emails, URLs, addresses, or phone numbers
        if "@" in line or "http" in line or "linkedin" in line:
            continue
        if re.search(r"\d", line):
            continue
        if len(line.split()) in (2, 3, 4) and len(line) <= 40:
            # Check title-case or uppercase letters
            if re.match(r"^[A-Za-z\s\.\'-]+$", line):
                return line.title()
    return None
