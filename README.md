## HOW TO DO — Enhanced Control Over Cursor AI Agent

Cursor is a powerful AI-powered development environment, but sometimes its agent can be overly proactive: it writes excessive explanations, unexpectedly starts coding, or edits more files than necessary.

The **HOW TO DO** extension allows you to control Cursor's AI agent more precisely by linking short commands with detailed prompts that clearly define what the agent should accomplish.

### Key Benefits:

* 🔹 **Precise Instructions:** Clearly specify what the agent should do (e.g., "check tests", "create .gitignore", "only analyze function").
* 🔹 **Predictable Actions:** Reduce the likelihood of unexpected edits and make the agent's behavior more stable.
* 🔹 **AI Workflow Optimization:** Reduce token usage through concise and clear instructions, lowering costs and improving performance.

Using **HOW TO DO**, you can work with Cursor more efficiently and avoid unwanted surprises in your code.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/Protocol-MCP-orange.svg)](https://modelcontextprotocol.io)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)](https://github.com/mihail-gribov/how_to_do)

## 📋 Table of Contents

- [🎯 What HOW TO DO Solves](#-what-how-to-do-solves)
- [⚙️ How It Works](#️-how-it-works)
- [🚀 Quick Start](#-quick-start)
- [📚 Available Commands](#-available-commands)
- [🔧 Customization](#-customization)
- [📊 Resource Optimization](#-resource-optimization)
- [📄 License](#-license)

## 🎯 What HOW TO DO Solves

**Problem:** Interaction with Cursor's AI agent isn't always convenient and predictable:

* The agent produces too much text instead of specific actions
* It unpredictably edits code when only analysis or verification is needed
* It modifies multiple files instead of making minimal changes
* It doesn't always correctly understand what's required for a specific task

**Solution:** Short commands linked to detailed prompt instructions:

* You get concise responses focused strictly on the task
* The agent clearly understands what action to perform (analysis, fixing, generation, etc.)
* The agent only modifies code where it's truly necessary
* You reduce token costs through clear and specific prompts

**Additional Benefits:**

* Easy expansion: simple to create new commands for your tasks
* Improved agent interaction quality with regular use
* Ability to standardize and reuse effective prompt-commands

## ⚙️ How It Works

**HOW TO DO** allows developers to map short commands to custom prompts.

**Problem:** Writing long prompts for repetitive operations every time
```
You: "Check test test_validation, find the failure reason, suggest a fix, but don't modify code without permission, provide a structured report..."
```

**Solution:** Describe the prompt once and use a short command
```
You: check_test test_validation
# or
You: check test test_validation
```

**How it works:**
1. **You create a command** — short name for the task
2. **Configure the prompt** — precise instructions for AI (once)
3. **Define parameters** — what can be passed to the command
4. **Use it** — the agent automatically pulls the prompt for the specified command

**Customization example:**
```json
{
  "check_test": {
    "description": "Checks a specific test",
    "prompt": "Check test {test_name}. If the test fails, identify the cause and suggest a fix. DO NOT modify code without permission.",
    "parameters": {
      "test_name": "Test name to check"
    }
  }
}
```

**Result:** Instead of verbose explanations, AI receives clear instructions and provides structured responses without unexpected changes. The agent automatically uses your prompt when the command is called.

## 🚀 Quick Start

### Requirements

- Python 3.8+
- Cursor IDE with MCP support

### Installing the MCP Server

#### Automatic Installation (Recommended)

Run the installation script:

```bash
curl -fsSL https://raw.githubusercontent.com/mihail-gribov/how_to_do_mcp/main/install.sh | bash
```

**What happens when you run this command:**
1. Script downloads and runs immediately
2. Follows the installation process step by step
3. Shows progress in real-time
4. Handles all setup automatically

The script:
- Downloads the repository from GitHub
- Installs Python dependencies
- Configures Cursor IDE
- Verifies the installation
- Cleans up temporary files

#### Manual Installation

1. **Clone the repository:**
```bash
git clone https://github.com/mihail-gribov/how_to_do_mcp.git
cd how_to_do_mcp
```

2. **Ensure files are in the project root:**
   - `how_to_do.py` - main MCP server
   - `how_to_do.json` - tool configuration

3. **Configure MCP in Cursor:**
   - Open Cursor settings (Ctrl/Cmd + ,)
   - Go to "MCP Servers" section
   - Add new server with **absolute path**: `python3 /home/username/.cursor/tools/how_to_do.py`
   - **Important:** Use absolute path to the script, not relative
   - Save settings

### Cursor Setup

1. **Open Cursor settings:**
   - Windows/Linux: `Ctrl + ,`
   - macOS: `Cmd + ,`

2. **Find the MCP Servers section:**
   - Go to "Extensions" → "MCP Servers"

3. **Add a new server:**
   - Click "Add Server"
   - Enter command: `python3 /home/username/.cursor/tools/how_to_do.py`
   - **Important:** Use absolute path to the script, replace `username` with your actual username
   - Specify working directory (optional)
   - Save settings

4. **Restart Cursor:**
   - Close and reopen Cursor
   - MCP server should appear in the available list

### Installation Verification

After installation, you can verify the server works:

```python
# View all available commands
how_to_do_list
# or
show commands

# Check a specific test
check_test test_function_name
# or
check test test_function_name

# Analyze function performance
analyze_function function_name
# or
analyze function function_name
```

### Explicit Tool Usage

Sometimes Cursor's AI agent may not automatically recognize when to use HOW TO DO tools. In such cases, you can explicitly instruct the agent to use the tool:

**Example:**
```
Use how to do: create .gitignore file
```

**Other examples:**
```
Use how to do: check test test_validation
Use how to do: analyze function process_data
Use how to do: generate readme
Use how to do: type analyze for this function
```

This explicit instruction helps the agent understand that it should use the HOW TO DO MCP server instead of trying to perform the task directly.

## 📚 Available Commands

### Analysis and Testing

#### `check_test`
Checks a specific test, runs it, and provides a detailed report.

**Parameters:**
- `test_name` (required): Test name to check

**Example:**
```python
check_test test_data_processing
# or
check test test_data_processing
```

#### `check_all_tests`
Checks all project tests and analyzes results.

**Capabilities:**
- Complete analysis of all tests in the project
- Report on failed tests with detailed analysis
- Plan for fixing problems with prioritization

**Example:**
```python
check_all_tests
# or
check all tests
```

#### `analyze_function`
Performs comprehensive performance diagnostics of a function.

**Parameters:**
- `func_name` (required): Function name to analyze
- **Tip:** If your cursor is positioned inside a function, the agent can automatically detect the function name from the active window

**Analysis includes:**
- Time complexity (O-notation)
- Memory consumption and leaks
- Identification of bottlenecks
- Optimization suggestions with justifications

**Example:**
```python
analyze_function process_large_dataset
# or
analyze function process_large_dataset
# or simply (when cursor is inside a function):
analyze_function
# or
analyze function
```

#### `type_analyze`
Analyzes Python code typing and suggests improvements.

**Parameters:**
- `code_block` (required): Python code to analyze

**Capabilities:**
- Adding type annotations for parameters and return values
- Identifying typing issues and inconsistencies
- Suggesting TypedDict for dictionaries with fixed keys
- Using Protocol for interfaces (PEP 544)

**Example:**
```python
type_analyze """
def process_data(data, config=None):
    result = []
    for item in data:
        if config and item.get('active'):
            result.append(item['value'])
    return result
"""
# or
analyze types """
def process_data(data, config=None):
    result = []
    for item in data:
        if config and item.get('active'):
            result.append(item['value'])
    return result
"""
```

### Documentation and Setup

#### `generate_readme`
Generates README.md following Open Source best practices.

**Capabilities:**
- Complete project documentation with detailed description
- Structured content with navigation
- Examples of all capabilities usage
- Open Source project best practices

**Example:**
```python
generate_readme
# or
create README
```

#### `generate_gitignore`
Creates and updates .gitignore file based on project structure analysis.

**How it works:**
1. **Scans the project structure** - analyzes all files and directories in your project
2. **Reads source rules** - loads the initial rule set from `for_gitignore.toml`
3. **Filters rules** - keeps only rules that match files/directories actually present in your project
4. **Generates optimized .gitignore** - creates a clean, relevant .gitignore file

**Capabilities:**
- Automatic file structure analysis
- Rule filtering based on actual project content
- Application of rules from for_gitignore.toml
- Creation of optimized .gitignore with only relevant rules

**Customization:**
You can extend the `for_gitignore.toml` file with your own rules to match your specific project needs. The tool will automatically include your custom rules in the filtering process.

**Example:**
```python
generate_gitignore
# or
create gitignore
```

#### `how_to_do_list`
Shows a list of all available commands with descriptions.

**Parameters:**
- `query` (optional): Search query to filter commands

**Example:**
```python
# Show all commands
how_to_do_list
# or
show commands

# Search commands by keyword
how_to_do_list test
# or
show commands test
```

## 🔧 Customization

### Creating Custom Commands

**HOW TO DO** allows you to create commands that precisely match your workflows.

#### Method 1: Direct Configuration Editing

**Command structure:**
```json
{
  "my_command": {
    "description": "Command description",
    "prompt": "Precise instructions for AI",
    "inputSchema": {
      "type": "object",
      "properties": {
        "param1": {
          "type": "string",
          "description": "Parameter description"
        }
      },
      "required": ["param1"]
    }
  }
}
```

**Custom command example:**
```json
{
  "analyze_api": {
    "description": "Analyzes API endpoints",
    "prompt": "Analyze API endpoint {endpoint}. Check documentation, validation, error handling. DO NOT modify code.",
    "inputSchema": {
      "type": "object",
      "properties": {
        "endpoint": {
          "type": "string",
          "description": "API endpoint path"
        }
      },
      "required": ["endpoint"]
    }
  }
}
```

#### Method 2: Through Cursor Agent

The easiest way to create commands is to use Cursor Agent:

1. **Open the configuration file:**
   ```
   Open file how_to_do.json
   ```

2. **Ask the agent to add a command:**
   ```
   Add a new command "analyze_database" with prompt "Analyze database structure {table_name}. Check indexes, relationships, query performance. Provide optimization recommendations."
   ```

3. **The agent will automatically create the structure:**
   ```json
   {
     "analyze_database": {
       "description": "Analyzes database structure",
       "prompt": "Analyze database structure {table_name}. Check indexes, relationships, query performance. Provide optimization recommendations.",
       "inputSchema": {
         "type": "object",
         "properties": {
           "table_name": {
             "type": "string",
             "description": "Table name to analyze"
           }
         },
         "required": ["table_name"]
       }
     }
   }
   ```

**Benefits of customization through agent:**
- No need to know JSON syntax
- Agent automatically creates correct structure
- Can describe commands in natural language
- Fast command creation without studying documentation

### Customization Benefits

- **Commands speak your project's language**
- **Follow your coding conventions**
- **Execute tasks exactly as you expect**
- **Save time on explanations and rework**

## 📊 Resource Optimization

**Standard interaction:**
- Lots of unnecessary text
- Unexpected changes
- Repeated requests for clarifications
- High token consumption

**With HOW TO DO:**
- Structured responses
- Controlled actions
- Accurate results from the first try
- Optimal token usage

### Optimization Examples

**Without HOW TO DO:**
```
Request: "Check test test_validation"
Tokens: ~500 (lots of explanations)
Result: May be unexpected
```

**With HOW TO DO:**
```
Request: check_test test_validation
Tokens: ~150 (structured response)
Result: Predictable
```

## 📄 License

This project is distributed under the MIT license. See the [LICENSE](LICENSE) file for details.

---

**Result:** HOW TO DO transforms chaotic interaction with Cursor Agent into a predictable and efficient workflow where each command delivers exactly the result you expect, without unnecessary changes and explanations. 