export interface PersonalInfo {
  full_name: string;
  email: string;
  phone?: string;
  location?: string;
  linkedin_url?: string;
  portfolio_url?: string;
  github_url?: string;
}

export interface JobInfo {
  job_title: string;
  company_name: string;
  hiring_manager_name?: string;
  company_location?: string;
  job_description: string;
  application_type: string;
}

export interface ProfessionalInfo {
  technical_skills: string[];
  relevant_experience?: string;
  projects?: string;
  achievements?: string;
  certifications?: string;
  education?: string;
  additional_info?: string;
}

export interface ParsedResume {
  full_name?: string;
  email?: string;
  phone?: string;
  location?: string;
  linkedin_url?: string;
  github_url?: string;
  portfolio_url?: string;
  summary?: string;
  technical_skills: string[];
  relevant_experience?: string;
  projects?: string;
  achievements?: string;
  certifications?: string;
  education?: string;
  raw_text: string;
  page_count: number;
  warnings: string[];
}

export interface JobAnalysis {
  job_title?: string;
  company_name?: string;
  required_skills: string[];
  preferred_skills: string[];
  programming_languages: string[];
  frameworks: string[];
  tools: string[];
  experience_requirements?: string;
  educational_qualifications?: string;
  responsibilities: string[];
  keywords: string[];
  soft_skills: string[];
}

export interface ResumeMatch {
  match_percentage: number;
  scoring_explanation: string;
  matched_skills: string[];
  missing_skills: string[];
  suggested_keywords: string[];
  experience_match_summary: string;
  recommendations: string[];
  is_fresher_friendly: boolean;
}

export interface CoverLetterDraft {
  id: string;
  title: string;
  cover_letter: string;
  writing_style: string;
  template_id: string;
  personal_info: PersonalInfo;
  job_info: JobInfo;
  professional_info: ProfessionalInfo;
  created_at: string;
  updated_at: string;
}

export interface SpecificSuggestion {
  title: string;
  category: string;
  description: string;
  recommended_correction?: string;
}

export interface QualityReport {
  overall_score: number;
  assessment: string;
  positive_observations: string[];
  areas_for_improvement: string[];
  specific_suggestions: SpecificSuggestion[];
  metrics: Record<string, number>;
}

export interface BackendHealth {
  status: string;
  service: string;
  version: string;
  config: {
    model: string;
    has_gemini_key: boolean;
    has_openai_key?: boolean;
    demo_mode: boolean;
    max_upload_size_mb: number;
  };
  connection?: {
    connected: boolean;
    message: string;
  };
}

export type WritingStyle =
  | "Professional"
  | "Concise"
  | "Confident"
  | "Technical"
  | "Creative"
  | "Entry-Level / Fresher"
  | "Executive";

export interface TemplateDefinition {
  id: string;
  name: string;
  badge: string;
  description: string;
  suitableFor: string;
}
