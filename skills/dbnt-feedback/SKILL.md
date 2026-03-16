---
name: dbnt-feedback
description: "Create DBNT success/failure rule artifacts. Auto-fires on DB/DBN/DBNM/DBYC feedback commands. Also triggers on: 'save this as a rule', 'make this a rule', 'encode this lesson', 'write a failure artifact', 'capture this pattern'."
allowed-tools: [Write, Read, Bash]
---

# DBNT Feedback — Rule Artifact Creation

Create artifacts to encode patterns after feedback. DBNT (Do Better Next Time) is a universal feedback protocol for AI agents.

## Usage

```
/dbnt-feedback success "pattern-name"
/dbnt-feedback failure "pattern-name"
```

## Success Artifact Template

Location: `$HOME/.dbnt/rules/successes/[pattern-name].md`

```markdown
# Success: [Pattern Name]

**Context**: [What was happening when this worked]
**Pattern**: [The correct approach]
**Source**: [Session date YYYY-MM-DD]

## When to Apply
[Conditions that trigger this pattern]

## The Pattern
[Specific behavior to repeat]
```

## Failure Artifact Template (DBYC only)

Location: `$HOME/.dbnt/rules/failures/[pattern-name].md`

```markdown
# Failure: [What Went Wrong]

**Severity**: CRITICAL
**Context**: [What was happening]
**Mistake**: [What you did wrong]
**Correction**: [What user had to teach you]
**Source**: [Session date YYYY-MM-DD]

## Never Again
[Specific behavior to avoid - burn this into memory]
```

## Weight

- Success from DB: 1x (standard)
- Success from DBYC: 2x (critical — encode both failure AND success)
- Failure from DBYC: 2x (critical)
- Success signals weight 1.5x over failure (success is more information-dense)

## Signal Detection

DBNT classifies natural language feedback automatically:
- "that's not quite right" → NEGATIVE (mild)
- "perfect", "ship it" → POSITIVE (strong)
- "ok", "sure" → Neutral (no action)

## Protocol Commands

| Command | Points | Action |
|---------|--------|--------|
| `db` | -1 | Fix + encode success pattern |
| `dbn` | -1 | Fix faster + encode |
| `dbnm` | -1 | Fix + encode + move on |
| `dbyc` | -2 | Encode BOTH failure AND success |
| `good`/`fixed`/`ship it` | +3 | Acknowledge (1.5x weighted) |
| `tweak`/`almost` | +0.5 → -1 | Degrades on repetition |

Required response to any correction: **"Yes Chef!"** — then fix, encode, continue.
