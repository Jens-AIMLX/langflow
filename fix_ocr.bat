@echo off
echo ========================================
echo     TESSERACT LANGUAGE DATA FIX
echo ========================================
echo.

REM Create tessdata directory if it doesn't exist
echo Creating tessdata directory...
mkdir "langflow_venv\tesseract\tessdata" 2>nul

REM Download German language data directly using curl (usually available on Windows 10+)
echo Downloading German language data using curl...
curl -L -s -o "langflow_venv\tesseract\tessdata\deu.traineddata" "https://github.com/tesseract-ocr/tessdata/raw/main/deu.traineddata"

REM Check if the download was successful
if exist "langflow_venv\tesseract\tessdata\deu.traineddata" (
    echo German language data downloaded successfully!
) else (
    echo Failed to download with curl. Trying with bitsadmin...
    
    REM Try using bitsadmin (Windows built-in)
    bitsadmin /transfer "DownloadTessdata" "https://github.com/tesseract-ocr/tessdata/raw/main/deu.traineddata" "%CD%\langflow_venv\tesseract\tessdata\deu.traineddata" >nul
    
    if exist "langflow_venv\tesseract\tessdata\deu.traineddata" (
        echo German language data downloaded successfully with bitsadmin!
    ) else (
        echo Failed to download automatically.
        echo.
        echo Please download the file manually from:
        echo https://github.com/tesseract-ocr/tessdata/raw/main/deu.traineddata
        echo.
        echo Save it to: %CD%\langflow_venv\tesseract\tessdata\deu.traineddata
        
        set /p manual_download="Would you like to open the download URL in your browser? (y/n): "
        if /i "%manual_download%"=="y" (
            start "" "https://github.com/tesseract-ocr/tessdata/raw/main/deu.traineddata"
            echo Please save the file to: %CD%\langflow_venv\tesseract\tessdata\deu.traineddata
            echo Press any key after saving the file...
            pause >nul
        )
    )
)

REM Configure environment variables
echo.
echo Setting environment variables...
set "TESSDATA_PREFIX=%CD%\langflow_venv\tesseract\tessdata"
echo TESSDATA_PREFIX=%TESSDATA_PREFIX%

REM Create a batch file to set these variables
echo set TESSDATA_PREFIX=%TESSDATA_PREFIX% > set_tessdata_prefix.bat

REM Update virtual environment activation script
if exist "langflow_venv\Scripts\activate.bat" (
    echo Updating virtual environment activation script...
    
    REM Check if TESSDATA_PREFIX already exists in activation script
    findstr /C:"TESSDATA_PREFIX" "langflow_venv\Scripts\activate.bat" >nul
    if errorlevel 1 (
        echo set "TESSDATA_PREFIX=%CD%\langflow_venv\tesseract\tessdata" >> "langflow_venv\Scripts\activate.bat"
        echo Activation script updated.
    ) else (
        echo Activation script already contains TESSDATA_PREFIX.
    )
)

echo.
echo ========================================
echo Setup complete!
echo.
echo To use Tesseract OCR in the current window:
echo    call set_tessdata_prefix.bat
echo.
echo Next time you start Langflow, the variables will be set automatically.
echo ========================================
echo.
echo Press any key to exit...
pause >nul 