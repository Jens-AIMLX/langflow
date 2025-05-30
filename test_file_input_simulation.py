#!/usr/bin/env python3
"""
Comprehensive test to simulate exactly how Langflow FileInput works
and find where the original filename is stored.
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock

# Add the langflow path to sys.path to import modules
sys.path.insert(0, str(Path(__file__).parent))

def create_mock_file_input():
    """Create a mock FileInput that simulates the exact Langflow behavior."""
    
    # Based on the source code analysis:
    # FileInput inherits from: BaseInputMixin, ListableInputMixin, FileMixin, MetadataTraceMixin
    # FileMixin has: file_path, file_types, temp_file
    # BaseInputMixin has: value, name, display_name, etc.
    
    class MockFileInput:
        def __init__(self, **kwargs):
            # From BaseInputMixin
            self.name = kwargs.get('name', 'test_file')
            self.display_name = kwargs.get('display_name', 'Test File')
            self.value = kwargs.get('value', '')
            self.required = kwargs.get('required', True)
            self.show = kwargs.get('show', True)
            self.advanced = kwargs.get('advanced', False)
            
            # From FileMixin  
            self.file_path = kwargs.get('file_path', '')
            self.file_types = kwargs.get('file_types', [])
            self.temp_file = kwargs.get('temp_file', False)
            
            # From ListableInputMixin
            self.is_list = kwargs.get('is_list', False)
            self.list_add_label = kwargs.get('list_add_label', 'Add More')
            
            # From MetadataTraceMixin
            self.trace_as_metadata = kwargs.get('trace_as_metadata', True)
            
            # Field type
            self.field_type = 'file'
            
        def __repr__(self):
            return f"MockFileInput(name='{self.name}', value='{self.value}', file_path='{self.file_path}')"
    
    return MockFileInput

def simulate_frontend_upload():
    """Simulate exactly what the frontend does when uploading a file."""
    
    print("=== SIMULATING FRONTEND FILE UPLOAD ===")
    
    # Step 1: User selects file "gmbhsatzungkurz (1).RTF"
    original_filename = "gmbhsatzungkurz (1).RTF"
    print(f"1. User selects file: {original_filename}")
    
    # Step 2: Frontend uploads to backend and gets server path
    server_path = "C:\\Users\\Host\\AppData\\Local\\langflow\\langflow\\Cache\\74e3a67b-29bf-4e09-974c-d3beb0364c23\\938df858-26e6-401b-86b0-2c044da91679.RTF"
    print(f"2. Backend returns server path: {server_path}")
    
    # Step 3: Frontend calls handleOnNewValue with BOTH values
    # From the source code (lines 130-133):
    # handleOnNewValue({
    #   value: isList ? fileNames : fileNames[0],        // ORIGINAL FILENAME
    #   file_path: isList ? filePaths : filePaths[0],    // SERVER PATH  
    # });
    
    frontend_data = {
        'value': original_filename,      # This should contain the original filename!
        'file_path': server_path        # This contains the server path
    }
    
    print(f"3. Frontend sends to backend:")
    print(f"   value: {frontend_data['value']}")
    print(f"   file_path: {frontend_data['file_path']}")
    
    return frontend_data

def simulate_backend_component(frontend_data):
    """Simulate how the backend component receives and processes the data."""
    
    print("\n=== SIMULATING BACKEND COMPONENT ===")
    
    # Create mock FileInput with the data from frontend
    MockFileInput = create_mock_file_input()
    file_input = MockFileInput(
        name="rtf_file",
        display_name="RTF File",
        value=frontend_data['value'],           # Should be original filename
        file_path=frontend_data['file_path'],   # Should be server path
        file_types=["rtf"],
        required=True
    )
    
    print(f"4. Backend FileInput created:")
    print(f"   file_input.value: {file_input.value}")
    print(f"   file_input.file_path: {file_input.file_path}")
    print(f"   file_input.name: {file_input.name}")
    
    # Simulate component with _inputs dictionary (how Langflow stores inputs)
    class MockComponent:
        def __init__(self):
            self._inputs = {
                'rtf_file': file_input
            }
            self._attributes = {
                'rtf_file': frontend_data['file_path']  # This gets the server path
            }
            # Direct attribute access (what we see in debug)
            self.rtf_file = frontend_data['file_path']  # This also gets server path
    
    component = MockComponent()
    
    print(f"5. Component state:")
    print(f"   component.rtf_file: {component.rtf_file}")
    print(f"   component._attributes['rtf_file']: {component._attributes['rtf_file']}")
    print(f"   component._inputs['rtf_file'].value: {component._inputs['rtf_file'].value}")
    print(f"   component._inputs['rtf_file'].file_path: {component._inputs['rtf_file'].file_path}")
    
    return component

def test_filename_access_strategies(component):
    """Test all possible strategies to access the original filename."""
    
    print("\n=== TESTING FILENAME ACCESS STRATEGIES ===")
    
    strategies = []
    
    # Strategy 1: Direct attribute access
    try:
        filename = component.rtf_file
        strategies.append(f"Strategy 1 - Direct attribute: {filename}")
    except Exception as e:
        strategies.append(f"Strategy 1 - Direct attribute: ERROR - {e}")
    
    # Strategy 2: _attributes dictionary
    try:
        filename = component._attributes['rtf_file']
        strategies.append(f"Strategy 2 - _attributes: {filename}")
    except Exception as e:
        strategies.append(f"Strategy 2 - _attributes: ERROR - {e}")
    
    # Strategy 3: _inputs value property
    try:
        filename = component._inputs['rtf_file'].value
        strategies.append(f"Strategy 3 - _inputs.value: {filename}")
    except Exception as e:
        strategies.append(f"Strategy 3 - _inputs.value: ERROR - {e}")
    
    # Strategy 4: _inputs file_path property
    try:
        filename = component._inputs['rtf_file'].file_path
        strategies.append(f"Strategy 4 - _inputs.file_path: {filename}")
    except Exception as e:
        strategies.append(f"Strategy 4 - _inputs.file_path: ERROR - {e}")
    
    # Print results
    for i, strategy in enumerate(strategies, 1):
        print(f"{i}. {strategy}")
        if "gmbhsatzungkurz" in strategy:
            print(f"   ✅ SUCCESS! Found original filename!")
        else:
            print(f"   ❌ Contains server path/UUID")
    
    return strategies

def analyze_discrepancy():
    """Analyze why our simulation differs from the actual Langflow behavior."""
    
    print("\n=== ANALYZING DISCREPANCY ===")
    
    print("EXPECTED (from frontend source code):")
    print("  - value should contain: 'gmbhsatzungkurz (1).RTF'")
    print("  - file_path should contain: server path with UUID")
    
    print("\nACTUAL (from debug output):")
    print("  - value contains: server path with UUID")
    print("  - file_path contains: empty string")
    
    print("\nPOSSIBLE CAUSES:")
    print("1. Frontend is not sending the data as expected")
    print("2. Backend is overwriting the value property")
    print("3. Component initialization is changing the values")
    print("4. There's a mapping/transformation happening")
    
    print("\nNEXT STEPS:")
    print("1. Check if there's a backend transformation of the data")
    print("2. Look for any value mapping in component initialization")
    print("3. Check if the FileInput class has custom setters")
    print("4. Verify the actual network request data")

def main():
    """Run the comprehensive test simulation."""
    
    print("LANGFLOW FILEINPUT COMPREHENSIVE TEST")
    print("=" * 50)
    
    # Step 1: Simulate frontend upload
    frontend_data = simulate_frontend_upload()
    
    # Step 2: Simulate backend component
    component = simulate_backend_component(frontend_data)
    
    # Step 3: Test access strategies
    strategies = test_filename_access_strategies(component)
    
    # Step 4: Analyze discrepancy
    analyze_discrepancy()
    
    print("\n" + "=" * 50)
    print("TEST COMPLETE")
    
    # Check if we found the original filename
    success = any("gmbhsatzungkurz" in strategy for strategy in strategies)
    if success:
        print("✅ SUCCESS: Found original filename!")
    else:
        print("❌ FAILURE: Original filename not found in any strategy")
        print("   This confirms the frontend is NOT sending the original filename to backend")

if __name__ == "__main__":
    main()
