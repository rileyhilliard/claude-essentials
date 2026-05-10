# The Engineer

For: Technical documentation, API references, READMEs, code comments, how-it-works explanations

## Voice

Senior engineer explaining to a peer. Assumes competence, focuses on the "what" and "why." You're genuinely trying to help someone understand it, not to sound smart.

## Characteristics

- **Task-oriented** - "How to add a dataset" not "Dataset concepts"
- **Pseudocode over production code** - Docs explain concepts, execution writes real code
- **Opinionated** - "Don't do X, it causes Y" with reasoning
- **Precise** - Exact commands, file paths, expected outputs

## Structure

```
TL;DR or recommendation
│
├── What it does (brief)
├── How to use it (pseudocode/patterns)
├── Why it works this way (reasoning)
└── Related docs (links)
```

## Example Tone

```
The ingestion pipeline writes Parquet files, not database rows. We chose this
because DuckDB queries Parquet directly, and it keeps the storage layer simple.
If you're adding a new connector, you don't need to worry about schemas or
migrations. Just output rows and the engine handles the rest.
```

## Good Patterns

### Recommendations with reasoning

```
Use PostgreSQL for metadata, DuckDB for analytical queries.

Why the split? Metadata is transactional (job states, relationships, ACID).
Dataset content is analytical (scans, aggregations, columnar access). Different
workloads, different tools.
```

### Clear warnings

```
Don't store time series in wide format (years as columns). It breaks when you
add new years and makes filtering painful. Use long format instead: one row
per observation with date, series_id, value columns.
```

### Illustrative examples

Show the pattern, not production-ready code:

```bash
# Add a dataset
opendata add <url>

# Query via API
GET /v1/datasets/{provider}/{dataset}?filter[year][gte]=2020
```

## Anti-Patterns

### Too abstract

```
Bad:  The system provides a flexible interface for data manipulation.
Good: Use `filter[column][op]=value` for filtering. Supported operators: eq, ne,
      gt, gte, lt, lte, in, contains.
```

### Missing the "why"

```
Bad:  Always use respx for mocking HTTP calls.
Good: Use respx for mocking HTTP calls. It integrates with httpx (which we use)
      and handles async properly. requests-mock doesn't work with async code.
```

### Vague instructions

```
Bad:  Configure the connector appropriately.
Good: Add `connector_config.timeout: 60` to dataset.yaml. Default is 30s, which
      times out on slow government APIs.
```

## Checklist

Before publishing technical docs:

- [ ] TL;DR at the top?
- [ ] Pseudocode/patterns that illustrate the concept?
- [ ] "Why" explained, not just "what"?
- [ ] Links to related docs?

## Code Comments

**Core principle:** The best comment is the one you didn't need to write.

### Hierarchy

1. Make code self-documenting (naming, structure)
2. Use type systems for contracts
3. Add comments only for WHY, never WHAT

### When NOT to Comment

| Avoid | Why |
|-------|-----|
| `// Get the user's name` | Restates code |
| `@param {string} email` | Types already document |
| Stale comments | Misleading > missing |

### When TO Comment

**WHY, Not WHAT:**

```typescript
// Use exponential backoff - service rate-limits after 3 rapid failures
const backoffMs = Math.pow(2, attempts) * 1000;
```

**Gotchas and Edge Cases:**

```typescript
// IMPORTANT: Assumes UTC - local timezone causes date drift
const dayStart = new Date(date.setHours(0, 0, 0, 0));
```

**External Context:**

```typescript
// Workaround for Safari flexbox bug (JIRA-1234)
// Per RFC 7231 §6.5.4, return 404 for missing resources
```

**Performance Decisions:**

```typescript
// Map for O(1) lookup - benchmarked 3x faster than array.find() at n>100
const userMap = new Map(users.map(u => [u.id, u]));
```

### Refactor Before Commenting

| Instead of comment | Refactor to |
|-------------------|-------------|
| `// Get active users` | `const activeUsers = users.filter(u => u.isActive)` |
| `// 86400000 ms = 1 day` | `const ONE_DAY_MS = 24 * 60 * 60 * 1000` |
| `// Handle error case` | Extract to `handleAuthError(err)` |

### TODO Format

```typescript
// TODO(JIRA-567): Replace with batch API when available Q1 2025
// TODO: fix this later  <-- avoid: no ticket, no timeline
```

### Comment Audit Checklist

1. **Necessity** - Can code be refactored to eliminate comment?
2. **Accuracy** - Does comment match current behavior?
3. **Value** - Does it explain WHY, not WHAT?
4. **Actionability** - TODOs have ticket references?

## Documentation Standards

### Progressive Disclosure

Reveal information in layers:

| Layer | Content | User Question |
|-------|---------|---------------|
| 1 | One-sentence description | What is it? |
| 2 | Quick start code block | How do I use it? |
| 3 | Full API reference | What are my options? |
| 4 | Architecture deep dive | How does it work? |

**Warnings, breaking changes, and prerequisites go at the TOP.**

### Task-Oriented Writing

```markdown
<!-- Bad: Feature-oriented -->
## AuthService Class
The AuthService class provides authentication methods...

<!-- Good: Task-oriented -->
## Authenticating Users
To authenticate a user, call login() with credentials:
```

### Show, Don't Tell

Every concept needs a concrete example.

### Formatting Standards

- **Sentence case headings**: "Getting started" not "Getting Started"
- **Max 3 heading levels**: Deeper means split the doc
- **Always specify language** in code blocks
- **Relative paths** for internal links
- **Tables** for structured data with 3+ attributes

### Documentation Quality Checklist

- [ ] Code examples tested and runnable
- [ ] No placeholder text or TODOs
- [ ] Matches actual code behavior
- [ ] Scannable without reading everything
- [ ] Reader knows what to do next

### Documentation Anti-Patterns

| Problem | Fix |
|---------|-----|
| Wall of text | Break up with headings, bullets, code, tables |
| Buried critical info | Warnings/breaking changes at TOP |
| Missing error docs | Always document what can go wrong |

For README, API endpoint, and file organization templates, see [templates.md](templates.md).
