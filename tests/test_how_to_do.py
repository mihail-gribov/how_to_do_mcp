#!/usr/bin/env python3
"""
Tests for how_to_do.py after the refactoring
"""

import unittest
import tempfile
import os
import json

# Import the functions under test
from how_to_do import (
    load_config,
    get_project_path,
    load_gitignore_rules,
    scan_project_files,
    match_pattern,
    generate_commands_list,
    add_how_to_do_signature
)


class TestHowToDo(unittest.TestCase):
    """Tests for how_to_do.py functions"""
    
    def setUp(self):
        """Set up the tests"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a temporary configuration file
        self.config_file = os.path.join(self.temp_dir, "how_to_do.json")
        config_data = {
            "commands": [
                {
                    "name": "test_command",
                    "description": "Test command",
                    "prompt": "Test prompt"
                }
            ]
        }
        with open(self.config_file, 'w') as f:
            json.dump(config_data, f)
    
    def tearDown(self):
        """Clean up after the tests"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_load_config(self):
        """load_config"""
        # Temporarily change __file__ for the test
        import how_to_do
        original_file = how_to_do.__file__
        
        try:
            # Create a temporary how_to_do.py
            temp_how_to_do = os.path.join(self.temp_dir, "how_to_do.py")
            with open(temp_how_to_do, 'w') as f:
                f.write("# Test file")
    
            # Create a temporary how_to_do.json
            temp_json = os.path.join(self.temp_dir, "how_to_do.json")
            test_config = {
                "tools": {
                    "test_command": {
                        "description": "Test command",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        },
                        "prompt": "Test prompt"
                    }
                }
            }
            with open(temp_json, 'w') as f:
                json.dump(test_config, f)
    
            # Temporarily replace __file__
            how_to_do.__file__ = temp_how_to_do
    
            # Exercise configuration loading
            config = load_config()
            self.assertIsInstance(config, dict)
            self.assertIn("tools", config)
            
        finally:
            # Restore the original __file__
            how_to_do.__file__ = original_file
    
    def test_get_project_path(self):
        """get_project_path"""
        # Save the original environment variable
        original_project_path = os.environ.get('PROJECT_PATH')
        
        try:
            # Test without the environment variable
            if 'PROJECT_PATH' in os.environ:
                del os.environ['PROJECT_PATH']
            
            path = get_project_path()
            self.assertIsInstance(path, str)
            self.assertTrue(len(path) > 0)
            
            # Test with the environment variable
            test_path = "/test/path"
            os.environ['PROJECT_PATH'] = test_path
            path = get_project_path()
            self.assertEqual(path, test_path)
            
        finally:
            # Restore the original value
            if original_project_path:
                os.environ['PROJECT_PATH'] = original_project_path
            elif 'PROJECT_PATH' in os.environ:
                del os.environ['PROJECT_PATH']
    
    def test_scan_project_files(self):
        """scan_project_files"""
        # Create the test files
        test_files = [
            "test.py",
            "test.txt",
            "subdir/test.py",
            "subdir/test.txt"
        ]
        
        for file_path in test_files:
            full_path = os.path.join(self.temp_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write("test content")
        
        # Scan the files
        files = scan_project_files(self.temp_dir)
        self.assertIsInstance(files, set)
        self.assertTrue(len(files) > 0)
        
        # Every file must be found (the function returns relative paths)
        # Check only the files we created, ignore the rest
        for test_file in test_files:
            self.assertIn(test_file, files)
    
    def test_match_pattern(self):
        """match_pattern"""
        files = {
            "/path/to/file.py",
            "/path/to/file.txt",
            "/path/to/subdir/file.py"
        }
        
        # Pattern that should match
        result = match_pattern("*.py", files)
        self.assertTrue(result)
        
        # Pattern that should not match
        result = match_pattern("*.java", files)
        self.assertFalse(result)
    
    def test_generate_commands_list(self):
        """generate_commands_list"""
        config = {
            "tools": {
                "test_command": {
                    "description": "Test command",
                    "inputSchema": {
                        "properties": {
                            "param1": {
                                "description": "Test parameter"
                            }
                        }
                    }
                }
            }
        }
        
        commands = generate_commands_list(config)
        self.assertIsInstance(commands, str)
        self.assertTrue(len(commands) > 0)
        
        # Check the content
        self.assertIn("test_command", commands)
        self.assertIn("Test command", commands)
        self.assertIn("param1", commands)
    
    def test_add_how_to_do_signature(self):
        """add_how_to_do_signature"""
        prompt = "Test prompt"
        result = add_how_to_do_signature(prompt)
        
        self.assertIsInstance(result, str)
        self.assertIn("Test prompt", result)
        self.assertIn("HOW TO DO", result)


if __name__ == '__main__':
    unittest.main() 