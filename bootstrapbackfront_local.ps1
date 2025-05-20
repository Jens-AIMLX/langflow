<#
.SYNOPSIS
  Bootstraps LangFlow backend + frontend from a local checkout using the py‐launcher

.DESCRIPTION
  1) Creates .venv (if missing) via "py -m venv .\.venv"
  2) Activates the venv
  3) Upgrades pip/setuptools/wheel
  4) Installs Poetry into the venv (if not already present)
  5) Runs `poetry install`
  6) Starts the backend in dev mode (via Poetry in the background)
  7) Installs & starts the React frontend
#>

Param(
  [string]$Python = "py"
)

# 1) Create venv if missing
if ( -not ( Test-Path .\.venv ) ) {
    Write-Host "🔧 Creating venv via `$Python -m venv .\.venv`..."
    & $Python -m venv .\.venv
}
else {
    Write-Host "♻️  Re-using existing .venv"
}

# 2) Activate it
Write-Host "🚀 Activating .venv..."
. .\.venv\Scripts\Activate.ps1

# 3) Upgrade core packaging tools
Write-Host "⬆️  Upgrading pip, setuptools, wheel..."
pip install --upgrade pip setuptools wheel

# 4) Ensure Poetry is in the venv
if ( -not ( & $Python -m pip show poetry ) ) {
    Write-Host "📦 Installing Poetry into the venv..."
    & $Python -m pip install poetry
}
else {
    Write-Host "✅ Poetry already present"
}

# 5) Install backend deps
Write-Host "🔨 Installing backend via Poetry..."
& $Python -m poetry install

# 6) Launch backend (dev mode) in a new process
Write-Host "🖥️  Starting backend (dev)..."
Start-Process $Python -ArgumentList '-m','poetry','run','python','-m','langflow','run','--dev' -NoNewWindow

# 7) Frontend: npm install & start
Write-Host "🌐 Bootstrapping frontend..."
Push-Location frontend

if ( -not ( Test-Path node_modules ) ) {
    Write-Host "📥 Installing frontend packages..."
    npm install 
}
else {
    Write-Host "⏭️  Frontend already bootstrapped"
}

Write-Host "🚀 Starting React frontend..."
npm start

Pop-Location

Write-Host "`n✅ Done!  Backend → http://localhost:7860 | Frontend → http://localhost:3000"
