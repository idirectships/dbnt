"""Claude Code adapter - integrates with Claude Code's hook system."""

import json
from pathlib import Path

from dbnt.adapters.base import BaseAdapter
from dbnt.core import Rule, RuleType


class ClaudeCodeAdapter(BaseAdapter):
    """
    Adapter for Claude Code.

    Integrates DBNT with Claude Code's hook system:
    - Installs signal detection hook (UserPromptSubmit)
    - Syncs rules to ~/.claude/rules/ and ~/.claude/rules/successes/
    - Maintains compatibility with existing rule format
    """

    def __init__(self, claude_dir: Path | None = None):
        self.claude_dir = claude_dir or Path.home() / ".claude"
        self.rules_dir = self.claude_dir / "rules"
        self.successes_dir = self.rules_dir / "successes"
        self.hooks_dir = self.claude_dir / "hooks"
        self.settings_path = self.claude_dir / "settings.json"

    def install(self) -> None:
        """Install DBNT into Claude Code."""
        # Ensure directories exist
        self.successes_dir.mkdir(parents=True, exist_ok=True)
        self.hooks_dir.mkdir(parents=True, exist_ok=True)

        # Install the signal detection hook
        self._install_hook()

        # Update settings.json to register hook
        self._register_hook()

        print(f"DBNT installed to Claude Code at {self.claude_dir}")

    def uninstall(self) -> None:
        """Remove DBNT from Claude Code."""
        hook_path = self.hooks_dir / "dbgt-detector.sh"
        if hook_path.exists():
            hook_path.unlink()

        # Remove hook registration from settings
        self._unregister_hook()

        print("DBNT uninstalled from Claude Code")

    def get_rules_path(self) -> Path:
        """Get Claude Code rules path."""
        return self.rules_dir

    def sync_rule(self, rule: Rule) -> None:
        """
        Sync a rule to Claude Code format.

        Success rules go to ~/.claude/rules/successes/
        Failure rules go to ~/.claude/rules/
        """
        if rule.type == RuleType.SUCCESS:
            path = self.successes_dir / f"{rule.category.value}-{rule.id}.md"
        else:
            path = self.rules_dir / f"{rule.category.value}-{rule.id}.md"

        # Convert to Claude Code rule format
        content = self._to_claude_format(rule)
        path.write_text(content)

    def is_installed(self) -> bool:
        """Check if DBNT hook is installed."""
        hook_path = self.hooks_dir / "dbgt-detector.sh"
        return hook_path.exists()

    def _to_claude_format(self, rule: Rule) -> str:
        """Convert rule to Claude Code markdown format."""
        if rule.type == RuleType.SUCCESS:
            title = f"Success: {rule.pattern[:50]}"
            section = "## Pattern That Worked"
        else:
            title = f"{rule.category.value.title()}: {rule.pattern[:50]}"
            section = "## Pattern to Avoid"

        return f"""# {title}

{rule.context}

{section}

{rule.pattern}

## Source

- Created: {rule.created.strftime("%Y-%m-%d")}
- Session: {rule.source_session or "unknown"}
- Weight: {rule.weight}
"""

    def _install_hook(self) -> None:
        """Install the DBGT signal detection hook."""
        hook_content = """#!/bin/bash
# DBGT Signal Detection Hook
# Installed by DBNT - Do Better Next Time
# Detects positive feedback signals for success encoding

set -e

INPUT=$(cat)
MESSAGE=$(echo "$INPUT" | jq -r '.user_prompt // .prompt // ""' 2>/dev/null || echo "")

# Signal patterns
POSITIVE_STRONG="perfect|exactly what i needed|ship it|love it|that's it|nailed it|thats it"
POSITIVE_MODERATE="great|nice|good job|thanks.*works|yes!|awesome"

if echo "$MESSAGE" | grep -iqE "$POSITIVE_STRONG"; then
    SIGNAL="STRONG"
    MATCH=$(echo "$MESSAGE" | grep -ioE "$POSITIVE_STRONG" | head -1)
elif echo "$MESSAGE" | grep -iqE "$POSITIVE_MODERATE"; then
    SIGNAL="MODERATE"
    MATCH=$(echo "$MESSAGE" | grep -ioE "$POSITIVE_MODERATE" | head -1)
else
    echo '{"result": "continue"}'
    exit 0
fi

# Log for potential encoding
LOG_DIR="$HOME/.dbnt/signals"
mkdir -p "$LOG_DIR"
echo "{\\"timestamp\\": \\"$(date -Iseconds)\\", \\"signal\\": \\"$SIGNAL\\", \\"match\\": \\"$MATCH\\"}" >> "$LOG_DIR/positive.jsonl"

cat << EOF
{
    "result": "continue",
    "message": "DBGT [$SIGNAL]: '$MATCH' - Consider encoding this success pattern"
}
EOF
"""
        hook_path = self.hooks_dir / "dbgt-detector.sh"
        hook_path.write_text(hook_content)
        hook_path.chmod(0o755)

    def _register_hook(self) -> None:
        """Register hook in settings.json."""
        if not self.settings_path.exists():
            settings = {"hooks": {}}
        else:
            settings = json.loads(self.settings_path.read_text())

        if "hooks" not in settings:
            settings["hooks"] = {}

        if "UserPromptSubmit" not in settings["hooks"]:
            settings["hooks"]["UserPromptSubmit"] = []

        # Check if already registered
        hook_cmd = "$HOME/.claude/hooks/dbgt-detector.sh"
        for entry in settings["hooks"]["UserPromptSubmit"]:
            for hook in entry.get("hooks", []):
                if hook.get("command") == hook_cmd:
                    return  # Already registered

        # Add hook at the beginning
        settings["hooks"]["UserPromptSubmit"].insert(
            0, {"hooks": [{"type": "command", "command": hook_cmd}]}
        )

        self.settings_path.write_text(json.dumps(settings, indent=2))

    def _unregister_hook(self) -> None:
        """Remove hook from settings.json."""
        if not self.settings_path.exists():
            return

        settings = json.loads(self.settings_path.read_text())
        if "hooks" not in settings or "UserPromptSubmit" not in settings["hooks"]:
            return

        hook_cmd = "$HOME/.claude/hooks/dbgt-detector.sh"
        settings["hooks"]["UserPromptSubmit"] = [
            entry
            for entry in settings["hooks"]["UserPromptSubmit"]
            if not any(hook.get("command") == hook_cmd for hook in entry.get("hooks", []))
        ]

        self.settings_path.write_text(json.dumps(settings, indent=2))
