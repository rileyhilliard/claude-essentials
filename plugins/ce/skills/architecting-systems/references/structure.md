# Structure and Separation of Concerns

Every module, file, and function should have one clear reason to change. When something has multiple reasons to change, it becomes a coordination bottleneck.

## Layers

Organize code into layers with clear responsibilities. Dependencies flow one direction (inward toward the domain).

```
Presentation  →  Application  →  Domain  ←  Infrastructure
(UI, API)        (orchestration)  (rules)    (DB, external APIs)

→ = depends on (points toward what it imports)
```

- **Domain:** Business rules and entities. No framework imports. No I/O.
- **Application:** Use cases that orchestrate domain objects. Thin layer.
- **Infrastructure:** Database, HTTP clients, file systems. Implements interfaces defined by the domain (arrow points inward).
- **Presentation:** Controllers, routes, views. Translates between external formats and application calls.

## Vertical Slices

Use features as your top-level organization, with layers as internal structure within each feature. A `payments/` directory with its own domain, routes, and tests is easier to reason about than scattering payment logic across `controllers/`, `services/`, `models/`, and `types/`.

```
src/
├── payments/
│   ├── domain.ts        # types, business rules, repository interface
│   ├── service.ts       # application logic, orchestration
│   ├── routes.ts        # presentation (HTTP handlers)
│   ├── repository.ts    # infrastructure (database)
│   └── tests/
├── users/
│   ├── domain.ts
│   ├── service.ts
│   └── ...
└── shared/              # genuinely shared utilities only
```

This combines both approaches: features as boundaries (vertical), layers within features (horizontal). Each feature owns its full stack. Layers within features keep the dependency rule intact.

**The "shared" trap:** If `shared/` or `utils/` keeps growing, it's a sign that boundaries are wrong. Shared code should be small, stable, and genuinely cross-cutting (logging, error formatting). Not a dumping ground.
