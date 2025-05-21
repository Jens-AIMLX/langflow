@echo off
setlocal enabledelayedexpansion
echo Installing Langflow using uv...

REM Step 0: Thorough cleanup of any existing Langflow processes
echo Performing thorough cleanup...

REM Kill any Python processes with langflow in the title
taskkill /F /IM "python.exe" /FI "WINDOWTITLE eq langflow*" > nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Terminated Langflow processes with matching window title.
)

REM Kill any Python processes running langflow module
for /f "tokens=2" %%a in ('tasklist /fi "imagename eq python.exe" /v ^| findstr /i "langflow"') do (
    taskkill /F /PID %%a > nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo Terminated Python process with PID %%a.
    )
)

REM Check for any processes using port 7860
for /f "tokens=5" %%p in ('netstat -ano ^| findstr :7860') do (
    taskkill /F /PID %%p > nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo Terminated process with PID %%p using port 7860.
    )
)

echo Cleanup completed.

REM Step 1: Check if Rust is installed
rustc --version > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Rust is required for some dependencies but is not installed.
    echo Please install Rust from https://rustup.rs/ and run this script again.
    echo.
    echo After installing Rust, restart your command prompt and run this script again.
    exit /b 1
)

REM Step 2: Add the x86_64-pc-windows-msvc target for Rust (64-bit)
echo Adding required Rust target (x86_64-pc-windows-msvc)...
rustup target add x86_64-pc-windows-msvc

REM Step 3: Set environment variables to force 64-bit architecture
echo Setting environment variables to force 64-bit architecture...
set ARCHFLAGS=-arch x86_64
set DISTUTILS_ARCHITECTURE=x86_64
set DISTUTILS_PLATFORM=win-amd64

REM Step 4: Clean up and recreate the virtual environment
echo Checking for existing virtual environment...
if exist langflow_venv (
    echo Removing existing virtual environment...
    rmdir /s /q langflow_venv
    if !ERRORLEVEL! NEQ 0 (
        echo Failed to remove existing virtual environment. Please close any applications using it and try again.
        exit /b 1
    )
)

echo Creating fresh virtual environment...
py -m venv langflow_venv
if %ERRORLEVEL% NEQ 0 (
    echo Failed to create virtual environment.
    exit /b 1
)

REM Step 5: Activate the virtual environment
echo Activating virtual environment...
call langflow_venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo Failed to activate virtual environment.
    exit /b 1
)

REM Step 6: Upgrade pip and install uv
echo Upgrading pip and installing uv...
python -m pip install --upgrade pip
python -m pip install uv
if %ERRORLEVEL% NEQ 0 (
    echo Failed to install uv.
    exit /b 1
)

REM Step 7: Install Langflow with all dependencies
echo Installing Langflow with all dependencies...
python -m uv pip install "langflow==1.1.4" --verbose
if %ERRORLEVEL% NEQ 0 (
    echo Failed to install Langflow.
    exit /b 1
)

REM Step 8: Run Langflow
echo Starting Langflow...
echo Running command: python -m langflow run

REM Create a log directory if it doesn't exist
if not exist logs mkdir logs

REM Start Langflow in a new window and log output
start "Langflow" cmd /c "python -m langflow run > logs\langflow_startup.log 2>&1"

REM Step 9: Health check to verify Langflow is running
echo Performing health check...
echo Waiting for Langflow to start (15 seconds)...
timeout /t 15 /nobreak > nul

REM Try multiple health check endpoints
echo Checking if Langflow is running...
set /a max_attempts=5
set /a attempt=1
set backend_running=0

:check_backend_loop
if %attempt% gtr %max_attempts% goto :check_backend_done
echo Attempt %attempt% of %max_attempts%...

REM Try the /health endpoint
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://127.0.0.1:7860/health' -TimeoutSec 2 -UseBasicParsing; if ($response.StatusCode -eq 200) { Write-Host 'Langflow is running! (Status: ' $response.StatusCode ')' -ForegroundColor Green; exit 0 } else { exit 1 } } catch { exit 1 }" > nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set backend_running=1
    goto :check_backend_done
)

REM Try the /health_check endpoint
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://127.0.0.1:7860/health_check' -TimeoutSec 2 -UseBasicParsing; if ($response.StatusCode -eq 200) { Write-Host 'Langflow is running! (Status: ' $response.StatusCode ')' -ForegroundColor Green; exit 0 } else { exit 1 } } catch { exit 1 }" > nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set backend_running=1
    goto :check_backend_done
)

REM Try the root endpoint
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://127.0.0.1:7860/' -TimeoutSec 2 -UseBasicParsing; if ($response.StatusCode -eq 200) { Write-Host 'Langflow is running! (Status: ' $response.StatusCode ')' -ForegroundColor Green; exit 0 } else { exit 1 } } catch { exit 1 }" > nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set backend_running=1
    goto :check_backend_done
)

echo Langflow not responding yet...
set /a attempt+=1
timeout /t 3 /nobreak > nul
goto :check_backend_loop

:check_backend_done
if %backend_running%==1 (
    echo Langflow is running successfully!
) else (
    echo Health check failed. Langflow may not be running correctly.
    echo Checking startup log:
    echo ----------------------------------------------------------------------------------
    type logs\langflow_startup.log
    echo ----------------------------------------------------------------------------------
)

echo.
echo If Langflow started successfully, you can access it at: http://127.0.0.1:7860/flows
echo.
echo To restart Langflow later:
echo 1. Run: langflow_venv\Scripts\activate.bat
echo 2. Run: python -m langflow run
echo.
echo To stop Langflow:
echo - Close the Langflow command window
echo - Or run: taskkill /F /FI "WINDOWTITLE eq Langflow*"
echo.
echo Note: We're using Langflow version 1.1.4 which provides a good balance of features and stability.
echo This version should work well for integration with Ollama.
echo.
echo If you encounter any issues:
echo 1. Check the logs in the logs directory
echo 2. Try running this script again to perform a clean installation
echo 3. Make sure no other applications are using port 7860

endlocal