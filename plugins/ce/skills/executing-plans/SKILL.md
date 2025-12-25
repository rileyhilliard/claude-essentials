---
name: executing-plans
description: Execute implementation plans with smart task grouping. Group related tasks to share context, parallelize across subsystems.
---

# Executing Plans

Execute plans by grouping related tasks and dispatching one agent per group. Tasks in the same subsystem share context within a single agent, reducing redundant codebase exploration.

## Core Rules

1. **Group related tasks** - Tasks in the same subsystem go to the same agent
2. **One group = one agent** - Each agent handles multiple related tasks sequentially
3. **Parallelize groups** - Independent groups (different subsystems) run in parallel
4. **Max 3-4 tasks per group** - Don't overload a single agent

## Why Grouping Matters

Each agent pays context cost to understand the codebase. Without grouping:

```
Task 1 (auth/login)  → Agent 1 [explores codebase, reads auth/]
Task 2 (auth/logout) → Agent 2 [explores codebase, reads auth/ again]
Task 3 (auth/session)→ Agent 3 [explores codebase, reads auth/ again]
```

With grouping:

```
Tasks 1-3 (auth/*)   → Agent 1 [explores once, executes 3 tasks]
```

## Execution Flow

```
Plan Execution Progress:
- [ ] Step 1: Load the plan file
- [ ] Step 2: Analyze and group tasks by subsystem
- [ ] Step 3: Create TodoWrite with task groups
- [ ] Step 4: Dispatch agents for independent groups in parallel
- [ ] Step 5: Update plan file (mark IN_PROGRESS)
- [ ] Step 6: Wait for completion, dispatch dependent groups
- [ ] Step 7: Run final verification (tests, build, lint)
- [ ] Step 8: Dispatch code-reviewer agent
- [ ] Step 9: Update plan status to COMPLETED
```

1. Load the plan file
2. **Analyze tasks and group by subsystem** (see grouping rules below)
3. Create TodoWrite with task groups (not individual tasks)
4. Evaluate skills relevant to each group
5. Dispatch agents for independent groups in parallel
6. **Update plan file** - Mark task checkboxes complete, update status to IN_PROGRESS
7. Wait for completion, then dispatch dependent groups
8. Run final verification (tests, build, lint)
9. Dispatch `ce:code-reviewer` for review
10. **Update plan status** to COMPLETED when done

## Task Grouping Rules

### Auto-grouping by directory pattern

Infer groups from file paths mentioned in tasks:

```
Task 1: "Add login endpoint"      → touches src/auth/*
Task 2: "Add logout endpoint"     → touches src/auth/*
Task 3: "Add session management"  → touches src/auth/*
Task 4: "Add billing API"         → touches src/billing/*
Task 5: "Add webhook handlers"    → touches src/billing/*

Groups:
  Group A (auth): Tasks 1, 2, 3    → 1 agent
  Group B (billing): Tasks 4, 5   → 1 agent (parallel with A)
```

### Respect plan structure

If the plan uses sections/phases, treat each as a group:

```markdown
## Authentication Tasks        ← Group A
### Task 1: Add login
### Task 2: Add logout

## Billing Tasks               ← Group B
### Task 3: Add billing API
### Task 4: Add webhooks
```

### Grouping heuristics

| Signal | Group together |
|--------|----------------|
| Same directory prefix | `src/auth/*` tasks together |
| Same domain/feature | Auth tasks, billing tasks, UI tasks |
| Shared dependencies | Tasks that read same config/types |
| Plan sections | Tasks under same `##` heading |

### Group size limits

- **Minimum**: 1 task (can't group if truly isolated)
- **Maximum**: 3-4 tasks (avoid overloading agent context)
- **Split large groups**: If >4 related tasks, split into 2 groups

## Group Dispatch

```
# Dispatch one agent per group, groups run in parallel
Task tool (general-purpose):
  description: "Auth tasks: login, logout, session"
  prompt: |
    Execute the following tasks from [plan-file] IN ORDER:
    - Task 1: Add login endpoint
    - Task 2: Add logout endpoint
    - Task 3: Add session management

    These tasks are in the same subsystem (auth). Execute them
    sequentially, sharing your understanding of the codebase.

    Use skills: <list skills that fit>
    Commit after each task completes.
    Report: files changed per task, test results

Task tool (general-purpose):
  description: "Billing tasks: API, webhooks"
  prompt: |
    Execute the following tasks from [plan-file] IN ORDER:
    - Task 4: Add billing API
    - Task 5: Add webhook handlers

    These tasks are in the same subsystem (billing). Execute them
    sequentially, sharing your understanding of the codebase.

    Use skills: <list skills that fit>
    Commit after each task completes.
    Report: files changed per task, test results
```

## When to Parallelize Groups

**Parallel:** Groups touch different subsystems

```
Group A: src/auth/*      ─┬─ parallel
Group B: src/billing/*   ─┘
```

**Sequential:** Groups have dependencies

```
Group A: Create shared types  → Group B: Use those types
```

## Agent Selection

- **general-purpose**: Default for most tasks
- **ce:haiku**: Only for purely mechanical tasks (copy file, add single export, log parse, etc)

## Progress Tracking

Update the plan file as you execute:

1. Set plan status to `IN_PROGRESS` when starting
2. Check off `[x]` each task as agents complete them
3. After each group completes, verify all its task checkboxes are marked done
4. Set plan status to `COMPLETED` when all groups pass verification

This keeps the plan file as the source of truth for progress.

## Auto-Recovery

If a task within a group fails:

1. The agent should attempt to fix it (it has full context)
2. If agent can't fix, it reports failure for that task
3. Dispatch a fix agent with the error output and group context
4. If same error twice, stop and ask user

## Final Verification

After all tasks:

1. Run full test suite and linters
2. Run build
3. Dispatch `ce:code-reviewer` agent to review changes
4. Plan and fix issues found
5. Mark plan COMPLETED
