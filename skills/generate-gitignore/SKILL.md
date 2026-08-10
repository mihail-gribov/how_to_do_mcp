---
name: generate-gitignore
description: Creates and updates .gitignore file based on project structure analysis and rules from how_to_do_gitignore.toml
---

<!-- Generated from how_to_do.json by scripts/generate_skills.py. Edit how_to_do.json, not this file. -->

# generate-gitignore

The user's request supplies the following values:

- `project_path` (required) - Path to the project for which .gitignore file needs to be generated

Placeholders such as `{project_path}` below refer to these values.

## Procedure

Create .gitignore file ONLY with provided rules

**PROJECT INFORMATION:**
- Project path: {project_path}
- .gitignore file path: {gitignore_path}

**RULES FOR USE (STRICTLY ONLY THESE):**
{rules_by_category}

**Statistics:**
- Total rules: {total_rules}
- Categories: {categories_count}

**CRITICALLY IMPORTANT:**
1. Use ONLY rules from the list above
2. DO NOT add any additional rules
3. DO NOT add general rules like *.log, *.tmp, *.bak, etc.
4. DO NOT add rules for OS, IDE or other categories
5. Create .gitignore file in project root
6. Group rules by categories with comments
7. Add empty lines between categories

**Output format:**
```
# Category
rule1
rule2

# Another category
rule3
```

**Result:** Created .gitignore file ONLY with provided rules. Report: which categories were created and how many rules in each.

**REPORT:**
- Project scanned: {project_path}
- .gitignore file created: {gitignore_path}
- Total rules applied: {total_rules}
- Categories used: {categories_count}
