# Auto-Ops-AI Run Script for Windows PowerShell

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Auto-Ops-AI Backend Server Launcher" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Ensure script runs from repository root (where this script file is located)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
if ($scriptDir -and (Test-Path $scriptDir)) {
    Set-Location $scriptDir
}

# Check if venv exists
if (-not (Test-Path "venv")) {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run setup.ps1 first:" -ForegroundColor Yellow
    Write-Host "  .\setup.ps1" -ForegroundColor Cyan
    exit 1
}

# Activate venv
Write-Host "Activating virtual environment..." -ForegroundColor Green
$venvActivate = Join-Path -Path (Get-Location) -ChildPath "venv\Scripts\Activate.ps1"
if (Test-Path $venvActivate) {
    & $venvActivate
} else {
    Write-Host "ERROR: Could not find virtual environment activation script at $venvActivate" -ForegroundColor Red
    exit 1
}

# Check if .env exists
if (-not (Test-Path "backend\.env")) {
    Write-Host ""
    Write-Host "WARNING: backend\.env not found!" -ForegroundColor Yellow
    Write-Host "Copy backend\.env.example and add your API keys:" -ForegroundColor Yellow
    Write-Host "  Copy-Item backend\.env.example backend\.env" -ForegroundColor Cyan
    Write-Host ""
}

# Start the server
Write-Host ""
Write-Host "Starting Auto-Ops-AI Backend Server..." -ForegroundColor Green
Write-Host "Server will be available at: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "API Documentation: http://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host "ReDoc Documentation: http://127.0.0.1:8000/redoc" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press CTRL+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Change to backend directory and run uvicorn
Set-Location backend
python -m uvicorn app.main:app --reload
