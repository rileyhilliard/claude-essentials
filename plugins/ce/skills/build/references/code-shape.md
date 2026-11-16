# Code shape

Left alone, lanes pass their tests with one large file nobody can follow. Part 1 is for you while planning and checking. Part 2 goes into every lane prompt, since a lane can't read this file. The repo's own layout and style rules win over both.

## Part 1: planning and checking

### Layout is a contract

A lane can't split a file it doesn't own, so the scaffold commits the folder structure along with the types. Before the scaffold:

- Read `architecting-systems`' `structure.md` reference and choose layers or vertical slices to match the repo, following its existing layout if it has one.
- Give each responsibility its own module path and stub. A responsibility is describable without "and": parsing the request, pricing an order, persisting an order.
- The entry point (`main`, `index`, the router) only wires modules together.
- No `utils`, `helpers`, `common` or `misc` files. A function that fits nowhere needs a named owner module.
- Tests mirror the source layout, one test file per module.

Files over about 250 lines and functions over about 40 usually hold two jobs. If a lane's work wouldn't fit its owned files at those sizes, add modules to the contracts before dispatch.

### Checking a lane diff

Part of the inline check in SKILL.md section 5. Send a lane back for:

- A new file above the size limits, or a function that mixes parsing, decisions and I/O.
- Logic in the entry point, or a new `utils`-style file.
- A module reaching into another module's internals instead of its exported contract.
- A catch block that swallows an error, returns a default in its place, or drops the original cause.
- An export or module file without a JSDoc-style doc block, a throwing function without `@throws`, or JSDoc that repeats TypeScript types.
- Comments that restate the code, narrate the change ("added", "now", "fixed"), or refer to the task.
- Names that need a comment to be understood (`data`, `tmp`, `handle`, `process`, single letters outside tiny loops).

## Part 2: lane block

Paste this into every lane prompt, under the brief.

```
Write code a stranger can follow top to bottom.

Structure
- One responsibility per file and per function; if describing it needs "and", split it. Stay in your owned files, and report if the work doesn't fit them at about 250 lines per file and 40 per function, since the plan then needs another module.
- Business logic is plain functions from inputs to results. Keep I/O (network, disk, database, clock, randomness) at the edges and pass it in, so logic tests need no mocks.
- Use other modules only through their exported contracts. Don't add a shared helper file.
- Keep logic out of the entry point and follow the scaffold's layout.

Naming and flow
- Name things for what they are or do (`applyDiscount`, `pendingOrders`), not `data`, `result`, `handle`, `process` or `manager`.
- Prefer early returns over nesting and named constants over bare literals. Extract a named function instead of commenting a block.

Errors
- Follow the handling-errors skill and the plan's error model. Catch only to recover or add context, keep the original cause, and never return a default or empty value in place of a failure.

Comments
- Doc comments are JSDoc style, a `/** ... */` block above the declaration, or the language's equivalent (Python docstrings, Rust and C# `///`, Go comments starting with the name).
- Every export gets one, opening with a one-sentence summary. Each module file opens with a short block on what it's responsible for.
- Add `@throws` (or equivalent) for every error a caller can see, naming the type and when. Add `@param` and `@returns` only when name and type leave a question, such as units, ranges or what empty means. In TypeScript never repeat the type in JSDoc braces.
- Inside function bodies, use `//` comments only for what the code can't say: why this approach, an outside constraint, a surprising edge case.
- Write comments the way a colleague would explain across the desk: plain, specific, no hype, no em dashes. Say what is true now, not what you changed or what the task was.
- No commented-out code, and no TODO without a reason and an owner.

Example:

    /**
     * Applies the customer's discount tier to an order subtotal.
     * Tiers stack with promo codes, but the total discount is capped at 50%.
     *
     * @param subtotalCents - Pre-tax subtotal in cents.
     * @throws {UnknownTierError} When the customer's tier isn't in the pricing table.
     */
    export function applyDiscount(subtotalCents: number, customer: Customer): number {
```
