<#
.SYNOPSIS
    Starts the AI Cover Letter Generator Production Server on Windows.
.DESCRIPTION
    1. Checks for python virtual environment.
    2. Builds the frontend Vue 3 distribution if not already present.
    3. Launches the Waitress production WSGI server serving both the SPA frontend and REST API on port 5000.
#>

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "  Starting AI Cover Letter Generator - Production Server         " -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

# 1. Check Python Virtual Environment
$PythonExe = Join-Path $ScriptDir "backend\venv\Scripts\python.exe"
if (-not (Test-Path $PythonExe)) {
    Write-Host "[ERROR] Virtual environment not found at $PythonExe" -ForegroundColor Red
    Write-Host "Please create it using: cd backend; python -m venv venv; .\venv\Scripts\pip install -r requirements.txt"
    exit 1
}

# 2. Check and Build Frontend if needed
$FrontendDist = Join-Path $ScriptDir "frontend\dist\index.html"
if (-not (Test-Path $FrontendDist)) {
    Write-Host "[BUILD] Frontend production build not found. Compiling Vue 3 application..." -ForegroundColor Yellow
    Push-Location (Join-Path $ScriptDir "frontend")
    try {
        npm run build
    } finally {
        Pop-Location
    }
} else {
    Write-Host "[OK] Compiled frontend distribution located at frontend\dist" -ForegroundColor Green
}

# 3. Check .env configuration
$EnvFile = Join-Path $ScriptDir "backend\.env"
if (-not (Test-Path $EnvFile)) {
    Write-Host "[WARNING] backend\.env file not found. Copying from .env.example..." -ForegroundColor Yellow
    Copy-Item (Join-Path $ScriptDir "backend\.env.example") $EnvFile
}

# 4. Launch Waitress Production Server
Write-Host "[START] Launching production Waitress WSGI server..." -ForegroundColor Green
Push-Location (Join-Path $ScriptDir "backend")
try {
    & $PythonExe serve.py --host 0.0.0.0 --port 5000 --threads 8
} finally {
    Pop-Location
}
