# PostgreSQL Architecture & Maintenance

Non-obvious configuration, maintenance gotchas, and operational patterns for PostgreSQL.

## Contents

- Partitioning decisions
- Indexing gotchas
- VACUUM and autovacuum tuning
- work_mem traps
- Bloat management

## Partitioning decisions

### When to partition

| Condition | Partition? | Why |
|-----------|------------|-----|
| Table >100M rows | Yes | Partition pruning cuts scan scope |
| Time-based retention (delete old data) | Yes | Drop partition instead of DELETE (instant, no bloat) |
| Queries always filter by a specific column | Yes | Pruning eliminates irrelevant partitions |
| Table <10M rows | No | Planning overhead outweighs pruning benefit |
| Queries scan full table anyway | No | No pruning opportunity |

### Partition count guidelines

- Aim for dozens to low hundreds of partitions
- Each partition should have >10,000 rows
- Too many partitions = planning overhead (query planner evaluates every partition)
- Too few = no pruning benefit

### Automate with pg_partman

Manual partition creation is error-prone. Forgetting to create next month's partition causes insert failures.

```sql
SELECT partman.create_parent(
    p_parent_table := 'public.events',
    p_control := 'created_at',
    p_type := 'native',
    p_interval := 'monthly',
    p_premake := 3  -- Create 3 future partitions
);
```

## Indexing gotchas

### Partial indexes (the most underused PostgreSQL feature)

Index only the rows you actually query. Dramatically smaller, faster, and cheaper to maintain than full indexes.

```sql
-- Only index active users (if 90% of queries filter on active)
CREATE INDEX idx_users_active_email ON users(email)
    WHERE status = 'active';

-- Only index recent data (if old data is rarely queried)
CREATE INDEX idx_events_recent ON events(type)
    WHERE created_at > '2024-01-01';
```

Claude tends to generate full indexes by default. Partial indexes should be the first consideration when the query workload consistently filters on a specific condition.

### Covering indexes avoid heap lookups

```sql
-- INCLUDE adds columns to leaf pages without affecting index ordering
CREATE INDEX idx_orders_user ON orders(user_id)
    INCLUDE (status, total);

-- This query becomes an index-only scan (no table heap access)
SELECT status, total FROM orders WHERE user_id = 123;
```

The gotcha: index-only scans require a recently vacuumed table (visibility map must be current). High heap fetches in `EXPLAIN ANALYZE` means you need to vacuum.

### Finding wasted indexes

Unused indexes slow writes and waste storage. Check periodically:

```sql
-- Find indexes that have never been scanned
SELECT schemaname, relname, indexrelname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0 AND indexrelname NOT LIKE '%_pkey';

-- Find duplicate indexes (same columns, different names)
SELECT pg_size_pretty(sum(pg_relation_size(idx))::bigint) as size,
       (array_agg(idx))[1] as idx1, (array_agg(idx))[2] as idx2
FROM (SELECT indexrelid::regclass as idx, indrelid, indkey
      FROM pg_index) sub
GROUP BY indrelid, indkey HAVING count(*) > 1;
```

## VACUUM and autovacuum tuning

### The default autovacuum threshold trap

Default autovacuum triggers at 20% dead tuples. On a 100M row table, that means 20M dead tuples before autovacuum kicks in. This causes massive bloat on large, high-churn tables.

```sql
-- Fix: aggressive autovacuum on hot tables
ALTER TABLE events SET (
    autovacuum_vacuum_scale_factor = 0.02,  -- Vacuum at 2% dead (vs 20% default)
    autovacuum_analyze_scale_factor = 0.01, -- Analyze at 1% change
    autovacuum_vacuum_cost_limit = 1000     -- Work harder per run
);
```

### Checking if autovacuum is keeping up

```sql
SELECT relname, n_dead_tup, last_vacuum, last_autovacuum
FROM pg_stat_user_tables
WHERE n_dead_tup > 10000
ORDER BY n_dead_tup DESC;
```

If `n_dead_tup` is consistently high and `last_autovacuum` is recent, autovacuum is running but not keeping up. Increase `autovacuum_vacuum_cost_limit` or decrease the scale factor.

## work_mem traps

### Per-operation, not per-query

`work_mem` is allocated **per sort/hash operation**, not per query. A complex query with 10 sorts uses 10x `work_mem`. Setting it to 256MB globally with 100 concurrent connections could use 256GB of RAM in the worst case.

### Detecting disk spills

```sql
EXPLAIN (ANALYZE, BUFFERS) SELECT ... ORDER BY ...;
-- Look for "Sort Method: external merge" = sort spilled to disk
-- "Sort Method: quicksort" = fits in memory
```

### Safe pattern: set per-session, not globally

```sql
-- Global: keep conservative (32-64MB)
-- Per-session for heavy analytical queries:
SET work_mem = '256MB';
-- Runs your big query
RESET work_mem;
```

## Bloat management

### VACUUM FULL gotchas

VACUUM FULL rewrites the entire table. Two things people don't expect:

1. **Locks the table for the entire duration.** No reads, no writes. On a 500GB table, this can be hours.
2. **Requires free disk space equal to the table size.** A 500GB bloated table needs 500GB free space to VACUUM FULL.

### Better alternatives

| Method | Locks? | Disk space needed | Speed |
|--------|--------|-------------------|-------|
| `VACUUM FULL` | Full table lock | Equal to table size | Slow |
| `pg_repack` | No (online) | Equal to table size | Moderate |
| Create new table + swap | Brief lock at swap | Equal to table size | Fast for extreme cases |

```bash
# pg_repack: online, no locks, preferred method
pg_repack -d mydb -t events
```

### Detecting bloat

```sql
SELECT schemaname, relname,
    pg_size_pretty(pg_total_relation_size(relid)) as total_size,
    n_dead_tup,
    round(100.0 * n_dead_tup / nullif(n_live_tup + n_dead_tup, 0), 1) as dead_pct
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC;
```

Dead tuple percentage above 20% is a strong signal for bloat. Above 50% means autovacuum has fallen behind significantly.
