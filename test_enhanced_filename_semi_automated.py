#!/usr/bin/env python3
"""
Semi-Automated Tests for Enhanced Filename Support in Langflow.
Combines Playwright automation with user interaction and verification.
All tests are visible and executable in VS Code Test Explorer.
"""

import sys
import os
import tempfile
import asyncio
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
import pytest

# Try to import Playwright for browser automation
try:
    from playwright.async_api import async_playwright, Page, Browser, BrowserContext
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

class UserInteractionHelper:
    """Helper class for user interaction and verification."""
    
    @staticmethod
    def ask_user_confirmation(question: str, details: str = "") -> bool:
        """Ask user for confirmation with details."""
        print("\n" + "=" * 60)
        print("USER VERIFICATION REQUIRED")
        print("=" * 60)
        print(f"QUESTION: {question}")
        if details:
            print(f"DETAILS: {details}")
        print("=" * 60)
        
        while True:
            response = input("Did you see the expected behavior? (y/n/skip): ").lower().strip()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            elif response in ['s', 'skip']:
                pytest.skip("User chose to skip this verification")
            else:
                print("Please enter 'y' for yes, 'n' for no, or 'skip' to skip this test")
    
    @staticmethod
    def show_user_instructions(title: str, instructions: List[str], expected_result: str):
        """Show detailed instructions to the user."""
        print("\n" + "=" * 60)
        print(f"MANUAL TEST: {title}")
        print("=" * 60)
        print("INSTRUCTIONS:")
        for i, instruction in enumerate(instructions, 1):
            print(f"  {i}. {instruction}")
        print(f"\nEXPECTED RESULT: {expected_result}")
        print("=" * 60)
        input("Press ENTER when you have completed the instructions...")

class TestEnhancedFilenameSemiAutomated:
    """Semi-automated tests combining automation with user verification."""
    
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        self.test_files = []
        self.temp_dir = tempfile.mkdtemp()
        self.user_helper = UserInteractionHelper()
    
    async def setup_browser(self):
        """Setup browser for automated parts."""
        if not PLAYWRIGHT_AVAILABLE:
            pytest.skip("Playwright not available for browser automation")
        
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False)  # Visible for user
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
    
    async def teardown_browser(self):
        """Cleanup browser resources."""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
    
    def create_test_file(self, filename: str, content: str = "Test content") -> str:
        """Create a test file for testing."""
        file_path = os.path.join(self.temp_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        self.test_files.append(file_path)
        return file_path
    
    @pytest.mark.semi_automated
    @pytest.mark.browser_automation
    async def test_UI_langflow_startup_and_enhanced_features(self):
        """Test Langflow startup with enhanced filename features - Semi-automated."""
        print("SEMI-AUTO: Testing Langflow Startup with Enhanced Features")
        
        # Step 1: Automated - Check if Langflow is running
        try:
            import requests
            response = requests.get("http://localhost:7860", timeout=5)
            langflow_running = response.status_code == 200
        except:
            langflow_running = False
        
        if not langflow_running:
            # Manual step - User needs to start Langflow
            self.user_helper.show_user_instructions(
                "Start Enhanced Langflow",
                [
                    "Open command prompt in the Langflow directory",
                    "Run: run_langflow.bat",
                    "Wait for the enhanced startup message showing:",
                    "  - 'Original filename preservation: ENABLED'",
                    "  - 'Enhanced metadata extraction: ENABLED'",
                    "  - 'File metadata extractors: READY'",
                    "Open browser to: http://localhost:7860"
                ],
                "Langflow UI loads successfully with enhanced features enabled"
            )
            
            # Verify user completed the startup
            startup_confirmed = self.user_helper.ask_user_confirmation(
                "Did Langflow start successfully with enhanced features enabled?",
                "You should see the enhanced startup banner and Langflow UI should be accessible"
            )
            assert startup_confirmed, "Langflow startup with enhanced features failed"
        
        # Step 2: Automated - Navigate to Langflow
        await self.setup_browser()
        try:
            await self.page.goto("http://localhost:7860", timeout=30000)
            await self.page.wait_for_load_state("networkidle")
            
            # Step 3: Semi-automated - Verify UI loaded
            ui_loaded = self.user_helper.ask_user_confirmation(
                "Did the Langflow UI load completely?",
                "You should see the main Langflow interface with flow designer"
            )
            assert ui_loaded, "Langflow UI did not load properly"
            
        finally:
            await self.teardown_browser()
    
    @pytest.mark.semi_automated
    @pytest.mark.user_interaction
    async def test_UI_file_upload_with_original_filename_display(self):
        """Test file upload with original filename display - Semi-automated."""
        print("SEMI-AUTO: Testing File Upload with Original Filename Display")
        
        # Step 1: Automated - Create test files
        test_files = [
            ("my_important_document.pdf", "PDF content for testing"),
            ("quarterly_report_Q4_2024.xlsx", "Excel data for testing"),
            ("meeting_notes_jan_15.docx", "Word document for testing")
        ]
        
        created_files = []
        for filename, content in test_files:
            file_path = self.create_test_file(filename, content)
            created_files.append((filename, file_path))
        
        # Step 2: Manual - User uploads files and verifies filename display
        self.user_helper.show_user_instructions(
            "Upload Files and Verify Original Filename Display",
            [
                "In Langflow UI, create a new flow or open existing flow",
                "Add a 'File' component to the canvas",
                "Click on the File component to configure it",
                f"Upload the test file: {created_files[0][1]}",
                "Observe the filename display in the component",
                "Repeat for other test files if desired"
            ],
            f"Original filename '{created_files[0][0]}' should be displayed (not a UUID)"
        )
        
        # Step 3: User verification
        filename_preserved = self.user_helper.ask_user_confirmation(
            f"Did you see the original filename '{created_files[0][0]}' displayed in the File component?",
            "The component should show the original filename, not a server-generated UUID"
        )
        assert filename_preserved, "Original filename was not preserved in UI display"
        
        # Step 4: Test multiple files
        multiple_files_test = self.user_helper.ask_user_confirmation(
            "Did you test multiple file types and see original filenames for all?",
            "All uploaded files should display their original names"
        )
        assert multiple_files_test, "Multiple file upload test failed"
    
    @pytest.mark.semi_automated
    @pytest.mark.user_interaction
    def test_UI_file_metadata_extractor_component_availability(self):
        """Test File Metadata Extractor component availability - Semi-automated."""
        print("SEMI-AUTO: Testing File Metadata Extractor Component Availability")
        
        # Manual step - User searches for and configures component
        self.user_helper.show_user_instructions(
            "Find and Configure File Metadata Extractor Component",
            [
                "In Langflow UI, look at the component sidebar",
                "Search for 'File Metadata Extractor' in the component search",
                "Drag the 'File Metadata Extractor' component to the canvas",
                "Click on the component to see its configuration options",
                "Look for enhanced options like 'Extract Original Filename'",
                "Connect a File component to the File Metadata Extractor"
            ],
            "File Metadata Extractor component should be available with enhanced options"
        )
        
        # User verification
        component_found = self.user_helper.ask_user_confirmation(
            "Did you find the 'File Metadata Extractor' component in the component library?",
            "The component should be searchable and draggable to the canvas"
        )
        assert component_found, "File Metadata Extractor component not found"
        
        enhanced_options = self.user_helper.ask_user_confirmation(
            "Did you see enhanced configuration options in the File Metadata Extractor?",
            "Options should include settings for original filename extraction"
        )
        assert enhanced_options, "Enhanced configuration options not available"
    
    @pytest.mark.semi_automated
    @pytest.mark.user_interaction
    def test_UI_flow_execution_with_filename_preservation(self):
        """Test flow execution with filename preservation - Semi-automated."""
        print("SEMI-AUTO: Testing Flow Execution with Filename Preservation")
        
        # Create test file
        test_filename = "user_test_document.pdf"
        test_file_path = self.create_test_file(test_filename, "PDF content for flow execution test")
        
        # Manual step - User creates and executes flow
        self.user_helper.show_user_instructions(
            "Create and Execute Flow with File Processing",
            [
                "Create a flow: File Input -> File Metadata Extractor -> Text Output",
                "Upload the test file to the File Input component",
                f"Use the test file: {test_file_path}",
                "Configure the File Metadata Extractor to extract original filename",
                "Connect the components in sequence",
                "Execute the flow by clicking the Run button",
                "Observe the output in the Text Output component"
            ],
            f"Output should contain the original filename '{test_filename}'"
        )
        
        # User verification
        flow_executed = self.user_helper.ask_user_confirmation(
            "Did the flow execute successfully?",
            "All components should process without errors"
        )
        assert flow_executed, "Flow execution failed"
        
        filename_in_output = self.user_helper.ask_user_confirmation(
            f"Did you see the original filename '{test_filename}' in the flow output?",
            "The Text Output should display the original filename, not a UUID"
        )
        assert filename_in_output, "Original filename not preserved in flow output"
    
    @pytest.mark.semi_automated
    @pytest.mark.user_interaction
    def test_UI_error_handling_with_filename_context(self):
        """Test error handling with filename context - Semi-automated."""
        print("SEMI-AUTO: Testing Error Handling with Filename Context")
        
        # Create problematic test file
        problematic_filename = "test_file.unknown"
        problematic_file_path = self.create_test_file(problematic_filename, "Content with unknown extension")
        
        # Manual step - User tests error scenarios
        self.user_helper.show_user_instructions(
            "Test Error Handling with Original Filename Context",
            [
                "Try to upload a file with unsupported extension",
                f"Use the test file: {problematic_file_path}",
                "Attempt to process it through File Metadata Extractor",
                "Observe any error messages that appear",
                "Check if error messages include the original filename",
                "Try uploading a very large file (if available)",
                "Test with a corrupted file (rename .txt to .pdf)"
            ],
            "Error messages should include the original filename for user clarity"
        )
        
        # User verification
        error_occurred = self.user_helper.ask_user_confirmation(
            "Did you encounter error messages during testing?",
            "Some operations should produce errors for testing purposes"
        )
        
        if error_occurred:
            filename_in_error = self.user_helper.ask_user_confirmation(
                f"Did error messages include the original filename '{problematic_filename}'?",
                "Error messages should help users identify which file caused the problem"
            )
            assert filename_in_error, "Error messages did not include original filename context"
        else:
            pytest.skip("No errors occurred during testing - unable to verify error message quality")
    
    @pytest.mark.semi_automated
    @pytest.mark.user_interaction
    def test_UI_user_experience_quality_assessment(self):
        """Test overall user experience quality - Semi-automated."""
        print("SEMI-AUTO: Testing User Experience Quality Assessment")
        
        # Manual step - User evaluates overall experience
        self.user_helper.show_user_instructions(
            "Evaluate Overall User Experience with Enhanced Filename Support",
            [
                "Use the enhanced filename features for 5-10 minutes",
                "Upload various file types and observe filename handling",
                "Create different flows using file processing components",
                "Evaluate the clarity of filename display throughout the UI",
                "Assess whether the enhanced features improve your workflow",
                "Consider if the original filename preservation is helpful",
                "Check if the interface is intuitive and user-friendly"
            ],
            "Enhanced filename support should provide a better user experience"
        )
        
        # User experience evaluation
        ui_clarity = self.user_helper.ask_user_confirmation(
            "Are original filenames clearly visible throughout the Langflow UI?",
            "Filenames should be easy to identify in components and outputs"
        )
        assert ui_clarity, "UI clarity for filename display is insufficient"
        
        workflow_improvement = self.user_helper.ask_user_confirmation(
            "Do the enhanced filename features improve your workflow?",
            "You should be able to easily track and identify files in your flows"
        )
        assert workflow_improvement, "Enhanced filename features do not improve workflow"
        
        overall_satisfaction = self.user_helper.ask_user_confirmation(
            "Are you satisfied with the overall enhanced filename implementation?",
            "The features should feel natural and helpful"
        )
        assert overall_satisfaction, "Overall user satisfaction with enhanced filename features is low"

# Async test runner for pytest compatibility
@pytest.mark.semi_automated
async def test_run_all_semi_automated_tests():
    """Run all semi-automated tests - Entry point for pytest."""
    test_instance = TestEnhancedFilenameSemiAutomated()
    
    try:
        # Run tests that require browser automation
        await test_instance.test_UI_langflow_startup_and_enhanced_features()
        await test_instance.test_UI_file_upload_with_original_filename_display()
        
        # Run tests that are purely manual with verification
        test_instance.test_UI_file_metadata_extractor_component_availability()
        test_instance.test_UI_flow_execution_with_filename_preservation()
        test_instance.test_UI_error_handling_with_filename_context()
        test_instance.test_UI_user_experience_quality_assessment()
        
        print("\nSUCCESS: All semi-automated tests completed successfully!")
        print("PASS: Enhanced filename support verified through user interaction")
        print("PASS: User experience quality confirmed")
        
    except Exception as e:
        print(f"FAIL: Semi-automated test failed: {e}")
        raise
    finally:
        # Cleanup
        for file_path in test_instance.test_files:
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
            except:
                pass

if __name__ == "__main__":
    # Direct execution for testing
    asyncio.run(test_run_all_semi_automated_tests())
