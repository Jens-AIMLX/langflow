@echo off
echo Installing Langflow using uv...

REM Step 1: Create a virtual environment using Python launcher
py -m venv langflow_venv

REM Step 2: Activate the virtual environment
call langflow_venv\Scripts\activate.bat

REM Step 3: Install uv inside the virtual environment
py -m pip install uv

REM Step 4: Install Langflow with specific version constraints
echo Installing Langflow...
py -m uv pip install "langflow==0.6.3"

REM Step 5: Run Langflow
echo Starting Langflow...
py -m langflow run

echo.
echo If Langflow started successfully, you can access it at: http://localhost:7860
echo.
echo To restart Langflow later:
echo 1. Run: langflow_venv\Scripts\activate.bat
echo 2. Run: py -m langflow run
echo.
echo Note: We're using Langflow version 0.6.3 which has fewer dependency conflicts.