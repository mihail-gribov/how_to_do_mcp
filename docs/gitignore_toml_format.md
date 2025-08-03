# Формат TOML файла gitignore

## Обзор

Файл `how_to_do_gitignore.toml` содержит правила для создания `.gitignore` файлов, организованные по категориям. Правила автоматически мержатся с пользовательским файлом при установке и обновлении.

## Структура файла

### Основная структура

```toml
# Категория правил
CategoryName = { patterns = [
  "pattern1",           # комментарий
  "pattern2",           # еще комментарий
  "pattern3"            # последний паттерн
]}
```

### Примеры категорий

```toml
####################################################################
# [OperatingSystem] — мусор ОС (macOS, Windows, Linux)
OperatingSystem = { patterns = [
  ".DS_Store",           # macOS Desktop metadata
  "Thumbs.db",           # Windows Explorer thumbnail cache
  "ehthumbs.db",
  "Icon?",
  ".Spotlight-V100",
  ".Trashes",
  "*.swp", "*.swo", "*~" # Vim/shell backup files
]}

####################################################################
# [IDE] — файлы, генерируемые редакторами и IDE
IDE = { patterns = [
  ".idea/", "*.iml", "*.iws", "*.ipr",           # JetBrains IDEA / PyCharm / etc.
  ".vscode/", "*.code-workspace",                # Visual Studio Code
  ".cursor/", "*.cursor-workspace",              # Cursor IDE
  "*.sln", "*.suo", "*.user", "*.ncb", "*.sdf",  # Visual Studio
  ".metadata/", ".classpath", ".project",        # Eclipse
  "*.launch",                                    # Eclipse run configs
  "*.sublime-project", "*.sublime-workspace",    # Sublime Text
  ".atom/",                                      # Atom
  ".emacs.d/", "*.elc", "*.eln",                 # Emacs
  ".vim/", "*.viminfo",                          # Vim
  "#*#",                                         # Generic lock/temp
  "*.tmproj"                                     # TextMate
]}
```

## Правила именования

### Категории
- Используйте PascalCase для названий категорий
- Названия должны быть описательными
- Избегайте специальных символов кроме подчеркивания

### Паттерны
- Используйте стандартные gitignore паттерны
- Поддерживаются wildcards: `*`, `?`, `[abc]`
- Поддерживаются отрицания: `!pattern`
- Поддерживаются директории: `dir/`

## Процесс мержа

### Приоритеты
1. **Пользовательские правила** имеют приоритет над дистрибутивными
2. **Новые категории** из пользовательского файла добавляются
3. **Дубликаты** автоматически удаляются
4. **Комментарии** сохраняются из пользовательского файла

### Алгоритм мержа
```python
# Псевдокод алгоритма мержа
for category in distributor_categories:
    merged_data[category] = distributor_patterns[category]

for category in user_categories:
    if category in merged_data:
        # Объединяем правила с дедупликацией
        merged_patterns = deduplicate(user_patterns + distributor_patterns)
        merged_data[category] = merged_patterns
    else:
        # Добавляем новую категорию
        merged_data[category] = user_patterns
```

## Примеры пользовательских правил

### Добавление новых IDE
```toml
IDE = { patterns = [
  ".vscode/",            # Visual Studio Code
  ".sublime-project",    # Sublime Text (custom)
  ".atom/",              # Atom (custom)
  ".brackets.json",      # Brackets (custom)
  "*.sublime-workspace"  # Sublime workspace (custom)
]}
```

### Создание новой категории
```toml
CustomProject = { patterns = [
  "config/local.json",   # локальные настройки
  "logs/",               # логи приложения
  "temp/",               # временные файлы
  "cache/",              # кэш приложения
  "uploads/",            # загруженные файлы
  "backups/"             # резервные копии
]}
```

### Расширение существующей категории
```toml
Python = { patterns = [
  "venv/",               # virtual environments
  "pip-wheel-metadata/", # pip metadata (custom)
  ".tox/",               # tox (custom)
  ".pytest_cache/",      # pytest cache (custom)
  ".coverage",           # coverage reports (custom)
  "htmlcov/"             # coverage HTML (custom)
]}
```

## Обработка ошибок

### Некорректный TOML
- При ошибке парсинга пользовательского файла используется только дистрибутивный
- Логируется предупреждение о пропуске пользовательского файла
- Процесс установки продолжается

### Отсутствующие файлы
- Если пользовательский файл отсутствует, используется только дистрибутивный
- Если дистрибутивный файл отсутствует, генерируется ошибка

### Валидация структуры
- Проверяется корректность типов данных
- Валидируется структура категорий
- Проверяется наличие обязательных полей

## Лучшие практики

### Организация правил
- Группируйте связанные паттерны в одну категорию
- Используйте описательные названия категорий
- Добавляйте комментарии к сложным паттернам

### Совместимость
- Используйте стандартные gitignore паттерны
- Тестируйте паттерны на реальных проектах
- Избегайте слишком специфичных паттернов

### Обновления
- Регулярно обновляйте дистрибутивный файл
- Проверяйте совместимость пользовательских правил
- Делайте резервные копии перед обновлениями

## Отладка

### Логирование
- Все операции мержа логируются
- Ошибки парсинга записываются в лог
- Результаты валидации отображаются

### Диагностика
```bash
# Проверка структуры файла
python3 -c "import tomllib; tomllib.load(open('how_to_do_gitignore.toml', 'rb'))"

# Проверка мержа
python3 -c "from how_to_do import merge_gitignore_rules; print(merge_gitignore_rules())"
```

## Миграция

### Из старого формата
- Старые файлы автоматически конвертируются
- Сохраняется обратная совместимость
- Логируются предупреждения о устаревшем формате

### В новый формат
- Новые функции требуют обновленного формата
- Рекомендуется обновление при возможности
- Предоставляется инструмент миграции 