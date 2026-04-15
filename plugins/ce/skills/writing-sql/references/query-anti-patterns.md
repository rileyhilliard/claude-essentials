# Query Anti-Patterns

Patterns that look correct, return correct results, and destroy performance at scale. Most are invisible until the table hits millions of rows.

## OFFSET Pagination

`LIMIT n OFFSET m` scans and discards `m` rows on every request. The cost grows linearly with page depth.

```sql
-- Page 1: fast (scans 20 rows)
SELECT * FROM orders ORDER BY created_at DESC LIMIT 20 OFFSET 0;

-- Page 1000: scans 20,020 rows, returns 20
SELECT * FROM orders ORDER BY created_at DESC LIMIT 20 OFFSET 20000;

-- Page 50,000: scans 1,000,020 rows, returns 20
SELECT * FROM orders ORDER BY created_at DESC LIMIT 20 OFFSET 1000000;
```

### Keyset Pagination

Use the last row's values as the next page's starting point:

```sql
-- First page:
SELECT id, created_at, amount
FROM orders
ORDER BY created_at DESC, id DESC
LIMIT 20;

-- Next page (pass last row's created_at and id from previous result):
SELECT id, created_at, amount
FROM orders
WHERE (created_at, id) < ($last_created_at, $last_id)
ORDER BY created_at DESC, id DESC
LIMIT 20;
```

The tuple comparison `(created_at, id) < (val1, val2)` correctly handles ties on `created_at` by falling back to `id`. This requires a composite index:

```sql
CREATE INDEX ON orders (created_at DESC, id DESC);
```

Every page request is O(log n) instead of O(n). At page 50,000, the keyset query reads exactly 20 rows.

**When OFFSET is acceptable:**
- Total result set is small (under ~10,000 rows)
- Admin/internal tools where page 500 is never reached
- Batch exports that read sequentially (OFFSET 0, 1000, 2000...)

## NOT IN with Nullable Subquery

This is the most dangerous NULL pitfall in SQL. The query returns correct results for years, then a single NULL value enters the subquery column and the outer query returns zero rows.

```sql
-- Looks right, silently broken when parent_id contains any NULL:
SELECT * FROM categories
WHERE id NOT IN (SELECT parent_id FROM categories);

-- Why: NOT IN with NULLs
-- WHERE id NOT IN (1, 5, NULL, 23)
-- = WHERE id != 1 AND id != 5 AND id != NULL AND id != 23
-- = WHERE ... AND NULL (unknown)
-- = WHERE ... AND FALSE (for every row, the NULL comparison makes the whole condition unknown)
-- Result: zero rows
```

### Fix

```sql
-- Option 1: NOT EXISTS (correct, and often faster)
SELECT * FROM categories c1
WHERE NOT EXISTS (
  SELECT 1 FROM categories c2
  WHERE c2.parent_id = c1.id
);

-- Option 2: Filter NULLs from the subquery explicitly
SELECT * FROM categories
WHERE id NOT IN (
  SELECT parent_id FROM categories WHERE parent_id IS NOT NULL
);

-- Option 3: LEFT JOIN anti-join pattern
SELECT c1.*
FROM categories c1
LEFT JOIN categories c2 ON c2.parent_id = c1.id
WHERE c2.parent_id IS NULL;
```

`NOT EXISTS` is usually the clearest and gives the planner the most flexibility to choose an efficient plan.

## DISTINCT Masking a Bad Join

When a query unexpectedly returns duplicate rows and `SELECT DISTINCT` is added to "fix" it, the duplicates are symptoms of a join producing multiple matches. DISTINCT hides the problem without solving it, and adds a full sort or hash operation.

```sql
-- Adding DISTINCT here probably means the join is wrong:
SELECT DISTINCT u.id, u.name
FROM users u
JOIN user_tags ut ON ut.user_id = u.id
JOIN tags t ON t.id = ut.tag_id;
-- If you don't need tag columns in SELECT, the JOIN produces one row per tag per user

-- Fix: ask why you're joining tags at all
-- If checking existence: use EXISTS
SELECT u.id, u.name
FROM users u
WHERE EXISTS (SELECT 1 FROM user_tags WHERE user_id = u.id);

-- If you need tag data: don't DISTINCT, accept one row per tag
-- Or aggregate: STRING_AGG(t.name, ', ')
```

## Correlated Subqueries in SELECT List

A subquery in the SELECT list that references the outer query runs once per row in the outer result. For a 100,000-row result, that's 100,000 separate queries.

```sql
-- Runs one COUNT query per customer row:
SELECT
  c.id,
  c.name,
  (SELECT COUNT(*) FROM orders WHERE customer_id = c.id) AS order_count
FROM customers c;
```

### Fix: Join or Lateral

```sql
-- Left join with pre-aggregation (usually fastest):
SELECT c.id, c.name, COALESCE(o.order_count, 0) AS order_count
FROM customers c
LEFT JOIN (
  SELECT customer_id, COUNT(*) AS order_count
  FROM orders
  GROUP BY customer_id
) o ON o.customer_id = c.id;

-- Or LATERAL (cleaner when computing multiple values from the same subquery):
SELECT c.id, c.name, o.order_count, o.total_revenue
FROM customers c
CROSS JOIN LATERAL (
  SELECT COUNT(*) AS order_count, SUM(amount) AS total_revenue
  FROM orders
  WHERE customer_id = c.id
) o;
```

## Functions on Indexed Columns in WHERE

Applying a function to a column in a WHERE clause prevents the planner from using a regular index on that column. The planner can only use an index if the predicate is in the same form as the index entries.

```sql
-- Bypasses index on created_at:
WHERE date_trunc('day', created_at) = '2024-01-15'

-- Fix: use a range instead
WHERE created_at >= '2024-01-15' AND created_at < '2024-01-16'

-- Bypasses index on email:
WHERE LOWER(email) = 'riley@example.com'

-- Fix: expression index (index must be created first)
CREATE INDEX ON users (LOWER(email));
-- Now the query can use the index

-- Bypasses index (a common ORM pattern):
WHERE EXTRACT(year FROM created_at) = 2024

-- Fix: range
WHERE created_at >= '2024-01-01' AND created_at < '2025-01-01'
```

## Large IN Lists vs = ANY()

For large IN lists passed as parameters, prefer `= ANY()` with an array parameter:

```sql
-- Literal list: planner may generate a poor plan above ~1000 elements
WHERE id IN (1, 2, 3, ..., 5000)

-- Subquery: usually transformed to a semi-join efficiently
WHERE id IN (SELECT id FROM staging_table WHERE batch_id = $1)

-- Array parameter: clean, indexed, works at any size
WHERE id = ANY($1::int[])
-- Bind as: cursor.execute("...", [list_of_ids])
-- With psycopg2: pass a Python list, it handles the array conversion
```

The `= ANY(array)` form allows the planner to use an index on `id` and processes the array as a single parameter rather than N literals.

## Unbounded Recursive CTEs

Recursive CTEs without cycle protection will loop forever if the data has cycles. Always bound recursion depth or add cycle detection.

```sql
-- Dangerous: no cycle detection, infinite loop if data has cycles
WITH RECURSIVE tree AS (
  SELECT id, parent_id, name FROM categories WHERE parent_id IS NULL
  UNION ALL
  SELECT c.id, c.parent_id, c.name
  FROM categories c
  JOIN tree t ON t.id = c.parent_id
)
SELECT * FROM tree;

-- PostgreSQL 14+: built-in cycle detection
WITH RECURSIVE tree AS (
  SELECT id, parent_id, name FROM categories WHERE parent_id IS NULL
  UNION ALL
  SELECT c.id, c.parent_id, c.name
  FROM categories c
  JOIN tree t ON t.id = c.parent_id
)
CYCLE id SET is_cycle USING path
SELECT * FROM tree WHERE NOT is_cycle;

-- PostgreSQL 13 and earlier: manual path accumulation
WITH RECURSIVE tree AS (
  SELECT id, parent_id, name, ARRAY[id] AS visited
  FROM categories WHERE parent_id IS NULL
  UNION ALL
  SELECT c.id, c.parent_id, c.name, t.visited || c.id
  FROM categories c
  JOIN tree t ON t.id = c.parent_id
  WHERE c.id != ALL(t.visited)  -- stop if we've seen this node
)
SELECT * FROM tree;
```

Always index the recursive join column (`parent_id` in this case). Without an index, each recursive iteration does a full table scan.

## Unnecessary Sorting in Subqueries

An ORDER BY inside a subquery or CTE has no guaranteed effect on the outer query's result order. The planner is free to ignore it.

```sql
-- The ORDER BY here does nothing guaranteed:
SELECT * FROM (
  SELECT id, name FROM users ORDER BY name
) sub
WHERE id > 100;

-- The outer query may return rows in any order
-- If you need ordering, put ORDER BY on the outer query:
SELECT id, name FROM users
WHERE id > 100
ORDER BY name;
```

The exception is when ORDER BY is combined with LIMIT inside a subquery - in that case it selects which rows to keep, which does matter. But ordering for the sake of the outer query's result order never works reliably.
