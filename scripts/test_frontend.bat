@echo off
chcp 65001 >nul
echo Testing Frontend Setup...
echo.

REM Change to project root directory
cd /d %~dp0..
cd frontend

echo Checking Node.js...
where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Node.js not found
    exit /b 1
) else (
    echo ✅ Node.js found
)

echo.
echo Checking npm...
npm --version
if %ERRORLEVEL% NEQ 0 (
    echo ❌ npm not working
    exit /b 1
) else (
    echo ✅ npm working
)

echo.
echo Checking dependencies...
if not exist node_modules (
    echo ❌ node_modules not found
    echo Installing dependencies...
    call npm install --legacy-peer-deps
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ npm install failed
        exit /b 1
    )
) else (
    echo ✅ node_modules exists
)

echo.
echo ✅ Frontend setup looks good!
echo.
echo You can now run: start_frontend.bat
echo.
pause

