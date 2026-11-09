<#
.SYNOPSIS
    Compiles and tests the entire AI Cover Letter Generator for production.
#>

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "  Building & Validating Production Release                       " -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

# 1. Run Backend Pytest Suite
Write-Host "`n[STEP 1/3] Running Backend Pytest Suite..." -ForegroundColor Yellow
$PythonExe = Join-Path $ScriptDir "backend\venv\Scripts\python.exe"
Push-Location (Join-Path $ScriptDir "backend")
try {
    & $PythonExe -m pytest tests --rootdir . -p no:cacheprovider -v
    if ($LASTEXITCODE -ne 0) { throw "Backend tests failed." }
} finally {
    Pop-Location
}
Write-Host "[PASS] Backend tests passed." -ForegroundColor Green

# 2. Run Frontend Vitest Suite
Write-Host "`n[STEP 2/3] Running Frontend Vitest Suite..." -ForegroundColor Yellow
Push-Location (Join-Path $ScriptDir "frontend")
try {
    npm test
    if ($LASTEXITCODE -ne 0) { throw "Frontend tests failed." }
} finally {
    Pop-Location
}
Write-Host "[PASS] Frontend tests passed." -ForegroundColor Green

# 3. Build Production Vue 3 Static Assets
Write-Host "`n[STEP 3/3] Compiling Production Frontend Assets (vue-tsc + vite)..." -ForegroundColor Yellow
Push-Location (Join-Path $ScriptDir "frontend")
try {
    npm run build
    if ($LASTEXITCODE -ne 0) { throw "Frontend build failed." }
} finally {
    Pop-Location
}
Write-Host "[PASS] Production build complete in frontend\dist." -ForegroundColor Green

Write-Host "`n=================================================================" -ForegroundColor Cyan
Write-Host "  Build SUCCESS! Ready to deploy with: .\start-production.ps1    " -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan
