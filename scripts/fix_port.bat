@echo off
chcp 65001 >nul
echo ========================================
echo Fix Port Conflicts (8000 and 3000)
echo ========================================
echo.

REM Fix port 8000 (backend)
echo Checking for processes using port 8000...
netstat -ano | findstr ":8000"

echo.
echo Terminating processes on port 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo Terminating process %%a on port 8000
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
echo.

REM Fix port 3000 (frontend)
echo Checking for processes using port 3000...
netstat -ano | findstr ":3000"

echo.
echo Terminating processes on port 3000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3000" ^| findstr "LISTENING"') do (
    echo Terminating process %%a on port 3000
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo Waiting 2 seconds...
timeout /t 2 /nobreak >nul

echo.
echo Checking port 3000 again...
netstat -ano | findstr ":3000"
if %ERRORLEVEL% NEQ 0 (
    echo ✅ Port 3000 is now free!
) else (
    echo ⚠️  Port 3000 is still in use
)

echo.
echo ========================================
pause

