# Plan template

Fill this in after the grill, or convert an adopted plan or RFC into it. Phase 1 gets full lane briefs and a test-case list now; later phases get them while the phase before runs. `plan_graph.py` parses the header lines, phase headings, `Depends on`/`Scaffold`/`Tag` lines and lane tables, so keep their shape.

```markdown
# Plan: <name>

Skill: <sprint or deliver>. Profile: <sprint or deliver>. On resume, re-read shared/lane-dag.md before anything else.
plan_graph: <absolute path to plan_graph.py>
Started: <time>. Timebox: <T or none>. Landing branch: <branch>.
Gate: `<full gate command>` (<seconds>s). Filtered tests: `<command with a file or name filter>`. Typecheck: `<command>`.
Runner: `<wrapper that queues or offloads test runs, if the repo uses one>`, or plain commands.
Worktree setup: `<command that makes a fresh worktree runnable without changing the lockfile>`.
Suppressions: <extra markers check-lane should reject, comma-separated, if any>
Manifests: <extra manifest file names check-lane should reject, if any>

## Spec

What it does and who uses it, in two or three sentences.

In scope: the settled answers from the grill or the adopted plan, one line each.
Out of scope: what was explicitly cut.
Assumptions: decisions defaulted without asking, which the user can override.
Error model: what fails, how it's reported, what a caller sees.

## Contracts (scaffold commit)

Shared types and interfaces, and a stub at each new module path that exports its signatures and throws "not implemented". Anything two lanes both need lives here.

Layout: the folder tree, one line per module giving its single responsibility, entry point marked as wiring only. Example:

    src/
      main.ts              wires config, routes and server; no logic
      orders/parse.ts      validates a raw order request into an Order
      orders/pricing.ts    computes totals and discounts; pure
      orders/store.ts      reads and writes orders; the only module that touches the database

## Phases

### Phase 1: <capability> (MVP)

Demo: `<command or steps that show it working>`
Checkpoint: <time, sprint only>
Test cases: one line per behavior and edge case, including every edge case the spec names.

| Lane | Size | Owns files | Reads | Tests | Model | Status | Branch | Done when |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| a | S | src/items.ts | contracts | src/items.test.ts | sonnet | pending | | items tests pass |
| b | M | src/orders.ts, src/pricing.ts | contracts, src/items.ts | src/orders.test.ts | opus | pending | | orders tests pass |

#### Lane a brief

- Goal: what this lane adds, in one or two sentences.
- Interface: exact signatures, types and module paths it implements or calls, citing the contracts by name.
- Behavior: one line per behavior and edge case, with exact outputs, error kinds and messages where the spec fixes them. For code that reads files, paths or text, name how it handles binary input, line endings, path separators and symlinks.
- Decisions already made: answers from the grill and assumptions that touch this lane.
- Out of scope: what the lane must not add, including things a reasonable engineer might add unprompted.
- Done when: the tests that must pass and the commands that prove it.

(One brief per lane. A test-writing lane lists its test files under Owns files, and its behavior list is the test cases to write.)

### Phase 2: <capability>

Demo: ...
Depends on: phase 1
Checkpoint: <time, sprint only>

| Lane | Size | Owns files | Reads | Tests | Model | Status | Branch | Done when |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| a | S | src/report.ts | | | sonnet | pending | | |

(Test cases and briefs written during phase 1.)

## Log

Phase tags, cut lanes, accepted lane choices, review and QA findings and what happened to each (fixed, or rejected with a reason).
```

Add a phase's `Scaffold: <sha>` line when its scaffold is committed, and let `plan_graph.py tag` write its `Tag:` line. Don't add either early: the script treats a phase with the line as scaffolded or tagged. Owns files is what a lane may edit, disjoint across lanes that can run at the same time. Paths are comma-separated and repo-relative, optionally in backticks; a trailing `/` means a whole directory; globs aren't allowed. Tests lists test files the lane must pass and may not edit. Reads is the contracts plus at most two pattern files. Status is `pending`, `running`, `merged` or `cut`. Size and Model follow "Sizing lanes" and "Choosing a lane's model" in lane-dag.md.
