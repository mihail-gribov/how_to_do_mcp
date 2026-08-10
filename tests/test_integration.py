#!/usr/bin/env python3
"""
Integration tests covering installer.py and how_to_do.py working together
"""

import unittest
import tempfile
import os
import shutil

# Import the functions under test
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

from how_to_do import (
    load_config,
    get_project_path,
    load_gitignore_rules,
    scan_project_files,
    match_pattern
)


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def setUp(self):
        """Set up the tests"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create the test TOML files
        self.distributor_toml = os.path.join(self.temp_dir, "distributor.toml")
        self.user_toml = os.path.join(self.temp_dir, "user.toml")
        
        # Create the distributed TOML file
        distributor_content = """# Distributor TOML file
Python = { patterns = [
    "*.py",
    "*.pyc",
    "__pycache__/"
]}

Java = { patterns = [
    "*.class",
    "*.jar"
]}
"""
        with open(self.distributor_toml, 'w') as f:
            f.write(distributor_content)
        
        # Create the user TOML file
        user_content = """# User TOML file
Python = { patterns = [
    "*.pyc",  # duplicate
    "*.pyo",
    "venv/"
]}

Custom = { patterns = [
    "custom_file.txt"
]}
"""
        with open(self.user_toml, 'w') as f:
            f.write(user_content)
    
    def tearDown(self):
        """Clean up after the tests"""
        shutil.rmtree(self.temp_dir)
    
    def test_merge_gitignore_toml_files_integration(self):
        """merge_gitignore_toml_files integration"""
        # Merge the files
        result = merge_gitignore_toml_files(self.distributor_toml, self.user_toml)
        
        # Check the result
        self.assertIsInstance(result, dict)
        self.assertIn("Python", result)
        self.assertIn("Java", result)
        self.assertIn("Custom", result)
        
        # Duplicates must be removed
        python_patterns = result["Python"]
        self.assertIn("*.py", python_patterns)
        self.assertIn("*.pyc", python_patterns)
        self.assertIn("__pycache__/", python_patterns)
        self.assertIn("*.pyo", python_patterns)
        self.assertIn("venv/", python_patterns)
        
        # The *.pyc duplicate must not repeat
        pyc_count = python_patterns.count("*.pyc")
        self.assertEqual(pyc_count, 1)
    
    def test_save_and_load_integration(self):
        """Saving and loading a TOML file"""
        # Merge the files
        merged_data = merge_gitignore_toml_files(self.distributor_toml, self.user_toml)
        
        # Save the result
        output_file = os.path.join(self.temp_dir, "merged.toml")
        success = save_merged_gitignore_toml(merged_data, output_file)
        self.assertTrue(success)
        
        # The file must have been created
        self.assertTrue(os.path.exists(output_file))
        
        # Read the file and check its content
        with open(output_file, 'r') as f:
            content = f.read()
        
        self.assertIn("Python", content)
        self.assertIn("Java", content)
        self.assertIn("Custom", content)
        self.assertIn("*.py", content)
        self.assertIn("*.class", content)
        self.assertIn("custom_file.txt", content)
    
    def test_deduplicate_patterns_integration(self):
        """deduplicate_patterns integration"""
        patterns = [
            "*.py",
            "*.pyc",
            "*.py",  # duplicate
            "*.pyc",  # duplicate
            "*.log",
            "*.py # python files",  # with a comment
            "*.py # another comment"  # duplicate with a comment
        ]
        
        result = deduplicate_patterns(patterns)
        
        # Duplicates must be removed
        self.assertIn("*.py", result)
        self.assertIn("*.pyc", result)
        self.assertIn("*.log", result)
        
        # Duplicates must not repeat
        self.assertEqual(result.count("*.py"), 1)
        self.assertEqual(result.count("*.pyc"), 1)
    
    def test_validate_merged_toml_structure_integration(self):
        """validate_merged_toml_structure integration"""
        # Valid structure
        valid_data = {
            "Python": ["*.py", "*.pyc"],
            "Java": ["*.class", "*.jar"]
        }
        result = validate_merged_toml_structure(valid_data)
        self.assertTrue(result)
        
        # Invalid structure
        invalid_data = {
            "Python": "*.py",  # must be a list
            "Java": ["*.class", "*.jar"]
        }
        result = validate_merged_toml_structure(invalid_data)
        self.assertFalse(result)
    
    def test_get_category_description_integration(self):
        """get_category_description integration"""
        # Known categories
        result = get_category_description("Python")
        self.assertIn("Python", result)
        
        result = get_category_description("Java")
        self.assertIn("JVM", result)
        
        # Unknown category
        result = get_category_description("UnknownCategory")
        self.assertEqual(result, "user-defined category")
    
    def test_file_operations_integration(self):
        """File operations integration"""
        test_file = os.path.join(self.temp_dir, "test.txt")
        content = "test content"
        
        # Create the file
        result = safe_write_file(test_file, content)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(test_file))
        
        # Read the file
        with open(test_file, 'r') as f:
            file_content = f.read()
        self.assertEqual(file_content, content)
        
        # Modify the file
        new_content = "new content"
        result = safe_write_file(test_file, new_content)
        self.assertTrue(result)
        
        # A backup must have been created
        backup_file = test_file + '.backup'
        self.assertTrue(os.path.exists(backup_file))
        
        # Check the backup content
        with open(backup_file, 'r') as f:
            backup_content = f.read()
        self.assertEqual(backup_content, content)
        
        # Check the new content
        with open(test_file, 'r') as f:
            new_file_content = f.read()
        self.assertEqual(new_file_content, new_content)


if __name__ == '__main__':
    unittest.main() 