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

REM Step 2: Add the i686-pc-windows-msvc target for Rust
echo Adding required Rust target (i686-pc-windows-msvc)...
rustup target add i686-pc-windows-msvc

REM Step 3: Create a virtual environment using Python launcher
py -m venv langflow_venv

REM Step 4: Activate the virtual environment
call langflow_venv\Scripts\activate.bat

REM Step 5: Install uv inside the virtual environment
py -m pip install uv

REM Step 6: Install pandas first (required by Langflow)
echo Installing pandas...
py -m uv pip install "pandas<2.0.0,>=1.5.3"

REM Step 7: Install Langflow with specific version constraints and skip problematic dependencies
echo Installing Langflow...
py -m uv pip install "langflow==0.0.78" --no-deps

REM Step 8: Install dependencies manually, excluding problematic ones
echo Installing dependencies...
py -m uv pip install "langchain<0.0.177,>=0.0.176" "fastapi<0.93.0,>=0.92.0" "uvicorn<0.21.0,>=0.20.0" "beautifulsoup4<5.0.0,>=4.11.2" "typer<0.8.0,>=0.7.0" "pypdf<4.0.0,>=3.7.1" "lxml<5.0.0,>=4.9.2" "pydantic>=1.10.8,<2.0.0" "python-multipart>=0.0.6,<0.0.7" "sqlmodel>=0.0.8,<0.0.9" "orjson>=3.9.2,<3.10.0" "rich<14.0.0,>=13.3.3" "openai<0.28.0,>=0.27.2" "jinja2>=3.1.2,<3.2.0" "aiohttp>=3.8.5,<3.9.0" "typing-inspect>=0.9.0,<0.10.0" "packaging>=23.1,<23.2" "dill<0.4.0,>=0.3.6" "docstring-parser<0.16,>=0.15" "networkx<4.0,>=3.1" "websockets<12.0.0,>=11.0.2" "wikipedia<2.0.0,>=1.4.0"

REM Step 9: Try to install tiktoken with uv
echo Attempting to install tiktoken...
py -m uv pip install "tiktoken==0.3.3" --no-build

REM Step 10: Run Langflow
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