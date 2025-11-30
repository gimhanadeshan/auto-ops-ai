@echo off
REM Auto-Ops-AI Run Script for Windows Command Prompt

echo.
echo =========================================
echo Auto-Ops-AI Backend Server Launcher
echo =========================================
echo.

REM Check if venv exists
if not exist "venv" (
    echo ERROR: Virtual environment not found!
    echo Please run setup.ps1 first
    pause
    exit /b 1
)

REM Activate venv
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if .env exists
if not exist "backend\.env" (
    echo.
    echo WARNING: backend\.env not found!
    echo Copy backend\.env.example and add your API keys
    echo.
)

REM Start the server
echo.
echo Starting Auto-Ops-AI Backend Server...
echo Server available at: http://127.0.0.1:8000
echo API Docs: http://127.0.0.1:8000/docs
echo.
echo Press CTRL+C to stop the server
echo.

REM Change to backend directory and run uvicorn
cd backend
python -m uvicorn app.main:app --reload
