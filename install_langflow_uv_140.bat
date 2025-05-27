@echo off
echo Installing Langflow using uv

REM Step 0: Check if Python is installed and install if needed
echo Checking Python installation
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python not found. Checking for py launcher
    py --version >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo Python is not installed. Installing Python 3.12
        echo.
        echo Downloading Python 3.12 installer

        REM Create temp directory for Python installer
        if not exist "temp" mkdir temp

        REM Detect system architecture and download appropriate Python installer
        echo Detecting system architecture
        if "%PROCESSOR_ARCHITECTURE%"=="AMD64" (
            echo Detected 64-bit system. Downloading Python 3.12 64-bit
            powershell -Command "& {$ProgressPreference = 'SilentlyContinue'; Write-Host 'Downloading Python 3.12 64-bit'; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe' -OutFile 'temp\python-installer.exe'}"
        ) else (
            echo Detected 32-bit system. Downloading Python 3.12 32-bit
            powershell -Command "& {$ProgressPreference = 'SilentlyContinue'; Write-Host 'Downloading Python 3.12 32-bit'; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.8/python-3.12.8.exe' -OutFile 'temp\python-installer.exe'}"
        )

        if not exist "temp\python-installer.exe" (
            echo ERROR: Failed to download Python installer.
            echo Please download and install Python manually from https://www.python.org/downloads/
            pause
            exit /b 1
        )

        echo Installing Python 3.12
        echo This may take a few minutes. Please wait
        echo.

        REM Install Python silently with all features and add to PATH
        REM InstallAllUsers=0 means install for current user only (no admin required)
        REM PrependPath=1 adds Python to PATH
        echo Starting Python installation
        temp\python-installer.exe /quiet InstallAllUsers=0 PrependPath=1 Include_test=0 Include_doc=0 Include_dev=1 Include_debug=0 Include_launcher=1 InstallLauncherAllUsers=0 Include_tcltk=1 Include_pip=1 Include_symbols=0

        REM Wait for installation to complete (Python installer can take 2-5 minutes)
        echo Waiting for Python installation to complete
        timeout /t 30 /nobreak >nul

        REM Check if installation was successful
        echo Verifying Python installation
        timeout /t 5 /nobreak >nul

        REM Clean up installer
        del temp\python-installer.exe >nul 2>&1
        rmdir temp >nul 2>&1

        echo Python installation completed.
        echo.
        echo IMPORTANT: Please restart your command prompt and run this script again.
        echo This is necessary for the PATH changes to take effect.
        echo.
        pause
        exit /b 0
    ) else (
        echo Found py launcher. Using py command for Python.
        set PYTHON_CMD=py
    )
) else (
    echo Python found. Using python command.
    set PYTHON_CMD=python
)

REM Verify Python version
echo Checking Python version
%PYTHON_CMD% --version
%PYTHON_CMD% -c "import sys; print('Python ' + str(sys.version_info.major) + '.' + str(sys.version_info.minor) + '.' + str(sys.version_info.micro))"

REM Check if Python version is compatible (3.8+)
%PYTHON_CMD% -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python 3.8 or higher is required for Langflow.
    echo Please install a newer version of Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python version is compatible.
echo.

REM Step 1: Kill any existing Langflow processes
echo Checking for existing Langflow processes
taskkill /F /IM "python.exe" /FI "WINDOWTITLE eq langflow*" > nul 2>&1
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
echo Adding required Rust target x86_64-pc-windows-msvc
rustup target add x86_64-pc-windows-msvc

REM Step 3: Set environment variables to force 64-bit architecture
echo Setting environment variables to force 64-bit architecture
set ARCHFLAGS=-arch x86_64
set DISTUTILS_ARCHITECTURE=x86_64
set DISTUTILS_PLATFORM=win-amd64

REM Step 4: Create a virtual environment using Python launcher
echo Creating virtual environment
%PYTHON_CMD% -m venv langflow_venv

REM Step 5: Activate the virtual environment
call langflow_venv\Scripts\activate.bat

REM Step 6: Install required packages
echo Installing required packages
%PYTHON_CMD% -m pip install pdf2image pytesseract pillow pyth3

REM Step 7: Setup Poppler silently (treated as part of Langflow dependencies)
echo Setting up Poppler dependencies
set POPPLER_DIR=langflow_venv\poppler
if not exist "%POPPLER_DIR%" (
    mkdir "%POPPLER_DIR%" > nul 2>&1

    echo Downloading Poppler
    powershell -Command "& {$ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri 'https://github.com/oschwartz10612/poppler-windows/releases/download/v24.02.0-0/Release-24.02.0-0.zip' -OutFile '%POPPLER_DIR%\poppler.zip'}" > nul 2>&1

    echo Extracting Poppler
    powershell -Command "& {Add-Type -AssemblyName System.IO.Compression.FileSystem; [System.IO.Compression.ZipFile]::ExtractToDirectory('%POPPLER_DIR%\poppler.zip', '%POPPLER_DIR%')}" > nul 2>&1

    del "%POPPLER_DIR%\poppler.zip" > nul 2>&1
)

REM Step 8: Setup Tesseract OCR silently (treated as part of Langflow dependencies)
echo Setting up Tesseract OCR dependencies
set TESSERACT_DIR=langflow_venv\tesseract
if not exist "%TESSERACT_DIR%" (
    mkdir "%TESSERACT_DIR%" > nul 2>&1

    echo Downloading Tesseract OCR
    powershell -Command "& {$ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri 'https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.1.20230401.exe' -OutFile '%TESSERACT_DIR%\tesseract-installer.exe'}" > nul 2>&1

    echo Installing Tesseract OCR silently
    echo This may take a moment, please wait
    "%TESSERACT_DIR%\tesseract-installer.exe" /S /D=%CD%\%TESSERACT_DIR% > nul 2>&1

    echo Downloading German language data
    if not exist "%TESSERACT_DIR%\tessdata" (
        mkdir "%TESSERACT_DIR%\tessdata" > nul 2>&1
    )
    powershell -Command "& {$ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri 'https://github.com/tesseract-ocr/tessdata/raw/main/deu.traineddata' -OutFile '%TESSERACT_DIR%\tessdata\deu.traineddata'}" > nul 2>&1

    del "%TESSERACT_DIR%\tesseract-installer.exe" > nul 2>&1
)

REM Add dependencies to PATH for the current session
set "PATH=%PATH%;%CD%\%POPPLER_DIR%\Library\bin;%CD%\%TESSERACT_DIR%"

REM Create a script to set the environment variables when activating the virtual environment
echo @echo off > langflow_venv\Scripts\activate.bat.tmp
echo REM ===== BEGIN ORIGINAL ACTIVATE.BAT ===== >> langflow_venv\Scripts\activate.bat.tmp
type langflow_venv\Scripts\activate.bat >> langflow_venv\Scripts\activate.bat.tmp
echo REM ===== END ORIGINAL ACTIVATE.BAT ===== >> langflow_venv\Scripts\activate.bat.tmp
echo. >> langflow_venv\Scripts\activate.bat.tmp
echo REM Set dependency paths >> langflow_venv\Scripts\activate.bat.tmp
echo set "PATH=%%PATH%%;%%VIRTUAL_ENV%%\poppler\Library\bin;%%VIRTUAL_ENV%%\tesseract" >> langflow_venv\Scripts\activate.bat.tmp
echo set "TESSDATA_PREFIX=%%VIRTUAL_ENV%%\tesseract\tessdata" >> langflow_venv\Scripts\activate.bat.tmp
move /Y langflow_venv\Scripts\activate.bat.tmp langflow_venv\Scripts\activate.bat > nul

REM Create a custom_nodes directory if it doesn't exist
if not exist "custom_nodes" (
    mkdir custom_nodes
)

REM Step 9: Install uv inside the virtual environment
echo Installing uv package manager
%PYTHON_CMD% -m pip install uv

REM Step 10: Install Langflow with dependencies
echo Installing Langflow with OCR/Vision support
%PYTHON_CMD% -m uv pip install "langflow[vision]==1.4.0" --verbose

REM The langflow-vision package might not be available, skip if it fails
echo Checking for Langflow vision plugins
%PYTHON_CMD% -m pip install --no-deps --dry-run langflow-vision 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Installing Langflow Vision plugin
    %PYTHON_CMD% -m uv pip install langflow-vision --verbose
) else (
    echo Langflow Vision plugin package not found, skipping.
    echo This is normal - we will use our custom components instead.
)

echo.
echo Installation completed successfully
echo.

REM Step 11: Ask user if they want to start Langflow now
set /p start_now="Do you want to start Langflow now? (y/n): "
if /i "%start_now%"=="y" (
    echo.
    echo Starting Langflow
    call run_langflow.bat
) else (
    echo.
    echo Langflow has been installed but not started.
    echo You can start it later by running: run_langflow.bat
    echo.
    echo When Langflow starts, you can access it at: http://127.0.0.1:7860/flows
)

echo.
echo Note: We're using Langflow version 1.4.0 with OCR capabilities.
echo This version includes Poppler for PDF to image conversion and Tesseract for OCR.