#!/usr/bin/env python3
"""Print the gitignore rules that apply to a project.

The rules come from how_to_do_gitignore.toml merged with the user's own file, and
are filtered down to the patterns that actually match something in the project.

This is the same analysis the MCP server performs, exposed as a plain command so
the generate-gitignore skill works without a server:

    python3 scripts/gitignore_rules.py [project_path] [--json]
"""

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from how_to_do import analyze_project_for_gitignore  # noqa: E402
from installer import get_category_description  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "project_path",
        nargs="?",
        default=os.getcwd(),
        help="project to analyse (default: current directory)",
    )
    parser.add_argument("--json", action="store_true", help="emit JSON instead of text")
    args = parser.parse_args()

    project_path = os.path.abspath(args.project_path)
    if not os.path.isdir(project_path):
        print(f"error: {project_path} is not a directory", file=sys.stderr)
        return 1

    rules_by_category = analyze_project_for_gitignore(project_path)
    if not rules_by_category:
        print(f"No matching rules found for {project_path}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(rules_by_category, indent=2))
        return 0

    print(f"# Rules matching {project_path}")
    for category, patterns in rules_by_category.items():
        print(f"\n## {category} - {get_category_description(category)}")
        for pattern in patterns:
            print(f"  {pattern}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
