# Build: orders api

Skill: deliver. Profile: deliver. On resume, re-read shared/lane-dag.md before anything else.
plan_graph: /abs/path/plan_graph.py
Suppressions: `@SuppressWarnings`, `# nosec`
Manifests: `deno.json`

## Phases

### Phase 1: list items (MVP)

Demo: `curl localhost:3000/items`
Scaffold: 1a2b3c4
Tag: phase-1

| Lane | Size | Owns files | Reads | Tests | Model | Status | Branch | Done when |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| a | M | `src/items.ts`, src/items/ | contracts | src/items.test.ts | sonnet | merged | build/x-1a | items tests pass |
| b | S | src/orders.ts | contracts, src/items.ts | src/orders.test.ts | opus | running | build/x-1b | orders tests pass |

### Phase 2: pricing

Depends on: phase 1
| Lane | Size | Owns files | Reads | Tests | Model | Status | Branch | Done when |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| a | S | src/pricing.ts | | | sonnet | pending | | |
