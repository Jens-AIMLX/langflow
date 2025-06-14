#!/usr/bin/env python3
"""
Script to rename all test methods with clear prefixes:
- U_ for Unit Tests
- I_ for Integration Tests  
- S_ for System Tests
- UI_ for User Interaction Tests
"""

import os
import re

def rename_test_methods_in_file(file_path, test_type_mapping):
    """Rename test methods in a file based on test type mapping."""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False
    
    # Read file content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes_made = 0
    
    # Apply test method renames based on mapping
    for pattern, prefix in test_type_mapping.items():
        # Find all test methods matching the pattern
        regex = rf'def (test_{pattern}[^(]*)\('
        matches = re.findall(regex, content)
        
        for match in matches:
            old_name = match
            # Skip if already has a prefix
            if old_name.startswith('test_U_') or old_name.startswith('test_I_') or old_name.startswith('test_S_') or old_name.startswith('test_UI_'):
                continue
            
            # Create new name with prefix
            new_name = old_name.replace('test_', f'test_{prefix}_', 1)
            
            # Replace in content
            content = content.replace(f'def {old_name}(', f'def {new_name}(')
            
            # Also replace any calls to this function
            content = content.replace(f'{old_name}()', f'{new_name}()')
            
            print(f"  Renamed: {old_name} -> {new_name}")
            changes_made += 1
    
    # Write back if changes were made
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Applied {changes_made} changes to: {file_path}")
        return True
    else:
        print(f"No changes needed for: {file_path}")
        return False

def main():
    """Rename test methods in all test files."""
    print("Renaming test methods with clear prefixes...")
    print("=" * 60)
    
    # Define test files and their test type mappings
    test_files_config = {
        'test_enhanced_filename_flow_design.py': {
            'file_upload_simulation': 'I',
            'component_chain_with_files': 'I', 
            'bulk_file_processing': 'I',
            'flow_json_with_enhanced_files': 'I',
            'backward_compatibility': 'I'
        },
        'test_enhanced_filename_user_interaction.py': {
            'drag_and_drop_file_upload': 'S',
            'file_browser_upload': 'S',
            'component_configuration_ui': 'S',
            'flow_execution_with_files': 'S',
            'error_handling_user_experience': 'S'
        },
        'test_enhanced_filename_browser_automation.py': {
            'langflow_file_upload_ui': 'S',
            'file_metadata_extractor_component': 'S',
            'flow_execution_with_enhanced_filename': 'S',
            'error_messages_with_filename': 'S'
        },
        'test_enhanced_filename_semi_automated.py': {
            'langflow_startup_and_enhanced_features': 'UI',
            'file_upload_with_original_filename_display': 'UI',
            'file_metadata_extractor_component_availability': 'UI',
            'flow_execution_with_filename_preservation': 'UI',
            'error_handling_with_filename_context': 'UI',
            'user_experience_quality_assessment': 'UI'
        },
        'test_enhanced_filename_comprehensive.py': {
            'unit_basic_functionality': 'U',
            'unit_enhanced_filename_core': 'U',
            'integration_flow_design': 'I',
            'integration_performance': 'I',
            'user_interaction_simulation': 'S',
            'semi_automated_langflow_startup': 'UI',
            'semi_automated_file_upload_ui': 'UI',
            'semi_automated_component_availability': 'UI',
            'semi_automated_flow_execution': 'UI',
            'semi_automated_error_handling': 'UI',
            'semi_automated_user_experience': 'UI',
            'browser_automation_availability': 'S',
            'regression_backward_compatibility': 'I',
            'comprehensive_summary': 'S'
        }
    }
    
    total_files_processed = 0
    total_changes = 0
    
    for file_path, test_mapping in test_files_config.items():
        print(f"\nProcessing: {file_path}")
        if rename_test_methods_in_file(file_path, test_mapping):
            total_files_processed += 1
    
    print("\n" + "=" * 60)
    print("TEST METHOD RENAMING COMPLETE")
    print("=" * 60)
    print(f"Files processed: {total_files_processed}")
    print("\nTest Naming Convention Applied:")
    print("  U_  = Unit Test (fully automated)")
    print("  I_  = Integration Test (fully automated)")
    print("  S_  = System Test (fully automated)")
    print("  UI_ = User Interaction Test (semi-automated)")
    print("\nAll tests should now have clear, descriptive names!")

if __name__ == "__main__":
    main()
