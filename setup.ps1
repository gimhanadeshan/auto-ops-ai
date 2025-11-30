# Auto-Ops-AI Startup Script (Windows)

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Auto-Ops-AI Backend Setup" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Check if .env exists
if (-not (Test-Path "backend\.env")) {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item "backend\.env.example" "backend\.env"
    Write-Host "⚠️  Please edit backend\.env and add your API keys!" -ForegroundColor Yellow
    Write-Host ""
}

# Create necessary directories
Write-Host "Creating necessary directories..." -ForegroundColor Green
New-Item -ItemType Directory -Force -Path "data\processed" | Out-Null
New-Item -ItemType Directory -Force -Path "data\raw" | Out-Null
New-Item -ItemType Directory -Force -Path "logs" | Out-Null

# Check Python version and select appropriate requirements file
$pythonVersion = python --version 2>&1
Write-Host "Python version: $pythonVersion" -ForegroundColor Green

# Determine requirements file based on Python version
$requirementsFile = "requirements.txt"
if ($pythonVersion -like "*3.14*") {
    Write-Host "WARNING: Python 3.14 detected. Using minimal requirements (no AI/ML packages)." -ForegroundColor Yellow
    Write-Host "For full AI features, use Python 3.11/3.12 or Docker." -ForegroundColor Yellow
    $requirementsFile = "requirements-minimal.txt"
}

# Setup Python virtual environment
Write-Host ""
Write-Host "Setting up Python virtual environment..." -ForegroundColor Green
if (-not (Test-Path "venv")) {
    Write-Host "Creating venv..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate venv and install dependencies
Write-Host "Activating venv and installing dependencies..." -ForegroundColor Green
$venvActivate = ".\venv\Scripts\Activate.ps1"
if (Test-Path $venvActivate) {
    & $venvActivate
    & .\venv\Scripts\python.exe -m pip install --upgrade pip
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to upgrade pip!" -ForegroundColor Red
        exit 1
    }
    # Install all project dependencies
    Write-Host "Installing project dependencies from $requirementsFile..." -ForegroundColor Green
    & .\venv\Scripts\pip.exe install -r $requirementsFile
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install dependencies!" -ForegroundColor Red
        exit 1
    }
    Write-Host "[OK] Dependencies installed successfully!" -ForegroundColor Green
} else {
    Write-Host "ERROR: Could not find venv activation script!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Edit backend\.env and add your API keys (GOOGLE_API_KEY or OPENAI_API_KEY)" -ForegroundColor White
Write-Host "2. Place your ticketing data in data\raw\ticketing_system_data_new.json" -ForegroundColor White
Write-Host "3. To run the server, first activate the virtual environment in every new terminal:" -ForegroundColor White
Write-Host "   .\\venv\\Scripts\\Activate" -ForegroundColor Cyan
Write-Host "   cd backend" -ForegroundColor Cyan
Write-Host "   uvicorn app.main:app --reload" -ForegroundColor Cyan
Write-Host ""
Write-Host "Or use Docker:" -ForegroundColor White
Write-Host "   docker-compose up --build" -ForegroundColor Cyan
Write-Host ""
