# SQL

Read when querying a database through `effect/sql`, decoding rows, or using transactions. Drivers are separate packages (`@effect/sql-sqlite-node`, `@effect/sql-pg` and so on). Example: `ai-docs/src/40_sql/10_basics.ts`; the transaction semantics are in the JSDoc of `src/sql/SqlClient.ts`.

The driver is a layer chosen at the platform entry point. Domain code depends on the application's own store or service interface, and that layer depends only on `SqlClient.SqlClient`, so swapping the driver (or using a temporary database in tests) is a layer change.

Write statements with the tagged template, `sql\`select * from users where id = ${id}\``; interpolated values are parameters, never string concatenation. A generic row type on a query is a compile-time hope, not a check: decode rows with `SqlSchema.findAll`, `findOne`, `findOneOption`, `findNonEmpty` or `void`, which pair a request schema and a result schema around the query.

`sql.withTransaction(effect)` runs the effect in one transaction, carried in the fiber's context. Everything inside must stay in that context: a separately run runtime, or a fiber forked to outlive the transaction, doesn't see it and uses a new connection. Keep unrelated slow work (HTTP calls) outside the transaction.

`sql.afterCommit(effect)` runs work after the outermost commit and drops it on rollback, including callbacks registered in a savepoint that rolls back. Observed in 4.0: callbacks run uninterruptibly and `withTransaction` waits for them, so keep them short and fork long work; they're lost if the process exits before they run, so work that must happen belongs in a row written inside the transaction; registering one after the transaction has ended is a defect.

Translate driver failures (`SqlError`) to domain errors by what the caller can do: a unique-constraint violation may be a conflict the client should see, an unavailable database a retryable failure. Don't leak driver errors through a public contract or turn every one into a defect.

`SqlModel` and the migrator are available, not required; follow the repo's existing store and migration ownership.
