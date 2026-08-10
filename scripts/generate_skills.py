#!/usr/bin/env python3
"""Generate the skills/ tree from how_to_do.json.

how_to_do.json is the single source of truth for the procedures. The MCP server
serves them over the protocol; this script renders the same procedures as skill
files, so an agent that loads skills directly needs no server at all.

Run from the repository root:

    python3 scripts/generate_skills.py

Use --check to verify that the committed skills match how_to_do.json (used by the
test suite).
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "how_to_do.json"
SKILLS_DIR = ROOT / "skills"

# Commands that only make sense inside the MCP server: an agent that loads skills
# already sees the list of available skills natively.
SERVER_ONLY = {"how_to_do_list", "info_command"}

HEADER = (
    "<!-- Generated from how_to_do.json by scripts/generate_skills.py. "
    "Edit how_to_do.json, not this file. -->"
)


def skill_name(command: str) -> str:
    return command.replace("_", "-")


def argument_section(schema: dict) -> str:
    properties = schema.get("properties") or {}
    if not properties:
        return "This skill takes no arguments.\n\n"

    required = set(schema.get("required") or [])
    lines = ["The user's request supplies the following values:", ""]
    for name, spec in properties.items():
        marker = "required" if name in required else "optional"
        description = spec.get("description", "").strip()
        lines.append(f"- `{name}` ({marker}) - {description}")
    lines.append("")
    lines.append(
        "Placeholders such as `{" + next(iter(properties)) + "}` below refer to these values."
    )
    lines.append("")
    lines.append("")
    return "\n".join(lines)


def render(command: str, spec: dict) -> str:
    description = spec.get("description", "").strip()
    prompt = spec.get("prompt", "").strip()
    schema = spec.get("inputSchema") or {}

    return (
        "---\n"
        f"name: {skill_name(command)}\n"
        f"description: {description}\n"
        "---\n\n"
        f"{HEADER}\n\n"
        f"# {skill_name(command)}\n\n"
        f"{argument_section(schema)}"
        "## Procedure\n\n"
        f"{prompt}\n"
    )


def build() -> dict:
    tools = json.loads(CONFIG.read_text(encoding="utf-8"))["tools"]
    return {
        command: render(command, spec)
        for command, spec in tools.items()
        if command not in SERVER_ONLY
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the committed skills match how_to_do.json instead of writing them",
    )
    args = parser.parse_args()

    wanted = build()
    stale = []

    for command, content in wanted.items():
        path = SKILLS_DIR / skill_name(command) / "SKILL.md"
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if current == content:
            continue
        if args.check:
            stale.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            print(f"wrote {path.relative_to(ROOT)}")

    expected_dirs = {skill_name(command) for command in wanted}
    if SKILLS_DIR.exists():
        for child in SKILLS_DIR.iterdir():
            if child.is_dir() and child.name not in expected_dirs:
                message = f"{child.relative_to(ROOT)} has no matching command"
                if args.check:
                    stale.append(message)
                else:
                    print(f"warning: {message}")

    if args.check:
        if stale:
            print("skills are out of date with how_to_do.json:")
            for item in stale:
                print(f"  {item}")
            print("run: python3 scripts/generate_skills.py")
            return 1
        print(f"skills are in sync with how_to_do.json ({len(wanted)} skills)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
