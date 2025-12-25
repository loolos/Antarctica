@echo off
echo Running Tests...
echo.

py tests/run_tests.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo All tests passed!
) else (
    echo.
    echo Some tests failed. Check the output above.
)

pause

