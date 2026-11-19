# RFC: one lane DAG for build and executing-plans

Status: draft, revised after one devil's advocate pass (see "Review log")
Target: ce 6.0.0 (renames two skills)

## Summary

`build` and `executing-plans` both turn a plan into merged code with parallel subagents, but each hand-writes its own schedule, and the two have drifted. `build` lands work per phase with mechanical lane checks and a contracts scaffold. `executing-plans`, the skill meant for production work, merges everything at the end, has no defined step for merging subagent branches, and can loop on code review with no stopping rule.

This RFC moves the shared execution model into required references under `plugins/ce/shared/`, plus a script, `plan_graph.py`, that validates the plan graph, reports which lanes are ready and checks a lane's diff. Both skills load the DAG reference before they dispatch anything. Each skill keeps its own front half and sets an effort profile for the shared stages. The two skills are renamed for what they now do.

## Problem

1. `executing-plans` has no fan-in. Subagents "commit on their own branch only" and never merge (`executing-plans/SKILL.md:38`), and section 4 merges only the worktree branch to main (`:64`). Nothing says who merges the subagent branches, in what order, or what runs after.
2. `executing-plans` has nothing to show until the end. With no per-phase landing, a failure in the last group blocks everything, and integration bugs between groups surface only at the final review.
3. Review in `executing-plans` doesn't converge. `code-reviewer` is told to report "every real defect," include findings it isn't sure about, and treat every item as a fix (`agents/code-reviewer.md:76,102-104`), and the skill reruns it "if the fixes were substantial" (`executing-plans/SKILL.md:59`) with no definition or cap. Each round re-reviews the whole diff and finds something new, and later rounds push toward over-optimization that can make the result worse.
4. `build` reviews once at the end and checks only opus lanes with a model (`build/SKILL.md:135,147`), because review sits on the critical path.

Both skills also spend model context on work a script does better. `build` describes its mechanical lane check in prose (`build/SKILL.md:131`), and its fast DA spends one of five findings on overlapping file ownership (`build/references/dispatch-prompts.md:16`), which is a set intersection.

## Goals and non-goals

Goals:

- One definition of the DAG (nodes, edges, scheduling, landing, state) that both skills follow.
- The skills differ in their front half and their effort profile, and nowhere else in the execution stages.
- Deterministic checks run as a script; model calls go to judgment.
- Every review has a stopping rule, and no code is reviewed in full more than twice.
- A crash or compaction mid-run resumes from the plan file without reconstructing state from git.

Non-goals:

- Lane-level dependency edges. Phases stay the unit of dependency. A lane in phase 2 waiting on one lane in phase 1 would save little at four lanes in flight, and it would remove the phase tag as the demo and resume point.
- A runtime or daemon. The orchestrator is still the model, looping on `plan_graph.py ready`.

## Design

### Layout

```
plugins/ce/
  shared/
    lane-dag.md              # the DAG: sizing, routing, briefing, scheduling, landing, review rules
    grill.md                 # moved from build section 1, used by both skills
    plan-template.md         # moved from build/references, gains Status, Branch and Scaffold
    dispatch-prompts.md      # moved from build/references, prompts parameterized by profile
    code-shape.md            # moved from build/references
    scripts/plan_graph.py    # validate, ready, check-lane, mark, tag
    scripts/test_plan_graph.py
  skills/
    sprint/SKILL.md          # was build
    deliver/SKILL.md         # was executing-plans
```

`claude plugin validate --strict` passes with a `shared/` directory at the plugin root (checked against 5.9.0), and both agents' installs copy the whole plugin directory, so `shared/` ships with the skills.

Skills link to shared files by plain relative path from the skill directory, `../../shared/<file>`. Claude Code gives the model each skill's base directory when it loads, and Codex resolves relative paths from the skill directory: a probe on codex-cli 0.170.0 read `../shared/dag.md` from a skill and returned its contents. Skill bodies don't use `${CLAUDE_PLUGIN_ROOT}`. Claude Code substitutes it in plugin skills, but the same probe showed Codex passes it through literally; Codex substitutes it only in hook and MCP configs.

Each SKILL.md links every shared file it needs directly, so references stay one level deep. Shared files name each other in plain text ("Sizing lanes in lane-dag.md") but don't link, and the moved files' pointers to skill sections are rewritten to name sections of `lane-dag.md`.

### Making the reference required

A skill can't force a file into context, so three things carry the requirement:

- The SKILL.md says, before its first execution step, "Read `lane-dag.md` in full now. The steps below set its effort profile and use its terms." That instruction sits in the first 5k tokens of the skill, which Claude Code re-attaches after compaction.
- The plan file's header records the skill and profile and says to re-read `lane-dag.md` on resume, so a compacted orchestrator that re-reads the plan is pointed back.
- The orchestrator resolves `../../shared/scripts/plan_graph.py` against the skill directory once, writes the absolute path into the plan header, and puts it in every lane prompt, since lanes run in other worktrees and don't know where the skill lives.

### The DAG

```
plan ─> validate ─> scaffold ─> phase 1 ─┬─> phase 2 ─> phase 4 ─┐
                                         └─> phase 3 ────────────┴─> final review ─> approve ─> done

inside a phase:
  scaffold commit ─> lane a ─┐
                     lane b ─┼─> each lane landed as it reports ─> gate ─> tag phase-N
                     lane c ─┘
```

Nodes are lanes (one brief, one subagent, one worktree, disjoint owned files) grouped into phases. Edges are phase-level `Depends on` lines. A phase is ready when every phase it depends on is tagged and its own scaffold commit is recorded. Phase 1 always runs alone. At most four lanes are in flight across all phases.

`lane-dag.md` carries what `build/SKILL.md` sections 2 (sizing, model routing, briefing), 4 and 5 say today, generalized. That text moves and is rewritten only where this RFC changes it.

Small work skips the graph. When the whole plan is one lane's worth of scope by the sizing table, the orchestrator does it inline with no template conversion, no worktree for a single-file change, and goes straight to the profile's review. This keeps `executing-plans`' current skip for trivial changes (`executing-plans/SKILL.md:12`).

### Existing codebases

`build`'s mechanics assume greenfield code: stubs that throw "not implemented" at every module path and registration files owned by the scaffold. In an existing codebase, `lane-dag.md` relaxes three of them:

- The scaffold commit holds only new contracts (new types, new module stubs, new exports added to shared registration files) plus the phase's new failing tests. Existing modules aren't stubbed.
- Edits to a shared file (a router, a types file, a barrel) that two lanes both need go into the scaffold when they are declarations, or into one lane that owns the file when they're behavior. A phase where most lanes need the same file has too many lanes; it runs as fewer, larger lanes or across phases.
- Existing tests stay editable by a lane that owns them when the plan says the behavior changes. The brief names which tests change and why.

### Plan file as state store

Plan header additions:

```markdown
Skill: deliver. Profile: deliver. On resume, re-read shared/lane-dag.md before anything else.
plan_graph: /abs/path/to/shared/scripts/plan_graph.py
```

Each phase heading gets `Depends on:`, `Scaffold: <sha>` once committed, and `Tag: phase-N` once tagged. Every phase's lane table has the same columns from the start, so a later phase's unbriefed rows parse the same way:

```markdown
| Lane | Size | Owns files | Reads | Tests | Model | Status | Branch | Done when |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| a | M | src/items.ts | contracts | src/items.test.ts | sonnet | merged | build/x-1a | items tests pass |
| b | S | src/orders/ | contracts | | opus | pending | | |
```

Status is `pending`, `running`, `merged` or `cut`. Review state isn't tracked per lane, because review findings become work in briefs or fix lanes that have their own rows.

Column grammar, which `validate` enforces: `Owns files` and `Tests` are comma-separated repo-relative paths, optionally in backticks, where a trailing `/` means a directory and everything under it. No globs. `Reads` may also contain the word `contracts`. Empty cells are allowed in phases without a `Scaffold:` line.

### plan_graph.py

Python 3 standard library only, matching `post-mortem/scripts/extract-friction.py`. Skills say to run it, not read it. Every failure prints one line per problem naming the phase, lane and file.

| Command | Does |
| --- | --- |
| `validate <plan>` | Columns parse per the grammar; owned paths (files and directories, compared by prefix) are disjoint across lanes in phases that can run concurrently; every `Depends on` names a real phase; no cycles |
| `ready <plan>` | Prints `pending` lanes in phases that have a `Scaffold:` line and whose dependencies all have a `Tag:` line, up to four minus the lanes `running` |
| `check-lane <plan> <phase>/<lane> <base>` | On `git diff <base>...<branch>`: every changed path is under `Owns files`, or under `Tests` for a lane whose brief owns tests; no lockfile or manifest changed; no added line matches the skip or suppression list |
| `mark <plan> <phase>/<lane> <status> [--branch <name>]` | Rewrites the Status cell, and the Branch cell when given |
| `tag <plan> <phase> <tag>` | Writes the `Tag:` line after the orchestrator creates the git tag |

Test-file protection falls out of ownership: an implementation lane's tests are in its `Tests` column, not `Owns files`, so editing them fails the path check. No test-path heuristics are needed.

The skip and suppression list is fixed in the script and covers the common cases: `.skip(`, `.only(`, `.todo(`, `xit(`, `fit(`, `@pytest.mark.skip`, `t.Skip(`, `@ts-ignore`, `@ts-expect-error`, `@ts-nocheck`, `eslint-disable`, `# type: ignore`, `# noqa`, `# pyright: ignore`, `//nolint`, `#[allow(`. The manifest list is `package.json`, the common lockfiles, `pyproject.toml`, `requirements*.txt`, `go.mod`, `go.sum`, `Cargo.toml` and `Cargo.lock`. A plan can extend either list in its header. The check for an export only tests use stays a model check, since it needs a call graph.

Resume rule, in `lane-dag.md`: a lane marked `running` whose agent is no longer live is checked with `check-lane` if its branch has commits past the scaffold, and set back to `pending` otherwise.

`test_plan_graph.py` covers each command against fixture plans (concurrent phases, a cycle, overlapping directory ownership, an unbriefed phase) and a temporary git repo, in the same commit as the script.

### Landing a lane

1. Run `check-lane`. Lanes also run it on themselves before reporting, using the absolute path from their prompt, so most violations are fixed by the agent that has the context.
2. Model check against the brief (nothing extra, reported choices accepted and logged, no export only tests use), then shape per `code-shape.md`.
3. Lane review by `code-reviewer` with the lane-check prompt, when the profile calls for it.
4. `git merge --no-ff` into the landing branch, or the phase branch for a concurrent phase, in the order lanes pass. `mark` it merged.
5. After the phase's last merge: full gate, a `phase N: fixes` commit if needed, the demo, the git tag, then `tag`.

A lane that fails twice on the same error, or a decision the plan leaves open that the user would want to make, stops the run and goes to the user. This carries over `executing-plans/SKILL.md:16,41`.

### Review that converges

Four rules, in `lane-dag.md`, apply to every review in both skills.

A finding needs evidence. A correctness finding names the input or state that breaks and what happens; a maintainability finding names the split or rewrite that fixes it. A finding without that is dropped.

The orchestrator triages. Each finding is fixed or rejected with a one-line reason in the plan's Log. The reviewer keeps its flat list; the judgment moves to the orchestrator, who has the spec.

A second round reviews only the fix. It gets `git diff <pre-fix sha>..HEAD` and the round-one findings, and answers whether each was fixed and whether the fix broke anything. There is no third round; anything still open goes in the report.

Each review has one scope. A lane review checks one lane's diff against its brief. A phase review checks only the boundaries between that phase's lanes and the code they call. The final review covers the whole diff. None of them re-checks what a narrower one's scope already covered unless the code changed since.

These rules contradict the `code-reviewer` agent's defaults (full `<base>...HEAD` diff, include unsure findings), so the agent gets one paragraph: when the dispatch prompt sets a diff range, a scope or an output format, follow the prompt. `build`'s dispatch prompts already override the default template this way; the paragraph makes the override explicit for scope too. Standalone use of `code-reviewer` is unchanged.

### Phase review placement

Review placement is where the profiles differ most, so it's stated per profile instead of as one pipelining rule.

`sprint` runs no phase review. Lane checks catch most failures before merge, and the final review covers the whole diff once. This is today's `build` behavior with lane review widened (see profiles). Pipelining phase reviews was considered and dropped: phase N+1 usually edits phase N's files, so findings arrive about code that has moved, and fix lanes would change ownership after `validate`.

`deliver` runs one blocking phase review after phase 1, before any later phase starts, scoped to the contracts and module boundaries that phase set up. It runs before anything builds on that code, which is when an architecture finding is cheapest to act on. Later phases get lane reviews and the final review only.

### Effort profiles

| Stage | sprint (was build) | deliver (was executing-plans) |
| --- | --- | --- |
| Plan | Grill from `grill.md`, at most three rounds | Adopt the user's plan or RFC and convert it to the template; grill from `grill.md` only for decisions it leaves open |
| Plan critique | `devils-advocate` on sonnet, 5 findings, plan only, not rerun | `devils-advocate` on opus, checked against the code, focused on boundaries, contracts, error model and failure modes; skipped when the plan was already reviewed |
| Scaffold | New contracts, stubs and phase tests | Same, with the existing-codebase relaxations |
| Lane model check | Every lane | Every lane |
| Lane review | opus lanes, and any lane touching state, concurrency, security or money | Every lane |
| Phase review | None | Phase 1, blocking, boundaries only |
| Final review | One round on the whole diff | Whole diff, then at most one fix-diff round |
| Exercise as a user | The demo command | API calls, CLI runs, UI use or real data, as `executing-plans/SKILL.md:51-55` describes today |
| Timebox and checkpoints | Yes | No |
| Ends at | Tagged landing branch; merge only on request | Report and tags shown to the user, then a local merge to main once they approve; push only on request |

Implementation lanes route by the same judgment rule in both profiles, since a wrong sonnet lane costs more to investigate in either mode. Effort means review depth and blocking.

Worst case, `deliver` reviews each line of code twice in full (its lane review and the final review) plus once more in phase 1's boundary review, and one fix-diff round. That replaces today's uncapped loop of whole-diff reviews.

### The two skills

`sprint` is today's `build`: intake and timebox, grill, plan, then the DAG with the sprint profile. It's for work where wall-clock time is the constraint and the result still has to be usable: prototypes, timeboxed demos, spikes that may be kept. It stays `disable-model-invocation: true`.

`deliver` owns the whole plan, orchestrate, merge, approve cycle. It stays model-invocable, because the README's main example ("Have DA review the plan, then implement it, run code review and merge to main", `README.md:58`) depends on it loading on its own, and only merges after the user approves at the end. Both skills keep `agents/openai.yaml` with `allow_implicit_invocation: false`, so Codex never runs them implicitly.

```yaml
name: sprint
description: Builds something end to end against the clock, landing a demoable, tested phase as early as possible and adding one capability per phase. Grills for scope, writes a phased plan, runs parallel subagent lanes in worktrees, and checks and merges each lane as it finishes, with one review at the end. Use for "/ce:sprint <prompt>", timeboxed builds, prototypes and live demos, or when speed matters more than review depth. For production work, use deliver.
```

```yaml
name: deliver
description: Takes a feature, plan or RFC to production-ready code merged to main, with emphasis on architecture and code quality. Adopts or writes a phased plan, has it critiqued against the codebase, scaffolds contracts, runs parallel subagent lanes, reviews every lane with a capped review cycle, and merges after approval. Use when asked to execute, implement or ship a plan or RFC, for "have DA review it, then implement", or for work that needs full review depth. For timeboxed or prototype work, use sprint.
```

### Manual QA per phase

Each `phase-N` tag is a point the user can check by hand while later phases keep running. QA is optional: the orchestrator never waits for a QA sign-off, and a run where the user checks nothing proceeds exactly the same. This is possible which `executing-plans` can't offer today because nothing lands until every group is done. Both skills tell the user in one line when a phase tags: what it adds, the demo command, and how to run it.

The user runs it from a separate checkout of the tag (`git worktree add <dir> phase-N`), not the landing worktree, because lane merges keep changing files there and would shift under a running dev server. The orchestrator creates that checkout when it tags, and removes it at the end.

Issues the user reports from QA are handled like review findings. One that touches files no running lane owns becomes a fix lane in the next phase to start, or a fix commit before the final review if no phases are left. One in files a running lane owns goes into that lane's follow-up once it merges. Only an explicit request from the user ("hold after phase N") pauses dependent phases; the orchestrator never proposes or defaults to one.

## Migration

Renames are a major version bump per the repo's CLAUDE.md: 6.0.0. `build` and `executing-plans` are removed, not aliased, since a stub skill would still show in the skill list and split triggering. The CLAUDE.md and README inventory tables are updated, the repo is grepped for both old names (the `builder` agent's description says "the build skill"), and `docs/claude-code-best-practices.md` gains a note that `${CLAUDE_PLUGIN_ROOT}` is substituted in Claude Code skill bodies but not in Codex, so shared files are linked by relative path.

Order of work:

1. `plan_graph.py` and its tests.
2. `shared/` files, moved from `build` with the changes above.
3. `sprint` from `build`, slimmed to its front half and profile.
4. `deliver` from `executing-plans`.
5. The `code-reviewer` scope paragraph, the `builder` description, inventory tables, version bump in both manifests, `scripts/check-manifests.sh`, `claude plugin validate --strict` on the marketplace and the plugin.

## Verifying it works

`test_plan_graph.py` covers the script. The skills need real runs: before release, run each skill once on a small task with two or three capabilities, once greenfield and once in an existing repo, and check that the plan validates, phase 1 tags before later phases start, a resume after compaction mid-phase picks up only unmerged lanes, and `deliver` stops after at most one fix-diff round.

## Open questions

1. Lane review breadth in `sprint`. Widening it to lanes touching state, concurrency, security or money adds a background opus review to some sonnet lanes. Is that worth its tokens in a timebox, or should sprint stay at opus lanes only?

## Review log

One `devils-advocate` pass on the first draft returned eight findings. Changes:

- Pipelined phase review dropped: findings went stale as the next phase edited the same files, and fix lanes changed ownership after validation.
- Convergence rules now come with a `code-reviewer` scope paragraph, since the agent's system prompt demanded full-diff review; `deliver` caps full reviews per line at two.
- `plan_graph.py` gained `--branch`, `tag`, the `Scaffold:` precondition for `ready`, a column grammar, a fixed skip and suppression list, and a resume rule for dead `running` lanes.
- Added existing-codebase relaxations, an inline path for small plans, and the skips and stop rules `executing-plans` has today.
- `deliver` stays model-invocable to keep the README's documented trigger.
- Shared-file paths settled by a Codex probe: relative paths from the skill directory work in both agents, and `${CLAUDE_PLUGIN_ROOT}` isn't substituted in Codex skill bodies, so skills don't use it.
- Added "Manual QA per phase" after the author confirmed it as a main reason for the change.
- Names settled as `sprint` and `deliver`, chosen over `building-fast` and `building-for-production` because they're short to type as slash commands and say the mode.
- The grill moved to `shared/grill.md`, and moved files' cross-references are rewritten.
- Finding 8 was partly wrong: the current Claude Code skills docs do document `${CLAUDE_PLUGIN_ROOT}` for shared files. The repo's notes were stale. The compaction and lane-path points were valid and are addressed under "Making the reference required."

A `code-reviewer` pass on the implementation found eight more gaps, all fixed in the skills: lanes now get their branch name at dispatch and rename to it, so `check-lane` and resume can find it; `deliver`'s phase 1 boundary review runs before the tag, so `ready` holds phase 2 without extra state; small work has a defined base commit and spec; a lane review blocks only its own lane's merge; `deliver` writes its plan inside the run's worktree; lanes in a concurrent phase merge from their phase branch; the phase dependency rule, the `writer` skill, commit message guidance, scaled verification and letting a failed lane fix itself first are restored.
