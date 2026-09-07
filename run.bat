@echo off
setlocal

echo ==========================================================
echo ⚡ Starting TechPrice Thailand IT Equipment Aggregator
echo ==========================================================

:: Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Create Virtual Environment if not exists
if not exist "venv\" (
    echo Creating Python Virtual Environment (venv)...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Upgrading pip and installing required packages...
    python -m pip install --upgrade pip
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

set PORT=8000
set HOST=0.0.0.0

echo.
echo ----------------------------------------------------------
echo 🌐 Web Dashboard:    http://localhost:%PORT%
echo 🛡️ Admin Portal:     http://localhost:%PORT%/admin
echo 🔔 Watchlist/Alerts: http://localhost:%PORT%/watchlist
echo 📊 Compare Matrix:   http://localhost:%PORT%/compare
echo ⚡ Thai Scrapers:    http://localhost:%PORT%/platforms
echo 🚀 API Swagger Docs: http://localhost:%PORT%/docs
echo ----------------------------------------------------------
echo.

:: Start Uvicorn Server on Windows
uvicorn app.main:app --host %HOST% --port %PORT% --reload

pause
