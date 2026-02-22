---
description: Initialize or audit Claude Code configuration for a repository
argument-hint: "[--audit | --force]"
allowed-tools: Bash, Read, Write, Glob, Grep, AskUserQuestion, Skill
---

Initialize or audit `.claude/` configuration for this repository based on detected stack.

**Before generating or auditing any files**, load `Skill(ce:configuring-claude)` for best practices on writing rules, CLAUDE.md, and skills. Load its `references/rules-and-memory.md` reference for rules and CLAUDE.md specifics, and `references/skills.md` if generating project-specific skills.

Arguments:

- `$ARGUMENTS`: Optional flags
  - `--audit`: Only analyze existing config, report improvements
  - `--force`: Overwrite existing files without confirmation

## Mode Detection

1. Check if `.claude/` directory exists
2. If exists AND no `--force`: Run **Audit Mode**
3. If not exists OR `--force`: Run **Fresh Init Mode**

---

## Configuration Best Practices

All generated files (rules, CLAUDE.md, skills) must follow the principles from `ce:configuring-claude`. Key points:

- Rules reference ce:* skills rather than duplicating skill content
- Main files stay concise; split large content into `references/` subdirectories
- References are always one level deep (no nested references)

See the skill and its references for full details on progressive disclosure, token efficiency, and file structure.

---

## Fresh Init Mode

### Step 1: Detect Stack

Check for manifest files in the repository root:

| File | Stack | Test Framework |
|------|-------|----------------|
| `pyproject.toml` or `requirements.txt` | Python | pytest |
| `package.json` | Node.js/TypeScript | vitest, jest |
| `Cargo.toml` | Rust | cargo test |
| `go.mod` | Go | go test |
| `pom.xml` or `build.gradle` | Java/Kotlin | JUnit |
| `Gemfile` | Ruby | RSpec |

For Node.js projects, also check:
- `tsconfig.json` -> TypeScript
- `package.json` dependencies for `react` -> React
- `vite.config.*` -> Vite
- `next.config.*` -> Next.js

For monorepos, check:
- `packages/` or `apps/` directories
- `workspaces` field in package.json
- Multiple manifest files in subdirectories

### Step 2: Read Project Metadata

Extract from detected manifest:
- Project name
- Description
- Scripts/commands (test, lint, build)
- Dependencies (for framework detection)

### Step 3: Build Generation Plan

Based on detected stack, prepare:

**CLAUDE.md** content:
- Project name and description
- Architecture section (if monorepo or multiple directories)
- Quick commands from package scripts
- Prerequisites (detected package managers)

**settings.json** content:
- `_readme` explaining the file
- `permissions.allow` based on stack (see Permission Mappings below)
- `permissions.ask` with safety defaults

**rules/** content:
- Universal rules (always generate)
- Stack-specific rules (based on detection)

### Step 4: Present Plan and Confirm

Show the user what will be created:

**Simple project (minimal structure):**
```
Detected stack: Python + pytest

Will create:
  .claude/
  ├── CLAUDE.md                 # Project overview
  ├── settings.json             # Permissions for: uv, pytest, git
  └── rules/
      ├── testing.md            # -> ce:writing-tests
      ├── error-handling.md     # -> ce:handling-errors
      ├── debugging.md          # -> ce:systematic-debugging
      ├── verification.md       # -> ce:verification-before-completion
      └── python/
          └── testing.md        # pytest patterns
```

**Complex project (with references for progressive disclosure):**
```
Detected stack: TypeScript + React + FastAPI backend

Will create:
  .claude/
  ├── CLAUDE.md                 # Project overview, architecture
  ├── settings.json             # Permissions for: npm, uv, pytest, git
  └── rules/
      ├── testing.md            # -> ce:writing-tests
      ├── error-handling.md     # -> ce:handling-errors
      ├── debugging.md          # -> ce:systematic-debugging
      ├── verification.md       # -> ce:verification-before-completion
      ├── frontend/
      │   ├── testing.md        # vitest + msw patterns
      │   └── react.md          # component patterns
      └── api/
          ├── conventions.md    # API patterns overview
          └── references/       # Detailed docs (loaded on-demand)
              ├── errors.md     # Error response formats
              └── endpoints.md  # Endpoint patterns
```

Use `AskUserQuestion` to confirm before writing files.

### Step 5: Generate Files

Write all files using the templates below.

---

## Audit Mode

### Step 1: Read Existing Configuration

- Read `.claude/CLAUDE.md`
- Read `.claude/settings.json`
- Glob `.claude/rules/**/*.md`

### Step 2: Analyze Against Best Practices

Use `ce:configuring-claude` principles (and its references) as the baseline for what "good" looks like. Check for:

**Missing skill references in rules:**
- Rules should reference ce:* skills for detailed guidance
- Example: testing.md should mention `ce:writing-tests`

**Permission gaps:**
- Compare allowed commands against detected stack
- Check for missing common patterns

**Missing universal rules:**
- testing.md, error-handling.md, debugging.md, verification.md

**Missing stack-specific rules:**
- Python project without python/testing.md
- TypeScript project without frontend/testing.md

**Progressive disclosure violations (per ce:configuring-claude):**
- Files over 500 lines that should be split into references/
- Nested references (references pointing to other references)
- Duplicated content that should reference a ce:* skill instead
- Large inline code examples that should be in references/

### Step 3: Generate Audit Report

```
Audit of .claude/ configuration:

Good:
  + CLAUDE.md exists with project overview
  + settings.json has reasonable permissions
  + Rules properly reference ce:* skills

Suggestions:
  - rules/testing.md: Add reference to ce:writing-tests skill
  - Missing: rules/python/testing.md for detected Python code
  - settings.json: Add "Bash(uv run pytest:*)" to allow list

Progressive disclosure issues:
  - rules/api/endpoints.md: 847 lines, consider splitting into references/
  - rules/frontend/components.md: Duplicates ce:design skill content
  - skills/my-skill/references/nested/deep.md: References should be one level deep

Apply suggestions? [Y/n/select]
```

### Step 4: Apply Fixes (if confirmed)

For each accepted suggestion, make the appropriate edit or create the missing file.

---

## Templates

### CLAUDE.md Template

```markdown
# {project_name}

{description from manifest or "A project using {stack}"}

## Quick Commands

\`\`\`bash
{test_command}    # Run tests
{lint_command}    # Lint code
{build_command}   # Build project
\`\`\`

## Prerequisites

- {package_manager} - Package manager
{additional prerequisites based on stack}
```

### settings.json Template

```json
{
  "_readme": "Claude Code configuration. Machine-specific overrides go in settings.local.json (gitignored).",
  "permissions": {
    "allow": [
      "Skill",
      "WebFetch",
      "WebSearch",
      "Bash(git:*)",
      "Bash(make:*)",
      {stack_specific_permissions}
    ],
    "deny": [
      "Bash(rm -rf /)",
      "Bash(rm -rf ~)",
      "Bash(rm -rf .)",
      "Bash(git push --force)",
      "Bash(git push -f)",
      "Bash(git reset --hard)"
    ]
  }
}
```

### Universal Rule Templates

**rules/testing.md:**
```markdown
---
paths:
  - "**/*.test.*"
  - "**/*.spec.*"
  - "**/test_*.py"
  - "**/tests/**"
---

# Testing Rules

When writing tests, load the ce:writing-tests skill for general patterns.

## Flaky Tests

When fixing flaky tests, load the ce:fixing-flaky-tests skill.

| Symptom | Likely Cause |
|---------|--------------|
| Passes alone, fails in suite | Shared state |
| Random timing failures | Race condition |
```

**rules/error-handling.md:**
```markdown
---
paths:
  - "**/*.ts"
  - "**/*.tsx"
  - "**/*.js"
  - "**/*.py"
  - "**/*.go"
  - "**/*.rs"
---

# Error Handling

When designing error handling, load the ce:handling-errors skill.

Key principles:
- Never swallow errors silently
- Preserve error context when re-throwing
- Log errors once at the appropriate boundary
```

**rules/debugging.md:**
```markdown
---
paths:
  - "**/*"
---

# Debugging

When investigating bugs or unexpected behavior, load the ce:systematic-debugging skill.

Four-phase approach:
1. Reproduce the issue
2. Trace the code path
3. Identify root cause
4. Verify the fix
```

**rules/verification.md:**
```markdown
---
paths:
  - "**/*"
---

# Verification

Before claiming work is complete, load the ce:verification-before-completion skill.

Always verify:
- Tests pass
- Linting passes
- The feature works end-to-end
```

### Stack-Specific Rule Templates

**rules/python/testing.md:**
```markdown
---
paths:
  - "**/test_*.py"
  - "**/*_test.py"
  - "**/tests/**/*.py"
---

# Python Testing

Extends the universal testing rules with Python-specific patterns.

## Commands

\`\`\`bash
{test_command}              # Run all tests
{test_command} -x           # Stop on first failure
{test_command} -k "pattern" # Run matching tests
\`\`\`

## HTTP Mocking

Use `respx` for HTTP mocking:

\`\`\`python
import respx
from httpx import Response

@respx.mock
@pytest.mark.asyncio
async def test_api_call():
    respx.get("https://api.example.com/data").mock(
        return_value=Response(200, json={"key": "value"})
    )
\`\`\`
```

**rules/frontend/testing.md:**
```markdown
---
paths:
  - "**/*.test.ts"
  - "**/*.test.tsx"
  - "**/*.spec.ts"
  - "**/__tests__/**"
---

# Frontend Testing

Extends the universal testing rules with frontend-specific patterns.

## Commands

\`\`\`bash
{test_command}              # Run all tests
{test_command} --watch      # Watch mode
\`\`\`

## HTTP Mocking

Use MSW for API mocking:

\`\`\`typescript
import { http, HttpResponse } from 'msw'

export const handlers = [
  http.get('/api/user', () => {
    return HttpResponse.json({ name: 'Test User' })
  })
]
\`\`\`

## Async Waiting

\`\`\`typescript
await waitFor(() => expect(element).toBeVisible())
// NOT: await sleep(500)
\`\`\`
```

**rules/frontend/react.md:**
```markdown
---
paths:
  - "**/*.tsx"
  - "**/*.jsx"
---

# React Patterns

## Component Structure

- Prefer function components with hooks
- Keep components focused on one responsibility
- Extract custom hooks for reusable logic

## Testing Components

Use Testing Library idioms:

\`\`\`typescript
import { render, screen } from '@testing-library/react'

test('renders greeting', () => {
  render(<Greeting name="World" />)
  expect(screen.getByText('Hello, World!')).toBeInTheDocument()
})
\`\`\`
```

### Rule with References Template (for complex domains)

**rules/api/conventions.md:**
```markdown
---
paths:
  - "**/api/**"
  - "**/routes/**"
---

# API Conventions

When designing APIs, load the ce:architecting-systems skill for general patterns.

## Quick Reference

| Topic | Reference |
|-------|-----------|
| Error responses | [references/errors.md](references/errors.md) |
| Pagination | [references/pagination.md](references/pagination.md) |
| Authentication | [references/auth.md](references/auth.md) |

## Core Patterns

{Brief patterns here, main file stays under 100 lines}
```

**rules/api/references/errors.md:**
```markdown
# API Error Handling

## Contents
- Error response format
- HTTP status codes
- Error codes by domain
- Client-friendly messages

## Error Response Format

\`\`\`json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request",
    "details": [...]
  }
}
\`\`\`

{Detailed patterns, can be longer since loaded on-demand}
```

---

### Project-Specific Skill Template (Optional)

When the project has complex domain patterns (APIs, connectors, data schemas), scaffold a project skill:

**skills/{project}-patterns/SKILL.md:**
```markdown
---
name: {project}-patterns
description: Project-specific patterns for {project}. Use when working with {domain} code or implementing new {features}.
---

# {Project} Development Patterns

## Quick Reference

| Pattern | When to Use | Reference |
|---------|-------------|-----------|
| API endpoints | Adding new routes | [references/api.md](references/api.md) |
| Data models | Changing schemas | [references/models.md](references/models.md) |
| Authentication | Auth-related code | [references/auth.md](references/auth.md) |

## Core Conventions

{Brief conventions here, ~50 lines max}

## Detailed Guides

For specific patterns, read the relevant reference file:
- **API patterns**: See [references/api.md](references/api.md)
- **Data models**: See [references/models.md](references/models.md)
```

**skills/{project}-patterns/references/api.md:**
```markdown
# API Patterns

## Contents
- Endpoint structure
- Request validation
- Response formatting
- Error handling

## Endpoint Structure

{Detailed patterns with code examples}
```

**When to generate project skills:**
- Project has 3+ distinct domains (API, auth, data, etc.)
- Existing codebase has conventions that differ from ce:* skill defaults
- Team has documented patterns that should be enforced

**When NOT to generate:**
- Simple projects where ce:* skills cover all patterns
- Greenfield projects without established conventions
- If it would duplicate ce:* skill content

---

## Permission Mappings

| Stack | Permissions to Add |
|-------|-------------------|
| Python | `Bash(uv:*)`, `Bash(uv run:*)`, `Bash(python:*)`, `Bash(python3:*)`, `Bash(pip:*)` |
| Node.js | `Bash(npm:*)`, `Bash(npx:*)`, `Bash(node:*)` |
| Bun | `Bash(bun:*)`, `Bash(bunx:*)` |
| Yarn | `Bash(yarn:*)` |
| pnpm | `Bash(pnpm:*)`, `Bash(pnpx:*)` |
| Rust | `Bash(cargo:*)`, `Bash(rustc:*)` |
| Go | `Bash(go:*)` |
| Docker | `Bash(docker:*)`, `Bash(docker-compose:*)` |

---

## Examples

| Command | Result |
|---------|--------|
| `/init` on new Python project | Creates .claude/ with Python rules |
| `/init` on existing config | Runs audit, suggests improvements |
| `/init --force` on existing config | Overwrites with fresh config |
| `/init --audit` | Only reports issues, no changes |
