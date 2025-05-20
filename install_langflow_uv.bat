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

REM Step 7: Install pandas using uv (required by Langflow)
echo Installing pandas using uv...
py -m uv pip install "pandas==1.5.3"

REM Step 8: Install Langflow with specific version constraints and skip problematic dependencies
echo Installing Langflow...
py -m uv pip install "langflow==0.0.78" --no-deps --verbose

REM Step 9: Install dependencies manually, excluding problematic ones
echo Installing dependencies...
py -m uv pip install "langchain<0.0.177,>=0.0.176" "fastapi<0.93.0,>=0.92.0" "uvicorn<0.21.0,>=0.20.0" "beautifulsoup4<5.0.0,>=4.11.2" "typer<0.8.0,>=0.7.0" "pypdf<4.0.0,>=3.7.1" "lxml<5.0.0,>=4.9.2" "pydantic>=1.10.8,<2.0.0" "python-multipart>=0.0.6,<0.0.7" "sqlmodel>=0.0.8,<0.0.9" "orjson>=3.9.2,<3.10.0" "rich<14.0.0,>=13.3.3" "openai<0.28.0,>=0.27.2" "jinja2>=3.1.2,<3.2.0" "typing-inspect>=0.9.0,<0.10.0" "packaging>=23.1,<23.2" "dill<0.4.0,>=0.3.6" "docstring-parser<0.16,>=0.15" "networkx<4.0,>=3.1" "websockets<12.0.0,>=11.0.2" "wikipedia<2.0.0,>=1.4.0" "pillow<10.0.0,>=9.0.0" --verbose

REM Step 10: Skip tiktoken installation - it's not essential for basic Ollama integration
echo Skipping tiktoken installation due to architecture compatibility issues...
echo Note: Some advanced text tokenization features may not be available.

REM Step 11: Try to install aiohttp with uv
echo Attempting to install aiohttp...
py -m uv pip install "aiohttp<4.0.0,>=3.8.0"

REM Step 12: Run Langflow
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