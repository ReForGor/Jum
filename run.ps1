# TechPrice Windows PowerShell Startup Script

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "⚡ Starting TechPrice Thailand IT Equipment Aggregator" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan

# Check Python
try {
    $pyVersion = python --version
    Write-Host "Found: $pyVersion" -ForegroundColor Gray
} catch {
    Write-Host "[ERROR] Python is not installed or not in PATH!" -ForegroundColor Red
    Write-Host "Please install Python 3.10+ from https://www.python.org/downloads/"
    Exit 1
}

# Create venv if needed
if (-Not (Test-Path -Path ".\venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip
    pip install -r requirements.txt
} else {
    .\venv\Scripts\Activate.ps1
}

$PORT = "8000"
$checkPort = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($checkPort) {
    Write-Host "[INFO] Port 8000 is occupied or reserved, switching to port 8001..." -ForegroundColor Yellow
    $PORT = "8001"
}
$APP_HOST = "0.0.0.0"

Write-Host ""
Write-Host "🌐 Web Dashboard:    http://localhost:$PORT" -ForegroundColor Cyan
Write-Host "🛡️ Admin Portal:     http://localhost:$PORT/admin" -ForegroundColor Magenta
Write-Host "🔔 Watchlist/Alerts: http://localhost:$PORT/watchlist" -ForegroundColor Yellow
Write-Host "📊 Compare Matrix:   http://localhost:$PORT/compare" -ForegroundColor Green
Write-Host "⚡ Thai Scrapers:    http://localhost:$PORT/platforms" -ForegroundColor Cyan
Write-Host "🚀 API Swagger Docs: http://localhost:$PORT/docs" -ForegroundColor Blue
Write-Host ""

uvicorn app.main:app --host $APP_HOST --port $PORT --reload
