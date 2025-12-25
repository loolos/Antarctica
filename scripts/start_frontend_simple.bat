@echo off
chcp 65001
title Frontend Server

echo ========================================
echo Starting Frontend...
echo ========================================
echo.

REM Change to project root directory
cd /d %~dp0..
cd frontend

if not exist "node_modules" (
    echo Installing dependencies first...
    call npm install --legacy-peer-deps
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install dependencies
        echo.
        pause
        exit /b 1
    )
    echo.
)

echo Starting React development server...
echo.
echo The server will start at http://localhost:3000
echo Keep this window open while the server is running
echo Press Ctrl+C to stop the server
echo.
echo ========================================
echo.

REM Set BROWSER=none to prevent auto-opening browser
set BROWSER=none

REM Start npm and keep window open
call npm start

REM If we get here, npm start exited
echo.
echo ========================================
echo Server stopped
echo ========================================
echo.
pause

