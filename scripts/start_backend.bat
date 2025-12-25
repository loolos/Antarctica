@echo off
chcp 65001 >nul
echo ========================================
echo Starting Backend Service...
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
echo Press Ctrl+C to stop the server
echo ========================================
echo.

py main.py

pause
