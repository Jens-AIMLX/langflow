import os
import pytest
import json
import sqlite3
from pathlib import Path
import sys

# Add necessary paths to import from
sys.path.append(os.path.join(os.path.dirname(__file__), "src/backend/base"))

# Try to import enhanced components
try:
    from src.backend.base.langflow.custom.enhanced_component import EnhancedComponent, BackwardCompatibleComponent
    from src.backend.base.langflow.inputs.enhanced_inputs import EnhancedFileInput
    from custom_nodes.file_metadata_extractor import FileMetadataExtractor
    from custom_nodes.backward_compatible_file_metadata_extractor import BackwardCompatibleFileMetadataExtractor
    ENHANCED_AVAILABLE = True
    print("Enhanced components successfully imported.")
except ImportError as e:
    print(f"Import error: {e}")
    ENHANCED_AVAILABLE = False


class TestEnhancedFilename:
    """Test class for checking enhanced filename functionality"""
    
    @pytest.fixture
    def setup_test_db(self, tmp_path):
        """Create a test database with file entries."""
        # Create test database
        db_path = tmp_path / "test_langflow.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create file table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS file (
            id INTEGER PRIMARY KEY,
            name TEXT,
            path TEXT,
            size INTEGER,
            type TEXT
        )
        """)
        
        # Insert test file entry
        test_uuid = "938df858-26e6-401b-86b0-2c044da91679"
        test_dir = "74e3a67b-29bf-4e09-974c-d3beb0364c23"
        cursor.execute(
            "INSERT INTO file (name, path, size, type) VALUES (?, ?, ?, ?)",
            ("Original_Important_Document.RTF", f"{test_dir}/{test_uuid}.RTF", 55638, "rtf")
        )
        
        conn.commit()
        conn.close()
        
        # Create test directory and file
        test_dir_path = tmp_path / test_dir
        test_dir_path.mkdir(exist_ok=True)
        test_file_path = test_dir_path / f"{test_uuid}.RTF"
        
        # Create a simple RTF file for testing
        with open(test_file_path, 'w') as f:
            f.write(r"{\rtf1\ansi\ansicpg1252\cocoartf2580 Test Content}")
        
        # Return paths
        return {
            "db_path": str(db_path),
            "file_path": str(test_file_path),
            "file_uuid": test_uuid,
            "dir_uuid": test_dir,
            "original_filename": "Original_Important_Document.RTF"
        }
    
    def test_get_original_filename_legacy(self, setup_test_db, monkeypatch):
        """Test original filename retrieval using legacy database lookup."""
        if not ENHANCED_AVAILABLE:
            pytest.skip("Enhanced components not available")
        
        # Set up environment
        test_data = setup_test_db
        monkeypatch.setattr("os.path.exists", lambda path: path == test_data["db_path"] or path == test_data["file_path"])
        monkeypatch.setattr("os.getcwd", lambda: str(Path(test_data["db_path"]).parent))
        
        # Initialize component
        component = BackwardCompatibleFileMetadataExtractor()
        
        # Mock inputs
        component.input_file = test_data["file_path"]
        
        # Test the metadata extraction
        result = component.extract_metadata()
        
        # Verify the result contains the correct original filename
        assert result.text.strip() != ""
        
        # Parse the JSON part from the result
        metadata_text = result.text.split("=== DETAILED METADATA ===")[1].strip()
        metadata = json.loads(metadata_text)
        
        # Verify the metadata contains the correct original filename
        assert "file_system" in metadata
        assert "original_filename" in metadata["file_system"]
        assert metadata["file_system"]["original_filename"] == test_data["original_filename"]
    
    def test_get_original_filename_enhanced(self):
        """Test original filename retrieval using enhanced metadata."""
        if not ENHANCED_AVAILABLE:
            pytest.skip("Enhanced components not available")
        
        # Initialize component
        component = FileMetadataExtractor()
        
        # Create a test file path
        test_file_path = "test_file.txt"
        test_original_filename = "User_Original_Document.txt"
        
        # Create enhanced input with original filename
        enhanced_input = {
            "path": test_file_path,
            "original_filename": test_original_filename,
            "content_type": "text/plain",
            "file_size": 1024
        }
        
        # Mock the file exists
        original_exists = os.path.exists
        try:
            os.path.exists = lambda path: path == test_file_path or original_exists(path)
            
            # Mock inputs - test with dictionary format
            component.input_file = enhanced_input
            
            # Get file info using universal method
            file_info = component.get_file_info_universal('input_file')
            
            # Verify that the enhanced information is correctly extracted
            assert file_info["is_enhanced"] == True
            assert file_info["original_filename"] == test_original_filename
            assert file_info["detection_method"] in ["dict_format", "enhanced_input", "object_format"]
            
        finally:
            # Restore original function
            os.path.exists = original_exists


if __name__ == "__main__":
    pytest.main(["-v", "test_enhanced_filename_quick.py"]) 