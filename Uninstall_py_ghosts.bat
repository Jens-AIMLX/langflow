@echo off
setlocal enabledelayedexpansion

:: ======================================================
:: Python 3.12 (32-bit) Registry GUID Cleaner
:: ======================================================

:: Elevate to admin if not already
openfiles >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting administrative privileges...
    set "PSExec=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"
    "%PSExec%" -NoProfile -Command "Start-Process '%~f0' -Verb runAs"
    exit /b
)

echo =====================================================
echo Python 3.12 (32-bit) Registry GUID Cleaner
echo This will locate and remove ALL registry keys containing
echo the Python installation GUIDs
echo =====================================================

:: Terminating all Python processes
echo Terminating Python processes...
taskkill /F /IM msiexec.exe /T >nul 2>&1
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM pythonw.exe /T >nul 2>&1
taskkill /F /IM py.exe /T >nul 2>&1
taskkill /F /IM pip.exe /T >nul 2>&1
echo Done.

:: Dynamically retrieve GUIDs for Python 3.12 (32-bit) using PowerShell
set "GUIDS="
for /f "usebackq tokens=*" %%G in (`powershell -NoProfile -Command "Get-WmiObject -Class Win32_Product | Where-Object { $_.Name -match 'Python 3\.12.*\(32-bit\)' } | Select-Object -ExpandProperty IdentifyingNumber"`) do (
    set "GUIDS=!GUIDS! %%G"
)
:: GUIDS now contains all relevant IdentifyingNumbers (GUIDs) for installed Python 3.12 (32-bit) products

:: Create a temporary file to export registry search results
set "TEMP_FILE=%TEMP%\py_reg_search.txt"
echo. > "%TEMP_FILE%"

echo Searching registry for Python GUID entries...
echo (This may take a while)

:: Main registry search function
for %%G in (%GUIDS%) do (
    echo Searching for GUID: %%G
    
    :: Search in HKLM - both with and without braces
    reg query "HKLM" /f "%%G" /s > "%TEMP_FILE%_%%G.txt" 2>nul
    reg query "HKLM" /f "{%%G}" /s >> "%TEMP_FILE%_%%G.txt" 2>nul
    
    :: Search in HKCU - both with and without braces
    reg query "HKCU" /f "%%G" /s >> "%TEMP_FILE%_%%G.txt" 2>nul
    reg query "HKCU" /f "{%%G}" /s >> "%TEMP_FILE%_%%G.txt" 2>nul
    
    :: Process and delete found keys
    for /f "tokens=*" %%R in ('type "%TEMP_FILE%_%%G.txt" ^| findstr /i "HKEY_"') do (
        echo Found key: %%R
        
        :: Convert to reg delete format
        set "regpath=%%R"
        set "regpath=!regpath:HKEY_LOCAL_MACHINE=HKLM!"
        set "regpath=!regpath:HKEY_CURRENT_USER=HKCU!"
        
        echo Deleting: !regpath!
        reg delete "!regpath!" /f >nul 2>&1
        
        if !errorlevel! equ 0 (
            echo [SUCCESS] Key deleted
        ) else (
            echo [WARNING] Could not delete key, attempting again with specific access...
            
            :: Try with different access modes
            reg delete "!regpath!" /f /reg:64 >nul 2>&1 && echo [SUCCESS] Key deleted with /reg:64 || echo [FAILED] Could not delete with /reg:64
            reg delete "!regpath!" /f /reg:32 >nul 2>&1 && echo [SUCCESS] Key deleted with /reg:32 || echo [FAILED] Could not delete with /reg:32
        )
        echo.
    )
    
    :: Clean up temp file
    del "%TEMP_FILE%_%%G.txt" >nul 2>&1
)

:: Extra: Check Installer registry subkeys that contain Python references
echo Checking Windows Installer database entries...
for %%P in (
    "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Installer\UserData\S-1-5-18\Products"
    "HKLM\SOFTWARE\Classes\Installer\Products"
) do (
    echo Scanning %%P for Python entries...
    
    :: Export the Products key structure to find Python entries
    reg export %%P "%TEMP_FILE%_products.reg" >nul 2>&1
    
    :: Search for Python in the export
    findstr /i "Python" "%TEMP_FILE%_products.reg" > "%TEMP_FILE%_found.txt"
    
    :: Extract key paths that have Python and contain any of the GUIDs
    for /f "tokens=1 delims=:" %%K in ('findstr /i /n "\[" "%TEMP_FILE%_products.reg"') do (
        set /a next=%%K+1
        
        :: Get the key name
        set "line="
        for /f "tokens=*" %%L in ('type "%TEMP_FILE%_products.reg" ^| findstr /n "^" ^| findstr "^%%K:"') do (
            set "line=%%L"
        )
        set "line=!line:*:=!"
        set "keyname=!line!"
        
        :: Check if current key has Python
        set "hasPython=0"
        set "endOfKey=0"
        for /f "tokens=1 delims=:" %%M in ('findstr /i /n "Python" "%TEMP_FILE%_products.reg"') do (
            if %%M gtr %%K (
                if !endOfKey! equ 0 (
                    for /f "tokens=1 delims=:" %%N in ('findstr /i /n "\[" "%TEMP_FILE%_products.reg"') do (
                        if %%N gtr %%K (
                            if %%M lss %%N (
                                set "hasPython=1"
                            )
                            if !endOfKey! equ 0 set "endOfKey=%%N"
                        )
                    )
                )
            )
        )
        
        :: If has Python, check for GUIDs
        if !hasPython! equ 1 (
            echo Found potential Python registry key: !keyname!
            set "hasGUID=0"
            
            for %%G in (%GUIDS%) do (
                findstr /i "%%G" "%TEMP_FILE%_products.reg" | findstr /i "!keyname!" >nul 2>&1
                if !errorlevel! equ 0 (
                    set "hasGUID=1"
                    echo Found GUID %%G in key !keyname!
                )
            )
            
            if !hasGUID! equ 1 (
                :: Extract the key path properly
                set "keypath=!keyname!"
                set "keypath=!keypath:\[=!"
                set "keypath=!keypath:\]=!"
                
                echo Attempting to delete: !keypath!
                reg delete "!keypath!" /f >nul 2>&1
                
                if !errorlevel! equ 0 (
                    echo [SUCCESS] Installer key deleted
                ) else (
                    echo [WARNING] Could not delete installer key, trying alternatives...
                    reg delete "!keypath!" /f /reg:64 >nul 2>&1 && echo [SUCCESS] Key deleted with /reg:64 || echo [FAILED] Could not delete with /reg:64
                    reg delete "!keypath!" /f /reg:32 >nul 2>&1 && echo [SUCCESS] Key deleted with /reg:32 || echo [FAILED] Could not delete with /reg:32
                )
                echo.
            )
        )
    )
    
    :: Clean up temp files
    del "%TEMP_FILE%_products.reg" >nul 2>&1 
    del "%TEMP_FILE%_found.txt" >nul 2>&1
)

:: Final cleanup of commonly problematic keys
echo Directly removing known problematic registry locations...
for %%G in (%GUIDS%) do (
    :: Remove with and without braces from multiple locations
    for %%F in ("{%%G}" "%%G") do (
        reg delete "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\%%F" /f >nul 2>&1
        reg delete "HKLM\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\%%F" /f >nul 2>&1
        reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\%%F" /f >nul 2>&1
    )
)

:: Remove Python top-level keys
echo Removing Python root registry keys...
reg delete "HKLM\SOFTWARE\Python" /f >nul 2>&1
reg delete "HKLM\SOFTWARE\WOW6432Node\Python" /f >nul 2>&1
reg delete "HKCU\SOFTWARE\Python" /f >nul 2>&1

:: Clean up any leftover install directories
echo Cleaning installation directories...
if exist "%ProgramFiles(x86)%\Python3.12-32" rmdir /s /q "%ProgramFiles(x86)%\Python3.12-32" >nul 2>&1
if exist "%ProgramFiles%\Python3.12-32" rmdir /s /q "%ProgramFiles%\Python3.12-32" >nul 2>&1
if exist "%LocalAppData%\Programs\Python\Python3.12-32" rmdir /s /q "%LocalAppData%\Programs\Python\Python3.12-32" >nul 2>&1

echo =====================================================
echo Cleanup complete! 
echo A system restart is recommended to complete the process.
echo If entries still appear, please try a restart first.
echo =====================================================
pause
