@echo off
REM CrisisMesh Demo Recording Helper
REM Run this to start all services for demo recording

echo ============================================
echo CrisisMesh Demo Environment Setup
echo ============================================
echo.

echo [1/4] Starting Backend API...
cd /d "C:\Users\venka\Gen AI Hackathon\CrisisMesh\backend"
start "CrisisMesh Backend" cmd /k ".venv\Scripts\activate && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info"

timeout /t 5 /nobreak >nul

echo [2/4] Starting Frontend Dev Server...
cd /d "C:\Users\venka\Gen AI Hackathon\CrisisMesh\frontend"
start "CrisisMesh Frontend" cmd /k "npm run dev"

timeout /t 3 /nobreak >nul

echo [3/4] Verifying Health Check...
curl -s http://localhost:8000/health

echo.
echo [4/4] Opening Demo URLs...
start http://localhost:5173
start http://localhost:8000/api/v1/scenarios

echo.
echo ============================================
echo Demo Environment Ready!
echo ============================================
echo.
echo Frontend:  http://localhost:5173
echo Backend:   http://localhost:8000
echo Health:    http://localhost:8000/health
echo Scenarios: http://localhost:8000/api/v1/scenarios
echo.
echo For recording:
echo 1. Use OBS Studio or Windows Game Bar (Win+G)
echo 2. Record at 1920x1080, 30fps
echo 3. Follow DEMO_SCRIPT.md timing
echo 4. Backup: run 'python test_pipeline.py' in backend folder
echo.
pause