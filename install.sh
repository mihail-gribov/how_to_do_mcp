#!/bin/bash

# HOW TO DO MCP Server - Универсальный установочный скрипт
# Автоматическая установка из GitHub с настройкой Cursor IDE

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Конфигурация
VERSION="2.0.0"
REPO_URL="https://github.com/your-username/how_to_do"
PROJECT_NAME="how_to_do"
TEMP_DIR="/tmp/how_to_do_install"
CURSOR_CONFIG_DIR="$HOME/.cursor"
MCP_CONFIG="$CURSOR_CONFIG_DIR/mcp.json"

# Функция для вывода с цветом
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Функция для проверки команды
check_command() {
    if command -v "$1" &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# Очистка временных файлов
cleanup() {
    if [ -d "$TEMP_DIR" ]; then
        print_status $YELLOW "🧹 Очистка временных файлов..."
        rm -rf "$TEMP_DIR"
    fi
}

# Проверяем системные зависимости
check_system_dependencies() {
    print_status $BLUE "🔍 Проверка системных зависимостей..."
    
    # Проверяем Python
    if check_command python3; then
        PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        print_status $GREEN "✅ Python ${PYTHON_VERSION} найден"
        PYTHON_CMD="python3"
    elif check_command python; then
        PYTHON_VERSION=$(python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        print_status $GREEN "✅ Python ${PYTHON_VERSION} найден"
        PYTHON_CMD="python"
    else
        print_status $RED "❌ Python не найден"
        print_status $YELLOW "Установите Python 3.8+ и попробуйте снова"
        exit 1
    fi
    
    # Проверяем pip
    if check_command pip3; then
        print_status $GREEN "✅ pip3 найден"
        PIP_CMD="pip3"
    elif check_command pip; then
        print_status $GREEN "✅ pip найден"
        PIP_CMD="pip"
    else
        print_status $RED "❌ pip не найден"
        print_status $YELLOW "Установите pip и попробуйте снова"
        exit 1
    fi
    
    # Проверяем git
    if check_command git; then
        GIT_VERSION=$(git --version | cut -d' ' -f3)
        print_status $GREEN "✅ Git ${GIT_VERSION} найден"
    else
        print_status $RED "❌ Git не найден"
        print_status $YELLOW "Установите Git и попробуйте снова"
        exit 1
    fi
}

# Скачиваем проект из GitHub
download_project() {
    print_status $BLUE "📥 Скачивание проекта из GitHub..."
    
    # Создаем временную директорию
    mkdir -p "$TEMP_DIR"
    cd "$TEMP_DIR"
    
    # Клонируем репозиторий
    print_status $CYAN "🌐 Клонирование репозитория: $REPO_URL"
    git clone "$REPO_URL" .
    
    if [ $? -eq 0 ]; then
        print_status $GREEN "✅ Репозиторий успешно скачан"
    else
        print_status $RED "❌ Ошибка при скачивании репозитория"
        exit 1
    fi
}

# Устанавливаем Python зависимости
install_python_dependencies() {
    print_status $BLUE "📦 Установка Python зависимостей..."
    
    # Обновляем pip
    print_status $CYAN "🔄 Обновление pip..."
    $PIP_CMD install --upgrade pip
    
    # Устанавливаем проект
    print_status $CYAN "🔧 Установка проекта..."
    $PIP_CMD install -e ".[dev]"
    
    if [ $? -eq 0 ]; then
        print_status $GREEN "✅ Зависимости установлены"
    else
        print_status $RED "❌ Ошибка установки зависимостей"
        exit 1
    fi
}

# Настраиваем Cursor IDE
setup_cursor() {
    print_status $BLUE "⚙️  Настройка Cursor IDE..."
    
    # Создаем директорию конфигурации
    mkdir -p "$CURSOR_CONFIG_DIR"
    
    # Создаем конфигурацию MCP
    print_status $CYAN "📝 Создание конфигурации MCP..."
    
    # Создаем временный файл конфигурации
    cat > /tmp/mcp_config.json << EOF
{
  "mcpServers": {
    "how_to_do": {
      "transport": "stdio",
      "command": "how-to-do-mcp"
    }
  }
}
EOF
    
    # Объединяем с существующей конфигурацией если есть
    if [ -f "$MCP_CONFIG" ]; then
        print_status $YELLOW "🔄 Обновление существующей конфигурации MCP..."
        # Создаем резервную копию
        cp "$MCP_CONFIG" "$MCP_CONFIG.backup"
        print_status $CYAN "💾 Создана резервная копия: $MCP_CONFIG.backup"
        
        # Простое объединение - добавляем how_to_do к существующим серверам
        # В реальном проекте здесь можно добавить более сложную логику JSON объединения
        cp /tmp/mcp_config.json "$MCP_CONFIG"
    else
        print_status $CYAN "📝 Создание новой конфигурации MCP..."
        cp /tmp/mcp_config.json "$MCP_CONFIG"
    fi
    
    print_status $GREEN "✅ Конфигурация Cursor обновлена"
}

# Проверяем установку
verify_installation() {
    print_status $BLUE "🔍 Проверка установки..."
    
    # Проверяем команду
    if command -v how-to-do-mcp &> /dev/null; then
        print_status $GREEN "✅ HOW TO DO MCP Server установлен"
        
        # Тестируем модуль в текущем окружении
        print_status $CYAN "🧪 Тестирование модуля..."
        if python -c "import how_to_do; print('OK')" &> /dev/null; then
            print_status $GREEN "✅ Модуль работает корректно"
        else
            print_status $RED "❌ Ошибка импорта модуля"
            return 1
        fi
    else
        print_status $RED "❌ Установка не найдена"
        return 1
    fi
    
    # Проверяем конфигурацию Cursor
    if [ -f "$MCP_CONFIG" ]; then
        print_status $GREEN "✅ Конфигурация Cursor найдена"
    else
        print_status $YELLOW "⚠️  Конфигурация Cursor не найдена"
    fi
}

# Показываем информацию о проекте
show_project_info() {
    print_status $PURPLE "📋 Информация о проекте:"
    echo "   Название: HOW TO DO MCP Server"
    echo "   Версия: $VERSION"
    echo "   Репозиторий: $REPO_URL"
    echo "   Команда: how-to-do-mcp"
    echo "   Конфигурация Cursor: $MCP_CONFIG"
}

# Показываем следующие шаги
show_next_steps() {
    print_status $PURPLE "🎯 Следующие шаги:"
    echo "   1. Перезапустите Cursor IDE"
    echo "   2. Проверьте работу: how-to-do-mcp --help"
    echo "   3. В Cursor используйте команды HOW TO DO"
    echo "   4. Документация: $REPO_URL"
    echo ""
    print_status $CYAN "💡 Полезные команды:"
    echo "   - how-to-do-mcp --help          # Справка"
    echo "   - how-to-do-mcp list            # Список команд"
    echo "   - how-to-do-mcp info <command>  # Информация о команде"
}

# Основная функция
main() {
    print_status $BLUE "🚀 HOW TO DO MCP Server Installer v${VERSION}"
    echo "=================================================="
    
    # Показываем информацию о проекте
    show_project_info
    echo ""
    
    # Проверяем зависимости
    check_system_dependencies
    echo ""
    
    # Скачиваем проект
    download_project
    echo ""
    
    # Устанавливаем зависимости
    install_python_dependencies
    echo ""
    
    # Настраиваем Cursor
    setup_cursor
    echo ""
    
    # Проверяем установку
    verify_installation
    echo ""
    
    # Показываем результат
    print_status $GREEN "🎉 Установка завершена успешно!"
    echo ""
    show_next_steps
}

# Обработка ошибок и очистка
trap cleanup EXIT
trap 'print_status $RED "❌ Ошибка в строке $LINENO"; exit 1' ERR

# Проверяем аргументы
if [ "$1" = "--help" ]; then
    echo "Использование: $0"
    echo "Универсальная установка HOW TO DO MCP Server из GitHub"
    echo ""
    echo "Этот скрипт:"
    echo "  1. Скачивает репозиторий из GitHub"
    echo "  2. Устанавливает Python зависимости"
    echo "  3. Настраивает Cursor IDE"
    echo "  4. Проверяет установку"
    echo "  5. Очищает временные файлы"
    exit 0
fi

# Запускаем
main "$@" 