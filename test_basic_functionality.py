#!/usr/bin/env python3
"""
Basic functionality test for VS Code Test Explorer.

This is a minimal test file to verify that pytest and VS Code Test Explorer work correctly.
"""

import os
import sys
import tempfile
import pytest


class TestBasicFunctionality:
    """Basic functionality tests that should always work."""
    
    def test_U_python_version(self):
        """Unit Test: Python version is acceptable."""
        version = sys.version_info
        assert version.major >= 3
        assert version.minor >= 8
        print(f"PASS: Python version: {version.major}.{version.minor}.{version.micro}")

    def test_U_file_operations(self):
        """Unit Test: Basic file operations."""
        # Test file creation and deletion
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("test content")
            temp_path = f.name
        
        try:
            # Test file exists
            assert os.path.exists(temp_path)
            
            # Test file reading
            with open(temp_path, 'r') as f:
                content = f.read()
            assert content == "test content"
            
            print("PASS: File operations work correctly")
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_U_path_operations(self):
        """Unit Test: Basic path operations."""
        test_path = "/test/path/file.txt"

        # Test basename
        basename = os.path.basename(test_path)
        assert basename == "file.txt"

        # Test dirname
        dirname = os.path.dirname(test_path)
        assert dirname == "/test/path"

        # Test splitext
        name, ext = os.path.splitext(basename)
        assert name == "file"
        assert ext == ".txt"

        print("PASS: Path operations work correctly")

    def test_U_string_operations(self):
        """Unit Test: Basic string operations."""
        test_string = "Hello, World!"

        assert test_string.lower() == "hello, world!"
        assert test_string.upper() == "HELLO, WORLD!"
        assert "World" in test_string
        assert test_string.startswith("Hello")
        assert test_string.endswith("!")

        print("PASS: String operations work correctly")

    def test_U_list_operations(self):
        """Unit Test: Basic list operations."""
        test_list = [1, 2, 3, 4, 5]

        assert len(test_list) == 5
        assert test_list[0] == 1
        assert test_list[-1] == 5
        assert 3 in test_list
        assert max(test_list) == 5
        assert min(test_list) == 1

        print("PASS: List operations work correctly")


class TestEnvironmentChecks:
    """Environment and system checks."""

    def test_S_current_directory(self):
        """System Test: Current working directory access."""
        cwd = os.getcwd()
        assert cwd is not None
        assert len(cwd) > 0
        assert os.path.exists(cwd)
        print(f"PASS: Current directory: {cwd}")

    def test_S_environment_variables(self):
        """System Test: Environment variable access."""
        # Test PATH variable (should exist on all systems)
        path = os.environ.get('PATH')
        assert path is not None
        assert len(path) > 0
        print("PASS: Environment variables accessible")

    def test_S_temp_directory(self):
        """System Test: Temporary directory access."""
        temp_dir = tempfile.gettempdir()
        assert temp_dir is not None
        assert os.path.exists(temp_dir)
        assert os.path.isdir(temp_dir)
        print(f"PASS: Temp directory: {temp_dir}")


class TestPytestFeatures:
    """Test pytest-specific features."""

    @pytest.mark.parametrize("input,expected", [
        ("hello", "HELLO"),
        ("world", "WORLD"),
        ("test", "TEST"),
    ])
    def test_U_parametrized(self, input, expected):
        """Unit Test: Parametrized test functionality."""
        assert input.upper() == expected
        print(f"PASS: Parametrized test: {input} -> {expected}")

    def test_U_fixture_usage(self, tmp_path):
        """Unit Test: Pytest fixture usage."""
        # tmp_path is a pytest fixture that provides a temporary directory
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        assert test_file.exists()
        assert test_file.read_text() == "test content"
        print(f"PASS: Fixture usage: {tmp_path}")

    def test_U_exception_handling(self):
        """Unit Test: Exception handling in tests."""
        with pytest.raises(ZeroDivisionError):
            _ = 1 / 0

        with pytest.raises(ValueError):
            int("not_a_number")

        print("PASS: Exception handling works correctly")


# Standalone functions for direct execution
def test_U_standalone_basic():
    """Unit Test: Standalone test function."""
    assert 1 + 1 == 2
    print("PASS: Standalone basic test passed")


def test_U_standalone_file():
    """Unit Test: Standalone file test function."""
    with tempfile.NamedTemporaryFile(mode='w', delete=True) as f:
        f.write("test")
        f.flush()
        assert os.path.exists(f.name)
    print("PASS: Standalone file test passed")


if __name__ == "__main__":
    # Direct execution mode
    print("Basic Functionality Tests")
    print("=" * 40)
    
    try:
        test_U_standalone_basic()
        test_U_standalone_file()
        print("\nPASS: All standalone tests passed!")
        print("\nTo run with pytest:")
        print("python -m pytest test_basic_functionality.py -v")
    except Exception as e:
        print(f"\nFAIL: Test failed: {e}")
        sys.exit(1)
