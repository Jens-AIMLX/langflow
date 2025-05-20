# Langflow Bootstrap with UV and Python Launcher

This script provides a simple way to install Langflow using UV with the Python Launcher (py), following the exact steps from the [Ollama-Langflow integration article](https://upwarddynamism.com/ai-use-cases-prompts/local-ai-agents-ollama-langflow/).

## Installation Options

### Option 1: Using Command Prompt (CMD)

Run the batch script:
```
bootstrap_uv.bat
```

### Option 2: Using PowerShell

If you're using PowerShell, you might need to set the execution policy first:
```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
```

Then run the PowerShell script:
```powershell
.\bootstrap_uv.ps1
```

## What the Script Does

The script follows these exact steps from the article, using the Python Launcher (py):

1. Installs UV package manager: `py -m pip install uv`
2. Creates a dedicated Langflow folder
3. Creates a virtual environment using UV: `py -m uv venv .venv`
4. Activates the virtual environment
5. Installs Langflow using UV: `py -m uv pip install langflow`
6. Runs Langflow: `py -m langflow run`

## Restarting Langflow Later

To restart Langflow after closing it:

### Using Command Prompt (CMD)
```
cd Langflow
.venv\Scripts\activate.bat
py -m langflow run
```

### Using PowerShell
```powershell
cd Langflow
.\.venv\Scripts\Activate.ps1
py -m langflow run
```

## Using Langflow with Ollama

Once Langflow is installed:

1. Install Ollama from [ollama.ai](https://ollama.ai/)
2. Run a model with tool support (e.g., `ollama run qwen2.5:7b`)
3. In the Langflow interface, add an "Ollama" component and configure it with:
   - Base URL: http://localhost:11434
   - Model Name: your chosen model (e.g., qwen2.5:7b)
   - Enable "Tool Model Enabled"

## Troubleshooting

If you encounter build errors related to `webrtcvad`, you may need to install Visual C++ Build Tools:

1. Download and install [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
2. During installation, select "Desktop development with C++"
3. Try installing Langflow again
