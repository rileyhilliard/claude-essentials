# Neo4j Architecture & Maintenance

Non-obvious configuration, data modeling, and maintenance patterns for Neo4j graph databases.

## Contents

- Data modeling decisions
- Schema and constraints
- Index gotchas
- Memory configuration
- Supernode mitigation
- Transaction management
- Clustering and scaling
- Backup strategy
- Monitoring

## Data modeling decisions

### When to promote a property to a node

This is the most impactful modeling decision and the one most likely to be wrong on first pass.

A property should become a node when:

- You filter on it during traversals (a `city` property on Person should become a `City` node if you query "find all people in the same city")
- Multiple nodes share the same value and you want to traverse through it
- You need to attach additional properties or relationships to it

A property should stay a property when:

- It's only used for display or returned in results
- It's unique per node (no traversal benefit)
- It changes frequently (node creation/deletion is more expensive than property updates)

### Label design gotchas

Labels serve as query entry points and affect planner decisions.

| Decision | Recommendation | Why |
|----------|---------------|-----|
| Labels vs properties for state | Labels for stable categories (`:Premium`, `:Verified`), properties for volatile state (`status: 'active'`) | Label changes are more expensive than property updates, but the planner uses labels for filtering |
| Multiple labels | Use for genuine type hierarchy (`(:Person:Employee:Manager)`) | Each node has ~4 pre-allocated label slots. Beyond that, storage overhead increases |
| Dynamic labels from data | Avoid creating labels from user input or high-cardinality data | Each unique label adds planning overhead. Thousands of labels degrades query planning |

### Intermediary node pattern

When a relationship accumulates complex data or connects more than two entities, factor it into a node.

```cypher
// Before: overloaded relationship
(Person)-[:WORKED_AT {role, startDate, endDate, department}]->(Company)

// After: intermediary node
(Person)-[:HAD_ROLE]->(Employment)-[:AT]->(Company)
// Employment node holds role, startDate, endDate, department
```

The trigger: if you want to **index** relationship properties (standard indexes don't cover them) or if a relationship connects more than two entities.

## Schema and constraints

### Community vs Enterprise constraint strategy

| Constraint | Community | Enterprise |
|------------|-----------|------------|
| Property Uniqueness | Yes (creates backing index automatically) | Yes |
| Property Existence | No. Use application-level validation | Yes |
| Property Type | No. Use application-level validation | Yes |
| Node Key (uniqueness + existence) | No | Yes (creates backing index) |

The key insight for Community Edition: uniqueness constraints are your only schema enforcement tool, but they also create indexes. This means your constraint strategy and your indexing strategy are coupled. Plan accordingly.

### Constraint-index coupling

Uniqueness and Node Key constraints automatically create backing indexes. This means:

- Don't create a separate index on the same property (you'll have a duplicate)
- Dropping the constraint drops the backing index too
- If you need the index but not the constraint, you need to create the index separately after dropping the constraint

## Index gotchas

### Token Lookup indexes (never delete)

Every Neo4j database has two default Token Lookup indexes for labels and relationship types. Deleting them causes **all** queries to degrade to `AllNodesScan`. No warning, no error, just every query becomes a full scan.

```cypher
-- If accidentally deleted, recreate immediately:
CREATE LOOKUP INDEX node_label_lookup_index FOR (n) ON EACH labels(n)
CREATE LOOKUP INDEX rel_type_lookup_index FOR ()-[r]-() ON EACH type(r)
```

### Index type selection (Neo4j 5+)

B-tree indexes from Neo4j 4.x no longer exist. The replacements:

| Old (4.x) | New (5+) | Gotcha |
|-----------|---------|--------|
| B-tree | Range | Range indexes cap at ~8 KB key size. Longer strings silently don't index. |
| B-tree for strings | Text | Required for `CONTAINS` and `ENDS WITH`. Range index won't activate for these. |
| N/A | Point | Only for spatial distance/bounding box queries |
| Full-Text (Lucene) | Full-Text | Still the only index type that works on **relationship** properties |

### Composite index activation rules

Composite indexes fail silently (fall back to label scan) when predicates don't meet strict requirements:

- Query must filter on **all** properties for the index to activate
- Equality/list membership predicates must target the **first-defined properties**
- Maximum **one** range/prefix search predicate per composite query
- Predicates after a prefix search degrade to existence checks

Always `PROFILE` after creating composite indexes to verify they're being used.

### Write cost of indexes

Each index roughly doubles storage for indexed data and slows writes. On write-heavy workloads, be selective. A table with 10 indexes updates all 10 on every write.

Monitor unused indexes:

```cypher
SHOW INDEX YIELD name, lastRead, readCount
-- lastRead = null means the index has never been used
```

## Memory configuration

### Three memory pools

| Pool | Setting | Purpose | Sizing |
|------|---------|---------|--------|
| Heap | `server.memory.heap.initial_size` / `max_size` | Java objects, query state, transactions | Set initial = max to avoid GC resize pauses |
| Page Cache | `server.memory.pagecache.size` | Caches graph data + indexes from disk | Store size + expected growth + 10% |
| Transaction | `dbms.memory.transaction.total.max` | Uncommitted data, results, intermediate state | Depends on workload |

**Formula:** `Total Physical Memory = Heap + Page Cache + OS Reserve (1-2 GB)`

| Total RAM | Heap | Page Cache |
|-----------|------|------------|
| 16 GB | 5 GB | 7-9 GB |
| 32 GB | 8 GB | 20 GB |
| 64 GB | 16 GB | 44 GB |

Page cache hit ratio below 98% means your store doesn't fit in memory. Either add RAM or accept disk I/O latency.

```bash
# Let Neo4j calculate recommendations
neo4j-admin server memory-recommendation --memory=16g
```

## Supernode mitigation

Nodes with millions of relationships are the most common Neo4j performance trap at scale. Every traversal through a supernode scans all its relationships.

### Fan-out node pattern

The most effective mitigation for known supernodes. Distribute connections through intermediate bucket nodes.

```cypher
// Before: celebrity with 5M followers (supernode)
(:User)-[:FOLLOWS]->(:Celebrity)

// After: fan-out through date-based buckets
(:User)-[:FOLLOWS]->(:FollowBucket {month: '2026-01'})-[:BUCKET_OF]->(:Celebrity)

// Query "does Alice follow Bob?" still works:
MATCH (alice:User {name: 'Alice'})-[:FOLLOWS]->(bucket)-[:BUCKET_OF]->(bob:Celebrity {name: 'Bob'})
RETURN count(*) > 0 AS follows
```

### Other strategies

| Strategy | When to use |
|----------|------------|
| Specific relationship types | `LIKED`, `SHARED`, `COMMENTED_ON` instead of generic `INTERACTED_WITH`. Lets engine filter at storage level |
| Query direction | Traverse from the less-connected end. `MATCH (user)-[:FOLLOWS]->(celebrity)` is faster starting from user |
| Relationship property filters | Narrow scope before scanning: `WHERE r.since > date('2025-01-01')` |

## Transaction management

### Auto-commit vs explicit transactions

| Mode | Use when | Gotcha |
|------|----------|--------|
| Auto-commit (implicit) | Simple single-statement queries | Each statement is its own transaction. Multi-statement scripts aren't atomic |
| Explicit (`BEGIN`/`COMMIT`) | Multi-statement operations that must be atomic | Holding transactions open too long blocks other operations |
| Transaction functions (driver) | Application code | Automatic retry on transient errors (leader changes, deadlocks). Always prefer this in application code |

### Bulk operations and memory

Without batching, Neo4j holds the entire write operation in memory until commit. A `FOREACH` or `UNWIND` over 1M items in a single transaction will likely OOM.

```cypher
// OOM risk: single transaction for 1M updates
MATCH (p:Person) WHERE p.needsUpdate = true
SET p.updated = true

// Safe: batch in chunks
MATCH (p:Person) WHERE p.needsUpdate = true
CALL (p) {
  SET p.updated = true
} IN TRANSACTIONS OF 10000 ROWS
```

**Partial failure risk:** Each batch commits independently. If batch 500 fails, batches 1-499 are already committed. Design for idempotent operations or add tracking properties.

## Clustering and scaling

### Write scaling limitation

Neo4j does not support horizontal write sharding. All writes go to a single primary cluster. This is the most important architectural constraint to understand early.

For write-heavy workloads:

- Scale vertically (bigger machine)
- Application-level partitioning (separate databases for independent subgraphs)
- Batch writes and reduce transaction frequency

### Primary-Secondary architecture

**Fault tolerance formula:** `M = 2F + 1` (M = primaries, F = tolerated failures)

| Primaries | Tolerates | Notes |
|-----------|-----------|-------|
| 3 | 1 failure | Minimum for HA |
| 5 | 2 failures | Production recommended |
| 9 | 4 failures | Max recommended (more adds write latency) |

Secondaries replicate asynchronously. Scale reads up to 20 secondaries. They don't participate in consensus, so reads may lag behind writes.

### Causal consistency via bookmarks

Clients receive **bookmarks** after write transactions. Subsequent reads present the bookmark to ensure the server has data at least as fresh as the write. This is the mechanism that guarantees read-your-own-writes across different servers.

Without bookmarks, a write to the primary followed by a read from a secondary can return stale data. Always use bookmarks in application code when consistency matters.

## Backup strategy

### What to back up

- All databases individually (including `system` database for security config)
- `neo4j.conf` configuration files
- SSL/TLS certificates and keys
- Custom plugins and license files

### Full vs incremental

`neo4j-admin` auto-detects whether to do full or incremental based on existing backup artifacts. Incremental captures changes since last backup. Periodically run aggregate to combine incrementals and speed up restore time.

### Point-in-time restore

```bash
neo4j-admin database restore --restore-until="2026-02-22T10:00:00Z" ...
```

Store backups on separate servers or different availability zones. Test recovery routines regularly.

## Monitoring

### Key metrics

| Category | Metric | Target |
|----------|--------|--------|
| Page Cache | `page_cache.hit_ratio` | 98-100% (below = store doesn't fit in memory) |
| Page Cache | `page_cache.usage_ratio` | <100% (100% = out of cache space) |
| Transactions | `transaction.active` | Stable baseline (spikes = high load or hung transactions) |
| Bolt | `bolt.connections_running` | Below thread pool max |
| Bolt | `messages_received` vs `messages_started` | Gap = server saturation |
| Cluster | `cluster.raft.is_leader` | Sum across cluster = 1 (0 = split brain or no leader) |
| Store | `store.size.database` | Watch growth rate. Affects page cache requirements |

### Disk warning signs

- High swap/paging activity = insufficient RAM for heap + page cache
- Distribute store files and transaction logs across separate disks
- Use `db.checkpoint.iops.limit` to throttle checkpoint writes on write-heavy workloads (trades longer checkpoints for lower I/O impact on queries)
