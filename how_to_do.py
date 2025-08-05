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

# Cache for merge results
_merge_cache = {}
_cache_timestamp = None
_cache_duration = timedelta(minutes=5)  # Cache for 5 minutes

def _is_cache_valid() -> bool:
    """Checks if the cache is valid"""
    global _cache_timestamp
    if _cache_timestamp is None:
        return False
    return datetime.now() - _cache_timestamp < _cache_duration

def _clear_cache():
    """Clears the cache"""
    global _merge_cache, _cache_timestamp
    _merge_cache = {}
    _cache_timestamp = None

def _update_cache(data: Dict[str, List[str]]):
    """Updates the cache"""
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

def get_project_path() -> str:
    """Gets the path to the current project"""
    project_path = os.getenv('PROJECT_PATH')
    if project_path:
        return project_path
    
    return os.getcwd()

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


def load_gitignore_rules() -> Dict[str, List[str]]:
    """Loads rules from how_to_do_gitignore.toml (already merged during installation)"""
    try:
        # Load the ready merged file from tools directory
        rules_path = os.path.join(os.path.expanduser('~'), '.cursor', 'tools', 'how_to_do_gitignore.toml')
        
        if not os.path.exists(rules_path):
            # Fallback to distributor file if merged file not found
            distributor_path = os.path.join(os.path.dirname(__file__), 'how_to_do_gitignore.toml')
            if os.path.exists(distributor_path):
                logger.warning("Merged gitignore.toml not found, using distributor file")
                rules_path = distributor_path
            else:
                raise FileNotFoundError("No gitignore rules file found")
        
        with open(rules_path, 'rb') as f:
            data = tomllib.load(f)
        
        # Convert TOML structure to dictionary
        rules = {}
        for section_name, section_data in data.items():
            if isinstance(section_data, dict) and 'patterns' in section_data:
                rules[section_name] = section_data['patterns']
        
        logger.info(f"Loaded {len(rules)} gitignore rule sections from {rules_path}")
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
        # Log the project directory name
        project_name = os.path.basename(project_path)
        logger.info(f"Analyzing project directory: {project_name} ({project_path})")
        
        rules = load_gitignore_rules()
        
        # Log the source of rules
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
    instruction = "\n\nПроверь, что ты точно следуешь инструкции."
    return prompt_text + signature + instruction

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
                        # Get project_path from agent parameters
                        project_path = arguments.get("project_path")
                        if not project_path:
                            # Fallback to current directory if no path provided
                            project_path = get_project_path()
                            logger.warning("No project_path provided, using current directory")
                        
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
                        
                        # Determine .gitignore file path
                        gitignore_path = os.path.join(project_path, '.gitignore')
                        
                        report_text = prompt_template.format(
                            project_path=project_path,
                            rules_by_category=rules_text,
                            total_rules=total_rules,
                            categories_count=len(rules_by_category),
                            gitignore_path=gitignore_path
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





