# Plan template

Fill this in after the grill. Phase 1 gets full lane briefs and a test-case list now; later phases get them while the phase before runs.

```markdown
# Build: <name>

Started: <time>. Timebox: <T or none>. Landing branch: build/<slug>.
Gate: `<full gate command>` (<seconds>s). Filtered tests: `<command with a file or name filter>`. Typecheck: `<command>`.
Runner: `rr run --local "<cmd>"` (no `.rr.yaml`), `rr run "<cmd>"` (hosts in `.rr.yaml`), or plain commands without rr.
Worktree setup: `<command that makes a fresh worktree runnable without changing the lockfile>`.
Scaffold commits: phase 1 <sha>; phase 2 <sha>; ...

## Spec

What it does and who uses it, in two or three sentences.

In scope: the settled answers from the grill, one line each.
Out of scope: what was explicitly cut.
Assumptions: decisions defaulted without asking, which the user can override.
Error model: what fails, how it's reported, what a caller sees.

## Contracts (scaffold commit)

Shared types and interfaces, and a stub at each module path that exports its signatures and throws "not implemented". Anything two lanes both need lives here.

Layout: the folder tree, one line per module giving its single responsibility, entry point marked as wiring only. Example:

    src/
      main.ts              wires config, routes and server; no logic
      orders/parse.ts      validates a raw order request into an Order
      orders/pricing.ts    computes totals and discounts; pure
      orders/store.ts      reads and writes orders; the only module that touches the database

## Phases

### Phase 1: <capability> (MVP)

Demo: `<command or steps that show it working>`
Checkpoint: <time>
Test cases: one line per behavior and edge case, including every edge case the spec names.

| Lane | Size | Owns files | Reads | Tests | Model | Done when |
| --- | --- | --- | --- | --- | --- | --- |
| a | S | src/items.ts | contracts | items.test.ts | sonnet | items tests pass |
| b | SM | src/orders.ts, src/pricing.ts | contracts, src/items.ts | orders.test.ts | opus | orders tests pass |

#### Lane a brief

- Goal: what this lane adds, in one or two sentences.
- Interface: exact signatures, types and module paths it implements or calls, citing the contracts by name.
- Behavior: one line per behavior and edge case, with exact outputs, error kinds and messages where the spec fixes them. For code that reads files, paths or text, name how it handles binary input, line endings, path separators and symlinks.
- Decisions already made: answers from the grill and assumptions that touch this lane.
- Out of scope: what the lane must not add, including things a reasonable engineer might add unprompted.
- Done when: the tests that must pass and the commands that prove it.

(One brief per lane. A test-writing lane's behavior list is the test cases to write.)

### Phase 2: <capability>

Demo: ...
Depends on: phase 1
Checkpoint: <time>

| Lane | Size | Owns files | Model |
| --- | --- | --- | --- |
| a | S | ... | sonnet |

(Test cases and briefs written during phase 1.)

## Log

Phase tags, cut lanes, accepted lane choices, DA and review findings and what happened to each.
```

"Owns files" is what a lane may edit, disjoint across lanes. "Reads" is the contracts plus at most two pattern files. Size and Model follow "Sizing lanes" and "Choosing a lane's model" in SKILL.md.
