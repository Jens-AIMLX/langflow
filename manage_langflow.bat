@echo off
setlocal enabledelayedexpansion

:menu
cls
echo ===================================
echo    LANGFLOW MANAGEMENT CONSOLE
echo ===================================
echo.
echo  1. Start Langflow
echo  2. Stop Langflow
echo  3. Restart Langflow
echo  4. Check Langflow Status
echo  5. Exit
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto start
if "%choice%"=="2" goto stop
if "%choice%"=="3" goto restart
if "%choice%"=="4" goto status
if "%choice%"=="5" goto end
echo Invalid choice. Please try again.
timeout /t 2 >nul
goto menu

:start
cls
echo Starting Langflow...
echo.

REM Check if Langflow is already running
set "running=0"
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":7860" 2^>nul') do (
    set "running=1"
)

if "!running!"=="1" (
    echo Langflow appears to be already running.
    echo.
    echo You can access it at: http://127.0.0.1:7860/flows
    echo.
    pause
    goto menu
)

REM Start Langflow using run_langflow.bat
call run_langflow.bat
goto menu

:stop
cls
echo Stopping Langflow...
echo.

REM Find and terminate Langflow processes
taskkill /F /FI "WINDOWTITLE eq langflow*" /IM "python.exe" 2>nul
taskkill /F /FI "COMMANDLINE eq *langflow run*" /IM "python.exe" 2>nul
taskkill /F /FI "COMMANDLINE eq *-m langflow*" /IM "python.exe" 2>nul

REM Also try to terminate via port (Langflow typically uses port 7860)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":7860" 2^>nul') do (
    echo Found process using port 7860: %%a
    taskkill /F /PID %%a 2>nul
    if !ERRORLEVEL! EQU 0 (
        echo Successfully terminated process %%a
    ) else (
        echo Could not terminate process %%a. You may need administrative privileges.
    )
)

echo.
echo Langflow has been stopped.
echo.
pause
goto menu

:restart
cls
echo Restarting Langflow...
echo.

REM Stop Langflow
call :stop_silent

REM Start Langflow
timeout /t 2 >nul
call run_langflow.bat
goto menu

:status
cls
echo Checking Langflow Status...
echo.

REM Check if Langflow is running
set "running=0"
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":7860" 2^>nul') do (
    set "running=1"
    set "pid=%%a"
)

if "!running!"=="1" (
    echo Langflow is RUNNING on port 7860.
    echo Process ID: !pid!
    echo.
    echo You can access Langflow at: http://127.0.0.1:7860/flows
) else (
    echo Langflow is NOT RUNNING.
)

echo.
pause
goto menu

:stop_silent
REM Silently stop Langflow without messages or pauses
taskkill /F /FI "WINDOWTITLE eq langflow*" /IM "python.exe" 2>nul
taskkill /F /FI "COMMANDLINE eq *langflow run*" /IM "python.exe" 2>nul
taskkill /F /FI "COMMANDLINE eq *-m langflow*" /IM "python.exe" 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":7860" 2^>nul') do (
    taskkill /F /PID %%a 2>nul
)
exit /b

:end
exit 