@echo off
echo ========================================
echo Resetting Langflow Environment
echo ========================================
echo.

echo This will:
echo - Clear all environment variables
echo - Remove configuration files
echo - Reset Langflow to default state
echo - Preserve custom components
echo.
set /p confirm="Continue? (y/n): "
if /i not "%confirm%"=="y" (
    echo Operation cancelled.
    pause
    exit /b 0
)

REM Kill any running Langflow processes
echo.
echo Stopping any running Langflow processes...
taskkill /F /IM "python.exe" /FI "WINDOWTITLE eq *langflow*" >nul 2>&1
taskkill /F /IM "uvicorn.exe" >nul 2>&1

REM Activate virtual environment
echo Activating virtual environment...
call langflow_venv\Scripts\activate.bat

REM Clear environment variables
echo Clearing environment variables...
set LANGFLOW_LOG_LEVEL=
set LANGFLOW_HOST=
set LANGFLOW_PORT=
set LANGFLOW_CUSTOM_COMPONENTS_PATH=
set LANGFLOW_LOAD_CUSTOM_COMPONENTS=
set LANGFLOW_ENHANCED_FILENAME_ENABLED=
set UVICORN_LOG_LEVEL=
set LOG_LEVEL=
set PYTHONPATH=

REM Backup and remove configuration files
echo Backing up configuration files...
if exist ".env" (
    copy .env .env.backup.%date:~-4,4%%date:~-10,2%%date:~-7,2% >nul 2>&1
    del .env >nul 2>&1
    echo ✅ Removed .env file
)

if exist "langflow.db" (
    copy langflow.db langflow.db.backup.%date:~-4,4%%date:~-10,2%%date:~-7,2% >nul 2>&1
    echo ✅ Backed up langflow.db
)

REM Clear Python cache
echo Clearing Python cache...
if exist "__pycache__" (
    rmdir /s /q "__pycache__" >nul 2>&1
)
if exist "custom_nodes\__pycache__" (
    rmdir /s /q "custom_nodes\__pycache__" >nul 2>&1
)

REM Reinstall Langflow to ensure clean state
echo.
echo Reinstalling Langflow for clean state...
python -m pip uninstall -y langflow langflow-base >nul 2>&1
python -m pip install langflow==1.4.0

REM Verify installation
echo.
echo Verifying Langflow installation...
python -c "import langflow; print('✅ Langflow version:', langflow.__version__)" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Langflow installation failed
    echo Please run install_langflow_uv_140.bat to reinstall
    pause
    exit /b 1
)

REM Create minimal clean configuration
echo.
echo Creating minimal clean configuration...
echo # Minimal Langflow Configuration > .env
echo LANGFLOW_HOST=127.0.0.1 >> .env
echo LANGFLOW_PORT=7860 >> .env

echo ✅ Environment reset complete

echo.
echo ========================================
echo Environment Reset Complete
echo ========================================
echo.
echo ✅ Langflow reinstalled cleanly
echo ✅ Configuration files reset
echo ✅ Environment variables cleared
echo ✅ Python cache cleared
echo ✅ Custom components preserved
echo.
echo Next steps:
echo.
echo 1. Test basic Langflow startup:
echo    python -m langflow run
echo.
echo 2. If that works, add custom components:
echo    python -m langflow run --components-path custom_nodes
echo.
echo 3. If issues persist, check:
echo    - Python version compatibility
echo    - Virtual environment activation
echo    - Port availability (7860)
echo.
pause
