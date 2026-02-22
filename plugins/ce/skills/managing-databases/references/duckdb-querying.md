# DuckDB Advanced Querying

DuckDB SQL extensions to prefer over the verbose standard SQL that Claude would generate by default.

## Contents

- ASOF JOIN for temporal data
- QUALIFY over subquery wrapping
- PIVOT and UNPIVOT
- SELECT shortcuts
- POSITIONAL JOIN
- List comprehensions
- GROUPING SETS, ROLLUP, CUBE
- Anti-patterns in DuckDB

## ASOF JOIN for temporal data

Solves the "what was the value at this point in time?" problem that normally requires ugly correlated subqueries or window functions.

### Prefer ASOF JOIN over this pattern

```sql
-- Standard SQL approach (verbose, slow):
SELECT s.*, (
    SELECT p.price FROM prices p
    WHERE p.ticker = s.ticker AND p.price_time <= s.sale_time
    ORDER BY p.price_time DESC LIMIT 1
) as price
FROM sales s;

-- DuckDB: one line
SELECT s.*, p.price
FROM sales s
ASOF JOIN prices p
  ON s.ticker = p.ticker
  AND s.sale_time >= p.price_time;
```

For each row in `sales`, finds the row in `prices` with matching ticker and the largest `price_time` that is <= `sale_time`.

### When to use

| Scenario | Use ASOF JOIN? |
|----------|---------------|
| Point-in-time lookups (price, rate, status at time T) | Yes |
| Joining time-series data with different granularities | Yes |
| Exact match on timestamp | No (use regular JOIN) |
| Nearest future match (not past) | Flip the inequality direction |

### Gotcha: requires sorted input

ASOF JOIN assumes the temporal column is sorted. On unsorted data, results may be wrong or the query may be slow. Sort your data or ensure the source is time-ordered.

## QUALIFY over subquery wrapping

Filter window function results inline without a subquery. Claude tends to generate the verbose subquery pattern. Use QUALIFY instead.

```sql
-- Claude's default: subquery wrapping
SELECT * FROM (
    SELECT *, row_number() OVER (PARTITION BY dept ORDER BY salary DESC) as rn
    FROM employees
) sub
WHERE rn = 1;

-- DuckDB: QUALIFY (same result, less nesting)
SELECT *
FROM employees
QUALIFY row_number() OVER (PARTITION BY dept ORDER BY salary DESC) = 1;
```

### Common patterns

```sql
-- Top N per group
SELECT *
FROM orders
QUALIFY row_number() OVER (PARTITION BY customer_id ORDER BY date DESC) <= 3;

-- Filter on aggregate window
SELECT *
FROM sales
QUALIFY sum(amount) OVER (PARTITION BY region) > 10000;

-- Deduplicate: keep latest per key
SELECT *
FROM events
QUALIFY row_number() OVER (PARTITION BY event_id ORDER BY updated_at DESC) = 1;
```

## PIVOT and UNPIVOT

Prefer over CASE expression matrices for data reshaping.

### PIVOT (long to wide)

```sql
-- Instead of:
SELECT year,
    sum(CASE WHEN quarter = 'Q1' THEN sales END) as Q1,
    sum(CASE WHEN quarter = 'Q2' THEN sales END) as Q2,
    sum(CASE WHEN quarter = 'Q3' THEN sales END) as Q3,
    sum(CASE WHEN quarter = 'Q4' THEN sales END) as Q4
FROM monthly_sales GROUP BY year;

-- Use PIVOT:
PIVOT monthly_sales
ON quarter
USING sum(sales)
GROUP BY year;
```

### Dynamic PIVOT (auto-detect column values)

```sql
-- Don't need to enumerate all values
PIVOT sales_data
ON quarter
USING sum(amount)
GROUP BY year;
```

### UNPIVOT (wide to long)

```sql
UNPIVOT products
ON jan, feb, mar
INTO NAME month VALUE sales;

-- Dynamic: all columns except specified ones
UNPIVOT products
ON COLUMNS(* EXCLUDE (product_id, product_name))
INTO NAME attribute VALUE value;
```

## SELECT shortcuts

DuckDB extensions that produce cleaner queries. Use these instead of the standard SQL equivalents.

### FROM-first queries

```sql
-- Skip SELECT for quick exploration
FROM orders WHERE status = 'completed';

-- FROM-first with SELECT
FROM orders
SELECT customer_id, sum(total)
WHERE status = 'completed'
GROUP BY customer_id;
```

### EXCLUDE and REPLACE

```sql
-- All columns except specific ones (vs listing 50 columns)
SELECT * EXCLUDE (password, ssn) FROM users;

-- All columns with transformations applied
SELECT * REPLACE (upper(name) AS name, round(score, 2) AS score) FROM users;
```

### Column aliases in GROUP BY/HAVING

```sql
-- Reference alias directly (not valid in standard SQL)
SELECT customer_id, extract(year from order_date) as year, sum(total)
FROM orders
GROUP BY customer_id, year;
```

### Function chaining

```sql
-- Chain operations (reads left to right)
SELECT name.lower().trim().replace(' ', '_') as slug FROM users;
```

## POSITIONAL JOIN

Join tables by row position when there's no common key. Equivalent to pandas index-based join.

```sql
SELECT *
FROM predictions
POSITIONAL JOIN actuals;
```

Use for:
- Combining parallel arrays or separate computation results
- Aligning data from different sources without a join key
- Quick comparison of two same-length result sets

**Gotcha:** If tables have different row counts, shorter table gets NULLs. No error, just silent NULL padding.

## List comprehensions

Python-style list operations in SQL. Prefer over verbose `unnest`/`array_agg` patterns.

```sql
-- Transform elements
SELECT [x * 2 FOR x IN [1, 2, 3]];  -- [2, 4, 6]

-- Filter elements
SELECT [x FOR x IN scores IF x > 90];  -- Only passing scores

-- Transform array column
SELECT [upper(tag) FOR tag IN tags] as upper_tags FROM posts;

-- Nested comprehension
SELECT [x + y FOR x IN [1, 2] FOR y IN [10, 20]];  -- [11, 21, 12, 22]
```

## GROUPING SETS, ROLLUP, CUBE

Multiple aggregation levels in one query. Prefer over UNION ALL of separate GROUP BY queries.

### GROUPING SETS (specific combinations)

```sql
SELECT region, product, sum(sales)
FROM orders
GROUP BY GROUPING SETS (
    (region, product),  -- Detail
    (region),           -- Region subtotal
    (product),          -- Product subtotal
    ()                  -- Grand total
);
```

### ROLLUP (hierarchical drilldown)

```sql
-- Generates: (year, quarter, month), (year, quarter), (year), ()
SELECT year, quarter, month, sum(sales)
FROM orders
GROUP BY ROLLUP (year, quarter, month);
```

### CUBE (all combinations)

```sql
-- Generates all 2^n combinations
SELECT region, product, sum(sales)
FROM orders
GROUP BY CUBE (region, product);
```

### Identifying which level each row belongs to

```sql
SELECT
    CASE WHEN grouping(region) = 1 THEN 'All' ELSE region END as region,
    CASE WHEN grouping(product) = 1 THEN 'All' ELSE product END as product,
    sum(sales)
FROM orders
GROUP BY CUBE (region, product);
```

## Anti-patterns in DuckDB

### Using standard SQL when DuckDB extensions exist

The biggest anti-pattern is writing verbose standard SQL when DuckDB has a cleaner, faster alternative. If you find yourself writing a subquery just to filter window functions, use QUALIFY. If you're writing CASE expression matrices for pivoting, use PIVOT. If you're writing correlated subqueries for temporal lookups, use ASOF JOIN.

### SELECT * on remote Parquet files

```sql
-- Extremely slow: downloads entire file over network
SELECT * FROM read_parquet('s3://bucket/huge.parquet') WHERE id = 123;

-- Fast: only downloads needed columns
SELECT id, name FROM read_parquet('s3://bucket/huge.parquet') WHERE id = 123;
```

Column projection on remote files isn't just a performance tip; it can be the difference between a 2-second query and a 10-minute query.

### Not setting memory limits in shared environments

DuckDB defaults to using all available RAM. In production environments with other services, always set explicit limits:

```sql
SET memory_limit = '4GB';
SET threads = 4;
```

Without these, a single analytical query can starve your web server, database, or other critical processes.
