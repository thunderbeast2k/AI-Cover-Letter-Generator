# AI Cover Letter Generator - Architecture & Design System

## 1. System Overview

**AI Cover Letter Generator** is a production-quality SaaS web application engineered to bridge the gap between job seekers' verified credentials and corporate ATS job requirements.

### Core Architectural Principle
> **Never fabricate a candidate's qualifications, education, experience, achievements, or skills.**

The system operates on verified facts extracted directly from applicant resumes or user inputs. Where qualifications are missing or candidates are fresh graduates, the engine emphasizes relevant academic coursework, capstone projects, foundational competencies, and motivation without inventing corporate roles.

---

## 2. Architecture Diagram

```
+---------------------------------------------------------------------------------+
|                                 CLIENT TIER                                     |
|  Vue 3 + Vite + TypeScript + Tailwind CSS + Inspira UI + Motion-V               |
|                                                                                 |
|  - Dashboard View (Hero, Recent Drafts, Quick Start, Particles & Glow)          |
|  - Cover Letter Workspace (Two-column layout, Reactive Form, Live Editor)       |
|  - Job Description Analyzer (Skill & Keyword Extractor)                         |
|  - Semantic Resume Matching (Heuristic Alignment & Fresher-friendly scoring)    |
|  - Template Gallery (Classic, Minimal, Technical, Graduate, Internship)         |
|  - Local Storage Layer (Zero-server retention for maximum candidate privacy)    |
+----------------------------------------+----------------------------------------+
                                         |  /api (Vite Dev Proxy / REST)
                                         v
+---------------------------------------------------------------------------------+
|                                BACKEND TIER                                     |
|  Python 3.11+ / Flask App Factory + Flask-CORS + Pydantic v2                    |
|                                                                                 |
|  +-------------------------+  +----------------------------------------------+  |
|  | Blueprints & Routes     |  | Service Layer                                |  |
|  | - /api/health           |  | - ResumeParserService (PyMuPDF, python-docx) |  |
|  | - /api/resume/parse     |  | - JobAnalyzerService (Keyword & Heuristic)   |  |
|  | - /api/resume/match     |  | - MatchingService (Transparent Scoring)      |  |
|  | - /api/jobs/analyze     |  | - DocumentService (ReportLab, python-docx)   |  |
|  | - /api/letters/generate |  | - PromptService (Anti-hallucination prompts) |  |
|  | - /api/letters/improve  |  | - AIService (OpenAI SDK + Demo Mode Engine)  |  |
|  | - /api/letters/quality  |  +----------------------------------------------+  |
|  | - /api/letters/export/* |                                                    |
|  +-------------------------+                                                    |
+----------------------------------------+----------------------------------------+
                                         |
                                         v
                       +----------------------------------+
                       |          EXTERNAL TIER           |
                       | - OpenAI Chat Completions API    |
                       | - (or Deterministic Demo Engine) |
                       +----------------------------------+
```

---

## 3. Inspira UI & Design Philosophy

The interface follows a modern, calm SaaS aesthetic:
- **Depth & Dimension**: Subtle radial spotlighting (`CardSpotlight.vue`), glowing borders (`BorderBeam.vue`), and low-CPU background canvas dynamics (`ParticlesBg.vue`).
- **Tactile Feedback**: Shimmer buttons (`ShimmerButton.vue`) for primary calls to action with subtle keyframe gradients.
- **Typography & Rhythm**: Neutral charcoal foregrounds, soft slate borders, high-contrast badges for skills, and responsive vertical scaling for mobile viewports.
- **Micro-animations**: Powered by `motion-v` and `tw-animate-css` with complete support for reduced-motion preferences.

---

## 4. Document Processing Pipeline

### Ingestion (Parsing)
1. Uploaded file is streamed into a temporary sandbox directory with a unique UUID filename.
2. Binary magic numbers are verified:
   - PDF: `%PDF-` header check.
   - DOCX: `PK\x03\x04` ZIP container header check.
3. Plain text and structure are parsed:
   - PDF: PyMuPDF (`fitz`) multi-page extraction.
   - DOCX: `python-docx` paragraph and table text extraction.
4. Heuristic segmenter detects sections (Summary, Skills, Experience, Education, Projects).
5. Sanitizer disarms potential prompt-injection strings.
6. The temporary file is **guaranteed to be deleted** in a `finally` block.

### Export (Generation)
- **PDF**: Generated on-the-fly with `ReportLab` using strict margin rules (0.75"), clean font leading, and automatic line-wrapping designed to respect standard single-page bounds.
- **DOCX**: Rendered as a Microsoft Word `.docx` file using `python-docx`, maintaining editable typography and professional styles.

---

## 5. Security & Privacy Safeguards

1. **Zero Permanent Server Storage**: Uploaded resumes are never saved to disk permanently.
2. **Untrusted Prompt Isolation**: Candidate text and job postings are isolated in delimited prompt blocks with strict system guardrails instructing the AI to ignore instruction overrides.
3. **Backend-Only Secrets**: The `OPENAI_API_KEY` is strictly managed via server environment variables and never exposed to the client bundle or network payload.
4. **Local Browser Drafts**: Drafts are stored in the client's `localStorage`, ensuring user ownership and instant recovery without server tracking.
