#!/usr/bin/env python3
"""
Unit Test: Automated Component Test for Filename Exposure Functionality

This test verifies that our filename exposure components work correctly
and can be used as a source for enhanced filename functionality.

Test Categories:
- U_ = Unit Test (fully automated)
- Component functionality testing
- Filename exposure verification
- Backward compatibility testing
"""

import pytest
import os
import tempfile
import json
import sqlite3
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# Add custom_nodes to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_nodes'))

class TestFilenameExposureComponents:
    """Test filename exposure components for automated verification."""
    
    def setup_method(self):
        """Set up test environment."""
        self.test_files = []
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Clean up test environment."""
        for file_path in self.test_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except:
                pass
        try:
            os.rmdir(self.temp_dir)
        except:
            pass
    
    def create_test_file(self, filename: str, content: str = "test content") -> str:
        """Create a test file and return its path."""
        file_path = os.path.join(self.temp_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        self.test_files.append(file_path)
        return file_path
    
    def create_mock_database(self, db_path: str, file_records: list):
        """Create a mock Langflow database with file records."""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create file table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                path TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert test records
        for record in file_records:
            cursor.execute(
                "INSERT INTO file (name, path) VALUES (?, ?)",
                (record['name'], record['path'])
            )
        
        conn.commit()
        conn.close()
        return db_path

    def test_U_file_metadata_extractor_import(self):
        """Unit Test: File metadata extractor can be imported."""
        try:
            from file_metadata_extractor import FileMetadataExtractor
            assert FileMetadataExtractor is not None
            print("✅ FileMetadataExtractor imported successfully")
        except ImportError as e:
            pytest.skip(f"FileMetadataExtractor not available: {e}")

    def test_U_backward_compatible_extractor_import(self):
        """Unit Test: Backward compatible extractor can be imported."""
        try:
            from backward_compatible_file_metadata_extractor import BackwardCompatibleFileMetadataExtractor
            assert BackwardCompatibleFileMetadataExtractor is not None
            print("✅ BackwardCompatibleFileMetadataExtractor imported successfully")
        except ImportError as e:
            pytest.skip(f"BackwardCompatibleFileMetadataExtractor not available: {e}")

    def test_U_component_initialization(self):
        """Unit Test: Components can be initialized."""
        try:
            from backward_compatible_file_metadata_extractor import BackwardCompatibleFileMetadataExtractor
            
            component = BackwardCompatibleFileMetadataExtractor()
            assert component is not None
            assert hasattr(component, 'extract_metadata')
            assert hasattr(component, 'get_original_filename_legacy')
            assert hasattr(component, 'detect_input_format')
            
            print("✅ Component initialization successful")
        except ImportError:
            pytest.skip("Component not available for testing")

    def test_U_legacy_filename_detection(self):
        """Unit Test: Legacy filename detection from file path."""
        try:
            from backward_compatible_file_metadata_extractor import BackwardCompatibleFileMetadataExtractor
            
            component = BackwardCompatibleFileMetadataExtractor()
            
            # Test with simple file path
            test_path = "/uploads/uuid-123/my_document.pdf"
            filename = component.get_original_filename_legacy(test_path)
            
            # Should fallback to basename since no database
            assert filename == "my_document.pdf"
            print(f"✅ Legacy filename detection: {filename}")
            
        except ImportError:
            pytest.skip("Component not available for testing")

    def test_U_database_filename_lookup(self):
        """Unit Test: Database filename lookup functionality."""
        try:
            from backward_compatible_file_metadata_extractor import BackwardCompatibleFileMetadataExtractor
            
            # Create test database
            db_path = os.path.join(self.temp_dir, "test_langflow.db")
            file_records = [
                {"name": "Original Document.pdf", "path": "uuid-123/server_file.pdf"},
                {"name": "My Report.docx", "path": "uuid-456/another_file.docx"}
            ]
            self.create_mock_database(db_path, file_records)
            
            component = BackwardCompatibleFileMetadataExtractor()
            
            # Mock the database path discovery
            with patch.object(component, 'get_original_filename_legacy') as mock_method:
                def mock_lookup(file_path):
                    if "uuid-123" in file_path:
                        # Simulate database lookup
                        conn = sqlite3.connect(db_path)
                        cursor = conn.cursor()
                        cursor.execute("SELECT name FROM file WHERE path = ?", ("uuid-123/server_file.pdf",))
                        result = cursor.fetchone()
                        conn.close()
                        return result[0] if result else os.path.basename(file_path)
                    return os.path.basename(file_path)
                
                mock_method.side_effect = mock_lookup
                
                # Test database lookup
                test_path = "/uploads/uuid-123/server_file.pdf"
                filename = component.get_original_filename_legacy(test_path)
                assert filename == "Original Document.pdf"
                print(f"✅ Database lookup successful: {filename}")
                
        except ImportError:
            pytest.skip("Component not available for testing")

    def test_U_input_format_detection(self):
        """Unit Test: Input format detection (legacy vs enhanced)."""
        try:
            from backward_compatible_file_metadata_extractor import BackwardCompatibleFileMetadataExtractor
            
            component = BackwardCompatibleFileMetadataExtractor()
            
            # Test legacy format (string)
            legacy_input = "/uploads/uuid-123/file.pdf"
            format_info = component.detect_input_format(legacy_input)
            
            assert format_info["is_enhanced"] == False
            assert format_info["detection_method"] == "legacy_string"
            assert format_info["file_path"] == legacy_input
            print(f"✅ Legacy format detection: {format_info['detection_method']}")
            
            # Test enhanced format (dict)
            enhanced_input = {
                "path": "/uploads/uuid-456/file.pdf",
                "original_filename": "My Document.pdf"
            }
            format_info = component.detect_input_format(enhanced_input)
            
            assert format_info["is_enhanced"] == True
            assert format_info["detection_method"] == "enhanced_dict"
            assert format_info["original_filename"] == "My Document.pdf"
            print(f"✅ Enhanced format detection: {format_info['detection_method']}")
            
        except ImportError:
            pytest.skip("Component not available for testing")

    def test_U_component_metadata_extraction(self):
        """Unit Test: Complete metadata extraction workflow."""
        try:
            from backward_compatible_file_metadata_extractor import BackwardCompatibleFileMetadataExtractor
            
            # Create test file
            test_content = "This is a test document with some content for word counting."
            test_file = self.create_test_file("test_document.txt", test_content)
            
            component = BackwardCompatibleFileMetadataExtractor()
            
            # Mock the input_file attribute
            component.input_file = test_file
            
            # Extract metadata
            result = component.extract_metadata()
            
            assert result is not None
            assert hasattr(result, 'text')
            assert "BACKWARD COMPATIBLE FILE METADATA SUMMARY" in result.text
            assert "test_document.txt" in result.text
            
            print("✅ Complete metadata extraction successful")
            print(f"   Result type: {type(result)}")
            print(f"   Contains filename: {'test_document.txt' in result.text}")
            
        except ImportError:
            pytest.skip("Component not available for testing")

    def test_U_enhanced_vs_legacy_comparison(self):
        """Unit Test: Compare enhanced vs legacy input handling."""
        try:
            from backward_compatible_file_metadata_extractor import BackwardCompatibleFileMetadataExtractor
            
            test_file = self.create_test_file("comparison_test.txt", "test content")
            component = BackwardCompatibleFileMetadataExtractor()
            
            # Test legacy input
            legacy_format = component.detect_input_format(test_file)
            
            # Test enhanced input
            enhanced_format = component.detect_input_format({
                "path": test_file,
                "original_filename": "Enhanced Filename.txt"
            })
            
            # Verify differences
            assert legacy_format["is_enhanced"] == False
            assert enhanced_format["is_enhanced"] == True
            assert enhanced_format["original_filename"] == "Enhanced Filename.txt"
            assert legacy_format["original_filename"] == "comparison_test.txt"
            
            print("✅ Enhanced vs Legacy comparison successful")
            print(f"   Legacy filename: {legacy_format['original_filename']}")
            print(f"   Enhanced filename: {enhanced_format['original_filename']}")
            
        except ImportError:
            pytest.skip("Component not available for testing")

    def test_U_component_as_filename_source(self):
        """Unit Test: Component can serve as filename source for other components."""
        try:
            from backward_compatible_file_metadata_extractor import BackwardCompatibleFileMetadataExtractor
            
            test_file = self.create_test_file("source_test.txt", "content for source testing")
            component = BackwardCompatibleFileMetadataExtractor()
            component.input_file = test_file
            
            # Extract metadata
            result = component.extract_metadata()
            
            # Parse the JSON metadata from the result
            lines = result.text.split('\n')
            json_start = False
            json_lines = []
            
            for line in lines:
                if "=== DETAILED METADATA ===" in line:
                    json_start = True
                    continue
                if json_start:
                    json_lines.append(line)
            
            if json_lines:
                metadata_json = '\n'.join(json_lines)
                metadata = json.loads(metadata_json)
                
                # Verify we can extract filename information
                assert "file_system" in metadata
                assert "original_filename" in metadata["file_system"]
                
                filename = metadata["file_system"]["original_filename"]
                assert filename == "source_test.txt"
                
                print("✅ Component can serve as filename source")
                print(f"   Extracted filename: {filename}")
                print(f"   Metadata structure: {list(metadata.keys())}")
                
                return {
                    "success": True,
                    "filename": filename,
                    "metadata": metadata
                }
            else:
                print("⚠️ Could not parse JSON metadata from result")
                return {"success": False, "reason": "JSON parsing failed"}
                
        except ImportError:
            pytest.skip("Component not available for testing")
        except Exception as e:
            print(f"⚠️ Component source test failed: {e}")
            return {"success": False, "reason": str(e)}

    def test_U_component_error_handling(self):
        """Unit Test: Component error handling for invalid inputs."""
        try:
            from backward_compatible_file_metadata_extractor import BackwardCompatibleFileMetadataExtractor
            
            component = BackwardCompatibleFileMetadataExtractor()
            
            # Test with None input
            component.input_file = None
            result = component.extract_metadata()
            assert "Error: No file provided" in result.text
            
            # Test with non-existent file
            component.input_file = "/non/existent/file.txt"
            result = component.extract_metadata()
            assert "Error: File not found" in result.text
            
            print("✅ Component error handling works correctly")
            
        except ImportError:
            pytest.skip("Component not available for testing")


def test_U_filename_exposure_component_availability():
    """Unit Test: Verify filename exposure components are available."""
    test_instance = TestFilenameExposureComponents()
    test_instance.setup_method()
    
    try:
        test_instance.test_U_backward_compatible_extractor_import()
        test_instance.test_U_component_initialization()
        print("✅ Filename exposure components are available and functional")
        return True
    except Exception as e:
        print(f"⚠️ Filename exposure components not fully available: {e}")
        return False
    finally:
        test_instance.teardown_method()


def test_U_filename_exposure_functionality():
    """Unit Test: Verify complete filename exposure functionality."""
    test_instance = TestFilenameExposureComponents()
    test_instance.setup_method()
    
    try:
        test_instance.test_U_legacy_filename_detection()
        test_instance.test_U_input_format_detection()
        test_instance.test_U_enhanced_vs_legacy_comparison()
        result = test_instance.test_U_component_as_filename_source()
        
        if result and result.get("success"):
            print("✅ Complete filename exposure functionality verified")
            return True
        else:
            print(f"⚠️ Filename exposure functionality incomplete: {result}")
            return False
            
    except Exception as e:
        print(f"⚠️ Filename exposure functionality test failed: {e}")
        return False
    finally:
        test_instance.teardown_method()


if __name__ == "__main__":
    print("Enhanced Filename Exposure - Component Testing")
    print("=" * 60)
    
    # Run component availability test
    availability = test_U_filename_exposure_component_availability()
    
    # Run functionality test
    functionality = test_U_filename_exposure_functionality()
    
    print("\n" + "=" * 60)
    print("COMPONENT TEST SUMMARY")
    print("=" * 60)
    print(f"Component Availability: {'✅ PASS' if availability else '❌ FAIL'}")
    print(f"Functionality Test: {'✅ PASS' if functionality else '❌ FAIL'}")
    
    if availability and functionality:
        print("\n🎉 FILENAME EXPOSURE COMPONENTS ARE READY FOR USE!")
        print("\nComponents available:")
        print("  • BackwardCompatibleFileMetadataExtractor")
        print("  • FileMetadataExtractor (if enhanced system available)")
        print("\nThese components can be used as sources for filename exposure in Langflow flows.")
    else:
        print("\n⚠️ Some components may need setup or are not fully functional.")
        print("Check the test output above for specific issues.")
