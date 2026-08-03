# Rule and Config Templates

Templates for generating `.claude/` files during Fresh Init Mode (Step 5) or when applying Audit Mode fixes.

## CLAUDE.md Template

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

## settings.json Template

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

## Universal Rule Templates

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

## Stack-Specific Rule Templates

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

## Rule with References Template (for complex domains)

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
