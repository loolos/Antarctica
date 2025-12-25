@echo off
chcp 65001
title Frontend Server - Antarctic Simulation

echo ========================================
echo Starting Frontend Service...
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
echo Keep this window open while the server is running
echo Press Ctrl+C to stop the server
echo ========================================
echo.

REM Prevent browser from auto-opening
set BROWSER=none

REM Start npm
call npm start

REM If we get here, npm start exited
echo.
echo ========================================
echo Server stopped
echo ========================================
echo.
pause

