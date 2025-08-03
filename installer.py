#!/usr/bin/env python3
"""
HOW TO DO Installer - инсталляционные функции для проекта

Этот файл содержит функции для установки и настройки проекта,
включая работу с gitignore файлами, создание бэкапов и валидацию.
"""

import os
import json
import logging
import sys
import tomllib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

# Настройка логирования
import logging
import sys

# Configure logging to stderr for debugging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [HOW_TO_DO_INSTALLER] %(levelname)s: %(message)s',
    stream=sys.stderr,
    datefmt='%H:%M:%S'
)

logger = logging.getLogger(__name__)

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

def load_config():
    """Loads configuration from JSON file"""
    try:
        config_path = os.path.splitext(__file__)[0] + '.json'
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        logger.info(f"Configuration loaded from {config_path}")
        return config
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
    """Loads rules from how_to_do_gitignore.toml (already merged during installation)"""
    try:
        # Загружаем готовый мерженный файл из tools директории
        rules_path = os.path.join(os.path.expanduser('~'), '.cursor', 'tools', 'how_to_do_gitignore.toml')
        
        if not os.path.exists(rules_path):
            # Fallback к дистрибутивному файлу если мерженный не найден
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


def load_gitignore_rules() -> Dict[str, List[str]]:
    """Loads rules from how_to_do_gitignore.toml (already merged during installation)"""
    try:
        # Загружаем готовый мерженный файл из tools директории
        rules_path = os.path.join(os.path.expanduser('~'), '.cursor', 'tools', 'how_to_do_gitignore.toml')
        
        if not os.path.exists(rules_path):
            # Fallback к дистрибутивному файлу если мерженный не найден
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