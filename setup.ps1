# Auto-Ops-AI Setup Script

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Auto-Ops-AI Setup" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Create directories
Write-Host "Creating directories..." -ForegroundColor Green
New-Item -ItemType Directory -Force -Path "data\processed", "data\raw", "logs", "backend\data\processed" | Out-Null

# Check Python version
$pythonVersion = py --version 2>&1
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
    py -m venv venv
}

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Green
& .\venv\Scripts\python.exe -m pip install --upgrade pip -q
& .\venv\Scripts\pip.exe install -r $requirementsFile -q

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install dependencies!" -ForegroundColor Red
    exit 1
}

# Setup .env file (if not exists)
if (-not (Test-Path "backend\.env")) {
    if (Test-Path "backend\.env.example") {
        Copy-Item "backend\.env.example" "backend\.env"
        Write-Host ""
        Write-Host "Created backend\.env from example" -ForegroundColor Green
        Write-Host "⚠️  IMPORTANT: Edit backend\.env and add your GOOGLE_API_KEY!" -ForegroundColor Yellow
    } else {
        Write-Host ""
        Write-Host "WARNING: No .env.example found. Please create backend\.env manually." -ForegroundColor Yellow
    }
}

# Run comprehensive backend setup
Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Running Backend Setup" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "This will set up:" -ForegroundColor White
Write-Host "  ✓ Database initialization" -ForegroundColor Gray
Write-Host "  ✓ Migrations (if needed)" -ForegroundColor Gray
Write-Host "  ✓ Test users and agents" -ForegroundColor Gray
Write-Host "  ✓ Knowledge base ingestion" -ForegroundColor Gray
Write-Host ""

$currentDir = Get-Location
Set-Location backend

try {
    $setupOutput = & ..\venv\Scripts\python.exe setup_backend.py 2>&1
    $setupExitCode = $LASTEXITCODE
    
    Write-Host $setupOutput
    
    if ($setupExitCode -eq 0) {
        Write-Host ""
        Write-Host "[OK] Backend setup completed successfully!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "⚠️  Backend setup had some issues" -ForegroundColor Yellow
        Write-Host "   You can retry by running:" -ForegroundColor Cyan
        Write-Host "   cd backend; ..\venv\Scripts\python.exe setup_backend.py" -ForegroundColor White
    }
} finally {
    Set-Location $currentDir
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Start the backend:" -ForegroundColor Cyan
Write-Host "     .\run.ps1" -ForegroundColor White
Write-Host ""
Write-Host "  2. Or start manually:" -ForegroundColor Cyan
Write-Host "     cd backend" -ForegroundColor White
Write-Host "     ..\venv\Scripts\python.exe -m uvicorn app.main:app --reload" -ForegroundColor White
Write-Host ""
Write-Host "  3. API will be available at:" -ForegroundColor Cyan
Write-Host "     http://localhost:8000" -ForegroundColor White
Write-Host "     http://localhost:8000/docs (API Documentation)" -ForegroundColor White
Write-Host ""
Write-Host "  4. Admin Credentials:" -ForegroundColor Yellow
Write-Host "     Email:    admin@acme.com" -ForegroundColor White
Write-Host "     Password: admin123" -ForegroundColor White
Write-Host ""
