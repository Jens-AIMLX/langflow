#!/usr/bin/env python3
"""
Test Enhanced Filename Components in Langflow Environment

This script tests the components within the Langflow virtual environment
to verify they work correctly when loaded by Langflow.
"""

import os
import sys
import tempfile
import json
from pathlib import Path

def setup_langflow_environment():
    """Set up the environment to work with Langflow components."""
    # Add custom_nodes to Python path
    custom_nodes_path = os.path.join(os.path.dirname(__file__), 'custom_nodes')
    if custom_nodes_path not in sys.path:
        sys.path.insert(0, custom_nodes_path)
    
    print(f"✅ Added custom_nodes to Python path: {custom_nodes_path}")

def test_component_import():
    """Test if we can import the component."""
    print("\n🔍 Testing Component Import...")
    print("=" * 40)
    
    try:
        # Try to import the backward compatible component
        from backward_compatible_file_metadata_extractor import BackwardCompatibleFileMetadataExtractor
        print("✅ Successfully imported BackwardCompatibleFileMetadataExtractor")
        
        # Create an instance
        component = BackwardCompatibleFileMetadataExtractor()
        print("✅ Successfully created component instance")
        
        # Check component attributes
        print(f"   Display Name: {component.display_name}")
        print(f"   Component Name: {component.name}")
        print(f"   Has extract_metadata: {hasattr(component, 'extract_metadata')}")
        
        return component
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("   This is expected when running outside Langflow environment")
        return None
    except Exception as e:
        print(f"❌ Component creation failed: {e}")
        return None

def test_component_functionality(component):
    """Test the component functionality with a real file."""
    if component is None:
        print("\n⚠️ Skipping functionality test - component not available")
        return False
    
    print("\n🔍 Testing Component Functionality...")
    print("=" * 40)
    
    try:
        # Create a test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a test document for filename extraction testing.")
            test_file_path = f.name
        
        print(f"✅ Created test file: {os.path.basename(test_file_path)}")
        
        # Test filename extraction
        original_filename = component.get_original_filename_legacy(test_file_path)
        print(f"✅ Extracted filename: {original_filename}")
        
        # Test input format detection
        format_info = component.detect_input_format(test_file_path)
        print(f"✅ Format detection: {format_info['detection_method']}")
        
        # Test metadata extraction
        component.input_file = test_file_path
        result = component.extract_metadata()
        
        if hasattr(result, 'text'):
            print("✅ Metadata extraction successful")
            print(f"   Result type: {type(result)}")
            print(f"   Contains filename: {original_filename in result.text}")
            
            # Show a snippet of the result
            snippet = result.text[:200] + "..." if len(result.text) > 200 else result.text
            print(f"   Result snippet: {snippet}")
            
        else:
            print(f"❌ Unexpected result type: {type(result)}")
            return False
        
        # Clean up
        os.unlink(test_file_path)
        print("✅ Test file cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False

def test_langflow_integration():
    """Test if the component can be used in Langflow context."""
    print("\n🔍 Testing Langflow Integration...")
    print("=" * 40)
    
    try:
        # Test if we can import Langflow components
        from langflow.custom import Component
        from langflow.io import FileInput, Output
        from langflow.schema import Message
        print("✅ Langflow imports successful")
        
        # Test if our component inherits correctly
        from backward_compatible_file_metadata_extractor import BackwardCompatibleFileMetadataExtractor
        
        component = BackwardCompatibleFileMetadataExtractor()
        
        # Check if it's a proper Langflow component
        if isinstance(component, Component):
            print("✅ Component is a proper Langflow Component")
        else:
            print(f"⚠️ Component type: {type(component)}")
        
        # Check component structure
        if hasattr(component, 'inputs'):
            print(f"✅ Component has inputs: {len(component.inputs)} input(s)")
        
        if hasattr(component, 'outputs'):
            print(f"✅ Component has outputs: {len(component.outputs)} output(s)")
        
        return True
        
    except ImportError as e:
        print(f"❌ Langflow integration test failed: {e}")
        print("   This might be due to circular imports or missing dependencies")
        print("   The component should still work when loaded through Langflow UI")
        return False
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def create_usage_instructions():
    """Create instructions for using the component in Langflow."""
    print("\n📋 Usage Instructions...")
    print("=" * 40)
    
    instructions = """
To use the Enhanced Filename Components in Langflow:

1. Start Langflow:
   run_langflow.bat

2. Open browser:
   http://127.0.0.1:7860/flows

3. Create a new flow

4. Look for these components in the component panel:
   - "Backward Compatible File Metadata Extractor"
   - "File Metadata Extractor"

5. Drag the component to your canvas

6. Connect a FileInput component to it:
   FileInput → Backward Compatible File Metadata Extractor

7. Upload a test file (e.g., "My Important Document.pdf")

8. Run the flow

9. Check the output - you should see:
   - Original filename: "My Important Document.pdf"
   - Comprehensive metadata about the file
   - File system information

Expected Output Format:
=== BACKWARD COMPATIBLE FILE METADATA SUMMARY ===
✨ Enhanced Format Detected - Original filename from metadata
📁 Original Filename: My Important Document.pdf
📏 File Size: 1.2 MB
🏷️ File Type: .pdf (application/pdf)
📅 Modified: 2024-01-15 10:30:45
🔧 Filename Source: database_lookup

If the components don't appear:
- Check Langflow console for import errors
- Restart Langflow
- Verify the custom_nodes directory contains the component files
"""
    
    print(instructions)

def main():
    """Main test function."""
    print("Enhanced Filename Components - Langflow Environment Test")
    print("=" * 60)
    
    # Setup environment
    setup_langflow_environment()
    
    # Test component import
    component = test_component_import()
    
    # Test functionality
    functionality_ok = test_component_functionality(component)
    
    # Test Langflow integration
    integration_ok = test_langflow_integration()
    
    # Summary
    print("\n" + "=" * 60)
    print("LANGFLOW ENVIRONMENT TEST SUMMARY")
    print("=" * 60)
    
    print(f"Component Import: {'✅ PASS' if component is not None else '❌ FAIL'}")
    print(f"Functionality Test: {'✅ PASS' if functionality_ok else '❌ FAIL'}")
    print(f"Langflow Integration: {'✅ PASS' if integration_ok else '❌ FAIL'}")
    
    if component is not None and functionality_ok:
        print("\n🎉 COMPONENTS ARE WORKING!")
        print("\nThe enhanced filename components are functional and ready to use in Langflow.")
        create_usage_instructions()
    else:
        print("\n⚠️ COMPONENTS NEED ATTENTION")
        print("\nSome tests failed, but components might still work in Langflow UI.")
        print("Try starting Langflow and looking for the components in the UI.")
        create_usage_instructions()

if __name__ == "__main__":
    main()
