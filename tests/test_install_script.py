#!/usr/bin/env python3
"""
Test that install.sh works with installer.py
"""

import unittest
import tempfile
import os
import subprocess
import shutil

class TestInstallScript(unittest.TestCase):
    """Tests for install.sh"""
    
    def setUp(self):
        """Set up the tests"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create the test files
        self.test_files = {
            "how_to_do.py": "# Test how_to_do.py\n",
            "installer.py": "# Test installer.py\n", 
            "how_to_do.json": '{"test": "data"}\n',
            "how_to_do_gitignore.toml": "# Test gitignore\n"
        }
        
        for filename, content in self.test_files.items():
            with open(os.path.join(self.temp_dir, filename), 'w') as f:
                f.write(content)
    
    def tearDown(self):
        """Clean up after the tests"""
        shutil.rmtree(self.temp_dir)
    
    def test_installer_imports_correctly(self):
        """installer.py imports cleanly"""
        # Copy installer.py into the test directory
        shutil.copy("installer.py", self.temp_dir)
        
        # installer.py must work
        result = subprocess.run(
            ["python3", "-c", "import installer; print('OK')"],
            cwd=self.temp_dir,
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("OK", result.stdout)
    
    def test_installer_functions_available(self):
        """installer.py functions are available"""
        # Copy installer.py into the test directory
        shutil.copy("installer.py", self.temp_dir)
        
        # Check that the functions import
        test_code = """
import installer
from installer import (
    check_and_backup_file,
    safe_write_file,
    merge_gitignore_toml_files,
    deduplicate_patterns,
    merge_gitignore_rules,
    save_merged_gitignore_toml,
    get_category_description,
    validate_merged_toml_structure
)
print('All functions imported successfully')
"""
        
        result = subprocess.run(
            ["python3", "-c", test_code],
            cwd=self.temp_dir,
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("All functions imported successfully", result.stdout)
    
    def test_install_script_syntax(self):
        """install.sh syntax"""
        result = subprocess.run(
            ["bash", "-n", "install.sh"],
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0, f"install.sh syntax error: {result.stderr}")
    
    def test_installer_independent_of_how_to_do(self):
        """installer.py works independently of how_to_do.py"""
        # Copy installer.py only
        shutil.copy("installer.py", self.temp_dir)
        
        # installer.py must work without how_to_do.py
        test_code = """
import installer
from installer import check_and_backup_file, safe_write_file

# Exercise the functions
result = check_and_backup_file("test.txt", "test content")
print(f'check_and_backup_file result: {result}')

result = safe_write_file("test.txt", "test content")
print(f'safe_write_file result: {result}')
"""
        
        result = subprocess.run(
            ["python3", "-c", test_code],
            cwd=self.temp_dir,
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("check_and_backup_file result:", result.stdout)
        self.assertIn("safe_write_file result:", result.stdout)


if __name__ == '__main__':
    unittest.main() 