---
name: sprint
description: Builds something end to end against the clock, landing a demoable, tested phase as early as possible and adding one capability per phase. Grills for scope, writes a phased plan, runs parallel subagent lanes in worktrees, checks and merges each lane as it finishes, tags every green phase so it can be demoed or checked by hand, and ends with one code review. Use for "/ce:sprint <prompt>", timeboxed builds, prototypes and live demos, or when speed matters more than review depth. For production work, use deliver.
argument-hint: "<what to build> [timebox, e.g. 90m]"
disable-model-invocation: true
---

# Sprint

If the repo has its own `.claude/rules/` or CLAUDE.md guidance on branching, testing or review, follow that where it conflicts with this file.

The goal is a landing branch where every phase ends green and demoable, each adding to the last, inside a timebox. Speed comes from one grilling session, one fast plan critique, background lanes and a single full review at the end. Quality comes from tests written first, complete lane briefs, file-disjoint lanes, a scripted and a model check of every lane before it merges, and the full gate on every landing.

Read [lane-dag.md](../../shared/lane-dag.md) in full before step 0. It defines the graph, lanes, landing, reviews and resuming, and the steps below set its effort profile and use its terms. The other shared files are [grill.md](../../shared/grill.md) (step 1), [plan-template.md](../../shared/plan-template.md) (step 2), [dispatch-prompts.md](../../shared/dispatch-prompts.md) and [code-shape.md](../../shared/code-shape.md) (steps 2 to 5), and the script `../../shared/scripts/plan_graph.py`, all relative to this skill's directory.

## Profile

| Stage | Sprint |
| --- | --- |
| Plan critique | "Plan critique, sprint" prompt: sonnet, five findings, plan only, never rerun |
| Lane review | opus lanes, and any lane touching state, concurrency, security or money |
| Phase boundary review | None |
| Final review | One round on the whole diff, no fix review |
| Timebox | Checkpoints below; late lanes are cut or deferred rather than waited on |
| Ends at | Tagged landing branch. Merge to main or push only when the user asks |

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

Don't forecast how long work will take, and don't cut scope or warn the user on a forecast. Agents estimate their own work like a human team would, so they say days for what lanes finish in minutes, and a plan built on that cuts scope the timebox could hold. Size work by scope, using "Sizing lanes" in lane-dag.md, and compare elapsed time (`date +%s` minus the start) against the checkpoints. A checkpoint has slipped only when that clock has passed it. Phase 1's measured time is the best guide to how much the later phases can hold.

While the first grill round is out, gather the repo facts listed at the end of "Scaffold" in lane-dag.md, and check the branch and whether the tree is clean. Uncommitted changes would ride into the scaffold, so ask whether to commit, stash or include them. Worktrees need a commit, so with no repo or no commits, `git init` and commit.

## 1. Grill

Follow grill.md until phase 1's scope is settled, at most three rounds.

## 2. Plan

If the whole build is one lane's worth of scope, follow "Small work" in lane-dag.md instead and go to step 5.

Otherwise create the landing branch (`sprint/<slug>` unless the grill chose the current branch), plan the graph per "Planning the graph" in lane-dag.md and write it to `plans/sprint-<slug>.md` from plan-template.md, with `Skill: sprint. Profile: sprint.` in the header. Show the user the phase list in a few lines; they approve phases, not prose. Run `plan_graph.py validate` and fix what it reports.

## 3. Scaffold and plan critique, in parallel

Dispatch `devils-advocate` in the background with the "Plan critique, sprint" prompt. It reads the plan, checks the code only briefly, and caps findings at five, which keeps it fast on a new build.

Meanwhile, commit the scaffold per "Scaffold" in lane-dag.md.

When the critique returns, apply findings that change phase 1, move the rest to the phase they affect, and drop the ones that don't hold. Don't rerun it. If it's still running when the scaffold is done, start phase 1 and fold findings in later.

## 4. Run the phases

Run phases per "Running a phase" and land them per "Landing a lane and a phase" in lane-dag.md, with lane reviews as the profile says. Tell the user in one line when each phase tags; they may check it by hand, and the run doesn't wait for them.

A lane past its checkpoint doesn't hold the phase: land without it, then merge it at the start of the next phase, or cut it.

## 5. Review once, then finish

At the 80% checkpoint or when the last phase lands, stop starting work. Dispatch the "Final review" prompt in the background. Meanwhile, walk the demo and fix rough edges, leaving structural cleanup to the review.

Triage findings per "Reviews" in lane-dag.md. Readability findings (file and function size, module boundaries, duplication, comments) count like any other. Fix the ones that hold, run the full gate, commit, and move the last phase tag or add a `final` tag. Findings left unfixed for time go in the report.

## 6. Report

Report each phase's delivery and tag, what was cut or left open, review findings fixed and rejected, the branch and the demo command. Mark the plan done and remove any QA checkouts.
