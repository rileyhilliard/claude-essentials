# Aggregation Patterns

Patterns for conditional aggregation, multi-level reporting, and the NULL edge cases that produce wrong results silently.

## FILTER Clause

`FILTER (WHERE condition)` is the correct way to write conditional aggregation. It replaces the `CASE WHEN ... THEN ... END` pattern that most developers reach for first.

```sql
-- What most developers write:
SELECT
  SUM(CASE WHEN status = 'paid' THEN amount ELSE 0 END) AS paid_total,
  SUM(CASE WHEN status = 'refunded' THEN amount ELSE 0 END) AS refunded_total,
  COUNT(CASE WHEN status = 'pending' THEN 1 END) AS pending_count
FROM orders;

-- What Staff+ DBAs write:
SELECT
  SUM(amount) FILTER (WHERE status = 'paid') AS paid_total,
  SUM(amount) FILTER (WHERE status = 'refunded') AS refunded_total,
  COUNT(*) FILTER (WHERE status = 'pending') AS pending_count
FROM orders;
```

FILTER works on any aggregate function: `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`, `ARRAY_AGG`, `STRING_AGG`, `JSON_AGG`, `BOOL_AND`, `BOOL_OR`.

### Why FILTER Over CASE WHEN

The CASE WHEN version returns `0` or `NULL` for non-matching rows depending on the ELSE branch. This creates subtle correctness issues:

```sql
-- CASE WHEN with no ELSE returns NULL for non-matching rows:
SUM(CASE WHEN status = 'paid' THEN amount END)
-- SUM ignores NULLs, so this works - but AVG won't:

AVG(CASE WHEN status = 'paid' THEN amount END)
-- Divides by count of non-NULL rows (only paid orders)
-- This is actually correct, but the intent is unclear

-- FILTER makes intent explicit:
AVG(amount) FILTER (WHERE status = 'paid')
-- Clearly: average amount among paid orders only
```

### Pivot Tables Without ORMs

```sql
-- Monthly revenue by product category - no CASE WHEN forest needed:
SELECT
  date_trunc('month', created_at) AS month,
  SUM(amount) FILTER (WHERE category = 'software') AS software_revenue,
  SUM(amount) FILTER (WHERE category = 'hardware') AS hardware_revenue,
  SUM(amount) FILTER (WHERE category = 'services') AS services_revenue,
  SUM(amount) AS total_revenue
FROM orders
GROUP BY date_trunc('month', created_at)
ORDER BY month;
```

## GROUPING SETS, ROLLUP, CUBE

These produce multi-level aggregations in a single pass. The alternative - UNION ALL of multiple GROUP BY queries - runs the same scan N times.

### GROUPING SETS

Explicit control over which grouping combinations to compute:

```sql
-- Instead of 3 separate queries unioned together:
SELECT region, product, SUM(revenue)
FROM sales
GROUP BY GROUPING SETS (
  (region, product),  -- subtotal by region + product
  (region),           -- subtotal by region only
  ()                  -- grand total
);
```

The `()` grouping set is the grand total (no columns in GROUP BY).

### ROLLUP

Hierarchical totals. `ROLLUP(a, b, c)` produces groupings: `(a,b,c)`, `(a,b)`, `(a)`, `()`.

```sql
-- Year > Month > Day revenue hierarchy:
SELECT
  EXTRACT(year FROM created_at) AS year,
  EXTRACT(month FROM created_at) AS month,
  EXTRACT(day FROM created_at) AS day,
  SUM(revenue) AS total
FROM orders
GROUP BY ROLLUP(
  EXTRACT(year FROM created_at),
  EXTRACT(month FROM created_at),
  EXTRACT(day FROM created_at)
);
```

### CUBE

All 2^n combinations. Use carefully - for 4 columns, that's 16 groupings.

```sql
-- All combinations of region, product, quarter:
SELECT region, product, quarter, SUM(revenue)
FROM sales
GROUP BY CUBE(region, product, quarter);
-- Produces 8 grouping combinations
```

### Detecting Grouping Level with GROUPING()

When rows represent different aggregation levels, use `GROUPING()` to distinguish them:

```sql
SELECT
  CASE WHEN GROUPING(region) = 1 THEN 'All Regions' ELSE region END AS region,
  CASE WHEN GROUPING(product) = 1 THEN 'All Products' ELSE product END AS product,
  SUM(revenue)
FROM sales
GROUP BY ROLLUP(region, product);
-- GROUPING() returns 1 when the column is aggregated away, 0 when it's grouped on
```

## NULL Edge Cases in Aggregates

### COUNT Distinctions

These return different results and the differences matter:

```sql
SELECT
  COUNT(*),              -- all rows including NULLs
  COUNT(col),            -- non-NULL values only
  COUNT(DISTINCT col),   -- distinct non-NULL values only
  COUNT(DISTINCT col1, col2)  -- NOT VALID in PostgreSQL - use COUNT(DISTINCT (col1, col2))
FROM t;
```

For multi-column distinct counts:
```sql
-- Wrong in PostgreSQL:
COUNT(DISTINCT col1, col2)

-- Right:
COUNT(DISTINCT (col1, col2))  -- counts distinct row combinations
-- Or if you need approximate counts on large tables:
SELECT COUNT(*) FROM (SELECT DISTINCT col1, col2 FROM t) sub;
```

### ARRAY_AGG Silently Drops NULLs

```sql
-- NULLs in the column are silently excluded from the array:
SELECT ARRAY_AGG(tag) FROM tags WHERE user_id = 1;
-- If tag is NULL for some rows, those rows are not in the array

-- If you need to preserve NULLs, they're included by default in ARRAY_AGG
-- If you want to explicitly exclude NULLs (and it's documented):
SELECT ARRAY_AGG(tag) FILTER (WHERE tag IS NOT NULL) FROM tags WHERE user_id = 1;
-- Or use array_remove to clean up after:
SELECT array_remove(ARRAY_AGG(tag), NULL) FROM tags WHERE user_id = 1;
```

### STRING_AGG and NULLs

`STRING_AGG(col, delimiter)` excludes NULL values from the concatenation. This is usually what you want, but if a NULL means "missing data" that should surface, handle it explicitly:

```sql
-- NULLs silently disappear:
SELECT STRING_AGG(name, ', ') FROM users;

-- Make missing data visible:
SELECT STRING_AGG(COALESCE(name, '[unknown]'), ', ') FROM users;
```

### NULLS FIRST / NULLS LAST in Window Functions

NULL ordering in window function ORDER BY affects RANGE frame behavior:

```sql
-- Default NULL ordering: NULLS LAST for ASC, NULLS FIRST for DESC
-- This affects which rows are included in the frame

SELECT
  value,
  SUM(value) OVER (
    ORDER BY created_at NULLS LAST  -- explicit is better than relying on defaults
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
  ) AS running_total
FROM events;
```

If `created_at` is NULL for some rows and you're using RANGE mode, those rows cluster together and the frame includes all of them. ROWS mode treats each row independently. When in doubt, use `ROWS` and be explicit about `NULLS FIRST/LAST`.
