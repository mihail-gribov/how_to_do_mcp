#!/usr/bin/env python3
"""
Тест для проверки работы install.sh с installer.py
"""

import unittest
import tempfile
import os
import subprocess
import shutil

class TestInstallScript(unittest.TestCase):
    """Тесты для проверки работы install.sh"""
    
    def setUp(self):
        """Настройка тестов"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Создаем тестовые файлы
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
        """Очистка после тестов"""
        shutil.rmtree(self.temp_dir)
    
    def test_installer_imports_correctly(self):
        """Тест, что installer.py импортируется корректно"""
        # Копируем installer.py в тестовую директорию
        shutil.copy("installer.py", self.temp_dir)
        
        # Проверяем, что installer.py работает
        result = subprocess.run(
            ["python3", "-c", "import installer; print('OK')"],
            cwd=self.temp_dir,
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("OK", result.stdout)
    
    def test_installer_functions_available(self):
        """Тест, что функции installer.py доступны"""
        # Копируем installer.py в тестовую директорию
        shutil.copy("installer.py", self.temp_dir)
        
        # Проверяем импорт функций
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
        """Тест синтаксиса install.sh"""
        result = subprocess.run(
            ["bash", "-n", "install.sh"],
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0, f"install.sh syntax error: {result.stderr}")
    
    def test_installer_independent_of_how_to_do(self):
        """Тест, что installer.py работает независимо от how_to_do.py"""
        # Копируем только installer.py
        shutil.copy("installer.py", self.temp_dir)
        
        # Проверяем, что installer.py работает без how_to_do.py
        test_code = """
import installer
from installer import check_and_backup_file, safe_write_file

# Тестируем функции
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