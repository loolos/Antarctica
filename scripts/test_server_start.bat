@echo off
chcp 65001 >nul
echo ========================================
echo Testing Backend Server Startup
echo ========================================
echo.

REM Change to project root directory
cd /d %~dp0..

REM Check virtual environment
if not exist "backend\venv\Scripts\python.exe" (
    echo ❌ Virtual environment not found, please run start_backend.bat first
    pause
    exit /b 1
)

echo ✅ Virtual environment exists
echo.

REM Test imports
echo Testing module imports...
backend\venv\Scripts\python.exe -c "import sys; sys.path.insert(0, '.'); from simulation.engine import SimulationEngine; print('✅ simulation module imported successfully')"
if errorlevel 1 (
    echo ❌ simulation module import failed
    pause
    exit /b 1
)

backend\venv\Scripts\python.exe -c "import fastapi; import uvicorn; print('✅ FastAPI dependencies installed')"
if errorlevel 1 (
    echo ❌ FastAPI dependencies not installed
    echo Installing...
    backend\venv\Scripts\python.exe -m pip install -r backend\requirements.txt
)

echo.
echo ========================================
echo ✅ All checks passed!
echo ========================================
echo.
echo Starting server...
echo Server URL: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

cd backend
..\backend\venv\Scripts\python.exe main.py

pause
