#!/usr/bin/env python3
"""
Test script for the File Metadata Extractor component.
This demonstrates how the component works with different file types.
"""

import os
import tempfile
from pathlib import Path

def create_test_files():
    """Create sample test files for demonstration."""
    test_dir = Path("test_files")
    test_dir.mkdir(exist_ok=True)
    
    # Create a simple text file
    text_file = test_dir / "sample.txt"
    with open(text_file, 'w', encoding='utf-8') as f:
        f.write("This is a sample text file.\nIt contains multiple lines.\nUsed for testing metadata extraction.")
    
    # Create a simple RTF file
    rtf_file = test_dir / "sample.rtf"
    with open(rtf_file, 'w', encoding='utf-8') as f:
        f.write(r"""{\rtf1\ansi\deff0 {\fonttbl {\f0 Times New Roman;}}
\f0\fs24 This is a sample RTF document.
\par It contains formatted text.
\par Used for testing metadata extraction.
}""")
    
    print(f"Created test files in: {test_dir.absolute()}")
    return test_dir

def simulate_metadata_extraction(file_path: str, original_filename: str):
    """Simulate the metadata extraction process."""
    print(f"\n=== SIMULATING METADATA EXTRACTION ===")
    print(f"File: {file_path}")
    print(f"Original filename: {original_filename}")
    
    # Import the component (this would normally be done by Langflow)
    import sys
    sys.path.insert(0, str(Path(__file__).parent / "custom_nodes"))
    
    try:
        from file_metadata_extractor import FileMetadataExtractor
        
        # Create component instance
        extractor = FileMetadataExtractor()
        
        # Simulate the input file being set
        extractor.input_file = file_path
        
        # Mock the _inputs structure to simulate how Langflow provides the original filename
        class MockFileInput:
            def __init__(self, value):
                self.value = value
                self.file_path = file_path
        
        extractor._inputs = {
            'input_file': MockFileInput(original_filename)
        }
        
        # Extract metadata
        result = extractor.extract_metadata()
        
        print("=== EXTRACTION RESULT ===")
        print(result.text)
        
    except Exception as e:
        print(f"Error during extraction: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main test function."""
    print("FILE METADATA EXTRACTOR TEST")
    print("=" * 50)
    
    # Create test files
    test_dir = create_test_files()
    
    # Test with text file
    text_file = test_dir / "sample.txt"
    if text_file.exists():
        simulate_metadata_extraction(str(text_file), "my_document.txt")
    
    # Test with RTF file
    rtf_file = test_dir / "sample.rtf"
    if rtf_file.exists():
        simulate_metadata_extraction(str(rtf_file), "gmbhsatzungkurz (1).RTF")
    
    print("\n" + "=" * 50)
    print("TEST COMPLETE")
    print("\nTo use this component in Langflow:")
    print("1. Copy file_metadata_extractor.py to your custom_nodes directory")
    print("2. Add the 'File Metadata Extractor' component to your flow")
    print("3. Upload any supported file type")
    print("4. The component will extract comprehensive metadata including the original filename")

if __name__ == "__main__":
    main()
