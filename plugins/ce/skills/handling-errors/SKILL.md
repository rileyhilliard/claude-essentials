---
name: handling-errors
description: Prevents silent failures and context loss in error handling. Use when writing try-catch blocks, designing error propagation, reviewing catch blocks, or implementing Result patterns.
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
| Generic "Error" messages | Undebuggable | Include what/why/context |
| Logging same error at each layer | Log pollution | Log once at boundary |
| Bare `except:` / `catch (e)` all | Catches system signals | Catch specific types |
