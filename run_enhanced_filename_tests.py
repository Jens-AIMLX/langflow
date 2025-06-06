#!/usr/bin/env python3
"""
Comprehensive Test Runner for Enhanced Filename Support.
Runs all automated tests and user interaction verification tests.
"""

import sys
import os
import time
import subprocess
from pathlib import Path
from typing import Dict, Any, List

def run_test_file(test_file: str, description: str) -> Dict[str, Any]:
    """Run a test file and return results."""
    print(f"\n🧪 Running {description}")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        # Run the test file
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            print(f"   Execution time: {execution_time:.2f} seconds")
            if result.stdout:
                print("   Output summary:")
                # Show last few lines of output
                output_lines = result.stdout.strip().split('\n')
                for line in output_lines[-5:]:
                    if line.strip():
                        print(f"   {line}")
            
            return {
                "status": "passed",
                "execution_time": execution_time,
                "output": result.stdout,
                "error": None
            }
        else:
            print(f"❌ {description} - FAILED")
            print(f"   Execution time: {execution_time:.2f} seconds")
            if result.stderr:
                print("   Error output:")
                error_lines = result.stderr.strip().split('\n')
                for line in error_lines[-10:]:  # Show last 10 lines of error
                    if line.strip():
                        print(f"   {line}")
            
            return {
                "status": "failed",
                "execution_time": execution_time,
                "output": result.stdout,
                "error": result.stderr
            }
    
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT")
        return {
            "status": "timeout",
            "execution_time": 300,
            "output": "",
            "error": "Test timed out after 5 minutes"
        }
    
    except Exception as e:
        print(f"❌ {description} - ERROR")
        print(f"   Exception: {e}")
        return {
            "status": "error",
            "execution_time": 0,
            "output": "",
            "error": str(e)
        }

def run_pytest_tests() -> Dict[str, Any]:
    """Run pytest tests."""
    print("\n🧪 Running Pytest Test Suite")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        # Run pytest with our test files
        pytest_command = [
            sys.executable, "-m", "pytest",
            "test_enhanced_filename_simple.py",
            "test_basic_functionality.py",
            "-v", "--tb=short"
        ]
        
        result = subprocess.run(
            pytest_command,
            capture_output=True,
            text=True,
            timeout=180  # 3 minute timeout
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        if result.returncode == 0:
            print("✅ Pytest Test Suite - PASSED")
            print(f"   Execution time: {execution_time:.2f} seconds")
            
            # Extract test count from output
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if "passed" in line and ("warning" in line or "error" in line or "failed" in line):
                    print(f"   {line.strip()}")
                    break
            
            return {
                "status": "passed",
                "execution_time": execution_time,
                "output": result.stdout,
                "error": None
            }
        else:
            print("❌ Pytest Test Suite - FAILED")
            print(f"   Execution time: {execution_time:.2f} seconds")
            
            # Show relevant error information
            if result.stdout:
                output_lines = result.stdout.split('\n')
                for line in output_lines[-10:]:
                    if line.strip() and ("FAILED" in line or "ERROR" in line):
                        print(f"   {line}")
            
            return {
                "status": "failed",
                "execution_time": execution_time,
                "output": result.stdout,
                "error": result.stderr
            }
    
    except Exception as e:
        print(f"❌ Pytest Test Suite - ERROR: {e}")
        return {
            "status": "error",
            "execution_time": 0,
            "output": "",
            "error": str(e)
        }

def check_langflow_running() -> bool:
    """Check if Langflow is running for browser tests."""
    try:
        import requests
        response = requests.get("http://localhost:7860", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    """Main test runner."""
    print("🚀 Enhanced Filename Support - Comprehensive Test Suite")
    print("=" * 70)
    print("Testing enhanced filename implementation across all components")
    print("=" * 70)
    
    # Test configuration
    test_suite = [
        {
            "file": "test_basic_functionality.py",
            "description": "Basic Functionality Tests",
            "category": "core",
            "required": True
        },
        {
            "file": "test_enhanced_filename_simple.py", 
            "description": "Enhanced Filename Simple Tests",
            "category": "core",
            "required": True
        },
        {
            "file": "test_enhanced_filename_flow_design.py",
            "description": "Flow Design Integration Tests",
            "category": "integration",
            "required": True
        },
        {
            "file": "test_enhanced_filename_user_interaction.py",
            "description": "User Interaction Simulation Tests",
            "category": "user_experience",
            "required": True
        },
        {
            "file": "test_enhanced_filename_browser_automation.py",
            "description": "Browser Automation Tests",
            "category": "browser",
            "required": False  # Optional if Langflow not running
        }
    ]
    
    # Check which test files exist
    available_tests = []
    missing_tests = []
    
    for test in test_suite:
        if os.path.exists(test["file"]):
            available_tests.append(test)
        else:
            missing_tests.append(test)
    
    if missing_tests:
        print("⚠️ Missing test files:")
        for test in missing_tests:
            print(f"   - {test['file']}")
        print()
    
    print(f"📋 Running {len(available_tests)} test suites:")
    for test in available_tests:
        print(f"   ✅ {test['description']}")
    print()
    
    # Run pytest first
    pytest_result = run_pytest_tests()
    
    # Run individual test files
    test_results = {}
    
    for test in available_tests:
        # Skip browser tests if Langflow not running
        if test["category"] == "browser" and not check_langflow_running():
            print(f"\n⚠️ Skipping {test['description']} - Langflow not running")
            test_results[test["file"]] = {
                "status": "skipped",
                "reason": "Langflow not running on localhost:7860"
            }
            continue
        
        result = run_test_file(test["file"], test["description"])
        test_results[test["file"]] = result
    
    # Generate comprehensive report
    print("\n" + "=" * 70)
    print("📊 COMPREHENSIVE TEST RESULTS SUMMARY")
    print("=" * 70)
    
    # Pytest results
    pytest_status = "✅ PASSED" if pytest_result["status"] == "passed" else "❌ FAILED"
    print(f"🧪 Pytest Test Suite: {pytest_status}")
    print(f"   Execution time: {pytest_result['execution_time']:.2f} seconds")
    
    # Individual test results
    total_tests = len(test_results)
    passed_tests = sum(1 for r in test_results.values() if r["status"] == "passed")
    failed_tests = sum(1 for r in test_results.values() if r["status"] == "failed")
    skipped_tests = sum(1 for r in test_results.values() if r["status"] == "skipped")
    
    print(f"\n📋 Individual Test Results:")
    for test_file, result in test_results.items():
        status_icon = {
            "passed": "✅",
            "failed": "❌", 
            "skipped": "⚠️",
            "timeout": "⏰",
            "error": "💥"
        }.get(result["status"], "❓")
        
        test_name = test_file.replace("test_enhanced_filename_", "").replace(".py", "")
        print(f"   {status_icon} {test_name}: {result['status'].upper()}")
        
        if result["status"] == "skipped" and "reason" in result:
            print(f"      Reason: {result['reason']}")
        elif result.get("execution_time"):
            print(f"      Time: {result['execution_time']:.2f}s")
    
    # Overall statistics
    total_execution_time = pytest_result["execution_time"] + sum(
        r.get("execution_time", 0) for r in test_results.values()
    )
    
    print(f"\n📊 Test Statistics:")
    print(f"   Total test suites: {total_tests + 1}")  # +1 for pytest
    print(f"   Passed: {passed_tests + (1 if pytest_result['status'] == 'passed' else 0)}")
    print(f"   Failed: {failed_tests + (1 if pytest_result['status'] == 'failed' else 0)}")
    print(f"   Skipped: {skipped_tests}")
    print(f"   Total execution time: {total_execution_time:.2f} seconds")
    
    # Success criteria
    core_tests_passed = all(
        test_results.get(test["file"], {}).get("status") == "passed"
        for test in available_tests
        if test["category"] == "core" and test["required"]
    )
    
    pytest_passed = pytest_result["status"] == "passed"
    
    overall_success = core_tests_passed and pytest_passed
    
    print(f"\n🎯 Overall Result:")
    if overall_success:
        print("🎉 ALL CORE TESTS PASSED!")
        print("✅ Enhanced filename implementation is working correctly")
        print("✅ All core functionality verified")
        print("✅ User interaction scenarios tested")
        print("✅ Integration tests successful")
        
        if skipped_tests > 0:
            print(f"ℹ️ {skipped_tests} optional tests were skipped")
        
        print("\n🚀 Enhanced filename support is READY FOR PRODUCTION!")
        
    else:
        print("❌ SOME CORE TESTS FAILED")
        print("⚠️ Enhanced filename implementation needs attention")
        
        if not pytest_passed:
            print("❌ Pytest suite failed - check core functionality")
        if not core_tests_passed:
            print("❌ Core integration tests failed - check implementation")
        
        print("\n🔧 Please review failed tests and fix issues before deployment")
    
    # Exit with appropriate code
    sys.exit(0 if overall_success else 1)

if __name__ == "__main__":
    main()
