#!/usr/bin/env python3
"""
Tests for installer.py
"""

import unittest
import tempfile
import os
from pathlib import Path

# Import the functions under test
from installer import (
    check_and_backup_file,
    safe_write_file,
    deduplicate_patterns,
    get_category_description,
    validate_merged_toml_structure
)


class TestInstaller(unittest.TestCase):
    """Tests for installer.py functions"""
    
    def setUp(self):
        """Set up the tests"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test.txt")
    
    def tearDown(self):
        """Clean up after the tests"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_check_and_backup_file_new_file(self):
        """check_and_backup_file with a new file"""
        content = "test content"
        result = check_and_backup_file(self.test_file, content)
        self.assertFalse(result)  # file does not exist, no backup needed
    
    def test_check_and_backup_file_existing_file_same_content(self):
        """check_and_backup_file with an existing file whose content matches"""
        # Create the file
        with open(self.test_file, 'w') as f:
            f.write("test content")
        
        result = check_and_backup_file(self.test_file, "test content")
        self.assertFalse(result)  # content matches, no backup needed
    
    def test_check_and_backup_file_existing_file_different_content(self):
        """check_and_backup_file with an existing file whose content differs"""
        # Create the file
        with open(self.test_file, 'w') as f:
            f.write("old content")
        
        result = check_and_backup_file(self.test_file, "new content")
        self.assertTrue(result)  # content differs, a backup was made
        
        # A backup must have been created
        backup_file = self.test_file + '.backup'
        self.assertTrue(os.path.exists(backup_file))
        
        # Check the backup content
        with open(backup_file, 'r') as f:
            backup_content = f.read()
        self.assertEqual(backup_content, "old content")
    
    def test_safe_write_file_new_file(self):
        """safe_write_file with a new file"""
        content = "test content"
        result = safe_write_file(self.test_file, content)
        self.assertTrue(result)
        
        # The file must have been created
        self.assertTrue(os.path.exists(self.test_file))
        
        # Check the content
        with open(self.test_file, 'r') as f:
            file_content = f.read()
        self.assertEqual(file_content, content)
    
    def test_safe_write_file_existing_file_same_content(self):
        """safe_write_file with an existing file whose content matches"""
        # Create the file
        with open(self.test_file, 'w') as f:
            f.write("test content")
        
        result = safe_write_file(self.test_file, "test content")
        self.assertFalse(result)  # nothing changed
    
    def test_safe_write_file_existing_file_different_content(self):
        """safe_write_file with an existing file whose content differs"""
        # Create the file
        with open(self.test_file, 'w') as f:
            f.write("old content")
        
        result = safe_write_file(self.test_file, "new content")
        self.assertTrue(result)  # file was updated
        
        # Check the new content
        with open(self.test_file, 'r') as f:
            file_content = f.read()
        self.assertEqual(file_content, "new content")
    
    def test_deduplicate_patterns_empty(self):
        """deduplicate_patterns with an empty list"""
        result = deduplicate_patterns([])
        self.assertEqual(result, [])
    
    def test_deduplicate_patterns_no_duplicates(self):
        """deduplicate_patterns without duplicates"""
        patterns = ["*.py", "*.pyc", "*.log"]
        result = deduplicate_patterns(patterns)
        self.assertEqual(result, patterns)
    
    def test_deduplicate_patterns_with_duplicates(self):
        """deduplicate_patterns with duplicates"""
        patterns = ["*.py", "*.pyc", "*.py", "*.log", "*.pyc"]
        result = deduplicate_patterns(patterns)
        expected = ["*.py", "*.pyc", "*.log"]
        self.assertEqual(result, expected)
    
    def test_deduplicate_patterns_with_comments(self):
        """deduplicate_patterns with comments"""
        patterns = ["*.py", "*.py # python files", "*.pyc", "*.py # python files"]
        result = deduplicate_patterns(patterns)
        expected = ["*.py", "*.pyc"]
        self.assertEqual(result, expected)
    
    def test_get_category_description_known(self):
        """get_category_description for a known category"""
        result = get_category_description("Python")
        expected = "files and directories specific to Python environments"
        self.assertEqual(result, expected)
    
    def test_get_category_description_unknown(self):
        """get_category_description for an unknown category"""
        result = get_category_description("UnknownCategory")
        expected = "user-defined category"
        self.assertEqual(result, expected)
    
    def test_validate_merged_toml_structure_valid(self):
        """validate_merged_toml_structure with a valid structure"""
        data = {
            "Python": ["*.py", "*.pyc"],
            "Java": ["*.class", "*.jar"]
        }
        result = validate_merged_toml_structure(data)
        self.assertTrue(result)
    
    def test_validate_merged_toml_structure_invalid_not_dict(self):
        """validate_merged_toml_structure with an invalid structure (not a dict)"""
        data = ["*.py", "*.pyc"]
        result = validate_merged_toml_structure(data)
        self.assertFalse(result)
    
    def test_validate_merged_toml_structure_invalid_not_list(self):
        """validate_merged_toml_structure with an invalid structure (not a list)"""
        data = {
            "Python": "*.py"  # must be a list
        }
        result = validate_merged_toml_structure(data)
        self.assertFalse(result)
    
    def test_validate_merged_toml_structure_invalid_not_string(self):
        """validate_merged_toml_structure with an invalid structure (not a string)"""
        data = {
            "Python": ["*.py", 123]  # must be strings
        }
        result = validate_merged_toml_structure(data)
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main() 