<#
.SYNOPSIS
  Clone, venv, Poetry-install LangFlow backend.

.DESCRIPTION
  1. Clones your branch.
  2. Creates & activates a Python 3.12 venv.
  3. Installs Poetry into that venv.
  4. Uses Poetry’s lockfile to install *exact*, pinned deps—no pip backtracking.
#>

param(
  [string]$RepoUrl   = "https://github.com/langflow-ai/langflow.git",
  [string]$Branch    = "main"
)

# 1) Clone
git clone --branch $Branch $RepoUrl langflow
Set-Location langflow

# 2) Create & activate venv
python -m venv .venv
. .\.venv\Scripts\Activate.ps1

# 3) Upgrade pip + install Poetry
pip install --upgrade pip setuptools wheel
pip install poetry

# 4) Make sure Poetry stays in-project
poetry config virtualenvs.in-project true

# 5) Point Poetry at our Python 3.12 explicitly
poetry env use (Get-Command python).Source

# 6) Install *exact* versions from poetry.lock (fast!)
poetry install --no-interaction --no-ansi
