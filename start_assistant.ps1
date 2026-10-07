# AI-Based Multilingual Government Scheme & Job Assistant Launcher
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  AI Multilingual Government Scheme & Job Assistant       " -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Select what you want to run:"
Write-Host "1) Start FastAPI Backend Server (Port 8000)"
Write-Host "2) Start Streamlit Interactive Frontend (Port 8501)"
Write-Host "3) Run Full End-to-End API Test Suite"
Write-Host ""

$choice = Read-Host "Enter option (1, 2, or 3)"

if ($choice -eq "1") {
    Write-Host "Starting FastAPI Backend..." -ForegroundColor Green
    & ".\.venv\Scripts\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
} elseif ($choice -eq "2") {
    Write-Host "Starting Streamlit Frontend Portal..." -ForegroundColor Green
    & ".\.venv\Scripts\streamlit.exe" run frontend_app.py
} elseif ($choice -eq "3") {
    Write-Host "Running Automated End-to-End Test Suite..." -ForegroundColor Green
    & ".\.venv\Scripts\python.exe" scripts\test_api_endpoints.py
} else {
    Write-Host "Invalid option selected." -ForegroundColor Red
}
