# AI Cover Letter Generator

AI Cover Letter Generator is a full-stack application for creating tailored, fact-based, ATS-friendly cover letters. Upload a PDF or DOCX resume, analyze a target job description, compare skills, generate a draft, refine it, and export the final letter as PDF or DOCX.

The application is designed for students, early-career candidates, engineers, and experienced professionals. It uses only information supplied by the candidate and job description; it is not intended to invent qualifications or employment history.

## Features

- Resume parsing for PDF and DOCX files
- Structured job-description analysis
- Resume-to-job skill matching with transparent results
- AI-generated cover letters with selectable writing styles
- In-editor refinement and quality assessment
- PDF and DOCX export
- Local browser draft storage; no application database
- Demo mode for testing without an AI API key
- Responsive Vue interface with light and dark themes
- Health and configuration diagnostics

## Technology

### Frontend

- Vue 3 with Composition API and TypeScript
- Vite development server and production bundling
- Vue Router
- Tailwind CSS
- Iconify Vue
- Motion-V and Inspira UI components
- Axios API client
- Vitest and Vue Test Utils

### Backend

- Python and Flask application factory
- Flask-CORS
- Google Gemini API integration
- Pydantic request and response models
- PyMuPDF for PDF extraction
- python-docx for DOCX extraction and generation
- ReportLab for PDF generation
- Waitress production WSGI server
- Pytest

## Project Structure

```text
AI-Cover-Letter-Generator/
├── backend/
│   ├── app/
│   │   ├── routes/                  # Flask API blueprints
│   │   │   ├── health.py
│   │   │   ├── jobs.py
│   │   │   ├── letters.py
│   │   │   └── resume.py
│   │   ├── schemas/                 # Pydantic request/response models
│   │   ├── services/                # AI, parsing, matching, and documents
│   │   ├── utils/                   # Validation and shared helpers
│   │   ├── config.py                # Environment-based configuration
│   │   └── __init__.py              # Flask application factory
│   ├── tests/
│   ├── requirements.txt
│   ├── run.py                       # Development server
│   ├── serve.py                     # Waitress production server
│   ├── .env.example
│   └── .env                         # Local-only configuration
├── frontend/
│   ├── src/
│   │   ├── components/              # Shared UI, editor, resume, and effects
│   │   ├── composables/             # Theme, drafts, and toast state
│   │   ├── layouts/                 # Application shell
│   │   ├── pages/                   # Dashboard and feature pages
│   │   ├── router/
│   │   ├── services/                # Axios API service
│   │   ├── types/
│   │   └── utils/
│   ├── tests/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   └── tsconfig.json
├── docs/
│   ├── architecture.md
│   └── api-documentation.md
├── Dockerfile
├── docker-compose.yml
├── build-production.ps1
├── start-production.ps1
└── README.md
```

## Requirements

- Windows PowerShell, macOS/Linux shell, or Docker
- Python 3.11 or newer
- Node.js 20 or newer
- A Gemini API key for live AI responses

The application can also run in demo mode without a Gemini key.

## Local Development

### 1. Configure the backend

From the repository root:

```powershell
py -m venv backend\venv
.\backend\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r backend\requirements.txt
Copy-Item backend\.env.example backend\.env
```

Edit `backend\.env`:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.8-flash
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
MAX_CONTENT_LENGTH=5242880
DEMO_MODE=false
```

Use `DEMO_MODE=true` when you want to test the application without making Gemini requests.

### 2. Start the backend

In the repository root:

```powershell
.\backend\venv\Scripts\python.exe backend\run.py
```

The development API is available at `http://127.0.0.1:5000`.

### 3. Start the frontend

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

The frontend is available at `http://localhost:5173`. Vite proxies `/api` requests to the backend at `http://127.0.0.1:5000`.

## API Endpoints

All endpoints are prefixed with `/api`.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Check service status and configuration |
| POST | `/resume/parse` | Parse a PDF or DOCX resume |
| POST | `/resume/match` | Compare resume information with a job |
| POST | `/jobs/analyze` | Extract job requirements and keywords |
| POST | `/letters/generate` | Generate a tailored cover letter |
| POST | `/letters/improve` | Improve or rewrite a cover letter |
| POST | `/letters/quality` | Assess quality and provide suggestions |
| POST | `/letters/export/pdf` | Download a PDF cover letter |
| POST | `/letters/export/docx` | Download a DOCX cover letter |

See [docs/api-documentation.md](docs/api-documentation.md) for request and response details.

## Testing and Validation

### Backend tests

```powershell
.\backend\venv\Scripts\python.exe -m pytest backend\tests -v
```

### Frontend tests

```powershell
cd frontend
npm run test
```

### Frontend production build

```powershell
cd frontend
npm run build
```

The frontend currently has six Vitest tests covering drafts, resume uploads, and editor behavior. Backend test coverage is maintained in `backend/tests`.

## Production

### Windows

Build and start the production server from the repository root:

```powershell
.\build-production.ps1
.\start-production.ps1
```

The production server uses Waitress and listens on port `5000` by default. It can serve the compiled Vue application and Flask API from one process when `frontend\dist` exists.

You can also start it directly:

```powershell
.\backend\venv\Scripts\python.exe backend\serve.py --host 0.0.0.0 --port 5000 --threads 8
```

### Docker Compose

Configure `backend\.env`, then run:

```powershell
docker compose up -d --build
```

The container exposes port `5000` and includes a health check for `/api/health`.

## Privacy and Security

- Resume files are processed from a temporary upload directory and are not stored as application records.
- Drafts are stored in the browser's `localStorage`.
- API keys are read by the backend and are not exposed to frontend code.
- Uploaded files are restricted to PDF and DOCX formats and are limited by `MAX_CONTENT_LENGTH` (5 MB by default).
- Resume text is validated and sanitized before it is used in AI prompts.
- Replace the development `SECRET_KEY` before production deployment.

## Troubleshooting

### The frontend cannot reach the API

Confirm that the backend is running on port `5000`. The Vite proxy target is configured in `frontend\vite.config.ts`.

### AI requests are unavailable

Check `GEMINI_API_KEY` and `GEMINI_MODEL` in `backend\.env`, or set `DEMO_MODE=true` for offline demo responses.

### PowerShell blocks virtual-environment activation

Run the backend without activating the environment:

```powershell
.\backend\venv\Scripts\python.exe backend\run.py
```

## Additional Documentation

- [Architecture](docs/architecture.md)
- [API documentation](docs/api-documentation.md)
- [Deployment guide](DEPLOYMENT.md)
