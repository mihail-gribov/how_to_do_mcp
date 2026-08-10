---
name: check-test
description: Checks a specific test: runs it, analyzes the result and provides a report
---

<!-- Generated from how_to_do.json by scripts/generate_skills.py. Edit how_to_do.json, not this file. -->

# check-test

The user's request supplies the following values:

- `test_name` (required) - Name of the specific test to check (e.g.: test_complex_type_annotations)

Placeholders such as `{test_name}` below refer to these values.

## Procedure

Check the test {test_name}.

If the test doesn't run or is not found, try looking for tests with names test_{test_name} or {test_name}_test. If this doesn't help, analyze the situation and explain why this is happening.

* If the test fails, determine the cause:
  * Incorrectly written code
  * Incorrectly written test

* Actions:
  * If the problem is in the code — analyze it, suggest a fix, assess risks and form a report
  * If the problem is in the test — fix it and form a report
