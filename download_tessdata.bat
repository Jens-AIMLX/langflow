@echo off
echo Downloading German language data for Tesseract OCR...

REM Create tessdata directory if it doesn't exist
if not exist "langflow_venv\tesseract\tessdata" mkdir "langflow_venv\tesseract\tessdata"

REM Download German language data
powershell -Command "& {$ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri 'https://github.com/tesseract-ocr/tessdata/raw/main/deu.traineddata' -OutFile 'langflow_venv\tesseract\tessdata\deu.traineddata'}"

if exist "langflow_venv\tesseract\tessdata\deu.traineddata" (
    echo German language data downloaded successfully to:
    echo %CD%\langflow_venv\tesseract\tessdata\deu.traineddata
) else (
    echo Failed to download German language data.
    echo Please download it manually from:
    echo https://github.com/tesseract-ocr/tessdata/raw/main/deu.traineddata
    echo And save it to: %CD%\langflow_venv\tesseract\tessdata\deu.traineddata
)

REM Set TESSDATA_PREFIX environment variable
set TESSDATA_PREFIX=%CD%\langflow_venv\tesseract\tessdata

echo.
echo TESSDATA_PREFIX set to: %TESSDATA_PREFIX%
echo.
echo Press any key to exit...
pause > nul 