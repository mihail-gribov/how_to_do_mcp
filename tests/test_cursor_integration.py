#!/usr/bin/env python3
"""
Тест интеграции с Cursor IDE
"""

import json
import sys
import os

def test_mcp_configuration():
    """Тест конфигурации MCP"""
    
    mcp_config_path = os.path.expanduser('~/.cursor/mcp.json')
    
    assert os.path.exists(mcp_config_path), "MCP конфигурация не найдена"
    
    try:
        with open(mcp_config_path, 'r') as f:
            config = json.load(f)
        
        # Проверяем, что HOW TO DO сервер настроен
        servers = config.get('mcpServers', {})
        how_to_do_server = None
        
        for server_name, server_config in servers.items():
            if 'how_to_do' in server_name.lower():
                how_to_do_server = server_config
                break
        
        assert how_to_do_server is not None, "HOW TO DO сервер не найден в MCP конфигурации"
        
        print("✅ HOW TO DO сервер найден в MCP конфигурации")
        print(f"   Имя: {list(servers.keys())[list(servers.values()).index(how_to_do_server)]}")
        print(f"   Команда: {how_to_do_server.get('command', 'N/A')}")
            
    except Exception as e:
        assert False, f"Ошибка чтения MCP конфигурации: {e}"

def test_server_files():
    """Тест файлов сервера"""
    
    server_dir = os.path.expanduser('~/.cursor/tools')
    required_files = ['how_to_do.py', 'how_to_do.json', 'how_to_do_gitignore.toml']
    
    print("📁 Проверка файлов сервера:")
    
    for file in required_files:
        file_path = os.path.join(server_dir, file)
        assert os.path.exists(file_path), f"Файл {file} не найден"
        size = os.path.getsize(file_path)
        print(f"   ✅ {file} ({size} байт)")

def test_server_executable():
    """Тест исполняемости сервера"""
    
    server_path = os.path.expanduser('~/.cursor/tools/how_to_do.py')
    
    assert os.path.exists(server_path), "Сервер не найден"
    assert os.access(server_path, os.X_OK), "Сервер не исполняемый"
    
    print("✅ Сервер исполняемый")

def test_generate_gitignore_command():
    """Тест команды generate gitignore"""
    
    try:
        # Импортируем сервер
        sys.path.insert(0, os.path.expanduser('~/.cursor/tools'))
        from how_to_do import handle_request
        
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
        
        # Обрабатываем запрос
        response = handle_request(request)
        
        assert "result" in response, f"Ошибка команды generate gitignore: {response.get('error', {})}"
        
        content = response["result"]["content"][0]["text"]
        
        # Проверяем, что ответ содержит правила
        assert "RULES FOR USE" in content and "##" in content, "Команда generate gitignore возвращает некорректный ответ"
        
        print("✅ Команда generate gitignore возвращает корректный ответ")
        print(f"   Длина ответа: {len(content)} символов")
            
    except Exception as e:
        assert False, f"Ошибка тестирования команды: {e}"

if __name__ == '__main__':
    print("🧪 Тестирование интеграции с Cursor IDE...")
    print()
    
    # Тест 1: Конфигурация MCP
    print("1. Тест конфигурации MCP:")
    test1 = test_mcp_configuration()
    print()
    
    # Тест 2: Файлы сервера
    print("2. Тест файлов сервера:")
    test2 = test_server_files()
    print()
    
    # Тест 3: Исполняемость сервера
    print("3. Тест исполняемости сервера:")
    test3 = test_server_executable()
    print()
    
    # Тест 4: Команда generate gitignore
    print("4. Тест команды generate gitignore:")
    test4 = test_generate_gitignore_command()
    print()
    
    # Итоговый результат
    if test1 and test2 and test3 and test4:
        print("🎉 Все тесты прошли успешно!")
        print()
        print("📋 Инструкции для использования в Cursor:")
        print("1. Перезапустите Cursor IDE")
        print("2. Откройте AI чат")
        print("3. Используйте команду: generate gitignore")
        print("4. Сервер автоматически проанализирует проект и создаст .gitignore")
    else:
        print("❌ Некоторые тесты не прошли")
        print("   Проверьте установку и перезапустите Cursor IDE") 