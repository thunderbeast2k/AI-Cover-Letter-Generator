import re
from typing import Optional
from app.schemas.response_models import ResumeMatchData
from app.services.job_analyzer import JobAnalyzerService


class MatchingService:
    """Calculates transparent, heuristic-based resume-to-job match estimates."""

    @classmethod
    def calculate_match(
        cls,
        candidate_skills: list[str],
        job_description: str,
        resume_text: Optional[str] = None,
        candidate_experience: Optional[str] = None,
        candidate_projects: Optional[str] = None,
        candidate_education: Optional[str] = None,
        job_title: Optional[str] = None,
        company_name: Optional[str] = None
    ) -> ResumeMatchData:
        # 1. Analyze the job description
        analysis = JobAnalyzerService.analyze_heuristic(
            job_description=job_description,
            job_title=job_title,
            company_name=company_name
        )

        all_job_skills = list(dict.fromkeys(analysis.required_skills + analysis.preferred_skills + analysis.programming_languages + analysis.frameworks + analysis.tools))
        
        # Normalize candidate skills
        candidate_skills_normalized = {s.strip().lower() for s in candidate_skills if s.strip()}
        
        # Also scan full resume_text or experience/projects for mentioned skills
        combined_candidate_text = f"{resume_text or ''} {candidate_experience or ''} {candidate_projects or ''} {' '.join(candidate_skills)}".lower()

        matched_skills: list[str] = []
        missing_skills: list[str] = []

        for skill in all_job_skills:
            skill_lower = skill.lower()
            # Match directly or by regex boundary
            pattern = r"(?<!\w)" + re.escape(skill_lower) + r"(?!\w)"
            if skill_lower in candidate_skills_normalized or re.search(pattern, combined_candidate_text):
                matched_skills.append(skill)
            else:
                missing_skills.append(skill)

        # Detect if the role is entry-level / fresher friendly
        job_desc_lower = job_description.lower()
        is_fresher_friendly = any(
            term in job_desc_lower
            for term in ["entry level", "entry-level", "junior", "graduate", "fresher", "intern", "internship", "0-1 year", "new grad"]
        )

        # SCORING HEURISTIC:
        # Skill Alignment: Up to 50 points
        if all_job_skills:
            skill_ratio = len(matched_skills) / len(all_job_skills)
            skill_score = min(50, int(skill_ratio * 50))
        else:
            skill_score = 40  # default when job doesn't list explicit tools

        # Project & Hands-On Evidence: Up to 25 points
        project_score = 0
        if candidate_projects and len(candidate_projects.strip()) > 40:
            project_score = 25
        elif candidate_experience and len(candidate_experience.strip()) > 40:
            project_score = 25
        elif len(matched_skills) >= 3:
            project_score = 15

        # Keywords & Relevant Context: Up to 15 points
        keyword_hits = 0
        for kw in analysis.keywords:
            if re.search(r"(?<!\w)" + re.escape(kw.lower()) + r"(?!\w)", combined_candidate_text):
                keyword_hits += 1
        keyword_score = min(15, keyword_hits * 3)

        # Education / Foundation: Up to 10 points
        edu_score = 10 if (candidate_education and len(candidate_education.strip()) > 10) else 5

        # Total heuristic score
        total_score = min(98, max(20, skill_score + project_score + keyword_score + edu_score))

        # Build transparent explanation
        scoring_explanation = (
            f"Heuristic Breakdown: Technical Skills ({skill_score}/50 pts, {len(matched_skills)} of {len(all_job_skills)} detected), "
            f"Projects & Applied Evidence ({project_score}/25 pts), "
            f"Keyword Overlap ({keyword_score}/15 pts), "
            f"Education & Foundation ({edu_score}/10 pts). "
            f"Note: This is an automated semantic match estimate, not an ATS pass/fail guarantee."
        )

        # Experience summary
        if is_fresher_friendly:
            exp_summary = (
                "This role appears welcoming to early-career or graduate candidates. "
                "Your academic projects, foundational coursework, and hands-on coding repositories "
                "are high-leverage assets."
            )
        else:
            exp_summary = (
                f"Candidate exhibits alignment with {len(matched_skills)} core technical criteria. "
                "Emphasizing real-world outcomes and production deployments in your cover letter will strengthen competitiveness."
            )

        # Recommendations
        recommendations = []
        if missing_skills:
            top_missing = missing_skills[:4]
            recommendations.append(
                f"Consider highlighting related coursework, personal experiments, or equivalent tooling for: {', '.join(top_missing)}."
            )
        if not candidate_projects or len(candidate_projects) < 50:
            recommendations.append("Detail 1-2 concrete capstone or open-source projects demonstrating practical implementation.")
        if keyword_hits < 3 and analysis.keywords:
            recommendations.append(
                f"Naturally weave in target terminology such as: {', '.join(analysis.keywords[:3])}."
            )
        recommendations.append("Tailor your opening paragraph directly to this company's product challenges or mission.")

        # Suggested keywords
        suggested_keywords = [k for k in analysis.keywords if k not in matched_skills][:8]

        return ResumeMatchData(
            match_percentage=total_score,
            scoring_explanation=scoring_explanation,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            suggested_keywords=suggested_keywords,
            experience_match_summary=exp_summary,
            recommendations=recommendations,
            is_fresher_friendly=is_fresher_friendly
        )
