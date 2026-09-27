# Extended Statistics

The highest-leverage thing most developers never touch. The PostgreSQL planner assumes column values are statistically independent by default. When they're not, estimates collapse and you get terrible plans.

## The Core Problem

```sql
-- country has 200 distinct values
-- city has 10,000 distinct values
-- But city implies country - 'Seattle' only appears with 'US'

SELECT * FROM users WHERE country = 'US' AND city = 'Seattle';
```

The planner estimates: `(users * 1/200) * (users * 1/10000)`. It multiplies the independent probabilities, getting a wildly low estimate. That causes it to choose nested loops where a hash join would be 100x faster, or skip an index that would pay off.

The planner has no idea that `city='Seattle'` already implies `country='US'`.

## CREATE STATISTICS

Three types. Pick based on the correlation:

| Type | Use when | Example |
|------|----------|---------|
| `dependencies` | One column functionally determines another | `city` implies `country`, `zip` implies `state` |
| `ndistinct` | COUNT(DISTINCT a, b) is wrong in GROUP BY estimates | Reporting queries with multi-column GROUP BY |
| `mcv` | Certain value combinations are vastly more common than others | `status='active', plan='free'` is 80% of rows |

```sql
-- For city/country correlation:
CREATE STATISTICS user_location_stats (dependencies)
ON city, country
FROM users;

-- For multi-column GROUP BY estimates:
CREATE STATISTICS order_group_stats (ndistinct)
ON status, region
FROM orders;

-- For tracking common value combinations:
CREATE STATISTICS order_status_stats (mcv)
ON status, payment_method
FROM orders;

-- Must run ANALYZE or the statistics have no effect:
ANALYZE users;
ANALYZE orders;
```

## When to Use Each Type

**`dependencies`** - When one column logically determines the other:
- Geographic hierarchies: `city`/`state`/`country`, `zip`/`state`
- Category trees: `subcategory` implies `category`
- Status transitions: certain status values only appear with certain type values

**`ndistinct`** - When GROUP BY multi-column queries have bad row estimates:
- Look for `Rows Removed by Filter` being much higher than estimated after a hash aggregate
- Or when the planner chooses a sort-based GroupAggregate over HashAggregate for a large table

**`mcv`** - When a small number of value combinations dominate the table:
- Soft-delete patterns: 95% of rows have `deleted_at IS NULL`
- Status columns: 80% of rows are `status='active'`

## Verifying It Worked

```sql
-- Check that statistics were collected:
SELECT statistics_name, column_names, kind, n_distinct, dependencies
FROM pg_stats_ext
WHERE tablename = 'users';

-- Confirm the plan improved:
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM users WHERE country = 'US' AND city = 'Seattle';
-- Look for: estimated rows now closer to actual rows
```

If the gap between estimated and actual rows is still large after ANALYZE, the wrong statistics type was chosen - try `mcv` if `dependencies` didn't help.

## Common Gotcha

Extended statistics don't help when the planner inlines a CTE. If you have:

```sql
WITH filtered AS (
  SELECT * FROM users WHERE country = 'US' AND city = 'Seattle'
)
SELECT * FROM filtered WHERE ...;
```

The planner may inline `filtered`, applying the multi-column predicate inside a larger join tree where the statistics don't apply. In that case, use `MATERIALIZED` to force the CTE to execute first, then check if the outer plan improved.

## Statistics Target

For skewed distributions, increase the statistics target on specific columns before creating extended statistics:

```sql
-- Default is 100 samples. Increase for high-cardinality or skewed columns:
ALTER TABLE orders ALTER COLUMN status SET STATISTICS 500;
ANALYZE orders;
```

Higher targets give better single-column estimates, which is the foundation that extended statistics build on.
