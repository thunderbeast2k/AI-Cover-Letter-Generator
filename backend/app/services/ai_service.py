import os
import json
import logging
import re
from typing import Optional

from openai import (
    OpenAI,
    OpenAIError,
    AuthenticationError,
    RateLimitError,
    APIConnectionError,
    NotFoundError,
    BadRequestError,
)

from app.config import Config
from app.schemas.response_models import (
    GeneratedLetterData,
    JobAnalysisData,
    LetterQualityData,
    SpecificSuggestion,
)
from app.services.prompt_service import (
    build_system_prompt,
    build_cover_letter_user_prompt,
    build_job_analyzer_prompt,
    build_improvement_prompt,
    build_quality_check_prompt,
)
from app.services.job_analyzer import JobAnalyzerService


logger = logging.getLogger(__name__)


class AIService:
    """
    AI service using Google's Gemini API through its OpenAI-compatible endpoint.

    The prompt builders, response schemas, and demo-mode functions
    are retained so the application functions seamlessly.
    """

    GEMINI_BASE_URL = (
        "https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    DEFAULT_MODEL = "gemini-3.8-flash"

    _client: Optional[OpenAI] = None

    @classmethod
    def _get_api_key(cls) -> str:
        """Read the Gemini API key from the environment or Flask Config."""
        return (
            os.getenv("GEMINI_API_KEY")
            or getattr(Config, "GEMINI_API_KEY", "")
            or ""
        ).strip()

    @classmethod
    def _get_model(cls) -> str:
        """Read the configured Gemini model."""
        return (
            os.getenv("GEMINI_MODEL")
            or os.getenv("AI_MODEL")
            or getattr(Config, "GEMINI_MODEL", None)
            or cls.DEFAULT_MODEL
        ).strip()

    @classmethod
    def _demo_mode_enabled(cls) -> bool:
        """Check whether offline demo mode is enabled."""
        return bool(getattr(Config, "DEMO_MODE", False))

    @classmethod
    def get_client(cls) -> OpenAI:
        """Initialize or retrieve singleton OpenAI client configured for Gemini."""
        api_key = cls._get_api_key()

        if not api_key:
            raise ValueError(
                "Gemini API key is missing. Add GEMINI_API_KEY to "
                "backend/.env and restart the Flask backend, or set DEMO_MODE=true."
            )

        if cls._client is None or cls._client.api_key != api_key:
            cls._client = OpenAI(
                api_key=api_key,
                base_url=cls.GEMINI_BASE_URL,
                timeout=45.0,
                max_retries=1,
            )

        return cls._client

    @classmethod
    def test_connection(cls) -> tuple[str, str]:
        """
        Perform a genuine connection test against the Gemini API.
        Returns: (status: 'Connected' | 'Not Connected', message: str)
        """
        api_key = cls._get_api_key()
        model = cls._get_model()

        if not api_key:
            if cls._demo_mode_enabled():
                return "Connected", "Demo Mode is active (offline generation)."
            return "Not Connected", "GEMINI_API_KEY is not configured in backend/.env."

        try:
            client = cls.get_client()
            # Retrieve model metadata to verify key and model validity with Google
            client.models.retrieve(model)
            return "Connected", f"Gemini API connection verified ({model})."
        except RateLimitError as rle:
            logger.warning("Gemini rate limit in health check: %s", rle)
            return "Connected", f"Gemini API connected ({model}). Note: Rate limit or quota warning."
        except AuthenticationError as ae:
            logger.warning("Gemini authentication failed: %s", ae)
            return "Not Connected", "Invalid Gemini API key. Please check GEMINI_API_KEY in backend/.env."
        except NotFoundError as nfe:
            logger.warning("Gemini model not found: %s", nfe)
            return "Not Connected", f"Configured Gemini model '{model}' was not found. Check GEMINI_MODEL in backend/.env."
        except APIConnectionError as ace:
            logger.warning("Gemini connection error: %s", ace)
            return "Not Connected", "Unable to connect to Google Gemini API servers. Check network/firewall."
        except Exception as e:
            err_msg = str(e)
            if "API key not valid" in err_msg or "API_KEY_INVALID" in err_msg or "400" in err_msg:
                return "Not Connected", "Invalid Gemini API key. Please pass a valid API key."
            if "404" in err_msg:
                return "Not Connected", f"Model '{model}' not found on Gemini API."
            if "Connection" in err_msg:
                return "Not Connected", "Unable to connect to Google Gemini API servers."
            logger.warning("Gemini connection test failed: %s", e)
            return "Not Connected", f"Gemini API error: {err_msg[:120]}"

    @classmethod
    def _format_gemini_error(cls, e: Exception, model: str) -> str:
        """Convert low-level API exceptions into friendly, actionable error messages."""
        err_str = str(e)
        if isinstance(e, AuthenticationError) or "API key not valid" in err_str or "API_KEY_INVALID" in err_str:
            return "Invalid Gemini API key. Please verify your GEMINI_API_KEY in backend/.env."
        if isinstance(e, RateLimitError) or "RESOURCE_EXHAUSTED" in err_str or "quota" in err_str.lower() or "429" in err_str:
            return "Gemini API rate limit or quota exceeded. Please check your quota at https://ai.google.dev or enable DEMO_MODE=true in backend/.env."
        if isinstance(e, APIConnectionError) or "Connection" in err_str:
            return "Network connection to Gemini API failed. Please check your internet connection."
        if "404" in err_str or isinstance(e, NotFoundError) or "model not found" in err_str.lower():
            return f"Configured Gemini model '{model}' was not found. Please verify GEMINI_MODEL in backend/.env."
        if "503" in err_str or "Service Unavailable" in err_str:
            return "Gemini service is temporarily unavailable (503). Please retry in a few moments."
        return f"Gemini API request failed: {err_str}"

    @staticmethod
    def _parse_json_response(raw_text: str) -> dict:
        """Clean and parse JSON returned by the model."""
        if not raw_text:
            raise ValueError("The AI model returned an empty response.")

        cleaned = raw_text.strip()

        # Remove Markdown code fences if present.
        cleaned = re.sub(
            r"^\s*```(?:json)?\s*",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )
        cleaned = re.sub(r"\s*```\s*$", "", cleaned)

        # Extract the JSON object if extra text surrounds it.
        start = cleaned.find("{")
        end = cleaned.rfind("}")

        if start != -1 and end != -1 and end > start:
            cleaned = cleaned[start:end + 1]

        result = json.loads(cleaned)

        if not isinstance(result, dict):
            raise ValueError("The AI response is not a JSON object.")

        return result

    @classmethod
    def generate_cover_letter(
        cls,
        personal_info: dict,
        job_info: dict,
        professional_info: dict,
        writing_style: str = "Professional",
    ) -> GeneratedLetterData:
        """Generate a personalized cover letter using Gemini."""

        if cls._demo_mode_enabled():
            return cls._generate_demo_letter(
                personal_info,
                job_info,
                professional_info,
                writing_style,
            )

        api_key = cls._get_api_key()
        if not api_key:
            raise ValueError(
                "Gemini API key is missing. Add GEMINI_API_KEY to "
                "backend/.env or enable DEMO_MODE=true for offline demonstration."
            )

        client = cls.get_client()
        model = cls._get_model()

        system_prompt = build_system_prompt()

        user_prompt = build_cover_letter_user_prompt(
            personal_info=personal_info,
            job_info=job_info,
            professional_info=professional_info,
            writing_style=writing_style,
        )

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
                max_tokens=1500,
            )

            content = response.choices[0].message.content or ""
            content = content.strip()

            # Remove Markdown fences if the model returns them.
            content = re.sub(
                r"^\s*```(?:text|markdown)?\s*",
                "",
                content,
                flags=re.IGNORECASE,
            )
            content = re.sub(r"\s*```\s*$", "", content)

            if not content:
                raise ValueError("Gemini returned an empty cover letter.")

            return GeneratedLetterData(
                cover_letter=content,
                writing_style=writing_style,
                word_count=len(content.split()),
                character_count=len(content),
                model_used=model,
                demo_mode=False,
            )

        except Exception as e:
            logger.error("Gemini cover letter generation error: %s", e)
            raise ValueError(cls._format_gemini_error(e, model))

    @classmethod
    def improve_cover_letter(
        cls,
        cover_letter: str,
        action: str,
        selected_text: Optional[str] = None,
        job_title: Optional[str] = None,
        company_name: Optional[str] = None,
        custom_instruction: Optional[str] = None,
    ) -> str:
        """Improve a cover letter or rewrite a selected section."""

        if cls._demo_mode_enabled():
            return cls._improve_demo_letter(
                cover_letter,
                action,
                selected_text,
            )

        api_key = cls._get_api_key()
        if not api_key:
            raise ValueError(
                "Gemini API key is missing. Add GEMINI_API_KEY to "
                "backend/.env or enable DEMO_MODE=true."
            )

        client = cls.get_client()
        model = cls._get_model()

        system_prompt = build_system_prompt()

        user_prompt = build_improvement_prompt(
            cover_letter=cover_letter,
            action=action,
            selected_text=selected_text,
            job_title=job_title,
            company_name=company_name,
            custom_instruction=custom_instruction,
        )

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.5,
                max_tokens=1500,
            )

            improved = response.choices[0].message.content or ""

            if not improved.strip():
                raise ValueError("Gemini returned an empty improvement.")

            return improved.strip().strip('"').strip("'")

        except Exception as e:
            logger.error("Gemini letter improvement error: %s", e)
            raise ValueError(cls._format_gemini_error(e, model))

    @classmethod
    def analyze_job_description(
        cls,
        job_description: str,
        job_title: Optional[str] = None,
        company_name: Optional[str] = None,
    ) -> JobAnalysisData:
        """Extract structured job requirements using Gemini."""

        if cls._demo_mode_enabled() or not cls._get_api_key():
            return JobAnalyzerService.analyze_heuristic(
                job_description=job_description,
                job_title=job_title,
                company_name=company_name,
            )

        client = cls.get_client()
        model = cls._get_model()

        user_prompt = build_job_analyzer_prompt(
            job_description,
            job_title,
            company_name,
        )

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You extract structured job requirements. "
                            "Return a valid JSON object only. Do not use "
                            "Markdown code fences or extra explanatory text."
                        ),
                    },
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
                max_tokens=1500,
                response_format={"type": "json_object"},
            )

            raw_json = response.choices[0].message.content or "{}"
            parsed = cls._parse_json_response(raw_json)

            return JobAnalysisData(
                job_title=parsed.get("job_title") or job_title,
                company_name=parsed.get("company_name") or company_name,
                required_skills=parsed.get("required_skills") or [],
                preferred_skills=parsed.get("preferred_skills") or [],
                programming_languages=parsed.get("programming_languages") or [],
                frameworks=parsed.get("frameworks") or [],
                tools=parsed.get("tools") or [],
                experience_requirements=parsed.get("experience_requirements"),
                educational_qualifications=parsed.get(
                    "educational_qualifications"
                ),
                responsibilities=parsed.get("responsibilities") or [],
                keywords=parsed.get("keywords") or [],
                soft_skills=parsed.get("soft_skills") or [],
            )

        except (RateLimitError, AuthenticationError) as e:
            logger.error("Gemini job analysis error: %s", e)
            raise ValueError(cls._format_gemini_error(e, model))
        except Exception as e:
            logger.warning(
                "Gemini job analysis encountered formatting/JSON issue; falling back to heuristic analysis: %s",
                e,
            )
            return JobAnalyzerService.analyze_heuristic(
                job_description,
                job_title,
                company_name,
            )

    @classmethod
    def check_cover_letter_quality(
        cls,
        cover_letter: str,
        job_description: Optional[str] = None,
        job_title: Optional[str] = None,
    ) -> LetterQualityData:
        """Evaluate cover letter quality using Gemini."""

        if cls._demo_mode_enabled() or not cls._get_api_key():
            return cls._demo_quality_check(cover_letter)

        client = cls.get_client()
        model = cls._get_model()

        user_prompt = build_quality_check_prompt(
            cover_letter,
            job_description,
            job_title,
        )

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a senior recruitment quality assessor. "
                            "Evaluate the cover letter and return a valid "
                            "JSON object only. Do not add Markdown fences."
                        ),
                    },
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                max_tokens=1500,
                response_format={"type": "json_object"},
            )

            raw_json = response.choices[0].message.content or "{}"
            parsed = cls._parse_json_response(raw_json)

            suggestions = []

            for suggestion in parsed.get("specific_suggestions") or []:
                suggestions.append(
                    SpecificSuggestion(
                        title=suggestion.get("title", "Suggestion"),
                        category=suggestion.get("category", "General"),
                        description=suggestion.get("description", ""),
                        recommended_correction=suggestion.get(
                            "recommended_correction"
                        ),
                    )
                )

            metrics = parsed.get("metrics")

            if not isinstance(metrics, dict):
                metrics = {
                    "readability": 85,
                    "tone": 90,
                    "personalization": 85,
                    "relevance": 88,
                }

            return LetterQualityData(
                overall_score=parsed.get("overall_score", 85),
                assessment=parsed.get(
                    "assessment",
                    "Strong professional alignment.",
                ),
                positive_observations=(
                    parsed.get("positive_observations") or []
                ),
                areas_for_improvement=(
                    parsed.get("areas_for_improvement") or []
                ),
                specific_suggestions=suggestions,
                metrics=metrics,
            )

        except (RateLimitError, AuthenticationError) as e:
            logger.error("Gemini quality check error: %s", e)
            raise ValueError(cls._format_gemini_error(e, model))
        except Exception as e:
            logger.warning(
                "Gemini quality check encountered JSON issue; falling back to heuristic scoring: %s",
                e,
            )
            return cls._demo_quality_check(cover_letter)

    @staticmethod
    def _generate_demo_letter(
        personal_info: dict,
        job_info: dict,
        professional_info: dict,
        writing_style: str,
    ) -> GeneratedLetterData:
        """Generate a deterministic sample letter in demo mode."""

        candidate_name = personal_info.get("full_name") or "Alex Taylor"
        company = job_info.get("company_name") or "Acme Tech"
        role = job_info.get("job_title") or "Software Engineer"
        manager = job_info.get("hiring_manager_name") or "Hiring Team"

        skills = ", ".join(
            professional_info.get("technical_skills")
            or [
                "Modern Web Development",
                "Python",
                "Cloud Architecture",
            ]
        )

        projects = (
            professional_info.get("projects")
            or "full-stack distributed platforms"
        )

        letter = f"""Dear {manager},

I am writing to express my enthusiasm for the {role} position at {company}. With a rigorous foundation in {skills} and a passion for engineering reliable, high-performance systems, I am excited about the prospect of contributing directly to {company}'s technical milestones.

During my work with {projects}, I focused on implementing clean architectural patterns, optimizing performance, and ensuring maintainable solutions. Whether building scalable web APIs or collaborating on cross-functional requirements, I bring a commitment to craftsmanship and thoughtful engineering that aligns closely with {company}'s high standards.

What particularly draws me to {company} is your dedication to impactful solutions and technical innovation. I would welcome the opportunity to discuss how my hands-on background in {skills} can assist your team in achieving its upcoming product objectives.

Thank you for your time and consideration. I look forward to speaking with you.

Sincerely,
{candidate_name}"""

        return GeneratedLetterData(
            cover_letter=letter.strip(),
            writing_style=writing_style,
            word_count=len(letter.split()),
            character_count=len(letter),
            model_used="demo-mode-engine",
            demo_mode=True,
        )

    @staticmethod
    def _improve_demo_letter(
        cover_letter: str,
        action: str,
        selected_text: Optional[str] = None,
    ) -> str:
        """Provide simple improvements in demo mode."""

        if action == "make_concise":
            paragraphs = [
                paragraph
                for paragraph in cover_letter.split("\n\n")
                if len(paragraph) > 30
            ]
            return "\n\n".join(paragraphs[:3])

        if action == "make_confident":
            return (
                cover_letter
                .replace("I believe I can", "I will")
                .replace(
                    "I hope to",
                    "I look forward to delivering immediate value by",
                )
            )

        if action == "fix_grammar":
            return cover_letter.strip()

        if action == "rewrite_selection" and selected_text:
            return (
                f"demonstrated measurable results with {selected_text}"
            )

        return cover_letter

    @staticmethod
    def _demo_quality_check(
        cover_letter: str,
    ) -> LetterQualityData:
        """Provide heuristic quality scoring in demo mode."""

        word_count = len(cover_letter.split())
        score = 88

        if word_count < 150:
            score -= 10
        elif word_count > 450:
            score -= 8

        return LetterQualityData(
            overall_score=score,
            assessment=(
                "The cover letter demonstrates clear structure, "
                "appropriate professional tone, and specific alignment "
                "with target objectives."
            ),
            positive_observations=[
                "Clear professional salutation and structured sign-off.",
                "Well-paced paragraph distribution without overwhelming blocks of text.",
                "Maintains respectful and professional career framing.",
            ],
            areas_for_improvement=[
                "Consider incorporating more quantifiable metrics or impact data in the core body paragraph.",
                "Ensure target keywords from the job description are prominent.",
            ],
            specific_suggestions=[
                SpecificSuggestion(
                    title="Quantify Engineering Impact",
                    category="Technical",
                    description=(
                        "Highlight specific percentage improvements, "
                        "latency reductions, or project deliverables."
                    ),
                    recommended_correction=(
                        "Optimized API response latency by 28% while "
                        "handling 10k+ daily queries."
                    ),
                )
            ],
            metrics={
                "readability": 92,
                "tone": 88,
                "personalization": 82,
                "relevance": 86,
            },
        )
