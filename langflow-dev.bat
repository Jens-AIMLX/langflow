@echo off
setlocal enabledelayedexpansion

:: Langflow Development Script for Windows
:: This script provides an all-in-one solution for Langflow development
:: Author: Jens-AIMLX

echo.
echo ===================================================
echo    LANGFLOW DEVELOPMENT ENVIRONMENT - WINDOWS
echo ===================================================
echo.

:: Check for required tools
echo Checking for required tools...
where uv >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] uv is not installed or not in PATH.
    echo Please install uv: https://docs.astral.sh/uv/getting-started/installation/
    exit /b 1
)

where npm >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] npm is not installed or not in PATH.
    echo Please install Node.js: https://nodejs.org/en/download/package-manager
    exit /b 1
)

where git >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] git is not installed or not in PATH.
    echo Please install Git: https://git-scm.com/downloads
    exit /b 1
)

echo [OK] All required tools are installed.
echo.

:: Parse command line arguments
set "init_only=false"
set "dev_mode=false"
set "clean=false"
set "help=false"
set "port=7860"
set "host=0.0.0.0"
set "env_file=.env"
set "workers=1"

:parse_args
if "%~1"=="" goto end_parse_args
if /i "%~1"=="--init-only" set "init_only=true" & goto next_arg
if /i "%~1"=="--dev" set "dev_mode=true" & goto next_arg
if /i "%~1"=="--clean" set "clean=true" & goto next_arg
if /i "%~1"=="--help" set "help=true" & goto next_arg
if /i "%~1"=="--port" set "port=%~2" & shift & goto next_arg
if /i "%~1"=="--host" set "host=%~2" & shift & goto next_arg
if /i "%~1"=="--env-file" set "env_file=%~2" & shift & goto next_arg
if /i "%~1"=="--workers" set "workers=%~2" & shift & goto next_arg
echo [WARNING] Unknown argument: %~1
:next_arg
shift
goto parse_args
:end_parse_args

:: Display help if requested
if "%help%"=="true" (
    echo Usage: langflow-dev.bat [options]
    echo.
    echo Options:
    echo   --init-only       Initialize the environment without starting servers
    echo   --dev             Start in development mode with hot-reloading
    echo   --clean           Clean caches before initializing
    echo   --port PORT       Set the backend port (default: 7860)
    echo   --host HOST       Set the backend host (default: 0.0.0.0)
    echo   --env-file FILE   Specify the environment file (default: .env)
    echo   --workers NUM     Number of backend workers (default: 1)
    echo   --help            Display this help message
    echo.
    exit /b 0
)

:: Clean caches if requested
if "%clean%"=="true" (
    echo Cleaning Python cache...
    for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
    del /s /q *.pyc *.pyo *.pyd >nul 2>&1
    if exist .mypy_cache rd /s /q .mypy_cache
    echo [OK] Python cache cleaned.
    
    echo Cleaning npm cache...
    cd src\frontend
    call npm cache clean --force
    if exist node_modules rd /s /q node_modules
    if exist build rd /s /q build
    if exist package-lock.json del /q package-lock.json
    cd ..\..
    if exist src\backend\base\langflow\frontend rd /s /q src\backend\base\langflow\frontend
    echo [OK] NPM cache and frontend directories cleaned.
    echo.
)

:: Create .env file if it doesn't exist
if not exist "%env_file%" (
    echo Creating %env_file% file...
    type nul > "%env_file%"
    echo [OK] Created %env_file% file.
    echo.
)

:: Initialize the environment
echo ===================================================
echo    INITIALIZING LANGFLOW DEVELOPMENT ENVIRONMENT
echo ===================================================
echo.

echo Installing backend dependencies...
call uv sync --frozen --extra "postgresql"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install backend dependencies.
    exit /b 1
)
echo [OK] Backend dependencies installed.
echo.

echo Installing frontend dependencies...
cd src\frontend
call npm install
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install frontend dependencies.
    cd ..\..
    exit /b 1
)
cd ..\..
echo [OK] Frontend dependencies installed.
echo.

echo Building frontend static files...
cd src\frontend
call npm run build
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to build frontend.
    cd ..\..
    exit /b 1
)
cd ..\..
echo [OK] Frontend built successfully.
echo.

:: Clear destination directory
if exist src\backend\base\langflow\frontend (
    rd /s /q src\backend\base\langflow\frontend
)
mkdir src\backend\base\langflow\frontend 2>nul

:: Copy build files
echo Copying build files to backend...
xcopy /E /I /Y src\frontend\build\* src\backend\base\langflow\frontend\
echo [OK] Frontend files copied to backend.
echo.

echo ===================================================
echo    INITIALIZATION COMPLETE
echo ===================================================
echo.

:: Exit if init-only mode
if "%init_only%"=="true" (
    echo Initialization completed successfully.
    echo Run 'langflow-dev.bat --dev' to start development servers.
    exit /b 0
)

:: Start development servers if in dev mode
if "%dev_mode%"=="true" (
    echo ===================================================
    echo    STARTING DEVELOPMENT SERVERS
    echo ===================================================
    echo.
    echo Starting backend and frontend servers in development mode...
    echo.
    echo Backend will be available at: http://%host%:%port%
    echo Frontend will be available at: http://localhost:3100
    echo.
    echo Press Ctrl+C in each terminal to stop the servers.
    echo.
    
    :: Start backend in a new terminal
    start cmd /k "title Langflow Backend && echo Starting Langflow Backend... && call uv run uvicorn --factory langflow.main:create_app --host %host% --port %port% --reload --env-file %env_file% --loop asyncio --workers %workers%"
    
    :: Start frontend in a new terminal
    start cmd /k "title Langflow Frontend && echo Starting Langflow Frontend... && cd src\frontend && npm start"
    
    echo [OK] Development servers started in separate terminals.
    echo.
    
    :: Wait for servers to start
    echo Waiting for servers to start...
    timeout /t 5 /nobreak >nul
    
    :: Open browser
    echo Opening browser...
    start http://localhost:3100
    
    echo ===================================================
    echo    DEVELOPMENT ENVIRONMENT RUNNING
    echo ===================================================
    echo.
    echo Backend: http://%host%:%port%
    echo Frontend: http://localhost:3100
    echo.
    echo Check the terminal windows for server logs.
    echo.
    
) else (
    :: Start the application in normal mode
    echo ===================================================
    echo    STARTING LANGFLOW APPLICATION
    echo ===================================================
    echo.
    echo Starting Langflow application...
    echo.
    echo Langflow will be available at: http://%host%:%port%
    echo.
    echo Press Ctrl+C to stop the server.
    echo.
    
    call uv run langflow run --frontend-path src\backend\base\langflow\frontend --log-level debug --host %host% --port %port% --env-file %env_file%
    
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to start Langflow application.
        exit /b 1
    )
)

endlocal
