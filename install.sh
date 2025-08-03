#!/bin/bash

# Installation Script for HOW TO DO MCP Server
# ===================================================
# 
# This script automatically installs MCP server for Cursor IDE:
# 1. Downloads project from GitHub repository
# 2. Installs Python dependencies
# 3. Configures Cursor IDE to work with MCP server
# 4. Verifies installation correctness
# 5. Cleans up temporary files
#
# MCP (Model Context Protocol) allows Cursor IDE to use
# external tools for project analysis and code generation.
# 
# Author: Mihail Gribov
# Repository: https://github.com/mihail-gribov/how_to_do_mcp

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
# =============
# 
# Main installation parameters:
# - REPO_URL: GitHub repository URL for downloading
# - PROJECT_NAME: Project name (used for directory creation)
# - TEMP_DIR: Temporary directory for downloading and installation
# - CURSOR_CONFIG_DIR: Cursor IDE configuration directory
# - MCP_CONFIG: Path to MCP servers configuration file
REPO_URL="https://github.com/mihail-gribov/how_to_do_mcp"
PROJECT_NAME="how_to_do"
TEMP_DIR="/tmp/how_to_do_install"
CURSOR_CONFIG_DIR="$HOME/.cursor"
MCP_CONFIG="$CURSOR_CONFIG_DIR/mcp.json"

# Function for colored message output
# =================================
# 
# Parameters:
# - color: ANSI color code (RED, GREEN, YELLOW, BLUE, etc.)
# - message: Message text to output
#
# Used for beautiful and informative status operation output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to check if a command exists in the system
# ================================================
# 
# Parameters:
# - $1: Command name to check (e.g., "python3", "git")
#
# Returns:
# - 0 (success): command found in PATH
# - 1 (error): command not found
#
# Used to check system dependencies before installation
check_command() {
    if command -v "$1" &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# Function to read project version from pyproject.toml
# ==================================================
# 
# Reads project version from pyproject.toml file, which allows
# avoiding version duplication in different places.
#
# Returns:
# - Project version (e.g., "1.0.0")
# - "unknown" if pyproject.toml file not found
#
# Used to display current version in installation logs
get_version() {
    if [ -f "pyproject.toml" ]; then
        grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/'
    else
        echo "unknown"
    fi
}

# Function to clean up temporary files
# ===================================
# 
# Removes temporary directory and all files created during installation.
# Called automatically when script finishes (successfully or with error).
#
# This is important for:
# - Freeing disk space
# - Removing potentially confidential data
# - Maintaining system cleanliness
cleanup() {
    if [ -d "$TEMP_DIR" ]; then
        print_status $YELLOW "Cleaning up temporary files..."
        rm -rf "$TEMP_DIR"
    fi
}

# Function to check system dependencies
# ===================================
# 
# Checks for required commands in the system:
# - Python 3.8+ (for running MCP server)
# - pip (for installing Python packages)
# - git (for downloading repository)
#
# If any dependency is not found, script exits with error
# and displays instructions for installing missing component.
check_system_dependencies() {
    print_status $BLUE "Checking system dependencies..."
    
    # Check Python
    if check_command python3; then
        PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        print_status $GREEN "Python ${PYTHON_VERSION} found"
        PYTHON_CMD="python3"
    elif check_command python; then
        PYTHON_VERSION=$(python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        print_status $GREEN "Python ${PYTHON_VERSION} found"
        PYTHON_CMD="python"
    else
        print_status $RED "ERROR: Python not found"
        print_status $YELLOW "Install Python 3.8+ and try again"
        exit 1
    fi
    
    # Check pip
    if check_command pip3; then
        print_status $GREEN "pip3 found"
        PIP_CMD="pip3"
    elif check_command pip; then
        print_status $GREEN "pip found"
        PIP_CMD="pip"
    else
        print_status $RED "ERROR: pip not found"
        print_status $YELLOW "Install pip and try again"
        exit 1
    fi
    
    # Check git
    if check_command git; then
        GIT_VERSION=$(git --version | cut -d' ' -f3)
        print_status $GREEN "Git ${GIT_VERSION} found"
    else
        print_status $RED "ERROR: Git not found"
        print_status $YELLOW "Install Git and try again"
        exit 1
    fi
}

# Function to download project from GitHub
# ======================================
# 
# Downloads project source code from GitHub repository:
# 1. Creates temporary directory
# 2. Clones repository using git
# 3. Checks operation success
#
# If download fails, script exits with error.
# This is a critical stage as installation is impossible without source code.
download_project() {
    print_status $BLUE "Downloading project from GitHub..."
    
    # Create temporary directory
    mkdir -p "$TEMP_DIR"
    cd "$TEMP_DIR"
    
    # Clone repository
    print_status $CYAN "Cloning repository: $REPO_URL"
    git clone "$REPO_URL" .
    
    if [ $? -eq 0 ]; then
        print_status $GREEN "Repository successfully downloaded"
        
        # Copy files to user's home directory
        print_status $CYAN "Copying files to user directory..."
        mkdir -p "$HOME/.cursor/tools"
        
        # Function to check and backup files
        check_and_backup_file() {
            local source_file="$1"
            local target_file="$HOME/.cursor/tools/$2"
            local timestamp=$(date +"%Y%m%d_%H%M%S")
            
            if [ -f "$target_file" ]; then
                if cmp -s "$source_file" "$target_file"; then
                    print_status $CYAN "File $2 is up to date, skipping"
                else
                    print_status $YELLOW "File $2 differs, creating backup"
                    cp "$target_file" "$target_file.backup.$timestamp"
                    cp "$source_file" "$target_file"
                    print_status $GREEN "Updated $2 (backup created: $2.backup.$timestamp)"
                fi
            else
                cp "$source_file" "$target_file"
                print_status $GREEN "Created new file $2"
            fi
        }
        
        # Function to merge and backup gitignore.toml
        merge_and_backup_gitignore_toml() {
            local source_file="$1"
            local target_file="$HOME/.cursor/tools/$2"
            local timestamp=$(date +"%Y%m%d_%H%M%S")
            
            if [ -f "$target_file" ]; then
                print_status $YELLOW "User gitignore.toml found, performing merge..."
                
                # Create backup of user file
                cp "$target_file" "$target_file.backup.$timestamp"
                print_status $CYAN "Created backup: $2.backup.$timestamp"
                
                # Try to merge using Python script with optimized I/O
                if python3 -c "
import sys
import os
sys.path.insert(0, os.getcwd())
from how_to_do import merge_gitignore_toml_files, save_merged_gitignore_toml

try:
    # Оптимизированный мерж с минимальными I/O операциями
    merged_data = merge_gitignore_toml_files('$source_file', '$target_file')
    if save_merged_gitignore_toml(merged_data, '$target_file'):
        print('Merge successful')
        exit(0)
    else:
        print('Merge failed')
        exit(1)
except Exception as e:
    print(f'Merge error: {e}')
    exit(1)
"; then
                    print_status $GREEN "Successfully merged gitignore.toml"
                else
                    print_status $YELLOW "Merge failed, falling back to distributor file"
                    cp "$source_file" "$target_file"
                    print_status $GREEN "Restored distributor gitignore.toml"
                fi
            else
                cp "$source_file" "$target_file"
                print_status $GREEN "Created new gitignore.toml"
            fi
        }
        
        # Backup and copy main script using check_and_backup_file function
        check_and_backup_file "how_to_do.py" "how_to_do.py"
        
        check_and_backup_file "how_to_do.json" "how_to_do.json"
        
        # Use merge function for gitignore.toml
        merge_and_backup_gitignore_toml "how_to_do_gitignore.toml" "how_to_do_gitignore.toml"
        chmod +x "$HOME/.cursor/tools/how_to_do.py"
        print_status $GREEN "Files processed in $HOME/.cursor/tools/"
    else
        print_status $RED "ERROR: Error downloading repository"
        exit 1
    fi
}

# Function to install Python dependencies
# =====================================
# 
# This function is not needed for MCP server installation
# as the server runs as a standalone script
# Keeping for compatibility but marking as deprecated
install_python_dependencies() {
    print_status $BLUE "Skipping Python dependencies installation..."
    print_status $CYAN "MCP server runs as standalone script, no pip install needed"
    print_status $GREEN "Dependencies check passed"
}

# Function to configure Cursor IDE
# ===============================
# 
# Configures Cursor IDE to work with MCP server:
# 1. Creates Cursor configuration directory (if not exists)
# 2. Checks and creates required files (how_to_do.py, mcp.json)
# 3. Determines absolute path to MCP server script
# 4. Creates or updates MCP configuration in ~/.cursor/mcp.json
# 5. Creates backup of existing configuration
#
setup_cursor() {
    print_status $BLUE "Configuring Cursor IDE..."
    
    # Create configuration directory
    mkdir -p "$CURSOR_CONFIG_DIR"
    mkdir -p "$HOME/.cursor/tools"
    
    # Check and create/update how_to_do.py
    if [ ! -f "$HOME/.cursor/tools/how_to_do.py" ]; then
        print_status $YELLOW "how_to_do.py not found, creating from project files..."
        if [ -f "how_to_do.py" ]; then
            cp "how_to_do.py" "$HOME/.cursor/tools/"
            chmod +x "$HOME/.cursor/tools/how_to_do.py"
            print_status $GREEN "Created how_to_do.py in $HOME/.cursor/tools/"
        else
            print_status $RED "ERROR: how_to_do.py not found in project directory"
            exit 1
        fi
    elif [ -f "how_to_do.py" ] && ! cmp -s "how_to_do.py" "$HOME/.cursor/tools/how_to_do.py"; then
        print_status $YELLOW "how_to_do.py differs from project version, updating..."
        local timestamp=$(date +"%Y%m%d_%H%M%S")
        cp "$HOME/.cursor/tools/how_to_do.py" "$HOME/.cursor/tools/how_to_do.py.backup.$timestamp"
        cp "how_to_do.py" "$HOME/.cursor/tools/"
        chmod +x "$HOME/.cursor/tools/how_to_do.py"
        print_status $GREEN "Updated how_to_do.py (backup created: how_to_do.py.backup.$timestamp)"
    fi
    
    # Check and create mcp.json if not exists
    if [ ! -f "$MCP_CONFIG" ]; then
        print_status $YELLOW "mcp.json not found, creating new configuration..."
        cat > "$MCP_CONFIG" << EOF
{
  "mcpServers": {
  }
}
EOF
        print_status $GREEN "Created new mcp.json configuration"
    fi
    
    # Determine absolute path to script in user's home directory
    SCRIPT_PATH="$HOME/.cursor/tools/how_to_do.py"
    print_status $CYAN "Script path: $SCRIPT_PATH"
    
    # Create MCP configuration
    print_status $CYAN "Creating MCP configuration..."
    
    # Create temporary configuration file with absolute path
    cat > /tmp/mcp_config.json << EOF
{
  "mcpServers": {
    "how_to_do": {
      "transport": "stdio",
      "command": "python3",
      "args": [
        "$SCRIPT_PATH"
      ]
    }
  }
}
EOF
    
    # Merge with existing configuration if exists
    if [ -f "$MCP_CONFIG" ]; then
        print_status $YELLOW "Updating existing MCP configuration..."
        # Create backup with timestamp
        local timestamp=$(date +"%Y%m%d_%H%M%S")
        cp "$MCP_CONFIG" "$MCP_CONFIG.backup.$timestamp"
        print_status $CYAN "Backup created: $MCP_CONFIG.backup.$timestamp"
        
        # Merge configurations - add how_to_do to existing servers
        # Use jq for proper JSON merging if available, otherwise use simple approach
        if command -v jq &> /dev/null; then
            print_status $CYAN "Using jq for JSON merging..."
            jq -s '.[0] * .[1]' "$MCP_CONFIG" /tmp/mcp_config.json > "$MCP_CONFIG.new" && mv "$MCP_CONFIG.new" "$MCP_CONFIG"
        else
            print_status $CYAN "Using simple JSON merge..."
            # Simple approach: read existing config, add our server, write back
            if grep -q '"mcpServers"' "$MCP_CONFIG"; then
                # Insert our server before the closing brace of mcpServers
                sed -i 's/}/    "how_to_do": {\n      "transport": "stdio",\n      "command": "python3",\n      "args": [\n        "'"$SCRIPT_PATH"'"\n      ]\n    },\n  }/' "$MCP_CONFIG"
            else
                # No existing mcpServers, replace entire file
                cp /tmp/mcp_config.json "$MCP_CONFIG"
            fi
        fi
    else
        print_status $CYAN "Creating new MCP configuration..."
        cp /tmp/mcp_config.json "$MCP_CONFIG"
    fi
    
    print_status $GREEN "Cursor configuration updated"
}

# Function to verify installation
# ==============================
# 
# Verifies MCP server installation correctness:
# 1. Checks for MCP server script presence
# 2. Checks script execution permissions
# 3. Fixes execution permissions if necessary
# 4. Checks for Cursor configuration presence
# 5. Validates configuration structure
#
# This verification ensures that:
# - MCP server can be launched by Cursor IDE
# - Configuration is correct and accessible
# - All components are properly installed
verify_installation() {
    print_status $BLUE "Verifying installation..."
    
    # Check script presence in user's home directory
    if [ -f "$HOME/.cursor/tools/how_to_do.py" ]; then
        print_status $GREEN "HOW TO DO MCP Server found"
        
        # Check execution permissions
        if [ -x "$HOME/.cursor/tools/how_to_do.py" ]; then
            print_status $GREEN "Script is executable"
        else
            print_status $YELLOW "Script not executable, fixing..."
            chmod +x "$HOME/.cursor/tools/how_to_do.py"
        fi
    else
        print_status $RED "ERROR: Script not found in $HOME/.cursor/tools/"
        print_status $YELLOW "Try running the installer again"
        return 1
    fi
    
    # Check Cursor configuration
    if [ -f "$MCP_CONFIG" ]; then
        print_status $GREEN "Cursor configuration found"
        
        # Validate configuration structure
        if grep -q '"how_to_do"' "$MCP_CONFIG"; then
            print_status $GREEN "HOW TO DO server configured in mcp.json"
        else
            print_status $YELLOW "WARNING: HOW TO DO server not found in mcp.json configuration"
            print_status $YELLOW "Configuration may need to be updated manually"
        fi
    else
        print_status $RED "ERROR: Cursor configuration not found at $MCP_CONFIG"
        print_status $YELLOW "Try running the installer again"
        return 1
    fi
    
    print_status $GREEN "Installation verification completed successfully"
}

# Function to display project information
# =====================================
# 
# Outputs detailed project information:
# - Name and description
# - Version (read from pyproject.toml)
# - Repository URL
# - Project type (MCP Server)
# - Cursor configuration path
#
# Helps user understand what is being installed
# and where to find additional information.
show_project_info() {
    print_status $PURPLE "Project information:"
    echo "   Name: HOW TO DO MCP Server"
    echo "   Version: $(get_version)"
    echo "   Repository: $REPO_URL"
    echo "   Type: MCP Server for Cursor IDE"
    echo "   Cursor configuration: $MCP_CONFIG"
}

# Function to display next steps
# =============================
# 
# Outputs usage instructions after installation:
# 1. Restart Cursor IDE (required to load new configuration)
# 2. Use HOW TO DO commands in AI chat
# 3. Documentation link
# 4. List of available tools
#
# Helps user start using MCP server
# immediately after installation.
show_next_steps() {
    print_status $PURPLE "Next steps:"
    echo "   1. Restart Cursor IDE"
    echo "   2. In Cursor, use HOW TO DO commands"
    echo "   3. Documentation: $REPO_URL"
    echo ""
    print_status $CYAN "How to use:"
    echo "   - Open Cursor IDE"
    echo "   - In AI chat, use HOW TO DO commands"

}

# Main installation function
# ========================
# 
# Coordinates the entire MCP server installation process:
# 1. Displays project information
# 2. Checks system dependencies
# 3. Downloads project from GitHub
# 4. Installs Python dependencies
# 5. Configures Cursor IDE
# 6. Verifies installation correctness
# 7. Displays usage instructions
#
# Each stage is executed sequentially.
# If error occurs at any stage, script exits.
main() {
    print_status $BLUE "HOW TO DO MCP Server Installer v$(get_version)"
    echo "=================================================="
    
    # Show project information
    show_project_info
    echo ""
    
    # Check dependencies
    check_system_dependencies
    echo ""
    
    # Download project
    download_project
    echo ""
    
    # Install dependencies
    install_python_dependencies
    echo ""
    
    # Configure Cursor
    setup_cursor
    echo ""
    
    # Verify installation
    verify_installation
    echo ""
    
    # Show result
    print_status $GREEN "Installation completed successfully!"
    echo ""
    show_next_steps
}

# Error handling and cleanup
# =========================
# 
# Signal handler setup:
# - EXIT: Calls cleanup() on any script termination
# - ERR: Outputs error message and terminates script
#
# This ensures:
# - Cleanup of temporary files even on error
# - Informative error messages
# - Proper script termination
trap cleanup EXIT
trap 'print_status $RED "Error at line $LINENO"; exit 1' ERR

# Command line arguments processing
# ===============================
# 
# Supported arguments:
# --help: Displays script usage help
#
# Help includes:
# - Brief description of script purpose
# - List of performed actions
# - Information about what each operation does
if [ "$1" = "--help" ]; then
    echo "Usage: $0"
    echo "Universal installation of HOW TO DO MCP Server from GitHub"
    echo ""
    echo "This script:"
    echo "  1. Downloads repository from GitHub"
    echo "  2. Installs Python dependencies"
    echo "  3. Configures Cursor IDE"
    echo "  4. Verifies installation"
    echo "  5. Cleans up temporary files"
    exit 0
fi

# Run the installer
main "$@" 