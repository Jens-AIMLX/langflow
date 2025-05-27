@echo off
echo Testing Python detection...

echo Checking for python command...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python command not found.
    echo Checking for py launcher...
    py --version >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo Py launcher not found either.
        set PYTHON_CMD=none
    ) else (
        echo Found py launcher.
        set PYTHON_CMD=py
    )
) else (
    echo Found python command.
    set PYTHON_CMD=python
)

if "%PYTHON_CMD%"=="none" (
    echo No Python installation found.
) else (
    echo Using Python command: %PYTHON_CMD%
    echo Python version:
    %PYTHON_CMD% --version
)

echo Test completed.
pause
