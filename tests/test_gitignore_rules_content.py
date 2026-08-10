"""Tests for the shipped gitignore rule set and how it is applied."""

import subprocess
import sys
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import how_to_do  # noqa: E402

RULES = tomllib.loads((ROOT / "how_to_do_gitignore.toml").read_text(encoding="utf-8"))


def patterns_of(category):
    return RULES.get(category, {}).get("patterns", [])


def every_pattern():
    for category in RULES:
        for pattern in patterns_of(category):
            yield category, pattern


class TestShippedRules(unittest.TestCase):
    """The rule set must not exclude things that belong in version control"""

    def test_secrets_category_exists(self):
        self.assertIn("Secrets", RULES)
        for pattern in (".env", "*.pem", "*.key", "id_rsa", "credentials.json"):
            self.assertIn(pattern, patterns_of("Secrets"), f"{pattern} must be ignored")

    def test_env_example_files_stay_tracked(self):
        for pattern in ("!.env.example", "!.env.sample", "!.env.template"):
            self.assertIn(pattern, patterns_of("Secrets"))

    def test_ci_configuration_is_not_ignored(self):
        # Ignoring these would silently drop the CI setup from the repository
        forbidden = {".github/", ".gitlab-ci.yml", "Jenkinsfile", ".circleci/", ".dockerignore"}
        for category, pattern in every_pattern():
            self.assertNotIn(pattern, forbidden, f"{category} must not ignore {pattern}")

    def test_no_blanket_yaml_or_config_globs(self):
        # "*.yml" would remove every workflow, compose file and k8s manifest
        forbidden = {"*.yml", "*.yaml", "*.json", "*.toml", "*.md"}
        for category, pattern in every_pattern():
            self.assertNotIn(pattern, forbidden, f"{category} must not ignore {pattern}")

    def test_lock_files_stay_tracked(self):
        forbidden = {"package-lock.json", "yarn.lock", "poetry.lock", "Pipfile.lock", "uv.lock"}
        for category, pattern in every_pattern():
            self.assertNotIn(pattern, forbidden, f"{category} must not ignore {pattern}")


class TestAlwaysInclude(unittest.TestCase):
    """Secrets are emitted whether or not such a file exists yet"""

    def setUp(self):
        self._original = how_to_do.load_gitignore_rules
        how_to_do.load_gitignore_rules = lambda: {
            "Secrets": [".env", "*.pem"],
            "Python": ["__pycache__/"],
        }

    def tearDown(self):
        how_to_do.load_gitignore_rules = self._original

    def test_secrets_emitted_for_a_project_without_secrets(self, ):
        import tempfile

        with tempfile.TemporaryDirectory() as project:
            (Path(project) / "main.py").write_text("print('hi')\n", encoding="utf-8")

            result = how_to_do.analyze_project_for_gitignore(project)

            self.assertIn("Secrets", result)
            self.assertEqual(result["Secrets"], [".env", "*.pem"])
            # Python rules are still conditional: nothing here matches __pycache__/
            self.assertNotIn("Python", result)

    def test_conditional_categories_still_match(self):
        import tempfile

        with tempfile.TemporaryDirectory() as project:
            (Path(project) / "__pycache__").mkdir()

            result = how_to_do.analyze_project_for_gitignore(project)

            self.assertIn("Python", result)
            self.assertIn("Secrets", result)


class TestSkillsInSync(unittest.TestCase):
    """skills/ is generated from how_to_do.json and must not drift"""

    def test_generated_skills_match_config(self):
        result = subprocess.run(
            [sys.executable, "scripts/generate_skills.py", "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
