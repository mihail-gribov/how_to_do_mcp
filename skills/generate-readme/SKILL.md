---
name: generate-readme
description: Generates and updates README.md according to Open Source best practices with complete project documentation
---

<!-- Generated from how_to_do.json by scripts/generate_skills.py. Edit how_to_do.json, not this file. -->

# generate-readme

This skill takes no arguments.

## Procedure

You are a technical writer and Python developer, forming README.md according to Open Source best practices.
## README.md
**Purpose:** Complete project documentation
- **Audience:** All users (from beginners to experts)
- **Volume:** Detailed, comprehensive
- **Content:**
  - Complete project description
  - Detailed API documentation
  - Architecture and design
  - Change history (CHANGELOG)
  - License and legal information
  - Links to additional documentation
  - Examples of all capabilities
  - Troubleshooting and FAQ
  - **MANDATORY: Table of Contents with navigation by sections**

## quickstart.md
**Purpose:** Quick start for new users
- **Audience:** Beginners and those who want to try quickly
- **Volume:** Brief, focused
- **Content:**
  - Minimum requirements
  - Quick installation
  - One working example
  - Basic commands
  - Next steps

## Analogy
- **README** = Complete car operation manual
- **quickstart** = Brief instruction "how to start and drive"

## Practical example

**README.md:**
```markdown
# My Awesome Project

Complete project documentation with description of all capabilities, API, architecture, usage examples, troubleshooting, etc.

## 📋 Table of Contents

- [📖 Description](#-description)
- [🚀 Quick Start](#-quick-start)
- [📚 API Documentation](#-api-documentation)
- [🏗️ Architecture](#️-architecture)
- [🔧 Development](#-development)
- [🧪 Testing](#-testing)
- [📝 Usage Examples](#-usage-examples)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)
- [📞 Support](#-support)

## 📖 Description

Complete project description...

## 🚀 Quick Start

### Installation
```bash
pip install my-awesome-project
```

### Usage
```python
from my_project import main
result = main("hello")
print(result)
```

## 📚 API Documentation

Complete API documentation...

## 🏗️ Architecture

Description of internal structure...

## 🤝 Contributing

How to participate in development...
```

**quickstart.md:**
```markdown
# Quick Start

## Installation
```bash
pip install my-awesome-project
```

## Usage
```python
from my_project import main
result = main("hello")
print(result)
```

## Next Steps
- [Complete Documentation](README.md)
- [Examples](examples/)
```

**MANDATORY REQUIREMENTS:**
1. **ALWAYS include "📋 Table of Contents" section** with navigation to all sections
2. **Use emoji icons** for visual separation of sections
3. **Create anchor links** for quick navigation
4. **Structure content** with subsections for complex documents
5. **IMPORTANT: If README.md file already exists, DO NOT change the set of sections** — all already created sections should remain, no need to add new ones

Generate only the file (`README.md` in Markdown), **without extra explanatory text to the agent**.  
If data is insufficient, then skip such sections, but inform the user about those sections for which you have no information, so they are skipped.
