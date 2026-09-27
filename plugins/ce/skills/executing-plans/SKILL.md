---
name: executing-plans
description: Executes an implementation plan or RFC end to end in a worktree, covering a devils-advocate review of the plan, grouped subagent implementation, the test gate, a code-reviewer pass with every finding fixed, a commit, and a local merge to main. Use when asked to execute, implement, or ship a plan, or for requests like "have DA review it, then implement", "run code review and commit", "implement, commit, merge to main", or "make an RFC, DA it, then build it".
---

# Executing Plans

The job is to take a written plan to a reviewed, committed, locally merged result without the user restating each step. Each stage below is part of the default flow; skip one only where this file says it can be skipped.

## 1. Setup

Create a worktree with `EnterWorktree` before changing anything, so the work stays isolated from main. Skip it only for a trivial single-file change.

Run a devil's advocate pass on the plan. Dispatch the `ce:devils-advocate` agent and ask it to check the plan against the real code, not just read it. Verify each finding against the code yourself, apply the ones that hold up, drop pure framing or hedging, and update the plan file. Skip this when the plan says it was already reviewed or a DA pass already ran on it this session.

If the plan leaves a real decision open (a tradeoff the user would want to make), ask before starting. Otherwise proceed.

Track the plan's work items with the task tool, with dependencies between them, so progress survives compaction and the user can see it.

## 2. Implement

Hand implementation to subagents grouped by subsystem, and do small pieces (a handful of tool calls) yourself. Each subagent re-reads the codebase, so a few agents with coherent scope beat one agent per task.

| Signal | Group together |
| --- | --- |
| Same directory prefix | `src/auth/*` tasks |
| Same feature or domain | Billing tasks |
| Same plan section | Tasks under one `##` heading |

Groups on different subsystems run in parallel. Groups that depend on each other (shared types first, then their users) run in sequence. Pass `isolation: "worktree"` when parallel agents might touch the same files.

Write each dispatch prompt so the agent acts rather than reports:

- Say "implement" or "fix directly". Agents asked to "recommend" or "propose" tend to come back with a report and no changes.
- Name the files, the plan section, and the test command it should run.
- Set `model` on every dispatch. Use `opus` for work that needs judgment (design choices, cross-cutting changes, tricky debugging) and `sonnet` for mechanical bulk edits. Don't use haiku for implementation.
- In an isolated worktree, tell it to run plain single commands from the worktree root, without `cd` chains, loops, or variable assignments around git. The harness refuses compound commands it can't verify.
- Subagents commit on their own branch only. They never merge, push, or call `ExitWorktree`; those belong to you.
- An agent that writes tests should edit test files only.

When an agent fails, let it fix its own failure first, since it has the context. If the same error comes back after a second attempt, stop and ask the user instead of retrying.

## 3. Verify

Nothing merges until these pass.

Run the project's documented test command (from CLAUDE.md or the README, scoped to the changed packages if the project documents scoped runs). Don't guess a runner.

Then exercise the change the way a user would, because passing tests don't show that the feature works:

- API: call the endpoints with realistic payloads.
- External integrations: hit the real service to catch rate limits, format drift, and bot blocking.
- CLI: run the commands and read the output.
- UI: start the dev server and use the feature.
- Parsers: feed real data, not only fixtures.

Fix rough edges you hit on the way (confusing errors, noisy output, inconsistent behavior) rather than shipping them.

Then dispatch the `ce:code-reviewer` agent on the full diff against the base branch. This step always runs. Name the domain skills that apply in its prompt (`architecting-systems`, `managing-databases`, `handling-errors`, `writing-tests`). Fix every finding it returns; its list has no optional tier. If the fixes were substantial, run the reviewer again on the new diff.

## 4. Complete

1. Commit with a message that says what was implemented and why.
2. Merge to main locally from the worktree branch.
3. Push only if the user's request said push or deploy. Pushing main often triggers CI deploys, and the usual flow is for the user to QA from main first. Say in the final report that nothing was pushed.
4. Call `ExitWorktree` with `action: "remove"`.
5. Mark the plan as completed and move it to `./plans/done/` if the project uses that folder.

Keep the final report to what changed, what the review caught, and anything left for the user.
