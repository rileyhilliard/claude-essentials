---
name: writing-sql
description: Trains Claude to write SQL at Staff+ DBA level by targeting the non-obvious patterns Claude's defaults miss. Covers multi-column statistics for correlated predicates, operator class selection for index usage, aggregate FILTER patterns, keyset pagination, and the query anti-patterns that silently destroy production performance. Use when writing complex SQL, reviewing a query for correctness or performance, adding indexes, or optimizing a slow query.
---

# Writing SQL

**Core principle:** Every query you write has an execution plan. Write SQL with that plan in mind, not just the result.

This skill covers only what Claude's defaults miss. Topics already handled by `managing-databases/postgres-querying.md` (LATERAL, CTE materialization, DISTINCT ON, EXPLAIN red flags, ROWS vs RANGE) are not repeated here.

## Topic Navigation

| Task | Load |
|------|------|
| Planner picking bad plans on multi-column WHERE | [extended-statistics.md](references/extended-statistics.md) |
| LIKE search not using index, text pattern matching | [index-internals.md](references/index-internals.md) |
| Composite index column ordering, INCLUDE clause | [index-internals.md](references/index-internals.md) |
| Type mismatch between param and column silently bypassing index | [index-internals.md](references/index-internals.md) |
| Conditional aggregation, pivot queries, subtotals | [aggregation-patterns.md](references/aggregation-patterns.md) |
| GROUPING SETS, ROLLUP, CUBE | [aggregation-patterns.md](references/aggregation-patterns.md) |
| NULL edge cases in aggregates and window functions | [aggregation-patterns.md](references/aggregation-patterns.md) |
| Paginating large result sets | [query-anti-patterns.md](references/query-anti-patterns.md) |
| NOT IN returning zero rows unexpectedly | [query-anti-patterns.md](references/query-anti-patterns.md) |
| DISTINCT added to fix duplicate rows | [query-anti-patterns.md](references/query-anti-patterns.md) |
| Correlated subqueries in SELECT list | [query-anti-patterns.md](references/query-anti-patterns.md) |
| Functions in WHERE bypassing indexes | [query-anti-patterns.md](references/query-anti-patterns.md) |

## Iron Rules

These apply to every query, no exceptions:

- **Never paginate with OFFSET on large tables.** Use keyset pagination.
- **Never use NOT IN when the subquery column is nullable.** Use NOT EXISTS.
- **Always match parameter types to column types exactly.** Implicit casts bypass indexes.
- **Replace CASE WHEN inside aggregates with FILTER.** It's cleaner and semantically correct.
- **When a multi-column WHERE produces bad estimates, add extended statistics before adding hints or rewrites.**
