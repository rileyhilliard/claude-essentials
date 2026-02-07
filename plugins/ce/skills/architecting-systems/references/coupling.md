# Loose Coupling and Dependency Management

Coupling is the #1 cause of systems becoming painful at scale. Every unnecessary dependency between modules is a future coordination problem.

## Depend on Interfaces, Not Implementations

Define what you need, not how it's provided. This isn't abstract architecture advice; it's the difference between a 10-minute change and a 2-day refactor.

```ts
// Tight coupling: service knows about specific database
class OrderService {
  private db = new PostgresDatabase(); // locked in
}

// Loose coupling: service declares what it needs
class OrderService {
  constructor(private repository: OrderRepository) {} // any implementation works
}
```

## Boundaries Through Contracts

Modules communicate through explicit, stable interfaces. Internal implementation details stay internal.

- **Public API per module:** Each module exports a clear interface. No deep imports into another module's internals.
- **Enforce boundary direction:** Shared packages never import from app code. Feature modules don't import from each other directly.
- **Anti-corruption layers:** When integrating with external systems or messy legacy code, translate at the boundary. Don't let external data shapes infect your domain.

## Communication Patterns

| Pattern | When | Coupling Level |
|---------|------|----------------|
| Direct function calls | Same module, synchronous | Tightest |
| Interface/protocol | Cross-module within a service | Moderate |
| Events/messages | Cross-service, async workflows | Loosest |
| API contracts | Service-to-service | Loose (if versioned) |

Choose the loosest coupling level that still makes the code readable and debuggable. Don't use event-driven architecture for something that's just a function call.

## The Dependency Rule

Dependencies point inward. Business logic never imports infrastructure. Infrastructure implements interfaces the business logic defines.

```ts
// Domain defines what it needs (no framework imports)
interface OrderRepository {
  save(order: Order): Promise<void>;
  findById(id: string): Promise<Order | null>;
}

// Infrastructure provides it
class PostgresOrderRepository implements OrderRepository {
  async save(order: Order): Promise<void> {
    // actual database code here
  }
}
```

## Minimize External Dependencies

Every dependency is a liability: security surface, upgrade burden, potential abandonment. Before adding a library:

- Can the standard library do this?
- Is this solving a problem we actually have?
- What's the maintenance health of this project?
- Would 20 lines of code eliminate the need?

## Manage What You Can't Avoid

For dependencies you do take on:

- **Pin versions** and update deliberately, not reactively
- **Wrap libraries you might realistically replace** (unstable deps, vendor SDKs, libraries you're evaluating). Don't wrap stable utilities you'll use forever.
- **Isolate vendor-specific code** in infrastructure layers
