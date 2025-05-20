@echo off
setlocal

REM — optionally override Python launcher by passing first arg:
if "%~1"=="" (
    set "PY=py"
) else (
    set "PY=%~1"
)

REM 1) Create venv if missing
if not exist .venv (
    echo 🔧 Creating virtual environment...
    %PY% -m venv .venv
) else (
    echo ♻️  Re-using existing .venv
)

REM 2) Activate it
echo 🚀 Activating .venv...
call .venv\Scripts\activate.bat

REM 3) Upgrade pip, setuptools, wheel
echo ⬆️  Upgrading pip, setuptools, wheel...
pip install --upgrade pip setuptools wheel

REM 4) Ensure Poetry is present
where poetry >nul 2>&1
if errorlevel 1 (
    echo 📦 Installing Poetry into the venv...
    pip install poetry
) else (
    echo ✅ Poetry already installed
)

REM 5) Install backend dependencies
echo 🔨 Installing backend via Poetry...
poetry install

REM 6) Launch backend in dev mode
echo 🖥️  Starting LangFlow backend (dev)...
start "LangFlow Backend" cmd /k "poetry run python -m langflow run --dev"

REM 7) Bootstrap and start frontend
echo 🌐 Bootstrapping frontend...
pushd frontend

if not exist node_modules (
    echo 📥 Installing frontend packages...
    npm install
) else (
    echo ⏭️  Frontend already bootstrapped
)

echo 🚀 Starting React frontend...
start "LangFlow Frontend" cmd /k "npm start"

popd

echo.
echo ✅ Done! Backend → http://localhost:7860    Frontend → http://localhost:3000
endlocal
