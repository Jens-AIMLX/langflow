# Requires -RunAsAdministrator

# Python 3.12.10 (32-bit) GUIDs to remove
$pythonGUIDs = @(
    "{D7A39801-C8C5-4899-B280-A3C0508A92D1}",
    "{30BCE321-E857-4022-A79B-FD611958DA05}",
    "{4B1491F1-E78B-412B-8768-125E196F6983}",
    "{A4D35316-E413-4CBF-A3CC-3363832D5714}",
    "{69427B1B-D6CD-4041-A912-8F92AE35BE5E}",
    "{9B0E77EB-2D43-48CF-980A-F04559AF8DF0}",
    "{7156BA5D-D7C5-4A22-8B19-6EE15A4E07D7}",
    "{D16977AD-7BC4-40B8-9874-114E21F43810}",
    "{BE47ECAD-93A9-403C-991F-20A8CCD2562D}"
)

Write-Host "Starting aggressive removal of Python 3.12.10 (32-bit) ghost installations..." -ForegroundColor Cyan
Write-Host "This script will attempt multiple methods to remove these entries." -ForegroundColor Yellow

# APPROACH 1: Direct WMI removal using the real source of Programs and Features entries
Write-Host "`n== APPROACH 1: Direct WMI removal ==" -ForegroundColor Magenta
try {
    Write-Host "Searching for Python components in WMI database..." -ForegroundColor Cyan
    
    # Get all Python components from WMI
    $pythonProducts = Get-WmiObject -Class Win32_Product | Where-Object { 
        $_.Name -like "*Python 3.12*32-bit*" -or 
        $_.IdentifyingNumber -in $pythonGUIDs 
    }
    
    if ($pythonProducts) {
        Write-Host "Found $(($pythonProducts | Measure-Object).Count) Python component(s) in WMI" -ForegroundColor Green
        
        foreach ($product in $pythonProducts) {
            Write-Host "Uninstalling: $($product.Name) [GUID: $($product.IdentifyingNumber)]" -ForegroundColor Yellow
            try {
                $result = $product.Uninstall()
                if ($result.ReturnValue -eq 0) {
                    Write-Host "Successfully uninstalled via WMI" -ForegroundColor Green
                } else {
                    Write-Host "WMI uninstall returned code: $($result.ReturnValue)" -ForegroundColor Red
                }
            } catch {
                Write-Host "Error during WMI uninstall: $_" -ForegroundColor Red
            }
        }
    } else {
        Write-Host "No Python components found in WMI" -ForegroundColor Yellow
    }
} catch {
    Write-Host "Error accessing WMI: $_" -ForegroundColor Red
}

# APPROACH 2: Direct Registry Cleanup for ARP (Add/Remove Programs) entries
Write-Host "`n== APPROACH 2: Direct Registry Cleanup of ARP entries ==" -ForegroundColor Magenta

# All possible registry locations for Programs and Features entries
$uninstallKeys = @(
    "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
    "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
)

foreach ($keyPath in $uninstallKeys) {
    if (Test-Path $keyPath) {
        Write-Host "Searching in $keyPath..." -ForegroundColor Cyan
        
        $subKeys = Get-ChildItem -Path $keyPath
        
        foreach ($subKey in $subKeys) {
            $displayName = (Get-ItemProperty -Path $subKey.PSPath -ErrorAction SilentlyContinue).DisplayName
            $displayVersion = (Get-ItemProperty -Path $subKey.PSPath -ErrorAction SilentlyContinue).DisplayVersion
            
            # Check if this is a Python 3.12.10 (32-bit) component
            if ($displayName -like "*Python 3.12.10*32-bit*") {
                Write-Host "Found ARP entry: $displayName v$displayVersion at $($subKey.PSPath)" -ForegroundColor Green
                
                # Aggressive direct registry removal
                try {
                    Remove-Item -Path $subKey.PSPath -Recurse -Force -ErrorAction Stop
                    Write-Host "Successfully removed entry from registry" -ForegroundColor Green
                } catch {
                    Write-Host "Error removing registry key: $_" -ForegroundColor Red
                }
            }
        }
    } else {
        Write-Host "Registry path not found: $keyPath" -ForegroundColor Yellow
    }
}

# APPROACH 3: Manipulate MsiServer directly with deeper GUID formats
Write-Host "`n== APPROACH 3: Direct MSI Database Manipulation ==" -ForegroundColor Magenta

# Check and clean all possible MSI registration paths
$msiDBPaths = @(
    "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Installer\UserData\S-1-5-18\Products",
    "HKLM:\SOFTWARE\Classes\Installer\Products",
    "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Installer\UpgradeCodes",
    "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Installer\Products"
)

foreach ($msiPath in $msiDBPaths) {
    if (Test-Path $msiPath) {
        Write-Host "Searching in $msiPath..." -ForegroundColor Cyan
        
        try {
            $products = Get-ChildItem -Path $msiPath -ErrorAction SilentlyContinue
            foreach ($product in $products) {
                # Look for any registry values related to Python 3.12
                $productProps = Get-ItemProperty -Path $product.PSPath -ErrorAction SilentlyContinue
                
                $isPythonComponent = $false
                
                # Check all property values for strings containing Python 3.12
                foreach ($prop in $productProps.PSObject.Properties) {
                    if ($prop.Value -is [string] -and $prop.Value -like "*Python 3.12*") {
                        $isPythonComponent = $true
                        break
                    }
                }
                
                # If we found a Python component or the key name is a reordered GUID we're looking for
                if ($isPythonComponent) {
                    Write-Host "Found MSI DB entry: $($product.PSPath)" -ForegroundColor Green
                    # Aggressive direct registry removal
                    try {
                        Remove-Item -Path $product.PSPath -Recurse -Force -ErrorAction Stop
                        Write-Host "Successfully removed entry from MSI database" -ForegroundColor Green
                    } catch {
                        Write-Host "Error removing MSI DB key: $_" -ForegroundColor Red
                    }
                }
            }
        } catch {
            Write-Host "Error processing $msiPath : $_" -ForegroundColor Red
        }
    }
}

# APPROACH 4: Specific direct registry removal based on display names
Write-Host "`n== APPROACH 4: Direct registry removal by display name ==" -ForegroundColor Magenta

# Components to find by display name
$componentDisplayNames = @(
    "Python 3.12.10 Core Interpreter (32-bit)",
    "Python 3.12.10 Documentation (32-bit)",
    "Python 3.12.10 Standard Library (32-bit)",
    "Python 3.12.10 pip Bootstrap (32-bit)",
    "Python 3.12.10 Executables (32-bit)",
    "Python 3.12.10 Test Suite (32-bit)",
    "Python 3.12.10 Development Libraries (32-bit)",
    "Python 3.12.10 Add to Path (32-bit)",
    "Python 3.12.10 Tcl/Tk Support (32-bit)"
)

# Function to search deeper in registry for values
function Search-RegistryValueDeep {
    param (
        [Parameter(Mandatory=$true)]
        [string]$RootKey,
        
        [Parameter(Mandatory=$true)]
        [string]$SearchText,
        
        [int]$MaxDepth = 3,
        
        [int]$CurrentDepth = 0
    )
    
    if ($CurrentDepth -ge $MaxDepth) { return }
    
    try {
        $subKeys = Get-ChildItem -Path $RootKey -ErrorAction SilentlyContinue
        
        foreach ($key in $subKeys) {
            # Get all properties in this key
            $props = Get-ItemProperty -Path $key.PSPath -ErrorAction SilentlyContinue
            
            $found = $false
            
            # Check all string values
            foreach ($prop in $props.PSObject.Properties) {
                if ($prop.Value -is [string] -and $prop.Value -like "*$SearchText*") {
                    Write-Host "Found match: $($prop.Value) at $($key.PSPath)" -ForegroundColor Green
                    $found = $true
                    
                    # Try to remove the key directly
                    try {
                        Remove-Item -Path $key.PSPath -Recurse -Force -ErrorAction Stop
                        Write-Host "Successfully removed registry key" -ForegroundColor Green
                        # Break out of this key since we've already removed it
                        break
                    } catch {
                        Write-Host "Error removing registry key: $_" -ForegroundColor Red
                    }
                }
            }
            
            # Continue searching deeper if we haven't removed this key yet
            if (-not $found) {
                Search-RegistryValueDeep -RootKey $key.PSPath -SearchText $SearchText -MaxDepth $MaxDepth -CurrentDepth ($CurrentDepth + 1)
            }
        }
    } catch {
        # Just continue if we can't access a key
    }
}

# Search the entire registry for these specific Python components
$rootKeys = @(
    "HKLM:\SOFTWARE",
    "HKLM:\SYSTEM\CurrentControlSet\Services"
)

foreach ($displayName in $componentDisplayNames) {
    Write-Host "Searching for: $displayName" -ForegroundColor Cyan
    
    foreach ($rootKey in $rootKeys) {
        Search-RegistryValueDeep -RootKey $rootKey -SearchText $displayName -MaxDepth 3
    }
}

# APPROACH 5: Force direct MsiExec removal with /x /f
Write-Host "`n== APPROACH 5: Forced MSI direct uninstallation ==" -ForegroundColor Magenta

foreach ($guid in $pythonGUIDs) {
    Write-Host "Attempting forced uninstall for: $guid" -ForegroundColor Cyan
    
    try {
        # Use more aggressive flags for msiexec
        $arguments = "/x $guid /qn /norestart /forcerestart /f"
        Start-Process -FilePath "msiexec.exe" -ArgumentList $arguments -Wait -NoNewWindow
        Write-Host "Forced MSI uninstall command completed" -ForegroundColor Green
    } catch {
        Write-Host "Error during forced MSI uninstall: $_" -ForegroundColor Red
    }
}

Write-Host "`n== All cleanup approaches completed ==" -ForegroundColor Magenta
Write-Host "The system should be restarted to complete the removal process." -ForegroundColor Yellow
Write-Host "If entries still persist after restart, manual removal through regedit may be required." -ForegroundColor Yellow 