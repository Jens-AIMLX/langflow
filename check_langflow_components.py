#!/usr/bin/env python3
"""
Check if enhanced filename components are available in Langflow installation.
This script verifies component availability without requiring full Langflow imports.
"""

import os
import sys
from pathlib import Path

def check_langflow_installation():
    """Check if Langflow is properly installed."""
    print("🔍 Checking Langflow Installation...")
    print("=" * 50)
    
    # Check for virtual environment
    venv_path = Path("langflow_venv")
    if venv_path.exists():
        print("✅ Found: langflow_venv directory")
        
        # Check for Python in venv
        python_exe = venv_path / "Scripts" / "python.exe"
        if python_exe.exists():
            print("✅ Found: Python executable in virtual environment")
        else:
            print("❌ Missing: Python executable in virtual environment")
            return False
            
        # Check for Langflow installation
        site_packages = venv_path / "Lib" / "site-packages"
        langflow_dirs = list(site_packages.glob("langflow*"))
        if langflow_dirs:
            print(f"✅ Found: Langflow installation ({len(langflow_dirs)} packages)")
            for pkg in langflow_dirs:
                print(f"   - {pkg.name}")
        else:
            print("❌ Missing: Langflow installation in virtual environment")
            return False
            
    else:
        print("❌ Missing: langflow_venv directory")
        print("   Please run install_langflow_uv_140.bat first")
        return False
    
    return True

def check_custom_components():
    """Check if custom components are available."""
    print("\n🔍 Checking Custom Components...")
    print("=" * 50)
    
    custom_nodes_path = Path("custom_nodes")
    if not custom_nodes_path.exists():
        print("❌ Missing: custom_nodes directory")
        return False
    
    print("✅ Found: custom_nodes directory")
    
    # Check for specific component files
    required_components = [
        "file_metadata_extractor.py",
        "backward_compatible_file_metadata_extractor.py"
    ]
    
    found_components = []
    missing_components = []
    
    for component in required_components:
        component_path = custom_nodes_path / component
        if component_path.exists():
            print(f"✅ Found: {component}")
            found_components.append(component)
            
            # Check file size (should not be empty)
            size = component_path.stat().st_size
            if size > 1000:  # At least 1KB
                print(f"   Size: {size:,} bytes (looks good)")
            else:
                print(f"   Size: {size} bytes (might be empty or incomplete)")
                
        else:
            print(f"❌ Missing: {component}")
            missing_components.append(component)
    
    if missing_components:
        print(f"\n⚠️ Missing {len(missing_components)} required components:")
        for component in missing_components:
            print(f"   - {component}")
        return False
    
    return True

def check_component_content():
    """Check if component files have the expected content."""
    print("\n🔍 Checking Component Content...")
    print("=" * 50)
    
    components_to_check = [
        ("custom_nodes/backward_compatible_file_metadata_extractor.py", "BackwardCompatibleFileMetadataExtractor"),
        ("custom_nodes/file_metadata_extractor.py", "FileMetadataExtractor")
    ]
    
    all_good = True
    
    for file_path, class_name in components_to_check:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if class_name in content:
                    print(f"✅ {file_path}: Contains {class_name} class")
                    
                    # Check for key methods
                    key_methods = ["extract_metadata", "get_original_filename"]
                    for method in key_methods:
                        if method in content:
                            print(f"   ✅ Has {method} method")
                        else:
                            print(f"   ⚠️ Missing {method} method")
                            
                else:
                    print(f"❌ {file_path}: Missing {class_name} class")
                    all_good = False
                    
            except Exception as e:
                print(f"❌ {file_path}: Error reading file - {e}")
                all_good = False
        else:
            print(f"❌ {file_path}: File not found")
            all_good = False
    
    return all_good

def check_langflow_component_discovery():
    """Check if Langflow can discover our components."""
    print("\n🔍 Checking Langflow Component Discovery...")
    print("=" * 50)
    
    # Check if .env file exists with proper configuration
    env_file = Path(".env")
    if env_file.exists():
        try:
            with open(env_file, 'r') as f:
                env_content = f.read()
            
            if "LANGFLOW_CUSTOM_COMPONENTS_PATH" in env_content:
                print("✅ Found: LANGFLOW_CUSTOM_COMPONENTS_PATH in .env")
            else:
                print("⚠️ Missing: LANGFLOW_CUSTOM_COMPONENTS_PATH in .env")
                
            if "custom_nodes" in env_content:
                print("✅ Found: custom_nodes path configured")
            else:
                print("⚠️ Missing: custom_nodes path configuration")
                
        except Exception as e:
            print(f"❌ Error reading .env file: {e}")
    else:
        print("⚠️ Missing: .env file (components might still work)")
    
    # Check if custom_nodes has __init__.py (not required but helpful)
    init_file = Path("custom_nodes/__init__.py")
    if init_file.exists():
        print("✅ Found: custom_nodes/__init__.py")
    else:
        print("ℹ️ Info: custom_nodes/__init__.py not found (not required)")
    
    return True

def provide_integration_instructions():
    """Provide instructions for integrating components."""
    print("\n📋 Integration Instructions...")
    print("=" * 50)
    
    print("To integrate the enhanced filename components:")
    print()
    print("1. Run the integration script:")
    print("   integrate_filename_components.bat")
    print()
    print("2. Start Langflow:")
    print("   run_langflow.bat")
    print()
    print("3. Open browser:")
    print("   http://127.0.0.1:7860/flows")
    print()
    print("4. Look for these components in the component panel:")
    print("   - 'File Metadata Extractor'")
    print("   - 'Backward Compatible File Metadata Extractor'")
    print()
    print("5. If components don't appear:")
    print("   - Check Langflow console for import errors")
    print("   - Restart Langflow")
    print("   - Verify component files are not corrupted")

def main():
    """Main function to check everything."""
    print("Enhanced Filename Components - Installation Check")
    print("=" * 60)
    
    # Check Langflow installation
    langflow_ok = check_langflow_installation()
    
    # Check custom components
    components_ok = check_custom_components()
    
    # Check component content
    content_ok = check_component_content()
    
    # Check discovery configuration
    discovery_ok = check_langflow_component_discovery()
    
    # Summary
    print("\n" + "=" * 60)
    print("INSTALLATION CHECK SUMMARY")
    print("=" * 60)
    
    print(f"Langflow Installation: {'✅ PASS' if langflow_ok else '❌ FAIL'}")
    print(f"Custom Components: {'✅ PASS' if components_ok else '❌ FAIL'}")
    print(f"Component Content: {'✅ PASS' if content_ok else '❌ FAIL'}")
    print(f"Discovery Config: {'✅ PASS' if discovery_ok else '❌ FAIL'}")
    
    overall_status = langflow_ok and components_ok and content_ok
    
    if overall_status:
        print("\n🎉 COMPONENTS ARE READY!")
        print("\nYour enhanced filename components should be available in Langflow.")
        print("Start Langflow and look for the metadata extractor components.")
    else:
        print("\n⚠️ SETUP INCOMPLETE")
        print("\nSome components or configuration are missing.")
        provide_integration_instructions()
    
    return overall_status

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
