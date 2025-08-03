#!/usr/bin/env python3
"""
MCP server HOW TO DO - intelligent test analysis and execution
"""

import json
import sys
import logging
import os
import glob
import tomllib
from datetime import datetime, timedelta
from typing import Any, Dict, List, Set
from pathlib import Path

# Кэш для результатов мержа
_merge_cache = {}
_cache_timestamp = None
_cache_duration = timedelta(minutes=5)  # Кэш на 5 минут

def _is_cache_valid() -> bool:
    """Проверяет, действителен ли кэш"""
    global _cache_timestamp
    if _cache_timestamp is None:
        return False
    return datetime.now() - _cache_timestamp < _cache_duration

def _clear_cache():
    """Очищает кэш"""
    global _merge_cache, _cache_timestamp
    _merge_cache = {}
    _cache_timestamp = None

def _update_cache(data: Dict[str, List[str]]):
    """Обновляет кэш"""
    global _merge_cache, _cache_timestamp
    _merge_cache = data.copy()
    _cache_timestamp = datetime.now()

# Configure logging to stderr for debugging in Cursor
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [HOW_TO_DO] %(levelname)s: %(message)s',
    stream=sys.stderr,
    datefmt='%H:%M:%S'
)

logger = logging.getLogger(__name__)

_config = None

def load_config():
    """Loads configuration from JSON file"""
    global _config
    if _config is not None:
        return _config
    
    try:
        config_path = os.path.splitext(__file__)[0] + '.json'
        with open(config_path, 'r', encoding='utf-8') as f:
            _config = json.load(f)
        logger.info(f"Configuration loaded from {config_path}")
        return _config
    except Exception as e:
        logger.error(f"Failed to load configuration: {str(e)}")
        raise RuntimeError(f"Failed to load configuration: {str(e)}")

def get_project_path() -> str:
    """Gets the path to the current project"""
    project_path = os.getenv('PROJECT_PATH')
    if project_path:
        return project_path
    
    return os.getcwd()

def check_and_backup_file(file_path: str, new_content: str) -> bool:
    """
    Checks if file exists and differs from new content.
    Creates backup if file exists and differs.
    Returns True if file was updated, False if no changes needed.
    """
    try:
        file_path = Path(file_path)
        
        # Check if file exists
        if not file_path.exists():
            logger.info(f"File {file_path} does not exist, will create new")
            return False
        
        # Read existing content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()
        except Exception as e:
            logger.warning(f"Could not read existing file {file_path}: {e}")
            return False
        
        # Compare content
        if existing_content.strip() == new_content.strip():
            logger.info(f"File {file_path} is up to date, no changes needed")
            return False
        
        # Content differs, create backup
        backup_path = file_path.with_suffix(file_path.suffix + '.backup')
        try:
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(existing_content)
            logger.info(f"Created backup: {backup_path}")
        except Exception as e:
            logger.error(f"Failed to create backup for {file_path}: {e}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error checking file {file_path}: {e}")
        return False

def safe_write_file(file_path: str, content: str) -> bool:
    """
    Safely writes content to file with backup creation if needed.
    Returns True if file was written, False if no changes needed.
    """
    try:
        file_path = Path(file_path)
        
        # Check if backup is needed
        if check_and_backup_file(str(file_path), content):
            # Write new content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Updated file: {file_path}")
            return True
        else:
            # No changes needed or file doesn't exist
            if not file_path.exists():
                # Create new file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"Created new file: {file_path}")
                return True
            return False
            
    except Exception as e:
        logger.error(f"Error writing file {file_path}: {e}")
        return False

def load_gitignore_rules() -> Dict[str, List[str]]:
    """Loads rules from how_to_do_gitignore.toml with optional merging"""
    try:
        distributor_path = os.path.join(os.path.dirname(__file__), 'how_to_do_gitignore.toml')
        user_path = os.path.join(os.path.expanduser('~'), '.cursor', 'tools', 'how_to_do_gitignore.toml')
        
        # Если пользовательский файл существует, делаем мерж
        if os.path.exists(user_path):
            logger.info("User gitignore.toml found, performing merge")
            return merge_gitignore_toml_files(distributor_path, user_path)
        else:
            # Иначе загружаем только дистрибутивный файл
            with open(distributor_path, 'rb') as f:
                data = tomllib.load(f)
            
            # Convert TOML structure to dictionary
            rules = {}
            for section_name, section_data in data.items():
                if isinstance(section_data, dict) and 'patterns' in section_data:
                    rules[section_name] = section_data['patterns']
            
            logger.info(f"Loaded {len(rules)} gitignore rule sections from distributor")
            return rules
    except Exception as e:
        logger.error(f"Failed to load gitignore rules: {str(e)}")
        raise RuntimeError(f"Failed to load gitignore rules: {str(e)}")

def scan_project_files(project_path: str) -> Set[str]:
    """Scans the project file structure"""
    files = set()
    project_path = Path(project_path).resolve()
    
    try:
        import os
        
        for root, dirs, filenames in os.walk(project_path, followlinks=False):
            # Convert to Path objects for easier handling
            root_path = Path(root)
            
            # Skip if outside project boundaries
            try:
                relative_root = root_path.relative_to(project_path)
            except ValueError:
                continue
            
            # Add directories
            for dirname in dirs:
                try:
                    dir_path = root_path / dirname
                    if not dir_path.is_symlink():
                        relative_dir = dir_path.relative_to(project_path)
                        files.add(str(relative_dir) + '/')
                except (OSError, PermissionError):
                    continue
            
            # Add files
            for filename in filenames:
                try:
                    file_path = root_path / filename
                    if not file_path.is_symlink():
                        relative_file = file_path.relative_to(project_path)
                        files.add(str(relative_file))
                except (OSError, PermissionError):
                    continue
        
        logger.info(f"Scanned {len(files)} items in project")
        return files
    except Exception as e:
        logger.error(f"Failed to scan project files: {str(e)}")
        raise RuntimeError(f"Failed to scan project files: {str(e)}")

def match_pattern(pattern: str, files: Set[str]) -> bool:
    """Checks if there are files matching the pattern"""
    import fnmatch
    import os
    
    for file_path in files:
        normalized_path = file_path.replace('\\', '/')
        
        if fnmatch.fnmatch(normalized_path, pattern):
            return True
        
        if fnmatch.fnmatch(os.path.basename(normalized_path), pattern):
            return True
        
        if normalized_path.endswith('/'):
            dir_name = normalized_path[:-1]
            if fnmatch.fnmatch(dir_name, pattern):
                return True
            if fnmatch.fnmatch(os.path.basename(dir_name), pattern):
                return True
        
        if pattern.endswith('/'):
            pattern_without_slash = pattern[:-1]
            if normalized_path.endswith('/'):
                dir_name = normalized_path[:-1]
                if fnmatch.fnmatch(dir_name, pattern_without_slash):
                    return True
                if fnmatch.fnmatch(os.path.basename(dir_name), pattern_without_slash):
                    return True
            else:
                if fnmatch.fnmatch(os.path.basename(normalized_path), pattern_without_slash):
                    return True
    
    return False

def analyze_project_for_gitignore(project_path: str) -> Dict[str, List[str]]:
    """Analyzes the project and returns grouped rules by categories"""
    try:
        rules = load_gitignore_rules()
        
        # Логируем источник правил
        user_path = os.path.join(os.path.expanduser('~'), '.cursor', 'tools', 'how_to_do_gitignore.toml')
        if os.path.exists(user_path):
            logger.info("Using merged gitignore rules (distributor + user)")
        else:
            logger.info("Using distributor gitignore rules only")
        
        project_files = scan_project_files(project_path)
        
        needed_rules_by_category = {}
        
        for section_name, patterns in rules.items():
            section_rules = []
            
            for pattern in patterns:
                if match_pattern(pattern, project_files):
                    section_rules.append(pattern)
            
            if section_rules:
                needed_rules_by_category[section_name] = section_rules
        
        logger.info(f"Analyzed project, found {len(needed_rules_by_category)} categories with rules")
        return needed_rules_by_category
        
    except Exception as e:
        logger.error(f"Failed to analyze project for gitignore: {str(e)}")
        raise RuntimeError(f"Failed to analyze project for gitignore: {str(e)}")

def generate_commands_list(config):
    """Generates a list of commands for the how_to_do_list prompt"""
    commands_list = []
    
    for tool_name, tool_config in config["tools"].items():
        if tool_name == "how_to_do_list":
            continue
            
        command_info = f"**{tool_name}**\n"
        command_info += f"- Description: {tool_config['description']}\n"
        
        if "inputSchema" in tool_config and "properties" in tool_config["inputSchema"]:
            properties = tool_config["inputSchema"]["properties"]
            if properties:
                command_info += "- Parameters:\n"
                for param_name, param_config in properties.items():
                    param_desc = param_config.get("description", "No description")
                    command_info += f"  - `{param_name}`: {param_desc}\n"
            else:
                command_info += "- Parameters: none\n"
        else:
            command_info += "- Parameters: none\n"
        
        commands_list.append(command_info)
    
    return "\n".join(commands_list)

def add_how_to_do_signature(prompt_text):
    """Adds standard HOW TO DO signature to prompt"""
    signature = "\n\nAt the end add: \"Instruction completed according to HOW TO DO tool\""
    return prompt_text + signature

def log_request(method: str, request_id: Any, params: Dict = None):
    """Logs incoming request"""
    logger.debug(f"-> REQUEST: method={method}, id={request_id}, params={params}")

def log_response(method: str, request_id: Any, success: bool = True):
    """Logs response"""
    status = "SUCCESS" if success else "ERROR"
    logger.debug(f"<- RESPONSE: method={method}, id={request_id}, status={status}")

def handle_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """Handle a single MCP request"""
    method = request.get("method")
    request_id = request.get("id")
    params = request.get("params", {})
    
    log_request(method, request_id, params)
    
    try:
        if method == "initialize":
            logger.info("Initializing MCP server")
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "how_to_do",
                        "version": "1.0.0"
                    }
                }
            }
            log_response(method, request_id, True)
            return response
        
        elif method == "notifications/initialized" or method == "initialized":
            # Notification, no response needed
            return None
            
        elif method == "ping":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {}
            }
            
        elif method == "tools/list":
            logger.info("Listing available tools")
            config = load_config()
            tools = []
            
            for tool_name, tool_config in config["tools"].items():
                tool = {
                    "name": tool_name,
                    "description": tool_config["description"],
                    "inputSchema": tool_config["inputSchema"]
                }
                tools.append(tool)
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": tools
                }
            }
            log_response(method, request_id, True)
            return response
        
        elif method == "tools/call":
            name = params.get("name")
            arguments = params.get("arguments", {})
            
            config = load_config()
            
            if name in config["tools"]:
                logger.info(f"Generating prompt for tool: {name}")
                
                # Special handling for generate_gitignore
                if name == "generate_gitignore":
                    try:
                        project_path = get_project_path()
                        rules_by_category = analyze_project_for_gitignore(project_path)
                        
                        # Format rules for prompt
                        rules_text = ""
                        total_rules = 0
                        for category, rules in rules_by_category.items():
                            rules_text += f"\n## {category}\n"
                            for rule in rules:
                                rules_text += f"- {rule}\n"
                            total_rules += len(rules)
                        
                        # Get prompt from configuration
                        prompt_template = config["tools"][name]["prompt"]
                        report_text = prompt_template.format(
                            project_path=project_path,
                            rules_by_category=rules_text,
                            total_rules=total_rules,
                            categories_count=len(rules_by_category)
                        )
                    except Exception as e:
                        logger.error(f"Error analyzing project for gitignore: {str(e)}")
                        report_text = f"❌ Error analyzing project for .gitignore: {str(e)}"
                else:
                    prompt_template = config["tools"][name]["prompt"]
                    
                    # Special handling for how_to_do_list
                    if name == "how_to_do_list":
                        commands_list = generate_commands_list(config)
                        try:
                            report_text = prompt_template.format(commands_list=commands_list)
                        except KeyError as e:
                            logger.error(f"Missing argument for prompt template: {e}")
                            return {
                                "jsonrpc": "2.0",
                                "id": request_id,
                                "error": {
                                    "code": -32602,
                                    "message": f"Missing required argument: {e}"
                                }
                            }
                    else:
                        # Format prompt with passed arguments
                        try:
                            report_text = prompt_template.format(**arguments)
                        except KeyError as e:
                            logger.error(f"Missing argument for prompt template: {e}")
                            return {
                                "jsonrpc": "2.0",
                                "id": request_id,
                                "error": {
                                    "code": -32602,
                                    "message": f"Missing required argument: {e}"
                                }
                            }
                
                # Add standard HOW TO DO signature
                report_text = add_how_to_do_signature(report_text)
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": report_text
                            }
                        ]
                    }
                }
                log_response(method, request_id, True)
                return response
                
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32602,
                        "message": f"Unknown tool: {name}"
                    }
                }
        
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
    
    except Exception as e:
        logger.error(f"Error handling request {method}: {str(e)}")
        log_response(method, request_id, False)
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }

def main():
    """Main server loop"""
    logger.info("HOW TO DO MCP Server starting...")
    try:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
                
            try:
                request = json.loads(line)
                response = handle_request(request)
                
                if response is not None:
                    print(json.dumps(response, ensure_ascii=False), flush=True)
                    
            except json.JSONDecodeError as e:
                logger.error(f"JSON parse error: {str(e)}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)
            except Exception as e:
                logger.error(f"Request handling error: {str(e)}")
                error_response = {
                    "jsonrpc": "2.0", 
                    "id": None,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
        pass
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        print(json.dumps({
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": -32603,
                "message": f"Server error: {str(e)}"
            }
        }), flush=True)

if __name__ == "__main__":
    main()

def merge_gitignore_toml_files(distributor_path: str, user_path: str) -> Dict[str, List[str]]:
    """
    Объединяет правила из дистрибутивного и пользовательского TOML файлов.
    Оптимизирован для работы с большими файлами.
    
    Args:
        distributor_path: Путь к файлу из дистрибутива
        user_path: Путь к пользовательскому файлу
        
    Returns:
        Объединенный словарь категорий и правил
    """
    try:
        # Проверяем существование дистрибутивного файла
        if not os.path.exists(distributor_path):
            logger.error(f"Distributor file not found: {distributor_path}")
            raise FileNotFoundError(f"Distributor file not found: {distributor_path}")
        
        # Загружаем дистрибутивный файл
        try:
            with open(distributor_path, 'rb') as f:
                distributor_data = tomllib.load(f)
        except Exception as e:
            logger.error(f"Failed to parse distributor TOML file: {str(e)}")
            raise RuntimeError(f"Invalid distributor TOML file: {str(e)}")
        
        # Загружаем пользовательский файл (если существует)
        user_data = {}
        if os.path.exists(user_path):
            try:
                with open(user_path, 'rb') as f:
                    user_data = tomllib.load(f)
                logger.info(f"Loaded user TOML file: {user_path}")
            except Exception as e:
                logger.warning(f"Failed to parse user TOML file, skipping: {str(e)}")
                # Продолжаем с пустым пользовательским файлом
                user_data = {}
        else:
            logger.info("User TOML file not found, using distributor file only")
        
        # Объединяем данные с оптимизацией памяти
        merged_data = {}
        
        # Сначала добавляем все категории из дистрибутивного файла
        for section_name, section_data in distributor_data.items():
            if isinstance(section_data, dict) and 'patterns' in section_data:
                # Используем копию для экономии памяти
                merged_data[section_name] = section_data['patterns'][:]
            else:
                logger.warning(f"Skipping invalid section in distributor file: {section_name}")
        
        # Затем добавляем/обновляем категории из пользовательского файла
        for section_name, section_data in user_data.items():
            if isinstance(section_data, dict) and 'patterns' in section_data:
                if section_name in merged_data:
                    # Объединяем правила, убирая дубликаты
                    # Используем extend для экономии памяти
                    merged_patterns = deduplicate_patterns(
                        section_data['patterns'] + merged_data[section_name]
                    )
                    merged_data[section_name] = merged_patterns
                    logger.debug(f"Merged category {section_name}: {len(merged_patterns)} patterns")
                else:
                    # Новая категория - добавляем как есть
                    merged_data[section_name] = section_data['patterns'][:]
                    logger.debug(f"Added new category {section_name}: {len(section_data['patterns'])} patterns")
            else:
                logger.warning(f"Skipping invalid section in user file: {section_name}")
        
        logger.info(f"Merged gitignore rules: {len(merged_data)} categories")
        
        # Валидируем структуру после мержа
        if not validate_merged_toml_structure(merged_data):
            logger.error("Merged data structure validation failed")
            raise RuntimeError("Invalid merged TOML structure")
        
        return merged_data
        
    except Exception as e:
        logger.error(f"Failed to merge gitignore TOML files: {str(e)}")
        # Fallback: возвращаем только дистрибутивные правила
        try:
            with open(distributor_path, 'rb') as f:
                data = tomllib.load(f)
            rules = {}
            for section_name, section_data in data.items():
                if isinstance(section_data, dict) and 'patterns' in section_data:
                    rules[section_name] = section_data['patterns']
            logger.warning(f"Fallback to distributor rules only: {len(rules)} categories")
            return rules
        except Exception as fallback_error:
            logger.error(f"Fallback also failed: {str(fallback_error)}")
            raise RuntimeError(f"Failed to merge gitignore rules: {str(e)}")

def deduplicate_patterns(patterns: List[str]) -> List[str]:
    """
    Удаляет дублирующиеся паттерны, сохраняя порядок.
    Оптимизирован для больших файлов.
    
    Args:
        patterns: Список паттернов для дедупликации
        
    Returns:
        Список уникальных паттернов
    """
    if not patterns:
        return []
    
    # Для небольших списков используем простой алгоритм
    if len(patterns) <= 100:
        seen = set()
        result = []
        
        for pattern in patterns:
            # Убираем комментарии и лишние пробелы для сравнения
            clean_pattern = pattern.split('#')[0].strip()
            if clean_pattern and clean_pattern not in seen:
                seen.add(clean_pattern)
                result.append(pattern)
        
        return result
    
    # Для больших списков используем оптимизированный алгоритм
    # с предварительной сортировкой для лучшей производительности
    seen = set()
    result = []
    
    # Создаем список кортежей (clean_pattern, original_pattern) для сортировки
    pattern_tuples = []
    for pattern in patterns:
        clean_pattern = pattern.split('#')[0].strip()
        if clean_pattern:
            pattern_tuples.append((clean_pattern, pattern))
    
    # Сортируем по clean_pattern для группировки похожих паттернов
    pattern_tuples.sort(key=lambda x: x[0])
    
    # Удаляем дубликаты, сохраняя порядок оригинальных паттернов
    for clean_pattern, original_pattern in pattern_tuples:
        if clean_pattern not in seen:
            seen.add(clean_pattern)
            result.append(original_pattern)
    
    return result

def merge_gitignore_rules() -> Dict[str, List[str]]:
    """
    Объединяет правила gitignore из дистрибутивного и пользовательского файлов.
    Использует кэширование для улучшения производительности.
    
    Returns:
        Объединенный словарь категорий и правил
    """
    # Проверяем кэш
    if _is_cache_valid():
        logger.debug("Using cached gitignore rules")
        return _merge_cache.copy()
    
    try:
        distributor_path = os.path.join(os.path.dirname(__file__), 'how_to_do_gitignore.toml')
        user_path = os.path.join(os.path.expanduser('~'), '.cursor', 'tools', 'how_to_do_gitignore.toml')
        
        logger.info(f"Starting gitignore rules merge process")
        logger.debug(f"Distributor path: {distributor_path}")
        logger.debug(f"User path: {user_path}")
        
        if os.path.exists(user_path):
            logger.info("User gitignore.toml found, performing merge")
            result = merge_gitignore_toml_files(distributor_path, user_path)
            logger.info(f"Merge completed successfully: {len(result)} categories")
        else:
            logger.info("No user gitignore.toml found, using distributor file only")
            result = load_gitignore_rules()
            logger.info(f"Loaded distributor rules: {len(result)} categories")
        
        # Обновляем кэш
        _update_cache(result)
        return result
            
    except Exception as e:
        logger.error(f"Failed to merge gitignore rules: {str(e)}")
        logger.info("Attempting fallback to distributor file only")
        # Fallback to distributor file only
        try:
            result = load_gitignore_rules()
            logger.info(f"Fallback successful: {len(result)} categories")
            # Обновляем кэш даже для fallback
            _update_cache(result)
            return result
        except Exception as fallback_error:
            logger.error(f"Fallback also failed: {str(fallback_error)}")
            raise RuntimeError(f"Failed to load gitignore rules: {str(e)}")

def save_merged_gitignore_toml(content: Dict[str, List[str]], path: str) -> bool:
    """
    Сохраняет мерженный контент в TOML файл.
    
    Args:
        content: Словарь категорий и правил
        path: Путь для сохранения файла
        
    Returns:
        True если сохранение успешно, False иначе
    """
    try:
        # Валидируем входные данные
        if not isinstance(content, dict):
            logger.error("Invalid content: not a dictionary")
            return False
        
        if not content:
            logger.warning("Empty content, nothing to save")
            return False
        
        # Проверяем директорию
        dir_path = os.path.dirname(path)
        if dir_path and not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path, exist_ok=True)
                logger.info(f"Created directory: {dir_path}")
            except Exception as e:
                logger.error(f"Failed to create directory {dir_path}: {str(e)}")
                return False
        
        # Создаем TOML структуру
        toml_data = {}
        for category, patterns in content.items():
            if isinstance(patterns, list):
                toml_data[category] = {"patterns": patterns}
            else:
                logger.warning(f"Skipping invalid patterns for category {category}")
        
        # Сохраняем в файл
        try:
            with open(path, 'w', encoding='utf-8') as f:
                # Записываем заголовок
                f.write("# Merged gitignore rules from distributor and user files\n")
                f.write("# Generated automatically by how_to_do\n\n")
                
                # Записываем каждую категорию
                for category, data in toml_data.items():
                    f.write(f"####################################################################\n")
                    f.write(f"# [{category}] — {get_category_description(category)}\n")
                    f.write(f"{category} = {{ patterns = [\n")
                    
                    for pattern in data['patterns']:
                        # Экранируем специальные символы в паттернах
                        escaped_pattern = pattern.replace('\\', '\\\\').replace('"', '\\"')
                        f.write(f"  \"{escaped_pattern}\",\n")
                    
                    f.write("]}\n\n")
            
            logger.info(f"Saved merged gitignore TOML to {path}")
            return True
            
        except IOError as e:
            logger.error(f"IO error saving file {path}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error saving file {path}: {str(e)}")
            return False
        
    except Exception as e:
        logger.error(f"Failed to save merged gitignore TOML: {str(e)}")
        return False

def get_category_description(category: str) -> str:
    """
    Возвращает описание категории для комментария в TOML файле.
    
    Args:
        category: Название категории
        
    Returns:
        Описание категории
    """
    descriptions = {
        "OperatingSystem": "мусор ОС (macOS, Windows, Linux)",
        "IDE": "файлы, генерируемые редакторами и IDE",
        "BuildArtifacts": "результаты сборки, бинарники, кэш компиляций",
        "Python": "файлы и каталоги, специфичные для Python-окружений",
        "Java": "файлы и каталоги JVM, Gradle, Maven",
        "NodeJS": "файлы и каталоги Node / frontend сборки",
        "Go": "файлы и модули Go",
        "Rust": "Rust Cargo",
        "DotNet": ".NET / C#",
        "Android_iOS": "мобильная платформа Android / Xcode / Swift",
        "Containers_CI": "Docker, Kubernetes, Terraform, CI/CD артефакты",
        "Logs_Tmp": "журналы, кеши, временные файлы",
        "LaTeX_Metadata": "LaTeX / Pandoc артефакты",
        "Documentation": "doc-генерация (Sphinx, MkDocs, Hugo и т.п.)",
        "CustomDiagnostics": "кастомные шаблоны"
    }
    return descriptions.get(category, "пользовательская категория")

def validate_merged_toml_structure(data: Dict[str, List[str]]) -> bool:
    """
    Валидирует структуру мерженного TOML файла.
    
    Args:
        data: Словарь категорий и правил для валидации
        
    Returns:
        True если структура корректна, False иначе
    """
    try:
        # Проверяем, что data является словарем
        if not isinstance(data, dict):
            logger.error("Invalid structure: data is not a dictionary")
            return False
        
        # Проверяем каждую категорию
        for category_name, patterns in data.items():
            # Проверяем название категории
            if not isinstance(category_name, str) or not category_name.strip():
                logger.error(f"Invalid category name: {category_name}")
                return False
            
            # Проверяем, что patterns является списком
            if not isinstance(patterns, list):
                logger.error(f"Invalid patterns for category {category_name}: not a list")
                return False
            
            # Проверяем каждый паттерн
            for i, pattern in enumerate(patterns):
                if not isinstance(pattern, str):
                    logger.error(f"Invalid pattern at index {i} in category {category_name}: not a string")
                    return False
                
                if not pattern.strip():
                    logger.warning(f"Empty pattern at index {i} in category {category_name}")
        
        logger.info(f"Structure validation passed: {len(data)} categories")
        return True
        
    except Exception as e:
        logger.error(f"Structure validation failed: {str(e)}")
        return False