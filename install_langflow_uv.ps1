Write-Host "Installing Langflow using uv..."

# Step 1: Create a virtual environment using Python launcher
py -m venv langflow_venv

# Step 2: Activate the virtual environment
& .\langflow_venv\Scripts\Activate.ps1

# Step 3: Install uv inside the virtual environment
py -m pip install uv

# Step 4: Install Langflow using uv
Write-Host "Installing Langflow with uv (this may take some time)..."
py -m uv pip install langflow

# Step 5: Run Langflow
Write-Host "Starting Langflow..."
py -m langflow run

Write-Host ""
Write-Host "If Langflow started successfully, you can access it at: http://localhost:7860"
Write-Host ""
Write-Host "To restart Langflow later:"
Write-Host "1. Run: .\langflow_venv\Scripts\Activate.ps1"
Write-Host "2. Run: py -m langflow run"
