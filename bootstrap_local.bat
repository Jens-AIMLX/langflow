@echo off
setlocal

REM Use a simple approach to find Python, trying multiple methods
set "PY=python"

if "%~1" NEQ "" (
  set "PY=%~1"
)

REM Ensure we're using a compatible Python version (not 3.13)
echo Verifying Python version compatibility...
%PY% -c "import sys; print('Using Python', sys.version); version_info = sys.version_info; exit(1 if version_info.major==3 and version_info.minor>=13 else 0)" > python_version.log 2>&1

if errorlevel 9009 (
  echo Python command failed: '%PY%'. Trying alternatives...

  REM Try py launcher with version flag if user didn't specify
  if "%~1"=="" (
    echo Trying py launcher with -3.12...
    py -3.12 -c "import sys; print('Using Python', sys.version)" > python_version.log 2>&1
    if not errorlevel 1 (
      set "PY=py -3.12"
      goto python_found
    )

    echo Trying py launcher with -3.11...
    py -3.11 -c "import sys; print('Using Python', sys.version)" > python_version.log 2>&1
    if not errorlevel 1 (
      set "PY=py -3.11"
      goto python_found
    )
  )

  REM Try with python3 command
  echo Trying python3...
  python3 -c "import sys; print('Using Python', sys.version)" > python_version.log 2>&1
  if not errorlevel 1 (
    set "PY=python3"
    goto python_found
  )

  REM Check common Python locations
  if exist "C:\Python312\python.exe" (
    echo Found Python at C:\Python312\python.exe
    set "PY=C:\Python312\python.exe"
    goto python_found
  )

  if exist "C:\Python311\python.exe" (
    echo Found Python at C:\Python311\python.exe
    set "PY=C:\Python311\python.exe"
    goto python_found
  )

  echo ERROR: Could not find a working Python installation.
  echo Please install Python 3.11 or 3.12 and ensure it's in your PATH.
  exit /b 1
)

:python_found
echo Found Python: %PY%

REM Check Python version for 3.13 compatibility
%PY% -c "import sys; version_info = sys.version_info; exit(1 if version_info.major==3 and version_info.minor>=13 else 0)" > nul 2>&1
if errorlevel 1 (
  echo ERROR: Python 3.13+ detected, but this project requires Python ^<3.13
  echo Please use Python 3.11 or 3.12
  exit /b 1
)

REM 1) Make sure we're on the right branch
echo 🔄  Checking out main
git fetch && git checkout main && git pull

REM 2) Create venv if needed
if not exist .venv (
  echo 🛠️  Creating venv with %PY%...
  %PY% -m venv .venv
) else (
  echo ♻️  Re-using .venv
)

REM 3) Activate it
echo 🚀  Activating venv...
call .venv\Scripts\activate.bat

REM 4) Core tooling
echo ⬆️  Upgrading pip, setuptools, wheel...
pip install --upgrade pip setuptools wheel

echo 📦 Installing Poetry...
pip install poetry

REM 5) Update pyproject.toml to resolve dependency conflicts
echo Updating pyproject.toml to resolve dependency conflicts...

REM Create a Python script to update the pyproject.toml file
echo import re > update_project.py
echo with open('pyproject.toml', 'r') as f: >> update_project.py
echo     content = f.read() >> update_project.py
echo # Update chromadb version to be compatible with crewai >> update_project.py
echo content = re.sub(r'"chromadb==0.5.23",', '"chromadb>=0.5.23",', content) >> update_project.py
echo # Remove crewai that conflicts with chromadb >> update_project.py
echo content = re.sub(r'"crewai==0.102.0",', '"# crewai==0.102.0 # Temporarily disabled due to chromadb conflict",', content) >> update_project.py
echo # Update Python version constraint to be more permissive >> update_project.py
echo content = re.sub(r'requires-python = ">=3.10,<3.13"', 'requires-python = ">=3.10,<3.14"', content) >> update_project.py
echo with open('pyproject.toml', 'w') as f: >> update_project.py
echo     f.write(content) >> update_project.py
echo print("Pyproject.toml updated successfully") >> update_project.py

%PY% update_project.py
if errorlevel 1 (
    echo Failed to update pyproject.toml
) else (
    echo Successfully updated pyproject.toml
)

REM 5) Install backend with Poetry
echo 🔨 Running Poetry install with logging...
echo. > poetry_debug.log
echo ---------------------------------------------------------------------------------- >> poetry_debug.log
echo Poetry installation started at %TIME% >> poetry_debug.log
echo ---------------------------------------------------------------------------------- >> poetry_debug.log

REM Log Poetry environment info
echo [DEBUG] Checking Poetry environment info: >> poetry_debug.log
poetry env info >> poetry_debug.log 2>&1

echo [DEBUG] Setting up local repository for langflow-base... >> poetry_debug.log
poetry config repositories.local %CD%\src\backend\base >> poetry_debug.log 2>&1
poetry config http-basic.local "none" "none" >> poetry_debug.log 2>&1

REM Run Poetry install with both console and logfile output
echo Starting Poetry install - this may take a few minutes...
echo ---------------------------------------------------------------------------------- >> poetry_debug.log
echo POETRY INSTALL OUTPUT: >> poetry_debug.log
echo ---------------------------------------------------------------------------------- >> poetry_debug.log
rem call :log_cmd "poetry install -vv" poetry_debug.log
poetry debug resolve
poetry install

echo ---------------------------------------------------------------------------------- >> poetry_debug.log
echo Poetry installation completed at %TIME% >> poetry_debug.log
echo ---------------------------------------------------------------------------------- >> poetry_debug.log

REM 6) Set up langflow module structure for proper imports
echo [DEBUG] Setting up __init__.py files to ensure proper module structure...
echo [DEBUG] Setting up __init__.py files... >> poetry_debug.log

REM Create backend/__init__.py
if not exist src\backend\__init__.py (
  echo """Backend package for Langflow""" > src\backend\__init__.py
  echo. >> src\backend\__init__.py
  echo import os >> src\backend\__init__.py
  echo import sys >> src\backend\__init__.py
  echo. >> src\backend\__init__.py
  echo # Ensure base directory is in path >> src\backend\__init__.py
  echo base_path = os.path.abspath^(os.path.join^(os.path.dirname^(__file__^), "base"^)^) >> src\backend\__init__.py
  echo if base_path not in sys.path: >> src\backend\__init__.py
  echo     sys.path.insert^(0, base_path^) >> src\backend\__init__.py
  echo Created src\backend\__init__.py
) else (
  echo Using existing src\backend\__init__.py
)

if not exist src\backend\langflow mkdir src\backend\langflow
if not exist src\backend\langflow\__init__.py (
  echo # Langflow package wrapper > src\backend\langflow\__init__.py
  echo """Wrapper for langflow-base""" >> src\backend\langflow\__init__.py
  echo import sys >> src\backend\langflow\__init__.py
  echo import os >> src\backend\langflow\__init__.py
  echo. >> src\backend\langflow\__init__.py
  echo # Add base to path for proper imports >> src\backend\langflow\__init__.py
  echo base_path = os.path.abspath^(os.path.join^(os.path.dirname^(__file__^), "../base"^)^) >> src\backend\langflow\__init__.py
  echo if base_path not in sys.path: >> src\backend\langflow\__init__.py
  echo     sys.path.insert^(0, base_path^) >> src\backend\langflow\__init__.py
  echo. >> src\backend\langflow\__init__.py
  echo # Import all from the actual implementation >> src\backend\langflow\__init__.py
  echo from src.backend.base.langflow import * >> src\backend\langflow\__init__.py
  echo. >> src\backend\langflow\__init__.py
  echo # Make __main__ accessible >> src\backend\langflow\__init__.py
  echo from src.backend.base.langflow.__main__ import run_langflow >> src\backend\langflow\__init__.py
  echo Created src\backend\langflow\__init__.py
) else (
  echo Using existing src\backend\langflow\__init__.py
)

if not exist src\backend\langflow\main mkdir src\backend\langflow\main
if not exist src\backend\langflow\main\__init__.py (
  echo # Import main module > src\backend\langflow\main\__init__.py
  echo """Import the main module from langflow-base""" >> src\backend\langflow\main\__init__.py
  echo. >> src\backend\langflow\main\__init__.py
  echo import sys >> src\backend\langflow\main\__init__.py
  echo import os >> src\backend\langflow\main\__init__.py
  echo. >> src\backend\langflow\main\__init__.py
  echo # Add base to path for proper imports >> src\backend\langflow\main\__init__.py
  echo base_path = os.path.abspath^(os.path.join^(os.path.dirname^(__file__^), "../../base"^)^) >> src\backend\langflow\main\__init__.py
  echo if base_path not in sys.path: >> src\backend\langflow\main\__init__.py
  echo     sys.path.insert^(0, base_path^) >> src\backend\langflow\main\__init__.py
  echo. >> src\backend\langflow\main\__init__.py
  echo # Direct import from the base package >> src\backend\langflow\main\__init__.py
  echo from src.backend.base.langflow.main import create_app >> src\backend\langflow\main\__init__.py
  echo Created src\backend\langflow\main\__init__.py
) else (
  echo Using existing src\backend\langflow\main\__init__.py
)

REM Verify import setup
echo [DEBUG] Verifying if langflow is importable...
echo ---------------------------------------------------------------------------------- > import_check.log
echo PYTHON IMPORT CHECK: >> import_check.log
echo ---------------------------------------------------------------------------------- >> import_check.log

REM Create a Python script for the import check
echo import sys > check_import.py
echo print('PYTHONPATH:', sys.path) >> check_import.py
echo sys.path.extend([r'%CD%', r'%CD%\src', r'%CD%\src\backend', r'%CD%\src\backend\base']) >> check_import.py
echo from importlib import util >> check_import.py
echo print('Can import langflow: ', util.find_spec('langflow') is not None) >> check_import.py
echo spec=util.find_spec('langflow') >> check_import.py
echo print('Found at:', spec.origin if spec else 'Not found') >> check_import.py

call :log_cmd "%PY% check_import.py" import_check.log
del check_import.py

REM 6) Start backend with output to both console and log
echo 🖥️  Starting LangFlow backend...
echo Starting backend with path setup for proper imports...

REM Create log directory if it doesn't exist
if not exist logs mkdir logs

REM Create a proper Python script for the backend
echo import sys > run_backend.py
echo import os >> run_backend.py
echo sys.path.extend([r'%CD%', r'%CD%\src', r'%CD%\src\backend', r'%CD%\src\backend\base']) >> run_backend.py
echo from src.backend.base.langflow.__main__ import run_langflow >> run_backend.py
echo print('Starting LangFlow backend on port 7860...') >> run_backend.py
echo run_langflow('0.0.0.0', 7860, 'debug', {}, None) >> run_backend.py

REM Create a batch file to run the backend
echo @echo off > run_backend.bat
echo echo. > backend.log >> run_backend.bat
echo echo ---------------------------------------------------------------------------------- >> backend.log >> run_backend.bat
echo echo LangFlow Backend started at %TIME% >> backend.log >> run_backend.bat
echo echo ---------------------------------------------------------------------------------- >> backend.log >> run_backend.bat
echo set PYTHONPATH=%CD%;%CD%\src;%CD%\src\backend;%CD%\src\backend\base >> run_backend.bat
echo call :log_cmd "%PY% run_backend.py" backend.log >> run_backend.bat
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

REM 7) Check for frontend directory
echo 🌐  Checking for frontend...
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

REM Bootstrap & start frontend
echo 🌐  Bootstrapping frontend...

REM Add a delay to ensure backend is fully started
echo ⏳  Waiting for backend to initialize (10 seconds)...
timeout /t 10 /nobreak > nul

:backend_check
REM Try to verify the backend is running
echo Checking if backend is running...
set /a max_attempts=10
set /a attempt=1
set backend_running=0

:check_backend_loop
if %attempt% gtr %max_attempts% goto :check_backend_done
echo Attempt %attempt% of %max_attempts%...
curl -s -o nul -w "%%{http_code}" http://localhost:7860/health_check > temp.txt 2>nul
set /p status_code=<temp.txt
del temp.txt
if "%status_code%"=="200" (
  echo Backend is running! (Status code: %status_code%)
  set backend_running=1
  goto :check_backend_done
)
echo Backend not responding yet (Status code: %status_code%)
set /a attempt+=1
timeout /t 3 /nobreak > nul
goto :check_backend_loop

:check_backend_done
if %backend_running%==0 (
  echo WARNING: Backend may not be running properly.
  echo Looking at recent backend log:
  echo ----------------------------------------------------------------------------------
  type backend.log
  echo ----------------------------------------------------------------------------------
  echo.
  echo Press any key to continue anyway...
  pause > nul
)

if not exist %FRONTEND_DIR% (
  echo Frontend directory not found. Skipping frontend startup.
  goto end
)

pushd %FRONTEND_DIR%

if not exist node_modules (
  echo 📥  npm install...
  call :log_cmd "npm install" ..\..\frontend.log
  echo npm install completed, log saved to frontend.log
) else (
  echo ⏭️  node_modules already present
)

echo 🚀  npm start...
echo Starting frontend...
REM Create a batch file to run npm start in the frontend directory
echo @echo off > ..\..\run_frontend.bat
echo cd "%CD%" >> ..\..\run_frontend.bat
echo echo. > ..\..\frontend.log >> ..\..\run_frontend.bat
echo echo ---------------------------------------------------------------------------------- >> ..\..\frontend.log >> ..\..\run_frontend.bat
echo echo LangFlow Frontend started at %TIME% >> ..\..\frontend.log >> ..\..\run_frontend.bat
echo echo ---------------------------------------------------------------------------------- >> ..\..\frontend.log >> ..\..\run_frontend.bat
echo call :log_cmd "npm start" ..\..\frontend.log >> ..\..\run_frontend.bat
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

goto end

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

:end
echo.
echo ✅  All done!
echo    • Backend → http://localhost:7860
if exist %FRONTEND_DIR% echo    • Frontend → http://localhost:3000
echo.
echo Check the log files for details:
echo   - backend.log: Backend server logs
echo   - poetry_debug.log: Poetry installation logs
if exist %FRONTEND_DIR% echo   - frontend.log: Frontend logs

REM Clean up temporary batch file
if exist run_backend.bat del run_backend.bat

endlocal
