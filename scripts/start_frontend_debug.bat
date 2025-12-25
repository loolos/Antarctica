@echo off
chcp 65001
echo ========================================
echo Starting Frontend Service (Debug Mode)
echo ========================================
echo.

REM Change to project root directory
cd /d %~dp0..
echo Current directory: %CD%
echo.

REM Check Node.js
echo [1/5] Checking Node.js...
where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Node.js not found!
    echo Please install Node.js from https://nodejs.org/
    echo.
    pause
    exit /b 1
)
echo OK - Node.js found
node --version
echo.

REM Check frontend directory
echo [2/5] Checking frontend directory...
if not exist "frontend" (
    echo ERROR: frontend directory not found!
    echo Current directory: %CD%
    echo.
    pause
    exit /b 1
)
echo OK - frontend directory exists
cd frontend
echo Changed to: %CD%
echo.

REM Check package.json
echo [3/5] Checking package.json...
if not exist "package.json" (
    echo ERROR: package.json not found!
    echo.
    pause
    exit /b 1
)
echo OK - package.json found
echo.

REM Check node_modules
echo [4/5] Checking dependencies...
if not exist "node_modules" (
    echo WARNING: node_modules not found
    echo Installing dependencies...
    echo.
    call npm install --legacy-peer-deps
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo ERROR: npm install failed with code %ERRORLEVEL%
        echo.
        pause
        exit /b 1
    )
    echo.
    echo OK - Dependencies installed
) else (
    echo OK - node_modules exists
)
echo.

REM Check if react-scripts is installed
echo [5/5] Checking react-scripts...
if not exist "node_modules\react-scripts" (
    echo ERROR: react-scripts not found in node_modules!
    echo Try running: npm install --legacy-peer-deps
    echo.
    pause
    exit /b 1
)
echo OK - react-scripts found
echo.

echo ========================================
echo All checks passed! Starting server...
echo ========================================
echo.
echo Frontend will be available at: http://localhost:3000
echo Press Ctrl+C to stop
echo.
echo ========================================
echo.

REM Start npm with error handling
call npm start
set EXIT_CODE=%ERRORLEVEL%

echo.
echo ========================================
echo Server stopped
echo Exit code: %EXIT_CODE%
echo ========================================
echo.

if %EXIT_CODE% NEQ 0 (
    echo ERROR: npm start failed with exit code %EXIT_CODE%
    echo.
    echo Common issues:
    echo 1. Port 3000 might be in use
    echo 2. Dependencies might be corrupted - try: npm install --legacy-peer-deps
    echo 3. Check the error messages above
    echo.
)

pause

