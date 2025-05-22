@echo off
echo Stopping Langflow...

REM Find and terminate Langflow processes
taskkill /F /FI "WINDOWTITLE eq langflow*" /IM "python.exe" 2>nul
taskkill /F /FI "COMMANDLINE eq *langflow run*" /IM "python.exe" 2>nul
taskkill /F /FI "COMMANDLINE eq *-m langflow*" /IM "python.exe" 2>nul

REM Also try to terminate via port (Langflow typically uses port 7860)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":7860"') do (
    echo Found process using port 7860: %%a
    taskkill /F /PID %%a 2>nul
    if %ERRORLEVEL% EQU 0 (
        echo Successfully terminated process %%a
    ) else (
        echo Could not terminate process %%a. You may need administrative privileges.
    )
)

REM Verify if any Langflow processes are still running
set "processes_found=0"
for /f "tokens=2" %%p in ('tasklist /fi "IMAGENAME eq python.exe" /fi "WINDOWTITLE eq langflow*" ^| findstr "python"') do (
    set "processes_found=1"
)

for /f "tokens=2" %%p in ('tasklist /fi "IMAGENAME eq python.exe" /v ^| findstr /i "langflow"') do (
    set "processes_found=1"
)

if "%processes_found%"=="0" (
    echo Langflow has been successfully stopped.
) else (
    echo Warning: Some Langflow processes might still be running.
    echo You may need to manually end these processes in Task Manager.
)

echo.
echo To start Langflow again, run: run_langflow.bat
echo. 