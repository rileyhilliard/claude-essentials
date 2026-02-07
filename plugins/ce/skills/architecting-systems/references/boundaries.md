# Boundary Design

Good boundaries are the difference between a system where teams can work independently and one where every change requires cross-team coordination.

## Bounded Contexts

Different parts of your system mean different things by the same words. A "User" in auth is credentials and sessions. A "User" in billing is payment methods and invoices. A "User" in social is profiles and connections.

These should be separate models, not one god object that grows every field any consumer needs. In practice, bounded contexts become separate modules (or services) with their own types, storage, and logic. Communication between contexts happens through explicit interfaces or events, not shared database tables or direct imports.

**How to identify boundaries:** If two parts of the system change for different business reasons, they belong in different contexts. If a change in one area frequently breaks another, the boundary is missing or leaking.

**Start simple:** You don't need to get boundaries perfect on day one. Start with modules in a monolith. Extract to services later if the boundary proves real and the team needs independent deployment. Wrong service boundaries are much harder to fix than wrong module boundaries.

## API Boundaries

- **Contract-first:** Define the API before building it. The contract is the agreement; the implementation is an internal detail.
- **Version APIs that cross team or service boundaries from day one.** Internal APIs within a single service can wait until they stabilize.
- **Validate at boundaries:** Trust internal code. Validate external input aggressively (user input, API responses, file reads).

## Package/Module Boundaries

- Each package owns one domain concept
- Expose a minimal public API (single entry point where possible)
- Internal structure is private and can change freely
- Dependencies between packages flow in one direction
