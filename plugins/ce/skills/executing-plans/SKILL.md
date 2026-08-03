---
name: executing-plans
description: Executes implementation plans directly with a verification gate and conditional code review. Use when carrying out a written plan step by step; delegates to subagents only for large, genuinely independent, parallelizable work.
---

# Executing Plans

**Default to implementing directly.** Delegation is the exception, not the default. Delegate to a subagent only for large tasks that are genuinely independent and parallelizable, such as a wide multi-file investigation. Do not delegate work you can finish yourself in a handful of tool calls, and do not use subagents to verify or double-check your own work. If one subagent can complete the task, use one rather than several, and keep spawn counts low.

## 1. Setup

**Create a worktree** using `EnterWorktree` before starting any work. This isolates changes from the main branch and makes cleanup safe. Skip only for trivial single-file changes that don't warrant isolation.

**Clarify ambiguity upfront.** If the plan has unclear requirements or meaningful tradeoffs, ask before starting. Don't guess when the user can clarify in 10 seconds.

**Track progress with tasks.** Create tasks for each major work item from the plan. Set up dependency chains between tasks using `addBlocks`/`addBlockedBy` so blocked tasks don't start prematurely. Update task status as work progresses. This keeps execution visible to the user and persists across context compactions.

## 2. Execute

Work through the plan's tasks directly, in order, updating task status as you go.

**If delegation is warranted** (large, independent, parallelizable work identified in step 1), group related tasks by subsystem rather than spawning per-task, since each agent re-investigates the codebase.

| Signal | Group together |
|--------|----------------|
| Same directory prefix | `src/auth/*` tasks |
| Same domain/feature | Auth tasks, billing tasks |
| Plan sections | Tasks under same `##` heading |

Keep concurrent agents to a small handful. Claude Code hard-fails above 20 concurrent subagents, but that's not a target, stay well under it.

**Parallel vs sequential:** Groups that touch different subsystems run in parallel. Groups with dependencies run sequentially (e.g., create shared types before using them). When parallel agents may touch overlapping files, use `isolation: "worktree"` on the Agent call.

**Recovery:** Fix failures inline yourself. If the same error recurs after a second attempt, stop and ask the user rather than keep retrying.

## 3. Verify

Verification is a **gate**, not a checklist. Nothing proceeds to merge until all checks pass.

**Automated tests.** Run the full test suite. All tests must pass.

**Manual verification.** Automated tests aren't sufficient. Actually exercise the changes:
- **API changes:** Curl endpoints with realistic payloads
- **External integrations:** Test against real services to catch rate limiting, format drift, bot detection
- **CLI changes:** Run actual commands, verify output
- **UI changes:** Start the dev server and use the feature in a browser
- **Parser changes:** Feed real data, not just fixtures

Watch for DX friction during manual testing: confusing error messages, noisy output, inconsistent behavior, rough edges that technically work but feel bad. Fix inline or document for follow-up. Don't ship friction.

**Code review (conditional).** For large or risky diffs, dispatch the `ce:code-reviewer` agent to review the full diff against the base branch after tests pass and manual verification is done. Skip it for small or simple changes.

Load relevant domain skills into the reviewer based on what was implemented. Evaluate which apply and include them in the agent prompt:
- `Skill(architecting-systems)` - system design, module boundaries
- `Skill(managing-databases)` - database work
- `Skill(handling-errors)` - error handling
- `Skill(writing-tests)` - test quality
- `Skill(optimizing-performance)` - performance work

Handle the review verdict:
- **Must fix:** Fix all Critical and Important issues
- **Suggestions:** Fix these too unless there's a clear reason not to

## 4. Complete

Once verification passes:

1. **Commit** the work with a message summarizing what was implemented
2. **Merge to main** from the worktree branch
3. **Exit worktree** using `ExitWorktree` with `action: "remove"` to clean up
4. **Mark plan as COMPLETED** and move to `./plans/done/` if applicable

Match the length of written documents (commit messages, failure reports) to what the task needs: cover the substance, but do not pad with filler sections, redundant summaries, or boilerplate.
