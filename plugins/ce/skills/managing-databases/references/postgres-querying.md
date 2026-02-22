# PostgreSQL Advanced Querying

Non-obvious query techniques and optimization patterns that Claude wouldn't default to.

## Contents

- LATERAL joins
- CTE materialization control
- DISTINCT ON
- Index-only scan requirements
- EXPLAIN ANALYZE red flags
- RANGE vs ROWS window frame gotcha

## LATERAL joins

LATERAL allows subqueries to reference columns from preceding tables. Use when you need correlated subqueries that return multiple rows/columns.

### When to use LATERAL

| Scenario | Use LATERAL? |
|----------|--------------|
| Top-N per group | Yes (faster than window functions for this) |
| Correlated subquery returning multiple columns | Yes |
| Table function with parameters from outer query | Yes |
| Simple join | No, use regular JOIN |
| Uncorrelated subquery | No |

### Top-N per group pattern

```sql
-- Get the 3 most recent orders per customer
SELECT c.id, c.name, recent_orders.*
FROM customers c
CROSS JOIN LATERAL (
    SELECT o.id, o.total, o.created_at
    FROM orders o
    WHERE o.customer_id = c.id
    ORDER BY o.created_at DESC
    LIMIT 3
) recent_orders;
```

This is faster than the `row_number()` window function approach for large datasets because it stops after N rows per group instead of numbering all rows.

### Set-returning function pattern

```sql
-- Unnest array and join with related data
SELECT u.id, u.name, t.tag
FROM users u
CROSS JOIN LATERAL unnest(u.tags) AS t(tag);
```

## CTE materialization control

PostgreSQL 12+ changed CTE behavior. CTEs are now inlined by default if referenced once. This is non-obvious because older PostgreSQL treated CTEs as optimization barriers, and many guides still reference the old behavior.

### Force materialization

Use when the CTE is expensive and referenced multiple times, or when you want a deliberate optimization barrier:

```sql
WITH expensive_calc AS MATERIALIZED (
    SELECT user_id, sum(amount) as total
    FROM transactions
    GROUP BY user_id
)
SELECT * FROM expensive_calc WHERE total > 1000
UNION ALL
SELECT * FROM expensive_calc WHERE total < 100;
```

### Force inlining

Use when you want the optimizer to push predicates into the CTE:

```sql
WITH filtered_data AS NOT MATERIALIZED (
    SELECT * FROM large_table
)
SELECT * FROM filtered_data
WHERE status = 'active';  -- This predicate gets pushed down into the CTE
```

### Decision guide

| Situation | Materialize? |
|-----------|-------------|
| CTE used multiple times | Yes (avoid recomputation) |
| You want an optimization fence | Yes (predictable execution) |
| CTE result is small, outer query complex | Yes |
| CTE used once | No (let optimizer push predicates) |
| Outer query adds selective WHERE | No (predicate pushdown helps) |

## DISTINCT ON

PostgreSQL-specific way to get first row per group. Faster than window functions for simple cases and something Claude should prefer over the `row_number()` pattern when applicable.

```sql
-- Get most recent order per customer
SELECT DISTINCT ON (customer_id)
    customer_id, id, total, created_at
FROM orders
ORDER BY customer_id, created_at DESC;
```

### Requirements

- DISTINCT ON columns must be leftmost in ORDER BY
- ORDER BY determines which row is "first"

### When to prefer DISTINCT ON over window functions

| Scenario | Use |
|----------|-----|
| First/last row per group, simple ordering | DISTINCT ON (simpler, faster) |
| Top-N per group (N > 1) | Window function or LATERAL |
| Complex tie-breaking logic | Window function |
| Need the row number in output | Window function |

## Index-only scan requirements

When PostgreSQL can answer a query entirely from the index without touching the table heap. The conditions for this are non-obvious.

### Three conditions (all required)

1. All columns in SELECT are in the index (or INCLUDE'd)
2. Visibility map shows pages are all-visible (table must be recently vacuumed)
3. No columns need to be fetched from heap

### The visibility map gotcha

Even with a perfect covering index, PostgreSQL checks the **visibility map** to determine if it can trust the index alone. If pages aren't marked all-visible (because vacuum hasn't run recently), it falls back to heap fetches.

```sql
EXPLAIN (ANALYZE, BUFFERS) SELECT user_id, email FROM users WHERE user_id = 123;
-- "Index Only Scan" with "Heap Fetches: 0" = working perfectly
-- "Index Only Scan" with "Heap Fetches: 5000" = vacuum needed
```

```sql
-- Fix high heap fetches
VACUUM users;
```

## EXPLAIN ANALYZE red flags

Don't read the whole plan. Look for these specific signals:

| Red flag | What's wrong | Fix |
|----------|-------------|-----|
| `Seq Scan` on large table with WHERE | Missing index | Create index on filter column |
| `Sort Method: external merge` | Sort spilled to disk | Increase `work_mem` for session |
| Large `Rows Removed by Filter` | Post-fetch filtering | Index doesn't cover this predicate |
| Estimated rows far from actual rows | Stale statistics | Run `ANALYZE tablename` |
| `Nested Loop` with high outer rows | Wrong join strategy | Check if `work_mem` allows hash join |
| `Buffers: shared read` >> `shared hit` | Cold cache or table too large | Warm cache or increase `shared_buffers` |

### The estimate accuracy check

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM orders WHERE customer_id = 123;

-- Compare "rows=1" (estimate) with "actual...rows=1"
-- If estimate says rows=1 but actual is rows=50000, run ANALYZE
```

Bad row estimates cascade. The planner chooses join strategies based on estimated cardinality. Wrong estimates lead to nested loops where hash joins would be 100x faster.

## RANGE vs ROWS window frame gotcha

This is the most common window function bug and it's subtle. The default frame is `RANGE UNBOUNDED PRECEDING`, which includes all rows with the **same ORDER BY value** as the current row.

```sql
SELECT value,
    sum(value) OVER (ORDER BY value RANGE UNBOUNDED PRECEDING) as range_sum,
    sum(value) OVER (ORDER BY value ROWS UNBOUNDED PRECEDING) as rows_sum
FROM (VALUES (1), (2), (2), (3)) t(value);

-- value | range_sum | rows_sum
--     1 |         1 |        1
--     2 |         5 |        3  <- RANGE includes BOTH 2s
--     2 |         5 |        5  <- RANGE includes BOTH 2s
--     3 |         8 |        8
```

When your ORDER BY column has duplicates:
- `RANGE` (default) includes all tied rows, giving the same aggregate value for ties
- `ROWS` processes one row at a time, giving a running total

If you want a true running total (monotonically increasing), use `ROWS`, not the default `RANGE`.
