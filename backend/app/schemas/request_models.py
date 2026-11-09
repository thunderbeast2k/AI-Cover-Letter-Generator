from typing import Optional, List
from pydantic import BaseModel, Field


class PersonalInfo(BaseModel):
    full_name: str = Field(..., min_length=1, description="Applicant full name")
    email: Optional[str] = Field(default="", description="Applicant email address")
    phone: Optional[str] = Field(None, description="Phone number")
    location: Optional[str] = Field(None, description="City, State / Country")
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profile URL")
    portfolio_url: Optional[str] = Field(None, description="Portfolio website URL")
    github_url: Optional[str] = Field(None, description="GitHub profile URL")


class JobInfo(BaseModel):
    job_title: str = Field(..., min_length=1, description="Target job title")
    company_name: str = Field(..., min_length=1, description="Target company name")
    hiring_manager_name: Optional[str] = Field(None, description="Hiring manager or department name")
    company_location: Optional[str] = Field(None, description="Company location")
    job_description: str = Field(..., min_length=1, description="Full or excerpt of job description")
    application_type: str = Field(
        default="Full-time",
        description="Application type: Full-time, Internship, Graduate role, Contract, Other"
    )


class ProfessionalInfo(BaseModel):
    technical_skills: List[str] = Field(default_factory=list, description="Skills possessed by candidate")
    relevant_experience: Optional[str] = Field(None, description="Summary of work or internship experience")
    projects: Optional[str] = Field(None, description="Key projects built or contributed to")
    achievements: Optional[str] = Field(None, description="Awards, competitions, notable achievements")
    certifications: Optional[str] = Field(None, description="Certificates and credentials")
    education: Optional[str] = Field(None, description="Degrees, universities, graduation years")
    additional_info: Optional[str] = Field(None, description="Any extra context (e.g. visa, availability)")


class JobAnalysisRequest(BaseModel):
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    job_description: str = Field(..., min_length=10, description="Raw job description text")


class ResumeMatchRequest(BaseModel):
    resume_text: Optional[str] = None
    candidate_skills: List[str] = Field(default_factory=list)
    candidate_experience: Optional[str] = None
    candidate_education: Optional[str] = None
    candidate_projects: Optional[str] = None
    job_description: str = Field(..., min_length=10)
    job_title: Optional[str] = None
    company_name: Optional[str] = None


class CoverLetterGenerateRequest(BaseModel):
    personal_info: PersonalInfo
    job_info: JobInfo
    professional_info: ProfessionalInfo
    writing_style: str = Field(default="Professional")
    template_id: Optional[str] = Field(default="classic")


class LetterImproveRequest(BaseModel):
    cover_letter: str = Field(..., min_length=10)
    action: str = Field(
        ...,
        description="Action type: improve_writing, make_professional, make_concise, make_confident, improve_technical, improve_opening, improve_closing, fix_grammar, rewrite_selection"
    )
    selected_text: Optional[str] = None
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    custom_instruction: Optional[str] = None


class LetterQualityRequest(BaseModel):
    cover_letter: str = Field(..., min_length=10)
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    job_description: Optional[str] = None


class ExportRequest(BaseModel):
    cover_letter: str = Field(..., min_length=10)
    personal_info: PersonalInfo
    job_info: JobInfo
    template_id: str = Field(default="classic")
