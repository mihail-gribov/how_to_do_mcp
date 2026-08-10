---
name: check-all-tests
description: Checks all project tests: runs the full test suite and analyzes results
---

<!-- Generated from how_to_do.json by scripts/generate_skills.py. Edit how_to_do.json, not this file. -->

# check-all-tests

This skill takes no arguments.

## Procedure

ACTIONS:
1. Run pytest command in terminal with -v flags for verbose output
2. Collect test execution results
3. Analyze the results

RESULT ANALYSIS:
- If tests didn't start: explain the reason and suggest a solution
- If there are failed tests: for each failed test:
  * Describe what the test checks
  * Explain the cause of failure (error in test or in code)
  * Suggest how to fix it
- If all tests passed: confirm success

REPORT FORMAT:
* Brief summary (X passed, Y failed)
* Detailed analysis of failed tests (if any)
* Plan for fixing problems
* Save full report to test_report.txt file

EXECUTE: Run tests and provide analysis according to the instructions above.
