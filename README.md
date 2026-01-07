# DBNT - Do Better Next Time

Universal learning protocol for AI systems. Not anger-driven. Signal-driven.

## What It Is

DBNT is a behavioral encoding system that helps AI systems learn from both failures AND successes across sessions.

```
DBNT = Do Better Next Time (encode failures)
DBGT = Do Better... Got It (encode successes)
```

## The Problem

Most AI systems:
- Have no cross-session learning
- Or only learn from negative feedback (errors, corrections)
- Result: 65%+ learning dissonance - systems that know what NOT to do but can't replicate success

## The Solution

DBNT provides:
- **Signal detection** - Recognize positive/negative feedback without requiring anger
- **Weighted encoding** - Success signals weight 1.5x over failure (inverted from typical)
- **Persistent rules** - Learnings survive context clears, session boundaries, model updates
- **Dissonance monitoring** - Track the balance between success/failure encoding

## Core Insight

> Failure tells you ONE path to avoid (from infinite bad paths).
> Success tells you ONE path that WORKS (from few good paths).
> Success is more information-dense than failure.

The Ralph Wiggum Problem: knowing 100 ways to fail doesn't teach you how to succeed.

## Installation

```bash
# Claude Code
dbnt install --adapter claude-code

# Generic (any system)
dbnt install --adapter generic
```

## Usage

### Signal Detection (No Yelling Required)

```python
from dbnt import detect_signal

# These all work - no anger needed
detect_signal("that's not quite right")     # → NEGATIVE (mild)
detect_signal("hmm, try again")             # → NEGATIVE (mild)
detect_signal("perfect")                     # → POSITIVE (strong)
detect_signal("that works")                  # → POSITIVE (moderate)
```

### Manual Encoding

```python
from dbnt import encode_success, encode_failure

# After something works
encode_success(
    category="code-pattern",
    pattern="Used dataclass for config objects",
    context="User approved the implementation"
)

# After something fails
encode_failure(
    category="protocol",
    pattern="Used npm instead of pnpm",
    context="Project requires pnpm"
)
```

### Dissonance Check

```python
from dbnt import check_dissonance

result = check_dissonance()
# {
#     "score": 0.15,
#     "status": "balanced",
#     "success_rules": 12,
#     "failure_rules": 8,
#     "recommendation": None
# }
```

## Adapters

| Adapter | Status | Description |
|---------|--------|-------------|
| `claude-code` | ✅ | Hooks into Claude Code's hook system |
| `cursor` | 🚧 | Cursor IDE rules integration |
| `langchain` | 🚧 | LangChain callback integration |
| `generic` | ✅ | File-based, works anywhere |

## Architecture

```
┌─────────────────────────────────────────────────┐
│                    DBNT Core                     │
├─────────────────────────────────────────────────┤
│  Signal Detector  │  Rule Encoder  │  Dissonance │
│    (NLP-based)    │   (weighted)   │  Calculator │
└─────────────────────────────────────────────────┘
           │                │               │
           ▼                ▼               ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Claude Code  │  │    Cursor    │  │   Generic    │
│   Adapter    │  │   Adapter    │  │   Adapter    │
└──────────────┘  └──────────────┘  └──────────────┘
           │                │               │
           ▼                ▼               ▼
     ~/.claude/        .cursorrules      ./dbnt/
       rules/                             rules/
```

## Signal Strength

| Signal | Type | Strength | Action |
|--------|------|----------|--------|
| "perfect", "exactly right", "ship it" | Positive | STRONG | Create success rule |
| "great", "nice", "thanks" | Positive | MODERATE | Log for review |
| "that's wrong", "no", "fix this" | Negative | STRONG | Create failure rule |
| "hmm", "not quite", "try again" | Negative | MODERATE | Log for review |
| "ok", "sure" | Neutral | WEAK | No action |

## Encoding Weights

```
Success signals: 1.5x weight
Failure signals: 1.0x weight

Target ratio: 60% success rules, 40% failure rules
```

## Why 1.5x for Success?

Traditional ML minimizes loss (avoid bad outcomes). But human expertise works differently:

- Experts study successful cases
- Medical training: study healthy patients, not just diseased
- Sports: watch film of good plays, not just mistakes
- Music: practice what sounds good

DBNT-dominant learning mirrors human expertise acquisition.

## Configuration

```yaml
# dbnt.yaml
version: 1

signals:
  positive:
    strong: ["perfect", "exactly", "ship it", "nailed it"]
    moderate: ["great", "nice", "thanks", "good"]
  negative:
    strong: ["wrong", "no", "fix", "broken"]
    moderate: ["hmm", "not quite", "try again"]

weights:
  success: 1.5
  failure: 1.0

targets:
  success_ratio: 0.60
  max_dissonance: 0.20

storage:
  adapter: claude-code  # or: cursor, generic
  path: ~/.dbnt/rules/
```

## License

MIT

## Related

- [Tesseract](../tesseract) - Hierarchical knowledge compression
- [Claude Code](https://claude.com/claude-code) - AI coding assistant
- [Gas Town](https://steve-yegge.medium.com) - Inspiration for agent swarms
