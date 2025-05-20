# ============================================================================
# Langflow Bootstrap Script using uv with Python Launcher (PowerShell Version)
# Based on: https://upwarddynamism.com/ai-use-cases-prompts/local-ai-agents-ollama-langflow/
# ============================================================================

Write-Host "Langflow Bootstrap Script"
Write-Host "Based on: https://upwarddynamism.com/ai-use-cases-prompts/local-ai-agents-ollama-langflow/"
Write-Host ""

# Step 1: Install uv if not already installed
Write-Host "Step 1: Installing uv package manager..."
py -m pip install uv
Write-Host ""

# Step 2: Create a dedicated folder for Langflow
Write-Host "Step 2: Creating a dedicated folder for Langflow..."
if (-not (Test-Path "Langflow")) {
    New-Item -Path "Langflow" -ItemType Directory | Out-Null
}
Set-Location -Path "Langflow"
Write-Host "Created and moved to Langflow folder: $((Get-Location).Path)"
Write-Host ""

# Step 3: Create the virtual environment
Write-Host "Step 3: Creating virtual environment..."
py -m uv venv .venv
Write-Host ""

# Step 4: Activate the virtual environment
Write-Host "Step 4: Activating virtual environment..."
& .\.venv\Scripts\Activate.ps1
Write-Host ""

# Step 5: Install Langflow using uv
Write-Host "Step 5: Installing Langflow using uv..."
Write-Host "This may take some time..."
py -m uv pip install langflow
Write-Host ""

# Step 6: Run Langflow
Write-Host "Step 6: Running Langflow..."
py -m langflow run
Write-Host ""

# This part will only execute if the user manually stops Langflow
Write-Host ""
Write-Host "To restart Langflow later:"
Write-Host "1. Navigate to this folder: $((Get-Location).Path)"
Write-Host "2. Run: .\.venv\Scripts\Activate.ps1"
Write-Host "3. Run: py -m langflow run"
Write-Host ""
