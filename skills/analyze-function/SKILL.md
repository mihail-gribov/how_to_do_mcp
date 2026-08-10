---
name: analyze-function
description: Conducts performance diagnostics of a function: analyzes time complexity, memory consumption and suggests optimizations
---

<!-- Generated from how_to_do.json by scripts/generate_skills.py. Edit how_to_do.json, not this file. -->

# analyze-function

The user's request supplies the following values:

- `func_name` (required) - Function name for performance analysis

Placeholders such as `{func_name}` below refer to these values.

## Procedure

Conduct performance diagnostics of function **{func_name}**:

**Do not change the code** — only analysis and recommendations.

**If the function is suspiciously slow (e.g. heavy loops, hacky algorithms):**
1. Conduct analysis:
   - Time complexity (O‑n, O‑n log n…) 
   - Memory consumption (successful case vs bad case)
   - Loops, copying, comprehensions, recursions
2. Suggest profiling (if this turns out to be useful):
   - `cProfile`, `memory-profiler`, `psutil`, `timeit`
   - If profiling is not needed — skip
3. Identify bottlenecks, indicate possible improvements with justifications, risk and benefit assessments

**If the function is well implemented (no obvious bottlenecks):**
- Give status `"OK"` and brief "function looks good, no obvious issues"

**Sometimes you can suggest a quick fix:**  
If an obvious targeted optimization is evident, add it as a **patch line** (with replacement only within this function). 
- Ask the user: *"Allow insertion of this change?"*  
If the user agrees — insert the patch.
Without consent — just suggest the patch in the report
