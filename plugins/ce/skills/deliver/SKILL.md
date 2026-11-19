---
name: deliver
description: Takes a feature, plan or RFC to production-ready code merged to main, with emphasis on architecture and code quality. Adopts or writes a phased plan, has it critiqued against the codebase, scaffolds contracts, runs parallel subagent lanes, lands and tags each phase on a feature branch as it finishes, reviews every lane with a capped review cycle, and merges to main after approval. Use when asked to execute, implement or ship a plan or RFC, for "have DA review it, then implement", "implement, review and merge to main", or for work that needs full review depth. For timeboxed or prototype work, use sprint.
argument-hint: "<plan path, RFC or feature>"
---

# Deliver

If the repo has its own `.claude/rules/` or CLAUDE.md guidance on branching, testing or review, follow that where it conflicts with this file.

The goal is production-ready code on main: sound module boundaries, an explicit error model, tests for every in-scope behavior, and review that converges instead of looping. Each phase lands on the feature branch as soon as it's green, so there is always something working to look at, and only the final merge to main waits for the user.

Read [lane-dag.md](../../shared/lane-dag.md) in full before step 1. It defines the graph, lanes, landing, reviews and resuming, and the steps below set its effort profile and use its terms. The other shared files are [grill.md](../../shared/grill.md) (step 1), [plan-template.md](../../shared/plan-template.md) (step 1), [dispatch-prompts.md](../../shared/dispatch-prompts.md) and [code-shape.md](../../shared/code-shape.md) (steps 2 to 5), and the script `../../shared/scripts/plan_graph.py`, all relative to this skill's directory.

## Profile

| Stage | Deliver |
| --- | --- |
| Plan critique | "Plan critique, deliver" prompt: opus, checked against the code; skipped when the plan says it was already reviewed or a critique already ran on it this session |
| Lane review | Every lane |
| Phase boundary review | Phase 1 only, before its tag, so no later phase starts until its findings are triaged and fixed, since everything builds on those contracts |
| Final review | Whole diff, then at most one fix review |
| Exercise as a user | Before the final review (step 4) |
| Timebox | None |
| Ends at | Local merge to main after the user approves. Push only when the user asks |

## 1. Plan

Small work skips the graph: if the whole change is one lane's worth of scope by "Sizing lanes" in lane-dag.md, follow "Small work" in "The graph", implement it inline, run the gate, and go to step 4. Steps 4 and 5 then use the recorded base commit for diffs and the report in place of the plan.

Otherwise, create the run's worktree and the landing branch in it (`deliver/<slug>`) first, then get a plan in the shape of plan-template.md inside that worktree under `plans/`, with `Skill: deliver. Profile: deliver.` in the header:

- Given a plan or RFC, convert it: keep its decisions, and add lanes with owned files, contracts and a test-case list for phase 1. The conversion is required, because `plan_graph.py` reads the lane tables.
- Given only a feature request, write the plan per "Planning the graph", grilling per grill.md first.

Either way, grill only for decisions the plan leaves open that the user would want to make. Facts you can look up aren't questions. Follow "Existing codebases" in lane-dag.md when the work changes existing code. Run `plan_graph.py validate` and fix what it reports.

## 2. Critique the plan

Dispatch `devils-advocate` with the "Plan critique, deliver" prompt, unless the profile says to skip it. Check each finding against the code yourself, apply the ones that hold to the plan, drop framing and hedging, and run `validate` again. Commit nothing until this is done, since its findings change contracts.

## 3. Scaffold and run the phases

Commit the scaffold per "Scaffold" in lane-dag.md, then run phases per "Running a phase" and land them per "Landing a lane and a phase", with a lane review for every lane.

Phase 1 gets one more step before its tag: once its gate is green, dispatch the "Phase boundary review" prompt and wait for it. Triage per "Reviews", commit what holds as `phase 1: boundary fixes`, rerun the gate, then tag. Because `ready` won't start phase 2 until `phase-1` is tagged, this blocks later phases without extra state, and a resume lands on it through the untagged-phase rule. Later phases don't get a boundary review; their lane reviews and the final review cover them.

Tell the user in one line when each phase tags; they may check it by hand, and the run doesn't wait for them.

## 4. Exercise and review

When the last phase lands, exercise the change the way a user would, because passing tests don't show the feature works. Scale it to what the change touches: a change to one unit gets a targeted check, not a sweep of every package.

- API: call the endpoints with realistic payloads.
- External integrations: hit the real service to catch rate limits, format drift and bot blocking.
- CLI: run the commands and read the output.
- UI: start the dev server and use the feature.
- Parsers: feed real data, not only fixtures.

Dispatch the "Final review" prompt in the background as soon as the last phase lands (for small work, as soon as the gate passes), so it runs while you exercise. Fix rough edges you hit (confusing errors, noisy output, inconsistent behavior), leaving structural cleanup to the review. Name the domain skills that apply (`architecting-systems`, `managing-databases`, `handling-errors`, `writing-tests`) in the review prompt.

Triage its findings per "Reviews" in lane-dag.md and fix the ones that hold. When the fixes changed behavior or touched more than a few lines, dispatch the "Fix review" prompt on them; fix what it confirms, and stop there. Run the full gate and commit with a message that says what was implemented and why.

## 5. Approve and merge

Report what each phase delivered and its tag, what the reviews caught and what was rejected and why, anything still open, and how to try the result. Ask the user to approve the merge to main. Once they do:

1. Merge the landing branch to main locally.
2. Push only if the user's request said push or deploy. Pushing main often triggers CI deploys, and the usual flow is for the user to QA from main first. Say in the report that nothing was pushed.
3. Remove the run's worktree and any QA checkouts.
4. Mark the plan done and move it to `./plans/done/` if the project uses that folder.
