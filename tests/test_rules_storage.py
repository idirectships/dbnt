"""Tests for rule file storage."""

import tempfile
from pathlib import Path

from dbnt.core import Category, RuleType
from dbnt.storage.rules import load_rules_from_dir, parse_rule_file


class TestParseRuleFile:
    """Test markdown rule file parsing."""

    def test_parse_failure_rule(self):
        d = Path(tempfile.mkdtemp())
        rule_file = d / "rule_never_push_main.md"
        rule_file.write_text("""# Rule: Never Push to Main

**ID:** rule_never_push_main
**Source:** feedback:db (2026-03-08)
**Created:** 2026-03-08
**Confidence:** high
**Applied:** 0

## Trigger
Any git push operation targeting main or master.

## Action
Always use feature branches and PRs.

## Evidence
- 2026-03-08: Pushed directly to main, broke CI.
""")
        rule = parse_rule_file(rule_file)
        assert rule is not None
        assert rule.type == RuleType.FAILURE

    def test_parse_success_rule(self):
        d = Path(tempfile.mkdtemp()) / "successes"
        d.mkdir()
        rule_file = d / "code-dataclass_pattern.md"
        rule_file.write_text("""# Success: Used dataclass for config

**Category**: code
**Weight**: 1.5
**Created**: 2026-03-10

## Context
Clean and typed configuration.

## Pattern
Use dataclasses for configuration objects instead of dicts.
""")
        rule = parse_rule_file(rule_file)
        assert rule is not None
        assert rule.type == RuleType.SUCCESS
        assert rule.category == Category.CODE

    def test_load_directory(self):
        d = Path(tempfile.mkdtemp()) / "failures"
        d.mkdir()
        (d / "rule_a.md").write_text("# Failure: A\n\n## Pattern\nDon't do A.")
        (d / "rule_b.md").write_text("# Failure: B\n\n## Pattern\nDon't do B.")

        rules = load_rules_from_dir(d)
        assert len(rules) == 2

    def test_empty_directory(self):
        d = Path(tempfile.mkdtemp())
        rules = load_rules_from_dir(d)
        assert rules == []

    def test_nonexistent_directory(self):
        rules = load_rules_from_dir(Path("/nonexistent"))
        assert rules == []
