@echo off
setlocal enabledelayedexpansion

REM ============================================================================
REM Langflow Bootstrap Script using uv
REM Based on: https://upwarddynamism.com/ai-use-cases-prompts/local-ai-agents-ollama-langflow/
REM ============================================================================

REM Create logs directory if it doesn't exist
if not exist logs mkdir logs

echo ================================================================================ > logs\bootstrap.log
echo Langflow Bootstrap started at %TIME% >> logs\bootstrap.log
echo ================================================================================ >> logs\bootstrap.log

REM Define the log_cmd function at the beginning
goto skip_log_cmd_definition

:log_cmd
set cmd=%~1
set logfile=%~2
echo ^>^> Executing: %cmd%
echo. >> %logfile%
echo ^>^> Command: %cmd% >> %logfile%
echo. >> %logfile%

REM Run the command and capture output to a temporary file
%cmd% > temp_output.txt 2>&1

REM Display the output to console
type temp_output.txt

REM Append the output to the log file
type temp_output.txt >> %logfile%

REM Clean up
if exist temp_output.txt del temp_output.txt
exit /b

:skip_log_cmd_definition

REM ============================================================================
REM Step 1: Check Python Installation
REM ============================================================================

REM Use Python launcher by default
set "PY=py"

REM Allow user to specify a different Python command
if "%~1" NEQ "" (
  set "PY=%~1"
)

echo Verifying Python version compatibility...
echo ================================================================================ > logs\python_version.log
echo Python version check started at %TIME% >> logs\python_version.log
echo ================================================================================ >> logs\python_version.log

REM Try the specified Python command first
%PY% -c "import sys; print('Using Python', sys.version); version_info = sys.version_info; exit(0 if (version_info.major==3 and version_info.minor>=10 and version_info.minor<=13) else 1)" > temp_output.txt 2>&1
set PYTHON_CHECK_RESULT=%ERRORLEVEL%
type temp_output.txt
type temp_output.txt >> logs\python_version.log
del temp_output.txt

if %PYTHON_CHECK_RESULT% EQU 0 (
  echo Python version is compatible.
  goto python_found
)

if %PYTHON_CHECK_RESULT% EQU 9009 (
  echo Python command failed: '%PY%'. Trying alternatives...

  REM Try py launcher with version flags if user didn't specify
  if "%~1"=="" (
    for %%V in (3.12 3.11 3.10) do (
      echo Trying py launcher with -%%V...
      py -%%V -c "import sys; print('Using Python', sys.version)" > temp_output.txt 2>&1
      set PY_CHECK_RESULT=!ERRORLEVEL!
      type temp_output.txt
      type temp_output.txt >> logs\python_version.log
      del temp_output.txt
      
      if !PY_CHECK_RESULT! EQU 0 (
        set "PY=py -%%V"
        goto python_found
      )
    )
  )

  echo ERROR: Could not find a working Python installation.
  echo Please install Python 3.10, 3.11, or 3.12 and ensure it's in your PATH.
  exit /b 1
) else (
  echo WARNING: Python version check failed or incompatible version detected.
  echo Please ensure you're using Python 3.10, 3.11, or 3.12.
  echo Continuing anyway, but you may encounter issues...
)

:python_found
echo Found Python: %PY%

REM ============================================================================
REM Step 2: Install uv
REM ============================================================================

echo 📦 Installing uv package manager...
call :log_cmd "%PY% -m pip install uv" logs\uv_install.log

REM ============================================================================
REM Step 3: Create a dedicated folder for Langflow
REM ============================================================================

set "LANGFLOW_DIR=%CD%\langflow_env"
echo 🔧 Creating Langflow environment in %LANGFLOW_DIR%...

if not exist "%LANGFLOW_DIR%" mkdir "%LANGFLOW_DIR%"
cd "%LANGFLOW_DIR%"

REM Create virtual environment using uv
echo 🔧 Creating virtual environment...
call :log_cmd "%PY% -m uv venv .venv" logs\venv_create.log

REM Activate the virtual environment
echo 🔧 Activating virtual environment...
call .venv\Scripts\activate.bat

REM ============================================================================
REM Step 4: Install Langflow
REM ============================================================================

echo 📦 Installing Langflow...
call :log_cmd "%PY% -m uv pip install langflow" logs\langflow_install.log

REM ============================================================================
REM Step 5: Set up module structure
REM ============================================================================

echo 🔧 Setting up module structure...

REM Create a Python script to set up the module structure
echo import os, sys > setup_modules.py
echo from pathlib import Path >> setup_modules.py
echo. >> setup_modules.py
echo def ensure_dir(path): >> setup_modules.py
echo     if not os.path.exists(path): >> setup_modules.py
echo         os.makedirs(path) >> setup_modules.py
echo         print(f"Created directory: {path}") >> setup_modules.py
echo. >> setup_modules.py
echo def write_init(path, content): >> setup_modules.py
echo     if not os.path.exists(path): >> setup_modules.py
echo         with open(path, 'w') as f: >> setup_modules.py
echo             f.write(content) >> setup_modules.py
echo         print(f"Created {path}") >> setup_modules.py
echo     else: >> setup_modules.py
echo         print(f"Using existing {path}") >> setup_modules.py
echo. >> setup_modules.py
echo # Ensure directories exist >> setup_modules.py
echo ensure_dir('src/backend/langflow') >> setup_modules.py
echo ensure_dir('src/backend/langflow/main') >> setup_modules.py
echo. >> setup_modules.py
echo # Backend __init__.py >> setup_modules.py
echo backend_init = '''"""Backend package for Langflow""" >> setup_modules.py
echo. >> setup_modules.py
echo import os >> setup_modules.py
echo import sys >> setup_modules.py
echo. >> setup_modules.py
echo # Ensure base directory is in path >> setup_modules.py
echo base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "base")) >> setup_modules.py
echo if base_path not in sys.path: >> setup_modules.py
echo     sys.path.insert(0, base_path) >> setup_modules.py
echo ''' >> setup_modules.py
echo. >> setup_modules.py
echo # Langflow __init__.py >> setup_modules.py
echo langflow_init = '''# Langflow package wrapper >> setup_modules.py
echo """Wrapper for langflow-base""" >> setup_modules.py
echo import sys >> setup_modules.py
echo import os >> setup_modules.py
echo. >> setup_modules.py
echo # Add base to path for proper imports >> setup_modules.py
echo base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../base")) >> setup_modules.py
echo if base_path not in sys.path: >> setup_modules.py
echo     sys.path.insert(0, base_path) >> setup_modules.py
echo. >> setup_modules.py
echo # Import all from the actual implementation >> setup_modules.py
echo from src.backend.base.langflow import * >> setup_modules.py
echo. >> setup_modules.py
echo # Make __main__ accessible >> setup_modules.py
echo from src.backend.base.langflow.__main__ import run_langflow >> setup_modules.py
echo ''' >> setup_modules.py
echo. >> setup_modules.py
echo # Main __init__.py >> setup_modules.py
echo main_init = '''# Import main module >> setup_modules.py
echo """Import the main module from langflow-base""" >> setup_modules.py
echo. >> setup_modules.py
echo import sys >> setup_modules.py
echo import os >> setup_modules.py
echo. >> setup_modules.py
echo # Add base to path for proper imports >> setup_modules.py
echo base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../base")) >> setup_modules.py
echo if base_path not in sys.path: >> setup_modules.py
echo     sys.path.insert(0, base_path) >> setup_modules.py
echo. >> setup_modules.py
echo # Direct import from the base package >> setup_modules.py
echo from src.backend.base.langflow.main import create_app >> setup_modules.py
echo ''' >> setup_modules.py
echo. >> setup_modules.py
echo # Write the files >> setup_modules.py
echo write_init('src/backend/__init__.py', backend_init) >> setup_modules.py
echo write_init('src/backend/langflow/__init__.py', langflow_init) >> setup_modules.py
echo write_init('src/backend/langflow/main/__init__.py', main_init) >> setup_modules.py
echo. >> setup_modules.py
echo print("Module structure setup complete.") >> setup_modules.py

REM Run the module setup script
call :log_cmd "%PY% setup_modules.py" logs\module_setup.log
del setup_modules.py

REM ============================================================================
REM Step 6: Start Langflow backend
REM ============================================================================

echo 🖥️ Starting Langflow backend...

REM Create a Python script for the backend
echo import sys > run_backend.py
echo import os >> run_backend.py
echo. >> run_backend.py
echo # Set up paths >> run_backend.py
echo base_dir = os.getcwd() >> run_backend.py
echo sys.path.extend([base_dir, >> run_backend.py
echo                  os.path.join(base_dir, 'src'), >> run_backend.py
echo                  os.path.join(base_dir, 'src', 'backend'), >> run_backend.py
echo                  os.path.join(base_dir, 'src', 'backend', 'base')]) >> run_backend.py
echo. >> run_backend.py
echo # Import the run_langflow function >> run_backend.py
echo from langflow.__main__ import run_langflow >> run_backend.py
echo. >> run_backend.py
echo print('Starting LangFlow backend on port 7860...') >> run_backend.py
echo run_langflow('0.0.0.0', 7860, 'debug', {}, None) >> run_backend.py

REM Create a batch file to run the backend
echo @echo off > run_backend.bat
echo echo. > logs\backend.log >> run_backend.bat
echo echo ================================================================================ >> logs\backend.log >> run_backend.bat
echo echo LangFlow Backend started at %%TIME%% >> logs\backend.log >> run_backend.bat
echo echo ================================================================================ >> logs\backend.log >> run_backend.bat
echo set PYTHONPATH=%LANGFLOW_DIR%;%LANGFLOW_DIR%\src;%LANGFLOW_DIR%\src\backend;%LANGFLOW_DIR%\src\backend\base >> run_backend.bat
echo call :log_cmd "%PY% run_backend.py" logs\backend.log >> run_backend.bat
echo goto :eof >> run_backend.bat
echo. >> run_backend.bat
echo :log_cmd >> run_backend.bat
echo set cmd=%%~1 >> run_backend.bat
echo set logfile=%%~2 >> run_backend.bat
echo echo ^>^> Executing: %%cmd%% >> run_backend.bat
echo echo. >> %%logfile%% >> run_backend.bat
echo echo ^>^> Command: %%cmd%% >> %%logfile%% >> run_backend.bat
echo echo. >> %%logfile%% >> run_backend.bat
echo. >> run_backend.bat
echo REM Run the command and capture output to a temporary file >> run_backend.bat
echo %%cmd%% ^> temp_output.txt 2^>^&1 >> run_backend.bat
echo. >> run_backend.bat
echo REM Display the output to console >> run_backend.bat
echo type temp_output.txt >> run_backend.bat
echo. >> run_backend.bat
echo REM Append the output to the log file >> run_backend.bat
echo type temp_output.txt ^>^> %%logfile%% >> run_backend.bat
echo. >> run_backend.bat
echo REM Clean up >> run_backend.bat
echo if exist temp_output.txt del temp_output.txt >> run_backend.bat
echo exit /b >> run_backend.bat

REM Start in new window
start "LangFlow-backend" cmd /c run_backend.bat

REM ============================================================================
REM Step 7: Check for frontend directory
REM ============================================================================

echo 🌐 Checking for frontend...
set "FRONTEND_DIR=docker\frontend"
if not exist %FRONTEND_DIR% (
  echo ❌ Docker frontend directory not found!
  echo Checking if there are any frontend directories...
  dir /s /b frontend 2>nul || echo No frontend directory found
  echo.
  echo Please ensure you're in the correct directory structure.
  echo Current directory: %CD%
  echo Tried looking in: %CD%\%FRONTEND_DIR%
  goto backend_check
) else (
  echo ✅ Found frontend in %FRONTEND_DIR%
)

REM Add a delay to ensure backend is fully started
echo ⏳ Waiting for backend to initialize (5 seconds)...
timeout /t 5 /nobreak > nul

:backend_check
REM Try to verify the backend is running
echo Checking if backend is running...

REM Create a Python script to check backend health
echo import sys > check_backend.py
echo import requests >> check_backend.py
echo import time >> check_backend.py
echo. >> check_backend.py
echo def check_health(url, max_attempts=10, delay=3): >> check_backend.py
echo     print(f"Checking backend health at {url}") >> check_backend.py
echo     for attempt in range(1, max_attempts + 1): >> check_backend.py
echo         try: >> check_backend.py
echo             print(f"Attempt {attempt} of {max_attempts}...") >> check_backend.py
echo             response = requests.get(url, timeout=5) >> check_backend.py
echo             if response.status_code == 200: >> check_backend.py
echo                 print(f"Backend is running! (Status code: {response.status_code})") >> check_backend.py
echo                 return True >> check_backend.py
echo             print(f"Backend not responding correctly (Status code: {response.status_code})") >> check_backend.py
echo         except Exception as e: >> check_backend.py
echo             print(f"Error connecting to backend: {e}") >> check_backend.py
echo         if attempt < max_attempts: >> check_backend.py
echo             print(f"Waiting {delay} seconds before next attempt...") >> check_backend.py
echo             time.sleep(delay) >> check_backend.py
echo     return False >> check_backend.py
echo. >> check_backend.py
echo if __name__ == "__main__": >> check_backend.py
echo     result = check_health("http://localhost:7860/health_check") >> check_backend.py
echo     sys.exit(0 if result else 1) >> check_backend.py

call :log_cmd "%PY% check_backend.py" logs\backend_check.log
set BACKEND_CHECK_RESULT=%ERRORLEVEL%
del check_backend.py

if %BACKEND_CHECK_RESULT% NEQ 0 (
  echo WARNING: Backend may not be running properly.
  echo Looking at recent backend log:
  echo ================================================================================
  if exist logs\backend.log type logs\backend.log
  echo ================================================================================
  echo.
  echo Press any key to continue anyway...
  pause > nul
)

if not exist %FRONTEND_DIR% (
  echo Frontend directory not found. Skipping frontend startup.
  goto end
)

REM Bootstrap & start frontend
echo 🌐 Bootstrapping frontend...

pushd %FRONTEND_DIR%

if not exist node_modules (
  echo 📥 npm install...
  call :log_cmd "npm install" ..\..\logs\frontend.log
  echo npm install completed, log saved to logs\frontend.log
) else (
  echo ⏭️ node_modules already present
)

echo 🚀 npm start...
echo Starting frontend...

REM Create a batch file to run npm start in the frontend directory
echo @echo off > ..\..\run_frontend.bat
echo cd "%CD%" >> ..\..\run_frontend.bat
echo echo. > ..\..\logs\frontend.log >> ..\..\run_frontend.bat
echo echo ================================================================================ >> ..\..\logs\frontend.log >> ..\..\run_frontend.bat
echo echo LangFlow Frontend started at %%TIME%% >> ..\..\logs\frontend.log >> ..\..\run_frontend.bat
echo echo ================================================================================ >> ..\..\logs\frontend.log >> ..\..\run_frontend.bat
echo call :log_cmd "npm start" ..\..\logs\frontend.log >> ..\..\run_frontend.bat
echo goto :eof >> ..\..\run_frontend.bat
echo. >> ..\..\run_frontend.bat
echo :log_cmd >> ..\..\run_frontend.bat
echo set cmd=%%~1 >> ..\..\run_frontend.bat
echo set logfile=%%~2 >> ..\..\run_frontend.bat
echo echo ^>^> Executing: %%cmd%% >> ..\..\run_frontend.bat
echo echo. >> %%logfile%% >> ..\..\run_frontend.bat
echo echo ^>^> Command: %%cmd%% >> %%logfile%% >> ..\..\run_frontend.bat
echo echo. >> %%logfile%% >> ..\..\run_frontend.bat
echo. >> ..\..\run_frontend.bat
echo REM Run the command and capture output to a temporary file >> ..\..\run_frontend.bat
echo %%cmd%% ^> temp_output.txt 2^>^&1 >> ..\..\run_frontend.bat
echo. >> ..\..\run_frontend.bat
echo REM Display the output to console >> ..\..\run_frontend.bat
echo type temp_output.txt >> ..\..\run_frontend.bat
echo. >> ..\..\run_frontend.bat
echo REM Append the output to the log file >> ..\..\run_frontend.bat
echo type temp_output.txt ^>^> %%logfile%% >> ..\..\run_frontend.bat
echo. >> ..\..\run_frontend.bat
echo REM Clean up >> ..\..\run_frontend.bat
echo if exist temp_output.txt del temp_output.txt >> ..\..\run_frontend.bat
echo exit /b >> ..\..\run_frontend.bat

start "LangFlow-frontend" cmd /c ..\..\run_frontend.bat

popd

:end
echo.
echo ✅ All done!
echo    • Backend → http://localhost:7860
if exist %FRONTEND_DIR% echo    • Frontend → http://localhost:3000
echo.
echo Check the log files for details:
echo   - logs\backend.log: Backend server logs
echo   - logs\langflow_install.log: Langflow installation logs
if exist %FRONTEND_DIR% echo   - logs\frontend.log: Frontend logs

REM Clean up temporary batch files
if exist run_backend.bat del run_backend.bat

echo.
echo 📝 To restart Langflow later:
echo   1. Navigate to %LANGFLOW_DIR%
echo   2. Run: .venv\Scripts\activate.bat
echo   3. Run: python -m langflow run

endlocal