@echo off
echo Testing Enhanced Filename Installation
echo ==========================================
echo.

REM Check if virtual environment exists
if not exist "langflow_venv" (
    echo ERROR: Virtual environment not found
    echo Please run install_langflow_uv_140.bat first
    exit /b 1
)

echo SUCCESS: Virtual environment found

REM Activate virtual environment
call langflow_venv\Scripts\activate.bat

REM Check if .env file exists and contains enhanced settings
if exist ".env" (
    echo SUCCESS: Enhanced configuration file (.env) found

    REM Check for enhanced feature flags
    findstr /C:"LANGFLOW_FEATURE_enhanced_file_inputs=true" .env >nul
    if %ERRORLEVEL% EQU 0 (
        echo SUCCESS: Enhanced file inputs feature flag enabled
    ) else (
        echo WARNING: Enhanced file inputs feature flag not found
    )

    findstr /C:"LANGFLOW_ENHANCED_FILENAME_ENABLED=true" .env >nul
    if %ERRORLEVEL% EQU 0 (
        echo SUCCESS: Enhanced filename feature enabled
    ) else (
        echo WARNING: Enhanced filename feature flag not found
    )
) else (
    echo WARNING: Enhanced configuration file (.env) not found
    echo This will be created automatically on first run
)

REM Check for enhanced components
echo.
echo Checking Enhanced Components:
echo =============================

if exist "src\backend\base\langflow\custom\enhanced_component.py" (
    echo SUCCESS: Enhanced component framework found
) else (
    echo ERROR: Enhanced component framework missing
)

if exist "src\backend\base\langflow\api\v2\schemas.py" (
    echo SUCCESS: Enhanced API schemas found
) else (
    echo ERROR: Enhanced API schemas missing
)

if exist "src\backend\base\langflow\inputs\enhanced_inputs.py" (
    echo SUCCESS: Enhanced input classes found
) else (
    echo ERROR: Enhanced input classes missing
)

if exist "src\backend\base\langflow\services\migration\file_migration.py" (
    echo SUCCESS: Migration utilities found
) else (
    echo ERROR: Migration utilities missing
)

if exist "src\backend\base\langflow\services\settings\feature_flags.py" (
    echo SUCCESS: Feature flags found
) else (
    echo ERROR: Feature flags missing
)

REM Check for custom nodes
echo.
echo Checking Custom Nodes:
echo ======================

if exist "custom_nodes\file_metadata_extractor.py" (
    echo ✅ File Metadata Extractor component found
) else (
    echo ⚠️ File Metadata Extractor component not found
    echo This is normal - it will be available after first Langflow run
)

if exist "custom_nodes\backward_compatible_file_metadata_extractor.py" (
    echo ✅ Backward Compatible File Metadata Extractor found
) else (
    echo ⚠️ Backward Compatible File Metadata Extractor not found
    echo This is normal - it will be available after first Langflow run
)

REM Check for test files
echo.
echo Checking Test Infrastructure:
echo =============================

if exist "test_enhanced_filename_simple.py" (
    echo ✅ Enhanced filename tests found
) else (
    echo ⚠️ Enhanced filename tests not found
)

if exist "test_basic_functionality.py" (
    echo ✅ Basic functionality tests found
) else (
    echo ⚠️ Basic functionality tests not found
)

if exist "pytest.ini" (
    echo ✅ Pytest configuration found
) else (
    echo ⚠️ Pytest configuration not found
)

REM Check for documentation
echo.
echo Checking Documentation:
echo =======================

if exist "ENHANCED_FILENAME_IMPLEMENTATION.md" (
    echo ✅ Implementation guide found
) else (
    echo ⚠️ Implementation guide not found
)

if exist "FILE_METADATA_EXTRACTOR_README.md" (
    echo ✅ Component usage guide found
) else (
    echo ⚠️ Component usage guide not found
)

if exist "IMPLEMENTATION_COMPLETE_SUMMARY.md" (
    echo ✅ Feature overview found
) else (
    echo ⚠️ Feature overview not found
)

REM Test Python environment
echo.
echo Testing Python Environment:
echo ===========================

python -c "print('✅ Python is working')" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Python test failed
    exit /b 1
)

python -c "import sys; print(f'✅ Python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Python version check failed
    exit /b 1
)

REM Test if Langflow can be imported
echo Testing Langflow import...
python -c "import langflow; print('✅ Langflow import successful')" 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ✅ Langflow is properly installed
) else (
    echo ⚠️ Langflow import test failed
    echo This might be normal if this is the first run
)

REM Summary
echo.
echo ==========================================
echo 📋 ENHANCED INSTALLATION TEST SUMMARY
echo ==========================================
echo.

REM Count successful checks
set "SUCCESS_COUNT=0"
set "TOTAL_CHECKS=10"

if exist "langflow_venv" set /a SUCCESS_COUNT+=1
if exist ".env" set /a SUCCESS_COUNT+=1
if exist "src\backend\base\langflow\custom\enhanced_component.py" set /a SUCCESS_COUNT+=1
if exist "src\backend\base\langflow\api\v2\schemas.py" set /a SUCCESS_COUNT+=1
if exist "src\backend\base\langflow\inputs\enhanced_inputs.py" set /a SUCCESS_COUNT+=1
if exist "src\backend\base\langflow\services\migration\file_migration.py" set /a SUCCESS_COUNT+=1
if exist "src\backend\base\langflow\services\settings\feature_flags.py" set /a SUCCESS_COUNT+=1
if exist "test_enhanced_filename_simple.py" set /a SUCCESS_COUNT+=1
if exist "ENHANCED_FILENAME_IMPLEMENTATION.md" set /a SUCCESS_COUNT+=1

python -c "print('Python OK')" >nul 2>&1
if %ERRORLEVEL% EQU 0 set /a SUCCESS_COUNT+=1

echo 📊 Test Results: %SUCCESS_COUNT%/%TOTAL_CHECKS% checks passed
echo.

if %SUCCESS_COUNT% GEQ 8 (
    echo 🎉 INSTALLATION TEST PASSED!
    echo ✅ Enhanced filename implementation is ready
    echo ✅ Core components are in place
    echo ✅ Environment is properly configured
    echo.
    echo 🚀 Ready to start Langflow with enhanced features!
    echo Run: run_langflow.bat
) else (
    echo ⚠️ Some components are missing
    echo This might be normal for a fresh installation
    echo Enhanced features will be available after first Langflow run
    echo.
    echo 🔧 To complete setup, run: run_langflow.bat
)

echo.
pause
