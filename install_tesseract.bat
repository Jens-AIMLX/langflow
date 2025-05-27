@echo off
echo ========================================
echo     TESSERACT OCR INSTALLATION TOOL
echo ========================================
echo.

REM Define installation directory
set "INSTALL_DIR=%CD%\langflow_venv\tesseract"
echo Installation directory: %INSTALL_DIR%

REM Check if Tesseract is already installed somewhere
set "TESSERACT_FOUND=0"
set "TESSERACT_PATH="

echo Checking for existing Tesseract installations...

REM Check common installation paths
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
) else if exist "%INSTALL_DIR%\tesseract.exe" (
    set "TESSERACT_FOUND=1"
    set "TESSERACT_PATH=%INSTALL_DIR%"
    echo Found Tesseract at %TESSERACT_PATH%
)

REM Check PATH for tesseract
where tesseract 2>nul
if %ERRORLEVEL% EQU 0 (
    for /f "tokens=*" %%a in ('where tesseract') do (
        set "TESSERACT_FOUND=1"
        set "TESSERACT_PATH=%%~dpa"
        echo Found Tesseract in PATH at %%a
    )
)

if "%TESSERACT_FOUND%"=="1" (
    echo.
    echo Tesseract is already installed. Configuring environment...

    REM Download German language data if needed
    set "TESSDATA_DIR=%TESSERACT_PATH%\tessdata"
    if not exist "%TESSDATA_DIR%" (
        mkdir "%TESSDATA_DIR%"
        echo Created tessdata directory.
    )

    if not exist "%TESSDATA_DIR%\deu.traineddata" (
        echo Downloading German language data...
        powershell -Command "& {$ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri 'https://github.com/tesseract-ocr/tessdata/raw/main/deu.traineddata' -OutFile '%TESSDATA_DIR%\deu.traineddata'}"
        
        if exist "%TESSDATA_DIR%\deu.traineddata" (
            echo German language data downloaded successfully.
        ) else (
            echo Failed to download German language data.
            echo You can manually download it from:
            echo https://github.com/tesseract-ocr/tessdata/raw/main/deu.traineddata
            echo And save it to: %TESSDATA_DIR%\deu.traineddata
        )
    ) else (
        echo German language data already exists.
    )

    REM Add to PATH for current session
    set "PATH=%PATH%;%TESSERACT_PATH%"
    set "TESSDATA_PREFIX=%TESSDATA_DIR%"

    echo Added Tesseract to PATH for current session.
    echo TESSDATA_PREFIX set to %TESSDATA_PREFIX%

    REM Create a path file for the current session
    echo set PATH=%%PATH%%;%TESSERACT_PATH% > tesseract_path.bat
    echo set TESSDATA_PREFIX=%TESSDATA_DIR% >> tesseract_path.bat
    
    REM Update the virtual environment activate script
    if exist "langflow_venv\Scripts\activate.bat" (
        findstr /C:"tesseract" "langflow_venv\Scripts\activate.bat" > nul
        if errorlevel 1 (
            echo Adding Tesseract to virtual environment activation script...
            
            echo @echo off > langflow_venv\Scripts\activate.bat.tmp
            echo REM ===== BEGIN ORIGINAL ACTIVATE.BAT ===== >> langflow_venv\Scripts\activate.bat.tmp
            type langflow_venv\Scripts\activate.bat >> langflow_venv\Scripts\activate.bat.tmp
            echo REM ===== END ORIGINAL ACTIVATE.BAT ===== >> langflow_venv\Scripts\activate.bat.tmp
            echo. >> langflow_venv\Scripts\activate.bat.tmp
            echo REM Set Tesseract environment variables >> langflow_venv\Scripts\activate.bat.tmp
            echo set "PATH=%%PATH%%;%TESSERACT_PATH%" >> langflow_venv\Scripts\activate.bat.tmp
            echo set "TESSDATA_PREFIX=%TESSDATA_DIR%" >> langflow_venv\Scripts\activate.bat.tmp
            move /Y langflow_venv\Scripts\activate.bat.tmp langflow_venv\Scripts\activate.bat > nul
            
            echo Activation script updated successfully.
        ) else (
            echo Tesseract already configured in activation script.
        )
    ) else (
        echo Virtual environment activation script not found.
        echo You'll need to manually add Tesseract to your PATH.
    )
    
    goto :test_tesseract
) else (
    echo Tesseract not found. Beginning installation...
)

if not exist "%INSTALL_DIR%" (
    mkdir "%INSTALL_DIR%"
    echo Created installation directory.
) else (
    echo Installation directory already exists.
)

REM Download Tesseract installer
echo.
echo Step 1: Downloading Tesseract OCR installer...
echo.

set "INSTALLER=%INSTALL_DIR%\tesseract-installer.exe"
set "DOWNLOAD_URL=https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.1.20230401.exe"

powershell -Command "& {Write-Host 'Downloading from %DOWNLOAD_URL%'; $ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri '%DOWNLOAD_URL%' -OutFile '%INSTALLER%'}"

if not exist "%INSTALLER%" (
    echo Failed to download Tesseract installer.
    echo Please download it manually from:
    echo %DOWNLOAD_URL%
    echo And save it to: %INSTALLER%
    
    set /p manual_download="Would you like to open the download page in your browser? (y/n): "
    if /i "%manual_download%"=="y" (
        start "" "%DOWNLOAD_URL%"
    )
    
    pause
    exit /b 1
)

echo Download completed successfully.

REM Install Tesseract
echo.
echo Step 2: Installing Tesseract OCR...
echo This might take a few minutes...
echo.

echo Running installer with destination: %INSTALL_DIR%
echo You may need to click through the installer. Please choose:
echo - German language during installation
echo - Install to: %INSTALL_DIR%
start /wait "" "%INSTALLER%" /S /D=%INSTALL_DIR%

timeout /t 10 /nobreak > nul

REM Wait for installation to complete
set /p proceed="Has the installation completed? (y/n): "
if /i not "%proceed%"=="y" (
    echo Please complete the installation and then press 'y' to continue.
    pause
)

if not exist "%INSTALL_DIR%\tesseract.exe" (
    echo.
    echo WARNING: Tesseract executable not found after installation.
    echo This could indicate that the installation failed.
    echo.
    echo You may need to manually install Tesseract:
    echo 1. Run the installer at: %INSTALLER%
    echo 2. Choose to install to: %INSTALL_DIR%
    echo.
    set /p manual_install="Would you like to open the installer manually now? (y/n): "
    if /i "%manual_install%"=="y" (
        start "" "%INSTALLER%"
        echo Please select %INSTALL_DIR% as the installation directory.
        echo After installation completes, press any key to continue...
        pause > nul
    )
)

REM Download language data
echo.
echo Step 3: Downloading language data (German)...
echo.

set "TESSDATA_DIR=%INSTALL_DIR%\tessdata"
if not exist "%TESSDATA_DIR%" (
    mkdir "%TESSDATA_DIR%"
    echo Created tessdata directory.
)

powershell -Command "& {$ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri 'https://github.com/tesseract-ocr/tessdata/raw/main/deu.traineddata' -OutFile '%TESSDATA_DIR%\deu.traineddata'}"

if exist "%TESSDATA_DIR%\deu.traineddata" (
    echo German language data downloaded successfully.
) else (
    echo Failed to download German language data.
    echo You can manually download it from:
    echo https://github.com/tesseract-ocr/tessdata/raw/main/deu.traineddata
    echo And save it to: %TESSDATA_DIR%\deu.traineddata
)

REM Set up environment variables
echo.
echo Step 4: Setting up environment variables...
echo.

REM Add to PATH for current session
set "PATH=%PATH%;%INSTALL_DIR%"
set "TESSDATA_PREFIX=%TESSDATA_DIR%"

echo Tesseract added to PATH for current session.
echo TESSDATA_PREFIX set to %TESSDATA_PREFIX%

REM Create a path file for the current session
echo set PATH=%%PATH%%;%INSTALL_DIR% > tesseract_path.bat
echo set TESSDATA_PREFIX=%TESSDATA_DIR% >> tesseract_path.bat

REM Update the virtual environment activate script
if exist "langflow_venv\Scripts\activate.bat" (
    findstr /C:"tesseract" "langflow_venv\Scripts\activate.bat" > nul
    if errorlevel 1 (
        echo Adding Tesseract to virtual environment activation script...
        
        echo @echo off > langflow_venv\Scripts\activate.bat.tmp
        echo REM ===== BEGIN ORIGINAL ACTIVATE.BAT ===== >> langflow_venv\Scripts\activate.bat.tmp
        type langflow_venv\Scripts\activate.bat >> langflow_venv\Scripts\activate.bat.tmp
        echo REM ===== END ORIGINAL ACTIVATE.BAT ===== >> langflow_venv\Scripts\activate.bat.tmp
        echo. >> langflow_venv\Scripts\activate.bat.tmp
        echo REM Set Tesseract environment variables >> langflow_venv\Scripts\activate.bat.tmp
        echo set "PATH=%%PATH%%;%INSTALL_DIR%" >> langflow_venv\Scripts\activate.bat.tmp
        echo set "TESSDATA_PREFIX=%TESSDATA_DIR%" >> langflow_venv\Scripts\activate.bat.tmp
        move /Y langflow_venv\Scripts\activate.bat.tmp langflow_venv\Scripts\activate.bat > nul
        
        echo Activation script updated successfully.
    ) else (
        echo Tesseract already configured in activation script.
    )
) else (
    echo Virtual environment activation script not found.
    echo You'll need to manually add Tesseract to your PATH.
)

:test_tesseract
REM Test Tesseract installation
echo.
echo Step 5: Testing Tesseract installation...
echo.

set test_failed=0

REM Determine which Tesseract path to use
if "%TESSERACT_FOUND%"=="1" (
    set "TEST_PATH=%TESSERACT_PATH%\tesseract.exe"
) else (
    set "TEST_PATH=%INSTALL_DIR%\tesseract.exe"
)

echo Testing %TEST_PATH%...
"%TEST_PATH%" --version > tesseract_test.txt 2>&1
type tesseract_test.txt
findstr /C:"tesseract" tesseract_test.txt > nul
if errorlevel 1 (
    echo FAILED: Tesseract not responding to version command.
    set test_failed=1
) else (
    echo OK: Tesseract executable is working.
)

echo.
echo Testing language data...
"%TEST_PATH%" --list-langs > langs_test.txt 2>&1
type langs_test.txt
findstr /C:"deu" langs_test.txt > nul
if errorlevel 1 (
    echo FAILED: German language data not detected.
    set test_failed=1
) else (
    echo OK: German language data is available.
)

del tesseract_test.txt langs_test.txt > nul 2>&1

echo.
if %test_failed%==1 (
    echo Some tests failed. Tesseract may not be fully functional.
    echo Please see the log above for details.
) else (
    echo All tests passed! Tesseract is properly installed.
)

echo.
echo ========================================
echo Installation Summary:
echo ========================================
echo.
if "%TESSERACT_FOUND%"=="1" (
    echo Using existing Tesseract at: %TESSERACT_PATH%
) else (
    echo Tesseract executable: %INSTALL_DIR%\tesseract.exe
)
echo Language data: %TESSDATA_DIR%
echo.
echo IMPORTANT: To use Tesseract in the current command prompt:
echo   call tesseract_path.bat
echo.
echo If you restart Langflow, it will automatically detect Tesseract.
echo ========================================

echo.
echo Press any key to exit...
pause > nul 