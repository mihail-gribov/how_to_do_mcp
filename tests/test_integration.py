#!/usr/bin/env python3
"""
Интеграционные тесты для проверки совместной работы installer.py и how_to_do.py
"""

import unittest
import tempfile
import os
import shutil

# Импортируем функции для тестирования
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
    """Интеграционные тесты"""
    
    def setUp(self):
        """Настройка тестов"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Создаем тестовые TOML файлы
        self.distributor_toml = os.path.join(self.temp_dir, "distributor.toml")
        self.user_toml = os.path.join(self.temp_dir, "user.toml")
        
        # Создаем дистрибутивный TOML файл
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
        
        # Создаем пользовательский TOML файл
        user_content = """# User TOML file
Python = { patterns = [
    "*.pyc",  # Дубликат
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
        """Очистка после тестов"""
        shutil.rmtree(self.temp_dir)
    
    def test_merge_gitignore_toml_files_integration(self):
        """Тест интеграции merge_gitignore_toml_files"""
        # Объединяем файлы
        result = merge_gitignore_toml_files(self.distributor_toml, self.user_toml)
        
        # Проверяем результат
        self.assertIsInstance(result, dict)
        self.assertIn("Python", result)
        self.assertIn("Java", result)
        self.assertIn("Custom", result)
        
        # Проверяем, что дубликаты удалены
        python_patterns = result["Python"]
        self.assertIn("*.py", python_patterns)
        self.assertIn("*.pyc", python_patterns)
        self.assertIn("__pycache__/", python_patterns)
        self.assertIn("*.pyo", python_patterns)
        self.assertIn("venv/", python_patterns)
        
        # Проверяем, что дубликат *.pyc не повторяется
        pyc_count = python_patterns.count("*.pyc")
        self.assertEqual(pyc_count, 1)
    
    def test_save_and_load_integration(self):
        """Тест интеграции сохранения и загрузки TOML файла"""
        # Объединяем файлы
        merged_data = merge_gitignore_toml_files(self.distributor_toml, self.user_toml)
        
        # Сохраняем результат
        output_file = os.path.join(self.temp_dir, "merged.toml")
        success = save_merged_gitignore_toml(merged_data, output_file)
        self.assertTrue(success)
        
        # Проверяем, что файл создан
        self.assertTrue(os.path.exists(output_file))
        
        # Читаем файл и проверяем содержимое
        with open(output_file, 'r') as f:
            content = f.read()
        
        self.assertIn("Python", content)
        self.assertIn("Java", content)
        self.assertIn("Custom", content)
        self.assertIn("*.py", content)
        self.assertIn("*.class", content)
        self.assertIn("custom_file.txt", content)
    
    def test_deduplicate_patterns_integration(self):
        """Тест интеграции deduplicate_patterns"""
        patterns = [
            "*.py",
            "*.pyc",
            "*.py",  # Дубликат
            "*.pyc",  # Дубликат
            "*.log",
            "*.py # python files",  # С комментарием
            "*.py # another comment"  # Дубликат с комментарием
        ]
        
        result = deduplicate_patterns(patterns)
        
        # Проверяем, что дубликаты удалены
        self.assertIn("*.py", result)
        self.assertIn("*.pyc", result)
        self.assertIn("*.log", result)
        
        # Проверяем, что дубликаты не повторяются
        self.assertEqual(result.count("*.py"), 1)
        self.assertEqual(result.count("*.pyc"), 1)
    
    def test_validate_merged_toml_structure_integration(self):
        """Тест интеграции validate_merged_toml_structure"""
        # Валидная структура
        valid_data = {
            "Python": ["*.py", "*.pyc"],
            "Java": ["*.class", "*.jar"]
        }
        result = validate_merged_toml_structure(valid_data)
        self.assertTrue(result)
        
        # Невалидная структура
        invalid_data = {
            "Python": "*.py",  # Должен быть список
            "Java": ["*.class", "*.jar"]
        }
        result = validate_merged_toml_structure(invalid_data)
        self.assertFalse(result)
    
    def test_get_category_description_integration(self):
        """Тест интеграции get_category_description"""
        # Известные категории
        result = get_category_description("Python")
        self.assertIn("Python", result)
        
        result = get_category_description("Java")
        self.assertIn("JVM", result)
        
        # Неизвестная категория
        result = get_category_description("UnknownCategory")
        self.assertEqual(result, "пользовательская категория")
    
    def test_file_operations_integration(self):
        """Тест интеграции операций с файлами"""
        test_file = os.path.join(self.temp_dir, "test.txt")
        content = "test content"
        
        # Создаем файл
        result = safe_write_file(test_file, content)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(test_file))
        
        # Читаем файл
        with open(test_file, 'r') as f:
            file_content = f.read()
        self.assertEqual(file_content, content)
        
        # Изменяем файл
        new_content = "new content"
        result = safe_write_file(test_file, new_content)
        self.assertTrue(result)
        
        # Проверяем, что бэкап создан
        backup_file = test_file + '.backup'
        self.assertTrue(os.path.exists(backup_file))
        
        # Проверяем содержимое бэкапа
        with open(backup_file, 'r') as f:
            backup_content = f.read()
        self.assertEqual(backup_content, content)
        
        # Проверяем новое содержимое
        with open(test_file, 'r') as f:
            new_file_content = f.read()
        self.assertEqual(new_file_content, new_content)


if __name__ == '__main__':
    unittest.main() 