# Concurrency

Concurrency bugs are some of the hardest to reproduce and fix. The structural decisions you make early determine whether concurrency is manageable or a constant source of subtle failures.

## Default to Message Passing Over Shared State

Shared mutable state + multiple writers = race conditions. This is true regardless of language. Prefer architectures where components communicate through messages, channels, or queues rather than reading/writing the same data.

| Approach | Mechanism | Best for |
|----------|-----------|----------|
| Message passing / channels | CSP (Go channels), actor model | Cross-component coordination |
| Immutable data | Functional transforms, copy-on-write | Data processing pipelines |
| Single-owner state | One writer, many readers | State that changes infrequently |
| Locks / mutexes | Explicit synchronization | Last resort for shared mutable state |

## Async/Await Pitfalls

- **Don't mix sync and async.** Blocking inside async code causes deadlocks. If you need sync code in an async context, isolate it in a worker thread.
- **Limit concurrency explicitly.** Unbounded `Promise.all()` on 10,000 items will overwhelm downstream services. Use semaphores or concurrency-limited utilities.
- **Always propagate cancellation.** Pass abort signals / cancellation tokens through the entire call chain. Orphaned async tasks leak memory and connections.
- **Handle partial failures.** When running concurrent operations, some will succeed and some will fail. Design for this from the start (use `Promise.allSettled()` over `Promise.all()` when partial success is acceptable).

## In-Process Async vs Queue-Based Processing

| Use in-process async when | Use a queue when |
|--------------------------|------------------|
| Task completes in milliseconds | Task takes seconds or longer |
| Failure is immediately visible | Work needs to survive process restarts |
| Scale within a single process | Producers and consumers scale independently |
| Low operational overhead matters | Fault tolerance and retry logic matter |

Start with in-process async. Move to queues when you need durability, independent scaling, or cross-service decoupling.
