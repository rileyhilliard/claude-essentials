---
name: build
description: Takes a build request from requirements to demo-ready code fast. Grills the user for scope, writes a phased plan with the smallest demoable slice first, runs a quick devil's advocate pass, builds each phase with parallel subagents in isolated worktrees, checks each lane before it merges, tags every green phase so it can be demoed, and ends with a single full code review. Use for "/ce:build <prompt>", timeboxed builds, or when asked to plan and build something end to end quickly. For executing an already-written plan with full review depth, use executing-plans instead.
argument-hint: "<what to build> [timebox, e.g. 90m]"
disable-model-invocation: true
---

# Build

If the repo has its own `.claude/rules/` or CLAUDE.md guidance on branching, testing or review, follow that where it conflicts with this file.

The goal is a landing branch where every phase ends green and demoable, each adding to the last. Speed comes from one grilling session instead of open-ended planning, one fast critique of the plan, background lanes that never block you, and a quick pre-merge check per lane with one full review at the end. Quality comes from tests written before implementation, complete lane briefs, file-disjoint lanes, the pre-merge check, and the full gate on every landing.

## 0. Intake

Record the start time (`date +%s`) and the timebox if the request gives one. Without a timebox, skip the budget checks but keep the phase structure.

Budget for a timebox T, checked at every phase boundary:

| By | Done |
| --- | --- |
| 15% of T | Grill finished, plan written |
| 20% of T | Scaffold committed, DA findings applied |
| 45% of T | Phase 1 (MVP) tagged and demoed |
| 80% of T | Last phase tagged. Start nothing new after this |
| 100% of T | Review fixes landed, final report given |

When a checkpoint slips, cut scope from later phases. Don't compress the gate or the review.

Find the facts yourself, alongside the first grill round rather than before it:

- The test runner and how to filter it, the typecheck command, and how long the full gate takes (run it once).
- How a fresh worktree gets a runnable environment. A new worktree has no `node_modules`, `.venv` or build output, so pick one setup command for every lane: symlink the dependency directory from the main checkout (`ln -s <main checkout>/node_modules node_modules`), or the repo's install with a frozen lockfile. Lanes must not change the lockfile.
- Whether `rr` is on PATH and the repo has a `.rr.yaml` with hosts.
- The current branch and whether the tree is clean. Uncommitted changes would ride into the scaffold commit, so ask whether to commit, stash or include them. With no git repo, or a repo with no commits, run `git init` if needed and make an initial commit, since worktrees need one.
- Whether lanes' test, typecheck and `git add`/`git commit` commands run without permission prompts. Background lanes can't answer a prompt, so confirm the permission mode before phase 1 or the first lane stalls.

## 1. Grill

Question the user until the scope of phase 1 is settled. The technique is adapted from Matt Pocock's grilling skill: treat the request as a tree of decisions, and each round ask every question whose prerequisites are already answered.

Format each round as numbered questions, each with your recommended answer, worded so "yes" accepts the recommendation:

```
Q1. Storage: in-memory, SQLite, or Postgres? Recommend: in-memory behind a repository interface.
Q2. Invalid input: reject the whole request, or report every field error? Recommend: report every field error.
```

Keep each question to a sentence or two so a round can be answered in a minute. Facts you can look up are never questions.

Stop after the round that settles phase 1, usually two rounds and at most three. Decisions that only affect later phases take your recommended default and go in the plan's assumptions list, where the user can override them later. The last round always includes where phases land: a new `build/<slug>` branch (the default) or the current branch.

## 2. Plan

Load the `architecting-systems`, `writing-tests`, `handling-errors` and `writer` skills before writing the plan, and read [references/code-shape.md](references/code-shape.md). They set the house style for module boundaries, the contracts lanes build against, what the tests check, how errors propagate, and how code comments read, and those decisions are cheapest to make here, before any lane depends on them. The plan's contracts section is where the architecture shows up: it lists every module path with its single responsibility, and its spec states the error model (what fails, how it's reported, what a caller sees).

Lanes pass their tests by the shortest route, which is usually one large file. They can only split work across files the plan gave them, so the module layout is decided here, not discovered during the build. A plan whose contracts section names a single implementation file for more than one responsibility isn't ready to show the user.

Write the plan to `plans/build-<slug>.md` using [references/plan-template.md](references/plan-template.md), and show the user the phase list in a few lines. The user approves the phases, not the prose. Write full lane briefs and test-case lists for phase 1 only; later phases get one-line lane rows now and their briefs while the phase before them runs, so planning stays inside its budget.

Phase 1 is the smallest end-to-end slice the user could watch work. Each later phase adds one demoable capability. Ordering phases by layer (all types, then all logic, then all UI) leaves nothing to demo until the end, so order them by capability.

### Sizing lanes

A phase takes as long as its slowest lane plus landing, so keep every lane small and roughly equal. Every lane also carries a fixed cost: the agent's startup and code reading (tens of seconds), worktree setup, and your time checking and merging its diff (a minute or so). Too few lanes and one big lane becomes the bottleneck; too many and the fixed costs eat the parallelism.

Size each unit of work by scope, since time estimates are unreliable:

| Size | Scope | Where it goes |
| --- | --- | --- |
| Tiny | A few lines, one small function, a config change | Inline, or folded into a sibling lane that touches related files |
| S | 1 to 2 owned files, one function, endpoint or component, up to about 5 tests | A lane |
| SM | Up to 3 or 4 owned files, one module or capability, up to about 12 tests | A lane |
| Larger | More than one capability or more than 4 files | Never a lane. Split it by capability into S or SM lanes, or across two phases |

A lane is minutes of agent work: a Sonnet subagent built a precisely specified five-module, 300-line evaluator with tests in about 70 seconds. The "Larger" limit is about keeping lanes balanced and failures contained, not about any one agent being slow.

Then check the phase as a whole:

- Lanes own disjoint files. Two lanes that both need to edit the same file are one lane, or the shared part moves into the scaffold.
- Registration files belong to the scaffold: the public index or barrel, routers, and tests or docs that pin the public API. Stub every planned export there up front so no lane edits them.
- The longest lane is no more than about twice the shortest. Split the long one, or move part of it to the next phase.
- Two to four lanes per phase. Each added lane is another merge and another diff for you to check, so stop at the number of truly independent units.
- Give each lane a reads list: the contracts, its owned files, its tests, and at most two existing files whose patterns it should follow. Code reading is the largest per-lane overhead, and a named list keeps the agent from exploring.
- A phase with one lane, or only tiny units, runs inline in your own checkout with no worktree or subagent.

Small builds (a single module, a few hundred lines) are usually every phase inline. That is the expected outcome, not a failure to parallelize.

### Choosing a lane's model

Sonnet is faster, but a wrong lane costs more in investigation than the seconds it saved, so route by how much judgment the lane needs, not by its size. A lane goes to sonnet when all of these hold:

- Its contract is settled: the types and interfaces it builds against are in the scaffold, and its tests exist or are specified exactly enough to write without choices.
- The spec answers every case the lane touches, so its reads list is enough and nothing is left to interpret.
- It stays inside its owned files, with no invariant that spans modules.
- A wrong implementation would fail its tests, so mistakes surface at the lane, not in a later phase.

Implementing against an existing contract, writing tests from a settled case list, and mechanical edits usually pass. A lane that fails any check goes to opus: designing a contract other lanes depend on, filling a gap in the spec, invariants involving state, ordering, caching, concurrency, security or money, changes across module boundaries, and debugging a failed lane. On settled work Sonnet has matched Opus on quality, and its safety net is the lane's tests rather than the model; [references/benchmarks.md](references/benchmarks.md) has the measurements.

### Briefing lanes

Write every lane a brief that would let an engineer who has never seen the conversation do the work without asking anything: the goal, the exact interface, one line per behavior and edge case (with exact outputs and errors where the spec fixes them), the decisions already made that touch it, what is out of scope, and what done means. The template has the shape. Every delegated task gets one, whatever the model or tool, because each ambiguity left in becomes a choice the agent makes alone and you find in review.

The brief goes into the dispatch prompt in full, so the agent spends its time building rather than reconstructing the task from the plan and the codebase. If a brief can't be written without open questions, the lane isn't ready: settle the question, or route the lane to opus with the question named.

## 3. Scaffold and fast DA, in parallel

Dispatch the `devils-advocate` agent in the background with `model: sonnet` and the scoped prompt in [references/dispatch-prompts.md](references/dispatch-prompts.md). It reads the plan, including phase 1's test-case list, caps findings at five, and skips verifying against the codebase, which is what makes the default run slow on a greenfield build.

While it runs, create the landing branch and commit the scaffold:

- The plan file.
- Shared types and interfaces that lanes import.
- The full folder layout from the plan's contracts section, with the entry point limited to wiring.
- A stub at every planned module path that exports its contract signatures and throws "not implemented", so typecheck passes at the scaffold commit and only the tests fail. Empty files would fail every lane's typecheck on modules it doesn't own.
- The phase 1 tests, written from the test-case list and read by you before committing, with a test for every edge case the spec names, since a lane implements what its tests check and skips what they don't.
- Anything the gate needs to run.

Record the scaffold commit's SHA in the plan. Lanes start from it, so anything two lanes share belongs here. Tests are yours: implementation lanes treat them as read-only, and a missing case is fixed by you in the scaffold, not by the lane.

When the DA returns, check each finding against the plan. Apply the ones that change phase 1 now, move the rest to the phase they affect, and drop the ones that don't hold. Don't run it again. If the scaffold is done and the DA hasn't returned, start phase 1 and fold its findings in when they arrive.

## 4. Run a phase

Phases after the first start with their own scaffold commit: that phase's stubs and tests, merged from the test-writing lane if one wrote them. Never merge a later phase's tests during the current phase, since the gate would fail on tests nobody is meant to pass yet.

Dispatch all lanes of the phase in one message as background `builder` agents, each in its own worktree, using the lane prompt in [references/dispatch-prompts.md](references/dispatch-prompts.md). They must run in the background so you can check and merge each as it reports. The prompt has each lane confirm it started from the current scaffold commit and run the setup command first. The `builder` agent preloads the same three skills, and the lane prompt carries the code-shape block from [references/code-shape.md](references/code-shape.md) (structure, naming, errors, comments), so lanes follow the conventions the plan was written against. Its default model is sonnet; pass `model: opus` for lanes that fail the checks in "Choosing a lane's model". If the user asked for Codex delegation and the `foreman` skill is installed, a lane can go to it with the same brief and code-shape block, plus a line telling it to follow the ce `architecting-systems`, `writing-tests` and `handling-errors` skills, and a `--budget` that ends before the phase's checkpoint.

While lanes run, do the inline work: the phase's inline lane if there is one, then the next phase's briefs and test-case lists. Commit inline work whenever it compiles, because lane merges land in the same checkout.

The next phase's tests can go to a background sonnet `builder` lane once its test-case list is written. Deciding the cases stays with you, because a case nobody listed is a case no test checks. That lane's branch stays unmerged until the next phase's scaffold commit, and you read the tests before committing it.

Testing during a phase is scoped, because the landing gate covers everything:

| Who | When | Runs |
| --- | --- | --- |
| Lane | While working | Tests for its own files only, filtered by file or name |
| Lane | Before reporting | Its filtered tests plus typecheck |
| You | Each landing | Full gate: all tests plus typecheck plus build if the repo has one |
| You | End of build | Full gate plus the demo |

A lane waiting on the full suite is waiting on work the landing gate repeats. When the full gate takes under about 10 seconds, lanes can run it too, since filtering saves nothing.

When `rr` is installed, every test and typecheck command, yours and the lanes', runs through rr so concurrent lanes queue on a machine-wide lock instead of all hitting the CPU at once, which matters when the same machine is also screen sharing or running a dev server. Use `rr run --local "<cmd>"` when the repo has no `.rr.yaml`; it takes the lock with no config file in the repo and adds about 50ms per run. When the repo's `.rr.yaml` lists hosts, use `rr run "<cmd>"` so runs go to those hosts with the same queuing. The lock is shared with every other rr run on the machine, so a stuck run elsewhere blocks the build; `rr unlock --all` clears it. Without rr, run the commands directly.

## 5. Land a phase

Check each lane before it merges. The gate only catches what the tests check, and the usual lane failures (an edit outside its files, a weakened test, an unrequested feature, a silent assumption) pass it. Merged unchecked, they sit on the landing branch and the next phase builds on them.

Do the check yourself, inline, as soon as the lane reports. Spawning a reviewer per lane costs more than the check, and you already have the brief in context:

1. Mechanical, against `git diff <landing branch>...<lane branch>`: every changed path is in the lane's owned files; no test file changed unless the lane is a test-writing lane; no `.skip`, `.only` or `todo` was added; no manifest or lockfile changed; no new type or lint suppressions. Any hit sends the lane back.
2. Read the diff against the brief: nothing outside the brief was added, and each choice the lane reported is one you accept. Log accepted choices in the plan. This takes a minute or two.
3. Read the diff for shape using the list in "Checking a lane diff" in [references/code-shape.md](references/code-shape.md): oversized files or functions, logic in the entry point, catch-all helper files, cross-module reach-ins, swallowed errors, exports without a JSDoc-style doc block, and comments that restate code or narrate the change. Passing tests don't cover any of these, and each one compounds when the next phase builds on it, so send the lane back.

For lanes that ran on opus because they needed judgment, also dispatch the `code-reviewer` agent in the background with the lane-check prompt in [references/dispatch-prompts.md](references/dispatch-prompts.md), scoped to that lane's diff and brief. It runs while other lanes are still working, so it delays the phase only when it belongs to the last lane to report. The phase's tag waits for any lane review still running, and its findings are fixed before the tag.

Merge each lane with `git merge --no-ff <lane branch>` as soon as it passes its check, rather than waiting for the slowest. After the last merge, run the full gate. If it fails, fix it yourself when the fix is small; otherwise dispatch a fresh opus `builder` with the failing output, the lane's brief and its diff. A sonnet lane that reports failing tests, or whose reported choice you reject or that touches a contract or another lane, is likewise redispatched on opus rather than retried on sonnet, since it needed judgment the routing missed.

A merge conflict between lanes means two lanes touched the same file, which the plan said they wouldn't. Resolve it, and note in the plan which file was shared so later phases don't repeat it.

When the gate is green, commit any gate fixes as `phase N: fixes`, run the phase's demo command, tag the commit `phase-N`, and tell the user in one line that phase N is demo-ready and how to see it. The tags are the demo points; commits between them may be red. Remove that phase's worktrees.

When a lane is past its checkpoint, land the phase without it. Its work either finishes and merges early in the next phase or gets cut. A green phase without one lane is worth more than a late phase with all of them.

## 6. Review once, then finish

At the 80% checkpoint, or when the last phase lands, stop starting work. Dispatch the `code-reviewer` agent in the background with `model: opus` and the final-review prompt in [references/dispatch-prompts.md](references/dispatch-prompts.md), against the diff from the scaffold's parent to HEAD. While it runs, go through the demo yourself and fix rough edges.

The review includes readability: file and function size, module boundaries and comment quality. A finding there counts like any other, so split the file or rewrite the comment before the final tag.

Check each finding against the code, fix the ones that hold, run the full gate, commit, and move the last phase tag or add a `final` tag. This is the only full review. Findings left unfixed because time ran out go in the final report.

## 7. Report

Report what each phase delivered and its tag, what was cut or left open, the review findings fixed and skipped, the branch name, and the demo command. Mark the plan file done. Merging into main or pushing happens only when the user asks.
