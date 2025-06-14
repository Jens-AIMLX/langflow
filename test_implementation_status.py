#!/usr/bin/env python3
"""
Quick test to check current implementation status and identify missing components.
"""

import sys
import os
from pathlib import Path

def test_import_status():
    """Test which components are available and which need to be implemented."""
    print("🔍 Enhanced Filename Implementation Status Check")
    print("=" * 60)
    
    # Add paths
    sys.path.insert(0, str(Path(__file__).parent / "src" / "backend" / "base"))
    sys.path.insert(0, str(Path(__file__).parent / "custom_nodes"))
    
    components_status = {}
    
    # Test 1: Database Models
    print("\n📊 Database Models:")
    try:
        from langflow.services.database.models.file_metadata import FileMetadataEnhanced, FileMetadataService
        components_status["database_models"] = "✅ Available"
        print("  ✅ FileMetadataEnhanced model available")
        print("  ✅ FileMetadataService available")
    except ImportError as e:
        components_status["database_models"] = f"❌ Missing: {e}"
        print(f"  ❌ Database models missing: {e}")
    
    # Test 2: API Schemas
    print("\n🔗 API Schemas:")
    try:
        from langflow.api.v2.schemas import FileMetadata
        components_status["api_schemas"] = "✅ Available"
        print("  ✅ FileMetadata schema available")
        
        # Test utility functions
        try:
            from langflow.api.v2.schemas import normalize_file_input, get_file_path, get_original_filename
            print("  ✅ Utility functions available")
        except ImportError:
            print("  ⚠️ Some utility functions missing")
            
    except ImportError as e:
        components_status["api_schemas"] = f"❌ Missing: {e}"
        print(f"  ❌ API schemas missing: {e}")
    
    # Test 3: Enhanced Inputs
    print("\n📥 Enhanced Inputs:")
    try:
        from langflow.inputs.enhanced_inputs import EnhancedFileInput, FileInputAdapter
        components_status["enhanced_inputs"] = "✅ Available"
        print("  ✅ EnhancedFileInput available")
        print("  ✅ FileInputAdapter available")
        
        # Test utility functions
        try:
            from langflow.inputs.enhanced_inputs import get_enhanced_file_info
            print("  ✅ Enhanced file info utilities available")
        except ImportError:
            print("  ⚠️ Some enhanced input utilities missing")
            
    except ImportError as e:
        components_status["enhanced_inputs"] = f"❌ Missing: {e}"
        print(f"  ❌ Enhanced inputs missing: {e}")
    
    # Test 4: Enhanced Components
    print("\n🧩 Enhanced Components:")
    try:
        from langflow.custom.enhanced_component import EnhancedComponent
        components_status["enhanced_components"] = "✅ Available"
        print("  ✅ EnhancedComponent base class available")
        
        try:
            from langflow.custom.enhanced_component import BackwardCompatibleComponent
            print("  ✅ BackwardCompatibleComponent available")
        except ImportError:
            print("  ⚠️ BackwardCompatibleComponent missing")
            
    except ImportError as e:
        components_status["enhanced_components"] = f"❌ Missing: {e}"
        print(f"  ❌ Enhanced components missing: {e}")
    
    # Test 5: File Metadata Extractor
    print("\n🔍 File Metadata Extractor:")
    try:
        from file_metadata_extractor import FileMetadataExtractor
        components_status["file_metadata_extractor"] = "✅ Available"
        print("  ✅ FileMetadataExtractor available")
    except ImportError as e:
        components_status["file_metadata_extractor"] = f"❌ Missing: {e}"
        print(f"  ❌ FileMetadataExtractor missing: {e}")
    
    # Test 6: Backward Compatible Extractor
    print("\n🔄 Backward Compatible Extractor:")
    try:
        from backward_compatible_file_metadata_extractor import BackwardCompatibleFileMetadataExtractor
        components_status["backward_compatible_extractor"] = "✅ Available"
        print("  ✅ BackwardCompatibleFileMetadataExtractor available")
    except ImportError as e:
        components_status["backward_compatible_extractor"] = f"❌ Missing: {e}"
        print(f"  ❌ BackwardCompatibleFileMetadataExtractor missing: {e}")
    
    # Test 7: Migration Utilities
    print("\n🔄 Migration Utilities:")
    try:
        from langflow.services.migration.file_migration import FileMigrationService
        components_status["migration_utilities"] = "✅ Available"
        print("  ✅ FileMigrationService available")
    except ImportError as e:
        components_status["migration_utilities"] = f"❌ Missing: {e}"
        print(f"  ❌ Migration utilities missing: {e}")
    
    # Test 8: Feature Flags
    print("\n🚩 Feature Flags:")
    try:
        from langflow.services.settings.feature_flags import FEATURE_FLAGS
        components_status["feature_flags"] = "✅ Available"
        print("  ✅ Feature flags available")
        enhanced_flag = getattr(FEATURE_FLAGS, 'enhanced_file_inputs', 'Not available')
        print(f"  📊 Enhanced file inputs flag: {enhanced_flag}")
    except ImportError as e:
        components_status["feature_flags"] = f"❌ Missing: {e}"
        print(f"  ❌ Feature flags missing: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 IMPLEMENTATION STATUS SUMMARY")
    print("=" * 60)
    
    available_count = sum(1 for status in components_status.values() if status.startswith("✅"))
    total_count = len(components_status)
    
    print(f"📊 Overall Progress: {available_count}/{total_count} components available")
    print(f"🎯 Completion Rate: {(available_count/total_count)*100:.1f}%")
    
    print("\n📝 Component Status:")
    for component, status in components_status.items():
        print(f"  {component}: {status}")
    
    # Next steps
    print("\n🚀 NEXT IMPLEMENTATION PRIORITIES:")
    missing_components = [comp for comp, status in components_status.items() if status.startswith("❌")]
    
    if missing_components:
        print("  High Priority:")
        for comp in missing_components[:3]:  # Top 3 priorities
            print(f"    - {comp}")
        
        if len(missing_components) > 3:
            print("  Medium Priority:")
            for comp in missing_components[3:]:
                print(f"    - {comp}")
    else:
        print("  🎉 All core components implemented!")
    
    return components_status

if __name__ == "__main__":
    test_import_status()
