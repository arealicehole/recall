#!/usr/bin/env python3
"""
Comprehensive Test Runner for Recall Application
Runs both GUI tests and unit tests with detailed reporting
"""

import sys
import os
import argparse
import subprocess
import time
from pathlib import Path

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def check_dependencies():
    """Check if required testing dependencies are installed"""
    print("🔍 Checking test dependencies...")
    
    required_packages = [
        'pytest',
        'customtkinter',
        'flask',
        'pydub',
        'python-dotenv',
        'assemblyai'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"   ❌ {package} (missing)")
    
    if missing_packages:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing_packages)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    print("✅ All test dependencies available")
    return True

def run_unit_tests(verbose=False):
    """Run unit tests using pytest"""
    print("\n" + "=" * 60)
    print("🧪 RUNNING UNIT TESTS")
    print("=" * 60)
    
    # Ensure tests directory exists
    tests_dir = os.path.join(project_root, 'tests')
    if not os.path.exists(tests_dir):
        print("❌ Tests directory not found")
        return False
    
    # Run pytest
    cmd = [
        sys.executable, '-m', 'pytest', 
        tests_dir,
        '--tb=short',  # Short traceback format
        '-v' if verbose else '-q'  # Verbose or quiet
    ]
    
    print(f"Running: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, cwd=project_root)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running unit tests: {e}")
        return False

def run_gui_tests():
    """Run GUI tests"""
    print("\n" + "=" * 60)
    print("🖥️  RUNNING GUI TESTS")
    print("=" * 60)
    
    gui_test_script = os.path.join(project_root, 'test_gui.py')
    
    if not os.path.exists(gui_test_script):
        print("❌ GUI test script not found")
        return False
    
    try:
        # Run GUI tests
        result = subprocess.run([sys.executable, gui_test_script], cwd=project_root)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running GUI tests: {e}")
        return False

def run_integration_tests():
    """Run integration tests"""
    print("\n" + "=" * 60)
    print("🔗 RUNNING INTEGRATION TESTS")
    print("=" * 60)
    
    integration_scripts = [
        'debug_transcription.py',
        'check_audio_content.py'
    ]
    
    results = []
    
    for script in integration_scripts:
        script_path = os.path.join(project_root, script)
        
        if not os.path.exists(script_path):
            print(f"⚠️  Integration test script not found: {script}")
            continue
        
        print(f"\n🔍 Running: {script}")
        print("-" * 30)
        
        try:
            result = subprocess.run([sys.executable, script_path], cwd=project_root)
            success = result.returncode == 0
            results.append(success)
            
            if success:
                print(f"✅ {script} completed successfully")
            else:
                print(f"❌ {script} failed")
                
        except Exception as e:
            print(f"❌ Error running {script}: {e}")
            results.append(False)
    
    return all(results) if results else False

def run_web_tests():
    """Run web deployment tests"""
    print("\n" + "=" * 60)
    print("🌐 RUNNING WEB DEPLOYMENT TESTS")
    print("=" * 60)
    
    # Check if deployment test script exists
    deployment_script = os.path.join(project_root, 'scripts', 'test_deployment.sh')
    
    if not os.path.exists(deployment_script):
        print("❌ Web deployment test script not found")
        return False
    
    print("🚀 Running web deployment tests...")
    print("⚠️  This may take several minutes...")
    print("-" * 50)
    
    try:
        # Make script executable on Unix systems
        if os.name != 'nt':  # Not Windows
            os.chmod(deployment_script, 0o755)
        
        # Run deployment tests
        if os.name == 'nt':  # Windows
            result = subprocess.run(['bash', deployment_script], cwd=project_root)
        else:  # Unix
            result = subprocess.run([deployment_script], cwd=project_root)
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running web deployment tests: {e}")
        return False

def generate_test_report(results):
    """Generate a comprehensive test report"""
    print("\n" + "=" * 60)
    print("📊 TEST REPORT")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    failed_tests = total_tests - passed_tests
    
    print(f"📈 Overall Results:")
    print(f"   Total Test Suites: {total_tests}")
    print(f"   ✅ Passed: {passed_tests}")
    print(f"   ❌ Failed: {failed_tests}")
    print(f"   📊 Success Rate: {(passed_tests / total_tests) * 100:.1f}%")
    
    print(f"\n📋 Detailed Results:")
    for test_name, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"   {test_name}: {status}")
    
    if failed_tests > 0:
        print(f"\n⚠️  {failed_tests} test suite(s) failed. Check the output above for details.")
        return False
    else:
        print(f"\n🎉 All test suites passed!")
        return True

def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(description='Run Recall application tests')
    parser.add_argument('--unit', action='store_true', help='Run unit tests only')
    parser.add_argument('--gui', action='store_true', help='Run GUI tests only')
    parser.add_argument('--integration', action='store_true', help='Run integration tests only')
    parser.add_argument('--web', action='store_true', help='Run web deployment tests only')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--skip-deps', action='store_true', help='Skip dependency check')
    
    args = parser.parse_args()
    
    print("🚀 Recall Application Test Suite")
    print("=" * 60)
    
    # Check dependencies unless skipped
    if not args.skip_deps:
        if not check_dependencies():
            print("❌ Dependency check failed. Use --skip-deps to ignore.")
            return False
    
    # Determine which tests to run
    run_all = not (args.unit or args.gui or args.integration or args.web)
    
    results = {}
    
    # Run unit tests
    if run_all or args.unit:
        results['Unit Tests'] = run_unit_tests(args.verbose)
    
    # Run GUI tests
    if run_all or args.gui:
        results['GUI Tests'] = run_gui_tests()
    
    # Run integration tests
    if run_all or args.integration:
        results['Integration Tests'] = run_integration_tests()
    
    # Run web deployment tests
    if run_all or args.web:
        results['Web Deployment Tests'] = run_web_tests()
    
    # Generate report
    if results:
        success = generate_test_report(results)
        return success
    else:
        print("❌ No tests were run")
        return False

if __name__ == "__main__":
    start_time = time.time()
    success = main()
    end_time = time.time()
    
    print(f"\n⏱️  Total test time: {end_time - start_time:.1f} seconds")
    
    if success:
        print("🎉 All tests completed successfully!")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Check the output above.")
        sys.exit(1) 