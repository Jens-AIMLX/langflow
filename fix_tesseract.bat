@echo off
echo ========================================
echo     TESSERACT OCR FIX TOOL
echo ========================================
echo.

REM Check if Tesseract is already installed
set "TESSERACT_FOUND=0"
set "TESSERACT_PATHS="

REM Check common paths
echo Checking common Tesseract installation locations...

if exist "C:\Program Files\Tesseract-OCR\tesseract.exe" (
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
) else if exist "langflow_venv\tesseract\tesseract.exe" (
    set "TESSERACT_FOUND=1"
    set "TESSERACT_PATH=%CD%\langflow_venv\tesseract"
    echo Found Tesseract at %TESSERACT_PATH%
)

REM Check for tesseract in PATH
where tesseract 2>nul
if %ERRORLEVEL% EQU 0 (
    for /f "tokens=*" %%a in ('where tesseract') do (
        set "TESSERACT_FOUND=1"
        set "TESSERACT_PATH=%%~dpa"
        echo Found Tesseract in PATH at %%a
        goto :tesseract_found
    )
)

:tesseract_found
if "%TESSERACT_FOUND%"=="1" (
    echo.
    echo Tesseract is already installed. Setting up environment...
    
    REM Check if tessdata exists
    if exist "%TESSERACT_PATH%\tessdata" (
        echo Found tessdata directory at %TESSERACT_PATH%\tessdata
        
        REM Check if German language pack exists
        if not exist "%TESSERACT_PATH%\tessdata\deu.traineddata" (
            echo German language pack not found. Downloading it...
            powershell -Command "& {$ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri 'https://github.com/tesseract-ocr/tessdata/raw/main/deu.traineddata' -OutFile '%TESSERACT_PATH%\tessdata\deu.traineddata'}" 
            if %ERRORLEVEL% NEQ 0 (
                echo Failed to download German language pack. 
                echo Please download it manually from https://github.com/tesseract-ocr/tessdata/raw/main/deu.traineddata
                echo and save it to %TESSERACT_PATH%\tessdata\deu.traineddata
            ) else (
                echo German language pack downloaded successfully.
            )
        ) else (
            echo German language pack already exists.
        )
    ) else (
        echo Creating tessdata directory...
        mkdir "%TESSERACT_PATH%\tessdata" 2>nul
        
        echo Downloading German language pack...
        powershell -Command "& {$ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri 'https://github.com/tesseract-ocr/tessdata/raw/main/deu.traineddata' -OutFile '%TESSERACT_PATH%\tessdata\deu.traineddata'}" 
        if %ERRORLEVEL% NEQ 0 (
            echo Failed to download German language pack.
            echo Please download it manually from https://github.com/tesseract-ocr/tessdata/raw/main/deu.traineddata
            echo and save it to %TESSERACT_PATH%\tessdata\deu.traineddata
        ) else (
            echo German language pack downloaded successfully.
        )
    )
    
    REM Create a path config file to ensure custom components can find Tesseract
    echo Creating configuration files...
    
    REM Add to PATH for current session
    set "PATH=%PATH%;%TESSERACT_PATH%"
    set "TESSDATA_PREFIX=%TESSERACT_PATH%\tessdata"
    
    echo SET PATH=%%PATH%%;%TESSERACT_PATH% > tesseract_path.bat
    echo SET TESSDATA_PREFIX=%TESSERACT_PATH%\tessdata >> tesseract_path.bat
    
    REM Update the virtual environment activation script
    if exist "langflow_venv\Scripts\activate.bat" (
        echo Updating virtual environment activation script...
        
        REM Check if Tesseract path already exists in activation script
        findstr /C:"%TESSERACT_PATH%" "langflow_venv\Scripts\activate.bat" > nul
        if %ERRORLEVEL% NEQ 0 (
            echo @echo off > langflow_venv\Scripts\activate.bat.tmp
            echo REM ===== BEGIN ORIGINAL ACTIVATE.BAT ===== >> langflow_venv\Scripts\activate.bat.tmp
            type langflow_venv\Scripts\activate.bat >> langflow_venv\Scripts\activate.bat.tmp
            echo REM ===== END ORIGINAL ACTIVATE.BAT ===== >> langflow_venv\Scripts\activate.bat.tmp
            echo. >> langflow_venv\Scripts\activate.bat.tmp
            echo REM Set Tesseract environment variables >> langflow_venv\Scripts\activate.bat.tmp
            echo set "PATH=%%PATH%%;%TESSERACT_PATH%" >> langflow_venv\Scripts\activate.bat.tmp
            echo set "TESSDATA_PREFIX=%TESSERACT_PATH%\tessdata" >> langflow_venv\Scripts\activate.bat.tmp
            move /Y langflow_venv\Scripts\activate.bat.tmp langflow_venv\Scripts\activate.bat > nul
            echo Activation script updated successfully.
        ) else (
            echo Tesseract already configured in activation script.
        )
    ) else (
        echo Virtual environment activation script not found.
    )
    
    echo.
    echo ========================================
    echo Tesseract OCR setup complete!
    echo.
    echo Path: %TESSERACT_PATH%
    echo Language data: %TESSERACT_PATH%\tessdata
    echo.
    echo To make the changes take effect in current window:
    echo call tesseract_path.bat
    echo ========================================
    
) else (
    echo.
    echo Tesseract not found. Please install it now.
    echo.
    
    echo 1. Download Tesseract installer:
    echo    https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.1.20230401.exe
    echo.
    echo 2. Install to:
    echo    %CD%\langflow_venv\tesseract
    echo.
    echo 3. After installation, run this script again.
    echo.
    
    set /p download_now="Do you want to download Tesseract installer now? (y/n): "
    if /i "%download_now%"=="y" (
        echo.
        echo Downloading Tesseract installer...
        
        if not exist "langflow_venv\tesseract" (
            mkdir "langflow_venv\tesseract" 2>nul
        )
        
        powershell -Command "& {$ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri 'https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.1.20230401.exe' -OutFile 'langflow_venv\tesseract\tesseract-installer.exe'}"
        
        if exist "langflow_venv\tesseract\tesseract-installer.exe" (
            echo Download complete.
            echo.
            echo Please run the installer at:
            echo %CD%\langflow_venv\tesseract\tesseract-installer.exe
            echo.
            echo Install it to:
            echo %CD%\langflow_venv\tesseract
            echo.
            echo After installation, run this script again.
            
            set /p run_installer="Do you want to run the installer now? (y/n): "
            if /i "%run_installer%"=="y" (
                start "" "langflow_venv\tesseract\tesseract-installer.exe"
            )
        ) else (
            echo Failed to download the installer.
            echo Please download it manually from:
            echo https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.1.20230401.exe
        )
    )
)

echo.
echo Press any key to exit...
pause > nul 