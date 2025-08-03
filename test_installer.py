#!/usr/bin/env python3
"""
Тесты для installer.py
"""

import unittest
import tempfile
import os
from pathlib import Path

# Импортируем функции для тестирования
from installer import (
    check_and_backup_file,
    safe_write_file,
    deduplicate_patterns,
    get_category_description,
    validate_merged_toml_structure
)


class TestInstaller(unittest.TestCase):
    """Тесты для функций installer.py"""
    
    def setUp(self):
        """Настройка тестов"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test.txt")
    
    def tearDown(self):
        """Очистка после тестов"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_check_and_backup_file_new_file(self):
        """Тест check_and_backup_file для нового файла"""
        content = "test content"
        result = check_and_backup_file(self.test_file, content)
        self.assertFalse(result)  # Файл не существует, бэкап не нужен
    
    def test_check_and_backup_file_existing_file_same_content(self):
        """Тест check_and_backup_file для существующего файла с тем же содержимым"""
        # Создаем файл
        with open(self.test_file, 'w') as f:
            f.write("test content")
        
        result = check_and_backup_file(self.test_file, "test content")
        self.assertFalse(result)  # Содержимое одинаковое, бэкап не нужен
    
    def test_check_and_backup_file_existing_file_different_content(self):
        """Тест check_and_backup_file для существующего файла с разным содержимым"""
        # Создаем файл
        with open(self.test_file, 'w') as f:
            f.write("old content")
        
        result = check_and_backup_file(self.test_file, "new content")
        self.assertTrue(result)  # Содержимое разное, бэкап создан
        
        # Проверяем, что бэкап создан
        backup_file = self.test_file + '.backup'
        self.assertTrue(os.path.exists(backup_file))
        
        # Проверяем содержимое бэкапа
        with open(backup_file, 'r') as f:
            backup_content = f.read()
        self.assertEqual(backup_content, "old content")
    
    def test_safe_write_file_new_file(self):
        """Тест safe_write_file для нового файла"""
        content = "test content"
        result = safe_write_file(self.test_file, content)
        self.assertTrue(result)
        
        # Проверяем, что файл создан
        self.assertTrue(os.path.exists(self.test_file))
        
        # Проверяем содержимое
        with open(self.test_file, 'r') as f:
            file_content = f.read()
        self.assertEqual(file_content, content)
    
    def test_safe_write_file_existing_file_same_content(self):
        """Тест safe_write_file для существующего файла с тем же содержимым"""
        # Создаем файл
        with open(self.test_file, 'w') as f:
            f.write("test content")
        
        result = safe_write_file(self.test_file, "test content")
        self.assertFalse(result)  # Изменений не было
    
    def test_safe_write_file_existing_file_different_content(self):
        """Тест safe_write_file для существующего файла с разным содержимым"""
        # Создаем файл
        with open(self.test_file, 'w') as f:
            f.write("old content")
        
        result = safe_write_file(self.test_file, "new content")
        self.assertTrue(result)  # Файл обновлен
        
        # Проверяем новое содержимое
        with open(self.test_file, 'r') as f:
            file_content = f.read()
        self.assertEqual(file_content, "new content")
    
    def test_deduplicate_patterns_empty(self):
        """Тест deduplicate_patterns с пустым списком"""
        result = deduplicate_patterns([])
        self.assertEqual(result, [])
    
    def test_deduplicate_patterns_no_duplicates(self):
        """Тест deduplicate_patterns без дубликатов"""
        patterns = ["*.py", "*.pyc", "*.log"]
        result = deduplicate_patterns(patterns)
        self.assertEqual(result, patterns)
    
    def test_deduplicate_patterns_with_duplicates(self):
        """Тест deduplicate_patterns с дубликатами"""
        patterns = ["*.py", "*.pyc", "*.py", "*.log", "*.pyc"]
        result = deduplicate_patterns(patterns)
        expected = ["*.py", "*.pyc", "*.log"]
        self.assertEqual(result, expected)
    
    def test_deduplicate_patterns_with_comments(self):
        """Тест deduplicate_patterns с комментариями"""
        patterns = ["*.py", "*.py # python files", "*.pyc", "*.py # python files"]
        result = deduplicate_patterns(patterns)
        expected = ["*.py", "*.pyc"]
        self.assertEqual(result, expected)
    
    def test_get_category_description_known(self):
        """Тест get_category_description для известной категории"""
        result = get_category_description("Python")
        expected = "файлы и каталоги, специфичные для Python-окружений"
        self.assertEqual(result, expected)
    
    def test_get_category_description_unknown(self):
        """Тест get_category_description для неизвестной категории"""
        result = get_category_description("UnknownCategory")
        expected = "пользовательская категория"
        self.assertEqual(result, expected)
    
    def test_validate_merged_toml_structure_valid(self):
        """Тест validate_merged_toml_structure с валидной структурой"""
        data = {
            "Python": ["*.py", "*.pyc"],
            "Java": ["*.class", "*.jar"]
        }
        result = validate_merged_toml_structure(data)
        self.assertTrue(result)
    
    def test_validate_merged_toml_structure_invalid_not_dict(self):
        """Тест validate_merged_toml_structure с невалидной структурой (не словарь)"""
        data = ["*.py", "*.pyc"]
        result = validate_merged_toml_structure(data)
        self.assertFalse(result)
    
    def test_validate_merged_toml_structure_invalid_not_list(self):
        """Тест validate_merged_toml_structure с невалидной структурой (не список)"""
        data = {
            "Python": "*.py"  # Должен быть список
        }
        result = validate_merged_toml_structure(data)
        self.assertFalse(result)
    
    def test_validate_merged_toml_structure_invalid_not_string(self):
        """Тест validate_merged_toml_structure с невалидной структурой (не строка)"""
        data = {
            "Python": ["*.py", 123]  # Должны быть строки
        }
        result = validate_merged_toml_structure(data)
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main() 