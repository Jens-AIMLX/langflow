@echo off
echo Installing Poppler for PDF to Image conversion...

:: Create a directory for Poppler
set POPPLER_DIR=Release-24.08.0-0\poppler-24.08.0
if not exist "%POPPLER_DIR%" (
    echo Creating directory for Poppler...
    mkdir "%POPPLER_DIR%"
)

:: Check if wget is available
where wget >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo wget not found. Using PowerShell to download files instead.
    
    :: Download Poppler using PowerShell
    echo Downloading Poppler using PowerShell...
    powershell -Command "& {$ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri 'https://github.com/oschwartz10612/poppler-windows/releases/download/v24.02.0-0/Release-24.02.0-0.zip' -OutFile '%POPPLER_DIR%\poppler.zip'}"
) else (
    :: Download Poppler using wget
    echo Downloading Poppler using wget...
    wget -q --show-progress -O "%POPPLER_DIR%\poppler.zip" "https://github.com/oschwartz10612/poppler-windows/releases/download/v24.02.0-0/Release-24.02.0-0.zip"
)

:: Extract the Poppler zip file
echo Extracting Poppler...
powershell -Command "& {Add-Type -AssemblyName System.IO.Compression.FileSystem; [System.IO.Compression.ZipFile]::ExtractToDirectory('%POPPLER_DIR%\poppler.zip', '%POPPLER_DIR%')}"

:: Clean up the zip file
del "%POPPLER_DIR%\poppler.zip"

:: Add Poppler to PATH for the current session
set "PATH=%PATH%;%CD%\%POPPLER_DIR%\Library\bin"

echo Poppler installation complete!
echo.
echo Poppler has been installed to: %CD%\%POPPLER_DIR%\Library\bin
echo.
echo You can now use the PDF to Images component in Langflow.
echo.
echo Press any key to exit...
pause > nul 