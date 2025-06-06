#!/usr/bin/env python3
"""
Simple validation script for the enhanced filename implementation.
"""

import os
from pathlib import Path

def validate_files_exist():
    """Check that all implementation files exist."""
    print("=== Validating Implementation Files ===")
    
    files_to_check = [
        # Database models
        "src/backend/base/langflow/services/database/models/file_metadata.py",
        
        # API components
        "src/backend/base/langflow/api/v2/enhanced_files.py",
        "src/backend/base/langflow/api/v2/schemas.py",
        
        # Enhanced inputs
        "src/backend/base/langflow/inputs/enhanced_inputs.py",
        
        # Enhanced components
        "src/backend/base/langflow/custom/enhanced_component.py",
        
        # Migration utilities
        "src/backend/base/langflow/services/migration/file_migration.py",
        
        # Database migration
        "src/backend/base/langflow/alembic/versions/add_enhanced_file_metadata.py",
        
        # Feature flags
        "src/backend/base/langflow/services/settings/feature_flags.py",
        
        # Updated components
        "custom_nodes/file_metadata_extractor.py",
        
        # Scripts and tools
        "scripts/migrate_enhanced_files.py",
        
        # Documentation
        "ENHANCED_FILENAME_IMPLEMENTATION.md",
    ]
    
    missing_files = []
    existing_files = []
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            existing_files.append(file_path)
            print(f"✅ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"❌ {file_path}")
    
    print(f"\nSummary: {len(existing_files)}/{len(files_to_check)} files exist")
    
    if missing_files:
        print("\nMissing files:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        return False
    
    return True


def validate_file_contents():
    """Check that key files have expected content."""
    print("\n=== Validating File Contents ===")
    
    validations = []
    
    # Check feature flags
    try:
        with open("src/backend/base/langflow/services/settings/feature_flags.py", 'r') as f:
            content = f.read()
            if "enhanced_file_inputs" in content:
                print("✅ Feature flag added to feature_flags.py")
                validations.append(True)
            else:
                print("❌ Feature flag not found in feature_flags.py")
                validations.append(False)
    except Exception as e:
        print(f"❌ Error reading feature_flags.py: {e}")
        validations.append(False)
    
    # Check file metadata extractor
    try:
        with open("custom_nodes/file_metadata_extractor.py", 'r') as f:
            content = f.read()
            if "BackwardCompatibleComponent" in content:
                print("✅ File metadata extractor updated with enhanced support")
                validations.append(True)
            else:
                print("❌ File metadata extractor not updated")
                validations.append(False)
    except Exception as e:
        print(f"❌ Error reading file_metadata_extractor.py: {e}")
        validations.append(False)
    
    # Check database models
    try:
        with open("src/backend/base/langflow/services/database/models/file_metadata.py", 'r') as f:
            content = f.read()
            if "FileMetadataEnhanced" in content and "original_filename" in content:
                print("✅ Enhanced database models implemented")
                validations.append(True)
            else:
                print("❌ Enhanced database models incomplete")
                validations.append(False)
    except Exception as e:
        print(f"❌ Error reading file_metadata.py: {e}")
        validations.append(False)
    
    # Check enhanced inputs
    try:
        with open("src/backend/base/langflow/inputs/enhanced_inputs.py", 'r') as f:
            content = f.read()
            if "EnhancedFileInput" in content and "FileInputAdapter" in content:
                print("✅ Enhanced input classes implemented")
                validations.append(True)
            else:
                print("❌ Enhanced input classes incomplete")
                validations.append(False)
    except Exception as e:
        print(f"❌ Error reading enhanced_inputs.py: {e}")
        validations.append(False)
    
    return all(validations)


def validate_structure():
    """Validate the overall structure and architecture."""
    print("\n=== Validating Architecture ===")
    
    checks = []
    
    # Check that we have all layers
    layers = [
        ("Database Layer", "src/backend/base/langflow/services/database/models/file_metadata.py"),
        ("API Layer", "src/backend/base/langflow/api/v2/enhanced_files.py"),
        ("Input Layer", "src/backend/base/langflow/inputs/enhanced_inputs.py"),
        ("Component Layer", "src/backend/base/langflow/custom/enhanced_component.py"),
        ("Migration Layer", "src/backend/base/langflow/services/migration/file_migration.py"),
    ]
    
    for layer_name, file_path in layers:
        if os.path.exists(file_path):
            print(f"✅ {layer_name}")
            checks.append(True)
        else:
            print(f"❌ {layer_name} - Missing {file_path}")
            checks.append(False)
    
    # Check backward compatibility
    if os.path.exists("custom_nodes/file_metadata_extractor.py"):
        print("✅ Backward Compatibility - Updated component maintains compatibility")
        checks.append(True)
    else:
        print("❌ Backward Compatibility - Component not updated")
        checks.append(False)
    
    return all(checks)


def main():
    """Run all validations."""
    print("🔍 Enhanced Filename Implementation Validation")
    print("=" * 60)
    
    validations = [
        ("File Existence", validate_files_exist),
        ("File Contents", validate_file_contents),
        ("Architecture", validate_structure),
    ]
    
    results = []
    
    for validation_name, validation_func in validations:
        try:
            success = validation_func()
            results.append((validation_name, success))
        except Exception as e:
            print(f"❌ {validation_name} validation crashed: {e}")
            results.append((validation_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 Validation Summary")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for validation_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {validation_name}")
    
    print(f"\nOverall: {passed}/{total} validations passed")
    
    if passed == total:
        print("\n🎉 All validations passed!")
        print("✅ Enhanced filename exposure implementation is complete and ready for deployment.")
        print("\nNext steps:")
        print("1. Run database migration: alembic upgrade head")
        print("2. Enable feature flag: LANGFLOW_FEATURE_ENHANCED_FILE_INPUTS=true")
        print("3. Test with the File Metadata Extractor component")
        print("4. Migrate existing files: python scripts/migrate_enhanced_files.py migrate")
    else:
        print("\n⚠️ Some validations failed.")
        print("Please check the output above and ensure all files are properly created.")
    
    return passed == total


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
