@echo off
echo Installing Langflow using uv...

REM Step 1: Create a virtual environment using Python launcher
py -m venv langflow_venv

REM Step 2: Activate the virtual environment
call langflow_venv\Scripts\activate.bat

REM Step 3: Install uv inside the virtual environment
py -m pip install uv

REM Step 4: Install Langflow using uv
echo Installing Langflow with uv (this may take some time)...
py -m uv pip install langflow

REM Step 5: Run Langflow
echo Starting Langflow...
py -m langflow run

echo.
echo If Langflow started successfully, you can access it at: http://localhost:7860
echo.
echo To restart Langflow later:
echo 1. Run: langflow_venv\Scripts\activate.bat
echo 2. Run: py -m langflow run