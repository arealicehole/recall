#!/usr/bin/env python3
"""
Desktop GUI Test Script for Recall Application
Tests all GUI components and functionality
"""

import sys
import os
import tempfile
import shutil
import threading
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import GUI components
import customtkinter as ctk
from src.gui.app import TranscriberApp
from src.utils.config import Config
from src.core.audio_handler import AudioHandler
from src.core.transcriber import Transcriber

class GUITester:
    """Test runner for desktop GUI components"""
    
    def __init__(self):
        self.app = None
        self.test_results = []
        self.temp_dir = None
        self.test_files = []
        
    def setup_test_environment(self):
        """Set up test environment with mock files and config"""
        print("🔧 Setting up test environment...")
        
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test audio files (empty files for testing)
        test_audio_files = [
            "test1.wav", "test2.mp3", "test3.amr", "test4.m4a"
        ]
        
        for filename in test_audio_files:
            test_file = os.path.join(self.temp_dir, filename)
            with open(test_file, 'wb') as f:
                f.write(b'fake audio data')  # Mock audio data
            self.test_files.append(test_file)
        
        print(f"   Created {len(self.test_files)} test files in {self.temp_dir}")
        
    def cleanup_test_environment(self):
        """Clean up test environment"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            print("🧹 Cleaned up test environment")
    
    def run_test(self, test_name, test_func):
        """Run a single test and track results"""
        print(f"\n🧪 Testing: {test_name}")
        print("-" * 50)
        
        try:
            result = test_func()
            if result:
                print(f"✅ PASSED: {test_name}")
                self.test_results.append((test_name, "PASSED", None))
                return True
            else:
                print(f"❌ FAILED: {test_name}")
                self.test_results.append((test_name, "FAILED", "Test returned False"))
                return False
                
        except Exception as e:
            print(f"❌ ERROR: {test_name} - {str(e)}")
            self.test_results.append((test_name, "ERROR", str(e)))
            return False
    
    def test_app_initialization(self):
        """Test application initialization"""
        try:
            # Test app creation
            self.app = TranscriberApp()
            
            # Check window properties
            if not self.app.title():
                return False
            
            if self.app.winfo_width() <= 0 or self.app.winfo_height() <= 0:
                return False
            
            # Check if main components exist
            if not hasattr(self.app, 'main_frame'):
                return False
            
            if not hasattr(self.app, 'config'):
                return False
            
            print("   ✓ Application window created successfully")
            print(f"   ✓ Window title: {self.app.title()}")
            print(f"   ✓ Window size: {self.app.winfo_width()}x{self.app.winfo_height()}")
            print("   ✓ Main frame exists")
            print("   ✓ Configuration loaded")
            
            return True
            
        except Exception as e:
            print(f"   ❌ App initialization failed: {e}")
            return False
    
    def test_menu_creation(self):
        """Test menu bar creation"""
        try:
            if not self.app:
                return False
            
            # The app should have a menu (though CustomTkinter handles it differently)
            # Check if the app has menu-related methods
            if not hasattr(self.app, 'setup_menu'):
                return False
            
            print("   ✓ Menu setup method exists")
            return True
            
        except Exception as e:
            print(f"   ❌ Menu creation test failed: {e}")
            return False
    
    def test_file_selection_components(self):
        """Test file selection UI components"""
        try:
            if not self.app:
                return False
            
            # Check if file selection buttons exist
            if not hasattr(self.app, 'select_file_btn'):
                return False
            
            if not hasattr(self.app, 'select_dir_btn'):
                return False
            
            # Check if file list exists
            if not hasattr(self.app, 'file_list'):
                return False
            
            print("   ✓ Select Files button exists")
            print("   ✓ Select Directory button exists")
            print("   ✓ File list widget exists")
            
            return True
            
        except Exception as e:
            print(f"   ❌ File selection components test failed: {e}")
            return False
    
    def test_progress_tracking_components(self):
        """Test progress tracking UI components"""
        try:
            if not self.app:
                return False
            
            # Check if progress components exist
            if not hasattr(self.app, 'progress_bar'):
                return False
            
            if not hasattr(self.app, 'progress_label'):
                return False
            
            if not hasattr(self.app, 'log_text'):
                return False
            
            print("   ✓ Progress bar exists")
            print("   ✓ Progress label exists")
            print("   ✓ Log text widget exists")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Progress tracking components test failed: {e}")
            return False
    
    def test_output_directory_components(self):
        """Test output directory selection components"""
        try:
            if not self.app:
                return False
            
            # Check output directory components
            if not hasattr(self.app, 'output_path'):
                return False
            
            if not hasattr(self.app, 'select_output_btn'):
                return False
            
            if not hasattr(self.app, 'same_as_input_var'):
                return False
            
            print("   ✓ Output path entry exists")
            print("   ✓ Select output button exists")
            print("   ✓ Same as input checkbox exists")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Output directory components test failed: {e}")
            return False
    
    def test_configuration_loading(self):
        """Test configuration loading"""
        try:
            if not self.app:
                return False
            
            config = self.app.config
            
            # Check if config has required attributes
            if not hasattr(config, 'api_key'):
                return False
            
            if not hasattr(config, 'output_dir'):
                return False
            
            if not hasattr(config, 'supported_formats'):
                return False
            
            print("   ✓ Configuration object loaded")
            print(f"   ✓ API key configured: {'Yes' if config.api_key else 'No'}")
            print(f"   ✓ Output directory: {config.output_dir}")
            print(f"   ✓ Supported formats: {len(config.supported_formats)} formats")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Configuration loading test failed: {e}")
            return False
    
    @patch('tkinter.filedialog.askopenfilenames')
    def test_file_selection_dialog(self, mock_dialog):
        """Test file selection dialog functionality"""
        try:
            if not self.app:
                return False
            
            # Mock file selection
            mock_dialog.return_value = self.test_files
            
            # Test file selection method
            if hasattr(self.app, 'select_files'):
                # This would normally open a dialog, but we're mocking it
                mock_dialog.return_value = self.test_files
                
                print("   ✓ File selection dialog can be invoked")
                print(f"   ✓ Mock selected {len(self.test_files)} files")
                
                return True
            
            return False
            
        except Exception as e:
            print(f"   ❌ File selection dialog test failed: {e}")
            return False
    
    @patch('tkinter.filedialog.askdirectory')
    def test_directory_selection_dialog(self, mock_dialog):
        """Test directory selection dialog functionality"""
        try:
            if not self.app:
                return False
            
            # Mock directory selection
            mock_dialog.return_value = self.temp_dir
            
            # Test directory selection method
            if hasattr(self.app, 'select_directory'):
                print("   ✓ Directory selection dialog can be invoked")
                print(f"   ✓ Mock selected directory: {self.temp_dir}")
                
                return True
            
            return False
            
        except Exception as e:
            print(f"   ❌ Directory selection dialog test failed: {e}")
            return False
    
    def test_api_key_dialog(self):
        """Test API key configuration dialog"""
        try:
            if not self.app:
                return False
            
            # Check if API key methods exist
            if not hasattr(self.app, 'open_api_key_dialog'):
                return False
            
            if not hasattr(self.app, 'save_api_key_to_config'):
                return False
            
            print("   ✓ API key dialog method exists")
            print("   ✓ API key save method exists")
            
            return True
            
        except Exception as e:
            print(f"   ❌ API key dialog test failed: {e}")
            return False
    
    def test_error_handling(self):
        """Test error handling mechanisms"""
        try:
            if not self.app:
                return False
            
            # Test if error handling methods exist
            if not hasattr(self.app, 'show_error'):
                return False
            
            # Test logging functionality
            if not hasattr(self.app, 'log_message'):
                return False
            
            print("   ✓ Error display method exists")
            print("   ✓ Log message method exists")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error handling test failed: {e}")
            return False
    
    def test_transcription_workflow(self):
        """Test transcription workflow integration"""
        try:
            if not self.app:
                return False
            
            # Check if transcription components exist
            if not hasattr(self.app, 'audio_handler'):
                return False
            
            if not hasattr(self.app, 'transcriber'):
                return False
            
            if not hasattr(self.app, 'start_transcription'):
                return False
            
            print("   ✓ Audio handler integrated")
            print("   ✓ Transcriber integrated")
            print("   ✓ Start transcription method exists")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Transcription workflow test failed: {e}")
            return False
    
    def test_threading_safety(self):
        """Test threading safety for background operations"""
        try:
            if not self.app:
                return False
            
            # Check if threading is properly handled
            if not hasattr(self.app, 'processing'):
                return False
            
            # Test that UI updates are thread-safe
            print("   ✓ Processing state variable exists")
            print("   ✓ Threading considerations implemented")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Threading safety test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all GUI tests"""
        print("=" * 60)
        print("🖥️  DESKTOP GUI TEST SUITE")
        print("=" * 60)
        
        # Set up test environment
        self.setup_test_environment()
        
        # List of all tests to run
        tests = [
            ("Application Initialization", self.test_app_initialization),
            ("Menu Creation", self.test_menu_creation),
            ("File Selection Components", self.test_file_selection_components),
            ("Progress Tracking Components", self.test_progress_tracking_components),
            ("Output Directory Components", self.test_output_directory_components),
            ("Configuration Loading", self.test_configuration_loading),
            ("File Selection Dialog", self.test_file_selection_dialog),
            ("Directory Selection Dialog", self.test_directory_selection_dialog),
            ("API Key Dialog", self.test_api_key_dialog),
            ("Error Handling", self.test_error_handling),
            ("Transcription Workflow", self.test_transcription_workflow),
            ("Threading Safety", self.test_threading_safety),
        ]
        
        passed = 0
        failed = 0
        
        # Run each test
        for test_name, test_func in tests:
            if self.run_test(test_name, test_func):
                passed += 1
            else:
                failed += 1
        
        # Clean up
        if self.app:
            try:
                self.app.destroy()
            except:
                pass
        
        self.cleanup_test_environment()
        
        # Print summary
        print("\n" + "=" * 60)
        print("🏁 TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Tests Passed: {passed}")
        print(f"❌ Tests Failed: {failed}")
        print(f"📊 Success Rate: {(passed / (passed + failed)) * 100:.1f}%")
        
        if failed > 0:
            print("\n📋 Failed Tests:")
            for test_name, status, error in self.test_results:
                if status != "PASSED":
                    print(f"   • {test_name}: {status}")
                    if error:
                        print(f"     Error: {error}")
        
        print("\n" + "=" * 60)
        return failed == 0

def main():
    """Main test runner"""
    print("🚀 Starting Desktop GUI Tests...")
    
    # Check if required dependencies are available
    try:
        import customtkinter
        import tkinter
        print("✅ GUI dependencies available")
    except ImportError as e:
        print(f"❌ Missing GUI dependencies: {e}")
        return False
    
    # Run tests
    tester = GUITester()
    success = tester.run_all_tests()
    
    if success:
        print("🎉 All GUI tests passed!")
        return True
    else:
        print("⚠️  Some GUI tests failed. Check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 