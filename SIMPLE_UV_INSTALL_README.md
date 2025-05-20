# Simple Langflow Installation with UV

This guide provides simple instructions for installing Langflow using UV, following the approach described in [this article](https://upwarddynamism.com/ai-use-cases-prompts/local-ai-agents-ollama-langflow/), but using the Python launcher.

## Installation Options

### Option 1: Using the Batch Script (Windows CMD)

1. Run the batch script:
   ```
   install_langflow_uv.bat
   ```

### Option 2: Using the PowerShell Script (Windows PowerShell)

1. If needed, set the execution policy:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
   ```

2. Run the PowerShell script:
   ```powershell
   .\install_langflow_uv.ps1
   ```

### Option 3: Manual Installation

If you prefer to install manually, follow these steps:

1. Create a virtual environment using the Python launcher:
   ```
   py -m venv langflow_venv
   ```

2. Activate the virtual environment:
   - Windows CMD: `langflow_venv\Scripts\activate.bat`
   - Windows PowerShell: `.\langflow_venv\Scripts\Activate.ps1`

3. Install uv using the Python launcher:
   ```
   py -m pip install uv
   ```

4. Install Langflow using uv and the Python launcher:
   ```
   py -m uv pip install langflow
   ```

5. Run Langflow using the Python launcher:
   ```
   py -m langflow run
   ```

## Troubleshooting Build Errors

If you encounter build errors related to `webrtcvad`, you can try these solutions:

### Solution 1: Install Visual C++ Build Tools

The error indicates missing Visual C++ build tools. Install them:

1. Download and install [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
2. During installation, select "Desktop development with C++"
3. Try installing Langflow again

### Solution 2: Use a Pre-built Wheel

You can try installing a pre-built wheel for webrtcvad:

1. Download a compatible wheel from [Unofficial Windows Binaries](https://www.lfd.uci.edu/~gohlke/pythonlibs/#webrtcvad)
2. Install it with uv:
   ```
   py -m uv pip install path\to\downloaded\webrtcvad-2.0.10-cp312-cp312-win_amd64.whl
   ```
3. Then install Langflow:
   ```
   py -m uv pip install langflow
   ```

## Using Langflow with Ollama

Once Langflow is installed:

1. Install Ollama from [ollama.ai](https://ollama.ai/)
2. Run a model with tool support (e.g., `ollama run qwen2.5:7b`)
3. In the Langflow interface, add an "Ollama" component and configure it with:
   - Base URL: http://localhost:11434
   - Model Name: your chosen model (e.g., qwen2.5:7b)
   - Enable "Tool Model Enabled"

## Restarting Langflow Later

To restart Langflow after closing it:

1. Activate the virtual environment:
   - Windows CMD: `langflow_venv\Scripts\activate.bat`
   - Windows PowerShell: `.\langflow_venv\Scripts\Activate.ps1`

2. Run Langflow using the Python launcher:
   ```
   py -m langflow run
   ```
