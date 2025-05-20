@echo off
setlocal

REM <-- force Python 3.11 by default; you can override with e.g. "bootstrap-local.bat py-3.12"
if "%~1"=="" (
  set "PY=py -3.11"
) else (
  set "PY=%~1"
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

REM 5) Install backend
echo 🔨  Running Poetry install...
poetry install

REM 6) Fire up backend
echo 🖥️  Starting LangFlow backend...
start "LangFlow-backend" cmd /k "poetry run python -m langflow run --dev"

REM 7) Bootstrap & start frontend
echo 🌐  Bootstrapping frontend...
pushd frontend

if not exist node_modules (
  echo 📥  npm install...
  npm install
) else (
  echo ⏭️  node_modules already present
)

echo 🚀  npm start...
start "LangFlow-frontend" cmd /k "npm start"
popd

echo.
echo ✅  All done!              
echo    • Backend → http://localhost:7860  
echo    • Frontend → http://localhost:3000
endlocal
