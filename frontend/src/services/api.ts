import axios, { AxiosError } from "axios";
import type {
  BackendHealth,
  ParsedResume,
  JobAnalysis,
  ResumeMatch,
  PersonalInfo,
  JobInfo,
  ProfessionalInfo,
  QualityReport
} from "@/types";

const client = axios.create({
  baseURL: "/api",
  timeout: 60000,
  headers: {
    "Content-Type": "application/json"
  }
});

// Intercept error responses to extract backend error messages directly
client.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ success?: boolean; error?: string }>) => {
    const serverMessage = error.response?.data?.error;
    if (serverMessage) {
      error.message = serverMessage;
    }
    return Promise.reject(error);
  }
);

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  error?: string;
  meta?: Record<string, unknown>;
}

export class ApiService {
  /** Fetch backend configuration and connectivity status */
  static async getHealth(): Promise<BackendHealth> {
    const res = await client.get<BackendHealth>("/health");
    return res.data;
  }

  /** Upload and parse PDF/DOCX resume file */
  static async parseResume(file: File): Promise<ParsedResume> {
    const formData = new FormData();
    formData.append("file", file);

    const res = await client.post<ApiResponse<ParsedResume>>("/resume/parse", formData, {
      headers: {
        "Content-Type": "multipart/form-data"
      }
    });

    if (!res.data.success) {
      throw new Error(res.data.error || "Failed to parse resume document.");
    }
    return res.data.data;
  }

  /** Analyze job description requirements */
  static async analyzeJob(payload: {
    job_description: string;
    job_title?: string;
    company_name?: string;
  }): Promise<JobAnalysis> {
    const res = await client.post<ApiResponse<JobAnalysis>>("/jobs/analyze", payload);
    if (!res.data.success) {
      throw new Error(res.data.error || "Failed to analyze job description.");
    }
    return res.data.data;
  }

  /** Calculate heuristic resume-to-job match */
  static async matchResume(payload: {
    candidate_skills: string[];
    job_description: string;
    resume_text?: string;
    candidate_experience?: string;
    candidate_projects?: string;
    candidate_education?: string;
    job_title?: string;
    company_name?: string;
  }): Promise<ResumeMatch> {
    const res = await client.post<ApiResponse<ResumeMatch>>("/resume/match", payload);
    if (!res.data.success) {
      throw new Error(res.data.error || "Failed to compute match estimate.");
    }
    return res.data.data;
  }

  /** Generate tailored cover letter */
  static async generateCoverLetter(payload: {
    personal_info: PersonalInfo;
    job_info: JobInfo;
    professional_info: ProfessionalInfo;
    writing_style: string;
    template_id?: string;
  }): Promise<{
    cover_letter: string;
    writing_style: string;
    word_count: number;
    character_count: number;
    model_used: string;
    demo_mode: boolean;
  }> {
    const res = await client.post<ApiResponse<{
      cover_letter: string;
      writing_style: string;
      word_count: number;
      character_count: number;
      model_used: string;
      demo_mode: boolean;
    }>>("/letters/generate", payload);

    if (!res.data.success) {
      throw new Error(res.data.error || "Failed to generate cover letter.");
    }
    return res.data.data;
  }

  /** Improve entire cover letter or rewrite selection */
  static async improveCoverLetter(payload: {
    cover_letter: string;
    action: string;
    selected_text?: string;
    job_title?: string;
    company_name?: string;
    custom_instruction?: string;
  }): Promise<{
    improved_text: string;
    action: string;
    is_selection_replacement: boolean;
  }> {
    const res = await client.post<ApiResponse<{
      improved_text: string;
      action: string;
      is_selection_replacement: boolean;
    }>>("/letters/improve", payload);

    if (!res.data.success) {
      throw new Error(res.data.error || "Failed to improve cover letter.");
    }
    return res.data.data;
  }

  /** Run AI quality assessment */
  static async checkQuality(payload: {
    cover_letter: string;
    job_description?: string;
    job_title?: string;
  }): Promise<QualityReport> {
    const res = await client.post<ApiResponse<QualityReport>>("/letters/quality", payload);
    if (!res.data.success) {
      throw new Error(res.data.error || "Failed to evaluate quality.");
    }
    return res.data.data;
  }

  /** Export as PDF and trigger native file download */
  static async downloadPdf(payload: {
    cover_letter: string;
    personal_info: PersonalInfo;
    job_info: JobInfo;
    template_id?: string;
  }): Promise<void> {
    const response = await client.post("/letters/export/pdf", payload, {
      responseType: "blob"
    });

    // Check if error JSON was returned as blob
    if (response.data.type === "application/json") {
      const text = await (response.data as Blob).text();
      const err = JSON.parse(text);
      throw new Error(err.error || "Failed to export PDF document.");
    }

    const blob = new Blob([response.data], { type: "application/pdf" });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    
    // Extract filename from header or fallback
    const disposition = response.headers["content-disposition"];
    let filename = "Cover_Letter.pdf";
    if (disposition && disposition.includes("filename=")) {
      filename = disposition.split("filename=")[1].replace(/["']/g, "").trim();
    }
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  }

  /** Export as DOCX and trigger native file download */
  static async downloadDocx(payload: {
    cover_letter: string;
    personal_info: PersonalInfo;
    job_info: JobInfo;
    template_id?: string;
  }): Promise<void> {
    const response = await client.post("/letters/export/docx", payload, {
      responseType: "blob"
    });

    if (response.data.type === "application/json") {
      const text = await (response.data as Blob).text();
      const err = JSON.parse(text);
      throw new Error(err.error || "Failed to export DOCX document.");
    }

    const blob = new Blob([response.data], {
      type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;

    const disposition = response.headers["content-disposition"];
    let filename = "Cover_Letter.docx";
    if (disposition && disposition.includes("filename=")) {
      filename = disposition.split("filename=")[1].replace(/["']/g, "").trim();
    }
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  }
}
