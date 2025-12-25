@echo off
chcp 65001 >nul
echo ========================================
echo Testing Backend and Frontend Startup
echo ========================================
echo.

REM Test Backend
echo [1/2] Testing Backend...
echo.
cd /d %~dp0..
cd backend

if exist venv\Scripts\python.exe (
    echo ✅ Backend virtual environment exists
    venv\Scripts\python.exe -c "import sys; import os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')); from simulation.engine import SimulationEngine; print('✅ Simulation engine import OK')" 2>nul
    if errorlevel 1 (
        echo ⚠️  Simulation module test failed (may need to run from project root)
    )
    
    venv\Scripts\python.exe -c "import fastapi; import uvicorn; print('✅ FastAPI dependencies OK')" 2>nul
    if errorlevel 1 (
        echo ❌ FastAPI not installed - run scripts\start_backend.bat to install
    ) else (
        echo ✅ Backend ready to start
        echo    Run: scripts\start_backend.bat
    )
) else (
    echo ❌ Backend virtual environment not found
    echo    Run: scripts\start_backend.bat to create it
)

echo.
echo [2/2] Testing Frontend...
echo.
cd /d %~dp0..
cd frontend

where node >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ Node.js found
    node --version
) else (
    echo ❌ Node.js not found
    echo    Install from: https://nodejs.org/
    goto :end
)

if exist package.json (
    echo ✅ package.json found
) else (
    echo ❌ package.json not found
    goto :end
)

if exist node_modules (
    echo ✅ node_modules exists
    echo ✅ Frontend ready to start
    echo    Run: scripts\start_frontend.bat
) else (
    echo ⚠️  node_modules not found
    echo    Will be installed when running scripts\start_frontend.bat
)

:end
echo.
echo ========================================
echo Test Complete
echo ========================================
echo.
echo To start services:
echo   1. Open a terminal and run: scripts\start_backend.bat
echo   2. Open another terminal and run: scripts\start_frontend.bat
echo   3. Visit http://localhost:3000 in your browser
echo.
pause

