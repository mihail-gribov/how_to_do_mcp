#!/usr/bin/env python3
"""
Тесты для how_to_do.py после рефакторинга
"""

import unittest
import tempfile
import os
import json

# Импортируем функции для тестирования
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
    """Тесты для функций how_to_do.py"""
    
    def setUp(self):
        """Настройка тестов"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Создаем временный конфигурационный файл
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
        """Очистка после тестов"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_load_config(self):
        """Тест load_config"""
        # Временно изменяем __file__ для тестирования
        import how_to_do
        original_file = how_to_do.__file__
        
        try:
            # Создаем временный файл how_to_do.py
            temp_how_to_do = os.path.join(self.temp_dir, "how_to_do.py")
            with open(temp_how_to_do, 'w') as f:
                f.write("# Test file")
            
            # Временно заменяем __file__
            how_to_do.__file__ = temp_how_to_do
            
            # Тестируем загрузку конфигурации
            config = load_config()
            self.assertIsInstance(config, dict)
            self.assertIn("commands", config)
            
        finally:
            # Восстанавливаем оригинальный __file__
            how_to_do.__file__ = original_file
    
    def test_get_project_path(self):
        """Тест get_project_path"""
        # Сохраняем оригинальное значение переменной окружения
        original_project_path = os.environ.get('PROJECT_PATH')
        
        try:
            # Тест без переменной окружения
            if 'PROJECT_PATH' in os.environ:
                del os.environ['PROJECT_PATH']
            
            path = get_project_path()
            self.assertIsInstance(path, str)
            self.assertTrue(len(path) > 0)
            
            # Тест с переменной окружения
            test_path = "/test/path"
            os.environ['PROJECT_PATH'] = test_path
            path = get_project_path()
            self.assertEqual(path, test_path)
            
        finally:
            # Восстанавливаем оригинальное значение
            if original_project_path:
                os.environ['PROJECT_PATH'] = original_project_path
            elif 'PROJECT_PATH' in os.environ:
                del os.environ['PROJECT_PATH']
    
    def test_scan_project_files(self):
        """Тест scan_project_files"""
        # Создаем тестовые файлы
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
        
        # Сканируем файлы
        files = scan_project_files(self.temp_dir)
        self.assertIsInstance(files, set)
        self.assertTrue(len(files) > 0)
        
        # Проверяем, что все файлы найдены (функция возвращает относительные пути)
        # Проверяем только созданные нами файлы, игнорируя другие
        for test_file in test_files:
            self.assertIn(test_file, files)
    
    def test_match_pattern(self):
        """Тест match_pattern"""
        files = {
            "/path/to/file.py",
            "/path/to/file.txt",
            "/path/to/subdir/file.py"
        }
        
        # Тест с паттерном, который должен совпадать
        result = match_pattern("*.py", files)
        self.assertTrue(result)
        
        # Тест с паттерном, который не должен совпадать
        result = match_pattern("*.java", files)
        self.assertFalse(result)
    
    def test_generate_commands_list(self):
        """Тест generate_commands_list"""
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
        
        # Проверяем содержимое
        self.assertIn("test_command", commands)
        self.assertIn("Test command", commands)
        self.assertIn("param1", commands)
    
    def test_add_how_to_do_signature(self):
        """Тест add_how_to_do_signature"""
        prompt = "Test prompt"
        result = add_how_to_do_signature(prompt)
        
        self.assertIsInstance(result, str)
        self.assertIn("Test prompt", result)
        self.assertIn("HOW TO DO", result)


if __name__ == '__main__':
    unittest.main() 