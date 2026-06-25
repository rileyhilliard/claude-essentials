---
name: executing-plans
description: Executes implementation plans with smart task grouping. Groups related tasks to share context, parallelizes across independent subsystems.
---

# Executing Plans

**You are an orchestrator.** Spawn and coordinate sub-agents to do the actual implementation. Group related tasks by subsystem (one agent for API routes, another for tests) rather than spawning per-task. Each agent re-investigates the codebase, so fewer agents with broader scope = faster execution.

## 1. Setup

**Create a worktree** using `EnterWorktree` before starting any work. This isolates changes from the main branch and makes cleanup safe. Skip only for trivial single-file changes that don't warrant isolation.

**Clarify ambiguity upfront.** If the plan has unclear requirements or meaningful tradeoffs, ask before starting. Don't guess when the user can clarify in 10 seconds.

**Track progress with tasks.** Create tasks for each major work item from the plan. Set up dependency chains between tasks using `addBlocks`/`addBlockedBy` so blocked tasks don't start prematurely. Update task status as work progresses. This keeps execution visible to the user and persists across context compactions.

## 2. Group and Execute

Group related tasks to share agent context. One agent per subsystem, groups run in parallel.

| Signal | Group together |
|--------|----------------|
| Same directory prefix | `src/auth/*` tasks |
| Same domain/feature | Auth tasks, billing tasks |
| Plan sections | Tasks under same `##` heading |

3-4 tasks max per group. Split if larger. Overloading a single agent causes context compactions that degrade output quality, so err toward splitting over cramming.

**Parallel vs sequential:** Groups that touch different subsystems run in parallel. Groups with dependencies run sequentially (e.g., create shared types before using them). When parallel agents may touch overlapping files, use `isolation: "worktree"` on the Agent call.

**Auto-recovery:**
1. Agent attempts to fix failures (has context)
2. If it can't fix, report failure with error output
3. Dispatch fix agent with context from the failure
4. Same error twice: stop and ask user

## 3. Verify

Verification is a **gate**, not a checklist. Nothing proceeds to merge until all checks pass. If any check fails, fix and re-verify. This is a loop, not a one-shot.

**Automated tests.** Run the full test suite. All tests must pass.

**Manual verification.** Automated tests aren't sufficient. Actually exercise the changes:
- **API changes:** Curl endpoints with realistic payloads
- **External integrations:** Test against real services to catch rate limiting, format drift, bot detection
- **CLI changes:** Run actual commands, verify output
- **UI changes:** Start the dev server and use the feature in a browser
- **Parser changes:** Feed real data, not just fixtures

Watch for DX friction during manual testing: confusing error messages, noisy output, inconsistent behavior, rough edges that technically work but feel bad. Fix inline or document for follow-up. Don't ship friction.

**Code review (mandatory).** After tests pass and manual verification is done, dispatch the `ce:code-reviewer` agent to review the full diff against the base branch. This step is not optional.

Load relevant domain skills into the reviewer based on what was implemented. Evaluate which apply and include them in the agent prompt:
- `Skill(architecting-systems)` - system design, module boundaries
- `Skill(managing-databases)` - database work
- `Skill(handling-errors)` - error handling
- `Skill(writing-tests)` - test quality
- `Skill(optimizing-performance)` - performance work

Handle the review verdict:
- **Must fix:** Fix all Critical and Important issues, then re-run the review
- **Suggestions:** Fix these too unless there's a clear reason not to

Plan execution is not done until review findings are addressed.

## 4. Complete

Once verification passes:

1. **Commit** the work with a message summarizing what was implemented
2. **Merge to main** from the worktree branch
3. **Exit worktree** using `ExitWorktree` with `action: "remove"` to clean up
4. **Mark plan as COMPLETED** and move to `./plans/done/` if applicable
