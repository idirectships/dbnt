# Contributing to DBNT

Thanks for your interest in making AI systems learn better.

## Development Setup

```bash
git clone https://github.com/idirectships/dbnt
cd dbnt
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

## Running Tests

```bash
pytest
pytest --cov=dbnt  # with coverage
```

## Code Style

We use ruff for linting and formatting:

```bash
ruff check src tests
ruff format src tests
```

## Adding an Adapter

1. Create `src/dbnt/adapters/your_adapter.py`
2. Extend `BaseAdapter`
3. Register in `pyproject.toml` entry points
4. Add tests in `tests/test_adapters/`

Example adapter skeleton:

```python
from dbnt.adapters.base import BaseAdapter

class YourAdapter(BaseAdapter):
    def install(self) -> None:
        """Install DBNT hooks/integration."""
        pass

    def uninstall(self) -> None:
        """Remove DBNT from system."""
        pass

    def get_rules_path(self) -> Path:
        """Where rules are stored."""
        pass

    def sync_rule(self, rule: Rule) -> None:
        """Convert and save rule in system's format."""
        pass

    def is_installed(self) -> bool:
        """Check if DBNT is active."""
        pass
```

## Adding Signal Patterns

Edit `src/dbnt/signals/detector.py`:

- `POSITIVE_STRONG` - Triggers success rule creation
- `POSITIVE_MODERATE` - Logs for review
- `NEGATIVE_STRONG` - Triggers failure rule creation
- `NEGATIVE_MODERATE` - Logs for review

Patterns are regex. Keep them language-agnostic when possible.

## Philosophy

1. **Success > Failure** - Weight success signals 1.5x
2. **No anger required** - Mild feedback should work
3. **Portable** - Adapters make it work anywhere
4. **Measurable** - Dissonance gives a number to track

## Pull Requests

1. Fork and branch from `main`
2. Add tests for new features
3. Run `ruff check` and `pytest`
4. Keep commits atomic
5. Describe the "why" in your PR

## Questions?

Open an issue or reach out.
