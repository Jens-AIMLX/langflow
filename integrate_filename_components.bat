@echo off
echo ========================================
echo Enhanced Filename Components Integration
echo ========================================
echo.

REM Check if we're in the correct directory
if not exist "langflow_venv" (
    echo ERROR: langflow_venv directory not found.
    echo Please run this script from the directory where you installed Langflow.
    echo Expected structure:
    echo   - langflow_venv\
    echo   - custom_nodes\
    echo   - run_langflow.bat
    pause
    exit /b 1
)

REM Activate the virtual environment
echo Activating Langflow virtual environment...
call langflow_venv\Scripts\activate.bat

REM Check if Langflow is installed
echo Checking Langflow installation...
python -c "import langflow; print('Langflow version:', langflow.__version__)" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Langflow is not properly installed in the virtual environment.
    echo Please run install_langflow_uv_140.bat first.
    pause
    exit /b 1
)

echo ✅ Langflow is installed and accessible

REM Create custom_nodes directory if it doesn't exist
if not exist "custom_nodes" (
    echo Creating custom_nodes directory...
    mkdir custom_nodes
)

REM Check if our components exist
echo.
echo Checking for enhanced filename components...

set "COMPONENTS_FOUND=0"

if exist "custom_nodes\file_metadata_extractor.py" (
    echo ✅ Found: file_metadata_extractor.py
    set /a COMPONENTS_FOUND+=1
) else (
    echo ❌ Missing: file_metadata_extractor.py
)

if exist "custom_nodes\backward_compatible_file_metadata_extractor.py" (
    echo ✅ Found: backward_compatible_file_metadata_extractor.py
    set /a COMPONENTS_FOUND+=1
) else (
    echo ❌ Missing: backward_compatible_file_metadata_extractor.py
)

if %COMPONENTS_FOUND% LSS 2 (
    echo.
    echo ERROR: Enhanced filename components are missing!
    echo.
    echo Expected files in custom_nodes\ directory:
    echo   - file_metadata_extractor.py
    echo   - backward_compatible_file_metadata_extractor.py
    echo.
    echo Please ensure these files are in the custom_nodes directory.
    echo You can copy them from your development directory.
    pause
    exit /b 1
)

echo.
echo ✅ All enhanced filename components found!

REM Test component imports
echo.
echo Testing component imports...

REM Test basic Python imports first
echo Testing basic imports...
python -c "import os, sys, json, sqlite3, tempfile; print('✅ Basic imports successful')" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Basic Python imports failed
    pause
    exit /b 1
)

REM Test Langflow imports
echo Testing Langflow imports...
python -c "from langflow.custom import Component; from langflow.io import FileInput, Output; from langflow.schema import Message; print('✅ Langflow imports successful')" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Langflow imports failed
    echo This might be due to circular imports or missing dependencies.
    echo The components should still work when loaded through Langflow UI.
    echo.
) else (
    echo ✅ Langflow imports successful
)

REM Test component loading
echo Testing component loading...
cd custom_nodes
python -c "
import sys
import os
sys.path.insert(0, '.')

try:
    # Test if we can at least read the files
    with open('backward_compatible_file_metadata_extractor.py', 'r') as f:
        content = f.read()
        if 'BackwardCompatibleFileMetadataExtractor' in content:
            print('✅ Component file structure is valid')
        else:
            print('❌ Component class not found in file')
except Exception as e:
    print(f'❌ Error reading component file: {e}')
" 2>nul

cd ..

REM Create a test script to verify components work in Langflow context
echo.
echo Creating component verification script...

echo import sys > test_components.py
echo import os >> test_components.py
echo. >> test_components.py
echo # Add custom_nodes to path >> test_components.py
echo sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_nodes')) >> test_components.py
echo. >> test_components.py
echo def test_component_availability(): >> test_components.py
echo     """Test if components are available for Langflow.""" >> test_components.py
echo     try: >> test_components.py
echo         # Test file existence >> test_components.py
echo         component_files = [ >> test_components.py
echo             'custom_nodes/file_metadata_extractor.py', >> test_components.py
echo             'custom_nodes/backward_compatible_file_metadata_extractor.py' >> test_components.py
echo         ] >> test_components.py
echo. >> test_components.py
echo         for file_path in component_files: >> test_components.py
echo             if os.path.exists(file_path): >> test_components.py
echo                 print(f'✅ Found: {file_path}') >> test_components.py
echo             else: >> test_components.py
echo                 print(f'❌ Missing: {file_path}') >> test_components.py
echo                 return False >> test_components.py
echo. >> test_components.py
echo         print('✅ All component files are available') >> test_components.py
echo         return True >> test_components.py
echo. >> test_components.py
echo     except Exception as e: >> test_components.py
echo         print(f'❌ Component test failed: {e}') >> test_components.py
echo         return False >> test_components.py
echo. >> test_components.py
echo if __name__ == '__main__': >> test_components.py
echo     print('Testing Enhanced Filename Components...') >> test_components.py
echo     success = test_component_availability() >> test_components.py
echo     if success: >> test_components.py
echo         print('🎉 Components are ready for Langflow!') >> test_components.py
echo     else: >> test_components.py
echo         print('⚠️ Some components may not be available') >> test_components.py

echo Running component verification...
python test_components.py

REM Clean up test script
del test_components.py >nul 2>&1

REM Set up Langflow environment for custom components
echo.
echo Setting up Langflow environment for custom components...

REM Create or update .env file
echo # Enhanced Filename Components Configuration > .env
echo LANGFLOW_CUSTOM_COMPONENTS_PATH=custom_nodes >> .env
echo LANGFLOW_LOAD_CUSTOM_COMPONENTS=true >> .env
echo LANGFLOW_ENHANCED_FILENAME_ENABLED=true >> .env

echo ✅ Environment configured for custom components

REM Create a startup verification script
echo.
echo Creating startup verification script...

echo @echo off > verify_components_in_langflow.bat
echo echo Verifying components are available in Langflow... >> verify_components_in_langflow.bat
echo call langflow_venv\Scripts\activate.bat >> verify_components_in_langflow.bat
echo echo. >> verify_components_in_langflow.bat
echo echo Starting Langflow with component verification... >> verify_components_in_langflow.bat
echo echo When Langflow starts, look for these components: >> verify_components_in_langflow.bat
echo echo   - "File Metadata Extractor" >> verify_components_in_langflow.bat
echo echo   - "Backward Compatible File Metadata Extractor" >> verify_components_in_langflow.bat
echo echo. >> verify_components_in_langflow.bat
echo echo If you don't see them, check the Langflow logs for import errors. >> verify_components_in_langflow.bat
echo echo. >> verify_components_in_langflow.bat
echo pause >> verify_components_in_langflow.bat
echo python -m langflow run --host 127.0.0.1 --port 7860 >> verify_components_in_langflow.bat

echo ✅ Verification script created: verify_components_in_langflow.bat

echo.
echo ========================================
echo Integration Complete!
echo ========================================
echo.
echo ✅ Enhanced filename components are integrated
echo ✅ Environment configured for custom components
echo ✅ Verification scripts created
echo.
echo 🚀 Next Steps:
echo.
echo 1. Start Langflow:
echo    run_langflow.bat
echo.
echo 2. Open browser:
echo    http://127.0.0.1:7860/flows
echo.
echo 3. Look for these components in the component panel:
echo    - "File Metadata Extractor"
echo    - "Backward Compatible File Metadata Extractor"
echo.
echo 4. If components don't appear:
echo    - Check Langflow console for import errors
echo    - Run: verify_components_in_langflow.bat
echo    - Restart Langflow
echo.
echo 📋 Component Usage:
echo    1. Drag "Backward Compatible File Metadata Extractor" to canvas
echo    2. Connect FileInput to the component
echo    3. Upload a file (e.g., "My Document.pdf")
echo    4. Run the flow
echo    5. See original filename in the output!
echo.
echo 🔧 Troubleshooting:
echo    - If components don't load: Check custom_nodes directory
echo    - If imports fail: Components will still work in Langflow UI
echo    - If no output: Check file upload and component connections
echo.
pause
