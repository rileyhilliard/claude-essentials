# Neo4j Cypher Querying & Optimization

Non-obvious query patterns and optimization gotchas for Cypher on Neo4j.

## Contents

- Reading execution plans
- Cardinality management
- Variable-length path gotchas
- Batching large writes
- shortestPath limitations
- Composite index predicate rules
- UNWIND ordering traps
- Anti-patterns that silently kill performance
- Data modeling anti-patterns

## Reading execution plans

Use `PROFILE` (not `EXPLAIN`) when actively optimizing. `EXPLAIN` estimates; `PROFILE` shows real numbers.

Read bottom-up, starting from the lowest operator.

**Red flags in PROFILE output:**

| Signal | Problem | Fix |
|--------|---------|-----|
| `AllNodesScan` | Scanning every node in the database | Add label to MATCH, create index on filtered property |
| `NodeByLabelScan` on a filtered property | Full label scan despite having a WHERE clause | Create Range index on that property |
| `CartesianProduct` | Cross-joining disconnected MATCH patterns | Connect patterns with a relationship or use WITH |
| Large gap between estimated and actual rows | Stale statistics or bad cardinality estimate | Indicates the planner chose a bad strategy |
| DB Hits orders of magnitude higher than rows returned | Touching far more data than needed | Restructure query to filter earlier |
| `Eager` operator in a write query | Entire result set materialized before writing begins | Can cause OOM on large datasets. Use `CALL {} IN TRANSACTIONS` |

## Cardinality management

Cardinality explosions are the most common Cypher performance killer and the one Claude is most likely to generate naively. Row counts multiply at each traversal hop, and without explicit control, a 3-hop query can go from 1,000 starting rows to millions of intermediate rows.

### Aggregate early with WITH/COLLECT

```cypher
// Naive: row count multiplies at each hop
MATCH (a:Person)-[:KNOWS]->(b)-[:KNOWS]->(c)-[:KNOWS]->(d)
RETURN a.name, d.name

// Controlled: aggregate between stages to collapse rows
MATCH (a:Person)-[:KNOWS]->(b)
WITH a, collect(b) AS friends
UNWIND friends AS b
MATCH (b)-[:KNOWS]->(c)
WITH a, collect(DISTINCT c) AS fof
RETURN a.name, size(fof)
```

### Pattern comprehensions keep cardinality flat

Pattern comprehensions populate lists without expanding rows. Use them when you need related data but don't want to multiply your result set.

```cypher
// Instead of a JOIN-style expansion:
MATCH (p:Person)
RETURN p.name,
       [(p)-[:ACTED_IN]->(m:Movie) | m.title] AS movies,
       [(p)-[:DIRECTED]->(m:Movie) | m.title] AS directed
```

### Apply LIMIT before expensive operations

```cypher
// Bad: traverses everything, then limits
MATCH (a:Person)-[:KNOWS*1..4]->(b:Person)
RETURN DISTINCT b.name LIMIT 10

// Good: limit the starting set first
MATCH (a:Person) WHERE a.name = $name
WITH a LIMIT 1
MATCH (a)-[:KNOWS*1..4]->(b:Person)
RETURN DISTINCT b.name LIMIT 10
```

## Variable-length path gotchas

### Always bound the upper limit

```cypher
// Can traverse the entire graph
MATCH path = (a)-[*]->(b) RETURN path

// Bounded: predictable performance
MATCH path = (a)-[*1..5]->(b) RETURN path
```

### Relationship uniqueness within a single path only

Neo4j guarantees each relationship appears at most once **per path**, not globally across all matched paths. Two different result paths can share the same relationship. This matters for algorithms where you expect global uniqueness.

### Filtering within variable-length patterns

```cypher
// Filter relationships inside the pattern (Neo4j 5+)
MATCH path = (a)-[:KNOWS*1..5 {active: true}]->(b)
RETURN path

// Filter intermediate nodes requires a different approach
MATCH path = (a)-[:KNOWS*1..5]->(b)
WHERE ALL(n IN nodes(path) WHERE n.status = 'active')
RETURN path
// Warning: the ALL() predicate runs AFTER path expansion, not during.
// On large graphs this can be very slow.
```

## Batching large writes

`CALL {} IN TRANSACTIONS` prevents OOM on bulk operations by committing in batches. Without it, Neo4j holds the entire transaction in memory.

```cypher
// Batch update 1 million nodes in chunks of 10,000
MATCH (p:Person) WHERE p.needsUpdate = true
CALL (p) {
  SET p.updated = true, p.needsUpdate = false
} IN TRANSACTIONS OF 10000 ROWS
```

### Gotchas with batched transactions

- Each batch is a separate transaction. If batch 500 fails, batches 1-499 are already committed. Your operation is now partially applied.
- Variables from the outer query must be explicitly passed into the `CALL` block.
- `RETURN` inside the inner block aggregates across all batches, which can still accumulate memory. Use `RETURN` sparingly or redirect output.

## shortestPath limitations

`shortestPath()` is not always the right tool, even when you want the shortest path.

| Situation | Use `shortestPath()`? | Why |
|-----------|----------------------|-----|
| Simple shortest path between two nodes | Yes | Built-in BFS, optimized |
| Shortest path with intermediate node filters | Maybe | `WHERE` on path nodes runs after BFS, may miss valid paths |
| Weighted shortest path (costs on relationships) | No | `shortestPath` ignores weights. Use APOC `apoc.algo.dijkstra` or GDS |
| All shortest paths | Use `allShortestPaths()` | Returns all paths of minimum length |
| Shortest path with relationship property constraints | Careful | Filters on relationship properties inside the pattern work, but node filters in WHERE may not |

```cypher
// This LOOKS correct but can return wrong results:
MATCH path = shortestPath((a:Person {name: 'Alice'})-[*..10]-(b:Person {name: 'Bob'}))
WHERE ALL(n IN nodes(path) WHERE n.status = 'active')
RETURN path
// The WHERE runs AFTER finding shortest path. If the actual shortest path
// has an inactive node, you get no result (not the next-shortest valid path).
```

## Composite index predicate rules

Composite indexes have strict, non-obvious requirements that cause silent fallback to label scans.

For a composite index on `(name, born)`:

| Query predicates | Uses composite index? | Why |
|------------------|----------------------|-----|
| `name = X AND born = Y` | Yes | Full match |
| `name = X AND born > Y` | Yes | Equality + range |
| `name STARTS WITH X AND born = Y` | Partial | born degrades to existence check after prefix |
| `born = Y` only | No | Must include first property |
| `name = X` only | Partial | Seeks on name, ignores born |

The silent fallback is the dangerous part. No error, just slower queries. Always `PROFILE` after creating composite indexes to verify they're activating.

## UNWIND ordering traps

`UNWIND` doesn't guarantee ordering. If you need deterministic order from an unwound list, add explicit `ORDER BY`.

```cypher
// Order is NOT guaranteed to match the input list
WITH ['c', 'a', 'b'] AS items
UNWIND items AS item
MATCH (n:Node {name: item})
RETURN n.name
// May return in any order

// Fix: add explicit ordering
WITH ['c', 'a', 'b'] AS items
UNWIND items AS item
WITH item, apoc.coll.indexOf(['c', 'a', 'b'], item) AS idx
MATCH (n:Node {name: item})
RETURN n.name ORDER BY idx
```

### UNWIND on large lists and cardinality

`UNWIND` expands a list into rows. If you UNWIND a 10,000-element list and then MATCH against each element, you get 10,000 rows flowing through the rest of the query. On large lists, batch with `CALL {} IN TRANSACTIONS` to avoid memory pressure.

## Anti-patterns that silently kill performance

These patterns don't error out. They just make queries 10-1000x slower than they should be.

### Missing parameters (plan cache thrashing)

```cypher
// Every unique string value creates a new execution plan
MATCH (p:Person {name: 'Tom Hanks'}) RETURN p

// Parameters allow plan reuse across all invocations
MATCH (p:Person {name: $name}) RETURN p
```

Neo4j caches a limited number of execution plans. Literal values pollute the cache and force constant replanning.

### Cartesian products from disconnected patterns

```cypher
// Silent cartesian product: N * M rows
MATCH (a:Person), (b:Movie)
WHERE a.name = 'Tom' AND b.title = 'Forrest Gump'
RETURN a, b

// Fix: connect the patterns
MATCH (a:Person)-[:ACTED_IN]->(b:Movie)
WHERE a.name = 'Tom' AND b.title = 'Forrest Gump'
RETURN a, b
```

PROFILE will show a `CartesianProduct` operator. If you intentionally need a cross product, use `CROSS JOIN` syntax (Neo4j 5.21+) to signal intent.

### Token Lookup index deletion

The default Token Lookup indexes (for labels and relationship types) exist on every Neo4j database. Deleting them causes all queries to degrade to `AllNodesScan`. There's no warning when you delete them. Recreate with:

```cypher
CREATE LOOKUP INDEX node_label_lookup_index FOR (n) ON EACH labels(n)
CREATE LOOKUP INDEX rel_type_lookup_index FOR ()-[r]-() ON EACH type(r)
```

## Data modeling anti-patterns

### Relational join-table thinking

Don't create intermediate nodes that only exist to mimic foreign-key join tables. Direct relationships are the whole point.

```cypher
// Anti-pattern: relational join table
(:Person)-[:HAS_ORDER]->(:PersonOrder)-[:FOR_PRODUCT]->(:Product)

// Graph-native
(:Person)-[:ORDERED]->(:Product)
```

The exception: when the "join" itself has meaningful properties, timestamps, or connects to other entities. Then it's a legitimate intermediary node (see neo4j-architecture.md).

### Generic relationship types on high-degree nodes

Using broad types like `:RELATES_TO` or `:CONNECTED` forces Neo4j to scan all relationships when traversing. Specific types let the engine filter at the storage level.

```cypher
// Supernode trap: 5 million generic relationships
(:User)-[:INTERACTED_WITH]->(:Content)

// Specific types: engine filters before scanning
(:User)-[:LIKED]->(:Content)
(:User)-[:SHARED]->(:Content)
(:User)-[:COMMENTED_ON]->(:Content)
```

This becomes critical at scale. A node with 1M generic relationships scanned on every traversal vs. 3 specific types where only the relevant subset is scanned.
