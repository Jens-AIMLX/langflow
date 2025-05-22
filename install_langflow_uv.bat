@echo off
echo Installing Langflow using uv...

REM Step 0: Kill any existing Langflow processes
echo Checking for existing Langflow processes...
taskkill /F /IM "pythonthon.exe" /FI "WINDOWTITLE eq langflow*" > nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Existing Langflow processes terminated.
) else (
    echo No existing Langflow processes found.
)

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

REM Step 4: Create a virtual environment using Python launcher
python -m venv langflow_venv

REM Step 5: Activate the virtual environment
call langflow_venv\Scripts\activate.bat

REM Step 6: Install uv inside the virtual environment
python -m pip install uv

REM Step 7: Install a more recent stable version of Langflow with all dependencies
echo Installing Langflow with all dependencies except excludes...
python -m uv pip install "langflow==1.1.4" --verbose

REM Step 8: Run Langflow
echo Starting Langflow...
echo Running command: python -m langflow run
python -m langflow run

REM Step 9: Health check to verify Langflow is running
echo Performing health check...
timeout /t 5 /nobreak > nul
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://127.0.0.1:7860/health' -TimeoutSec 5; if ($response.StatusCode -eq 200) { Write-Host 'Langflow is running successfully!' -ForegroundColor Green } else { Write-Host 'Langflow may not be running correctly.' -ForegroundColor Yellow } } catch { Write-Host 'Health check failed. Langflow may not be running correctly.' -ForegroundColor Red }"

echo.
echo If Langflow started successfully, you can access it at: http://127.0.0.1:7860/flows
echo.
echo To restart Langflow later:
echo 1. Run: langflow_venv\Scripts\activate.bat
echo 2. Run: python -m langflow run
echo.
echo Note: We're using Langflow version 1.1.4 which provides a good balance of features and stability.
echo This version should work well for integration with Ollama.