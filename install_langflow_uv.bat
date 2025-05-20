@echo off
echo Installing Langflow using uv...

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
py -m venv langflow_venv

REM Step 5: Activate the virtual environment
call langflow_venv\Scripts\activate.bat

REM Step 6: Install uv inside the virtual environment
py -m pip install uv

REM Step 7: Install an older version of Langflow with all dependencies
echo Installing Langflow with all dependencies...
py -m uv pip install "langflow==0.0.78" --exclude tiktoken

REM Step 8: Run Langflow
echo Starting Langflow...
py -m langflow run

echo.
echo If Langflow started successfully, you can access it at: http://localhost:7860
echo.
echo To restart Langflow later:
echo 1. Run: langflow_venv\Scripts\activate.bat
echo 2. Run: py -m langflow run
echo.
echo Note: We're using an older version of Langflow and skipping problematic dependencies.
echo Some features might be limited, but it should work for basic integration with Ollama.