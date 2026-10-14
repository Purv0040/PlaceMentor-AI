# ============================================================
#  PlaceMentor AI - Full Project Starter
#  Run from project root:  .\start.ps1
# ============================================================

$root = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   PlaceMentor AI - Starting All Services" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ---- Backend (FastAPI via uvicorn) ----
Write-Host "[1/2] Starting Backend (FastAPI)  --> http://localhost:8000" -ForegroundColor Yellow
Start-Process powershell -ArgumentList `
    "-NoExit", `
    "-Command", `
    "cd '$root\Backend'; Write-Host 'Backend starting...' -ForegroundColor Green; .venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

Start-Sleep -Seconds 2

# ---- Frontend (Vite dev server) ----
Write-Host "[2/2] Starting Frontend (Vite)    --> http://localhost:3000" -ForegroundColor Yellow
Start-Process powershell -ArgumentList `
    "-NoExit", `
    "-Command", `
    "cd '$root\Frontend'; Write-Host 'Frontend starting...' -ForegroundColor Green; npm run dev"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Both servers launched in new windows!" -ForegroundColor Green
Write-Host ""
Write-Host "  Frontend : http://localhost:3000"      -ForegroundColor White
Write-Host "  Backend  : http://localhost:8000"      -ForegroundColor White
Write-Host "  API Docs : http://localhost:8000/docs" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
