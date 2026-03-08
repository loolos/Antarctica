@echo off
chcp 65001 >nul
title Antarctic Simulation - Backend + Frontend (120s)

REM ========================================
REM Start both backend and frontend, then
REM auto-close after 120 seconds
REM ========================================
set RUN_DURATION=120

echo ========================================
echo Starting Backend and Frontend
echo Will auto-close after %RUN_DURATION% seconds
echo ========================================
echo.

REM Change to project root directory
cd /d %~dp0..

REM Kill any existing processes on ports 8000 and 3000
echo Clearing ports 8000 and 3000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3000" ^| findstr "LISTENING"') do taskkill /F /PID %%a >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
ping 127.0.0.1 -n 2 >nul

REM ---- Step 1: Prepare and start Backend ----
echo [1/2] Starting Backend...
cd backend

if not exist venv (
    echo Creating virtual environment...
    py -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment
        pause
        exit /b 1
    )
)

call venv\Scripts\activate.bat

if not exist venv\Scripts\fastapi.exe (
    echo Installing backend dependencies...
    py -m pip install --upgrade pip
    py -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install backend dependencies
        pause
        exit /b 1
    )
)

echo Starting backend on http://localhost:8000
start /B py main.py
set BACKEND_STARTED=1
cd ..

REM Give backend a moment to start (use ping instead of timeout for compatibility)
ping 127.0.0.1 -n 3 >nul

REM ---- Step 2: Prepare and start Frontend ----
echo.
echo [2/2] Starting Frontend...
cd frontend

where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Node.js not found! Please install Node.js
    goto :cleanup
)

if not exist node_modules (
    echo Installing frontend dependencies...
    call npm install --legacy-peer-deps
    if errorlevel 1 (
        echo Error: Failed to install frontend dependencies
        goto :cleanup
    )
)

set BROWSER=none
echo Starting frontend on http://localhost:3000
start /B cmd /c "npm start"
cd ..

REM Give frontend a moment to start (use ping instead of timeout for compatibility)
ping 127.0.0.1 -n 6 >nul

REM ---- Step 3: Wait then cleanup ----
echo.
echo ========================================
echo Both services are running!
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Waiting %RUN_DURATION% seconds before auto-closing...
echo Press Ctrl+C to stop early
echo ========================================
echo.

REM Wait 120 seconds (ping -n 121 = ~120 sec, avoids timeout input-redirect issues)
ping 127.0.0.1 -n 121 >nul

:cleanup
echo.
echo Shutting down...

REM Kill frontend (port 3000 and node processes)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3000" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)
taskkill /F /IM node.exe >nul 2>&1

REM Kill backend (port 8000)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo ========================================
echo All services stopped
echo ========================================
pause
