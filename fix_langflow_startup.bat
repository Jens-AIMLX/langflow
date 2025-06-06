@echo off
echo ========================================
echo Fixing Langflow Startup Issues
echo ========================================
echo.

REM Activate the virtual environment
echo Activating Langflow virtual environment...
call langflow_venv\Scripts\activate.bat

REM Clear any problematic environment variables
echo Clearing problematic environment variables...
set LANGFLOW_LOG_LEVEL=
set UVICORN_LOG_LEVEL=
set LOG_LEVEL=

REM Remove any .env file that might have bad configuration
if exist ".env" (
    echo Backing up existing .env file...
    copy .env .env.backup >nul 2>&1
    echo Removing problematic .env file...
    del .env >nul 2>&1
)

REM Create a clean .env file
echo Creating clean .env configuration...
echo # Langflow Configuration > .env
echo LANGFLOW_LOG_LEVEL=info >> .env
echo LANGFLOW_HOST=127.0.0.1 >> .env
echo LANGFLOW_PORT=7860 >> .env
echo LANGFLOW_CUSTOM_COMPONENTS_PATH=custom_nodes >> .env
echo LANGFLOW_LOAD_CUSTOM_COMPONENTS=true >> .env
echo. >> .env
echo # Enhanced Filename Features >> .env
echo LANGFLOW_ENHANCED_FILENAME_ENABLED=true >> .env

echo ✅ Clean configuration created

REM Check Python and Langflow installation
echo.
echo Checking Langflow installation...
python -c "import langflow; print('Langflow version:', langflow.__version__)" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Langflow import failed
    echo Reinstalling Langflow...
    python -m pip install --upgrade langflow==1.4.0
) else (
    echo ✅ Langflow is properly installed
)

REM Try to start Langflow with explicit parameters
echo.
echo Starting Langflow with clean configuration...
echo.
echo ========================================
echo Langflow Starting...
echo ========================================
echo.
echo If Langflow starts successfully, you should see:
echo   - "Open Langflow → http://127.0.0.1:7860"
echo   - No error messages
echo.
echo Look for these components in the UI:
echo   - "Backward Compatible File Metadata Extractor"
echo   - "File Metadata Extractor"
echo.

REM Start Langflow with explicit clean parameters
python -m langflow run --host 127.0.0.1 --port 7860 --log-level info --components-path custom_nodes

echo.
echo ========================================
echo Langflow Startup Attempt Complete
echo ========================================
echo.
echo If Langflow failed to start, try these alternatives:
echo.
echo 1. Simple start (no custom components):
echo    python -m langflow run
echo.
echo 2. Different port:
echo    python -m langflow run --port 7861
echo.
echo 3. Debug mode:
echo    python -m langflow run --log-level debug
echo.
echo 4. Reset everything:
echo    reset_langflow_environment.bat
echo.
pause
