# Extending Claude Essentials for Your Projects

The `ce` plugin provides generic development patterns. Real projects need project-specific context. This guide shows how to wrap and extend `ce` for your codebase.

## The Extension Pattern

The `ce` plugin is intentionally generic. Your project's `.claude/` directory should:

1. **Reference ce skills** in your rules (don't duplicate them)
2. **Add project commands** that wrap your actual tooling
3. **Create project skills** for domain-specific knowledge
4. **Configure hooks** to enforce project conventions

## Directory Structure

```
your-project/
└── .claude/
    ├── CLAUDE.md              # Project overview, architecture, quick commands
    ├── settings.json          # Permissions, hooks, environment
    ├── commands/              # Project-specific slash commands
    │   ├── myproject:test.md
    │   ├── myproject:dev.md
    │   └── myproject:deploy.md
    ├── skills/                # Domain knowledge
    │   └── myproject-models/
    │       └── SKILL.md
    ├── rules/                 # Auto-injected context by file path
    │   ├── testing.md
    │   └── backend/
    │       └── api.md
    └── hooks/                 # Pre/post tool scripts
        └── lint.sh
```

## 1. Project CLAUDE.md

Keep this focused on what Claude needs to work in your codebase:

````markdown
# MyProject

Brief description of what the project does.

## Architecture

High-level structure. What lives where.

## Quick Commands

```bash
make dev          # Start development
make test         # Run tests
make lint         # Lint and format
```

## Key Patterns

Project-specific conventions Claude should follow.
````

## 2. Referencing ce Skills in Rules

Rules auto-inject based on file paths. Reference ce skills instead of duplicating content:

````markdown
---
paths:
  - "**/*.test.ts"
  - "**/test_*.py"
---

# Testing Rules

When writing tests, load the ce:writing-tests skill for general patterns.

## Project-Specific Patterns

| Area    | HTTP Mocking | Notes                    |
| ------- | ------------ | ------------------------ |
| Python  | `respx`      | Must match exact URL     |
| Frontend| `msw`        | Handlers in tests/mocks/ |

## Async Waiting

When fixing flaky tests, see async waiting patterns in ce:writing-tests.
````

This keeps rules lightweight while connecting to the deeper ce knowledge.

## 3. Project Commands

Create commands that wrap your actual workflows. Namespace them to avoid conflicts:

````markdown
---
description: Run tests on remote machine
argument-hint: [target]
---

Run tests using the remote runner (preferred over local).

```bash
rr test              # All tests
rr test-backend      # Backend only
rr test -x           # Stop on first failure
```

For advanced usage, load the rr:rr skill.
````

> *[rr](https://github.com/rileyhilliard/rr) is a distributed testing CLI for load balancing tests across multiple worker machines*

Commands should be thin wrappers that show:
- What to run
- Common variations
- Where to find more info (skills)

## 4. Project Skills

Create skills for domain knowledge that doesn't fit in rules:

````markdown
---
name: myproject-models
description: Data model patterns for MyProject. Use when creating new models, modifying schemas, or understanding relationships.
---

# Model Development

## Hierarchy

1. **Base models** - Shared fields, timestamps
2. **Domain models** - Business logic
3. **View models** - Query-time transforms

## Creating a New Model

Location: `src/models/{domain}.py`

```python
from myproject.models.base import BaseModel

class Widget(BaseModel):
    """Document the business purpose."""

    name: str
    status: WidgetStatus
```

## Key Files

- `src/models/base.py` - Base classes
- `src/schemas/` - Pydantic schemas
````

## 5. Rules Organization

Organize rules by scope. More specific paths take precedence:

```
rules/
├── testing.md           # All test files
├── error-handling.md    # Global error patterns
├── frontend/
│   ├── testing.md       # Frontend-specific test patterns
│   └── components.md    # React component patterns
└── backend/
    ├── api.md           # API endpoint patterns
    └── testing.md       # Backend test patterns
```

Each rule file uses path matching:

```markdown
---
paths:
  - frontend/**/*.tsx
  - frontend/**/*.ts
---

# Frontend Rules

React patterns for this project...
```

## Complete Example

Here's how a real project combines everything:

**`.claude/rules/testing.md`** - References ce skills:
```markdown
---
paths:
  - "**/*.test.*"
  - "**/test_*.py"
---

# Testing

Load ce:writing-tests for Testing Trophy patterns.
See async waiting patterns in ce:writing-tests for test timing fixes.

## Project Specifics

- Python: Use `respx` for HTTP mocking
- Frontend: Use `msw` with handlers in `tests/mocks/`
- Always run tests via `make test-remote`
```

**`.claude/commands/myproject:test.md`** - Wraps tooling:
````markdown
---
description: Run project tests
argument-hint: [area]
---

```bash
rr test                      # All tests
rr test-backend              # Backend only
rr test-backend ARGS="-x"    # Stop on first failure
```
````

**`.claude/skills/myproject-api/SKILL.md`** - Domain knowledge:
```markdown
---
name: myproject-api
description: API development patterns. Use when creating endpoints, handling auth, or designing responses.
---

# API Development

## Route Structure

All routes in `src/api/routes/`. Thin handlers that delegate to services...
```

## Key Principles

1. **Don't duplicate ce content** - Reference skills, don't copy them
2. **Keep commands thin** - Show what to run, link to skills for details
3. **Scope rules narrowly** - More specific paths = more relevant context
4. **Use hooks for enforcement** - Block bad patterns, auto-fix on stop
5. **Document the "why"** - Project CLAUDE.md explains architecture decisions
