---
name: managing-databases
description: Database architecture and SQL guidance for PostgreSQL, DuckDB, Parquet, PGVector, and Neo4j. Use when designing schemas, choosing a storage engine, writing or reviewing non-trivial SQL, adding indexes, tuning slow queries, or configuring vector and graph workloads.
---

# Managing Databases

Decision guidance for hybrid storage: PostgreSQL for transactional metadata, DuckDB over Parquet for analytics, PGVector for similarity search, Neo4j for relationship-heavy queries.

## Which engine

| Workload | Use | Why |
| --- | --- | --- |
| Transactional CRUD, users, sessions, metadata with foreign keys | PostgreSQL | ACID, row locking, constraints |
| Aggregations, scans, ad-hoc exploration | DuckDB on Parquet | Columnar, vectorized, no ETL |
| Analytical storage and interchange | Parquet | Compressed, columnar, portable |
| Time series with point lookups | PostgreSQL + partitioning | Partition pruning plus indexes |
| Time series analytics | DuckDB on Parquet | Scan performance |
| Similarity search, RAG, hybrid keyword + vector | PostgreSQL + PGVector | Embeddings next to metadata |
| Multi-hop traversal, path finding, knowledge graphs | Neo4j | Index-free adjacency |

## References

| Working on | Read |
| --- | --- |
| Postgres partitioning, autovacuum, maintenance | [references/postgres-architecture.md](references/postgres-architecture.md) |
| LATERAL, CTE materialization, DISTINCT ON, EXPLAIN red flags | [references/postgres-querying.md](references/postgres-querying.md) |
| Planner misestimates on multi-column WHERE | [references/postgres-extended-statistics.md](references/postgres-extended-statistics.md) |
| LIKE not using an index, composite index order, INCLUDE, param/column type mismatch | [references/postgres-index-internals.md](references/postgres-index-internals.md) |
| FILTER, GROUPING SETS/ROLLUP/CUBE, NULLs in aggregates and windows | [references/sql-aggregation-patterns.md](references/sql-aggregation-patterns.md) |
| Pagination, NOT IN, DISTINCT-as-a-fix, correlated subqueries, functions in WHERE | [references/sql-query-anti-patterns.md](references/sql-query-anti-patterns.md) |
| DuckDB storage, threads, memory | [references/duckdb-architecture.md](references/duckdb-architecture.md) |
| DuckDB-specific SQL | [references/duckdb-querying.md](references/duckdb-querying.md) |
| Parquet file sizing, partitioning, sort order | [references/parquet-architecture.md](references/parquet-architecture.md) |
| Parquet predicate pushdown and query tuning | [references/parquet-querying.md](references/parquet-querying.md) |
| HNSW vs IVFFlat, index parameters | [references/pgvector-architecture.md](references/pgvector-architecture.md) |
| Filtered and hybrid vector search | [references/pgvector-querying.md](references/pgvector-querying.md) |
| Graph modeling, indexes, supernodes | [references/neo4j-architecture.md](references/neo4j-architecture.md) |
| Cypher tuning and anti-patterns | [references/neo4j-querying.md](references/neo4j-querying.md) |

## SQL defaults

These hold for any query against a large table:

- Paginate with a keyset (`WHERE (created_at, id) < ($1, $2)`), not `OFFSET`.
- Use `NOT EXISTS` when the subquery column is nullable. `NOT IN` returns zero rows if any value is NULL.
- Match parameter types to column types. An implicit cast on the column side skips the index.
- Write conditional aggregates with `FILTER (WHERE ...)` rather than `CASE WHEN` inside `SUM`.
- When a multi-column `WHERE` gets bad row estimates, add extended statistics before rewriting the query.

## Engine defaults

- Postgres: partition tables past ~100M rows or with retention rules; index the columns in `WHERE` and `JOIN`, not everything; tune autovacuum on high-churn tables.
- DuckDB: read Parquet, not CSV; let it parallelize; raise threads above core count for remote reads.
- Parquet: 128MB to 1GB files; partition on low-to-moderate cardinality columns; sort by the columns you filter on.
- PGVector: HNSW by default, IVFFlat when memory-bound or batch-loaded; enable iterative scan for filtered queries.
- Neo4j: model around the queries; bound every variable-length path (`[*1..5]`); pass parameters so plans cache.

## Slow query triage

- Postgres: `EXPLAIN (ANALYZE, BUFFERS)`. Look for seq scans on large tables, missing filter/join indexes, dead-tuple bloat in `pg_stat_user_tables`, and disk sorts that point at `work_mem`.
- DuckDB: CSV instead of Parquet, `SELECT *` over remote data, thread count, needless casts.
- Parquet: check the plan for pushdown, file sizes, sort order, and partition keys with too many small files.
- PGVector: confirm the index is used, then check `ef_search` or `probes`, iterative scan, and IVFFlat recall after heavy updates.
- Neo4j: `PROFILE` and read bottom-up. `AllNodesScan` or `NodeByLabelScan` means a missing index; `CartesianProduct` means disconnected patterns; watch `page_cache.hit_ratio` below 98%.
