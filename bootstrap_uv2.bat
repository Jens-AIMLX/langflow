@echo off
setlocal

REM ============================================================================
REM Langflow Bootstrap Script using uv with Python Launcher
REM Based on: https://upwarddynamism.com/ai-use-cases-prompts/local-ai-agents-ollama-langflow/
REM ============================================================================

echo Langflow Bootstrap Script
echo Based on: https://upwarddynamism.com/ai-use-cases-prompts/local-ai-agents-ollama-langflow/
echo.

REM Step 1: Install uv if not already installed
echo Step 1: Installing uv package manager...
py -m pip install uv
echo.

REM Step 2: Create a dedicated folder for Langflow
echo Step 2: Creating a dedicated folder for Langflow...
if not exist "Langflow" mkdir Langflow
cd Langflow
echo Created and moved to Langflow folder: %CD%
echo.

REM Step 3: Create the virtual environment
echo Step 3: Creating virtual environment...
py -m uv venv .venv
echo.

REM Step 4: Activate the virtual environment
echo Step 4: Activating virtual environment...
call .venv\Scripts\activate.bat
echo.

REM Step 5: Install Langflow using uv
echo Step 5: Installing Langflow using uv...
echo This may take some time...
py -m uv pip install langflow
echo.

REM Step 6: Run Langflow
echo Step 6: Running Langflow...
py -m langflow run
echo.

REM This part will only execute if the user manually stops Langflow
echo.
echo To restart Langflow later:
echo 1. Navigate to this folder: %CD%
echo 2. Run: .venv\Scripts\activate.bat
echo 3. Run: py -m langflow run
echo.

endlocal
