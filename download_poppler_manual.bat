@echo off
echo ========================================
echo    MANUAL POPPLER INSTALLATION GUIDE
echo ========================================
echo.
echo This script will guide you through manual Poppler installation.
echo.

set POPPLER_DIR=langflow_venv\poppler
if not exist "%POPPLER_DIR%" (
    mkdir "%POPPLER_DIR%"
    echo Created directory: %POPPLER_DIR%
)

echo.
echo STEP 1: Download Poppler
echo -----------------------
echo Please download Poppler manually using one of these methods:
echo.
echo Option A: Download in your browser
echo   1. Open this URL in your browser:
echo      https://github.com/oschwartz10612/poppler-windows/releases/download/v24.02.0-0/Release-24.02.0-0.zip
echo   2. Save the file to: %CD%\%POPPLER_DIR%\poppler.zip
echo.
echo Option B: Use any download manager
echo   Download URL: https://github.com/oschwartz10612/poppler-windows/releases/download/v24.02.0-0/Release-24.02.0-0.zip
echo   Save as: %CD%\%POPPLER_DIR%\poppler.zip
echo.

echo Press any key when you've downloaded the Poppler zip file...
pause > nul

if not exist "%POPPLER_DIR%\poppler.zip" (
    echo.
    echo ERROR: Could not find %POPPLER_DIR%\poppler.zip
    echo Please download the file and try again.
    exit /b 1
)

echo.
echo STEP 2: Extract Poppler
echo ---------------------
echo Now we need to extract the zip file.
echo.

echo Checking for extraction tools...

REM Try using Windows built-in expand command
where expand >nul 2>&1
set EXPAND_AVAILABLE=%ERRORLEVEL%

REM Try using PowerShell
where powershell >nul 2>&1
set POWERSHELL_AVAILABLE=%ERRORLEVEL%

REM Try using tar
where tar >nul 2>&1
set TAR_AVAILABLE=%ERRORLEVEL%

if %POWERSHELL_AVAILABLE% EQU 0 (
    echo Using PowerShell to extract...
    powershell -Command "& {Add-Type -AssemblyName System.IO.Compression.FileSystem; [System.IO.Compression.ZipFile]::ExtractToDirectory('%POPPLER_DIR%\poppler.zip', '%POPPLER_DIR%')}"
) else if %TAR_AVAILABLE% EQU 0 (
    echo Using tar to extract...
    cd "%POPPLER_DIR%" && tar -xf poppler.zip && cd ..\..
) else (
    echo.
    echo No automatic extraction tools found.
    echo.
    echo Please extract the ZIP file manually:
    echo 1. Open File Explorer and navigate to: %CD%\%POPPLER_DIR%
    echo 2. Right-click poppler.zip and select "Extract All..."
    echo 3. Extract to the current directory (%CD%\%POPPLER_DIR%)
    echo.
    echo Press any key when extraction is complete...
    pause > nul
)

REM Verify extraction worked
if exist "%POPPLER_DIR%\Library\bin" (
    echo.
    echo SUCCESS: Poppler has been installed correctly!
    del "%POPPLER_DIR%\poppler.zip" >nul 2>&1
) else (
    echo.
    echo ERROR: Poppler extraction appears to have failed.
    echo.
    echo Please extract the zip file manually to: %CD%\%POPPLER_DIR%
    echo The directory structure should be: %CD%\%POPPLER_DIR%\Library\bin
    echo.
    echo After extraction, you can run run_langflow.bat again.
    exit /b 1
)

echo.
echo ========================================
echo Installation complete! You can now run:
echo run_langflow.bat
echo ========================================
echo.
pause 