---
name: handling-errors
description: Prevents silent failures and context loss in error handling. Use when writing try-catch blocks, writing error messages or error responses, designing error propagation, reviewing catch blocks, or implementing Result patterns.
---

If the current repo has its own rules/skills covering this topic (check .claude/rules/ and repo CLAUDE.md), those take precedence. Apply this skill where they're silent.

# Handling Errors

## Error Categories

| Type         | Examples                           | Handling                    |
| ------------ | ---------------------------------- | --------------------------- |
| **Expected** | Validation, Not found, Unauthorized| Return Result type, log info|
| **Transient**| Network timeout, Rate limit        | Retry with backoff, log warn|
| **Unexpected**| Null reference, DB crash          | Log error, show support ID  |
| **Critical** | Auth down, Payment gateway offline | Circuit breaker, alert      |

## Writing Error Messages

An error message should tell the reader what happened, why, and what they can do next. The reader may be a developer, an end user, or an agent calling your API or tool, and an agent can only recover from what the message says. A message like "invalid input" forces them to guess, retry blindly or give up.

| Instead of | Write |
| --- | --- |
| `Error: invalid input` | `Invalid date "2026-13-01": month must be 1-12. Use YYYY-MM-DD.` |
| `Upload failed` | `Upload failed: report.pdf is 14 MB and the limit is 10 MB. Compress it or split it.` |
| `Request failed` | `GET /v1/orders returned 429. Retry after 30s (see the Retry-After header).` |

- Name the failing thing with its real values (the path, id, limit, status, the input as received). Show expected versus actual, and list the valid options when the input has a fixed set. Quote enough of a value to explain the failure, not all of it.
- Give the cause: which constraint was violated or which dependency failed.
- Give the way forward when one exists: a corrected value, a command, a retry delay, an alternative. When you don't know the fix, say so and point to a request or support ID instead of guessing.
- Keep thrown errors and API responses to one or two sentences, roughly 200 characters. Keep UI copy shorter: about 12 to 18 words, roughly 100 characters. There is no formal limit; these figures come from UX writing guides. Put stack traces, cause chains and request payloads in structured fields or logs, and link to docs when the explanation needs more room.
- Leave secrets, tokens and personal data out of messages.

For text an end user will read, also avoid blame ("You entered...") and internal details, and use the `writer` skill's UX Writer persona. Developers get the full detail in logs; users get the short version with the next step.

## Fail Fast vs Degrade Gracefully

**Fail fast** for critical dependencies:

```typescript
await connectToDatabase(); // Throws on failure - app can't run without it
```

**Degrade gracefully** for optional features:

```typescript
const prefs = await loadPreferences(userId).catch(() => DEFAULT_PREFS);
```

## Log at the Right Layer

```typescript
// Bad: logging at every layer writes the same error 3x
async function fetchData() {
  try { return await fetch(url); }
  catch (e) { console.error("Fetch failed:", e); throw e; }
}

// Good: log once where the error is handled
async function fetchData() {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response;
}
// Top level logs the error once
```

## Language-Specific Patterns

- **TypeScript/React**: See [references/typescript-react.md](references/typescript-react.md) for Error Boundaries, typed errors, Result pattern, UI display
- **Python**: See [references/python.md](references/python.md) for EAFP, exception chaining, context managers
- **Go**: See [references/go.md](references/go.md) for explicit error returns, wrapping with %w, sentinel errors
- **Rust**: See [references/rust.md](references/rust.md) for Display vs source, per-operation variants, logging the chain, silent discards, panics at FFI and task boundaries

## Anti-Patterns

| Pattern | Problem | Fix |
|---------|---------|-----|
| Empty catch blocks | Hides errors | Log or re-throw |
| `return false` on error | Loses context | Return Result type |
| Generic "Error" messages | Undebuggable | Say what, why and the next step |
| Logging same error at each layer | Log pollution | Log once at boundary |
| Bare `except:` / `catch (e)` all | Catches system signals | Catch specific types |
