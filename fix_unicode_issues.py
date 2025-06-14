#!/usr/bin/env python3
"""
Fix Unicode issues in test files for German Windows compatibility.
"""

import os
import re

def fix_unicode_in_file(file_path):
    """Fix Unicode characters in a file."""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    
    # Read file content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Define emoji replacements
    emoji_replacements = {
        '🧪': 'TEST:',
        '🔗': 'CHAIN:',
        '⚡': 'PERF:',
        '📄': 'JSON:',
        '🔄': 'COMPAT:',
        '📊': 'SUMMARY:',
        '🎉': 'SUCCESS:',
        '✅': 'PASS:',
        '❌': 'FAIL:',
        '⚠️': 'WARNING:',
        '🚀': 'START:',
        '🎭': 'UI:',
        '🌐': 'BROWSER:',
        '🖱️': 'MOUSE:',
        '📁': 'FILE:',
        '⚙️': 'CONFIG:',
        '▶️': 'RUN:',
        '🧩': 'COMPONENT:',
        '📋': 'REPORT:',
        '🎯': 'RESULT:',
        '💥': 'ERROR:',
        '⏰': 'TIMEOUT:',
        '❓': 'UNKNOWN:',
        'ℹ️': 'INFO:',
        '🔧': 'FIX:'
    }
    
    # Replace emojis
    original_content = content
    for emoji, replacement in emoji_replacements.items():
        content = content.replace(emoji, replacement)
    
    # Write back if changed
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed Unicode issues in: {file_path}")
        return True
    else:
        print(f"No Unicode issues found in: {file_path}")
        return False

def main():
    """Fix Unicode issues in all test files."""
    test_files = [
        'test_basic_functionality.py',
        'test_enhanced_filename_simple.py',
        'test_enhanced_filename_flow_design.py',
        'test_enhanced_filename_user_interaction.py',
        'test_enhanced_filename_browser_automation.py'
    ]
    
    print("Fixing Unicode issues in test files...")
    print("=" * 50)
    
    fixed_count = 0
    for file_path in test_files:
        if fix_unicode_in_file(file_path):
            fixed_count += 1
    
    print("=" * 50)
    print(f"Fixed Unicode issues in {fixed_count} files")
    print("All test files should now work on German Windows")

if __name__ == "__main__":
    main()
