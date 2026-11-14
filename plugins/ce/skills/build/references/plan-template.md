# Plan template

Fill this in after the grill. Phase 1 gets full lane briefs and its test-case list now; later phases get one-line lane rows, and their briefs and test-case lists are written while the phase before them runs.

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

Shared types, interfaces and file layout that lanes build against, and the stub at each module path (exports the contract signatures, throws "not implemented"). Anything two lanes both need lives here.

## Phases

### Phase 1: <capability> (MVP)

Demo: `<command or steps that show it working>`
Checkpoint: <time>
Test cases: one line per behavior and edge case the phase's tests must cover, including every edge case the spec names.

| Lane | Size | Owns files | Reads | Tests | Model | Done when |
| --- | --- | --- | --- | --- | --- | --- |
| a | S | src/items.ts | contracts | items.test.ts | sonnet | items tests pass |
| b | SM | src/orders.ts, src/pricing.ts | contracts, src/items.ts | orders.test.ts | opus | orders tests pass |

Sizing check: longest lane is within about 2x the shortest; no lane is larger than SM; no lane is tiny.

#### Lane a brief

- Goal: what this lane adds, in one or two sentences.
- Interface: exact signatures, types and module paths it implements or calls, citing the contracts by name.
- Behavior: one line per behavior and edge case, with exact outputs, error kinds and messages where the spec fixes them.
- Decisions already made: answers from the grill and assumptions that touch this lane.
- Out of scope: what the lane must not add, including things a reasonable engineer might add unprompted.
- Done when: the tests that must pass and the commands that prove it.

(One brief per lane, including test-writing lanes, whose behavior list is the test cases to write.)

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

A lane's "Owns files" list is the list of files it may edit. If you can't write disjoint lists for two lanes, merge them into one. "Reads" names what the lane reads beyond its owned files and tests: the contracts plus at most two pattern files. Size is S or SM as defined in SKILL.md's sizing table; anything larger gets split before the plan is shown to the user. Model is sonnet only when the lane passes all four checks in SKILL.md's "Choosing a lane's model" (settled contract, no spec gaps, contained in its files, wrong code fails its tests); otherwise opus.
