# Index Internals

The sharp edges of PostgreSQL indexing - not the basics (those are in `managing-databases`), but the specific behaviors that silently break index usage in production.

## Operator Classes

The default B-tree index on a text column supports `=`, `<`, `>`, `<=`, `>=`. It does NOT support `LIKE 'prefix%'` pattern searches. Creating a standard index and then using LIKE is one of the most common performance bugs in Postgres applications.

### LIKE Prefix Search

```sql
-- This index DOES NOT help LIKE searches on most PostgreSQL installations:
CREATE INDEX ON users (email);

-- This does:
CREATE INDEX ON users (email text_pattern_ops);

-- Query must still anchor the pattern on the left:
SELECT * FROM users WHERE email LIKE 'riley%';  -- uses index
SELECT * FROM users WHERE email LIKE '%riley%'; -- cannot use index (no anchor)
```

`text_pattern_ops` tells PostgreSQL to store index entries using byte-comparison order, which LIKE pattern matching requires. Without it, the planner skips the index.

### Case-Insensitive Search

```sql
-- Option 1: Expression index (works with standard text type)
CREATE INDEX ON users (LOWER(email));

-- Query MUST use the exact same expression:
SELECT * FROM users WHERE LOWER(email) = 'riley@example.com'; -- uses index
SELECT * FROM users WHERE email ILIKE 'riley@example.com';    -- does NOT use index

-- Option 2: citext extension (cleaner, handles ILIKE)
CREATE EXTENSION IF NOT EXISTS citext;
ALTER TABLE users ALTER COLUMN email TYPE citext;
-- Now = and ILIKE both use the regular index
```

### Trigram Indexes for LIKE '%anywhere%'

When you need substring search (not just prefix), B-tree can't help. Use `pg_trgm`:

```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX ON users USING gin (email gin_trgm_ops);

-- Now works:
SELECT * FROM users WHERE email LIKE '%@gmail%';
SELECT * FROM users WHERE email ILIKE '%riley%';
```

GIN trigram indexes are larger and slower to update than B-tree, but they're the only option for arbitrary substring matching.

## Implicit Type Cast Index Bypass

Type mismatches between parameters and column types silently prevent index usage. This is one of the hardest-to-diagnose performance problems because the query returns correct results - it just scans the whole table.

### Safe Casts (PostgreSQL Handles These)

```sql
-- Literal cast - PostgreSQL casts the literal, not the column. Index still used:
WHERE user_id = '123'       -- user_id is INTEGER
WHERE created_at > '2024-01-01' -- created_at is TIMESTAMPTZ

-- The planner sees: WHERE user_id = 123::integer (cast happens on the right side)
```

### Dangerous Casts (Bypass Index)

```sql
-- Parameter bound as wrong type in application code:
-- Python: cursor.execute("SELECT ... WHERE user_id = %s", [str(user_id)])
-- user_id column is INTEGER, but parameter is text
-- Planner may cast the column: WHERE user_id::text = $1
-- Column cast = full table scan

-- varchar vs text mismatch in older schemas:
WHERE varchar_col = some_text_value  -- if types differ, implicit cast on column side
```

### The Rule

Column types must match parameter types exactly. When in doubt, cast explicitly on the value side, never the column side:

```sql
-- Wrong (casts the column, bypasses index):
WHERE user_id::text = $1

-- Right (casts the value):
WHERE user_id = $1::integer
```

In application code, always bind parameters with the correct type. In Python/psycopg2, pass integers as integers not strings. In SQL, use explicit casts on literals: `$1::int`, `$1::timestamptz`.

### The TIMESTAMPTZ Trap

Timezone-aware columns are a common source of implicit casts:

```sql
-- created_at is TIMESTAMPTZ
-- Comparing to a TIMESTAMP literal (no timezone):
WHERE created_at = '2024-01-15 10:00:00'
-- PostgreSQL converts the literal to TIMESTAMPTZ using session timezone
-- This is usually safe, but if the session timezone changes, results change

-- Safer - be explicit:
WHERE created_at = '2024-01-15 10:00:00+00'::timestamptz
```

## Composite Index Column Ordering

The order of columns in a composite index determines what queries it can serve.

### The Prefix Rule

An index on `(a, b, c)` can satisfy:
- `WHERE a = 1`
- `WHERE a = 1 AND b = 2`
- `WHERE a = 1 AND b = 2 AND c = 3`
- `WHERE a = 1 AND b BETWEEN 5 AND 10`

It cannot satisfy:
- `WHERE b = 2` (skips `a`)
- `WHERE b = 2 AND c = 3` (skips `a`)
- `WHERE c = 3` (skips `a` and `b`)

### Equality First, Range Last

When a query has both equality and range predicates, put equality columns first:

```sql
-- Query: WHERE status = 'active' AND created_at > now() - interval '7 days'
-- Good: equality column first, range column last
CREATE INDEX ON orders (status, created_at);

-- Bad: range column first, planner can't use both
CREATE INDEX ON orders (created_at, status);
-- This index can filter by created_at but then must scan all matching rows for status
```

The reason: once the planner hits a range predicate on a B-tree index, it can scan forward but can't use subsequent index columns for filtering.

### INCLUDE Columns vs Key Columns

The `INCLUDE` clause adds non-key columns to the index for covering scans. These are not part of the B-tree structure - they're stored as payload alongside the leaf entries.

```sql
-- Covering index for this query:
-- SELECT email, created_at FROM users WHERE user_id = 123
CREATE INDEX ON users (user_id) INCLUDE (email, created_at);
```

Key differences:
- Key columns (`user_id`): used for filtering, sorting, and join strategies
- INCLUDE columns (`email`, `created_at`): only available for index-only scans, cannot be used in WHERE or ORDER BY

Don't add columns to INCLUDE speculatively. Every added column bloats the index. Only include columns that eliminate heap fetches for a specific, high-frequency query.

## Partial Indexes on High-Selectivity Conditions

When most queries filter on the same condition, index only the relevant rows:

```sql
-- 95% of queries only care about active users:
CREATE INDEX ON users (email) WHERE active = true;

-- Dramatically smaller index, same coverage for the common case
-- Queries must include the WHERE condition to use the index:
SELECT * FROM users WHERE active = true AND email = 'x@example.com'; -- uses partial index
SELECT * FROM users WHERE email = 'x@example.com'; -- cannot use partial index
```

Partial indexes are especially powerful for soft-delete patterns (`WHERE deleted_at IS NULL`) and status-filtered lookups (`WHERE status = 'pending'`).
