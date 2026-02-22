# Parquet Query Optimization

Non-obvious query patterns that leverage Parquet's structure for fast execution.

## Contents

- Predicate pushdown mechanics
- Row group pruning
- Bloom filters
- Page-level pruning
- Data layout for queries
- Column projection
- Statistics limitations

## Predicate pushdown mechanics

Predicate pushdown filters data before it's fully loaded, using Parquet metadata to skip irrelevant data.

### How it works

1. Query engine reads Parquet footer (schema + row group metadata)
2. For each row group, checks column statistics against predicates
3. Skips row groups that can't contain matching rows
4. Only reads and decompresses relevant row groups

### What gets pushed down

| Predicate type | Pushed down? |
|----------------|--------------|
| `column = value` | Yes |
| `column > value` | Yes |
| `column BETWEEN a AND b` | Yes |
| `column IN (a, b, c)` | Yes |
| `column IS NULL` | Yes |
| `function(column) = value` | No |
| `column1 + column2 > value` | No |
| `LIKE '%pattern%'` | No |

### Enabling pushdown

Most engines enable it by default. Verify with query plans:

```sql
-- DuckDB
EXPLAIN SELECT * FROM read_parquet('data.parquet') WHERE year = 2024;
-- Look for "Parquet Scan" with filter pushed

-- Check actual pruning
EXPLAIN ANALYZE SELECT * FROM read_parquet('data.parquet') WHERE year = 2024;
-- Compare rows scanned vs rows returned
```

## Row group pruning

Row groups are skipped entirely based on min/max statistics.

### How statistics enable pruning

Each column in each row group stores:
- Minimum value
- Maximum value
- Null count

```
Row Group 0: year min=2020, max=2021
Row Group 1: year min=2022, max=2023
Row Group 2: year min=2024, max=2024

Query: WHERE year = 2024
Result: Only Row Group 2 is read
```

### When pruning works well

| Data layout | Pruning effectiveness |
|-------------|----------------------|
| Sorted by filter column | Excellent (1-2 row groups) |
| Clustered/semi-sorted | Good |
| Random order | Poor (most row groups overlap) |

### Checking pruning effectiveness

```sql
-- DuckDB: Compare file size vs data read
EXPLAIN ANALYZE
SELECT count(*) FROM read_parquet('data.parquet') WHERE id = 12345;
-- Look at actual rows scanned vs total rows
```

## Bloom filters

Bloom filters provide probabilistic membership tests for high-cardinality columns where min/max statistics don't help.

### When bloom filters help

| Column type | Min/max useful? | Bloom filter useful? |
|-------------|-----------------|---------------------|
| Sorted timestamp | Yes | No (redundant) |
| Status (few values) | Yes | No (redundant) |
| UUID / ID (random) | No | Yes |
| Email | No | Yes |
| High cardinality random | No | Yes |

### How bloom filters work

- Compact data structure (~2-8 KB per column per row group)
- Answers "might this value exist?" with possible false positives
- Never false negatives (if filter says "no", value definitely absent)
- Enables row group skipping for equality predicates on random data

### Writing with bloom filters

```python
# PyArrow
pq.write_table(
    table,
    'output.parquet',
    write_statistics=True,
    column_encoding={'id': 'PLAIN'},  # Bloom filters work with any encoding
    # Bloom filter config varies by writer
)
```

### Query patterns that benefit

```sql
-- Point lookups on high-cardinality columns
SELECT * FROM data WHERE user_id = 'abc-123-xyz';

-- IN clauses with few values
SELECT * FROM data WHERE order_id IN ('order1', 'order2', 'order3');
```

## Page-level pruning

More granular than row groups: skip individual pages within a row group.

### Requirements

- Parquet files must include page-level statistics
- Not all writers enable this by default

### How it works

```
Row Group 0 (1M rows):
  Page 0: id min=1, max=1000
  Page 1: id min=1001, max=2000
  Page 2: id min=2001, max=3000
  ...

Query: WHERE id = 1500
Result: Only Page 1 is read
```

### Checking for page statistics

```python
import pyarrow.parquet as pq

# Check if file has page statistics
metadata = pq.read_metadata('file.parquet')
for rg in range(metadata.num_row_groups):
    for col in range(metadata.num_columns):
        col_meta = metadata.row_group(rg).column(col)
        print(f"Has page stats: {col_meta.is_stats_set}")
```

## Data layout for queries

How you write data determines how well it can be queried.

### Sort by filter columns

```python
# Before writing, sort by commonly filtered columns
df = df.sort_values(['date', 'region'])
pq.write_table(pa.Table.from_pandas(df), 'sorted.parquet')
```

### Multi-column sort order

Sort by columns in order of:
1. Most selective filter (usually date)
2. Second most common filter
3. Third most common filter

```python
# If queries usually filter by date, then region, then status:
df = df.sort_values(['date', 'region', 'status'])
```

### Z-ordering for multi-dimensional queries

When queries filter by multiple columns equally, consider z-ordering (interleaved sorting). Available in Delta Lake, Iceberg, and some Spark configurations.

## Column projection

Always project only needed columns. On remote files (S3/HTTP), this is the single biggest performance lever: a 100-column file where you SELECT 3 columns reads ~3% of the data. Combined with predicate pushdown, you may read <1%.

## Statistics limitations

Understanding when statistics-based optimizations fail.

### When min/max statistics don't help

| Scenario | Why statistics fail |
|----------|---------------------|
| Random data order | Every row group overlaps |
| String prefix patterns | `LIKE 'A%'` can't use min/max well |
| Functions on columns | `year(date) = 2024` doesn't push down |
| OR conditions | Complex predicates may not prune |
| Nulls mixed throughout | Null stats don't help with value predicates |

### Checking statistics effectiveness

```sql
-- DuckDB: Compare planned vs actual
EXPLAIN ANALYZE SELECT count(*) FROM data WHERE condition;

-- If "Rows scanned" >> "Rows returned", statistics aren't helping
```

### Workarounds

1. **Sort data** before writing to improve statistics clustering
2. **Add bloom filters** for high-cardinality equality predicates
3. **Partition data** by low-cardinality filter columns
4. **Rewrite predicates** to be pushdown-friendly:

```sql
-- Bad: can't push down
WHERE extract(year from date_col) = 2024

-- Good: pushes down
WHERE date_col >= '2024-01-01' AND date_col < '2025-01-01'
```
