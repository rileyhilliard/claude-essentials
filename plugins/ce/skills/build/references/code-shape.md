# Code shape

Lanes optimize for passing their tests, so left alone they produce one large file that works and that nobody can follow. These rules keep the output readable. Part 1 is for you while planning and checking. Part 2 is pasted into every lane prompt, because a lane can't read this file.

If the repo has its own layout and style rules, they win over this file.

## Contents

- Part 1: planning and checking
- Part 2: lane block

## Part 1: planning and checking

### Layout is a contract

The scaffold commits the folder structure along with the types. A lane can't split a file it doesn't own, so a layout left to the lanes collapses into the one file that was easiest to write. Before the scaffold:

- Load `architecting-systems` and read its `structure.md` reference. Choose layers or vertical slices to match the repo, and follow the repo's existing layout when it has one.
- Name one module per responsibility, each at its own path with a stub. A responsibility is something you can describe without "and": parsing the request, pricing an order, persisting an order.
- The entry point (`main`, `index`, the router) only wires modules together. If the plan puts logic there, move it to a module.
- No `utils`, `helpers`, `common` or `misc` files. A function that fits nowhere has no clear owner yet, so name the module it belongs to.
- Tests mirror the source layout, one test file per module.

### Size limits

These are tripwires for a closer look, not targets. A file over about 250 lines, or a function over about 40, usually holds two jobs. A lane's owned-file list is the check: if an S or SM lane's work wouldn't fit in the files you gave it at these sizes, the plan needs more modules, so add them to the contracts before dispatch.

### Checking a lane diff

Add this to the inline check in SKILL.md section 5. Send a lane back when any of these hold:

- A new file above the size limits, or a function that mixes parsing, decisions and I/O.
- Logic placed in the entry point, or a new `utils`-style file.
- A module reaching into another module's internals instead of its exported contract.
- A catch block that swallows an error, returns a default in its place, or drops the original cause.
- An exported declaration or module file without a JSDoc-style doc block, a function that can throw with no `@throws`, or JSDoc that repeats TypeScript types.
- Comments that restate the code, narrate the change ("added", "now", "fixed"), or refer to the task.
- Names that need a comment to be understood (`data`, `tmp`, `handle`, `process`, single letters outside tiny loops).

## Part 2: lane block

Paste this into every lane prompt, under the brief.

```
Write code a stranger can follow top to bottom.

Structure
- One responsibility per file and per function. If you need "and" to describe it, split it. Stay in your owned files, and report if the work doesn't fit in them at about 250 lines per file and 40 per function, since that means the plan needs another module.
- Business logic is plain functions that take inputs and return results. Keep I/O (network, disk, database, clock, randomness) at the edges and pass it in, so logic can be tested without mocks.
- Depend on other modules only through their exported contracts. Don't reach into their internals and don't add a new shared helper file.
- Don't put logic in the entry point or in a catch-all file. Follow the layout already in the scaffold.

Naming and flow
- Name things for what they are or do (`applyDiscount`, `pendingOrders`), not `data`, `result`, `handle`, `process` or `manager`.
- Prefer early returns over nested conditionals, and named constants over bare numbers or strings. Extract a named function instead of writing a comment that explains a block.

Errors
- Follow the handling-errors skill and the plan's error model. Catch only where you can recover or add context, wrap with the original cause attached, and never return a default or an empty value in place of a failure.

Comments
- Doc comments are JSDoc style: a `/** ... */` block directly above the declaration. In other languages use the equivalent doc-comment form (Python docstrings, Rust and C# `///`, Go comments starting with the name).
- Every exported function, class, type and constant gets one, opening with a one-sentence summary of what it does or represents. Each module file opens with a short block saying what the module is responsible for.
- Add `@throws` (or the language's equivalent) for every error a caller can see, naming the error type and when it happens. Add `@param` and `@returns` only when the name and type leave a question open, such as units, ranges, or what an empty value means. In TypeScript never repeat the type inside JSDoc braces; the signature already has it.
- Inside function bodies, use plain `//` line comments, and only for what the code can't say: why this approach, a constraint from outside the code, a surprising edge case.
- Write every comment as a colleague would explain it across the desk: plain, specific, no hype and no em dashes. Say what is true now, not what you changed or what the task was.
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
