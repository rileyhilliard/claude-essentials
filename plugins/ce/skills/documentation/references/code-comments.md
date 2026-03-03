# Code Comments

**Core principle:** The best comment is the one you didn't need to write.

## Hierarchy

1. Make code self-documenting (naming, structure)
2. Use type systems for contracts
3. Add comments only for WHY, never WHAT

## When NOT to Comment

| Avoid | Why |
|-------|-----|
| `// Get the user's name` | Restates code |
| `@param {string} email` | Types already document |
| Stale comments | Misleading > missing |

## When TO Comment

### WHY, Not WHAT

```typescript
// Use exponential backoff - service rate-limits after 3 rapid failures
const backoffMs = Math.pow(2, attempts) * 1000;
```

### Gotchas and Edge Cases

```typescript
// IMPORTANT: Assumes UTC - local timezone causes date drift
const dayStart = new Date(date.setHours(0, 0, 0, 0));
```

### External Context

```typescript
// Workaround for Safari flexbox bug (JIRA-1234)
// Per RFC 7231 §6.5.4, return 404 for missing resources
```

### Performance Decisions

```typescript
// Map for O(1) lookup - benchmarked 3x faster than array.find() at n>100
const userMap = new Map(users.map(u => [u.id, u]));
```

## Refactor Before Commenting

| Instead of comment | Refactor to |
|-------------------|-------------|
| `// Get active users` | `const activeUsers = users.filter(u => u.isActive)` |
| `// 86400000 ms = 1 day` | `const ONE_DAY_MS = 24 * 60 * 60 * 1000` |
| `// Handle error case` | Extract to `handleAuthError(err)` |

## TODO Format

```typescript
// TODO(JIRA-567): Replace with batch API when available Q1 2025
// TODO: fix this later  <-- avoid: no ticket, no timeline
```

## Audit Checklist

1. **Necessity** - Can code be refactored to eliminate comment?
2. **Accuracy** - Does comment match current behavior?
3. **Value** - Does it explain WHY, not WHAT?
4. **Actionability** - TODOs have ticket references?
