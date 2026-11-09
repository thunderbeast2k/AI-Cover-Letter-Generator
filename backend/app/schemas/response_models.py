from typing import Optional, List, Dict, Any, Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None


class ParsedResumeData(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    summary: Optional[str] = None
    technical_skills: List[str] = Field(default_factory=list)
    relevant_experience: Optional[str] = None
    projects: Optional[str] = None
    achievements: Optional[str] = None
    certifications: Optional[str] = None
    education: Optional[str] = None
    raw_text: str
    page_count: int = 1
    warnings: List[str] = Field(default_factory=list)


class JobAnalysisData(BaseModel):
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    programming_languages: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    experience_requirements: Optional[str] = None
    educational_qualifications: Optional[str] = None
    responsibilities: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    soft_skills: List[str] = Field(default_factory=list)


class ResumeMatchData(BaseModel):
    match_percentage: int
    scoring_explanation: str
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    suggested_keywords: List[str] = Field(default_factory=list)
    experience_match_summary: str
    recommendations: List[str] = Field(default_factory=list)
    is_fresher_friendly: bool = False


class GeneratedLetterData(BaseModel):
    cover_letter: str
    writing_style: str
    word_count: int
    character_count: int
    model_used: str
    demo_mode: bool = False


class SpecificSuggestion(BaseModel):
    title: str
    category: str
    description: str
    recommended_correction: Optional[str] = None


class LetterQualityData(BaseModel):
    overall_score: int
    assessment: str
    positive_observations: List[str] = Field(default_factory=list)
    areas_for_improvement: List[str] = Field(default_factory=list)
    specific_suggestions: List[SpecificSuggestion] = Field(default_factory=list)
    metrics: Dict[str, int] = Field(default_factory=dict)
