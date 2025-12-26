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

REM Start backend using start_backend.bat (with AUTO_CLOSE=0 so it runs until we kill it)
echo.
echo [1/3] Starting backend server...
set AUTO_CLOSE=0
start "Backend Server" cmd /c "cd /d %~dp0 && set AUTO_CLOSE=0 && scripts\start_backend.bat"

REM Wait for backend to start
echo Waiting for backend to start (3 seconds)...
timeout /t 3 /nobreak >nul

REM Start frontend using start_frontend.bat (with AUTO_CLOSE=0 so it runs until we kill it)
echo [2/3] Starting frontend server...
start "Frontend Server" cmd /c "cd /d %~dp0 && set AUTO_CLOSE=0 && set BROWSER=none && scripts\start_frontend.bat"

REM Wait for frontend to start
echo Waiting for frontend to start (3 seconds)...
timeout /t 3 /nobreak >nul

REM Open browser manually (only once)
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

REM Close backend
echo Closing backend...
REM Method 1: Kill by port
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%BACKEND_PORT%" ^| findstr "LISTENING"') do (
    echo   Killing backend process on port %BACKEND_PORT% (PID: %%a)
    taskkill /F /PID %%a >nul 2>&1
)
REM Method 2: Kill Python processes running main.py
for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq python.exe" /FO CSV ^| findstr /I "python.exe"') do (
    wmic process where "CommandLine like '%%main.py%%' AND ProcessId=%%a" delete >nul 2>&1
)
REM Method 3: Kill by window title (Backend Server)
for /f "tokens=2" %%a in ('tasklist /FI "WINDOWTITLE eq Backend Server*" /FO CSV ^| findstr /I "cmd.exe"') do (
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 1 /nobreak >nul

REM Close frontend
echo Closing frontend...
REM Method 1: Kill by port
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%FRONTEND_PORT%" ^| findstr "LISTENING"') do (
    echo   Killing frontend process on port %FRONTEND_PORT% (PID: %%a)
    taskkill /F /PID %%a >nul 2>&1
)
REM Method 2: Kill all node processes (frontend)
taskkill /F /IM node.exe >nul 2>&1
REM Method 3: Kill by window title (Frontend Server)
for /f "tokens=2" %%a in ('tasklist /FI "WINDOWTITLE eq Frontend Server*" /FO CSV ^| findstr /I "cmd.exe"') do (
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 1 /nobreak >nul

echo.
echo ========================================
echo Services closed.
echo ========================================
