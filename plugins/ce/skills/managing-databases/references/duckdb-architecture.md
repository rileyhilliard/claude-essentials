# DuckDB Architecture

Non-obvious constraints and configuration for DuckDB in production systems.

## Contents

- Workload boundaries
- Concurrency model
- Thread configuration traps
- Out-of-core processing
- pg_duckdb integration

## Workload boundaries

### Where DuckDB excels vs where it doesn't

| Workload | DuckDB | Why |
|----------|--------|-----|
| Full table aggregations | Excellent | Columnar + vectorized = 10-1000x vs row stores |
| Column subset scans | Excellent | Only reads needed columns |
| Filter + aggregate | Excellent | Predicate pushdown + vectorized filtering |
| Single row lookup by ID | Poor | No row-level index seek. Use PostgreSQL |
| Many small transactions | Poor | Optimized for analytical batch, not OLTP |
| Heavy updates/deletes | Poor | Append-oriented storage. UPDATE rewrites segments |

The most common mistake is trying to use DuckDB for OLTP-style workloads. If your queries are mostly point lookups or single-row updates, stay in PostgreSQL.

## Concurrency model

**This is the most critical constraint to understand when designing systems with DuckDB.**

DuckDB is single-writer, multiple-reader.

| Operation | Concurrent access |
|-----------|------------------|
| Multiple readers | Yes (with `read_only=True`) |
| Single writer | Yes |
| Multiple writers | No (will fail or corrupt data) |

### Why this matters for system design

If you design a system expecting DuckDB to handle concurrent writes like PostgreSQL, you'll hit lock contention errors or data corruption. There's no warning before corruption in some edge cases.

```python
# Safe: Multiple processes can read
conn = duckdb.connect('db.duckdb', read_only=True)

# Dangerous: Only ONE process should write
conn = duckdb.connect('db.duckdb')  # Exclusive write lock
```

### The standard hybrid pattern

- PostgreSQL handles writes, metadata, and OLTP
- DuckDB reads Parquet files for analytics
- No concurrent write contention because DuckDB never writes

### In-process gotcha

DuckDB runs in-process (embedded). Each Python process gets its own DuckDB instance. Two processes opening the same `.duckdb` file for writing will conflict, and the error messages aren't always clear about what went wrong.

## Thread configuration traps

### Default is usually correct

DuckDB automatically uses all available CPU cores. Don't tune this unless you have a specific reason.

### Remote data: increase threads beyond CPU count

For queries over HTTP/S3 (Parquet files on remote storage), threads spend most of their time waiting for network I/O. More threads = more concurrent requests = better bandwidth utilization.

```sql
-- Network-bound: more threads than cores is correct
SET threads = 32;  -- Even on an 8-core machine

-- CPU-bound (local data): leave at default or match cores
SET threads = 8;
```

### Resource-constrained environments

When DuckDB runs alongside other services:

```sql
SET threads = 2;  -- Limit CPU usage
SET memory_limit = '2GB';  -- Limit memory
```

Without memory limits, DuckDB will happily use all available RAM for hash tables and sorts, starving other processes.

## Out-of-core processing

DuckDB handles datasets larger than RAM by spilling to disk. This is automatic but has gotchas.

### Temp directory matters

Spilling goes to the system temp directory by default. On servers with small `/tmp` partitions, this silently fails when disk fills up.

```sql
-- Point to a fast SSD with enough space
SET temp_directory = '/path/to/fast/ssd/duckdb_temp';
```

### Memory limits and spilling behavior

```sql
-- Set explicit memory limit
SET memory_limit = '8GB';

-- Monitor memory usage during a query
SELECT * FROM duckdb_memory();
```

When memory limit is hit, DuckDB spills hash tables and sorts to disk. Performance degrades gracefully but can be 10-100x slower for hash joins that don't fit in memory. If a query is unexpectedly slow, check if it's spilling.

## pg_duckdb integration

Run DuckDB's analytical engine inside PostgreSQL. Avoid data movement for mixed OLTP/analytics workloads.

### When pg_duckdb is the right call

| Scenario | Use pg_duckdb? |
|----------|---------------|
| Analytical queries on existing PostgreSQL tables | Yes (avoids data export) |
| Query Parquet/CSV from within PostgreSQL | Yes |
| Simple OLTP queries (lookups, inserts) | No (PostgreSQL is faster) |
| Queries using PostgreSQL-specific features (CTEs, lateral joins) | No (may not be supported) |
| Need DuckDB-specific SQL extensions | Check compatibility |

### Gotchas

- Not all PostgreSQL features are supported in the DuckDB execution path
- Write operations always go through PostgreSQL regardless of the setting
- Some type conversions between PostgreSQL and DuckDB types may produce unexpected results (especially for timestamps and numeric precision)
- `SET duckdb.execution = true` routes *supported* queries to DuckDB. If a query isn't supported, it silently falls back to PostgreSQL with no indication

```sql
-- Enable DuckDB execution for analytical queries
SET duckdb.execution = true;

-- This may or may not use DuckDB depending on query features
SELECT region, sum(sales) FROM orders GROUP BY region;

-- Query external Parquet directly from PostgreSQL
SELECT * FROM read_parquet('s3://bucket/data/*.parquet');
```
