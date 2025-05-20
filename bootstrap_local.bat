@echo off
setlocal

REM <-- force Python 3.12 by default; you can override with e.g. "bootstrap-local.bat py-3.11"
if "%~1"=="" (
  set "PY=py -3.12"
) else (
  set "PY=%~1"
)

REM Ensure we're using a compatible Python version (not 3.13)
echo Verifying Python version compatibility...
%PY% -c "import sys; print('Using Python', sys.version); version_info = sys.version_info; exit(1 if version_info.major==3 and version_info.minor>=13 else 0)" > python_version.log 2>&1
if errorlevel 1 (
  echo ERROR: Python 3.13+ detected, but this project requires Python <3.13
  echo Please use Python 3.11 or 3.12 by specifying: bootstrap_local.bat "py -3.11"
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

REM 5) Install backend with improved logging
echo 🔨  Running Poetry install with detailed logging...
echo [Debug] Checking Poetry version:
poetry --version > poetry_debug.log 2>&1
echo [Debug] Checking Poetry environment:
poetry env info >> poetry_debug.log 2>&1
echo [Debug] Checking Poetry package list before install:
poetry list >> poetry_debug.log 2>&1 || echo "Poetry list command failed - continuing" >> poetry_debug.log 2>&1

echo Running Poetry install - this may take a while...
poetry install --verbose >> poetry_debug.log 2>&1

echo [Debug] Checking if Poetry's Python can find langflow module:
poetry run python -c "import sys; print('PYTHONPATH:', sys.path); print('---'); import importlib.util; print('Looking for langflow:'); for p in sys.path: print(' checking ' + p); spec = importlib.util.find_spec('langflow', [p]); if spec: print(' FOUND at ' + p);" >> poetry_debug.log 2>&1 || echo "Import check failed" >> poetry_debug.log 2>&1

echo [Debug] Verifying Poetry environment:
poetry env info >> poetry_debug.log 2>&1

echo [Debug] Verifying if langflow is importable:
poetry run python -c "import importlib; print('Can import langflow: ', importlib.util.find_spec('langflow') is not None)" >> poetry_debug.log 2>&1

echo Poetry installation complete. Check poetry_debug.log for details.

REM 6) Fire up backend
echo 🖥️  Starting LangFlow backend...
echo [Debug] Checking if langflow module can be imported:
poetry run python -c "import sys; print('PYTHONPATH:', sys.path); print('Can import langflow directly:', __import__('importlib').util.find_spec('langflow') is not None)" > backend_debug.log 2>&1 || echo "Import check failed" > backend_debug.log 2>&1

echo [Debug] Checking Poetry detected project path:
poetry run python -c "import sys; print('Project directory:', __import__('pathlib').Path.cwd()); print('Is src in path:', 'src' in [p.split('\\')[-1] for p in sys.path if p])" >> backend_debug.log 2>&1

echo [Debug] Creating __init__.py in src/backend to ensure it's a package...
if not exist src\backend\__init__.py (
  echo. > src\backend\__init__.py
  echo Created missing __init__.py
)

echo Starting backend with a custom PYTHONPATH and module path...
start "LangFlow-backend" cmd /c "set PYTHONPATH=%CD%;%CD%\src;%CD%\src\backend;%CD%\src\backend\base&&set PYTHONDONTWRITEBYTECODE=1&&poetry run python -v -m langflow run --host 0.0.0.0 --port 7860 --dev --log-level debug > backend.log 2>&1"

REM 7) Bootstrap & start frontend
echo 🌐  Bootstrapping frontend...

REM Add a delay to ensure backend is fully started
echo ⏳  Waiting for backend to initialize (10 seconds)...
timeout /t 10 /nobreak > nul

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
  echo WARNING: Backend may not be running properly. Check backend.log for errors.
  echo Opening backend log to debug...
  type backend.log
  echo. 
  echo Poetry debug log:
  type poetry_debug.log
  echo.
  echo Press any key to continue anyway...
  pause > nul
)

pushd frontend

if not exist node_modules (
  echo 📥  npm install...
  npm install
) else (
  echo ⏭️  node_modules already present
)

echo 🚀  npm start...
echo Starting frontend with logging to frontend.log...
start "LangFlow-frontend" cmd /c "npm start > frontend.log 2>&1"
popd

echo.
echo ✅  All done!              
echo    • Backend → http://localhost:7860  
echo    • Frontend → http://localhost:3000
endlocal
