@echo off
echo Installing Langflow using uv...

REM Step 0: Kill any existing Langflow processes
echo Checking for existing Langflow processes...
taskkill /F /IM "pythonthon.exe" /FI "WINDOWTITLE eq langflow*" > nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Existing Langflow processes terminated.
) else (
    echo No existing Langflow processes found.
)

REM Step 1: Check if Rust is installed
rustc --version > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Rust is required for some dependencies but is not installed.
    echo Please install Rust from https://rustup.rs/ and run this script again.
    echo.
    echo After installing Rust, restart your command prompt and run this script again.
    exit /b 1
)

REM Step 2: Add the x86_64-pc-windows-msvc target for Rust (64-bit)
echo Adding required Rust target (x86_64-pc-windows-msvc)...
rustup target add x86_64-pc-windows-msvc

REM Step 3: Set environment variables to force 64-bit architecture
echo Setting environment variables to force 64-bit architecture...
set ARCHFLAGS=-arch x86_64
set DISTUTILS_ARCHITECTURE=x86_64
set DISTUTILS_PLATFORM=win-amd64

REM Step 4: Create a virtual environment using Python launcher
python -m venv langflow_venv

REM Step 5: Activate the virtual environment
call langflow_venv\Scripts\activate.bat

REM Step 6: Install required packages
echo Installing required packages...
python -m pip install pdf2image

REM Step 7: Setup Poppler silently (treated as part of Langflow dependencies)
echo Setting up dependencies...
set POPPLER_DIR=langflow_venv\poppler
if not exist "%POPPLER_DIR%" (
    mkdir "%POPPLER_DIR%" > nul 2>&1
    
    echo Downloading dependencies...
    powershell -Command "& {$ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri 'https://github.com/oschwartz10612/poppler-windows/releases/download/v24.02.0-0/Release-24.02.0-0.zip' -OutFile '%POPPLER_DIR%\poppler.zip'}" > nul 2>&1
    
    echo Extracting dependencies...
    powershell -Command "& {Add-Type -AssemblyName System.IO.Compression.FileSystem; [System.IO.Compression.ZipFile]::ExtractToDirectory('%POPPLER_DIR%\poppler.zip', '%POPPLER_DIR%')}" > nul 2>&1
    
    del "%POPPLER_DIR%\poppler.zip" > nul 2>&1
)

REM Add Poppler to PATH for the current session
set "PATH=%PATH%;%CD%\%POPPLER_DIR%\Library\bin"

REM Create a script to set the environment variable when activating the virtual environment
echo @echo off > langflow_venv\Scripts\activate.bat.tmp
echo REM ===== BEGIN ORIGINAL ACTIVATE.BAT ===== >> langflow_venv\Scripts\activate.bat.tmp
type langflow_venv\Scripts\activate.bat >> langflow_venv\Scripts\activate.bat.tmp
echo REM ===== END ORIGINAL ACTIVATE.BAT ===== >> langflow_venv\Scripts\activate.bat.tmp
echo. >> langflow_venv\Scripts\activate.bat.tmp
echo REM Set Poppler path >> langflow_venv\Scripts\activate.bat.tmp
echo set "PATH=%%PATH%%;%%VIRTUAL_ENV%%\poppler\Library\bin" >> langflow_venv\Scripts\activate.bat.tmp
move /Y langflow_venv\Scripts\activate.bat.tmp langflow_venv\Scripts\activate.bat > nul

REM Create a custom_nodes directory if it doesn't exist
if not exist "custom_nodes" (
    mkdir custom_nodes
)

REM Update the PDF to Images component to use the Poppler path from the virtual environment
if exist "custom_nodes\pdf_to_image.py" (
    echo Updating PDF to Images component...
    powershell -Command "(Get-Content custom_nodes\pdf_to_image.py) -replace 'default=\"D:\\\\dev\\\\Langflow\\\\langflow\\\\Release-24.08.0-0\\\\poppler-24.08.0\\\\Library\\\\bin\"', 'default=os.path.join(os.environ.get(\"VIRTUAL_ENV\", \"\"), \"poppler\", \"Library\", \"bin\")' | Set-Content custom_nodes\pdf_to_image.py"
)

REM Step 8: Install uv inside the virtual environment
python -m pip install uv

REM Step 9: Install a more recent stable version of Langflow with all dependencies
echo Installing Langflow with all dependencies except excludes...
python -m uv pip install "langflow==1.1.4" --verbose


echo To restart Langflow later:
echo 1. Run: langflow_venv\Scripts\activate.bat
echo 2. Run: python -m langflow run
echo.
echo Note: We're using Langflow version 1.1.4 which provides a good balance of features and stability.
echo This version should work well for integration with Ollama.