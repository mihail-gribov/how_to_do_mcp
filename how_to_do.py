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
from datetime import datetime
from typing import Any, Dict, List, Set
from pathlib import Path

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

def load_gitignore_rules() -> Dict[str, List[str]]:
    """Loads rules from for_gitignore.toml"""
    try:
        toml_path = os.path.join(os.path.dirname(__file__), 'for_gitignore.toml')
        with open(toml_path, 'rb') as f:
            data = tomllib.load(f)
        
        # Convert TOML structure to dictionary
        rules = {}
        for section_name, section_data in data.items():
            if isinstance(section_data, dict) and 'patterns' in section_data:
                rules[section_name] = section_data['patterns']
        
        logger.info(f"Loaded {len(rules)} gitignore rule sections")
        return rules
    except Exception as e:
        logger.error(f"Failed to load gitignore rules: {str(e)}")
        raise RuntimeError(f"Failed to load gitignore rules: {str(e)}")

def scan_project_files(project_path: str) -> Set[str]:
    """Scans the project file structure"""
    files = set()
    project_path = Path(project_path)
    
    try:
        for item in project_path.rglob('*'):
            relative_path = item.relative_to(project_path)
            
            if item.is_file():
                files.add(str(relative_path))
            elif item.is_dir():
                files.add(str(relative_path) + '/')
        
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
        command_info += f"- Описание: {tool_config['description']}\n"
        
        if "inputSchema" in tool_config and "properties" in tool_config["inputSchema"]:
            properties = tool_config["inputSchema"]["properties"]
            if properties:
                command_info += "- Параметры:\n"
                for param_name, param_config in properties.items():
                    param_desc = param_config.get("description", "Без описания")
                    command_info += f"  - `{param_name}`: {param_desc}\n"
            else:
                command_info += "- Параметры: нет\n"
        else:
            command_info += "- Параметры: нет\n"
        
        commands_list.append(command_info)
    
    return "\n".join(commands_list)

def add_how_to_do_signature(prompt_text):
    """Добавляет стандартную подпись HOW TO DO к промпту"""
    signature = "\n\nВ конце добавь: \"Выполнена инструкция согласно инструменту HOW TO DO\""
    return prompt_text + signature

def log_request(method: str, request_id: Any, params: Dict = None):
    """Логирует входящий запрос"""
    logger.debug(f"-> REQUEST: method={method}, id={request_id}, params={params}")

def log_response(method: str, request_id: Any, success: bool = True):
    """Логирует ответ"""
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
                
                # Специальная обработка для generate_gitignore
                if name == "generate_gitignore":
                    try:
                        project_path = get_project_path()
                        rules_by_category = analyze_project_for_gitignore(project_path)
                        
                        # Форматируем правила для промпта
                        rules_text = ""
                        total_rules = 0
                        for category, rules in rules_by_category.items():
                            rules_text += f"\n## {category}\n"
                            for rule in rules:
                                rules_text += f"- {rule}\n"
                            total_rules += len(rules)
                        
                        # Получаем промпт из конфигурации
                        prompt_template = config["tools"][name]["prompt"]
                        report_text = prompt_template.format(
                            project_path=project_path,
                            rules_by_category=rules_text,
                            total_rules=total_rules,
                            categories_count=len(rules_by_category)
                        )
                    except Exception as e:
                        logger.error(f"Error analyzing project for gitignore: {str(e)}")
                        report_text = f"❌ Ошибка при анализе проекта для .gitignore: {str(e)}"
                else:
                    prompt_template = config["tools"][name]["prompt"]
                    
                    # Специальная обработка для how_to_do_list
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
                        # Форматируем промпт с переданными аргументами
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
                
                # Добавляем стандартную подпись HOW TO DO
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