# Auto-Ops-AI Setup Script

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Auto-Ops-AI Setup" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Create directories
Write-Host "Creating directories..." -ForegroundColor Green
New-Item -ItemType Directory -Force -Path "data\processed", "data\raw", "logs", "backend\data\processed" | Out-Null

# Check Python version
$pythonVersion = python --version 2>&1
Write-Host "Python version: $pythonVersion" -ForegroundColor Green

# Determine requirements file
$requirementsFile = "requirements.txt"
if ($pythonVersion -like "*3.14*") {
    Write-Host "WARNING: Python 3.14 detected. Using minimal requirements." -ForegroundColor Yellow
    $requirementsFile = "requirements-minimal.txt"
}

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Green
if (-not (Test-Path "venv")) {
    python -m venv venv
}

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Green
& .\venv\Scripts\python.exe -m pip install --upgrade pip -q
& .\venv\Scripts\pip.exe install -r $requirementsFile -q

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install dependencies!" -ForegroundColor Red
    exit 1
}

# Setup .env file
if (-not (Test-Path "backend\.env")) {
    if (Test-Path "backend\.env.example") {
        Copy-Item "backend\.env.example" "backend\.env"
    }
}

# Initialize vector database
Write-Host "Initializing vector database..." -ForegroundColor Green
& .\venv\Scripts\Activate.ps1
Set-Location backend
& ..\venv\Scripts\python.exe -c "
try:
    from app.services.vector_db import get_vector_db_service
    service = get_vector_db_service()
    collection = service.get_or_create_collection()
    print(f'Vector database initialized with {collection.count()} documents')
except Exception as e:
    print(f'Vector database initialized (empty - add ticket data later)')
" 2>$null
Set-Location ..

Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Edit backend\.env and add your API key" -ForegroundColor White
Write-Host "2. Run the application: .\run.ps1" -ForegroundColor White
Write-Host ""
