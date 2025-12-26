@echo off
chcp 65001
title Frontend Server - Antarctic Simulation

REM ========================================
REM Auto-close timer (in seconds)
REM Set to 0 to disable auto-close (run forever)
REM Default: 60 seconds (1 minute)
REM ========================================
set AUTO_CLOSE=60

echo ========================================
echo Starting Frontend Service...
if %AUTO_CLOSE% EQU 0 (
    echo Auto-close: DISABLED (will run until manually stopped)
) else (
    echo Auto-close: ENABLED (will close after %AUTO_CLOSE% seconds)
)
echo ========================================
echo.

REM Change to project root directory
cd /d %~dp0..

REM Check Node.js
where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Node.js not found!
    echo Please install Node.js: https://nodejs.org/
    echo.
    pause
    exit /b 1
)

REM Check frontend directory
if not exist "frontend" (
    echo ERROR: frontend directory not found!
    echo Current directory: %CD%
    echo.
    pause
    exit /b 1
)

cd frontend

REM Check package.json
if not exist "package.json" (
    echo ERROR: package.json not found!
    echo.
    pause
    exit /b 1
)

REM Install dependencies if needed
if not exist "node_modules" (
    echo Installing dependencies... this may take a few minutes.
    echo.
    call npm install --legacy-peer-deps
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo ERROR: npm install failed
        echo Check the error messages above
        echo.
        pause
        exit /b 1
    )
    echo.
    echo Dependencies installed successfully!
    echo.
)

echo ========================================
echo Starting development server...
echo Frontend will be available at: http://localhost:3000
echo.
if %AUTO_CLOSE% EQU 0 (
    echo Keep this window open while the server is running
    echo Press Ctrl+C to stop the server
) else (
    echo Server will auto-close after %AUTO_CLOSE% seconds
    echo Press Ctrl+C to stop the server manually
)
echo ========================================
echo.

REM Prevent browser from auto-opening
set BROWSER=none

REM Wait for auto-close timer (if enabled)
if not %AUTO_CLOSE% EQU 0 (
    REM Start npm in background
    start /B cmd /c "npm start"
    
    echo Waiting %AUTO_CLOSE% seconds before auto-closing...
    timeout /t %AUTO_CLOSE% /nobreak >nul
    echo.
    echo Auto-closing server...
    REM Find and kill Node.js processes on port 3000
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3000" ^| findstr "LISTENING"') do (
        taskkill /F /PID %%a >nul 2>&1
    )
    REM Also kill node processes
    taskkill /F /IM node.exe >nul 2>&1
    echo Server closed.
) else (
    REM Run npm in foreground (user must stop manually)
    call npm start
)

REM If we get here, server exited
echo.
echo ========================================
echo Server stopped
echo ========================================
echo.

