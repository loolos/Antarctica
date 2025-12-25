@echo off
chcp 65001 >nul
REM ========================================
REM Auto-start backend and frontend, open browser, and close after 60 seconds
REM ========================================

set AUTO_CLOSE=60
set BACKEND_PORT=8000
set FRONTEND_PORT=3000

echo ========================================
echo Starting Antarctic Ecosystem Simulation
echo Auto-close: %AUTO_CLOSE% seconds
echo ========================================
echo.

REM Change to project root directory
cd /d %~dp0

REM Kill any existing processes on the ports
echo Checking for existing processes...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%BACKEND_PORT%" ^| findstr "LISTENING"') do (
    echo Killing process on port %BACKEND_PORT% (PID: %%a)
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%FRONTEND_PORT%" ^| findstr "LISTENING"') do (
    echo Killing process on port %FRONTEND_PORT% (PID: %%a)
    taskkill /F /PID %%a >nul 2>&1
)

REM Start backend in background
echo.
echo [1/3] Starting backend server...
cd backend
if not exist "venv\Scripts\activate.bat" (
    echo Error: Virtual environment not found. Please create it first.
    pause
    exit /b 1
)
call venv\Scripts\activate.bat
REM Start backend with AUTO_CLOSE=0 (we'll control it from here)
start "Backend Server" cmd /c "set AUTO_CLOSE=0 && venv\Scripts\activate.bat && python main.py"
cd ..

REM Wait for backend to start
echo Waiting for backend to start (5 seconds)...
timeout /t 5 /nobreak >nul

REM Start frontend in background
echo [2/3] Starting frontend server...
cd frontend
if not exist "node_modules" (
    echo Error: node_modules not found. Please run 'npm install' first.
    pause
    exit /b 1
)
REM Prevent browser auto-open from npm start and set AUTO_CLOSE=0
set BROWSER=none
start "Frontend Server" cmd /c "set BROWSER=none && set AUTO_CLOSE=0 && npm start"
cd ..

REM Wait for frontend to start (React dev server takes longer)
echo Waiting for frontend to start (15 seconds)...
timeout /t 15 /nobreak >nul

REM Open browser manually
echo [3/3] Opening browser...
start http://localhost:%FRONTEND_PORT%

echo.
echo ========================================
echo Services started successfully!
echo Backend: http://localhost:%BACKEND_PORT%
echo Frontend: http://localhost:%FRONTEND_PORT%
echo.
echo Services will close automatically in %AUTO_CLOSE% seconds...
echo Press Ctrl+C to stop manually
echo ========================================
echo.

REM Wait for the full AUTO_CLOSE duration (from now, after services are ready)
echo Waiting %AUTO_CLOSE% seconds before auto-closing...
timeout /t %AUTO_CLOSE% /nobreak

REM Close services
echo.
echo Closing services...
echo Closing backend...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%BACKEND_PORT%" ^| findstr "LISTENING"') do (
    echo   Killing backend process (PID: %%a)
    taskkill /F /PID %%a >nul 2>&1
)
REM Also kill Python processes running main.py
for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq python.exe" /FO CSV ^| findstr /I "python.exe"') do (
    wmic process where "CommandLine like '%%main.py%%' AND ProcessId=%%a" delete >nul 2>&1
)

echo Closing frontend...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%FRONTEND_PORT%" ^| findstr "LISTENING"') do (
    echo   Killing frontend process (PID: %%a)
    taskkill /F /PID %%a >nul 2>&1
)
REM Also kill all node processes (frontend)
taskkill /F /IM node.exe >nul 2>&1

echo.
echo ========================================
echo Services closed.
echo ========================================
pause

