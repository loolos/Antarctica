@echo off
chcp 65001 >nul
REM ========================================
REM Auto-close timer (in seconds)
REM Set to 0 to disable auto-close (run forever)
REM Default: 60 seconds (1 minute)
REM ========================================
set AUTO_CLOSE=60

echo ========================================
echo Starting Backend Service...
if %AUTO_CLOSE% EQU 0 (
    echo Auto-close: DISABLED (will run until manually stopped)
) else (
    echo Auto-close: ENABLED (will close after %AUTO_CLOSE% seconds)
)
echo ========================================
REM Change to project root directory
cd /d %~dp0..
cd backend

REM Check if virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    py -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment, please ensure Python is installed
        pause
        exit /b 1
    )
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if dependencies are installed
if not exist venv\Scripts\fastapi.exe (
    echo Installing dependencies...
    py -m pip install --upgrade pip
    if errorlevel 1 (
        echo Error: pip upgrade failed
        pause
        exit /b 1
    )
    py -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install dependencies
        pause
        exit /b 1
    )
) else (
    echo Dependencies installed, skipping...
)

echo.
echo Starting server...
echo Backend URL: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
if %AUTO_CLOSE% EQU 0 (
    echo Press Ctrl+C to stop the server
) else (
    echo Server will auto-close after %AUTO_CLOSE% seconds
    echo Press Ctrl+C to stop the server manually
)
echo ========================================
echo.

REM Wait for auto-close timer (if enabled)
if not %AUTO_CLOSE% EQU 0 (
    REM Start server in background
    start /B py main.py
    
    echo Waiting %AUTO_CLOSE% seconds before auto-closing...
    timeout /t %AUTO_CLOSE% /nobreak >nul
    echo.
    echo Auto-closing server...
    REM Find and kill the Python process running main.py
    for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq python.exe" /FO CSV ^| findstr /I "python.exe"') do (
        wmic process where "CommandLine like '%%main.py%%' AND ProcessId=%%a" delete >nul 2>&1
    )
    REM Also try to kill by port 8000
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
        taskkill /F /PID %%a >nul 2>&1
    )
    echo Server closed.
) else (
    REM Run server in foreground (user must stop manually)
    py main.py
)
