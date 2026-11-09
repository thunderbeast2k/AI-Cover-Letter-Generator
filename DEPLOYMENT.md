# Production Deployment Guide: AI Cover Letter Generator

This guide provides instructions for deploying the **AI Cover Letter Generator** in production across multiple environments:
1. **Direct Windows Server / VM Deployment** (Waitress WSGI Server)
2. **Docker & Docker Compose** (Containerized)
3. **Linux VPS with Systemd + Nginx Reverse Proxy** (Enterprise Ubuntu/Debian)
4. **Cloud Platforms** (Render, Railway, AWS, GCP Cloud Run)

---

## 1. Unified Production Architecture

In production, the application runs on a **Unified Single-Origin Architecture**:
- **WSGI Engine**: Multi-threaded **Waitress** WSGI production server (`backend/serve.py`).
- **SPA Serving**: The compiled Vue 3 + Vite frontend (`frontend/dist`) is served directly by the production WSGI server.
- **REST API**: All endpoints are mounted at `/api/*`.
- **Zero CORS Hurdles**: Both the UI and API share the exact same host and port in production, eliminating CORS preflight latency.
- **Automated Security Headers**: Enforces `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN`, `X-XSS-Protection`, and `Referrer-Policy`.

```
[ Client Browser ]
        │
        ▼  HTTP (Port 5000 / 80 / 443)
┌──────────────────────────────────────────────────────────────┐
│                  Waitress WSGI Production Server             │
│                                                              │
│  ┌─────────────────────────┐    ┌──────────────────────────┐ │
│  │  Vue 3 SPA (Dist)       │    │  Flask REST API          │ │
│  │  - /                    │    │  - /api/health           │ │
│  │  - /workspace           │    │  - /api/resume/parse     │ │
│  │  - /analyzer            │    │  - /api/jobs/analyze     │ │
│  │  - /matching            │    │  - /api/letters/generate │ │
│  │  - /assets/* (Cached)   │    │  - /api/letters/export/* │ │
│  └─────────────────────────┘    └──────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
                                │
                                ▼
                 [ Google Gemini 3.8 Flash API ]
```

---

## 2. Option 1: Native Windows Server / VM Deployment

### Prerequisites
- Python 3.11+ installed and added to PATH
- Node.js 18+ and npm installed

### Quick Start (PowerShell)

1. **Build and validate the release**:
   ```powershell
   .\build-production.ps1
   ```

2. **Configure production environment**:
   Edit `backend\.env`:
   ```env
   GEMINI_API_KEY=your_actual_gemini_api_key
   GEMINI_MODEL=gemini-3.8-flash
   DEMO_MODE=false
   SECRET_KEY=generate_a_long_random_secret_string_here
   FLASK_HOST=0.0.0.0
   FLASK_PORT=5000
   WAITRESS_THREADS=8
   ```

3. **Start the production server**:
   ```powershell
   .\start-production.ps1
   ```
   *Or directly invoke:*
   ```powershell
   cd backend
   .\venv\Scripts\python.exe serve.py --host 0.0.0.0 --port 5000 --threads 8
   ```

4. **Verify**: Open `http://localhost:5000` or `http://<server-ip>:5000` in any browser.

---

## 3. Option 2: Docker & Docker Compose (Recommended for Containers)

A multi-stage `Dockerfile` and `docker-compose.yml` are included in the repository root.

### One-Command Deployment

```bash
# 1. Provide your Gemini API key
export GEMINI_API_KEY="your_actual_gemini_api_key"

# 2. Build and launch container in background
docker compose up -d --build
```

### Docker Verification & Logs
```bash
# Check container status and health
docker compose ps

# View live application logs
docker compose logs -f

# Check health endpoint
curl -f http://localhost:5000/api/health
```

### Stopping the Container
```bash
docker compose down
```

---

## 4. Option 3: Linux VPS Deployment (Systemd + Nginx Reverse Proxy)

For Ubuntu 22.04 / 24.04 or Debian 12:

### Step 1: Install System Dependencies
```bash
sudo apt update && sudo apt install -y python3-venv python3-pip nodejs npm nginx certbot python3-certbot-nginx
```

### Step 2: Clone and Build Application
```bash
sudo mkdir -p /var/www/ai-cover-letter-generator
sudo chown -R $USER:$USER /var/www/ai-cover-letter-generator
git clone <repo-url> /var/www/ai-cover-letter-generator
cd /var/www/ai-cover-letter-generator

# Build frontend
cd frontend
npm ci
npm run build

# Setup Python Virtual Environment
cd ../backend
python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt
cp .env.example .env
nano .env # Paste your GEMINI_API_KEY and set DEMO_MODE=false
```

### Step 3: Install Systemd Service
```bash
sudo cp /var/www/ai-cover-letter-generator/deploy/ai-cover-letter.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ai-cover-letter
sudo systemctl start ai-cover-letter
sudo systemctl status ai-cover-letter
```

### Step 4: Configure Nginx & SSL
```bash
sudo cp /var/www/ai-cover-letter-generator/deploy/nginx.conf /etc/nginx/sites-available/ai-cover-letter
# Edit domain name in nginx config
sudo nano /etc/nginx/sites-available/ai-cover-letter
sudo ln -s /etc/nginx/sites-available/ai-cover-letter /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Obtain free SSL certificates via Let's Encrypt
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

---

## 5. Option 4: Cloud PaaS Deployment (Render / Railway / GCP Cloud Run)

### Render
1. Create a **New Web Service** pointing to your repository.
2. Select **Docker** as the Runtime (it will automatically use the root `Dockerfile`).
3. Add Environment Variables:
   - `GEMINI_API_KEY` = your Gemini key
   - `GEMINI_MODEL` = `gemini-3.8-flash`
   - `DEMO_MODE` = `false`
   - `SECRET_KEY` = `<random-secret>`
4. Set Health Check path to `/api/health`.

### Google Cloud Run
```bash
gcloud run deploy ai-cover-letter \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY="your_key",GEMINI_MODEL="gemini-3.8-flash",DEMO_MODE="false"
```

---

## 6. Environment Variables Reference

| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `GEMINI_API_KEY` | *(Required)* | Google Gemini API key for live GenAI generation. |
| `GEMINI_MODEL` | `gemini-3.8-flash` | Gemini model identifier. |
| `DEMO_MODE` | `false` | When `true`, uses offline heuristic templates without API calls. |
| `FLASK_HOST` | `0.0.0.0` | IP interface bound by the WSGI server (`0.0.0.0` for all interfaces). |
| `PORT` / `FLASK_PORT` | `5000` | Port on which the production server listens. |
| `WAITRESS_THREADS` | `8` | Number of concurrent worker threads handling incoming requests. |
| `FRONTEND_DIST_DIR` | `../frontend/dist` | Directory containing compiled Vue 3 production static assets. |
| `SECRET_KEY` | *(Configurable)* | Cryptographic session and cookie signing key. |
| `MAX_CONTENT_LENGTH` | `5242880` (5 MB) | Maximum permitted file upload size for resumes. |

---

## 7. Operational Health Check & Monitoring

The server includes a dedicated health and diagnostic endpoint:
```http
GET /api/health
```

Example JSON response:
```json
{
  "status": "Connected",
  "service": "AI Cover Letter Generator API",
  "version": "1.0.0",
  "config": {
    "model": "gemini-3.8-flash",
    "has_gemini_key": true,
    "demo_mode": false,
    "max_upload_size_mb": 5.0
  },
  "connection": {
    "connected": true,
    "message": "Gemini API connection verified (gemini-3.8-flash)."
  }
}
```
