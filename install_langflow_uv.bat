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

REM Step 2: Create a virtual environment using Python launcher
py -m venv langflow_venv

REM Step 3: Activate the virtual environment
call langflow_venv\Scripts\activate.bat

REM Step 4: Install uv inside the virtual environment
py -m pip install uv

REM Step 5: Install Langflow with specific version constraints and skip problematic dependencies
echo Installing Langflow...
py -m uv pip install "langflow==0.0.78" --no-deps

REM Step 6: Install dependencies manually, excluding problematic ones
echo Installing dependencies...
py -m uv pip install "langchain<0.0.267" "fastapi>=0.95.2,<0.100.0" "uvicorn>=0.22.0,<0.23.0" "beautifulsoup4>=4.12.2,<4.13.0" "typer>=0.9.0,<0.10.0" "pypdf>=3.15.1,<3.16.0" "lxml>=4.9.3,<4.10.0" "pydantic>=1.10.8,<2.0.0" "python-multipart>=0.0.6,<0.0.7" "sqlmodel>=0.0.8,<0.0.9" "orjson>=3.9.2,<3.10.0" "rich>=13.4.2,<13.5.0" "openai>=0.27.8,<0.28.0" "jinja2>=3.1.2,<3.2.0" "aiohttp>=3.8.5,<3.9.0" "typing-inspect>=0.9.0,<0.10.0" "packaging>=23.1,<23.2" "pandas>=2.0.3,<2.1.0" "fastapi-socketio>=0.0.10,<0.1.0" "httpx>=0.24.1,<0.25.0" "pillow>=10.0.0,<10.1.0" "watchdog>=3.0.0,<3.1.0" "tiktoken>=0.4.0,<0.5.0" "loguru>=0.7.0,<0.8.0" "passlib>=1.7.4,<1.8.0" "python-jose>=3.3.0,<3.4.0" "bcrypt>=4.0.1,<4.1.0"

REM Step 7: Run Langflow
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