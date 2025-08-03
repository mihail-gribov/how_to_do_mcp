#!/usr/bin/env python3
"""
Тест для проверки команды generate gitignore
"""

import json
import sys
import os

# Добавляем путь к установленному серверу
sys.path.insert(0, os.path.expanduser('~/.cursor/tools'))

def test_generate_gitignore():
    """Тест команды generate gitignore"""
    
    # Создаем тестовый запрос
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "generate_gitignore",
            "arguments": {}
        }
    }
    
    try:
        # Импортируем функцию обработки запросов
        from how_to_do import handle_request
        
        # Обрабатываем запрос
        response = handle_request(request)
        
        # Проверяем результат
        if "result" in response:
            print("✅ Команда generate gitignore работает корректно")
            print(f"Статус: {response.get('result', {}).get('content', [{}])[0].get('text', '')[:200]}...")
            return True
        else:
            print("❌ Ошибка в команде generate gitignore")
            print(f"Ошибка: {response.get('error', {})}")
            return False
            
    except Exception as e:
        print(f"❌ Исключение при выполнении команды: {e}")
        return False

def test_load_gitignore_rules():
    """Тест загрузки правил gitignore"""
    
    try:
        from how_to_do import load_gitignore_rules
        
        rules = load_gitignore_rules()
        print(f"✅ Правила gitignore загружены: {len(rules)} категорий")
        
        for category, patterns in rules.items():
            print(f"  - {category}: {len(patterns)} правил")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка загрузки правил gitignore: {e}")
        return False

def test_analyze_project():
    """Тест анализа проекта"""
    
    try:
        from how_to_do import analyze_project_for_gitignore, get_project_path
        
        project_path = get_project_path()
        print(f"📁 Анализируем проект: {project_path}")
        
        rules_by_category = analyze_project_for_gitignore(project_path)
        print(f"✅ Анализ проекта завершен: {len(rules_by_category)} категорий")
        
        for category, rules in rules_by_category.items():
            print(f"  - {category}: {len(rules)} правил")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка анализа проекта: {e}")
        return False

if __name__ == '__main__':
    print("🧪 Тестирование команды generate gitignore...")
    print()
    
    # Тест 1: Загрузка правил
    print("1. Тест загрузки правил gitignore:")
    test1 = test_load_gitignore_rules()
    print()
    
    # Тест 2: Анализ проекта
    print("2. Тест анализа проекта:")
    test2 = test_analyze_project()
    print()
    
    # Тест 3: Команда generate gitignore
    print("3. Тест команды generate gitignore:")
    test3 = test_generate_gitignore()
    print()
    
    # Итоговый результат
    if test1 and test2 and test3:
        print("🎉 Все тесты прошли успешно!")
    else:
        print("❌ Некоторые тесты не прошли") 