---
name: build
description: Takes a build request from requirements to demo-ready code fast. Grills the user for scope, writes a phased plan with the smallest demoable slice first, runs a quick devil's advocate pass, builds each phase with parallel subagents in isolated worktrees, checks each lane before it merges, tags every green phase so it can be demoed, and ends with a single full code review. Use for "/ce:build <prompt>", timeboxed builds, or when asked to plan and build something end to end quickly. For executing an already-written plan with full review depth, use executing-plans instead.
argument-hint: "<what to build> [timebox, e.g. 90m]"
disable-model-invocation: true
---

# Build

If the repo has its own `.claude/rules/` or CLAUDE.md guidance on branching, testing or review, follow that where it conflicts with this file.

The goal is a landing branch where every phase ends green and demoable, each adding to the last. Speed comes from one grilling session, one fast plan critique, background lanes and a single full review at the end. Quality comes from tests written first, complete lane briefs, file-disjoint lanes, a check of every lane before it merges, and the full gate on every landing.

## 0. Intake

Record the start time (`date +%s`) and the timebox, if any. Without one, skip the budget checks and keep the phases.

| By | Done |
| --- | --- |
| 15% of T | Grill finished, plan written |
| 20% of T | Scaffold committed, DA findings applied |
| 45% of T | Phase 1 (MVP) tagged and demoed |
| 80% of T | Last phase tagged. Start nothing new after this |
| 100% of T | Review fixes landed, final report given |

When a checkpoint slips, cut scope from later phases, never the gate or the review.

While the first grill round is out, find these yourself:

- The test runner and its filter syntax, the typecheck command, and how long the full gate takes (run it once).
- One setup command that makes a fresh worktree runnable without touching the lockfile: symlink the dependency directory from the main checkout (`ln -s <main checkout>/node_modules node_modules`) or a frozen-lockfile install.
- Whether `rr` is on PATH and the repo has a `.rr.yaml` with hosts.
- The branch and whether the tree is clean. Uncommitted changes would ride into the scaffold, so ask whether to commit, stash or include them. Worktrees need a commit, so with no repo or no commits, `git init` and commit.
- Whether lanes can run tests, typecheck and `git add`/`git commit` without permission prompts. Background lanes can't answer one, so settle the permission mode before phase 1.

## 1. Grill

Question the user until phase 1's scope is settled. Treat the request as a tree of decisions (adapted from Matt Pocock's grilling skill) and each round ask every question whose prerequisites are answered.

Ask through the agent's native question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex) so the user answers by picking options. Each question is a sentence or two with two to four concrete options, your recommendation first and marked "(Recommended)". When a round has more questions than one call allows, make several calls. Only without a question tool, fall back to a numbered list with a recommendation on each line. Facts you can look up are never questions.

Stop after the round that settles phase 1, usually two and at most three. Decisions that only affect later phases take your recommended default and go in the plan's assumptions, where the user can override them. The last round always asks where phases land: a new `build/<slug>` branch (the default) or the current branch.

## 2. Plan

Load `architecting-systems`, `writing-tests`, `handling-errors` and `writer`, and read [references/code-shape.md](references/code-shape.md). Module boundaries, contracts, error model and comment style are cheapest to decide here, before lanes depend on them.

Lanes pass their tests by the shortest route, usually one large file, and can only split work across files the plan gave them. So the contracts section lists every module path with its single responsibility, and the spec states the error model (what fails, how it's reported, what a caller sees). A plan that names one implementation file for two responsibilities isn't ready.

Write the plan to `plans/build-<slug>.md` from [references/plan-template.md](references/plan-template.md) and show the user the phase list in a few lines; they approve phases, not prose. Only phase 1 gets full lane briefs and a test-case list now. Later phases get one-line lane rows, with briefs written while the previous phase runs.

Phase 1 is the smallest end-to-end slice the user could watch work, and each later phase adds one demoable capability. Order phases by capability, not by layer, or there is nothing to demo until the end.

### Sizing lanes

A phase takes as long as its slowest lane plus landing, and each lane has a fixed cost: agent startup and code reading, worktree setup, and about a minute of your time checking and merging. Keep lanes small, roughly equal and few. Size by scope, since time estimates are unreliable:

| Size | Scope | Where it goes |
| --- | --- | --- |
| Tiny | A few lines, one small function, a config change | Inline, or folded into a related lane |
| S | 1 to 2 owned files, one function, endpoint or component, up to about 5 tests | A lane |
| SM | Up to 3 or 4 owned files, one module or capability, up to about 12 tests | A lane |
| Larger | More than one capability or more than 4 files | Split by capability, or across two phases |

The Larger limit keeps lanes balanced and failures contained; a well-briefed 300-line module takes a lane minutes, not hours. Then check each phase:

- Lanes own disjoint files. Two lanes that need the same file are one lane, or the shared part moves into the scaffold.
- The scaffold owns registration files (the public index or barrel, routers, tests or docs that pin the public API) with every planned export stubbed, so no lane edits them.
- The longest lane is at most about twice the shortest.
- Two to four lanes. Each extra lane is another diff to check and merge.
- Each lane has a reads list: contracts, owned files, its tests, and at most two pattern files. Code reading is the largest per-lane overhead.
- A phase with one lane, or only tiny units, runs inline in your checkout. Small builds are often inline throughout, which is fine.

### Choosing a lane's model

Route by how much judgment a lane needs, not its size, since a wrong lane costs more to investigate than Sonnet saves. A lane goes to sonnet only when its contract and tests are settled in the scaffold, the spec answers every case it touches, it stays inside its owned files with no cross-module invariant, and a wrong implementation would fail its tests. Implementing against a contract, writing tests from a settled case list and mechanical edits usually qualify.

Everything else goes to opus: designing a contract others depend on, filling a spec gap, invariants around state, ordering, caching, concurrency, security or money, cross-module changes, and debugging a failed lane.

### Briefing lanes

Each lane's brief lets an engineer who never saw the conversation finish without asking anything; the template has the fields. Paste it into the dispatch prompt in full, because every ambiguity left in becomes a choice the agent makes alone and you find in review. A brief you can't write without open questions means the lane isn't ready: settle the question, or route it to opus with the question named.

## 3. Scaffold and fast DA, in parallel

Dispatch `devils-advocate` in the background with `model: sonnet` and the scoped prompt from [references/dispatch-prompts.md](references/dispatch-prompts.md). It reads only the plan and caps findings at five, which is what keeps it fast on a greenfield build.

Meanwhile, create the landing branch and commit the scaffold:

- The plan file.
- Shared types and interfaces.
- The folder layout from the contracts section, with the entry point limited to wiring.
- A stub at every planned module path that exports its signatures and throws "not implemented", so typecheck passes and only tests fail.
- Phase 1's tests, written from the test-case list with a test for every edge case the spec names, and read by you before committing. A lane implements what its tests check and skips the rest.
- Anything the gate needs.

Record the scaffold SHA in the plan; lanes start from it. Tests are read-only to implementation lanes, and you fix a missing case in the scaffold.

When the DA returns, apply findings that change phase 1, move the rest to the phase they affect, and drop the ones that don't hold. Don't rerun it. If it's still running when the scaffold is done, start phase 1 and fold findings in later.

## 4. Run a phase

Later phases start with their own scaffold commit of stubs and tests. Never merge a later phase's tests early, or the gate fails on tests nobody is meant to pass yet.

Dispatch all lanes in one message as background `builder` agents, each in its own worktree, with the lane prompt from [references/dispatch-prompts.md](references/dispatch-prompts.md) and the code-shape block from [references/code-shape.md](references/code-shape.md). `builder` defaults to sonnet; pass `model: opus` per the routing above. If the user asked for Codex and the `foreman` skill is installed, a lane can go there with the same brief and code-shape block, a line pointing it at the ce `architecting-systems`, `writing-tests` and `handling-errors` skills, and a `--budget` that ends before the checkpoint.

While lanes run, do the phase's inline work, then write the next phase's briefs and test-case lists. Commit inline work whenever it compiles, since lane merges land in the same checkout. Once the next phase's cases are listed, a background sonnet `builder` can write those tests; its branch waits for the next scaffold commit, and you read the tests before committing.

| Who | When | Runs |
| --- | --- | --- |
| Lane | While working | Tests for its own files, filtered |
| Lane | Before reporting | Filtered tests plus typecheck |
| You | Each landing | Full gate: all tests, typecheck, build if any |
| You | End of build | Full gate plus the demo |

Lanes skip the full suite because the landing gate repeats it. If the full gate takes under about 10 seconds, lanes can run it too.

When `rr` is installed, run every test and typecheck command, yours and the lanes', through it so concurrent runs queue on a machine-wide lock instead of saturating the CPU: `rr run --local "<cmd>"` without a `.rr.yaml`, `rr run "<cmd>"` when `.rr.yaml` lists hosts. The lock is shared machine-wide, so a stuck run elsewhere blocks the build; `rr unlock --all` clears it. Before starting a run, stop any earlier run of yours that is still going, and don't start one mid-edit, since rr syncs the working tree as it stands.

## 5. Land a phase

Check each lane inline as soon as it reports. The usual lane failures (an edit outside its files, a weakened test, an unrequested feature, a silent assumption) pass the gate, and the next phase builds on whatever merges.

1. Mechanical, on `git diff <landing branch>...<lane branch>`: every changed path is owned; no test file changed unless it's a test-writing lane; no added `.skip`, `.only` or `todo`; no manifest or lockfile change; no new type or lint suppressions; no new export that only tests use. Any hit sends the lane back.
2. Against the brief: nothing extra was added, and you accept each choice the lane reported. Log accepted choices in the plan.
3. For shape, using "Checking a lane diff" in [references/code-shape.md](references/code-shape.md). Tests don't catch these, and they compound across phases, so send the lane back.

For opus lanes, also dispatch `code-reviewer` in the background with the lane-check prompt, scoped to that lane's diff and brief. Fix its findings before the phase tag.

Merge each lane with `git merge --no-ff <lane branch>` as soon as it passes, then run the full gate after the last merge. Fix small failures yourself; otherwise dispatch a fresh opus `builder` with the failing output, the brief and the diff. A sonnet lane that reports failing tests, makes a choice you reject, or touches a contract or another lane's files is redispatched on opus, since it needed judgment the routing missed.

A merge conflict means two lanes shared a file. Resolve it and note the file in the plan so later phases avoid it.

When the gate is green, commit any fixes as `phase N: fixes`, run the demo, tag `phase-N`, tell the user in one line how to see it, and remove the phase's worktrees. Tags are the demo points; commits between them may be red.

A lane past its checkpoint doesn't hold the phase. Land without it, then merge it early in the next phase or cut it.

## 6. Review once, then finish

At the 80% checkpoint or when the last phase lands, stop starting work. Dispatch `code-reviewer` in the background with `model: opus` and the final-review prompt, against the diff from the scaffold's parent to HEAD. Meanwhile, walk the demo and fix rough edges.

Readability findings (file and function size, module boundaries, comments) count like any other. Check each finding against the code, fix the ones that hold, run the full gate, commit, and move the last phase tag or add a `final` tag. Findings left unfixed for time go in the report.

## 7. Report

Report each phase's delivery and tag, what was cut or left open, review findings fixed and skipped, the branch and the demo command. Mark the plan done. Merge to main or push only when the user asks.
