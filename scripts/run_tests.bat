@echo off
echo Running Tests...
echo.

REM Change to project root directory
cd /d %~dp0..

py tests/run_tests.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo All tests passed!
) else (
    echo.
    echo Some tests failed. Check the output above.
)

pause

