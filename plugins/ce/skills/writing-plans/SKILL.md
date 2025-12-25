---
name: writing-plans
description: Create implementation plans with tasks grouped by subsystem. Related tasks share agent context; groups parallelize across subsystems.
---

# Writing Plans

Write step-by-step implementation plans for agentic execution. Each task should be a **complete unit of work** that one agent handles entirely.

**Save to:** `**/plans/YYYY-MM-DD-<feature-name>.md`

## Plan Template

````markdown
# [Feature Name] Implementation Plan

> **Status:** DRAFT | APPROVED | IN_PROGRESS | COMPLETED

## Specification

**Goal:** [What we're building and why]

**Success Criteria:**

- [ ] Criterion 1
- [ ] Criterion 2

## Context Loading

_Run before starting:_

```bash
read src/relevant/file.ts
glob src/feature/**/*.ts
```

## Tasks

### Task 1: [Complete Feature Unit]

**Context:** `src/auth/`, `tests/auth/`

**Steps:**

1. [ ] Create `src/auth/login.ts` with authentication logic
2. [ ] Add tests in `tests/auth/login.test.ts`
3. [ ] Export from `src/auth/index.ts`

**Verify:** `npm test -- tests/auth/`

---

### Task 2: [Another Complete Unit]

**Context:** `src/billing/`

**Steps:**

1. [ ] ...

**Verify:** `npm test -- tests/billing/`
````

## Task Sizing

A task includes **everything** to complete one logical unit:

- Implementation + tests + types + exports
- All steps a single agent should do together

**Right-sized:** "Add user authentication" - one agent does model, service, tests, types
**Wrong:** Separate tasks for model, service, tests - these should be one task

**Bundle trivial items:** Group small related changes (add export, update config, rename) into one task.

## Parallelization & Grouping

During execution, tasks are **grouped by subsystem** to share agent context. Structure your plan to make grouping clear:

```markdown
## Authentication Tasks          ← These will run in one agent
### Task 1: Add login
### Task 2: Add logout

## Billing Tasks                 ← These will run in another agent (parallel)
### Task 3: Add billing API
### Task 4: Add webhooks

## Integration Tasks             ← Sequential (depends on above)
### Task 5: Wire auth + billing
```

**Execution model:**
- Tasks under same `##` heading → grouped into one agent
- Groups touching different subsystems → run in parallel
- Max 3-4 tasks per group (split larger sections)

Tasks in the **same subsystem** should be sequential or combined into one task.

## Rules

1. **Explicit paths:** Say "create `src/utils/helpers.ts`" not "create a utility"
2. **Context per task:** List files the agent should read first
3. **Verify every task:** End with a command that proves it works
4. **One agent per task:** All steps in a task are handled by the same agent

## Large Plans

For plans over ~1000 lines, split into phases in a folder:

```
**/plans/YYYY-MM-DD-feature/
├── README.md           # Overview + phase tracking
├── phase-1-setup.md
└── phase-2-feature.md
```
