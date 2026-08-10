---
name: type-analyze
description: Analyzes Python code typing: adds type annotations, identifies issues and gives recommendations
---

<!-- Generated from how_to_do.json by scripts/generate_skills.py. Edit how_to_do.json, not this file. -->

# type-analyze

The user's request supplies the following values:

- `code_block` (required) - Python code for typing analysis

Placeholders such as `{code_block}` below refer to these values.

## Procedure

Analyze Python code in {code_block}:

1. Add type annotations:
   • function/method parameters
   • return values
2. Find untyped points: variables, parameters, results
3. For dictionaries with fixed keys — suggest TypedDict
4. For interface/structure abstraction — suggest Protocol (PEP 544)
5. If a value accepts multiple types — suggest Union
6. For containers: use Generic (`List[str]`, `Dict[int, Any]`)

Output format:
1. Code with added annotations (minimal, without logic)  
2. List of issues: missing annotations  
3. Recommendations: configure mypy/pyright for strict checking and Ignore‑flags

Logic in code doesn't change — only typing and advice.
