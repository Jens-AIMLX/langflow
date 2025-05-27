@echo off
echo Starting Langflow...

REM Check if virtual environment exists
if not exist "langflow_venv" (
    echo Virtual environment not found. Please run install_langflow_uv.bat first.
    exit /b 1
)

REM Activate virtual environment
call langflow_venv\Scripts\activate.bat

REM Check for Poppler in various locations
set "POPPLER_FOUND=0"
set "POPPLER_PATH="

REM Check for common Poppler locations
echo Checking for Poppler installation...

REM Check the exact directory structure you mentioned exists
if exist "langflow_venv\poppler\poppler-24.02.0\bin" (
    set "POPPLER_FOUND=1"
    set "POPPLER_PATH=%CD%\langflow_venv\poppler\poppler-24.02.0\bin"
    echo Found Poppler at %POPPLER_PATH%
) else if exist "langflow_venv\poppler\Library\bin" (
    set "POPPLER_FOUND=1"
    set "POPPLER_PATH=%CD%\langflow_venv\poppler\Library\bin"
    echo Found Poppler at %POPPLER_PATH%
) else if exist "Release-24.08.0-0\poppler-24.08.0\Library\bin" (
    set "POPPLER_FOUND=1"
    set "POPPLER_PATH=%CD%\Release-24.08.0-0\poppler-24.08.0\Library\bin"
    echo Found Poppler at %POPPLER_PATH%
) else if exist "Release-24.08.0-0\poppler-24.08.0\bin" (
    set "POPPLER_FOUND=1"
    set "POPPLER_PATH=%CD%\Release-24.08.0-0\poppler-24.08.0\bin"
    echo Found Poppler at %POPPLER_PATH%
)

REM Search for pdftoppm.exe in common locations as a further check
if "%POPPLER_FOUND%"=="0" (
    echo Searching for Poppler executables...
    where pdftoppm 2>nul
    if %ERRORLEVEL% EQU 0 (
        set "POPPLER_FOUND=1"
        for /f "tokens=*" %%a in ('where pdftoppm') do (
            set "POPPLER_PATH=%%~dpa"
            echo Found pdftoppm at %%a
        )
    )
)

REM If still not found, try to install
if "%POPPLER_FOUND%"=="0" (
    set POPPLER_DIR=langflow_venv\poppler
    echo Poppler not found. Installing it now...
    
    REM Create Poppler directory if it doesn't exist
    if not exist "%POPPLER_DIR%" (
        mkdir "%POPPLER_DIR%" > nul 2>&1
    )
    
    echo Checking available download methods...
    
    REM Check if PowerShell is available
    where powershell >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo Using PowerShell to download Poppler...
        powershell -Command "& {$ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri 'https://github.com/oschwartz10612/poppler-windows/releases/download/v24.02.0-0/Release-24.02.0-0.zip' -OutFile '%POPPLER_DIR%\poppler.zip'}" > nul
        
        if exist "%POPPLER_DIR%\poppler.zip" (
            echo Extracting with PowerShell...
            powershell -Command "& {Add-Type -AssemblyName System.IO.Compression.FileSystem; [System.IO.Compression.ZipFile]::ExtractToDirectory('%POPPLER_DIR%\poppler.zip', '%POPPLER_DIR%')}" > nul
            del "%POPPLER_DIR%\poppler.zip" > nul 2>&1
            
            REM Check if extraction worked
            if exist "%POPPLER_DIR%\Library\bin" (
                set "POPPLER_FOUND=1"
                set "POPPLER_PATH=%CD%\%POPPLER_DIR%\Library\bin"
                echo Poppler installed successfully.
            ) else if exist "%POPPLER_DIR%\poppler-24.02.0\bin" (
                set "POPPLER_FOUND=1"
                set "POPPLER_PATH=%CD%\%POPPLER_DIR%\poppler-24.02.0\bin"
                echo Poppler installed successfully.
            )
        ) else (
            echo PowerShell download failed.
        )
    ) else (
        echo PowerShell not available.
    )
    
    REM If PowerShell failed or not available, try using certutil
    if "%POPPLER_FOUND%"=="0" (
        echo Trying download with certutil...
        where certutil >nul 2>&1
        if %ERRORLEVEL% EQU 0 (
            certutil -urlcache -split -f "https://github.com/oschwartz10612/poppler-windows/releases/download/v24.02.0-0/Release-24.02.0-0.zip" "%POPPLER_DIR%\poppler.zip" > nul
            
            REM Try to extract with tar (available in Windows 10+)
            where tar >nul 2>&1
            if %ERRORLEVEL% EQU 0 (
                echo Extracting with tar...
                cd "%POPPLER_DIR%" && tar -xf poppler.zip && cd ..\..
                del "%POPPLER_DIR%\poppler.zip" > nul 2>&1
                
                REM Check directory structure after extraction
                if exist "%POPPLER_DIR%\Library\bin" (
                    set "POPPLER_FOUND=1"
                    set "POPPLER_PATH=%CD%\%POPPLER_DIR%\Library\bin"
                ) else if exist "%POPPLER_DIR%\poppler-24.02.0\bin" (
                    set "POPPLER_FOUND=1"
                    set "POPPLER_PATH=%CD%\%POPPLER_DIR%\poppler-24.02.0\bin"
                )
            )
        ) else (
            echo certutil not available.
        )
    )
    
    REM Check if Poppler was installed successfully
    if "%POPPLER_FOUND%"=="0" (
        echo Failed to install Poppler automatically.
        echo.
        echo We'll now try to guide you through manual installation.
        echo.
        
        set /p manual_choice="Would you like to proceed with manual installation? (y/n): "
        if /i "%manual_choice%"=="y" (
            call download_poppler_manual.bat
            if %ERRORLEVEL% NEQ 0 (
                exit /b 1
            ) else (
                REM Check new installation
                if exist "%POPPLER_DIR%\Library\bin" (
                    set "POPPLER_FOUND=1"
                    set "POPPLER_PATH=%CD%\%POPPLER_DIR%\Library\bin"
                ) else if exist "%POPPLER_DIR%\poppler-24.02.0\bin" (
                    set "POPPLER_FOUND=1"
                    set "POPPLER_PATH=%CD%\%POPPLER_DIR%\poppler-24.02.0\bin"
                )
            )
        ) else (
            echo.
            echo Please download poppler manually using the download_poppler_manual.bat script.
            echo After installation, run this script again.
            exit /b 1
        )
    )
)

REM If found, add Poppler to PATH
if "%POPPLER_FOUND%"=="1" (
    echo Adding Poppler to PATH: %POPPLER_PATH%
    set "PATH=%PATH%;%POPPLER_PATH%"
) else (
    echo CRITICAL ERROR: Could not find or install Poppler.
    echo PDF to Images component will not work correctly.
    echo.
    echo Please try running download_poppler_manual.bat separately.
    echo.
    set /p continue_anyway="Continue without Poppler? (y/n): "
    if /i not "%continue_anyway%"=="y" (
        exit /b 1
    )
)

REM Check for Tesseract OCR
set "TESSERACT_FOUND=0"
set "TESSERACT_PATH="

echo Checking for Tesseract OCR installation...

REM Check common Tesseract locations
if exist "langflow_venv\tesseract\tesseract.exe" (
    set "TESSERACT_FOUND=1"
    set "TESSERACT_PATH=%CD%\langflow_venv\tesseract"
    echo Found Tesseract at %TESSERACT_PATH%
) else if exist "C:\Program Files\Tesseract-OCR\tesseract.exe" (
    set "TESSERACT_FOUND=1"
    set "TESSERACT_PATH=C:\Program Files\Tesseract-OCR"
    echo Found Tesseract at %TESSERACT_PATH%
) else if exist "C:\Program Files (x86)\Tesseract-OCR\tesseract.exe" (
    set "TESSERACT_FOUND=1"
    set "TESSERACT_PATH=C:\Program Files (x86)\Tesseract-OCR"
    echo Found Tesseract at %TESSERACT_PATH%
) else if exist "%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe" (
    set "TESSERACT_FOUND=1"
    set "TESSERACT_PATH=%LOCALAPPDATA%\Programs\Tesseract-OCR"
    echo Found Tesseract at %TESSERACT_PATH%
)

REM Check if tesseract is in PATH
if "%TESSERACT_FOUND%"=="0" (
    where tesseract.exe >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set "TESSERACT_FOUND=1"
        for /f "tokens=*" %%a in ('where tesseract.exe') do (
            set "TESSERACT_PATH=%%~dpa"
            echo Found tesseract in PATH at %%a
        )
    )
)

REM Check for language data files
set "LANGUAGE_DATA_FOUND=0"
set "TESSDATA_DIR="

if "%TESSERACT_FOUND%"=="1" (
    echo Checking for Tesseract language data...
    
    REM Check in tesseract installation
    if exist "%TESSERACT_PATH%\tessdata\deu.traineddata" (
        set "LANGUAGE_DATA_FOUND=1"
        set "TESSDATA_DIR=%TESSERACT_PATH%\tessdata"
        echo Found German language data at %TESSDATA_DIR%
    ) else if exist "%CD%\langflow_venv\tesseract\tessdata\deu.traineddata" (
        set "LANGUAGE_DATA_FOUND=1"
        set "TESSDATA_DIR=%CD%\langflow_venv\tesseract\tessdata"
        echo Found German language data at %TESSDATA_DIR%
    )
    
    REM If language data not found, download it
    if "%LANGUAGE_DATA_FOUND%"=="0" (
        echo German language data not found. Downloading it now...
        
        REM Ensure tessdata directory exists
        if not exist "%CD%\langflow_venv\tesseract\tessdata" (
            mkdir "%CD%\langflow_venv\tesseract\tessdata" 2>nul
        )
        
        REM Try to download language data
        powershell -Command "& {$ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri 'https://github.com/tesseract-ocr/tessdata/raw/main/deu.traineddata' -OutFile '%CD%\langflow_venv\tesseract\tessdata\deu.traineddata'}" 2>nul
        
        if exist "%CD%\langflow_venv\tesseract\tessdata\deu.traineddata" (
            set "LANGUAGE_DATA_FOUND=1"
            set "TESSDATA_DIR=%CD%\langflow_venv\tesseract\tessdata"
            echo German language data downloaded successfully.
        ) else (
            echo Failed to download German language data.
            echo Running fix_ocr.bat script to attempt to fix the issue...
            call fix_ocr.bat
            
            if exist "%CD%\langflow_venv\tesseract\tessdata\deu.traineddata" (
                set "LANGUAGE_DATA_FOUND=1"
                set "TESSDATA_DIR=%CD%\langflow_venv\tesseract\tessdata"
                echo German language data downloaded successfully by fix_ocr.bat.
            )
        )
    )
) else (
    echo Tesseract OCR not found. It's needed for OCR functionality.
    echo.
    set /p install_tesseract="Would you like to install Tesseract OCR now? (y/n): "
    if /i "%install_tesseract%"=="y" (
        call install_tesseract.bat
        if %ERRORLEVEL% NEQ 0 (
            echo Tesseract installation failed.
            echo.
            set /p continue_anyway="Continue without Tesseract? (y/n): "
            if /i not "%continue_anyway%"=="y" (
                exit /b 1
            )
        ) else (
            set "TESSERACT_FOUND=1"
            set "TESSERACT_PATH=%CD%\langflow_venv\tesseract"
            echo Tesseract installed successfully at %TESSERACT_PATH%
            
            REM Check for language data after installation
            if exist "%TESSERACT_PATH%\tessdata\deu.traineddata" (
                set "LANGUAGE_DATA_FOUND=1"
                set "TESSDATA_DIR=%TESSERACT_PATH%\tessdata"
                echo Found German language data at %TESSDATA_DIR%
            ) else (
                echo Running fix_ocr.bat to download language data...
                call fix_ocr.bat
                
                if exist "%CD%\langflow_venv\tesseract\tessdata\deu.traineddata" (
                    set "LANGUAGE_DATA_FOUND=1"
                    set "TESSDATA_DIR=%CD%\langflow_venv\tesseract\tessdata"
                    echo German language data downloaded successfully.
                )
            )
        )
    ) else (
        echo.
        echo Continuing without Tesseract OCR.
        echo OCR functionality will not be available.
        echo.
        echo You can install it later by running: install_tesseract.bat
    )
)

REM Set up Tesseract environment variables if found
if "%TESSERACT_FOUND%"=="1" (
    echo Adding Tesseract to PATH: %TESSERACT_PATH%
    set "PATH=%PATH%;%TESSERACT_PATH%"
    
    if "%LANGUAGE_DATA_FOUND%"=="1" (
        echo Setting TESSDATA_PREFIX to %TESSDATA_DIR%
        set "TESSDATA_PREFIX=%TESSDATA_DIR%"
    ) else (
        echo WARNING: Language data not found. OCR may not work correctly.
        echo You can download language data later using fix_ocr.bat
    )
)

REM Ensure custom_nodes directory exists
if not exist "custom_nodes" (
    mkdir "custom_nodes" > nul 2>&1
)

REM Start Langflow
echo Starting Langflow...
python -m langflow run

echo.
echo To access Langflow, open your browser and go to: http://127.0.0.1:7860/flows 