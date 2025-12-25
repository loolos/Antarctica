@echo off
chcp 65001 >nul
echo ========================================
echo Fix Port 8000 Conflict
echo ========================================
echo.

echo Checking for processes using port 8000...
netstat -ano | findstr ":8000"

echo.
echo Terminating processes on port 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo Terminating process %%a
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo Waiting 2 seconds...
timeout /t 2 /nobreak >nul

echo.
echo Checking port 8000 again...
netstat -ano | findstr ":8000"
if %ERRORLEVEL% NEQ 0 (
    echo ✅ Port 8000 is now free!
) else (
    echo ⚠️  Port 8000 is still in use
)

echo.
echo ========================================
pause

